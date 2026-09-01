"""
Batch convert all supported files in a folder. No interaction; skips files that already have output.
Right-click folder -> one of the batch menu options.
"""
import argparse
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from _ffmpeg_config import setup_context_menu_log

# (extensions, script_path, output_exists_func)
# output_exists_func(f: Path) -> bool
ACTIONS = {
    "mp3": (
        [".mp4", ".m4a"],
        lambda p: (p.parent / (p.stem + ".mp3")).exists(),
        None,  # script chosen by ext below
    ),
    "ogg": (
        [".mp4", ".m4a", ".mkv", ".avi", ".webm", ".mov"],
        lambda p: (p.parent / (p.stem + ".ogg")).exists(),
        _root / "convert-to-ogg" / "convert_to_ogg.py",
    ),
    "split_midpoint": (
        [".mp4", ".mp3"],
        lambda p: (p.parent / (p.stem + "_part1" + p.suffix)).exists()
        and (p.parent / (p.stem + "_part2" + p.suffix)).exists(),
        _root / "split-mp4-middle" / "split_middle_overlap.py",
    ),
    "remove_silence": (
        [".mp3"],
        lambda p: (p.parent / (p.stem + "_no_silence.mp3")).exists(),
        _root / "remove-silence-mp3" / "remove_silence.py",
    ),
    "remove_long_silence": (
        [".mp3"],
        lambda p: (p.parent / (p.stem + "_no_long_silence.mp3")).exists(),
        _root / "remove-long-silence-mp3" / "remove_long_silence.py",
    ),
    "split_on_silence": (
        [".mp3"],
        lambda p: (p.parent / (p.stem + "_parts")).is_dir(),
        _root / "split-on-silence-mp3" / "split_on_silence.py",
    ),
}

MP3_SCRIPT_BY_EXT = {
    ".mp4": _root / "convert-mp4-to-mp3" / "convert_mp4_to_mp3.py",
    ".m4a": _root / "convert-m4a-to-mp3" / "convert_m4a_to_mp3.py",
}


def run_batch(folder_path: Path, action: str) -> None:
    if action not in ACTIONS:
        print(f"Unknown action: {action}")
        sys.exit(1)
    exts, output_exists, script = ACTIONS[action]
    folder_path = folder_path.resolve()
    if not folder_path.is_dir():
        print(f"Not a directory: {folder_path}")
        sys.exit(1)

    files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in exts]
    to_process = [f for f in files if not output_exists(f)]
    skipped = len(files) - len(to_process)
    if skipped:
        print(f"Skipped {skipped} (output already exists).")
    print(f"Processing {len(to_process)} file(s)...")
    import subprocess
    for i, f in enumerate(to_process, 1):
        if action == "mp3":
            script = MP3_SCRIPT_BY_EXT.get(f.suffix.lower())
            if not script:
                continue
        try:
            subprocess.run([sys.executable, str(script), str(f)], check=True)
            print(f"[{i}/{len(to_process)}] Done: {f.name}")
        except subprocess.CalledProcessError as e:
            print(f"[{i}/{len(to_process)}] Failed: {f.name} - {e}")
        except Exception as e:
            print(f"[{i}/{len(to_process)}] Error: {f.name} - {e}")
    print("Batch finished.")


def main():
    setup_context_menu_log()
    ap = argparse.ArgumentParser(description="Batch convert files in folder (no interaction; skips existing output).")
    ap.add_argument("folder", type=Path, help="Folder path")
    ap.add_argument("--action", required=True, choices=list(ACTIONS), help="Action to run")
    args = ap.parse_args()
    run_batch(args.folder, args.action)


if __name__ == "__main__":
    main()
