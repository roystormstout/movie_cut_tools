import cut_according_to_frame
import sys
import glob, os

if __name__ == '__main__':
    os.chdir(sys.argv[1]+"/movie")
    for file in glob.glob("*.mp4"):
        cut_according_to_frame.cut_videos(sys.argv[1],file[:-4])
