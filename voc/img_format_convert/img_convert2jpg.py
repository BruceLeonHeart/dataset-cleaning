#-*- coding:utf-8 -*-
import os
import argparse
from PIL import Image
import shutil

'''
    usage: python img_convert2jpg.py --img_dir /img_dir  --dest_dir /dest_dir
    -----------------------------------------------------------------------------------------
    img_dir:图片存放位置[保证内部全为图片，无其他文件]
    dest_dir:合并文件后所在的位置
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir',type=str)
    parser.add_argument('--dest_dir',type=str)
    opt = parser.parse_args()
    if None == (opt.img_dir or opt.dest_dir):
        print("检查输入参数,输入格式为'python '!")
    #目标文件夹不存在就创建
    if not os.path.exists(opt.dest_dir):
        os.mkdir(opt.dest_dir)
    imgs_set = os.listdir(opt.img_dir)
    for img in imgs_set:
        src = os.path.join(opt.img_dir,img)#原图
        dest = os.path.join(opt.dest_dir,os.path.splitext(img) + ".jpg")#最终的存储文件
        #大小写直接重命名处理
        if img.endswith("JPG"):
            shutil.copy(src,dest)
        else:
            try:
                image = Image.open(src)            
                image.save(dest,quality=100)
            except:
                print("image to jpg fail")

    print("Done")

    