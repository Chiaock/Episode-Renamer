from pathlib import Path
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
platform = root / "platforms/windows"
shutil.copy2(root / "src/rename_gui.py", platform / "assets/rename_gui.py")
shutil.copy2(root / "src/icon.png", platform / "assets/icon.png")
shutil.copy2(root / "assets/icon.ico", platform / "assets/icon.ico")
subprocess.run([sys.executable, "build_icon_resource.py"], cwd=platform, check=True)
environment = dict(os.environ, GOOS="windows", GOARCH="amd64", CGO_ENABLED="0")
output = root / "build/Episode Renamer.exe"
output.parent.mkdir(exist_ok=True)
subprocess.run(["go", "build", "-trimpath", "-ldflags=-H=windowsgui -s -w", "-o", str(output), "."], cwd=platform, env=environment, check=True)
print(output)
