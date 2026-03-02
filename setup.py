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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ffmpeg_config import VERSION

# Scripts and dirs we expect under project root
REQUIRED = [
    "convert-mp4-to-mp3/convert_mp4_to_mp3.py",
    "convert-m4a-to-mp3/convert_m4a_to_mp3.py",
    "convert-to-ogg/convert_to_ogg.py",
    "batch-convert/batch_convert.py",
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
    lines.append(f"Log file (after right-click runs): {root / 'context_menu.log'}")
    lines.append("--- end check ---")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Generate config.json and register_all.reg for context menu.")
    ap.add_argument("--python", metavar="PATH", help="Path to python.exe (if not in PATH)")
    ap.add_argument("--ffmpeg", metavar="PATH", help="Path to ffmpeg.exe (if not in PATH)")
    ap.add_argument("--ffprobe", metavar="PATH", help="Path to ffprobe.exe (optional; default: same dir as ffmpeg)")
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
    ffmpeg = (args.ffmpeg and str(Path(args.ffmpeg).resolve())) or shutil.which("ffmpeg") or ""
    ffprobe = (args.ffprobe and str(Path(args.ffprobe).resolve())) or shutil.which("ffprobe") or ""

    if not ffmpeg and getattr(sys.stdin, "isatty", lambda: False) and sys.stdin.isatty():
        prompt = "ffmpeg not in PATH. Enter path to ffmpeg.exe or its folder (e.g. from Explorer bar): "
        try:
            user_ffmpeg = input(prompt).strip().strip('"')
        except (EOFError, OSError):
            user_ffmpeg = ""
        if user_ffmpeg:
            ffmpeg = str(Path(user_ffmpeg).resolve())
            if not ffprobe:
                ffprobe = str(Path(ffmpeg).parent / "ffprobe.exe")

    def norm_exe(path: str, exe_name: str) -> str:
        """If path is a folder (e.g. pasted from Explorer address bar), use folder/exe_name."""
        if not path:
            return path
        p = Path(path).resolve()
        if p.is_dir():
            return str(p / exe_name)
        return str(p)

    if ffmpeg:
        ffmpeg = norm_exe(ffmpeg, "ffmpeg.exe")
    if ffmpeg and not ffprobe:
        ffprobe = str(Path(ffmpeg).parent / "ffprobe.exe")
    if ffprobe:
        ffprobe = norm_exe(ffprobe, "ffprobe.exe")

    config = {"ffmpeg": ffmpeg or "", "ffprobe": ffprobe or ""}
    with open(root / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print("config.json written (ffmpeg/ffprobe paths).")

    def esc(s):
        return str(s).replace("\\", "\\\\")

    # .reg value: inner quotes must be backslash-escaped: \"path\" \"path2\" \"%1\"
    def reg_cmd(py_exe, script_path):
        return f'\\"{esc(py_exe)}\\" \\"{esc(script_path)}\\" \\"%1\\"'

    def reg_cmd_dir(py_exe, script_path, action):
        return f'\\"{esc(py_exe)}\\" \\"{esc(script_path)}\\" \\"--action\\" \\"{action}\\" \\"%1\\"'

    py = python_exe
    batch_script = root / "batch-convert" / "batch_convert.py"
    entries = [
        (".mp4", "Convert to MP3", "Convert to MP3", reg_cmd(py, root / "convert-mp4-to-mp3" / "convert_mp4_to_mp3.py")),
        (".m4a", "Convert to MP3", "Convert to MP3", reg_cmd(py, root / "convert-m4a-to-mp3" / "convert_m4a_to_mp3.py")),
        (".mp4", "Convert to OGG 48kHz", "Convert to OGG 48kHz", reg_cmd(py, root / "convert-to-ogg" / "convert_to_ogg.py")),
        (".m4a", "Convert to OGG 48kHz", "Convert to OGG 48kHz", reg_cmd(py, root / "convert-to-ogg" / "convert_to_ogg.py")),
        (".mkv", "Convert to OGG 48kHz", "Convert to OGG 48kHz", reg_cmd(py, root / "convert-to-ogg" / "convert_to_ogg.py")),
        (".avi", "Convert to OGG 48kHz", "Convert to OGG 48kHz", reg_cmd(py, root / "convert-to-ogg" / "convert_to_ogg.py")),
        (".webm", "Convert to OGG 48kHz", "Convert to OGG 48kHz", reg_cmd(py, root / "convert-to-ogg" / "convert_to_ogg.py")),
        (".mov", "Convert to OGG 48kHz", "Convert to OGG 48kHz", reg_cmd(py, root / "convert-to-ogg" / "convert_to_ogg.py")),
        (".mp4", "Split midpoint (1s overlap)", "Split midpoint (1s overlap)", reg_cmd(py, root / "split-mp4-middle" / "split_middle_overlap.py")),
        (".mp3", "Split midpoint (1s overlap)", "Split midpoint (1s overlap)", reg_cmd(py, root / "split-mp4-middle" / "split_middle_overlap.py")),
        (".mp3", "Add Custom Music", "Add Custom Music", f'\\"{esc(str(root / "add-music-to-mp3" / "add_music.bat"))}\\" \\"%1\\"'),
        (".mp3", "Remove Silence", "Remove Silence (2s+)", reg_cmd(py, root / "remove-silence-mp3" / "remove_silence.py")),
        (".mp3", "Remove Long Silence", "Remove Long Silence (5s+)", reg_cmd(py, root / "remove-long-silence-mp3" / "remove_long_silence.py")),
        (".mp3", "Split on Silence", "Split on Silence (2s+)", reg_cmd(py, root / "split-on-silence-mp3" / "split_on_silence.py")),
        # Directory (folder) right-click batch actions
        ("Directory", "Convert all in folder to MP3", "Convert all in folder to MP3", reg_cmd_dir(py, batch_script, "mp3")),
        ("Directory", "Convert all in folder to OGG 48kHz", "Convert all in folder to OGG 48kHz", reg_cmd_dir(py, batch_script, "ogg")),
        ("Directory", "Split midpoint for all in folder", "Split midpoint for all in folder", reg_cmd_dir(py, batch_script, "split_midpoint")),
        ("Directory", "Remove silence for all in folder", "Remove silence for all in folder", reg_cmd_dir(py, batch_script, "remove_silence")),
        ("Directory", "Remove long silence for all in folder", "Remove long silence for all in folder", reg_cmd_dir(py, batch_script, "remove_long_silence")),
        ("Directory", "Split on silence for all in folder", "Split on silence for all in folder", reg_cmd_dir(py, batch_script, "split_on_silence")),
    ]

    lines = ["Windows Registry Editor Version 5.00", ""]
    for ext_or_dir, reg_key, label, cmd in entries:
        if ext_or_dir == "Directory":
            base = f"HKEY_CLASSES_ROOT\\Directory\\shell\\{reg_key}"
        else:
            base = f"HKEY_CLASSES_ROOT\\SystemFileAssociations\\{ext_or_dir}\\shell\\{reg_key}"
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
