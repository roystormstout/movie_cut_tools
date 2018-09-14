import shutil
import sys
import cv2
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

def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name,ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)
    
    cmd = [get_setting("FFMPEG_BINARY"),"-y",
      "-i", filename,
      "-ss", "%0.2f"%t1,
      "-t", "%0.2f"%(t2-t1),
      "-strict","-2",
      targetname]
    
    subprocess_call(cmd)

def cut_videos(root, video_name):
    video_path = root + "/movie/"
    saving_path = "./"+video_name+"/"
    file_name = root + "/shots_info/" + video_name+".txt"
    shots_list = load_split_file(file_name)
    clips_info = {'clips': [], 'name': video_name}
    vid_path = video_path+video_name+'.mp4'
    fps = read_fps(vid_path)
    # print(fps)
    if fps == 0:
	return
    if not os.path.exists(saving_path):
        os.makedirs(saving_path)
    else:
	return
        #shutil.rmtree(saving_path)
        #os.makedirs(saving_path)
    total_time = float(shots_list[len(shots_list)-1][1])/fps
    average_clip_length = total_time/20
    print("minimal time threshold is: "+str(average_clip_length))
    clip_index = 0
    i = 0
    while i < len(shots_list):
        clips_included = [i]
        target_name = saving_path+str(clip_index)+".mp4"
        start_time = float(shots_list[i][0])/fps
        end_time = float(shots_list[i][1])/fps
        while (end_time - start_time < 300.0 and end_time - start_time < average_clip_length) and i < len(shots_list)-1:
            i += 1
            end_time = float(shots_list[i][1])/fps
            clips_included.append(i)
        ffmpeg_extract_subclip(vid_path, start_time, end_time, targetname=target_name)
        clips_info['clips'].append({'index':clip_index,
                                    'start_time': start_time,
                                    'end_time': end_time,
                                    'combined_shots': clips_included})
        clip_index += 1
        i += 1
    with open(root + "/shots_info/" + video_name+'.clips.json', 'w') as outfile:
        json.dump(clips_info, outfile)


if __name__ == '__main__':
    print("\n".join(sys.argv))
    cut_videos(sys.argv[1],sys.argv[2])
