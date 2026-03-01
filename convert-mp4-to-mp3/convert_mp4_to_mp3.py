import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from _ffmpeg_config import get_ffmpeg, setup_context_menu_log

def convert_mp4_to_mp3(mp4_path):
    mp3_path = mp4_path.rsplit('.', 1)[0] + '.mp3'
    command = [get_ffmpeg(), '-i', mp4_path, mp3_path]
    subprocess.run(command)

if __name__ == '__main__':
    setup_context_menu_log()
    mp4_file = sys.argv[1]
    convert_mp4_to_mp3(mp4_file)
