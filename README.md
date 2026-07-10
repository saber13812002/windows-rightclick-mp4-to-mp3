# پروژه تبدیل و پردازش فایل‌های صوتی و تصویری

این پروژه مجموعه‌ای از ابزارهای ساده برای تبدیل و پردازش فایل‌های صوتی و تصویری است که از طریق منوی کلیک راست ویندوز قابل دسترسی هستند.

![تبدیل MP4 به MP3](Screenshot%202025-03-27%20113902.png)

---

## نصب سریع (روش پیشنهادی — فقط ۳ مرحله)

روی هر **ویندوز خام** (حتی بدون Python و FFmpeg) با این سه مرحله کار می‌کند:

### 1. دانلود وابستگی‌ها (یک بار)

روی [`download-deps.ps1`](download-deps.ps1) راست‌کلیک کنید → **"Run with PowerShell"** را انتخاب کنید.

این اسکریپت به صورت خودکار:
- **FFmpeg** (نسخه پرتابل) را از gyan.dev دانلود می‌کند → [`ffmpeg/`](ffmpeg/)
- **Embedded Python 3.11** را از python.org دانلود می‌کند → [`python/`](python/)

> ⚠ نیاز به اینترنت دارد. حجم کل دانلود: ~35 MB

### 2. نصب (با دسترسی Admin)

روی [`install.bat`](install.bat) راست‌کلیک کنید → **"Run as Administrator"** را انتخاب کنید.

این اسکریپت:
- به صورت خودکار دسترسی Admin می‌گیرد (UAC)
- Python و FFmpeg باندل شده را تشخیص می‌دهد
- فایل [`register_all.reg`](register_all.reg) را با مسیرهای درست می‌سازد
- رجیستری را import می‌کند

### 3. استفاده

روی هر فایل (یا پوشه) راست‌کلیک کنید ← گزینه مورد نظر را انتخاب کنید.

---

## روش جایگزین (اگر Python از قبل نصب است)

اگر Python 3 از قبل روی سیستم نصب است، می‌توانید فقط FFmpeg را دانلود کنید و از روش قبلی استفاده کنید:

```powershell
# فقط FFmpeg را دانلود کن (بدون Python)
.\download-deps.ps1
```

سپس:
```powershell
# یا setup_win.bat را اجرا کن (به Python سیستم نیاز دارد)
setup_win.bat
```

یا با دستور مستقیم:
```powershell
python setup.py
```

بعد از اجرای هر کدام، فایل `register_all.reg` باز می‌شود — **Merge** یا **Allow** را بزنید.

---

## نصب دستی (قدیمی)

**روش پیشنهادی (یک‌بار روی هر سیستم):** رجوع به [SETUP.md](SETUP.md) — سه مرحله ساده؛ مسیر پایتون و ffmpeg خودکار تشخیص داده می‌شود و همه گزینه‌ها یک‌جا روی راست‌کلیک ثبت می‌شوند.

روش دستی (در صورت نیاز): برای هر فیچر جداگانه فایل `.reg` مربوطه را اجرا کنید (مسیرهای داخل فایل را با مسیر سیستم خودت عوض کن). بعد از اجرا در UAC گزینه Allow را بزن.

---

## حذف منوهای اضافه شده

روی [`uninstall.bat`](uninstall.bat) راست‌کلیک کنید → **"Run as Administrator"** → تمام گزینه‌ها از منوی راست‌کلیک پاک می‌شوند.

---

## ساختار پروژه

```
convert_mp4_to_mp3/
├── install.bat                       # [NEW] نصاب یک‌کلیک (Admin)
├── uninstall.bat                     # [NEW] حذف‌کننده
├── download-deps.ps1                 # [NEW] دانلود Python + FFmpeg پرتابل
├── ffmpeg/                           # [NEW] FFmpeg پرتابل (بعد از دانلود)
│   ├── ffmpeg.exe
│   └── ffprobe.exe
├── python/                           # [NEW] Embedded Python (بعد از دانلود)
│   └── python.exe
├── _ffmpeg_config.py                 # [MODIFIED] تشخیص ffmpeg باندل شده
├── setup.py                          # [MODIFIED] تشخیص خودکار python/ffmpeg
├── setup_win.bat                     # [MODIFIED] اولویت با python باندل شده
├── register_all.reg                  # ساخته شده توسط setup.py
├── config.json                       # ساخته شده توسط setup.py
├── context_menu.log                  # لاگ اجراها
│
├── convert-mp4-to-mp3/
│   ├── convert_mp4_to_mp3.py
│   └── convert to mp3.reg
├── convert-m4a-to-mp3/
│   ├── convert_m4a_to_mp3.py
│   └── add_right_click_m4a.reg
├── convert-to-ogg/
│   └── convert_to_ogg.py
├── batch-convert/
│   └── batch_convert.py
├── split-mp4-middle/
│   └── split_middle_overlap.py
├── split-mp3-middle/
│   └── add_right_click_split_middle_python_mp3.reg
├── add-music-to-mp3/
│   ├── add_music.bat                 # [MODIFIED] استفاده از ffmpeg باندل شده
│   ├── add music.reg
│   ├── start.mp3
│   ├── middle.mp3
│   └── finish.mp3
├── remove-silence-mp3/
│   ├── remove_silence.py
│   └── remove_silence.reg
├── remove-long-silence-mp3/
│   ├── remove_long_silence.py
│   └── remove_long_silence.reg
└── split-on-silence-mp3/
    ├── split_on_silence.py
    └── split_on_silence.reg
```

