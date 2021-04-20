import pycocotools
import cv2
import argparse
from pycocotools.coco import COCO
import os
import skimage.io as io
import matplotlib.pyplot as plt
import numpy
import json
import glob


def load_annotations_file( annotation_path ):
    load_pt = annotation_path + '/*.json'
    file_list = glob.glob( load_pt )
    return file_list

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


def save_kp_list_txt( single_json, save_dir, persen_kps ):
    fp_l = single_json.split('/')
    s_j_f = fp_l[len(fp_l)-1]
    file_fix_index = s_j_f.rfind('.')

    file_fix = s_j_f[:file_fix_index]
    
    for index, kp_i in enumerate(persen_kps):
        save_file = file_fix + '_{}.json'.format(index)
        save_path = os.path.join(save_dir, save_file)
        with open(save_path, "w") as f:
            json.dump(kp_i, f, indent = 4, sort_keys = True)





def proc_json2train_list( single_json, save_path, kp_names, classify_label, lass_kp_num ):
    with open(single_json, 'r') as json_f:
        labelme_json_data = json.load( json_f )

        objs_shapes={}
        image_h = labelme_json_data['imageHeight']
        image_w = labelme_json_data['imageWidth']
        shapes = labelme_json_data['shapes']
        for index, shape in enumerate( shapes ):
            label_name = shape['label']
            if label_name in kp_names or label_name in classify_label:
                group_id = shape.get("group_id")
                if group_id in objs_shapes.keys():
                    objs_shapes[group_id].append(shape)
                else:
                    objs_shapes[group_id]=[]
                    objs_shapes[group_id].append(shape)
            


        
        persen_kps=[]
        for shape_d in objs_shapes:
   
            objs_sh = objs_shapes[shape_d]
            
            kp_minx = image_w
            kp_miny = image_h
            kp_maxx = 0
            kp_maxy = 0
            kp_num = 0
            ann_keypoints=[]
            for index, kp_name in enumerate( kp_names ):
                if 'neck' != kp_name:
                    kp = [ x for x in objs_sh if x['label'] == kp_name ]
                    if kp is not None and len(kp) > 0:
                        kp_i = kp[0]
                        kp_i_point = kp_i['points']
                        kp_ix = kp_i_point[0][0]
                        kp_iy = kp_i_point[0][1]

                        ann_keypoints.append(kp_ix)
                        ann_keypoints.append(kp_iy)
                        ann_keypoints.append(2)
                        
                        kp_minx = min(kp_minx,kp_ix)
                        kp_miny = min(kp_miny,kp_iy)
                        kp_maxx = max(kp_maxx,kp_ix)
                        kp_maxy = max(kp_maxy,kp_iy)
                        kp_num += 1
                    else:
                        ann_keypoints.append(0)
                        ann_keypoints.append(0)
                        ann_keypoints.append(0)

                else:
                    kp = [ x for x in objs_sh if x['label'] == kp_name ]
                    if kp is not None and len(kp) > 0:
                        kp_i = kp[0]
                        kp_i_point = kp_i['points']
                        kp_ix = kp_i_point[0][0]
                        kp_iy = kp_i_point[0][1]

                        ann_keypoints.append(kp_ix)
                        ann_keypoints.append(kp_iy)
                        ann_keypoints.append(2)
                        
                        kp_minx = min(kp_minx,kp_ix)
                        kp_miny = min(kp_miny,kp_iy)
                        kp_maxx = max(kp_maxx,kp_ix)
                        kp_maxy = max(kp_maxy,kp_iy)
                        kp_num += 1
                    else:
                        left_shoulder_name = 'left_shoulder'
                        left_shoulder_kp = [ x for x in objs_sh if x['label'] == left_shoulder_name ]
                        right_shoulder_name = 'right_shoulder'
                        right_shoulder_kp = [ x for x in objs_sh if x['label'] == right_shoulder_name ]

                        if left_shoulder_kp is not None and len(left_shoulder_kp) > 0 and right_shoulder_kp is not None and len(right_shoulder_kp) > 0:

                            left_shoulder_kp_i = left_shoulder_kp[0]
                            left_shoulder_kp_i_point = left_shoulder_kp_i['points']
                            left_shoulder_kp_ix = left_shoulder_kp_i_point[0][0]
                            left_shoulder_kp_iy = left_shoulder_kp_i_point[0][1]

                            right_shoulder_kp_i = right_shoulder_kp[0]
                            right_shoulder_kp_i_point = right_shoulder_kp_i['points']
                            right_shoulder_kp_ix = right_shoulder_kp_i_point[0][0]
                            right_shoulder_kp_iy = right_shoulder_kp_i_point[0][1]

                            kp_minx = min(kp_minx,left_shoulder_kp_ix)
                            kp_miny = min(kp_miny,left_shoulder_kp_iy)
                            kp_maxx = max(kp_maxx,left_shoulder_kp_ix)
                            kp_maxy = max(kp_maxy,left_shoulder_kp_iy)

                            kp_minx = min(kp_minx,right_shoulder_kp_ix)
                            kp_miny = min(kp_miny,right_shoulder_kp_iy)
                            kp_maxx = max(kp_maxx,right_shoulder_kp_ix)
                            kp_maxy = max(kp_maxy,right_shoulder_kp_iy)

                            ann_keypoints.append((left_shoulder_kp_ix + right_shoulder_kp_ix) / 2.0)
                            ann_keypoints.append((left_shoulder_kp_iy + right_shoulder_kp_iy) / 2.0)
                            ann_keypoints.append(2)
                            kp_num += 1
                        else:
                            ann_keypoints.append(0)
                            ann_keypoints.append(0)
                            ann_keypoints.append(0)
            # save list
            classify = 0
            for index, label in enumerate( classify_label ):
                cla = [ x for x in objs_sh if x['label'] == label ]
                if cla is not None and len(cla) > 0:
                   classify = index

            if kp_num >= lass_kp_num:
                person_kp_info = dict(
                                    classify = classify,
                                    image_w = image_w,
                                    image_h = image_h,
                                    kp_min_x = kp_minx,
                                    kp_min_y = kp_miny,
                                    kp_max_x = kp_maxx,
                                    kp_max_y = kp_maxy,
                                    person_kpl = ann_keypoints,
                                    kp_number = kp_num
                                    )

                persen_kps.append(person_kp_info)

        save_kp_list_txt( single_json, save_path, persen_kps)

                    
