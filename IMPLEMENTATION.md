# سند کامل پیاده‌سازی: تبدیل و پردازش فایل‌های صوتی/تصویری با راست‌کلیک

این سند همهٔ آنچه پیاده‌سازی شده را در یک فایل MD خلاصه می‌کند: نصب، رجیستری، تک‌فایل، batch، OGG برای ویدیو، لاگ و نسخه.

---

## ۱. نمای کلی

- **هدف:** راست‌کلیک روی فایل یا پوشه در ویندوز برای تبدیل/پردازش بدون نیاز به باز کردن ترمینال.
- **نصب:** یک‌بار در هر سیستم `setup.py` (یا `setup_win.bat`) اجرا می‌شود؛ مسیر پایتون و ffmpeg/ffprobe تشخیص یا از کاربر پرسیده می‌شود؛ فایل `register_all.reg` ساخته می‌شود و با اجرای آن همهٔ گزینه‌ها در منوی راست‌کلیک ثبت می‌شوند.
- **خروجی و خطا:** همهٔ اجراها (تک‌فایل و batch) در `context_menu.log` در روت پروژه لاگ می‌شوند؛ در ابتدای هر بلوک نسخه (مثلاً v1.1) نوشته می‌شود.

---

## ۲. ساختار پوشه‌ها و فایل‌ها

```
convert_mp4_to_mp3/
├── _ffmpeg_config.py          # مسیر ffmpeg/ffprobe از config.json؛ setup_context_menu_log؛ VERSION
├── config.json                # توسط setup ساخته می‌شود (مسیر ffmpeg/ffprobe)
├── context_menu.log           # لاگ خروجی/خطای راست‌کلیک (append)
├── register_all.reg           # توسط setup ساخته می‌شود (کلیدهای رجیستری)
├── setup.py                   # تولید config + reg؛ --python, --ffmpeg, --check, --version
├── setup_win.bat              # لانچر ویندوز: در صورت نبود پایتون/ffmpeg از کاربر می‌پرسد
├── check_setup.bat            # اجرای setup --check برای تست
├── SETUP.md                   # راهنمای نصب سه‌مرحله‌ای
├── IMPLEMENTATION.md          # این سند
│
├── convert-mp4-to-mp3/
│   └── convert_mp4_to_mp3.py  # تبدیل تک فایل .mp4 به .mp3
├── convert-m4a-to-mp3/
│   └── convert_m4a_to_mp3.py  # تبدیل تک فایل .m4a به .mp3
├── convert-to-ogg/
│   └── convert_to_ogg.py      # تبدیل تک فایل به OGG 48kHz (صدا؛ برای پیام‌رسان‌ها)
├── batch-convert/
│   └── batch_convert.py       # پردازش دسته‌ای پوشه: --action mp3|ogg|split_midpoint|...
├── split-mp4-middle/
│   └── split_middle_overlap.py # تقسیم از وسط با ۱ ثانیه هم‌پوشانی (.mp4 / .mp3)
├── add-music-to-mp3/
│   └── add_music.bat          # اضافه کردن موزیک ثابت به mp3های پوشه
├── remove-silence-mp3/
│   └── remove_silence.py      # حذف سکوت ۲+ ثانیه از .mp3
├── remove-long-silence-mp3/
│   └── remove_long_silence.py # حذف سکوت ۵+ ثانیه از .mp3
└── split-on-silence-mp3/
    └── split_on_silence.py    # تقسیم .mp3 بر اساس سکوت ۲+ ثانیه
```

---

## ۳. رجیستری ویندوز

### ۳.۱ راست‌کلیک روی فایل (SystemFileAssociations)

برای هر پسوند و هر گزینه، یک کلید به این شکل ساخته می‌شود:

