import numpy
import cv2
import os
import glob
import threadpool
import threading

g_file_list = []
g_bool_is_proc = []
g_file_lock = threading.RLock()
g_save_path = ''

def video_cut( video_file, save_path ):
    video = cv2.VideoCapture( video_file )
    video_file_split = video_file.split('/')
    head_name = video_file_split[ len( video_file_split ) - 1 ]
    video_file_head = head_name.split('.')[0]
    frame_index = 0
    if video.isOpened():

        save_dir = os.path.join( save_path, video_file_head )
        is_exisit = os.path.exists(save_dir)
        if is_exisit is False:
            os.makedirs( save_dir )
        while True:
            is_ok, image = video.read()
            if image is not None:
                #frame_file_name = video_file_head.copy()
                frame_file_name = '{}_{}.jpg'.format( video_file_head, frame_index )
                save_jpg_name = os.path.join( save_dir, frame_file_name )

                cv2.imwrite( save_jpg_name, image, [int( cv2.IMWRITE_JPEG_QUALITY), 95] )
            else:
                break

            frame_index += 1

def pthread_video_cut( save_path ):
    global g_file_list
    global g_bool_is_proc
    global g_file_lock
    global g_save_path
    save_path = g_save_path
    while True:
        is_find_proc = False
        video_file = ''
        g_file_lock.acquire()
        for index, is_proc in enumerate( g_bool_is_proc ):
            if is_proc is False:
                g_bool_is_proc[ index ] = True
                is_find_proc = True
                video_file = g_file_list[ index ]
                break

        g_file_lock.release()

        if is_find_proc is True:
            video = cv2.VideoCapture( video_file )
            video_file_split = video_file.split('/')
            head_name = video_file_split[ len( video_file_split ) - 1 ]
            video_file_head = head_name.split('.')[0]
            frame_index = 0
            if video.isOpened():

                save_dir = os.path.join( save_path, video_file_head )
                is_exisit = os.path.exists(save_dir)
                if is_exisit is False:
                    os.makedirs( save_dir )
                while True:
                    is_ok, image = video.read()
                    if image is not None:
                        #frame_file_name = video_file_head.copy()
                        frame_file_name = '{}_{}.jpg'.format( video_file_head, frame_index )
                        save_jpg_name = os.path.join( save_dir, frame_file_name )

                        cv2.imwrite( save_jpg_name, image, [int( cv2.IMWRITE_JPEG_QUALITY), 95] )
                    else:
                        break

                    frame_index += 1
        else:
            break


def run( pthread_num, source_video_path, save_path ):
    global g_file_list
    global g_bool_is_proc
    global g_save_path
    g_save_path = save_path
    g_file_list = glob.glob(source_video_path)
    g_bool_is_proc=[]
    for index in range(len(g_file_list)):
        g_bool_is_proc.append(False)

    pool = threadpool.ThreadPool(pthread_num)
    requests = threadpool.makeRequests(pthread_video_cut, save_path)
    [pool.putRequest(req) for req in requests]
    pool.wait()

if __name__ == "__main__":
    pthread_num = 8
    source_video_path = "/home/fisun/old_home/fisun/dataset/private/video_proc/fall_video/*.avi"
    save_path = '/home/fisun/old_home/fisun/dataset/private/video_proc/video_frame'
    run(pthread_num, source_video_path, save_path)




'''
def main():
    source_video_path = "./fast_move/*.mp4"
    save_path = "./"
    file_list = glob.glob( source_video_path )
    for index, video_file in enumerate(file_list):
        video_cut( video_file, save_path )
'''
    
