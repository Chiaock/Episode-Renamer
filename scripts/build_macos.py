from pathlib import Path
import shutil
import subprocess
import sys

if sys.platform != "darwin":
    raise SystemExit("Build the macOS app on a Mac.")
root = Path(__file__).resolve().parents[1]
app = root / "build/Episode Renamer.app"
macos = app / "Contents/MacOS"
resources = app / "Contents/Resources"
macos.mkdir(parents=True, exist_ok=True)
resources.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / "platforms/macos/launcher.sh", macos / "EpisodeRenamer")
(macos / "EpisodeRenamer").chmod(0o755)
shutil.copy2(root / "platforms/macos/Info.plist", app / "Contents/Info.plist")
shutil.copy2(root / "src/rename_gui.py", resources / "rename_gui.py")
shutil.copy2(root / "src/icon.png", resources / "icon.png")
shutil.copy2(root / "assets/icon.icns", resources / "EpisodeRenamer.icns")
setup = (root / "platforms/macos/Setup and Open.command").read_text()
marker = "<<'EPISODE_RENAMER_PYTHON'\n"
head, remainder = setup.split(marker, 1)
_, tail = remainder.split("\nEPISODE_RENAMER_PYTHON\n", 1)
source = (root / "src/rename_gui.py").read_text()
source = "import os\n" + source
source = source.replace("root.geometry('900x560')", "root.geometry('900x560')\nPath(os.environ['RENAME_READY_FILE']).touch()")
setup = head + marker + source + "\nEPISODE_RENAMER_PYTHON\n" + tail
installer = resources / "Install and Open.command"
installer.write_text(setup)
installer.chmod(0o755)
archive = root / "build/Episode Renamer macOS.zip"
subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(app), str(archive)], check=True)
print(archive)
