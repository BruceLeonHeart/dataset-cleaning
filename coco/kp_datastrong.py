import argparse
import json
from tqdm import tqdm
import cv2
import os
import os.path as osp
import numpy as np
from collections import defaultdict
from pycocotools.coco import COCO
import skimage.io as io
from skimage import transform

import matplotlib.pyplot as plt
import glob
import math
import copy
from shutil import copyfile



def load_annotations_file( annotation_path ):
    load_pt = annotation_path + '/*.json'
    file_list = glob.glob( load_pt )
    return file_list


def centor_rotate_angle( point, roate_angle, src_image_w, src_image_h ):

    angle = roate_angle * math.pi / 180
    src_cent_x = src_image_w/2
    src_cent_y = src_image_h/2

    p_line = [ point[0] - src_cent_x , point[1] - src_cent_y ]

    ro_point_x = p_line[0] * math.cos(angle) - p_line[1] * math.sin(angle)
    ro_point_y = p_line[0] * math.sin(angle) + p_line[1] * math.cos(angle)

    roat_point = [ro_point_x, ro_point_y]

    return roat_point



def points_roate_angle( points, roate_angle, src_image_w, src_image_h ):
    roate_points=[]
    for index, point in enumerate(points):
        roate_point = centor_rotate_angle( point, roate_angle, src_image_w, src_image_h )
        roate_points.append(roate_point)


    return roate_points


def rotate_bound(image, angle):
    
    # grab the dimensions of the image and then determine the

    # center

    (h, w) = image.shape[:2]

    (cX, cY) = (w // 2, h // 2)

 

    # grab the rotation matrix (applying the negative of the

    # angle to rotate clockwise), then grab the sine and cosine

    # (i.e., the rotation components of the matrix)

    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)

    cos = np.abs(M[0, 0])

    sin = np.abs(M[0, 1])

 

    # compute the new bounding dimensions of the image

    nW = int((h * sin) + (w * cos))

    nH = int((h * cos) + (w * sin))

 

    # adjust the rotation matrix to take into account translation

    M[0, 2] += (nW / 2) - cX

    M[1, 2] += (nH / 2) - cY

 

    # perform the actual rotation and return the image

    return cv2.warpAffine(image, M, (nW, nH))


def load_label_correction_names( label_file ):
    err_label = []
    corr_label = []

    with open(label_file, 'r') as name_fb:

        names_raw = name_fb.readlines()
        for index, name in enumerate(names_raw):
            name_p = name.replace('\n','')
            name_p = name_p.replace('\r','')
            cor_l = name_p.split(' ')
            err_label.append(cor_l[0])
            corr_label.append(cor_l[1])

    return err_label, corr_label

def find_all_index(arr, item):
    return [i for i, a in enumerate(arr) if a == item]

