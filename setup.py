r"""
یک‌بار اجرا کن: مسیر پایتون و ffmpeg را تشخیص می‌دهد، config.json و register_all.reg می‌سازد.
بعد فایل register_all.reg را اجرا کن تا همه گزینه‌ها روی راست‌کلیک اضافه شوند.
استفاده با مسیر دستی پایتون: python setup.py --python "C:\path\to\python.exe"
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "1.0"

# Scripts and dirs we expect under project root
REQUIRED = [
    "convert-mp4-to-mp3/convert_mp4_to_mp3.py",
    "convert-m4a-to-mp3/convert_m4a_to_mp3.py",
    "split-mp4-middle/split_middle_overlap.py",
    "add-music-to-mp3/add_music.bat",
    "remove-silence-mp3/remove_silence.py",
    "remove-long-silence-mp3/remove_long_silence.py",
    "split-on-silence-mp3/split_on_silence.py",
    "_ffmpeg_config.py",
]


def run_check(root: Path, python_exe: Path) -> None:
    """Print verification report so user can paste output and confirm setup."""
    lines = [
        "--- convert_mp4_to_mp3 setup check ---",
        f"Version: {VERSION}",
        f"Project root: {root}",
        f"Python: {python_exe}",
        "",
    ]
    try:
        r = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        ver = (r.stdout or r.stderr or "").strip()
        lines.append(f"Python version: {ver}")
    except Exception as e:
        lines.append(f"Python version: ERROR - {e}")
    lines.append("")

    config_path = root / "config.json"
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            lines.append("config.json: found")
            lines.append(f"  ffmpeg:  {cfg.get('ffmpeg') or '(use PATH)'}")
            lines.append(f"  ffprobe: {cfg.get('ffprobe') or '(use PATH)'}")
        except Exception as e:
            lines.append(f"config.json: ERROR - {e}")
    else:
        lines.append("config.json: not found (run setup once to create)")
    lines.append("")

    lines.append("Required files:")
    ok = 0
    for rel in REQUIRED:
        p = root / rel.replace("/", "\\")
        exists = p.exists()
        if exists:
            ok += 1
        lines.append(f"  {'OK' if exists else 'MISSING'}: {rel}")
    lines.append("")
    lines.append(f"Files: {ok}/{len(REQUIRED)} present")

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path and config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                ffmpeg_path = json.load(f).get("ffmpeg") or ""
        except Exception:
            pass
    lines.append(f"ffmpeg in PATH or config: {'yes' if ffmpeg_path else 'NO (install ffmpeg)'}")
    lines.append("--- end check ---")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Generate config.json and register_all.reg for context menu.")
    ap.add_argument("--python", metavar="PATH", help="Path to python.exe (if not in PATH)")
    ap.add_argument("--version", "-V", action="store_true", help="Print version and exit")
    ap.add_argument("--check", "-c", action="store_true", help="Verify setup and print report (no files written)")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent

    if args.version:
        print(f"convert_mp4_to_mp3 setup {VERSION}")
        return

    if args.check:
        python_exe = (Path(args.python).resolve() if args.python else Path(sys.executable)).resolve()
        run_check(root, python_exe)
        return

    python_exe = (Path(args.python).resolve() if args.python else Path(sys.executable)).resolve()
    ffmpeg = shutil.which("ffmpeg") or ""
    ffprobe = shutil.which("ffprobe") or ""

    config = {"ffmpeg": ffmpeg, "ffprobe": ffprobe}
    with open(root / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print("config.json written (ffmpeg/ffprobe paths).")

    def esc(s):
        return str(s).replace("\\", "\\\\")

    # .reg value: inner quotes must be backslash-escaped: \"path\" \"path2\" \"%1\"
    def reg_cmd(py_exe, script_path):
        return f'\\"{esc(py_exe)}\\" \\"{esc(script_path)}\\" \\"%1\\"'

    py = python_exe
    entries = [
        (".mp4", "Convert to MP3", "Convert to MP3", reg_cmd(py, root / "convert-mp4-to-mp3" / "convert_mp4_to_mp3.py")),
        (".m4a", "Convert to MP3", "Convert to MP3", reg_cmd(py, root / "convert-m4a-to-mp3" / "convert_m4a_to_mp3.py")),
        (".mp4", "Split midpoint (1s overlap)", "Split midpoint (1s overlap)", reg_cmd(py, root / "split-mp4-middle" / "split_middle_overlap.py")),
        (".mp3", "Split midpoint (1s overlap)", "Split midpoint (1s overlap)", reg_cmd(py, root / "split-mp4-middle" / "split_middle_overlap.py")),
        (".mp3", "Add Custom Music", "Add Custom Music", f'\\"{esc(str(root / "add-music-to-mp3" / "add_music.bat"))}\\" \\"%1\\"'),
        (".mp3", "Remove Silence", "Remove Silence (2s+)", reg_cmd(py, root / "remove-silence-mp3" / "remove_silence.py")),
        (".mp3", "Remove Long Silence", "Remove Long Silence (5s+)", reg_cmd(py, root / "remove-long-silence-mp3" / "remove_long_silence.py")),
        (".mp3", "Split on Silence", "Split on Silence (2s+)", reg_cmd(py, root / "split-on-silence-mp3" / "split_on_silence.py")),
    ]

    lines = ["Windows Registry Editor Version 5.00", ""]
    for ext, reg_key, label, cmd in entries:
        base = f"HKEY_CLASSES_ROOT\\SystemFileAssociations\\{ext}\\shell\\{reg_key}"
        lines.append(f"[{base}]")
        lines.append(f'@="{label}"')
        lines.append("")
        lines.append(f"[{base}\\command]")
        lines.append(f'@="{cmd}"')
        lines.append("")

    reg_path = root / "register_all.reg"
    with open(reg_path, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines))
    print("register_all.reg created.")

    # Open .reg so user can confirm merge (one click) — or run: reg import register_all.reg (as Admin)
    import os
    if os.name == "nt":
        os.startfile(str(reg_path))
        print("A dialog opened: click Yes/OK to add the context menu.")


if __name__ == "__main__":
    main()
