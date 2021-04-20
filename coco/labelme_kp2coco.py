import json
import os
import os.path as osp
import glob
import argparse
import datetime
import pycocotools.mask
import uuid
import collections
from tqdm import tqdm

g_ann_id = 1

def create_ann_id():
    global g_ann_id
    ids = g_ann_id
    g_ann_id += 1
    return ids


def load_skeleton(skeleton_file):
    
    with open(skeleton_file, 'r') as sk_fb:
        skeleton=[]
        sk_raw = sk_fb.readlines()
        for index, sk in enumerate(sk_raw):
            sk = sk.replace('\n', '')
            sk = sk.replace('\r', '')
            sk_sp = sk.split(',')
            sk_line = []
            sk_line.append(int(sk_sp[0]))
            sk_line.append(int(sk_sp[1]))
            skeleton.append(sk_line)
    return skeleton

def create_single_image_data( jpg_file_name = '', image_height = 0, image_width = 0, image_id = 0 ):
    single_image_info = dict(
                                license         = 4,
                                file_name       = jpg_file_name,
                                coco_url        = 'http://',
                                height          = image_height,
                                width           = image_width,
                                date_captured   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                flickr_url      = 'http://',
                                id              = image_id,
                            )
    return single_image_info

def create_coco_merge_dict( label_names, kp_names, skeleton_list, coco_licenses ):
    categories=[]
    for index, label in enumerate( label_names ):
        label_id = index + 1
        categorie_info = dict(
                                supercategory   = label,
                                id              = label_id,
                                name            = label,
                                keypoints       = kp_names,
                                skeleton        = skeleton_list,
                            )
        categories.append(categorie_info)
    
    merge_data = dict(
                        info=dict(
                                    description='person key points',
                                    url='http://cocodataset.org',
                                    version='1.0',
                                    year=datetime.datetime.now().year,
                                    contributor='COCO 2017 dataset',
                                    date_created=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                ),
                        #licenses=[dict(url=None, id=0, name=None,)],
                        licenses=coco_licenses,
                        images=[
                            # license, url, file_name, height, width, date_captured, id
                        ],
                        # type="instances",
                        annotations=[
                            # segmentation, area, iscrowd, image_id, bbox, category_id, id
                        ],
                        categories=categories,
                    )
    return merge_data

def create_single_annotations( semg_kp_list=[], num_kp=0, area=0, kps=[], image_id=0, bbox_list=[], category_id=0, ann_id=0 ):
    single_annotations = dict(
                                segmentation   = semg_kp_list, # x,y, x,y
                                num_keypoints   = num_kp,
                                area            = area,  # w*h
                                iscrowd         = 0,
                                keypoints       = kps, # x, y ,(0 no, 1, hide, 2 display )
                                image_id        = image_id,
                                bbox            = bbox_list, # [x,y,width,height]
                                category_id     = category_id,
                                id              = ann_id,
                            )
    return single_annotations

