在标注过程中，往往由于标注人员失误、或者图片本身存储失败 等因素导致jpg数目和xml数目不一致
此脚本用于提取xml文件夹和jpg文件夹中相对应的文件。

usage: python merge_img_xml.py --img_dir /img_dir --xml_dir /xml_dir --dest_dir /dest_dir
-----------------------------------------------------------------------------------------
jpg_dir:图片存放位置
xml_dir:VOC格式的xml文件存放位置
dest_dir:合并文件后所在的位置
