param(
  [Parameter(Mandatory=$true)][string]$Out,
  [int]$CropTop = 160,    # strip browser chrome (tabs+address+bookmarks)
  [int]$CropLeft = 8,
  [int]$CropRight = 8,
  [int]$CropBottom = 8
)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class CapW {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$u = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*UTOS*' } | Select-Object -First 1
if (-not $u) { Write-Output "ERROR: no UTOS window"; exit 1 }
$h = $u.MainWindowHandle
[CapW]::ShowWindow($h, 3) | Out-Null        # SW_MAXIMIZE
[CapW]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 600
$r = New-Object CapW+RECT; [CapW]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $hg = $r.Bottom - $r.Top
$full = New-Object System.Drawing.Bitmap $w, $hg
$g = [System.Drawing.Graphics]::FromImage($full)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size($w, $hg)))
$cw = $w - $CropLeft - $CropRight
$ch = $hg - $CropTop - $CropBottom
$rect = New-Object System.Drawing.Rectangle $CropLeft, $CropTop, $cw, $ch
$crop = $full.Clone($rect, $full.PixelFormat)
$crop.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $full.Dispose(); $crop.Dispose()
Write-Output "SAVED $Out  ${cw}x${ch}"
