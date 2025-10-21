import subprocess
import sys

def convert_mp4_to_mp3(m4a_path):
    mp3_path = m4a_path.rsplit('.', 1)[0] + '.mp3'
    command = ['ffmpeg', '-i', m4a_path, mp3_path]
    subprocess.run(command)

if __name__ == '__main__':
    m4a_file = sys.argv[1]
    convert_mp4_to_mp3(m4a_file)
