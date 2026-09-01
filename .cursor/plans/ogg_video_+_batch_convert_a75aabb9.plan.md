---
name: OGG video + batch convert
overview: اضافه کردن OGG برای پسوندهای ویدیویی بیشتر، و تبدیل دسته‌ای پوشه برای همهٔ قابلیت‌ها (MP3، OGG، Split midpoint، Remove silence، Remove long silence، Split on silence) بدون تعامل و با skip اگر خروجی از قبل وجود داشته باشد.
todos: []
isProject: false
---

# طرح: OGG برای ویدیوها + تبدیل دسته‌ای بدون تعامل

## ۱. OGG برای فایل‌های ویدیویی بیشتر

الان فقط **`.mp4`** و **`.m4a`** گزینه «Convert to OGG 48kHz» را دارند.

- در [setup.py](setup.py) برای همان دستور `convert_to_ogg.py` رجیستری برای پسوندهای ویدیویی رایج اضافه شود تا راست‌کلیک روی این نوع فایل‌ها هم «Convert to OGG 48kHz» را نشان دهد.
- پسوندهای پیشنهادی: **`.mkv`**, **`.avi`**, **`.webm`**, **`.mov`** (همه با همان اسکریپت فعلی [convert-to-ogg/convert_to_ogg.py](convert-to-ogg/convert_to_ogg.py) که با ffmpeg هر مدیایی را به OGG 48kHz صدا تبدیل می‌کند).

**تغییر:** در حلقهٔ `entries` در `setup.py` چهار entry جدید با همان `reg_key` و همان `reg_cmd` برای این پسوندها اضافه شود.

---

## ۲. تبدیل دسته‌ای پوشه برای **همهٔ قابلیت‌ها** (بدون سؤال، رد کردن قبلی‌ها)

خواسته: راست‌کلیک روی **پوشه** → برای **همهٔ فانکشنالیتی‌ها** (ویدیو/صدا به MP3، به OGG، Split midpoint، Remove silence، و غیره) یک گزینهٔ batch وجود داشته باشد که همهٔ فایل‌های مناسب داخل پوشه را بدون سؤال یا وقفه پردازش کند و **فقط فایل‌هایی که هنوز خروجی ساخته نشده را** در نظر بگیرد (اگر خروجی از قبل وجود داشت → skip).

### ۲.۱ رجیستری برای راست‌کلیک روی پوشه

در ویندوز برای راست‌کلیک روی پوشه:

- `HKEY_CLASSES_ROOT\Directory\shell\<MenuLabel>\command`

در [setup.py](setup.py) علاوه بر `SystemFileAssociations\.<ext>` برای فایل‌ها، برای **Directory** هم به ازای هر قابلیت batch یک entry اضافه شود؛ `%1` = مسیر پوشه.

ساختار: برای فایل مثل الان `(ext, reg_key, label, cmd)`؛ برای پوشه مقدار خاص مثلاً `"Directory"` به‌جای پسوند و `base = Directory\shell\{reg_key}`. در حلقهٔ ساخت `.reg` با یک `if` بر اساس نوع، کلید رجیستری ساخته شود.

### ۲.۲ لیست قابلیت‌های batch (همهٔ فانکشنالیتی‌ها)

| عمل | پسوندهای ورودی | شرط skip (اگر خروجی وجود داشت) |

|-----|-----------------|----------------------------------|

| Convert all to MP3 | .mp4, .m4a | وجود `name.mp3` |

| Convert all to OGG 48kHz | .mp4, .m4a, .mkv, .avi, .webm, .mov | وجود `name.ogg` |

| Split midpoint (all) | .mp4, .mp3 | وجود `name_part1.*` و `name_part2.*` |

| Remove silence (all) | .mp3 | وجود `name_no_silence.mp3` |

| Remove long silence (all) | .mp3 | وجود `name_no_long_silence.mp3` |

| Split on silence (all) | .mp3 | وجود پوشه `name_parts` |

هر کدام یک گزینه در منوی راست‌کلیک پوشه با برچسب واضح (مثلاً «Convert all in folder to MP3», «Convert all in folder to OGG 48kHz», «Split midpoint for all in folder», …).

### ۲.۳ اسکریپت batch واحد

**یک اسکریپت** (مثلاً `batch-convert/batch_convert.py`) با آرگومان‌های `folder_path` و `--action <name>`:

- **ورودی:** `argv[1] `= مسیر پوشه، `--action` یکی از: `mp3`, `ogg`, `split_midpoint`, `remove_silence`, `remove_long_silence`, `split_on_silence`.
- **منطق:** برای action داده‌شده، پسوندهای ورودی و شرط skip از جدول بالا؛ اسکن پوشه؛ برای هر فایل اگر خروجی(ها) از قبل وجود داشت skip؛ وگرنه همان منطق اسکریپت تک‌فایل موجود (import یا subprocess) را اجرا کن.
- **بدون تعامل:** هیچ `input()`؛ فقط لاگ در `context_menu.log` با `setup_context_menu_log()`.