def kp_data_strong( src_json, image_path, save_json_path, save_image_path, rotates=[90,180,270], old_labels=None, corr_labels=None ):
    
    with open( src_json, 'r' ) as src_f:
        json_data = json.load(src_f)

        image_w = json_data['imageWidth']
        image_h = json_data['imageHeight']
        src_jpg_file_path = json_data['imagePath']
        path_L_index = src_jpg_file_path.find('/')
        path_W_index = src_jpg_file_path.find('\\')
        if path_L_index >= 0:
            name_list = src_jpg_file_path.split( '/' )
            src_jpg_image_name = name_list[ len( name_list ) - 1 ]
        elif path_W_index >= 0:
            name_list = src_jpg_file_path.split( '\\' )
            src_jpg_image_name = name_list[ len( name_list ) - 1 ]
        else:
            src_jpg_image_name = src_jpg_file_path
        
        
    
        base_name_base = osp.splitext(osp.basename(src_json))[0]

        src_image_path = os.path.join( image_path, src_jpg_image_name )
        copy_image_path = os.path.join( save_image_path, src_jpg_image_name )
        copyfile(src_image_path, copy_image_path )

        dis_t_json = base_name_base + '.json'
        copy_json_path = os.path.join( save_json_path, dis_t_json )
        copyfile(src_json, copy_json_path )

        image_rect = [ [0, 0], [0, image_h], [image_w,0], [image_w, image_h] ]
        for index, rotate in enumerate(rotates):
            
            rotate_image_rect = points_roate_angle(image_rect, rotate, image_w, image_h)
            min_x = rotate_image_rect[0][0]
            min_y = rotate_image_rect[0][1]
            max_x = rotate_image_rect[0][0]
            max_y = rotate_image_rect[0][1]

            for rotate_index, rotate_point in enumerate(rotate_image_rect):
                min_x = min(min_x, rotate_point[0])
                min_y = min(min_y, rotate_point[1])
                max_x = max(max_x, rotate_point[0])
                max_y = max(max_y, rotate_point[1])

            rotate_image_w = max_x - min_x
            rotate_image_h = max_y - min_y

            offset_roate_x = rotate_image_w / 2
            offset_roate_y = rotate_image_h / 2

            json_data_rotate = copy.deepcopy(json_data)

            rotate_shapes = json_data_rotate['shapes']

            json_data_rotate['imageWidth'] = rotate_image_w
            json_data_rotate['imageHeight'] = rotate_image_h
            
            for index, shape in enumerate(rotate_shapes):
                label = shape['label']
                if old_labels is not None and label in old_labels:
                    err_index = find_all_index(old_labels, label)
                    shape['label'] = corr_labels[err_index[0]]
                src_points = shape['points']
                rotates_points = points_roate_angle(src_points, rotate, image_w, image_h)

                for p_r_i, r_point in enumerate(rotates_points):
                    r_point[0] += offset_roate_x
                    r_point[1] += offset_roate_y

                shape['points']=rotates_points

                rotate_shapes[index] = shape

            

            
            src_img = cv2.imread(src_image_path)

            rotate_jpg = rotate_bound(src_img, rotate)

            
            ds_base_image_name = base_name_base+ '_ro' + str(rotate) + '.jpg'
            ds_jpeg_file_name = os.path.join( save_image_path, ds_base_image_name )

            ds_base_json_name = base_name_base+ '_ro' + str(rotate) + '.json'
            ds_json_file_name = os.path.join( save_json_path, ds_base_json_name )

            cv2.imwrite(ds_jpeg_file_name, rotate_jpg, [int( cv2.IMWRITE_JPEG_QUALITY), 92])   
            json_data_rotate['imagePath'] = '.\\' + ds_base_image_name
            with open(ds_json_file_name, 'w') as save_json_f:
                json.dump(json_data_rotate, save_json_f, indent=4, sort_keys=False)


def main(args):
    json_files = load_annotations_file( args.input_annotation_path )
    old_label, corr_label = load_label_correction_names( args.relable )
    
    if not os.path.exists(args.output_annotation_path):
        os.makedirs(args.output_annotation_path)

    if not os.path.exists(args.output_image_path):
        os.makedirs(args.output_image_path)

    count = 0
    for json_index, json_file in enumerate( tqdm(json_files) ):
        kp_data_strong(json_file, args.input_image_path, args.output_annotation_path, args.output_image_path, old_labels=old_label, corr_labels=corr_label )
        count += 1
    print( 'proc file count:{}'.format(count) )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # person_keypoints_val2017.json person_keypoints_val2017_modified.json
    parser.add_argument('--input_annotation_path',  type=str, default='/home/fisun/dataset/public/coco_ds/split_json_val2017', help='annotation src directory')
    parser.add_argument('--input_image_path',       type=str, default='/home/fisun/dataset/public/coco_ds/val2017', help='image src directory')
    parser.add_argument('--output_annotation_path', type=str, default='/home/fisun/dataset/public/coco_ds/single_kp_ds_all_sample/val2017/json',   help='output data strong annotations path')
    parser.add_argument('--output_image_path',      type=str, default='/home/fisun/dataset/public/coco_ds/single_kp_ds_all_sample/val2017/images', help='output data strong image path')
    parser.add_argument('--relable',                type=str, default='/home/fisun/dataset/public/coco_ds/relable.txt',        help='dadastrong rename label')


    args = parser.parse_args()

    main( args )