---

## فیچرهای موجود

### 1. تبدیل MP4 به MP3
**پوشه**: [`convert-mp4-to-mp3/`](convert-mp4-to-mp3/)  
تبدیل فایل‌های ویدیویی MP4 به فایل‌های صوتی MP3.

### 2. تبدیل M4A به MP3
**پوشه**: [`convert-m4a-to-mp3/`](convert-m4a-to-mp3/)  
تبدیل فایل‌های صوتی M4A به فرمت MP3.

### 3. تبدیل به OGG 48kHz
**پوشه**: [`convert-to-ogg/`](convert-to-ogg/)  
تبدیل فایل‌های MP4, M4A, MKV, AVI, WEBM, MOV به OGG با کیفیت 48kHz (مناسب برای پیام‌رسان‌ها).

### 4. تقسیم ویدیو از وسط با هم‌پوشانی (MP4)
**پوشه**: [`split-mp4-middle/`](split-mp4-middle/)  
تقسیم فایل‌های ویدیویی MP4 از نقطه میانی با هم‌پوشانی 1 ثانیه‌ای.

### 5. تقسیم فایل صوتی از وسط با هم‌پوشانی (MP3)
**پوشه**: [`split-mp3-middle/`](split-mp3-middle/)  
تقسیم فایل‌های صوتی MP3 از نقطه میانی با هم‌پوشانی 1 ثانیه‌ای.

### 6. اضافه کردن موزیک به فایل‌های MP3
**پوشه**: [`add-music-to-mp3/`](add-music-to-mp3/)  
اضافه کردن فایل‌های موزیک ثابت (start.mp3، middle.mp3، finish.mp3) به ابتدا، وسط و انتهای فایل‌های MP3.

### 7. حذف سکوت از فایل‌های MP3
**پوشه**: [`remove-silence-mp3/`](remove-silence-mp3/)  
حذف خودکار بخش‌های سکوت 2 ثانیه‌ای یا بیشتر.

### 8. حذف سکوت‌های طولانی از فایل‌های MP3
**پوشه**: [`remove-long-silence-mp3/`](remove-long-silence-mp3/)  
حذف خودکار بخش‌های سکوت طولانی (5 ثانیه‌ای یا بیشتر). مناسب برای فایل‌های طولانی.

### 9. تقسیم موسیقی بر اساس سکوت
**پوشه**: [`split-on-silence-mp3/`](split-on-silence-mp3/)  
تقسیم فایل صوتی MP3 به قطعات جداگانه بر اساس سکوت‌های 2 ثانیه‌ای یا بیشتر.

---

## عملیات Batch (راست‌کلیک روی پوشه)

علاوه بر راست‌کلیک روی فایل‌ها، می‌توانید روی **پوشه** راست‌کلیک کنید و یکی از گزینه‌های زیر را انتخاب کنید:

- **Convert all in folder to MP3** — تبدیل همه MP4/M4A به MP3
- **Convert all in folder to OGG 48kHz** — تبدیل همه به OGG
- **Split midpoint for all in folder** — تقسیم همه فایل‌ها از وسط
- **Remove silence for all in folder** — حذف سکوت از همه MP3ها
- **Remove long silence for all in folder** — حذف سکوت‌های طولانی
- **Split on silence for all in folder** — تقسیم همه بر اساس سکوت

> فایل‌هایی که خروجی‌شان از قبل ساخته شده، **رد** می‌شوند (بدون سؤال).

---

## پیش‌نیازها (برای روش دستی)

- نصب **Python 3** (پایتون 3.11 یا بالاتر) — در روش باندل شده نیاز نیست
- نصب **FFmpeg** (شامل `ffmpeg` و `ffprobe`) و اضافه بودن به PATH سیستم — در روش باندل شده نیاز نیست
- سیستم عامل **Windows**

---

## اجرای دستی اسکریپت‌ها

همه اسکریپت‌های پایتون را می‌توان به صورت دستی نیز اجرا کرد:

```bash
python convert-mp4-to-mp3/convert_mp4_to_mp3.py "path\to\file.mp4"
python convert-m4a-to-mp3/convert_m4a_to_mp3.py "path\to\file.m4a"
python split-mp4-middle/split_middle_overlap.py "path\to\file.mp4"
python remove-silence-mp3/remove_silence.py "path\to\file.mp3"
# یا با مدت سکوت سفارشی:
python remove-silence-mp3/remove_silence.py "path\to\file.mp3" 3.0
python remove-long-silence-mp3/remove_long_silence.py "path\to\file.mp3"
# یا با مدت سکوت سفارشی:
python remove-long-silence-mp3/remove_long_silence.py "path\to\file.mp3" 10.0
python split-on-silence-mp3/split_on_silence.py "path\to\file.mp3"
# یا با مدت سکوت سفارشی:
python split-on-silence-mp3/split_on_silence.py "path\to\file.mp3" 3.0
```

---

## یادداشت توسعه

- هر فیچر جدید باید شامل یک فایل پایتون و یک فایل رجیستری باشد
- هر فیچر باید در پوشه جداگانه با نام انگلیسی قرار بگیرد
- نام پوشه‌ها باید واضح و توصیفی باشند (استفاده از خط تیره برای جدا کردن کلمات)
- نام فایل‌ها باید واضح و توصیفی باشند
- هر فیچر جدید باید در این README مستندسازی شود
- هنگام ساخت فایل رجیستری جدید، مسیر فایل پایتون باید به مسیر کامل در پوشه مربوطه اشاره کند
