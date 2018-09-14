import cut_according_to_frame
import sys
import glob, os
import extract_keyframes_from_combined_shots

def representsint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    command = 'h'
    if len(sys.argv) < 2:
        command = 'h'
    elif sys.argv[1] == '-c':
        command = 'c'
    elif sys.argv[1] == '-f':
        command = 'f'
    if command == 'h':
        print('\n-c: cut videos according to shots info' +
              '\n-f [int n]: extract n keyframes from each shots, default is 6\n')
    else:
        src_dir = os.getcwd()
        os.chdir(src_dir+"/movie")
        for file in glob.glob("*.mp4"):
            if command == 'c':
                cut_according_to_frame.cut_videos(src_dir,file[:-4])
            elif command == 'f':
                if len(sys.argv) == 3 and representsint(sys.argv[2]):
                    extract_keyframes_from_combined_shots.get_frames(src_dir,file[:-4],int(sys.argv[2]))
                else:
                    extract_keyframes_from_combined_shots.get_frames(src_dir, file[:-4], 6)
