import os
import random
import shutil
import xml.etree.ElementTree as ET
    
#检查标注文件中存在标签错误或者标签遗漏的情形

right_label = ["jyz_zc"]
checkpath = "/dataset/fenhua/20210309/guoyan/zc_merge_"
xmls_set = os.listdir(checkpath)

for xmlFile in xmls_set:
    if xmlFile.endswith("xml"):
        xml = open(os.path.join(checkpath,xmlFile),'r')
        tree = ET.parse(xml)
        root = tree.getroot()
        # object_list = root.find('object').text
        if None == root.find('object'):
            print("空标签文件 :{}".format(xmlFile))
            continue
        else:
            for obj in root.iter('object'):
                difficult = obj.find('difficult').text
                label = obj.find('name').text
                if label not in right_label or int(difficult) == 1:
                    print("标签与预期不一致 :{}".format(xmlFile))
                    continue
