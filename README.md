# Splash Player NVENC Crash Fix

Fixes Splash Player 2.7.0 crashing immediately (exit code 1) on Windows 10/11 with newer NVIDIA drivers.

## The Problem

Splash Player 2.7.0 tries to initialize **NVENC** (NVIDIA Video Encoder) at startup. When running with newer NVIDIA drivers (2024+), the NVENC API returns `NV_ENC_ERR_UNSUPPORTED_PARAM` because the API version has changed since 2019. Splash treats this as a fatal error and exits immediately with code 1, never opening the player window.

The error from stderr:
```
NVENC error at .\src\CNVEncoder.cpp:1417 code=12(NVENC unsupported parameter)
```

## The Fix

Place a stub `nvEncodeAPI.dll` in the Splash installation directory. Since Windows searches the application directory first when loading DLLs, this stub is loaded instead of the system NVENC driver.

The stub exports `NvEncodeAPICreateInstance` and returns `NULL` (0), which tells Splash that NVENC is not available. Splash then gracefully skips hardware encoding and falls back to software rendering.

**Result:** Splash opens and plays videos normally. Hardware NVENC encoding (video export) is disabled, but video playback works perfectly.

## Quick Install

1. Make sure [Python](https://www.python.org/) is installed
2. Right-click `install.bat` and **Run as Administrator**
3. Done!

## Manual Install

```bash
python fix/generate_stub.py "C:\Program Files (x86)\Mirillis\Splash\nvEncodeAPI.dll"
```

Run as Administrator (the Splash directory requires elevated permissions).

## Uninstall

Delete `nvEncodeAPI.dll` from the Splash installation folder:

```bash
del "C:\Program Files (x86)\Mirillis\Splash\nvEncodeAPI.dll"
```

## Compatibility

- Splash Player **2.7.0** (free version from [mirillis.com](https://mirillis.com/downloads))
- Windows 10 / Windows 11
- Any NVIDIA GPU driver version

## Security & Antivirus Notes

- **Nothing is downloaded from the internet**: the shortcut DLL is generated locally on your machine with Python's `struct` module. There are no binaries, no network calls, and no third-party payloads in this repository — the whole generator is ~4 KB of readable source you can inspect.
- **Antivirus/SmartScreen warning possible**: the generator places an *unsigned* DLL inside Splash's `Program Files` folder. Windows may show a SmartScreen notification (or treat the generated DLL as unusual). This is expected for any locally generated module and is not malware — the DLL only exports `NvEncodeAPICreateInstance` and returns `0`. If your AV quarantines it, add the Splash folder to the allow-list.
- **Run as Administrator** is required because the Splash folder is write-protected by Windows.
- Versioned Python launchers: `install.bat` now uses `python` if present, otherwise falls back to the `py` launcher, and exits with a clear message if neither exists (so it never silently executes a Store alias or an unrelated `python.exe`).

## Technical Details

The generated DLL is a minimal 32-bit PE DLL (1.5 KB) with:
- **DllMain** (entry point): Returns `TRUE` so `LoadLibrary` succeeds
- **NvEncodeAPICreateInstance**: Returns `0` (NULL) to indicate NVENC is unavailable
- No external dependencies

The stub is generated purely with Python's `struct` module — no compiler needed.

---

## ☕ Support this project

Free and open source (MIT). If this fix saved you time or money, consider a small thank-you:

- **GitHub Sponsors** -> https://github.com/sponsors/DigiSphereX
- **PayPal** -> https://www.paypal.com/donate/?hosted_button_id=CFANQH892RPH2
