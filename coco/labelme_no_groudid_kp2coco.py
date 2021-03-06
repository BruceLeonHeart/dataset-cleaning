import json
import os
import os.path as osp
import glob
import argparse
import datetime
import pycocotools.mask
import uuid
import collections

g_ann_id = 1

def create_ann_id():
    global g_ann_id
    ids = g_ann_id
    g_ann_id += 1
    return ids

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

def create_coco_merge_dict( kp_names, skeleton_list, coco_licenses ):

    categorie_info = dict(
                            supercategory   = 'person',
                            id              = 1,
                            name            = 'person',
                            keypoints       = kp_names,
                            skeleton        = skeleton_list,
                        )
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
                        categories=[ categorie_info
                            # supercategory, id, name
                        ],
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
            single_annotations = create_single_annotations( ann_segmentation, num_keypoints, roi_area, ann_keypoints, image_id, bbox, category_id, ann_id )
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
            name_p = name.replace('\n','')
            name_p = name_p.replace('\r','')
            names.append( name_p )
    return names

def main( args ):
    classify_names = ['person',]
    kp_names = ["nose","left_eye","right_eye","left_ear","right_ear","left_shoulder","right_shoulder","left_elbow","right_elbow","left_wrist","right_wrist","left_hip","right_hip","left_knee","right_knee","left_ankle","right_ankle"]
    skeleton_list = [[16,14],[14,12],[17,15],[15,13],[12,13],[6,12],[7,13],[6,7],[6,8],[7,9],[8,10],[9,11],[2,3],[1,2],[1,3],[2,4],[3,5],[4,6],[5,7]]

    kp_names = load_label_names(args.kp_names_file)
    if '' is not  args.names_file:
        classify_names = load_label_names(args.names_file)

    json_suf = '*.json'
    load_path = os.path.join( args.load_json_path, json_suf )
    json_list = glob.glob( load_path )

    coco_person_kp_val = 'val2017.json'

    sample_coco_val_f = open(coco_person_kp_val, 'r')
    sample_coco_val_data = json.load( sample_coco_val_f )

    
    coco_license_file_name = 'coco_license.json'                 

    '''
    coco_licenses = dict(
                            licenses = sample_coco_val_data['licenses']
                        )
    with open(coco_license_file_name, 'w') as json_f:
        json.dump(coco_licenses, json_f)
    '''
    coco_licenses = None
    with open( coco_license_file_name, 'r') as json_f:
        coco_licenses = json.load( json_f )
        
    if coco_licenses is not None:
        merge_json = create_coco_merge_dict( kp_names, skeleton_list, coco_licenses )
    else:
        merge_json = create_coco_merge_dict( kp_names, skeleton_list, sample_coco_val_data['licenses'] )
    
    image_id = 0
    ann_id = 0
    for index, single_json in enumerate( json_list ):
        with open(single_json, 'r') as json_f:

            print( 'proc json file {}'.format( single_json ) )

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

            kp_list = []
            shapes = labelme_json_data['shapes']
            for index, shape in enumerate( shapes ):
                if shape['label'] == 'person':
                    if 1 == len(kp_list):
                        kp_list=[] 
                    elif 1 < len(kp_list):
                        single_annotations = shape_kp_proc( single_shape=kp_list, 
                                        kp_name_array=kp_names,
                                        label_names='person', 
                                        image_id=image_id, 
                                        ann_id=create_ann_id(), 
                                        category_id=0 )

                        merge_json['annotations'].append(single_annotations)
                        kp_list=[]


                kp_list.append(shape)
                    
                    
            if len(kp_list) > 1:
                single_annotations = shape_kp_proc( single_shape=kp_list, 
                                kp_name_array=kp_names,
                                label_names='person', 
                                image_id=image_id, 
                                ann_id=create_ann_id(), 
                                category_id=0 )

                merge_json['annotations'].append(single_annotations)

            kp_list=[]

        image_id += 1

    with open( args.save_path, 'w' ) as m_f:
        print( 'proc {} files, save json {}'.format( image_id, args.save_path ) )
        json.dump( merge_json, m_f )



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--load_json_path', type=str, default='/home/fisun/dataset/private/comm_bus/f_Abnormal_behavior_sample20201005/fall_keypoint/annotations',
                        help='load json file path')       

    parser.add_argument('--save_path', type=str,      default='/home/fisun/dataset/private/comm_bus/f_Abnormal_behavior_sample20201005/fall_keypoint/fall_train.json',
                        help='save coco json path')

    parser.add_argument('--kp_names_file', type=str,  default='key_point_names.txt',
                        help='label names file')

    parser.add_argument('--names_file', type=str,     default='label_names.txt',
                        help='label names file')

    args = parser.parse_args()
    main( args )
