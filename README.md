# windows-rightclick-mp4-to-mp3


 run reg file 
 then right click on mp4
 then select conver to mp3
 then enjoy


![تبدیل MP4 به MP3](Screenshot%202025-03-27%20113902.png)

## تقسیم ویدیو از وسط با هم‌پوشانی ۱ ثانیه‌ای

### پیش‌نیاز
- نصب FFmpeg (شامل ffmpeg و ffprobe) و اضافه بودن به PATH

### نصب منوی کلیک راست
- فایل `add_right_click_split_middle.reg` را اجرا کنید و Allow بزنید.

### استفاده
- روی هر فایل `mp4` راست‌کلیک کنید و گزینه «Split at midpoint (1s overlap)» را بزنید.
- خروجی‌ها کنار فایل اصلی ساخته می‌شوند: `<name>_part1.mp4` و `<name>_part2.mp4`.

### اجرای دستی (اختیاری)
```powershell
pwsh -File .\split_middle_overlap.ps1 "path\to\video.mp4"
```







https://chatgpt.com/c/68f4d9aa-a4b4-832c-a50b-a238e88c807d