import os
import subprocess
import sys
import re
import tempfile


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


def detect_silence(input_path, silence_duration=5.0, silence_threshold=-30):
    """
    تشخیص بخش‌های سکوت در فایل صوتی
    silence_duration: حداقل مدت سکوت برای حذف (ثانیه)
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


def remove_long_silence(input_path, silence_duration=5.0):
    """
    حذف سکوت‌های طولانی (5 ثانیه‌ای یا بیشتر) از فایل صوتی
    این فیچر برای حذف سکوت‌های طولانی مثل یک دقیقه کامل یا بیشتر مناسب است
    """
    if not os.path.exists(input_path):
        print(f"فایل پیدا نشد: {input_path}")
        sys.exit(1)
    
    print(f"در حال پردازش: {input_path}")
    print(f"در حال جستجوی سکوت‌های طولانی ({silence_duration} ثانیه یا بیشتر)...")
    
    # تشخیص سکوت‌ها
    silence_starts, silence_ends = detect_silence(input_path, silence_duration)
    
    if not silence_starts:
        print(f"سکوت {silence_duration} ثانیه‌ای یا بیشتر پیدا نشد. فایل بدون تغییر کپی می‌شود.")
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_no_long_silence{ext}"
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-c", "copy",
            output_path
        ]
        run(cmd)
        print(f"فایل خروجی: {output_path}")
        return
    
    # دریافت مدت زمان کل فایل
    total_duration = get_audio_duration(input_path)
    
    # محاسبه مدت زمان کل سکوت‌ها
    total_silence_duration = 0.0
    for i, silence_start in enumerate(silence_starts):
        if i < len(silence_ends):
            total_silence_duration += silence_ends[i] - silence_start
        else:
            # اگر پایان سکوت پیدا نشد، تا انتهای فایل در نظر می‌گیریم
            total_silence_duration += total_duration - silence_start
    
    print(f"تعداد سکوت‌های طولانی پیدا شده: {len(silence_starts)}")
    print(f"مدت زمان کل سکوت‌ها: {total_silence_duration:.2f} ثانیه ({total_silence_duration/60:.2f} دقیقه)")
    
    # ساخت لیست بخش‌های غیر سکوت
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
        print("تمام فایل سکوت است!")
        sys.exit(1)
    
    print(f"تعداد بخش‌های غیر سکوت پیدا شده: {len(segments)}")
    
    # اگر فقط یک بخش باشد، می‌توانیم مستقیماً کپی کنیم
    if len(segments) == 1:
        start, end = segments[0]
        duration = end - start
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_no_long_silence{ext}"
        
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            output_path
        ]
        run(cmd)
        print(f"فایل خروجی: {output_path}")
        return
    
    # برای چند بخش، باید آن‌ها را استخراج و به هم بچسبانیم
    temp_dir = tempfile.mkdtemp()
    segment_files = []
    
    try:
        # استخراج هر بخش
        for i, (start, end) in enumerate(segments):
            duration = end - start
            segment_file = os.path.join(temp_dir, f"segment_{i:04d}.mp3")
            segment_files.append(segment_file)
            
            print(f"استخراج بخش {i+1}/{len(segments)}: {start:.2f}s تا {end:.2f}s")
            
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start),
                "-i", input_path,
                "-t", str(duration),
                "-c", "copy",
                segment_file
            ]
            run(cmd)
        
        # ساخت فایل لیست برای concat
        concat_list = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list, 'w', encoding='utf-8') as f:
            for segment_file in segment_files:
                # تبدیل مسیر به فرمت مناسب برای concat
                abs_path = os.path.abspath(segment_file).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        # چسباندن بخش‌ها
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_no_long_silence{ext}"
        
        print("در حال چسباندن بخش‌ها...")
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            output_path
        ]
        run(cmd)
        
        # محاسبه مدت زمان فایل خروجی
        output_duration = get_audio_duration(output_path)
        saved_time = total_duration - output_duration
        
        print(f"\n✓ پردازش کامل شد!")
        print(f"فایل خروجی: {output_path}")
        print(f"تعداد بخش‌های سکوت حذف شده: {len(silence_starts)}")
        print(f"مدت زمان فایل اصلی: {total_duration/60:.2f} دقیقه")
        print(f"مدت زمان فایل خروجی: {output_duration/60:.2f} دقیقه")
        print(f"زمان صرفه‌جویی شده: {saved_time/60:.2f} دقیقه ({saved_time:.2f} ثانیه)")
        
    finally:
        # پاک کردن فایل‌های موقت
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("استفاده: python remove_long_silence.py <فایل_mp3> [مدت_سکوت]")
        print("مثال: python remove_long_silence.py audio.mp3 5.0")
        sys.exit(1)
    
    input_file = sys.argv[1]
    silence_duration = 5.0  # حذف سکوت‌های 5 ثانیه‌ای یا بیشتر (پیش‌فرض)
    
    if len(sys.argv) >= 3:
        try:
            silence_duration = float(sys.argv[2])
            if silence_duration < 0:
                print("هشدار: مدت سکوت نمی‌تواند منفی باشد. از مقدار پیش‌فرض 5.0 استفاده می‌شود.")
                silence_duration = 5.0
        except ValueError:
            print("هشدار: مدت سکوت نامعتبر است. از مقدار پیش‌فرض 5.0 استفاده می‌شود.")
    
    remove_long_silence(input_file, silence_duration)


if __name__ == "__main__":
    main()

