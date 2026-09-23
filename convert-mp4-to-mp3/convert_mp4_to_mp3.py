import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from _ffmpeg_config import get_ffmpeg, setup_context_menu_log


BASE_DIR = Path(__file__).resolve().parents[1]
LOG_FILE = BASE_DIR / "debug.log"


# ffmpeg settings for each right-click quality level.
# Higher bitrate = better quality + bigger file; lower bitrate = smaller file.
QUALITY_LEVELS = {
    "high": {
        "label": "High (320 kbps)",
        "suffix": "",
        "args": ["-c:a", "libmp3lame", "-b:a", "320k"],
    },
    "medium": {
        "label": "Medium (192 kbps)",
        "suffix": " (192kbps)",
        "args": ["-c:a", "libmp3lame", "-b:a", "192k"],
    },
    "low": {
        "label": "Low (128 kbps)",
        "suffix": " (128kbps)",
        "args": ["-c:a", "libmp3lame", "-b:a", "128k"],
    },
    "64": {
        "label": "64 kbps",
        "suffix": " (64kbps)",
        "args": ["-c:a", "libmp3lame", "-b:a", "64k"],
    },
    "56": {
        "label": "56 kbps",
        "suffix": " (56kbps)",
        "args": ["-c:a", "libmp3lame", "-b:a", "56k"],
    },
    "48": {
        "label": "48 kbps",
        "suffix": " (48kbps)",
        "args": ["-c:a", "libmp3lame", "-b:a", "48k"],
    },
}


def log(message: str) -> None:
    """Append a timestamped log line to debug.log next to the project."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {message}\n")
    except Exception:
        # If even logging fails, we don't want the whole script to crash.
        pass


def show_error_box(message: str) -> None:
    """Show a Windows message box so when you run from right-click you see the error."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0, str(message), "MP4 → MP3 error", 0x10  # MB_ICONHAND
        )
    except Exception:
        # If the message box fails for any reason, ignore it.
        pass


def convert_mp4_to_mp3(mp4_path: str, quality: str = "high") -> None:
    mp4 = Path(mp4_path)
    settings = QUALITY_LEVELS.get(quality, QUALITY_LEVELS["high"])

    if settings["suffix"]:
        mp3 = mp4.with_name(f"{mp4.stem}{settings['suffix']}.mp3")
    else:
        mp3 = mp4.with_suffix(".mp3")

    ffmpeg_executable = get_ffmpeg()
    if not ffmpeg_executable:
        msg = (
            "ffmpeg executable not found. Install ffmpeg, place ffmpeg/ffmpeg.exe "
            "next to the project, or set the path in config.json."
        )
        log(msg)
        show_error_box(msg)
        return

    command = [ffmpeg_executable, "-y", "-i", str(mp4), *settings["args"], str(mp3)]
    log(
        f"Starting conversion. Quality='{quality}' ({settings['label']}) "
        f"Input='{mp4}' Output='{mp3}'"
    )
    log(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        log(f"ffmpeg return code: {result.returncode}")
        if result.stdout:
            log("ffmpeg stdout:")
            log(result.stdout)
        if result.stderr:
            log("ffmpeg stderr:")
            log(result.stderr)

        if result.returncode != 0:
            msg = f"ffmpeg failed with code {result.returncode}. See debug.log for details."
            log(msg)
            show_error_box(msg)
        else:
            log("Conversion finished successfully.")

    except Exception as exc:
        log("Exception during conversion:")
        log(traceback.format_exc())
        show_error_box(f"Unexpected error: {exc}")


if __name__ == "__main__":
    setup_context_menu_log()

    if len(sys.argv) < 2:
        show_error_box("No input file was passed to the script.")
        log("No input file in sys.argv")
        sys.exit(1)

    mp4_file = sys.argv[1]
    quality = sys.argv[2] if len(sys.argv) > 2 else "high"
    if quality not in QUALITY_LEVELS:
        log(f"Unknown quality '{quality}', falling back to 'high'.")
        quality = "high"

    log(f"Script called with argument: {mp4_file} (quality: {quality})")
    convert_mp4_to_mp3(mp4_file, quality)
