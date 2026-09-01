"""Convert media to OGG 48 kHz (good for messengers)."""
import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from _ffmpeg_config import get_ffmpeg, setup_context_menu_log


def convert_to_ogg(input_path: str) -> None:
    out = Path(input_path).with_suffix(".ogg")
    cmd = [
        get_ffmpeg(),
        "-y",
        "-i", input_path,
        "-c:a", "libvorbis",
        "-ar", "48000",
        "-q:a", "4",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"Created: {out}")


if __name__ == "__main__":
    setup_context_menu_log()
    if len(sys.argv) < 2:
        print("Usage: convert_to_ogg.py <file>")
        sys.exit(1)
    convert_to_ogg(sys.argv[1])
