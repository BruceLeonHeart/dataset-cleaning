# -*- coding:utf-8 -*-  
import os
import xml.etree.ElementTree as ET
import random

dirpath = './voc_1'     #label xml
train_file = 'train_annotation.txt'
val_file = 'test_annotation.txt'
rate = 0.95

classes = ['sly_bjbmyw','sly_dmyw','jsxs','bj_bjps','yw_gkxfw',\
    'yw_nc','bj_bpmh','hxq_gjbs','jyz','jyz_zc',\
    'jyz_pl','hxq_yfps','hxq_yfzc','hxq_gjzc','bj_zc']


train_txt = open(train_file, 'w')
val_txt = open(val_file, 'w')
xml_list = [i for i in os.listdir(dirpath) if i.endswith(".xml")]
if train_txt is not None and val_txt is not None:
    for fp in xml_list:
        root = ET.parse(os.path.join(dirpath,fp)).getroot()
        xmin, ymin, xmax, ymax = 0,0,0,0
        sz = root.find('size')
        width = float(sz.find('width').text)
        height = float(sz.find('height').text)
        filename = os.path.join(os.path.abspath(dirpath),root.find('filename').text)
        filename = os.path.join(os.path.abspath(dirpath),fp[:-4]+".jpg")  
        write_line = filename
        print(filename)
        for child in root.findall('object'):         

            cls_index = child.find('name').text               
            sub = child.find('bndbox')               
            #xmin = float(sub[0].text)
            #ymin = float(sub[1].text)
            #xmax = float(sub[2].text)
            #ymax = float(sub[3].text)
            xmin = sub.find('xmin').text
            ymin = sub.find('ymin').text
            xmax = sub.find('xmax').text
            ymax = sub.find('ymax').text
            obj_line = xmin + ',' + ymin + ',' + xmax + ',' + ymax +','+ str(classes.index(cls_index))
            write_line += ' '
            write_line += obj_line
        write_line += '\n'
        t_v_rate = random.random()
        if t_v_rate < rate:
            train_txt.write(write_line)
        else:
            val_txt.write(write_line)
train_txt.close()
val_txt.close()
print("Done")