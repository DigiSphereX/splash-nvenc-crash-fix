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

## Technical Details

The generated DLL is a minimal 32-bit PE DLL (1.5 KB) with:
- **DllMain** (entry point): Returns `TRUE` so `LoadLibrary` succeeds
- **NvEncodeAPICreateInstance**: Returns `0` (NULL) to indicate NVENC is unavailable
- No external dependencies

The stub is generated purely with Python's `struct` module — no compiler needed.

## Disclaimer / Backup advice

Use this fix at your own risk. Before applying it: read the generator (plain Python
source), **back up** the original `nvEncodeAPI.dll` you replace, and create a system
restore point. The fix places an unsigned DLL in Splash's `Program Files` folder
(requires Administrator) and only disables NVENC. The author is not responsible for
any unintentional damage or data loss.

## ☕ Support this project

Free and open source (MIT). If this project saved you time or money, consider a small thank-you:

- **GitHub Sponsors** -> https://github.com/sponsors/DigiSphereX
- **PayPal** -> https://www.paypal.com/donate/?hosted_button_id=CFANQH892RPH2
