"""
ماژول مشترک: مسیر ffmpeg/ffprobe از config.json (توسط setup.py پر می‌شود).
اگر config نبود یا خالی بود، از PATH استفاده می‌شود.
"""
import json
from pathlib import Path

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