- `HKEY_CLASSES_ROOT\SystemFileAssociations\.<ext>\shell\<RegKey>\`
- `HKEY_CLASSES_ROOT\SystemFileAssociations\.<ext>\shell\<RegKey>\command\`  
  مقدار: `"<python.exe>" "<script.py>" "%1"`

**جدول گزینه‌های تک‌فایل:**

| پسوند | برچسب منو | اسکریپت |
|--------|------------|----------|
| .mp4 | Convert to MP3 | convert-mp4-to-mp3/convert_mp4_to_mp3.py |
| .m4a | Convert to MP3 | convert-m4a-to-mp3/convert_m4a_to_mp3.py |
| .mp4, .m4a, .mkv, .avi, .webm, .mov | Convert to OGG 48kHz | convert-to-ogg/convert_to_ogg.py |
| .mp4, .mp3 | Split midpoint (1s overlap) | split-mp4-middle/split_middle_overlap.py |
| .mp3 | Add Custom Music | add-music-to-mp3/add_music.bat |
| .mp3 | Remove Silence (2s+) | remove-silence-mp3/remove_silence.py |
| .mp3 | Remove Long Silence (5s+) | remove-long-silence-mp3/remove_long_silence.py |
| .mp3 | Split on Silence (2s+) | split-on-silence-mp3/split_on_silence.py |

یعنی برای **OGG** علاوه بر mp4/m4a، پسوندهای ویدیویی **.mkv, .avi, .webm, .mov** هم همان اسکریپت `convert_to_ogg.py` را صدا می‌زنند.

### ۳.۲ راست‌کلیک روی پوشه (Directory)

برای هر عمل batch یک کلید به این شکل ساخته می‌شود:

- `HKEY_CLASSES_ROOT\Directory\shell\<RegKey>\`
- `HKEY_CLASSES_ROOT\Directory\shell\<RegKey>\command\`  
  مقدار: `"<python.exe>" "<batch_convert.py>" "--action" "<action>" "%1"`

**جدول گزینه‌های batch (پوشه):**

| برچسب منو | مقدار --action |
|------------|-----------------|
| Convert all in folder to MP3 | mp3 |
| Convert all in folder to OGG 48kHz | ogg |
| Split midpoint for all in folder | split_midpoint |
| Remove silence for all in folder | remove_silence |
| Remove long silence for all in folder | remove_long_silence |
| Split on silence for all in folder | split_on_silence |

`%1` در اینجا مسیر پوشه‌ای است که کاربر روی آن راست‌کلیک کرده است.

### ۳.۳ رفتار overwrite

هر بار که `register_all.reg` را اجرا کنی، همان کلیدهای این پروژه با مقادیر جدید (مسیرهای فعلی پایتون و اسکریپت‌ها) **جایگزین** می‌شوند. گزینه‌های سایر برنامه‌ها حذف نمی‌شوند.

---

## ۴. اسکریپت batch (`batch_convert.py`)

- **ورودی:** یک آرگومان موقعیتی `folder` (مسیر پوشه) و `--action` با یکی از مقادیر:  
  `mp3`, `ogg`, `split_midpoint`, `remove_silence`, `remove_long_silence`, `split_on_silence`.
- **منطق:**
  - اسکن پوشه برای فایل‌هایی با پسوندهای مجاز برای آن action.
  - برای هر فایل چک می‌شود آیا خروجی(ها) از قبل وجود دارد؛ اگر بله → **رد (skip)**.
  - بقیه یکی‌یکی با فراخوانی همان اسکریپت تک‌فایل (از طریق `subprocess`) پردازش می‌شوند.
- **بدون تعامل:** هیچ `input()` یا تأیید از کاربر؛ فقط چاپ و لاگ در `context_menu.log`.

**تعریف هر action (پسوندها و شرط skip):**

| action | پسوندهای ورودی | شرط skip |
|--------|-----------------|----------|
| mp3 | .mp4, .m4a | وجود فایل `name.mp3` |
| ogg | .mp4, .m4a, .mkv, .avi, .webm, .mov | وجود فایل `name.ogg` |
| split_midpoint | .mp4, .mp3 | وجود `name_part1.*` و `name_part2.*` |
| remove_silence | .mp3 | وجود `name_no_silence.mp3` |
| remove_long_silence | .mp3 | وجود `name_no_long_silence.mp3` |
| split_on_silence | .mp3 | وجود پوشه `name_parts` |

برای action برابر `mp3`، اسکریپت بر اساس پسوند انتخاب می‌شود:  
`.mp4` → `convert_mp4_to_mp3.py`، `.m4a` → `convert_m4a_to_mp3.py`.

---

## ۵. نصب و تنظیم اولیه

### ۵.۱ اجرای setup

- **با پایتون در PATH:**  
  `python setup.py`  
  یا با مسیر دستی پایتون/ffmpeg:  
  `python setup.py --python "C:\path\to\python.exe" --ffmpeg "C:\path\to\ffmpeg.exe"`
- **بدون پایتون در PATH:** دابل‌کلیک روی **setup_win.bat**. در صورت نبود ffmpeg در PATH، مسیر ffmpeg (یا پوشهٔ آن) از کاربر پرسیده می‌شود و در صورت نیاز به صورت خودکار به مسیر فایل `ffmpeg.exe` نرمال می‌شود (مثلاً با کپی از نوار آدرس اکسپلورر).

### ۵.۲ خروجی‌های setup

- **config.json:** مسیرهای `ffmpeg` و `ffprobe` (خالی یعنی استفاده از PATH).
- **register_all.reg:** همهٔ کلیدهای رجیستری برای فایل و پوشه با مسیرهای مطلق فعلی.
- پس از اجرا (در ویندوز) معمولاً یک بار `register_all.reg` باز می‌شود تا کاربر Merge را تأیید کند.

### ۵.۳ تست و نسخه

- `python setup.py --check` یا دابل‌کلیک **check_setup.bat**: گزارش وضعیت (پایتون، روت پروژه، وجود فایل‌های REQUIRED، config، ffmpeg، مسیر لاگ).
- `python setup.py --version`: فقط شمارهٔ نسخه (همان `VERSION` در `_ffmpeg_config.py`).

---

## ۶. لاگ و نسخه

- **فایل لاگ:** `context_menu.log` در روت پروژه؛ به صورت append.
- **محتوای هر بلوک:** یک خط با فرمت  
  `=== v<VERSION> | <ISO datetime> | <python executable> | argv: <sys.argv>`  
  و بعد همهٔ خروجی و خطاهای آن اجرا (از جمله خروجی ffmpeg).
- **نسخه:** در `_ffmpeg_config.py` متغیر `VERSION` (مثلاً `"1.1"`) تعریف شده و در همین هدر لاگ و در خروجی `setup --check` و `--version` استفاده می‌شود.

---

## ۷. لیست فایل‌های الزامی (REQUIRED در setup)

برای اینکه `setup --check` همه را تأیید کند، این مسیرها باید وجود داشته باشند:

- convert-mp4-to-mp3/convert_mp4_to_mp3.py
- convert-m4a-to-mp3/convert_m4a_to_mp3.py
- convert-to-ogg/convert_to_ogg.py
- batch-convert/batch_convert.py
- split-mp4-middle/split_middle_overlap.py
- add-music-to-mp3/add_music.bat
- remove-silence-mp3/remove_silence.py
- remove-long-silence-mp3/remove_long_silence.py
- split-on-silence-mp3/split_on_silence.py
- _ffmpeg_config.py

---

## ۸. خلاصهٔ قابلیت‌های پیاده‌سازی‌شده

| قابلیت | راست‌کلیک فایل | راست‌کلیک پوشه (batch) |
|--------|-----------------|-------------------------|
| تبدیل به MP3 | .mp4, .m4a | Convert all in folder to MP3 |
| تبدیل به OGG 48kHz | .mp4, .m4a, .mkv, .avi, .webm, .mov | Convert all in folder to OGG 48kHz |
| Split midpoint (۱s overlap) | .mp4, .mp3 | Split midpoint for all in folder |
| Add Custom Music | .mp3 | — |
| Remove Silence (۲s+) | .mp3 | Remove silence for all in folder |
| Remove Long Silence (۵s+) | .mp3 | Remove long silence for all in folder |
| Split on Silence (۲s+) | .mp3 | Split on silence for all in folder |

همهٔ اجراها (تک‌فایل و batch) بدون سؤال از کاربر انجام می‌شوند؛ در حالت batch فقط فایل‌هایی که خروجی‌شان از قبل ساخته نشده پردازش می‌شوند و بقیه رد می‌شوند.

این سند معادل یک فایل MD کامل از کل پیاده‌سازی است و برای مرجع بعدی یا انتقال به سیستم دیگر کافی است.
