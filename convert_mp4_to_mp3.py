import subprocess
import sys

def convert_mp4_to_mp3(mp4_path):
    mp3_path = mp4_path.rsplit('.', 1)[0] + '.mp3'
    command = ['ffmpeg', '-i', mp4_path, mp3_path]
    subprocess.run(command)

if __name__ == '__main__':
    mp4_file = sys.argv[1]
    convert_mp4_to_mp3(mp4_file)
