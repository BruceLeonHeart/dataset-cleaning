import argparse
import json
import tqdm
import cv2
import os
import numpy as np
from collections import defaultdict
from pycocotools.coco import COCO
import skimage.io as io
from skimage import transform
import datetime
import collections
import matplotlib.pyplot as plt


point_name = ["nose","left_eye","right_eye","left_ear","right_ear","left_shoulder","right_shoulder","left_elbow","right_elbow","left_wrist","right_wrist","left_hip","right_hip","left_knee","right_knee","left_ankle","right_ankle"]

kp_json_template = {
    "depth": 3,
    "filename": "person0000008",
    "imgHeight": 665,
    "imgWidth": 1000,
    "objects": []
}
bbox_template = {"bbox": [ [ 454, 258 ],[ 735, 584 ] ], 
            'date': '2020-09-12 22:06:18',
            'deleted': 0,
            'draw': True,
            'id': 0,
            'keypoints': [],
            "label": "baggage",
            "point_num": 17,
            "shape_type": "KEYPOINTS",
            "user": "fisun",
            "verified": 0 }


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

def main_proc( args ):
    with open(args.input_annotation_file, 'r') as f:
        data_src = json.load(f)
        print(data_src)

        bbox = {"bbox": [ [ 454, 258 ],[ 735, 584 ] ], 
            'date': '2020-09-12 22:06:18',
            'deleted': 0,
            'draw': True,
            'id': 0,
            'keypoints': [] }


        point=[ 1, 2 ]
        for index, name in enumerate( point_name ):
            kp_index = []
            kp_index.append( name )
            point[ 0 ] = point[0] + index
            point[ 1 ] = point[1] + index
            kp_index.append( point )
            kp_index.append( True )
            bbox["keypoints"].append(kp_index)
        kp_bbox = kp_json_template.copy()
        kp_bbox['objects'] = bbox

        with open(args.output_annotation_file, 'w') as result_file:
            json.dump(kp_bbox, result_file, indent=4, sort_keys=True)
        

def create_coco_shape( label_name, points=[], group_id=1, shape_type='polygon' ):
    shape_data = dict(
            label=label_name,
            points=points,
            group_id=group_id,
            shape_type=shape_type,
            flags={}
        )
    return shape_data

def create_coco_json_dict( shapes=[], image_path='', image_h=0, image_w=0 ):

    json_data = collections.OrderedDict(
                    version="4.5.6",
                    flags={},
                    shapes=shapes,
                    imagePath=image_path,
                    imageData=None,
                    imageHeight=image_h,
                    imageWidth=image_w,)
    return json_data

def save_coco_polygons_json_kp( img, classifys, kp_names, anns, save_path ):
    '''
    sample_json = 'sample/annotations/fall2_139.json'
    with open(sample_json, 'r') as json_file:
        json_sample_data=json.load(json_file)
    '''
    # 000000000872
    jpg_file = img[ 'file_name' ]
    fic = jpg_file.find('000000000872')
    if fic >= 0:
        jpg_file += 'jpg_file'

    shapes = []
    for g_id, ann in enumerate(anns):
        label_name = classifys[ann['category_id']-1]
        group_id = g_id + 1
        
        if 'segmentation' in ann:
            blobs = ann['segmentation']
            
            num_kp = ann['num_keypoints']
            if num_kp > 0:
                
                for b_index, blob in enumerate(blobs):
                    points=[]
                    for p_d_i in range(0,len(blob),2):
                        point = [blob[p_d_i], blob[p_d_i+1]]
                        points.append(point)

                    shape = create_coco_shape(label_name=label_name,points=points,group_id=group_id)
                    shapes.append(shape)

                keypoints=ann['keypoints']

            
                for kp_index in range(0,len(keypoints),3):
                    point=[[keypoints[kp_index], keypoints[kp_index + 1]]]
                    kp_en = int(keypoints[kp_index + 2])
                    kp_name = kp_names[int(kp_index/3)]
                    
                    if 2 == kp_en:
                        shape = create_coco_shape(label_name=kp_name,points=point,group_id=group_id, shape_type='point')
                        shapes.append(shape)



    output_json = os.path.join( save_path, img[ 'file_name' ] )
    output_json = output_json.replace( '.jpg', '.json' )
    output_json = output_json.replace( '.JPG', '.json' )
    output_json = output_json.replace( '.png', '.json' )
    output_json = output_json.replace( '.JPEG', '.json' )
    output_json = output_json.replace( '.PNG', '.json' )
    if len(shapes) > 0:
        image_path_s = '.\\' + img['file_name']
        save_json_data = create_coco_json_dict(shapes=shapes, image_path=image_path_s, image_h=img['height'], image_w=img['width'])
        with open( output_json, 'w') as result_file:
            json.dump( save_json_data, result_file, indent=4, sort_keys=True)



