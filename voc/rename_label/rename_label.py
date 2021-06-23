import os
import random
import shutil
import xml.etree.ElementTree as ET
import tqdm
    


origin_label = ["jyz_fh"]
replaced = "jyz_zc"
checkpath = "/dataset/double-light-fuse/0623/2021_6_fh/1/Annotations"
xmls_set = os.listdir(checkpath)

changes = 0
for xmlFile in xmls_set:
    if xmlFile.endswith("xml"):
        xml = open(os.path.join(checkpath,xmlFile),'r+')
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
                if label in origin_label:
                    obj.find('name').text = replaced
                    changes = changes +1
                    tree.write(os.path.join(checkpath,xmlFile),encoding="utf-8")
                    continue

print(str(changes)+ " files CHANGED")