def shape_kp_proc( single_shape, kp_name_array, label_names, image_id, ann_id, category_id=0 ):
    single_annotations = None
    if len(single_shape) > 1:
        person_seg = single_shape[ 0 ]
        if label_names == person_seg['label']:
            ann_segmentation=[]
            ann_keypoints=[]
            num_keypoints = 0
            person_seg_points = person_seg['points']
            min_x = person_seg_points[0][0]
            min_y = person_seg_points[0][1] 
            max_x = person_seg_points[0][0]
            max_y = person_seg_points[0][1]
            for index, point in enumerate(person_seg_points):
                ann_segmentation.append( point[ 0 ] ) # x1 y1 x2 y2 x3 y3  ...
                ann_segmentation.append( point[ 1 ] )
                min_x = min( min_x, point[ 0 ] )
                min_y = min( min_y, point[ 1 ] )
                max_x = max( max_x, point[ 0 ] )
                max_y = max( max_y, point[ 1 ] )

            roi_w = max_x - min_x
            roi_h = max_y - min_y

            roi_area = roi_w * roi_h
            iscrowd = 0
            bbox = [ min_x, min_y, roi_w, roi_h ]
        
            for index, kp_name in enumerate( kp_name_array ):
                kp = [ x for x in single_shape if x['label'] == kp_name ]
                if kp is not None and len(kp) > 0:
                    kp_i = kp[0]
                    kp_i_point = kp_i['points']
                    ann_keypoints.append(kp_i_point[0][0])
                    ann_keypoints.append(kp_i_point[0][1])
                    ann_keypoints.append(2)
                    num_keypoints += 1
                else:
                    ann_keypoints.append(0)
                    ann_keypoints.append(0)
                    ann_keypoints.append(0)
            ann_semg_blobs=[]
            ann_semg_blobs.append(ann_segmentation)
            single_annotations = create_single_annotations( ann_semg_blobs, num_keypoints, roi_area, ann_keypoints, image_id, bbox, category_id, ann_id )
            return single_annotations
        else:
            return single_annotations
    else:
        return single_annotations


def load_label_names( label_file ):
    names = []
    with open(label_file, 'r') as name_fb:
        names.clear()
        names_raw = name_fb.readlines()
        for index, name in enumerate(names_raw):
            name_p = name.replace('\n', '')
            name_p = name_p.replace('\r', '')
            names.append( name_p )
    return names

