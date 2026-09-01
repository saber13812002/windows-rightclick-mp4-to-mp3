# پروژه تبدیل و پردازش فایل‌های صوتی و تصویری

این پروژه مجموعه‌ای از ابزارهای ساده برای تبدیل و پردازش فایل‌های صوتی و تصویری است که از طریق منوی کلیک راست ویندوز قابل دسترسی هستند.

![تبدیل MP4 به MP3](Screenshot%202025-03-27%20113902.png)

---

## 🚀 نصب فوق‌العاده سریع (روی ویندوز خام)

**روی هر ویندوزی** — حتی بدون Python و FFmpeg — کار می‌کند.

### روش ۱: استفاده از EXEهای کامپایل شده (پیشنهادی)

اگر فایل‌های آماده در پوشه [`dist/`](dist/) دارید:

**۱.** روی [`install.bat`](install.bat) راست‌کلیک کنید → **Run as Administrator**

**۲.** راست‌کلیک روی فایل‌های mp4/m4a/mp3 → همه گزینه‌ها در منو.

> ✅ نیاز به Python یا FFmpeg جداگانه ندارد — همه چیز در EXEها و [`ffmpeg/`](ffmpeg/) باندل شده است.

### روش ۲: ساخت EXEها در محل

اگر کد منبع را clone کرده‌اید و می‌خواهید EXEها را خودتان بسازید:

**۱.** روی [`build-exes.ps1`](build-exes.ps1) راست‌کلیک کنید → **Run with PowerShell**

این اسکریپت:
- PyInstaller را نصب می‌کند (یک بار)
- همه اسکریپت‌های پایتون را به EXE کامپایل می‌کند → [`dist/`](dist/)
- FFmpeg پرتابل را دانلود می‌کند → [`dist/ffmpeg/`](dist/ffmpeg/)
- فایل‌های کمکی را کپی می‌کند

**۲.** سپس روی [`dist/install.bat`](dist/install.bat) راست‌کلیک کنید → **Run as Administrator**

**۳.** راست‌کلیک روی فایل‌ها → همه گزینه‌ها در منو.

---

## 📦 روش جایگزین (با Python سیستم)

اگر Python 3 از قبل روی سیستم نصب است:

```powershell
# مرحله ۱: اجرای setup
python setup.py

# مرحله ۲: import رجیستری
# (فایل register_all.reg باز می‌شود − Merge یا Allow را بزنید)
```

یا دابل‌کلیک کنید روی **`setup_win.bat`**

---

## 🗑️ حذف منوهای اضافه شده

روی [`uninstall.bat`](uninstall.bat) راست‌کلیک کنید → **Run as Administrator** → تمام گزینه‌ها از منوی راست‌کلیک پاک می‌شوند.

---

## 📁 ساختار پروژه

```
windows-rightclick-mp4-to-mp3/
│
├── install.bat                       # نصاب یک‌کلیک (Admin)
├── uninstall.bat                     # حذف‌کننده
├── build-exes.ps1                    # [NEW] کامپایل EXE + دانلود FFmpeg
├── download-deps.ps1                 # دانلود Python + FFmpeg پرتابل
├── setup.py                          # [MODIFIED] تشخیص خودکار python/ffmpeg/EXE
├── setup_win.bat                     # [MODIFIED] اولویت با EXE/python باندل شده
├── _ffmpeg_config.py                 # [MODIFIED] تشخیص PyInstaller + ffmpeg باندل شده
│
├── dist/                             # [NEW] خروجی build-exes.ps1
│   ├── install.bat
│   ├── uninstall.bat
│   ├── setup.exe
│   ├── convert_mp4_to_mp3.exe
│   ├── convert_m4a_to_mp3.exe
│   ├── convert_to_ogg.exe
│   ├── batch_convert.exe
│   ├── split_middle_overlap.exe
│   ├── remove_silence.exe
│   ├── remove_long_silence.exe
│   ├── split_on_silence.exe
│   ├── config.json
│   ├── register_all.reg
│   ├── context_menu.log
│   ├── ffmpeg/
│   │   ├── ffmpeg.exe
│   │   └── ffprobe.exe
│   └── add-music-to-mp3/
│       ├── add_music.bat             # [MODIFIED] استفاده از ffmpeg باندل شده
│       └── *.mp3
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
│   ├── add_music.bat
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

## ✨ فیچرهای موجود

### فایل → راست‌کلیک

| فیچر | پسوند | توضیح |
|------|-------|-------|
| **Convert to MP3** | `.mp4`, `.m4a` | تبدیل به MP3 |
| **Convert to OGG 48kHz** | `.mp4`, `.m4a`, `.mkv`, `.avi`, `.webm`, `.mov` | تبدیل به OGG (مناسب پیام‌رسان) |
| **Split midpoint (1s overlap)** | `.mp4`, `.mp3` | تقسیم از وسط با ۱ ثانیه هم‌پوشانی |
| **Add Custom Music** | `.mp3` | اضافه کردن start/middle/finish به MP3 |
| **Remove Silence (2s+)** | `.mp3` | حذف سکوت‌های ۲+ ثانیه |
| **Remove Long Silence (5s+)** | `.mp3` | حذف سکوت‌های طولانی ۵+ ثانیه |
| **Split on Silence (2s+)** | `.mp3` | تقسیم بر اساس سکوت‌های ۲+ ثانیه |

### پوشه → راست‌کلیک (Batch)

| فیچر | توضیح |
|------|-------|
| **Convert all in folder to MP3** | تبدیل همه فایل‌های پوشه به MP3 |
| **Convert all in folder to OGG 48kHz** | تبدیل همه به OGG |
| **Split midpoint for all in folder** | تقسیم همه از وسط |
| **Remove silence for all in folder** | حذف سکوت همه |
| **Remove long silence for all in folder** | حذف سکوت‌های طولانی همه |
| **Split on silence for all in folder** | تقسیم همه بر اساس سکوت |

> فایل‌هایی که خروجی‌شان از قبل ساخته شده، **رد** می‌شوند (بدون سؤال).

---

## 🔧 توسعه

### پیش‌نیازهای ساخت (Build)

- **Python 3.11+** (فقط برای ماشین توسعه‌دهنده)
- **pip** (برای نصب PyInstaller)
- اینترنت (برای دانلود FFmpeg)

### ساخت نسخه پرتابل

```powershell
.\build-exes.ps1
```

خروجی در [`dist/`](dist/) — می‌توانید کل پوشه را Zip کنید و به هر سیستم ویندوزی ببرید.

### نکات توسعه

- هر فیچر جدید = یک فایل پایتون + یک پوشه مجزا
- اسکریپت‌ها از `_ffmpeg_config.py` برای یافتن ffmpeg استفاده می‌کنند
- هنگام ساخت EXE با PyInstaller، `_project_root()` مسیر EXE را برمی‌گرداند
- فایل `config.json` در کنار EXEها قرار می‌گیرد

---

## 📝 یادداشت‌ها

- **نسخه:** v{VERSION} (در [`_ffmpeg_config.py`](_ffmpeg_config.py))
- **لاگ:** هر اجرا در `context_menu.log` ثبت می‌شود
- **رجیستری:** `register_all.reg` توسط `setup.py` ساخته می‌شود
- **سازگاری:** Windows 10 / 11

برای اطلاعات بیشتر به [SETUP.md](SETUP.md) و [IMPLEMENTATION.md](IMPLEMENTATION.md) مراجعه کنید.
