import pycocotools
import cv2
import argparse
from pycocotools.coco import COCO
import os
import skimage.io as io
import matplotlib.pyplot as plt
import numpy
import json



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
    with open(args.annotations_path, 'r') as f:
        coco_json_raw_data = json.load(f)

    label_names = load_label_names(args.calssify_names_file)
    kp_names = load_label_names(args.kp_names_file)

    cocodataset = COCO( args.annotations_path )
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

        image_file_src = os.path.join( args.images_path, img[ 'file_name' ] )
        I = io.imread(image_file_src)
        plt.imshow(I)
        plt.axis('off')
        
        annIds = cocodataset.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
        anns = cocodataset.loadAnns(annIds)

        cocodataset.showAnns(anns)
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotations_path', type=str, default='/home/fisun/dataset/public/coco_ds/person_keypoints_train2017_ods_modified.json', help='Path to COCO annotation json')
    parser.add_argument('--images_path', type=str, default='/home/fisun/dataset/public/coco_ds/single_kp_ds_json_train2017_image', help='Path to save COCO annotation split ')
    parser.add_argument('--calssify_names_file', type=str, default='coco_names.txt', help='COCO classify names')
    parser.add_argument('--kp_names_file', type=str, default='key_point_names.txt', help='key point names file')
    args = parser.parse_args()
    main( args )
