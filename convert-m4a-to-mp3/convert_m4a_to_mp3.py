import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import traceback


BASE_DIR = Path(__file__).resolve().parents[1]
LOG_FILE = BASE_DIR / "debug.log"
FFMPEG_PATH = Path(r"C:\Program Files (x86)\FastPCTools\Fast Screen Recorder\ffmpeg.exe")


def log(message: str) -> None:
    """Append a timestamped log line to debug.log next to the project."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] [m4a] {message}\n")
    except Exception:
        pass


def show_error_box(message: str) -> None:
    """Show a Windows message box so when you run from right‑click you see the error."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0, str(message), "M4A → MP3 error", 0x10
        )
    except Exception:
        pass


def convert_m4a_to_mp3(m4a_path: str) -> None:
    m4a = Path(m4a_path)
    mp3 = m4a.with_suffix(".mp3")

    ffmpeg_executable = str(FFMPEG_PATH) if FFMPEG_PATH.exists() else shutil.which("ffmpeg")
    if not ffmpeg_executable:
        msg = (
            "ffmpeg executable not found. Install ffmpeg or update FFMPEG_PATH "
            f"in script (expected at {FFMPEG_PATH})."
        )
        log(msg)
        show_error_box(msg)
        return

    command = [ffmpeg_executable, "-y", "-i", str(m4a), str(mp3)]
    log(f"Starting conversion. Input='{m4a}' Output='{mp3}'")
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
    if len(sys.argv) < 2:
        show_error_box("No input file was passed to the script.")
        log("No input file in sys.argv")
        sys.exit(1)

    m4a_file = sys.argv[1]
    log(f"Script called with argument: {m4a_file}")
    convert_m4a_to_mp3(m4a_file)
