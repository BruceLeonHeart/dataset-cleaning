import os
import random
import shutil
import xml.etree.ElementTree as ET
from tqdm import tqdm


def cutSuffix(fileList, suffix):
    nameList = []
    for file in fileList:
        name, suffix_ = os.path.splitext(file)
        if suffix_ != '.' + suffix:
            print(file, 'is not a', suffix, 'file')
            return None
        nameList.append(name)
    return nameList


def checkDatasets(datasetsDir):
    if not os.path.exists(datasetsDir):
        print('source Dataset', datasetsDir, 'is not existed')
        return None
    if not os.path.exists(os.path.join(datasetsDir, 'Annotations')):
        print('Annotations folder is not existed')
        return None
    if not os.path.exists(os.path.join(datasetsDir, 'JPEGImages')):
        print('JPEGImages folder is not existed')
        return None

    annoDir = os.path.join(datasetsDir, 'Annotations')
    imgDir = os.path.join(datasetsDir, 'JPEGImages')
    annoFileList = os.listdir(annoDir)
    imgFileList = os.listdir(imgDir)

    annoNameList = cutSuffix(annoFileList, 'xml')
    if annoNameList is None:
        return None
    imgNameList = cutSuffix(imgFileList, 'jpg')
    if imgNameList is None:
        return None

    for anno in annoNameList:
        if anno not in imgNameList:
            print(anno, 'xml file is not in JPEGImages')
            return None

    for img in imgNameList:
        if img not in annoNameList:
            print(img, 'img file is not in Annotations')
            return None

    return annoNameList


def initDataSpace(datasetName):
    print('create the dataset folder:', datasetName)
    os.mkdir(datasetName)
    os.mkdir(os.path.join(datasetName, 'train'))
    os.mkdir(os.path.join(datasetName, 'val'))


def createLabel(srcXmlPath, dstTxtPath, labelList):
    check_ok = False
    xmlFile = os.path.basename(srcXmlPath)
    xml = open(srcXmlPath, 'r')
    txt = open(dstTxtPath, 'w')
    tree = ET.parse(xml)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    base_w = 0.03
    base_h = 0.03
    objCnt = 0
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        label = obj.find('name').text
        if label not in labelList or int(difficult) == 1:
            continue
        labelID = labelList.index(label)
        bbox = obj.find('bndbox')

        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)

        if xmin > w or xmax > w or ymin > h or ymax > h or \
           xmin < 0 or xmax < 0 or ymin < 0 or ymax < 0:
            continue

        x_center = ((xmin + xmax) / 2) / w
        y_center = ((ymin + ymax) / 2) / h

        width = (xmax - xmin) / w
        height = (ymax - ymin) / h
        if width > base_w and height > base_h:
            
            b = [x_center, y_center, width, height]
            bn = ['x_center', 'y_center', 'width', 'height']

            for index, item in enumerate(b):
                if item > 1:
                    print('[Error] In {}, item {} of object {}: {}'.format(xmlFile, bn[index], objCnt, item))
                    print(xmin, ymin, xmax, ymax)
                    exit(-1)

            txt.write('{} {:.6f} {:.6f} {:.6f} {:.6f}\n'.format(int(labelID), b[0], b[1], b[2], b[3]))
            objCnt += 1
            check_ok = True

    xml.close()
    txt.close()
    if check_ok is False:
        os.remove(dstTxtPath)
    return check_ok


if __name__ == '__main__':
    srcDatasetDir = '/dataset/resource2/VOC_dataset'
    labelList = ['sly_bjbmyw','sly_dmyw','jsxs','bj_bjps','yw_gkxfw',\
    'yw_nc','bj_bpmh','hxq_gjbs','jyz','jyz_zc',\
    'jyz_pl','hxq_yfps','hxq_yfzc','hxq_gjzc','bj_zc']
    valPercent = 0.05

    #datasetName = os.path.basename(srcDatasetDir)
    datasetName = "VOC"
    if os.path.exists(datasetName):
        print(datasetName, 'is existed')
        exit(-1)
    initDataSpace(datasetName)

    print('checking dataset')
    fileNameList = checkDatasets(srcDatasetDir)
    if fileNameList is None:
        print('original dataset is invalid')
        exit(-1)
    datasetSize = len(fileNameList)

    random.shuffle(fileNameList)
    valList = fileNameList[:int(valPercent * datasetSize)]
    trainList = fileNameList[int(valPercent * datasetSize):]

    dataPartDic = {'train': trainList, 'val': valList}
    for part in ['train', 'val']:
        print(part)
        for fileName in tqdm(dataPartDic[part]):
            srcImgPath = os.path.join(srcDatasetDir, 'JPEGImages', fileName + '.jpg')
            dstImgPath = os.path.join(datasetName, part, fileName + '.jpg')
            
            check_ok = createLabel(os.path.join(srcDatasetDir, 'Annotations', fileName + '.xml'),
                        os.path.join(datasetName, part, fileName + '.txt'),
                        labelList)
            if check_ok:
                shutil.copyfile(srcImgPath, dstImgPath)
    train_path = os.path.join(datasetName, 'train')
    val_path = os.path.join(datasetName, 'val')
    print( 'train sample path {}'.format(train_path) )
    print( 'val sample path {}'.format(val_path) )
