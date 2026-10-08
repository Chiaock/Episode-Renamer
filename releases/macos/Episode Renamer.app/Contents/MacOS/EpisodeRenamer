#!/bin/zsh
APP_RESOURCES="${0:A:h:h}/Resources"
local_python=''
for candidate in /Library/Frameworks/Python.framework/Versions/3.*/bin/python3(N) /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  [[ -x "$candidate" ]] || continue
  if "$candidate" -c 'import tkinter as tk; r=tk.Tk(); r.withdraw(); r.destroy()' >/dev/null 2>&1; then
    local_python="$candidate"
    break
  fi
done
if [[ -z "$local_python" ]]; then
  /usr/bin/osascript -e 'display dialog "Python with Tkinter is required. Open the setup assistant? It will ask before installing anything." buttons {"Cancel", "Open Setup"} default button "Open Setup"' >/dev/null 2>&1 || exit 0
  /usr/bin/open "$APP_RESOURCES/Install and Open.command"
  exit 0
fi
RENAME_LOG_DIR="${TMPDIR:-/tmp/}"
"$local_python" "$APP_RESOURCES/rename_gui.py" > "${RENAME_LOG_DIR}episode-renamer-app.log" 2>&1
if [[ $? -ne 0 ]]; then
  /usr/bin/osascript -e 'display alert "Episode Renamer could not start" message "Details were saved in episode-renamer-app.log in your temporary folder."' >/dev/null 2>&1
fi
