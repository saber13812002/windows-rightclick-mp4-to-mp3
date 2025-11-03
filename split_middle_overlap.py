import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_tool_in_path(tool: str) -> None:
    if shutil.which(tool) is None:
        print(f"Error: {tool} not found in PATH. Install FFmpeg and ensure {tool} is accessible.", file=sys.stderr)
        sys.exit(1)


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(exc.returncode)


def ffprobe_duration_seconds(input_path: str) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        "--",
        input_path,
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        print("Failed to probe duration via ffprobe.", file=sys.stderr)
        sys.exit(exc.returncode)
    s = (result.stdout or "").strip()
    try:
        return float(s)
    except ValueError:
        print(f"Invalid duration output from ffprobe: {s}", file=sys.stderr)
        sys.exit(1)


def format_hhmmss_mmm(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    millis = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"


def split_midpoint_with_overlap(input_path: str) -> None:
    ensure_tool_in_path("ffprobe")
    ensure_tool_in_path("ffmpeg")

    input_path = str(Path(input_path).resolve())
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    duration = ffprobe_duration_seconds(input_path)
    if duration <= 0:
        print("Media duration is zero or invalid.", file=sys.stderr)
        sys.exit(1)

    midpoint = duration / 2.0
    start2 = max(midpoint - 1.0, 0.0)

    t1 = format_hhmmss_mmm(midpoint)
    ss2 = format_hhmmss_mmm(start2)

    parent = str(Path(input_path).parent)
    name = Path(input_path).stem
    ext = Path(input_path).suffix
    out1 = str(Path(parent) / f"{name}_part1{ext}")
    out2 = str(Path(parent) / f"{name}_part2{ext}")

    print(f"Input : {input_path}")
    print(f"Duration: {duration:.3f}s, Midpoint: {midpoint:.3f}s, Part2 starts at: {start2:.3f}s")
    print(f"Output1: {out1}")
    print(f"Output2: {out2}")

    # Part 1: from 0 to midpoint
    cmd1 = [
        "ffmpeg",
        "-y",
        "-hide_banner", "-loglevel", "error",
        "-i", input_path,
        "-t", t1,
        "-c", "copy",
        "--",
        out1,
    ]
    run(cmd1)

    # Part 2: from (midpoint - 1s) to end
    cmd2 = [
        "ffmpeg",
        "-y",
        "-hide_banner", "-loglevel", "error",
        "-ss", ss2,
        "-i", input_path,
        "-c", "copy",
        "--",
        out2,
    ]
    run(cmd2)

    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Split video at midpoint with 1s overlap (no re-encode)")
    parser.add_argument("input", help="Path to input video file")
    args = parser.parse_args()
    split_midpoint_with_overlap(args.input)


if __name__ == "__main__":
    main()


