import os
import glob
import argparse






def match_file(args):
    labels=os.listdir(args.load_label_path)
    images=os.listdir(args.label_image_path)


    label_funx=[]
    images_funx=[]
    unfind_label=[]
    unfind_image=[]
    rm_files = []
    for index, label in enumerate(labels):

        (filename,extension) = os.path.splitext(label)
        label_funx.append(filename)

    for index, image in enumerate(images):
        (filename,extension) = os.path.splitext(image)
        images_funx.append(filename)



    for index, label_f in enumerate(label_funx):
        if label_f not in images_funx:
            name=labels[index]
            unfind_label.append(name)
            rm_files.append(os.path.join(args.load_label_path, name))

    for index, image_f in enumerate(images_funx):
        if image_f not in label_funx:
            name=images[index]
            unfind_image.append(name)
            rm_files.append(os.path.join(args.label_image_path, name))
    if 'v' in args.proc_model:
        print('unfind match label file')
        print(unfind_label)
        print('unfind match image file')
        print(unfind_image)
        print('please delete file')
        print(rm_files)

    if 'd' in args.proc_model:
        for index, rm_f in enumerate(rm_files):
            if os.path.exists(rm_f):  # 如果文件存在
                print( 'del file {}'.format(rm_f))
                os.remove(rm_f)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_label_path', type=str, default='/home/fisun/dataset/private/comm_bus/annotation_vehicle_person/yolo_dataset/labels',
                        help='load json file path')    

    parser.add_argument('--label_image_path', type=str, default='/home/fisun/dataset/private/comm_bus/annotation_vehicle_person/yolo_dataset/images',
                        help='label file sufix')

    parser.add_argument('--proc_model', type=str,     default='vd',
                        help='v: delete file  v:display file')

    args = parser.parse_args()
    match_file(args)