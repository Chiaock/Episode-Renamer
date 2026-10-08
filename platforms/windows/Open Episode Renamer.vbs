Option Explicit
Dim shell, files, directory, command
Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
directory = files.GetParentFolderName(WScript.ScriptFullName)
command = "powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & files.BuildPath(directory, "launcher.ps1") & Chr(34)
shell.Run command, 0, False
