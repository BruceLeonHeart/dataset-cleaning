import json
import os
import glob
import argparse

def convert_coordinates(size, box):
    dw = 1.0/size[0]
    dh = 1.0/size[1]
    x = (box[0]+box[1])/2.0
    y = (box[2]+box[3])/2.0
    w = box[1]-box[0]
    h = box[3]-box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_yolo_label( image_w, image_h, annotations, names, file_name, save_path ):
    save_file = os.path.join( save_path, file_name )
    
    with open(save_file, "w") as yolo_f:
  
        for index, annotation in enumerate(annotations):
        
            label = annotation['label']
            if 'rectangle' == annotation['shape_type']:
                points = annotation['points']
                p1 = points[0]
                p2 = points[1]

                min_x = min(p1[0],p2[0])
                min_y = min(p1[1],p2[1])
                max_x = max(p1[0],p2[0])
                max_y = max(p1[1],p2[1])

                image_size = (float(image_w),float(image_h))
                box = (min_x,max_x,min_y,max_y)
                bb = convert_coordinates(image_size, box)
                class_idx = names.index(label)
                if class_idx >= 0:
                    yolo_f.write(str(class_idx) + " " + " ".join([("%.6f" % a) for a in bb]) + '\n')
                else:
                    raise IndexError('{} not in names {}'.format(label, names))


            else:
                print( 'shape_type not rectangle' )
                raise IndexError("shape_type not rectangle")

def main( args ):
    json_suf = '*.json'

    load_path = os.path.join( args.load_json_path, json_suf )
    json_list = glob.glob( load_path )

    names = ['person', 'vehicle']
    with open(args.names_file, 'r') as name_fb:
        names.clear()
        names_raw = name_fb.readlines()
        for index, name in enumerate(names_raw):
            name_p = name.replace('\n','')
            name_p = name_p.replace('\r','')
            names.append( name_p )
      

    for index, json_file in enumerate(json_list):
        print(json_file)

        with open(json_file, 'r') as f:
            json_data = json.load(f)
            image_w = json_data['imageWidth']
            image_h = json_data['imageHeight']
            label_shapes=json_data['shapes']

    
            label_name = json_file.split('/')
            yolo_label_txt = label_name[ len(label_name) - 1 ]
            yolo_label_txt = yolo_label_txt.replace( '.json', '.txt')

            # print(json_data)
            convert_yolo_label( image_w, image_h, label_shapes, names, yolo_label_txt, args.save_path )




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--load_json_path', type=str, default='/home/fisun/dataset/private/fall/abnormal_items_20210102/Gathering',
                        help='load json file path')       

    parser.add_argument('--save_path', type=str,      default='/home/fisun/dataset/private/fall/abnormal_items_20210102/yolo_label',
                        help='save yolo label path')

    parser.add_argument('--names_file', type=str,     default='/home/fisun/dataset/private/fall/abnormal_items_20210102/label_names.txt',
                        help='label names file')

    args = parser.parse_args()
    main(args)

    


