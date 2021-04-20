import argparse
import json
from tqdm import tqdm
import cv2
import os
import numpy as np

import glob

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

def find_all_index(arr, item):
    return [i for i, a in enumerate(arr) if a == item]

def main(args):
    json_files = load_annotations_file( args.input_annotation_path )
    err_label = []
    corr_label = []

    if None != args.label_corr_names:
        if os.path.exists(args.label_corr_names):
            err_label, corr_label = load_label_correction_names( args.label_corr_names )
        else:
            print('corr names file not exit {} '.format(args.label_corr_names))

    if None != args.check_label_names:
        if os.path.exists(args.check_label_names):
            check_label = load_label_names( args.check_label_names )
        else:
            print('check names file not exit {} '.format(args.check_label_names))
            check_label = None

    all_labels = []
    for index, json_f in enumerate(tqdm(json_files)):
        with open(json_f, 'r') as f:
            json_data = json.load(f)
        
        if None is not json_data:
            is_corr = False
            if args.judeg_filename:
                image_file = os.path.splitext( json_data['imagePath'] )
                src_name = os.path.splitext( os.path.basename(json_f) )

                if src_name[0] != image_file[0]:
                    reset_name = src_name[0] + '.jpg'
                    json_data['imagePath'] = reset_name
                    is_corr = True


            
            shapes = json_data['shapes']
            
            for index, shap in enumerate(shapes):
                label = shap['label']
                if label not in all_labels:
                    all_labels.append(label)
                if label in err_label:
                    err_index = find_all_index(err_label, label)
                    shap['label'] = corr_label[err_index[0]]
                    is_corr = True
                
                if check_label is not None:
                    if label not in check_label:
                        print( 'Error label {} {}'.format(label, json_f) )

                if args.judeg_groupid:
                    group_id = shap['group_id']
                    if group_id is None:
                        print( 'group ID is None {} {}'.format(label, json_f) )
            
            if args.judeg_groupid and args.judeg_label_only:
                t_gl = []
                for index, shap in enumerate(shapes):
                    label = shap['label']
                    group_id = shap['group_id']
                    if group_id is not None:
                        g_label = label+'_'+str(group_id)
                        if g_label not in t_gl:
                            t_gl.append( g_label )
                        else:
                            print( 'label group ID overlap {} {} {}'.format( label, group_id, json_f ) )


                

            if is_corr:
                with open(json_f, 'w') as f:
                    json.dump( json_data, f, indent=4, sort_keys=True)

    print(all_labels)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # person_keypoints_val2017.json person_keypoints_val2017_modified.json
    parser.add_argument('--input_annotation_path',  type=str, default='/home/fisun/dataset/private/fall/kp_20210107', help='annotation src directory')
    '''
    label_corr_names txt file
    jyz-ir jyz_ir
    jyz-kjg jyz_kjg
    height high
    hight high
    '''
    parser.add_argument('--label_corr_names', type=str, default=None,      help='label correction names list path')
    parser.add_argument('--check_label_names', type=str, default='/home/fisun/dataset/private/fall/kp_label_names.txt',      help='label correction names list path')
    parser.add_argument('--judeg_filename', action='store_true', default=True, help='check file name' )
    parser.add_argument('--judeg_groupid',  action='store_true', default=True, help='check file name' )
    parser.add_argument('--judeg_label_only', action='store_true', default=True, help='check file name' )
    args = parser.parse_args()

    main( args )

