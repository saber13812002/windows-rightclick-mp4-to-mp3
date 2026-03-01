"""
یک‌بار اجرا کن: مسیر پایتون و ffmpeg را تشخیص می‌دهد، config.json و register_all.reg می‌سازد.
بعد فایل register_all.reg را اجرا کن تا همه گزینه‌ها روی راست‌کلیک اضافه شوند.
"""
import json
import shutil
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    python_exe = sys.executable
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
