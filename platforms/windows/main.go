package main

import (
    "embed"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "syscall"
    "unsafe"
)

//go:embed assets/*
var assets embed.FS

func showError(message string) {
    text, _ := syscall.UTF16PtrFromString(message)
    title, _ := syscall.UTF16PtrFromString("Episode Renamer")
    syscall.NewLazyDLL("user32.dll").NewProc("MessageBoxW").Call(0, uintptr(unsafe.Pointer(text)), uintptr(unsafe.Pointer(title)), 0x10)
}

func run() error {
    dir, err := os.MkdirTemp("", "EpisodeRenamer-")
    if err != nil { return err }
    defer os.RemoveAll(dir)
    for _, name := range []string{"rename_gui.py", "icon.png", "icon.ico", "launcher.ps1"} {
        content, err := assets.ReadFile("assets/" + name)
        if err != nil { return err }
        if err := os.WriteFile(filepath.Join(dir, name), content, 0600); err != nil { return err }
    }
    powershell := filepath.Join(os.Getenv("SystemRoot"), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
    command := exec.Command(powershell, "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", filepath.Join(dir, "launcher.ps1"))
    command.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
    if err := command.Run(); err != nil { return fmt.Errorf("The Windows launcher stopped. %v", err) }
    return nil
}

func main() {
    if err := run(); err != nil { showError(err.Error()) }
}
