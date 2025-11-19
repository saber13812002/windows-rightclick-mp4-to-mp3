@echo off
setlocal enabledelayedexpansion

REM === مسیر فایل‌های ثابت ===
set START=start.mp3
set MIDDLE=middle.mp3
set FINAL=final.mp3

REM === فولدر فعلی ===
set CURR=%cd%

for %%F in (*.mp3) do (
    if /I not "%%F"=="%START%" if /I not "%%F"=="%MIDDLE%" if /I not "%%F"=="%FINAL%" (
        echo Processing %%F ...

        REM === بدست آوردن طول فایل اصلی ===
        for /f "tokens=2 delims==" %%A in ('ffprobe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 "%%F"') do set DURATION=%%A

        REM === محاسبه وسط و نقاط برش ===
        set /a MID=!DURATION!/2
        set /a BACK=!MID!-5

        echo Duration=!DURATION! sec, Mid=!MID!, Back=!BACK!

        REM === برش بخش اول و دوم از فایل اصلی ===
        ffmpeg -y -i "%%F" -t !MID! "part1.mp3"
        ffmpeg -y -i "%%F" -ss !BACK! "part2.mp3"

        REM === چسباندن فایل‌ها ===
        (
            echo file '%START%'
            echo file 'part1.mp3'
            echo file '%MIDDLE%'
            echo file 'part2.mp3'
            echo file '%FINAL%'
        ) > list.txt

        ffmpeg -y -f concat -safe 0 -i list.txt -c copy "output_%%~nF.mp3"

        del part1.mp3 part2.mp3 list.txt
        echo Done: output_%%~nF.mp3
    )
)

echo All files processed!
pause
