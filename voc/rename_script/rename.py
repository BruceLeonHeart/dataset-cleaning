#-*- coding:utf-8 -*-
import os
import shutil
import argparse
import sys
from tqdm import tqdm

'''
    usage: python merge_img_xml.py --img_dir /img_dir --xml_dir /xml_dir --dest_dir /dest_dir
    -----------------------------------------------------------------------------------------
    jpg_dir:图片存放位置
    xml_dir:VOC格式的xml文件存放位置
    dest_dir:合并文件后所在的位置
    命名规范为: 公司名 + 项目编号 + 编号
    公司名:SJZD
    项目编号:01
    图片编号:000001 [从1开始，六位数]
    示范:SJZD_01_000001.jpg
    SJZD_01_000001.xml
'''

#本批数据集起始编号
N = 1
company_name = "SJZD"
pro_num = "02"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir',type=str,default="/dataset/fenhua/trainset/VOC_dataset_copy/JPEGImages/")
    parser.add_argument('--xml_dir',type=str,default="/dataset/fenhua/trainset/VOC_dataset_copy/Annotations/")
    parser.add_argument('--dest_dir',type=str,default="/dataset/fenhua/trainset/VOC_dataset_copy/merge")
    opt = parser.parse_args()
    #三个参数均不可以为空
    if None == (opt.img_dir or opt.xml_dir or opt.dest_dir):
        print("检查输入参数,输入格式为'python '!")
    #os.listdir()返回字典,排序后确认是否图和标注是否配套
    #jpgs_list = [i for i in os.listdir(opt.jpg_dir).sort()]
    imgs_set = os.listdir(opt.img_dir)
    xmls_set = os.listdir(opt.xml_dir)
    imgs_set.sort()
    xmls_set.sort()
    # imgs_list = [i for i in os.listdir(opt.img_dir).sort()]
    # xmls_list = [i for i in os.listdir(opt.xml_dir).sort()]
    imgs_list = imgs_set
    xmls_list = xmls_set
    imgs_list_withoutend = [i.split('.')[0] for i in imgs_list]
    xmls_list_withoutend = [i.split('.')[0] for i in xmls_list]
    if imgs_list_withoutend!=xmls_list_withoutend:
        print("图片和标签文件名不匹配，请检查！")
        sys.exit()
    
    #目标文件夹不存在就创建
    if not os.path.exists(opt.dest_dir):
        os.mkdir(opt.dest_dir)
    for i in tqdm(imgs_list): 
        start_num =  str(N).zfill(6)       
        file_name = i.split('.')[0]#不带拓展名文件
        img_end_name = i.split('.')[1]#图片拓展名
        xml_end_name = 'json'#标注拓展名
        new_file_name = company_name + "_" + pro_num + "_" + start_num
        N +=1
        img_src = os.path.join(opt.img_dir,i)
        xml_src = os.path.join(opt.xml_dir,file_name + "." + xml_end_name)
        img_dst = os.path.join(opt.dest_dir,new_file_name + "." + img_end_name)
        xml_dst = os.path.join(opt.dest_dir,new_file_name + "." + xml_end_name)
        # shutil.move(jpg_src,jpg_dst)
        # shutil.move(xml_src,xml_dst)
        shutil.copy(img_src,img_dst)
        shutil.copy(xml_src,xml_dst)
    print("Done")