#统计型脚本
#xml标签存在一些问题，需要进行处理
#1.xml出现意料之外的标签
#2.xml信息丢失，缺少width/height值
#3.图片打开失败　图片损毁
#4.标注框超出实际范围
# -*- coding:utf-8 -*-  
import os
import xml.etree.ElementTree as ET
import random

def show_labels(dirpath):
    filename_list = [ i for i in os.listdir(dirpath) if i.endswith(".xml")]
    fo1 = open("error_filename.txt",'w')#记录xml中filename节点和fp文件名不一致的情形
    fo2 = open("error_chw.txt",'w')#记录fp中chw缺省的情形
    fo3 = open("labels_view.txt",'w')#记录fp中标签分布情形
    label_set = dict()
    for fp in filename_list:
        root = ET.parse(os.path.join(dirpath,fp)).getroot()
        filename = root.find('filename').text#文件中filename
        if fp[:-4]!=filename[:-4]:
            fo1.write("xml_file_name: {}    xml_node_name: {}".format(fp,filename))
            fo1.write("\n")
        sz = root.find('size')
        width = int(sz.find('width').text)
        height = int(sz.find('height').text)
        depth = int(sz.find('depth').text)
        if width==0 or height==0 or depth!=3:
            fo2.write("{}     channel:{} height:{} width:{}".format(fp,depth,height,width))
            fo2.write("\n")

        for child in root.findall('object'):         
            cls_index = child.find('name').text
            if cls_index=="jyz_lw":
                print(fp)
            if cls_index not in label_set:
                label_set[cls_index] = 0
            else:
                label_set[cls_index] +=1   
    for key in label_set.keys():
        fo3.write("{}  {}".format(key,label_set.get(key)))
        fo3.write("\n")
    fo1.close()
    fo2.close()
    fo3.close()


if __name__ == "__main__":
    # voc_dir = "/home/leon/Downloads/reource1/voc_1/"
    voc_dir = "voc_1"
    show_labels(voc_dir)
    print("Done")
