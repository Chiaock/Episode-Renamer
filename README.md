# Episode Renamer

A small windowed utility for renaming TV episode videos and subtitles. Choose a folder, enter a show title and season, preview the filenames, and confirm the rename.

![Orange hand-drawn app icon](src/icon.png)

## Downloads and use

### macOS

Extract `releases/macos/Episode Renamer.zip`, then double-click **Episode Renamer.app**. The app opens without a Terminal window during normal use. If Python 3 with working Tkinter is missing, it offers to open a Terminal setup assistant; the assistant asks before downloading and installing official Python with Tkinter.

The optional `Episode Renamer.command` is a single-file shell launcher.

### Windows

Double-click `releases/windows/Episode Renamer.exe`. This is a single executable for 64-bit Intel/AMD Windows 10/11, with the orange icon embedded. It contains the Python application and PowerShell setup launcher, extracts them to a temporary folder at runtime, and removes that folder when the application closes.

If Python 3 with working Tkinter is missing, a Yes/No dialog offers to install official Python with Tkinter for the current user. The download is checked against its pinned SHA-256 hash and its Windows signature before installation. Setup requires internet. A command prompt is not shown.

`Episode Renamer EXE.zip` contains the same executable. `Episode Renamer Scripts.zip` contains the earlier portable script version; extract it completely and run **Open Episode Renamer.vbs**.

### Python source / Linux

With Python 3.8+ and Tkinter available, run:

```sh
python3 src/rename_gui.py
```

On Windows, use `python src/rename_gui.py`. The source also runs on Linux; automatic setup is provided only by the macOS and Windows launchers.

## Filename support

| Original filename | Title / season input | Result |
| --- | --- | --- |
| `[Title][05][BDRIP][720P].mp4` | My Show / 2 | `My Show - S02E05.mp4` |
| `Durarara_2-28.mkv` | Durarara / 2 | `Durarara - S02E28.mkv` |
| `Title S01E03.ass` | My Show / 1 | `My Show - S01E03.ass` |
| `[Title][OVA][02].mkv` | My Show / 1 | `My Show - S00E02.mkv` |

- Episode numbers are preserved; there is no automatic offset or renumbering.
- OVA, OAD, and Special files use season 00. An unnumbered special defaults to episode 01.
- Distinct specials need unique numbers to avoid conflicts.
- Supported video formats: MP4, MKV, AVI, MOV, M4V, WebM.
- Supported subtitles: ASS, SSA, SRT, VTT.
- Each run processes one folder, without scanning subfolders.
- Files with no detected episode number are skipped.
- Destination conflicts are checked before renaming. A failure during renaming can leave some files renamed; the dialog reports how many completed.

## Repository layout

```text
src/                 Python GUI and selected icon
assets/              Mac/Windows icon formats and generation prompts
platforms/macos/     App launcher, setup command, and bundle metadata
platforms/windows/   Go EXE wrapper, PowerShell setup, and embedded assets
scripts/             Rebuild scripts
releases/            Ready-to-use Mac and Windows programs
```

## Building

### macOS app

On macOS with Python 3:

```sh
python3 scripts/build_macos.py
```

Creates the app and ZIP in `build/`. No third-party Python build packages are required. The app uses an existing Python installation or offers setup; it does not bundle a Python interpreter.

### Windows executable

Install Go 1.24+ and Python 3 on your build machine, then run:

```sh
python3 scripts/build_windows.py
```

On Windows, replace `python3` with `python`. The Go compiler can cross-compile this wrapper from macOS or Linux. The script regenerates the Windows icon resource and embeds the source files into `build/Episode Renamer.exe`.

The executable bundles the application scripts and icon, but uses an existing Python installation or offers to install Python. It is not a frozen Python runtime.

### Changing setup versions

The installers are pinned to Python 3.14.7. To update them, change the installer version, filenames, and verified SHA-256 hashes together in the macOS setup command and Windows PowerShell launchers. Official sources:

- https://www.python.org/downloads/release/python-3147/
- https://docs.python.org/3/using/windows.html
- https://www.python.org/download/mac/tcltk/

## Validation and current limits

Both included build scripts successfully rebuilt their programs from source. Python syntax, Mac bundle metadata, ZIP integrity, and the Windows executable format and embedded icon were checked. The Windows program and setup flow have not been tested on Windows. The Mac dependency installation flow has not been tested on a Mac without Python. Neither application is signed; macOS or Windows may display a security prompt. Managed Windows computers may disable PowerShell or Windows Script Host.

## Publishing on GitHub

Extract this archive and use the contents of `episode-renamer-github` as your repository root. Keep the source and build scripts in the repository; the packaged binaries can also be attached to a GitHub Release. This archive does not include the compiler download, build caches, or local workspace paths.
