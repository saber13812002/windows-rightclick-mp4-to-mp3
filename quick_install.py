"""
Quick installer — works on a fresh Windows machine with (almost) nothing installed.

Right-click quick_install.py -> Run with Python   (or:  python quick_install.py)

What it does (automatically):
  1. Finds a Python (system, or downloads an embedded Python into python/ if missing)
  2. Ensures a bundled FFmpeg (downloads it into ffmpeg/ if missing)
  3. Elevates to Administrator if needed (UAC prompt)
  4. Generates config.json + register_all.reg (via setup.py)
  5. Imports the registry -> right-click menu options appear

To remove everything later: run uninstall.bat as Administrator.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY_VERSION = "3.11.9"


def info(msg: str) -> None:
    print(f">>> {msg}")


def ok(msg: str) -> None:
    print(f"OK  {msg}")


def warn(msg: str) -> None:
    print(f"!!  {msg}")


def fail(msg: str) -> None:
    warn(msg)
    input("Press Enter to exit...")
    sys.exit(1)


# ─── 1. Find / download Python ───────────────────────────────────────────────
def find_python() -> Path:
    """Return a usable python.exe, downloading an embedded one if necessary."""
    # a) bundled python/ (from a previous run or download-deps.ps1)
    bundled = ROOT / "python" / "python.exe"
    if bundled.exists():
        ok(f"Using bundled Python: {bundled}")
        return bundled

    # b) py launcher / python on PATH
    for cmd in (["py", "-3"], ["python"], ["python3"]):
        try:
            out = subprocess.run(
                cmd + ["-c", "import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=30,
            )
            exe = out.stdout.strip()
            if out.returncode == 0 and exe:
                ok(f"Using system Python: {exe}")
                return Path(exe)
        except Exception:
            pass

    # c) the Python that is running this script itself (always exists)
    try:
        return Path(sys.executable).resolve()
    except Exception:
        pass

    # d) last resort -> download embedded Python
    warn("No Python found on this machine. Downloading embedded Python...")
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "amd64"
    url = f"https://www.python.org/ftp/python/{PY_VERSION}/python-{PY_VERSION}-embed-{arch}.zip"
    dest = ROOT / "python"
    dest.mkdir(exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tf:
            zip_path = Path(tf.name)
        info(f"Downloading {url}")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest)
        zip_path.unlink(missing_ok=True)
        # embedded python works fine for stdlib-only scripts as-is
        if (dest / "python.exe").exists():
            ok(f"Embedded Python ready: {dest / 'python.exe'}")
            return dest / "python.exe"
    except Exception as e:
        fail(f"Could not download Python: {e}")
    fail("No Python available and download failed.")


# ─── 2. Find / download FFmpeg ───────────────────────────────────────────────
def ensure_ffmpeg() -> Path:
    ff = ROOT / "ffmpeg" / "ffmpeg.exe"
    fp = ROOT / "ffmpeg" / "ffprobe.exe"
    if ff.exists() and fp.exists():
        ok(f"FFmpeg already present: {ff.parent}")
        return ff

    path_ff = shutil.which("ffmpeg")
    if path_ff:
        ok(f"Using system FFmpeg: {path_ff}")
        return Path(path_ff)

    warn("No FFmpeg found. Downloading portable FFmpeg...")
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tf:
            zip_path = Path(tf.name)
        info("Downloading FFmpeg (this can take a while)...")
        urllib.request.urlretrieve(url, zip_path)
        tmp = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)
        zip_path.unlink(missing_ok=True)
        bin_dir = next(iter(p for p in tmp.rglob("bin") if p.is_dir()), None)
        if bin_dir is None:
            raise RuntimeError("Could not find bin/ inside the FFmpeg archive.")
        ffdir = ROOT / "ffmpeg"
        ffdir.mkdir(exist_ok=True)
        shutil.copy(bin_dir / "ffmpeg.exe", ffdir / "ffmpeg.exe")
        shutil.copy(bin_dir / "ffprobe.exe", ffdir / "ffprobe.exe")
        shutil.rmtree(tmp, ignore_errors=True)
        ok(f"FFmpeg ready: {ffdir}")
        return ffdir / "ffmpeg.exe"
    except Exception as e:
        fail(f"Could not download FFmpeg: {e}")


# ─── 3. Elevation ────────────────────────────────────────────────────────────
def is_admin() -> bool:
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def reelevate(python_exe: Path) -> None:
    """Re-run this script as Administrator, then exit the current process."""
    info("Requesting administrator privileges (UAC prompt)...")
    script = str(ROOT / Path(__file__).name)
    ps = (
        "Start-Process -FilePath "
        f'"{python_exe}" -ArgumentList \'{script} --elevated\' '
        "-Verb RunAs -Wait"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    print("Installation finished (see the elevated window for details).")
    input("Press Enter to exit...")
    sys.exit(0)


# ─── 4. Generate + import registry ───────────────────────────────────────────
def generate_and_import(python_exe: Path, ffmpeg: Path) -> None:
    info("Generating config.json + register_all.reg ...")
    setup = ROOT / "setup.py"
    r = subprocess.run(
        [str(python_exe), str(setup), "--ffmpeg", str(ffmpeg), "--no-open"],
        cwd=ROOT, text=True,
    )
    if r.returncode != 0 or not (ROOT / "register_all.reg").exists():
        fail("setup.py failed to generate register_all.reg")
    ok("register_all.reg created")

    info("Importing registry entries...")
    r = subprocess.run(
        ["reg", "import", str(ROOT / "register_all.reg")],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        fail(f"Registry import failed: {r.stderr.strip()}")
    ok("Registry imported successfully")


def main() -> None:
    print("=" * 60)
    print("   Right-Click MP3/MP4 Tools - Quick Installer")
    print("=" * 60)

    python_exe = find_python()
    ffmpeg = ensure_ffmpeg()

    if not is_admin() and "--elevated" not in sys.argv:
        reelevate(python_exe)  # exits

    generate_and_import(python_exe, ffmpeg)

    print("=" * 60)
    print("   DONE! Right-click menu options are installed.")
    print("=" * 60)
    print()
    print("  .mp4 / .m4a  -> Convert to MP3 (High/Medium/Low/64/56/48 kbps)")
    print("  .mp4 / .m4a  -> Convert to OGG 48kHz")
    print("  .mkv/.avi/.webm/.mov -> Convert to OGG 48kHz")
    print("  .mp4 / .mp3  -> Split midpoint (1s overlap)")
    print("  .mp3         -> Add Custom Music / Remove Silence / Split on Silence")
    print("  Folder       -> Batch convert all (incl. bitrate submenus)")
    print()
    print("  Uninstall:  uninstall.bat  (Run as Administrator)")
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
