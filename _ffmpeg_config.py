"""
ماژول مشترک: مسیر ffmpeg/ffprobe از:
  1. باندل شده (ffmpeg/ffmpeg.exe در کنار پروژه) – اولویت اول
  2. config.json (توسط setup.py پر می‌شود)
  3. PATH سیستم

Support both normal Python scripts and PyInstaller-compiled EXEs.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

VERSION = "2.0"  # bumped for PyInstaller-based release
_LOG_FILE = None


class _Tee:
    def __init__(self, stream, log_file):
        self._stream = stream
        self._log = log_file

    def write(self, data):
        self._stream.write(data)
        if self._log:
            try:
                self._log.write(data)
                self._log.flush()
            except OSError:
                pass

    def flush(self):
        self._stream.flush()
        if self._log:
            try:
                self._log.flush()
            except OSError:
                pass


def setup_context_menu_log():
    """Write all prints and errors to context_menu.log (in project root) in addition to console."""
    global _LOG_FILE
    if _LOG_FILE is not None:
        return
    try:
        root = _project_root()
        log_path = root / "context_menu.log"
        _LOG_FILE = open(log_path, "a", encoding="utf-8")
        header = f"\n=== v{VERSION} | {datetime.now().isoformat()} | {sys.executable} | argv: {sys.argv}\n"
        _LOG_FILE.write(header)
        _LOG_FILE.flush()
        sys.stdout = _Tee(sys.stdout, _LOG_FILE)
        sys.stderr = _Tee(sys.stderr, _LOG_FILE)
    except Exception:
        pass

_CONFIG = None


def _project_root():
    """
    پوشه روت پروژه:
    - اگر EXE فریز شده (PyInstaller): پوشه‌ای که EXE در آن قرار دارد
    - اگر اسکریپت عادی: پوشه‌ای که _ffmpeg_config.py در آن است
    """
    if getattr(sys, "frozen", False):
        # Running as compiled EXE – root is the folder containing the EXE
        return Path(sys.executable).resolve().parent
    # Running as normal Python script
    p = Path(__file__).resolve().parent
    while p != p.parent and not (p / "_ffmpeg_config.py").exists():
        p = p.parent
    return p


def _load_config():
    global _CONFIG
    if _CONFIG is not None:
        return _CONFIG
    root = _project_root()
    config_path = root / "config.json"
    _CONFIG = {}
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                _CONFIG = json.load(f)
        except Exception:
            pass
    return _CONFIG


def _bundled_ffmpeg():
    """Return path to bundled ffmpeg.exe if it exists, else None."""
    root = _project_root()
    bundled = root / "ffmpeg" / "ffmpeg.exe"
    return str(bundled) if bundled.exists() else None


def _bundled_ffprobe():
    """Return path to bundled ffprobe.exe if it exists, else None."""
    root = _project_root()
    bundled = root / "ffmpeg" / "ffprobe.exe"
    return str(bundled) if bundled.exists() else None


def get_ffmpeg():
    """Get ffmpeg path: bundled first, then config.json, then 'ffmpeg' (PATH)."""
    bundled = _bundled_ffmpeg()
    if bundled:
        return bundled
    c = _load_config()
    return c.get("ffmpeg") or "ffmpeg"


def get_ffprobe():
    """Get ffprobe path: bundled first, then config.json, then 'ffprobe' (PATH)."""
    bundled = _bundled_ffprobe()
    if bundled:
        return bundled
    c = _load_config()
    return c.get("ffprobe") or "ffprobe"

