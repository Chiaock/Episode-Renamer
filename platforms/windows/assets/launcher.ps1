$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms

function Show-Error([string]$Text) {
    [void][System.Windows.Forms.MessageBox]::Show($Text, 'Episode Renamer', 'OK', 'Error')
}

function Find-Python {
    $candidates = @()
    $roots = @(
        'HKCU:\Software\Python\PythonCore',
        'HKLM:\Software\Python\PythonCore',
        'HKLM:\Software\WOW6432Node\Python\PythonCore'
    )
    foreach ($regRoot in $roots) {
        if (Test-Path $regRoot) {
            foreach ($version in Get-ChildItem $regRoot) {
                if ($version.PSChildName -notmatch '^3\.') { continue }
                $key = Join-Path $version.PSPath 'InstallPath'
                if (Test-Path $key) {
                    $installPath = (Get-Item $key).GetValue('')
                    if ($installPath) { $candidates += Join-Path $installPath 'python.exe' }
                }
            }
        }
    }
    $candidates += Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
    foreach ($name in @('python.exe', 'python3.exe')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notlike '*\Microsoft\WindowsApps\*') { $candidates += $cmd.Source }
    }
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (!(Test-Path -LiteralPath $candidate)) { continue }
        $pythonw = Join-Path (Split-Path $candidate) 'pythonw.exe'
        if (!(Test-Path -LiteralPath $pythonw)) { continue }
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo.FileName = $candidate
        $process.StartInfo.Arguments = '-c "import sys; assert sys.version_info >= (3, 8); import tkinter as tk; r=tk.Tk(); r.withdraw(); r.destroy()"'
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.CreateNoWindow = $true
        $process.StartInfo.RedirectStandardOutput = $true
        $process.StartInfo.RedirectStandardError = $true
        try {
            [void]$process.Start()
            if (!$process.WaitForExit(15000)) { $process.Kill(); continue }
            if ($process.ExitCode -eq 0) { return $pythonw }
        } catch { continue } finally { $process.Dispose() }
    }
    return $null
}

try {
    $pythonw = Find-Python
    if (!$pythonw) {
        $answer = [System.Windows.Forms.MessageBox]::Show(
            'Python 3 with working Tkinter was not found. Download and install official Python 3.14.7 with Tkinter for your user account? Internet access is required.',
            'Install Python?', 'YesNo', 'Question')
        if ($answer -ne [System.Windows.Forms.DialogResult]::Yes) { exit }
        $arch = $env:PROCESSOR_ARCHITEW6432
        if (!$arch) { $arch = $env:PROCESSOR_ARCHITECTURE }
        switch ($arch.ToUpperInvariant()) {
            'ARM64' {
                $filename = 'python-3.14.7-arm64.exe'
                $expected = '9a3fe120cc81bc2cb099550f794d8356811f96a86c7f438519243c3485db928d'
            }
            'AMD64' {
                $filename = 'python-3.14.7-amd64.exe'
                $expected = '9d9eb2709ef81bf5cd30db3c2096bdbc4ea10087c22e62f27d356b36f6ae9649'
            }
            'X86' {
                $filename = 'python-3.14.7.exe'
                $expected = '097fc03d4ac2de66ee1d73a0c5d2d323b5c0f14923f7207686ce93149a80f0a6'
            }
            default { throw "Unsupported Windows architecture: $arch" }
        }
        $setupFolder = Join-Path ([IO.Path]::GetTempPath()) ('EpisodeRenamer-' + [guid]::NewGuid())
        [void](New-Item -ItemType Directory -Path $setupFolder)
        try {
            $installer = Join-Path $setupFolder $filename
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $progress = New-Object System.Windows.Forms.Form
            $progress.Text = 'Episode Renamer setup'
            $progress.Width = 420
            $progress.Height = 140
            $progress.StartPosition = 'CenterScreen'
            $label = New-Object System.Windows.Forms.Label
            $label.Text = 'Downloading Python from python.org. Please wait...'
            $label.AutoSize = $true
            $label.Left = 18
            $label.Top = 25
            $progress.Controls.Add($label)
            $progress.Show()
            $client = New-Object Net.WebClient
            try {
                $task = $client.DownloadFileTaskAsync([Uri]("https://www.python.org/ftp/python/3.14.7/" + $filename), $installer)
                while (!$task.IsCompleted) {
                    [System.Windows.Forms.Application]::DoEvents()
                    if ($progress.IsDisposed) { $client.CancelAsync(); throw 'Download cancelled.' }
                    Start-Sleep -Milliseconds 100
                }
                $task.GetAwaiter().GetResult()
            } finally { $client.Dispose(); $progress.Close(); $progress.Dispose() }
            if ((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash -ne $expected) {
                throw 'Installer checksum did not match. Installation was not started.'
            }
            $signature = Get-AuthenticodeSignature -LiteralPath $installer
            if ($signature.Status -ne 'Valid') { throw 'Installer signature validation failed.' }
            $install = Start-Process -FilePath $installer -ArgumentList '/passive InstallAllUsers=0 Include_tcltk=1 Include_launcher=0 Include_test=0 PrependPath=0' -Wait -PassThru
            if ($install.ExitCode -notin @(0, 3010)) { throw "Python installation failed or was cancelled (code $($install.ExitCode))." }
        } finally { Remove-Item -LiteralPath $setupFolder -Recurse -Force -ErrorAction SilentlyContinue }
        $pythonw = Find-Python
        if (!$pythonw) { throw 'Python was installed, but working Tkinter could not be found. Try running the installer again and selecting Modify to enable Tcl/Tk.' }
    }
    $script = Join-Path $PSScriptRoot 'rename_gui.py'
    $log = Join-Path ([IO.Path]::GetTempPath()) 'episode-renamer-windows.log'
    $run = Start-Process -FilePath $pythonw -ArgumentList ('"' + $script + '"') -RedirectStandardError $log -Wait -PassThru
    if ($run.ExitCode -ne 0) { throw "The renamer could not start. Details are in: $log" }
} catch { Show-Error $_.Exception.Message; exit 1 }
