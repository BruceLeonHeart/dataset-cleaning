#-*- coding:utf-8 -*-
import os
import shutil
import argparse

'''
    usage: python merge_img_xml.py --img_dir /img_dir --xml_dir /xml_dir --dest_dir /dest_dir
    -----------------------------------------------------------------------------------------
    jpg_dir:图片存放位置
    xml_dir:VOC格式的xml文件存放位置
    dest_dir:合并文件后所在的位置
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir',type=str,default='/home/al/dataset/double-light-fuse/0623/2021_6_fh/2/JPEGImages')
    parser.add_argument('--xml_dir',type=str,default='/home/al/dataset/double-light-fuse/0623/2021_6_fh/2/Annotations')
    parser.add_argument('--dest_dir',type=str,default='/home/al/dataset/double-light-fuse/0623/2021_6_fh/2/merge')
    opt = parser.parse_args()
    #三个参数均不可以为空
    if None == (opt.img_dir or opt.xml_dir or opt.dest_dir):
        print("检查输入参数,输入格式为'python '!")
    #os.listdir()返回字典,这里不排序提升运行速度
    #jpgs_list = [i for i in os.listdir(opt.jpg_dir).sort()]
    imgs_set = [i for i in os.listdir(opt.img_dir)]
    xmls_set = [i for i in os.listdir(opt.xml_dir)]
    #目标文件夹不存在就创建
    if not os.path.exists(opt.dest_dir):
        os.mkdir(opt.dest_dir)
    N = 0#用于统计配对数目
    for i in imgs_set:
        for j in xmls_set:
            #按点分割不带拓展名的文件名
            img_name = i.split('.')[0]
            xml_name = j.split('.')[0]
            if xml_name==img_name:
                N+=1
                jpg_src = os.path.join(opt.img_dir,i)
                xml_src = os.path.join(opt.xml_dir,j)
                jpg_dst = os.path.join(opt.dest_dir,i)
                xml_dst = os.path.join(opt.dest_dir,j)
                shutil.move(jpg_src,jpg_dst)
                shutil.move(xml_src,xml_dst)
                # shutil.copy(jpg_src,jpg_dst)
                # shutil.copy(xml_src,xml_dst)   
    print("you got {} couple data".format(N))
    print("Done")