def save_coco_RLE_json_kp( img, anns, save_path ):
    kp_json = {
        "depth": 3,
        "filename": "person0000008",
        "imgHeight": 665,
        "imgWidth": 1000,
        "objects": []
    }
    kp_json[ 'filename' ]  = img[ 'file_name' ]
    kp_json[ 'imgHeight' ] = img[ 'height' ]
    kp_json[ 'imgWidth' ]  = img[ 'width' ]
    
    bboxes=[]
    id_index = 0
    for index_anns, ann in enumerate(anns):
        bbox = {'bbox': [ [ 454, 258 ],[ 735, 584 ] ], 
                'date': '2020-09-12 22:06:18',
                'deleted': 0,
                'draw': True,
                'id': 0,
                'keypoints': [],
                'label': 'baggage',
                'point_num': 17,
                'shape_type': 'KEYPOINTS',
                'user': 'fisun',
                'verified': 0
             }

        bbox_src = ann['bbox']
        bbox[ 'bbox' ] = [ [ bbox_src[0], bbox_src[1] ], [ bbox_src[2] + bbox_src[0], bbox_src[3] + bbox_src[1]] ]
        bbox[ 'date' ] = img[ 'date_captured' ]
        bbox[ 'id' ] = index_anns
        bbox[ 'date'] =datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        coco_kps = ann[ 'keypoints' ]
        kp_en_size = 0
        for index, name in enumerate( point_name ):
            kp_index = []
            kp_index.append( name )
            point=[ 1, 2 ]
            point[ 0 ] = coco_kps[ index * 3 ]
            point[ 1 ] = coco_kps[ index * 3 + 1 ]
            kp_index.append( point )
            if 2 is coco_kps[ index * 3 + 2 ]:
                kp_index.append( True )
                kp_en_size += 1
            else:
                kp_index.append( False )
            bbox["keypoints"].append(kp_index)
        if kp_en_size > 0:
            bbox[ 'id' ] = id_index
            bboxes.append(bbox)
            id_index += 1
    kp_json[ 'objects' ] = bboxes

    output_json = os.path.join( save_path, img[ 'file_name' ] )
    output_json = output_json.replace( '.jpg', '.json' )
    output_json = output_json.replace( '.JPG', '.json' )
    output_json = output_json.replace( '.png', '.json' )
    output_json = output_json.replace( '.JPEG', '.json' )
    output_json = output_json.replace( '.PNG', '.json' )
    with open( output_json, 'w') as result_file:
            json.dump( kp_json, result_file, indent=4, sort_keys=True)
        

def main_split( args ):
    label_names = load_label_names(args.calssify_names_file)
    kp_names = load_label_names(args.kp_names_file)

    if not os.path.exists(args.output_annotation_path):
        os.makedirs(args.output_annotation_path)


    cocodataset = COCO( args.input_annotation_file )
    cocodataset.info()
    imgs = cocodataset.imgs

    cats = cocodataset.loadCats(cocodataset.getCatIds())
    nms = [cat['name'] for cat in cats]
    print('COCO categories: \n{}\n'.format(' '.join(nms)))

    nms = set([cat['supercategory'] for cat in cats])
    print('COCO supercategories: \n{}'.format(' '.join(nms)))

    catIds = cocodataset.getCatIds(catNms=['person'])
    imgIds = cocodataset.getImgIds(catIds=catIds)

    for index, img_id in enumerate(imgIds):
        img = cocodataset.loadImgs( img_id )[0]
        # image_file_src = os.path.join( args.input_image_file, img[ 'file_name' ] )
        # I = io.imread(image_file_src)
        # plt.imshow(I)
        # plt.axis('off')
        annIds = cocodataset.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
        anns = cocodataset.loadAnns(annIds)
        save_coco_polygons_json_kp( img, label_names, kp_names, anns, args.output_annotation_path )
        # save_coco_json_kp( img, anns, args.output_annotation_path )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_annotation_file', type=str, default='/home/fisun/old_home/fisun/dataset/public/coco_ds/annotations/person_keypoints_val2017.json', help='Path to COCO annotation json')
    parser.add_argument('--output_annotation_path', type=str, default='/home/fisun/old_home/fisun/dataset/public/coco_ds/split_json_val2017', help='Path to save COCO annotation split ')
    parser.add_argument('--calssify_names_file', type=str, default='coco_names.txt', help='COCO classify names')
    parser.add_argument('--kp_names_file', type=str, default='key_point_names.txt', help='key point names file')
    args = parser.parse_args()
    main_split( args )


    