def main( args ):
    classify_names = ['person',]
    kp_names = ["nose","left_eye","right_eye","left_ear","right_ear","left_shoulder","right_shoulder","left_elbow","right_elbow","left_wrist","right_wrist","left_hip","right_hip","left_knee","right_knee","left_ankle","right_ankle"]
    skeleton_list = [[16,14],[14,12],[17,15],[15,13],[12,13],[6,12],[7,13],[6,7],[6,8],[7,9],[8,10],[9,11],[2,3],[1,2],[1,3],[2,4],[3,5],[4,6],[5,7]]

    if '' is not args.kp_names_file:
        kp_names = load_label_names(args.kp_names_file)

    if '' is not  args.names_file:
        classify_names = load_label_names(args.names_file)

    if '' is not  args.skeleton:
        skeleton_list = load_skeleton(args.skeleton)

    json_suf = '*.json'
    load_path = os.path.join( args.load_json_path, json_suf )
    json_list = glob.glob( load_path )


    
    coco_license_file_name = 'coco_license.json'                 

    coco_licenses = None
    with open( coco_license_file_name, 'r') as json_f:
        coco_licenses = json.load( json_f )
        
   
    merge_json = create_coco_merge_dict( classify_names, kp_names, skeleton_list, coco_licenses )

    
    image_id = 0
    for index, single_json in enumerate( tqdm(json_list) ):
        with open(single_json, 'r') as json_f:

            #print( 'proc json file {}'.format( single_json ) )

            labelme_json_data = json.load( json_f )

            image_name = labelme_json_data['imagePath']
            path_L_index = image_name.find('/')
            path_W_index = image_name.find('\\')
            if path_L_index >= 0:
                name_list = image_name.split( '/' )
                image_fix = name_list[ len( name_list ) - 1 ]
            elif path_W_index >= 0:
                name_list = image_name.split( '\\' )
                image_fix = name_list[ len( name_list ) - 1 ]
            else:
                image_fix = image_name

            image_h = labelme_json_data['imageHeight']
            image_w = labelme_json_data['imageWidth']
            image_info = create_single_image_data( jpg_file_name=image_fix, image_height=image_h, image_width=image_w, image_id=image_id )
            merge_json['images'].append(image_info)

            
            
            objs_shapes={}
            shapes = labelme_json_data['shapes']
            for index, shape in enumerate( shapes ):
                group_id = shape.get('group_id')
                if None is group_id:
                    shape['group_id'] = uuid.uuid1()
                    group_id = shape.get('group_id')
                    print('Warning {} no group id'.format(labelme_json_data['imagePath']) )
                if group_id in objs_shapes.keys():
                    objs_shapes[group_id].append(shape)
                else:
                    objs_shapes[group_id]=[]
                    objs_shapes[group_id].append(shape)
                

            for shape_d in objs_shapes:
                ann_semg_blobs = []
                objs_sh = objs_shapes[shape_d]
                min_x = image_w
                min_y = image_h
                max_x = 0
                max_y = 0
                for index, shape_obj in enumerate( objs_sh ):
                    label = shape_obj['label']
                    if label in classify_names:
                        category_id =  classify_names.index(label) + 1
                        ann_segmentation = []
                        person_seg_points = shape_obj['points']
                        '''
                        (x1, y1), (x2, y2) = points
                        x1, x2 = sorted([x1, x2])
                        y1, y2 = sorted([y1, y2])
                        points = [x1, y1, x2, y1, x2, y2, x1, y2]
                        '''
                        if 'polygon' == shape_obj['shape_type']:
                            for index, point in enumerate(person_seg_points):
                                ann_segmentation.append( point[ 0 ] ) # x1 y1 x2 y2 x3 y3  ...
                                ann_segmentation.append( point[ 1 ] )
                                min_x = min( min_x, point[ 0 ] )
                                min_y = min( min_y, point[ 1 ] )
                                max_x = max( max_x, point[ 0 ] )
                                max_y = max( max_y, point[ 1 ] )
                        else:
                            (x1, y1), (x2, y2) = person_seg_points
                            x1, x2 = sorted([x1, x2])
                            y1, y2 = sorted([y1, y2])
                            ann_segmentation = [x1, y1, x2, y1, x2, y2, x1, y2]
                            
                        ann_semg_blobs.append(ann_segmentation)
                num_keypoints=0
                ann_keypoints=[]
                for index, kp_name in enumerate( kp_names ):
                    kp = [ x for x in objs_sh if x['label'] == kp_name ]
                    if kp is not None and len(kp) > 0:
                        kp_i = kp[0]
                        kp_i_point = kp_i['points']
                        ann_keypoints.append(kp_i_point[0][0])
                        ann_keypoints.append(kp_i_point[0][1])
                        ann_keypoints.append(2)
                        num_keypoints += 1
                    else:
                        ann_keypoints.append(0)
                        ann_keypoints.append(0)
                        ann_keypoints.append(0)
                
                roi_w = max_x - min_x
                roi_h = max_y - min_y

                roi_area = roi_w * roi_h
                bbox = [ min_x, min_y, roi_w, roi_h ]
                
                single_annotations = create_single_annotations( ann_semg_blobs, num_keypoints, roi_area, ann_keypoints, image_id, bbox, category_id, ann_id=create_ann_id() )
                merge_json['annotations'].append(single_annotations)
            image_id += 1
    if os.path.exists(args.save_path):
        os.remove( args.save_path )
    with open( args.save_path, 'w' ) as m_f:
        print( 'begin proc {} files, save json {}'.format( image_id, args.save_path ) )
        json.dump( merge_json, m_f, sort_keys=True )
        print( 'end proc {} files, save json {}'.format( image_id, args.save_path ) )

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--load_json_path', type=str, default='/home/fisun/dataset/public/coco_ds/single_kp_ds_all_sample/train2017/json',
                        help='load json file path')

    parser.add_argument('--save_path', type=str,      default='/home/fisun/dataset/public/coco_ds/single_kp_ds_all_sample/train2017/person_keypoints_dsall_train2017.json',
                        help='save coco json path')

    parser.add_argument('--kp_names_file', type=str,  default='key_point_names.txt',
                        help='key point names file')

    parser.add_argument('--names_file', type=str,     default='label_names.txt',
                        help='label names file')

    parser.add_argument('--skeleton', type=str,   default='skeleton_17k.txt',
                        help='skeleton file')

    args = parser.parse_args()
    main(args)
