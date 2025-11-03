import os
import subprocess
import sys


def run(cmd):
    subprocess.run(cmd, check=True)


def ffprobe_duration_seconds(input_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        "--",
        input_path,
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    s = (result.stdout or "").strip()
    return float(s)


def format_hhmmss_mmm(seconds):
    if seconds < 0:
        seconds = 0.0
    millis = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"


def split_midpoint_with_overlap(input_path):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)

    duration = ffprobe_duration_seconds(input_path)
    if duration <= 0:
        print("Media duration is zero or invalid.")
        sys.exit(1)

    midpoint = duration / 2.0
    start2 = max(midpoint - 1.0, 0.0)

    t1 = format_hhmmss_mmm(midpoint)
    ss2 = format_hhmmss_mmm(start2)

    base, ext = os.path.splitext(input_path)
    out1 = f"{base}_part1{ext}"
    out2 = f"{base}_part2{ext}"

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


def main():
    input_file = sys.argv[1]
    split_midpoint_with_overlap(input_file)


if __name__ == "__main__":
    main()


