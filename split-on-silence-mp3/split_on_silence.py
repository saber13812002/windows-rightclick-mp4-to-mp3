import os
import subprocess
import sys
import re


def run(cmd, capture_output=False):
    """اجرای دستور و بازگرداندن نتیجه"""
    result = subprocess.run(
        cmd, 
        check=True, 
        capture_output=capture_output, 
        text=True
    )
    if capture_output:
        return result.stdout
    return None


def detect_silence(input_path, silence_duration=2.0, silence_threshold=-30):
    """
    تشخیص بخش‌های سکوت در فایل صوتی
    silence_duration: حداقل مدت سکوت برای تقسیم (ثانیه)
    silence_threshold: آستانه سکوت بر حسب dB (مثبت = سکوت)
    """
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-af", f"silencedetect=noise={silence_threshold}dB:d={silence_duration}",
        "-f", "null",
        "-"
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        stderr=subprocess.STDOUT
    )
    
    # استخراج نقاط شروع و پایان سکوت
    silence_starts = []
    silence_ends = []
    
    # الگو برای پیدا کردن silence_start و silence_end
    start_pattern = r"silence_start: ([\d.]+)"
    end_pattern = r"silence_end: ([\d.]+)"
    
    for line in result.stderr.split('\n'):
        start_match = re.search(start_pattern, line)
        if start_match:
            silence_starts.append(float(start_match.group(1)))
        
        end_match = re.search(end_pattern, line)
        if end_match:
            silence_ends.append(float(end_match.group(1)))
    
    return silence_starts, silence_ends


def get_audio_duration(input_path):
    """دریافت مدت زمان فایل صوتی"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def split_on_silence(input_path, silence_duration=2.0):
    """
    تقسیم فایل صوتی به قطعات جداگانه بر اساس سکوت‌های 2 ثانیه‌ای یا بیشتر
    هر قطعه به عنوان یک فایل جداگانه ذخیره می‌شود
    """
    if not os.path.exists(input_path):
        print(f"فایل پیدا نشد: {input_path}")
        sys.exit(1)
    
    print(f"در حال پردازش: {input_path}")
    print(f"در حال جستجوی سکوت‌های {silence_duration} ثانیه‌ای یا بیشتر برای تقسیم...")
    
    # تشخیص سکوت‌ها
    silence_starts, silence_ends = detect_silence(input_path, silence_duration)
    
    # دریافت مدت زمان کل فایل
    total_duration = get_audio_duration(input_path)
    
    # ساخت لیست بخش‌های غیر سکوت (قطعات)
    segments = []
    current_pos = 0.0
    
    # اضافه کردن بخش‌های غیر سکوت
    for i, silence_start in enumerate(silence_starts):
        # اگر قبل از سکوت، بخش صوتی وجود دارد
        if silence_start > current_pos:
            segments.append((current_pos, silence_start))
        
        # به‌روزرسانی موقعیت فعلی به پایان سکوت
        if i < len(silence_ends):
            current_pos = silence_ends[i]
        else:
            current_pos = silence_start
    
    # اضافه کردن بخش آخر (اگر باقی مانده باشد)
    if current_pos < total_duration:
        segments.append((current_pos, total_duration))
    
    if not segments:
        print("هیچ بخش صوتی پیدا نشد! فایل ممکن است فقط سکوت باشد.")
        sys.exit(1)
    
    print(f"تعداد قطعات پیدا شده: {len(segments)}")
    
    # ساخت پوشه خروجی
    base, ext = os.path.splitext(input_path)
    output_dir = f"{base}_parts"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"پوشه خروجی: {output_dir}")
    print("\nدر حال استخراج قطعات...")
    
    # استخراج هر قطعه به عنوان فایل جداگانه
    for i, (start, end) in enumerate(segments, 1):
        duration = end - start
        
        # نام فایل خروجی با شماره ترتیب
        output_file = os.path.join(output_dir, f"part_{i:03d}{ext}")
        
        print(f"  قطعه {i}/{len(segments)}: {start:.2f}s تا {end:.2f}s ({duration:.2f}s) -> {os.path.basename(output_file)}")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            output_file
        ]
        run(cmd)
    
    print(f"\n✓ تقسیم کامل شد!")
    print(f"تعداد قطعات ساخته شده: {len(segments)}")
    print(f"مسیر پوشه خروجی: {output_dir}")
    print(f"مدت زمان کل فایل اصلی: {total_duration/60:.2f} دقیقه")
    
    # محاسبه مدت زمان کل قطعات
    total_segments_duration = sum(end - start for start, end in segments)
    print(f"مدت زمان کل قطعات: {total_segments_duration/60:.2f} دقیقه")


def main():
    if len(sys.argv) < 2:
        print("استفاده: python split_on_silence.py <فایل_mp3> [مدت_سکوت]")
        print("مثال: python split_on_silence.py audio.mp3 2.0")
        sys.exit(1)
    
    input_file = sys.argv[1]
    silence_duration = 2.0  # تقسیم بر اساس سکوت‌های 2 ثانیه‌ای یا بیشتر (پیش‌فرض)
    
    if len(sys.argv) >= 3:
        try:
            silence_duration = float(sys.argv[2])
            if silence_duration < 0:
                print("هشدار: مدت سکوت نمی‌تواند منفی باشد. از مقدار پیش‌فرض 2.0 استفاده می‌شود.")
                silence_duration = 2.0
        except ValueError:
            print("هشدار: مدت سکوت نامعتبر است. از مقدار پیش‌فرض 2.0 استفاده می‌شود.")
    
    split_on_silence(input_file, silence_duration)


if __name__ == "__main__":
    main()

