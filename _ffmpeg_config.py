"""
ماژول مشترک: مسیر ffmpeg/ffprobe از config.json (توسط setup.py پر می‌شود).
اگر config نبود یا خالی بود، از PATH استفاده می‌شود.
همچنین setup_context_menu_log() برای نوشتن خروجی/خطا در context_menu.log.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.1"
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
    """همهٔ print و خطاها را علاوه بر کنسول در context_menu.log (در روت پروژه) هم بنویس."""
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
    """پوشه روت پروژه = جایی که _ffmpeg_config.py و config.json هست."""
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


def get_ffmpeg():
    """مسیر ffmpeg یا 'ffmpeg' اگر در config نبود (استفاده از PATH)."""
    c = _load_config()
    return c.get("ffmpeg") or "ffmpeg"


def get_ffprobe():
    """مسیر ffprobe یا 'ffprobe' اگر در config نبود."""
    c = _load_config()
    return c.get("ffprobe") or "ffprobe"
