r"""
Generate config.json and register_all.reg for context menu entries.

When running as a compiled EXE (PyInstaller):
  - Each tool script is a standalone EXE in the same folder
  - Registry entries point directly to those EXEs

When running as a Python script:
  - Registry entries use python.exe + script.py
  - Bundled or system python/ffmpeg are auto-detected
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


def _is_frozen():
    """Return True if running as a compiled PyInstaller EXE."""
    return getattr(sys, "frozen", False)


def _detect_bundled_ffmpeg(root: Path):
    """Return path to bundled ffmpeg.exe if it exists, else None."""
    bundled = root / "ffmpeg" / "ffmpeg.exe"
    return bundled if bundled.exists() else None


def _detect_bundled_ffprobe(root: Path):
    """Return path to bundled ffprobe.exe if it exists, else None."""
    bundled = root / "ffmpeg" / "ffprobe.exe"
    return bundled if bundled.exists() else None


def run_check(root: Path, python_exe: Path) -> None:
    """Print verification report."""
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
            lines.append(f"  ffmpeg:  {cfg.get('ffmpeg') or '(use PATH / bundled)'}")
            lines.append(f"  ffprobe: {cfg.get('ffprobe') or '(use PATH / bundled)'}")
        except Exception as e:
            lines.append(f"config.json: ERROR - {e}")
    else:
        lines.append("config.json: not found (run setup once to create)")
    lines.append("")

    bundled_ff = _detect_bundled_ffmpeg(root)
    bundled_fp = _detect_bundled_ffprobe(root)
    lines.append(f"Bundled ffmpeg:  {'YES' if bundled_ff else 'no'}")
    lines.append(f"Bundled ffprobe: {'YES' if bundled_fp else 'no'}")
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
    if not ffmpeg_path:
        ffmpeg_path = str(bundled_ff) if bundled_ff else ""
    path_available = bool(ffmpeg_path) or bool(bundled_ff)
    lines.append(f"ffmpeg available: {'yes' if path_available else 'NO (download ffmpeg)'}")
    if bundled_ff:
        lines.append(f"  (using bundled: {bundled_ff})")
    lines.append(f"Log file (after right-click runs): {root / 'context_menu.log'}")
    lines.append("--- end check ---")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Generate config.json and register_all.reg for context menu.")
    ap.add_argument("--python", metavar="PATH", help="Path to python.exe (ignored when running as EXE)")
    ap.add_argument("--ffmpeg", metavar="PATH", help="Path to ffmpeg.exe (if not in PATH)")
    ap.add_argument("--ffprobe", metavar="PATH", help="Path to ffprobe.exe (optional)")
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

    # ─── Detect ffmpeg ─────────────────────────────────────────────────────
    bundled_ff = _detect_bundled_ffmpeg(root)
    bundled_fp = _detect_bundled_ffprobe(root)

    if args.ffmpeg:
        ffmpeg = str(Path(args.ffmpeg).resolve())
    elif bundled_ff:
        ffmpeg = str(bundled_ff)
    else:
        ffmpeg = shutil.which("ffmpeg") or ""

    if args.ffprobe:
        ffprobe = str(Path(args.ffprobe).resolve())
    elif bundled_fp:
        ffprobe = str(bundled_fp)
    elif ffmpeg:
        ffprobe = str(Path(ffmpeg).parent / "ffprobe.exe")
    else:
        ffprobe = shutil.which("ffprobe") or ""

    # Interactive prompt if no ffmpeg found
    if not ffmpeg and getattr(sys.stdin, "isatty", lambda: False) and sys.stdin.isatty():
        prompt = "ffmpeg not found. Enter path to ffmpeg.exe or its folder: "
        try:
            user_ffmpeg = input(prompt).strip().strip('"')
        except (EOFError, OSError):
            user_ffmpeg = ""
        if user_ffmpeg:
            ffmpeg = str(Path(user_ffmpeg).resolve())
            if not ffprobe:
                ffprobe = str(Path(ffmpeg).parent / "ffprobe.exe")

    def norm_exe(path: str, exe_name: str) -> str:
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

    # ─── Registry command generation ───────────────────────────────────────
    # When running as compiled EXE: entries point directly to other EXEs
    # When running as script: entries use python.exe + script.py
    is_frozen = _is_frozen()
    script_dir = root  # same dir as this exe/script

    def exe_path(name):
        """Return path to a compiled EXE (in same dir as setup.exe)."""
        p = script_dir / f"{name}.exe"
        return str(p) if p.exists() else ""

    def reg_cmd(target):
        """Generate the registry command value."""
        if is_frozen:
            # Point directly to the compiled EXE
            return f'\\"{esc(target)}\\" \\"%1\\"'
        else:
            return f'\\"{esc(py_exe)}\\" \\"{esc(target)}\\" \\"%1\\"'

    def reg_cmd_dir(target, action):
        """Generate the registry command value for directory/batch actions."""
        if is_frozen:
            return f'\\"{esc(target)}\\" \\"--action\\" \\"{action}\\" \\"%1\\"'
        else:
            return f'\\"{esc(py_exe)}\\" \\"{esc(target)}\\" \\"--action\\" \\"{action}\\" \\"%1\\"'

    # For non-frozen mode, detect python
    if not is_frozen:
        if args.python:
            py_exe = str(Path(args.python).resolve())
        else:
            py_exe = str(Path(sys.executable).resolve())
        print(f"Using python: {py_exe}")
    else:
        print("Running as compiled EXE — entries will point directly to tool EXEs.")

    batch_script = script_dir / "batch_convert" / "batch_convert.py"
    if is_frozen:
        batch_script = Path(exe_path("batch_convert"))

    # Define all registry entries
    entries = [
        (".mp4", "Convert to MP3", "Convert to MP3",
         reg_cmd(exe_path("convert_mp4_to_mp3") or str(script_dir / "convert-mp4-to-mp3" / "convert_mp4_to_mp3.py"))),
        (".m4a", "Convert to MP3", "Convert to MP3",
         reg_cmd(exe_path("convert_m4a_to_mp3") or str(script_dir / "convert-m4a-to-mp3" / "convert_m4a_to_mp3.py"))),
        (".mp4", "Convert to OGG 48kHz", "Convert to OGG 48kHz",
         reg_cmd(exe_path("convert_to_ogg") or str(script_dir / "convert-to-ogg" / "convert_to_ogg.py"))),
        (".m4a", "Convert to OGG 48kHz", "Convert to OGG 48kHz",
         reg_cmd(exe_path("convert_to_ogg") or str(script_dir / "convert-to-ogg" / "convert_to_ogg.py"))),
        (".mkv", "Convert to OGG 48kHz", "Convert to OGG 48kHz",
         reg_cmd(exe_path("convert_to_ogg") or str(script_dir / "convert-to-ogg" / "convert_to_ogg.py"))),
        (".avi", "Convert to OGG 48kHz", "Convert to OGG 48kHz",
         reg_cmd(exe_path("convert_to_ogg") or str(script_dir / "convert-to-ogg" / "convert_to_ogg.py"))),
        (".webm", "Convert to OGG 48kHz", "Convert to OGG 48kHz",
         reg_cmd(exe_path("convert_to_ogg") or str(script_dir / "convert-to-ogg" / "convert_to_ogg.py"))),
        (".mov", "Convert to OGG 48kHz", "Convert to OGG 48kHz",
         reg_cmd(exe_path("convert_to_ogg") or str(script_dir / "convert-to-ogg" / "convert_to_ogg.py"))),
        (".mp4", "Split midpoint (1s overlap)", "Split midpoint (1s overlap)",
         reg_cmd(exe_path("split_middle_overlap") or str(script_dir / "split-mp4-middle" / "split_middle_overlap.py"))),
        (".mp3", "Split midpoint (1s overlap)", "Split midpoint (1s overlap)",
         reg_cmd(exe_path("split_middle_overlap") or str(script_dir / "split-mp4-middle" / "split_middle_overlap.py"))),
        (".mp3", "Add Custom Music", "Add Custom Music",
         f'\\"{esc(str(script_dir / "add-music-to-mp3" / "add_music.bat"))}\\" \\"%1\\"'),
        (".mp3", "Remove Silence", "Remove Silence (2s+)",
         reg_cmd(exe_path("remove_silence") or str(script_dir / "remove-silence-mp3" / "remove_silence.py"))),
        (".mp3", "Remove Long Silence", "Remove Long Silence (5s+)",
         reg_cmd(exe_path("remove_long_silence") or str(script_dir / "remove-long-silence-mp3" / "remove_long_silence.py"))),
        (".mp3", "Split on Silence", "Split on Silence (2s+)",
         reg_cmd(exe_path("split_on_silence") or str(script_dir / "split-on-silence-mp3" / "split_on_silence.py"))),
        # Directory (folder) right-click batch actions
        ("Directory", "Convert all in folder to MP3", "Convert all in folder to MP3",
         reg_cmd_dir(str(batch_script), "mp3")),
        ("Directory", "Convert all in folder to OGG 48kHz", "Convert all in folder to OGG 48kHz",
         reg_cmd_dir(str(batch_script), "ogg")),
        ("Directory", "Split midpoint for all in folder", "Split midpoint for all in folder",
         reg_cmd_dir(str(batch_script), "split_midpoint")),
        ("Directory", "Remove silence for all in folder", "Remove silence for all in folder",
         reg_cmd_dir(str(batch_script), "remove_silence")),
        ("Directory", "Remove long silence for all in folder", "Remove long silence for all in folder",
         reg_cmd_dir(str(batch_script), "remove_long_silence")),
        ("Directory", "Split on silence for all in folder", "Split on silence for all in folder",
         reg_cmd_dir(str(batch_script), "split_on_silence")),
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

    import os
    if os.name == "nt":
        os.startfile(str(reg_path))
        print("A dialog opened: click Yes/OK to add the context menu.")


if __name__ == "__main__":
    main()
