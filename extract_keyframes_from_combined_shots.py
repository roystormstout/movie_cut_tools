import shutil
import sys
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import json
import os
import subprocess as sp

from moviepy.tools import subprocess_call
from moviepy.config import get_setting


def load_split_file(filename):
    """ Read video shots file.

    ----------
    Arguments:
    vid_name: Video file name.

    ----------
    Return:
    list of shots.
    each shot is: [start, end, example1, example2, example3]
    """
    shots_list = []
    file = open(filename, "r")
    for line in file:
        current_shot = line.split()
        shots_list.append(current_shot)
    file.close()
    return shots_list


def read_fps(vid_name):
    """ Read video frame rate.

    ----------
    Arguments:
    vid_name: Video file name.

    ----------
    Return:
    Frame rate (float)
    """

    video = cv2.VideoCapture(vid_name)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()

    return fps


def ffmpeg_extract_frame(filename, t1, targetname):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """

    cmd = [get_setting("FFMPEG_BINARY"),
           "-i", filename,
           "-ss", "%0.2f" % t1,
           "-vframes", "1", targetname]

    subprocess_call(cmd)


def get_frames(root, vid_name):
    video_path = root + "/movie/"
    shots_list = load_split_file(root+'/shots_info/'+vid_name+'.txt')
    vid_path = video_path+vid_name+'.mp4'
    fps = read_fps(vid_path)
    with open(root + "/shots_info/" + vid_name+'.clips.json', 'r') as f:
        data = json.load(f)

    clip_index = 0
    for clip in data['clips']:
        list = []
        for index in clip['combined_shots']:
            for frame in shots_list[index][2:]:
                list.append(frame)
        increment = len(list)/6
        i = 0
        final_cut_list=[]
	print(len(list))
        while i < len(list):
            final_cut_list.append(list[i])
            i += increment
        frame_index=0
        for frame in final_cut_list:
	    print(float(frame))
            ffmpeg_extract_frame(vid_path,float(frame)/fps,video_path+vid_name+"/"+str(clip_index)+"_"+str(frame_index)+".jpg")
            frame_index += 1
        clip_index += 1


if __name__ == '__main__':
    print("\n".join(sys.argv))
    get_frames(sys.argv[1],sys.argv[2])