استفادهٔ مجدد از کد موجود:

- **MP3:** import از [convert-mp4-to-mp3](convert-mp4-to-mp3/convert_mp4_to_mp3.py) / [convert-m4a-to-mp3](convert-m4a-to-mp3/convert_m4a_to_mp3.py) یا subprocess.
- **OGG:** import از [convert-to-ogg/convert_to_ogg.py](convert-to-ogg/convert_to_ogg.py).
- **Split midpoint:** import از [split-mp4-middle/split_middle_overlap.py](split-mp4-middle/split_middle_overlap.py).
- **Remove silence / Remove long silence / Split on silence:** import از اسکریپت‌های مربوطه در [remove-silence-mp3](remove-silence-mp3/remove_silence.py), [remove-long-silence-mp3](remove-long-silence-mp3/remove_long_silence.py), [split-on-silence-mp3](split-on-silence-mp3/split_on_silence.py).

محل: پوشه **`batch-convert/`** با یک فایل `batch_convert.py`؛ در [setup.py](setup.py) و REQUIRED به آن اشاره شود و برای هر شش action یک entry رجیستری Directory اضافه شود.

---

## ۳. حالت‌های «Yes to all / No to all» (اختیاری برای آینده)

خواستهٔ «یس یس تو آل نو نو تو ال» معمولاً برای زمانی است که **خروجی از قبل وجود دارد** و کاربر بخواهد بگوید: همه را بازنویسی کن (Yes to all) یا هیچ‌کدام را بازنویسی نکن (No to all).

- در **حالت batch پوشه** که بالا توضیح داده شد، رفتار پیشنهادی: **همیشه «No to all» برای overwrite** — یعنی اگر خروجی وجود داشت، آن فایل را تبدیل نکن (بدون سؤال). این همان «بدون اینترکشن» و «فقط چیزهایی که هنوز تبدیل نشدن» است.
- اگر بعداً برای **تک فایل** (منوی راست‌کلیک روی خود فایل) بخواهی در صورت وجود خروجی سؤال کنی و گزینه Yes / Yes to all / No / No to all بدهی، آن را می‌توان در فاز بعد با یک اسکریپت wrapper یا یک دیالوگ ساده اضافه کرد. در این طرح فقط رفتار batch بدون تعامل و skip-if-exists پیاده می‌شود.

---

## ۴. خلاصهٔ فایل‌ها و تغییرات

| مورد | اقدام |

|------|--------|

| [setup.py](e:\saberprojects-eeeee\saber\convert_mp4_to_mp3\setup.py) | (۱) اضافه کردن entryهای OGG برای `.mkv`, `.avi`, `.webm`, `.mov`؛ (۲) پشتیبانی از نوع `Directory` در ساخت `.reg` و اضافه کردن **شش** گزینه batch: Convert all to MP3، Convert all to OGG 48kHz، Split midpoint for all، Remove silence for all، Remove long silence for all، Split on silence for all. |

| پوشهٔ جدید + اسکریپت | `batch-convert/batch_convert.py`: ورودی = مسیر پوشه + `--action` (mp3 | ogg | split_midpoint | remove_silence | remove_long_silence | split_on_silence)، اسکن، skip اگر خروجی وجود داشت، فراخوانی منطق اسکریپت‌های موجود، لاگ. |

| اسکریپت‌های فعلی (convert، split، remove، split_on_silence) | بدون تغییر در منطق تک‌فایل؛ فقط از توابع/ماژول‌شان در batch استفاده می‌شود. |

| [REQUIRED](e:\saberprojects-eeeee\saber\convert_mp4_to_mp3\setup.py) | اضافه کردن مسیر `batch-convert/batch_convert.py`. |

| [SETUP.md](e:\saberprojects-eeeee\saber\convert_mp4_to_mp3\SETUP.md) | توضیح راست‌کلیک روی پوشه و رفتار «همهٔ قابلیت‌ها به‌صورت batch؛ فقط فایل‌های بدون خروجی». |

---

## ۵. جریان کلی

```mermaid
flowchart LR
  subgraph file [راست‌کلیک فایل]
    A[mp4/m4a/mkv/avi/webm/mov]
    B[Convert to OGG 48kHz]
    A --> B
  end
  subgraph folder [راست‌کلیک پوشه]
    C[پوشه]
    D[batch_convert.py folder action]
    E[اسکن | skip اگر خروجی هست | اجرای همان منطق تك‌فایل]
    C --> D
    D --> E
  end
```

**خلاصه:** راست‌کلیک روی **فایل‌های ویدیویی** برای OGG (و پسوندهای بیشتر)؛ راست‌کلیک روی **پوشه** برای **همهٔ قابلیت‌ها** (MP3، OGG، Split midpoint، Remove silence، Remove long silence، Split on silence) به‌صورت batch، بدون تعامل، و فقط برای فایل‌هایی که خروجی‌شان هنوز ساخته نشده است.