def main(args):
    names = ['nose','left_eye','right_eye','left_ear','right_ear','left_shoulder','right_shoulder','left_elbow','right_elbow','left_wrist','right_wrist','left_hip','right_hip','left_knee','right_knee','left_ankle','right_ankle','neck']
    status_label = ['person', 'fall']
    if os.path.exists( args.classify  ):
        status_label = load_label_names( args.classify )

    json_files = load_annotations_file( args.input_json_path )

    if args.kp_names_file is not None and '' != args.kp_names_file:
        names = load_label_names( args.kp_names_file )

    if len(json_files) > 0:
        if not os.path.exists(args.save_path):
            os.makedirs(args.save_path)    

        for index, json_file in enumerate(json_files):
            proc_json2train_list( json_file, args.save_path, names, status_label, args.lass_kpnum )









if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json_path', type=str, default='/home/fisun/dataset/public/coco_ds/split_json_val2017', help='Path to COCO annotation json')
    parser.add_argument('--save_path',       type=str, default='/home/fisun/dataset/public/coco_ds/kp_fall_classies_sample/merage', help='Path to save COCO annotation split ')
    parser.add_argument('--kp_names_file',   type=str, default='fall_class_kp_name_list.txt', help='key point names file')
    parser.add_argument('--classify',        type=str, default='label_names.txt', help='classify index 0 normail 1 fall')
    parser.add_argument('--lass_kpnum',      type=int, default=7, help='more than this is legal dataset')
    args = parser.parse_args()
    main( args )
    