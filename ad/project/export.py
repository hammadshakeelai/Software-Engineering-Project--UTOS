"""Final exports: mux music into 16:9, and reframe to 9:16 + 1:1 (centered on a
blurred, darkened fill of the same footage)."""
import os, subprocess

FF = r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXP = os.path.join(ROOT, "exports")
SILENT = os.path.join(EXP, "UTOS_ad_16x9_silent.mp4")
BED = os.path.join(ROOT, "audio", "bed.wav")


def run(args, label):
    r = subprocess.run([FF, "-hide_banner", "-y"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR", label, "\n", r.stderr[-1600:]); raise SystemExit(1)
    print("ok", label)


# 16:9 with music
out169 = os.path.join(EXP, "UTOS_ad_16x9.mp4")
run(["-i", SILENT, "-i", BED,
     "-filter_complex", "[1:a]afade=in:st=0:d=1.2,afade=out:st=29.0:d=1.2[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out169], "16x9+music")

# 9:16
out916 = os.path.join(EXP, "UTOS_ad_9x16.mp4")
fc = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=42:2,eq=brightness=-0.20[bg];"
      "[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]")
run(["-i", out169, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
     "-c:v", "libx264", "-crf", "20", "-c:a", "copy", out916], "9x16")

# 1:1
out11 = os.path.join(EXP, "UTOS_ad_1x1.mp4")
fc1 = ("[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,boxblur=42:2,eq=brightness=-0.20[bg];"
       "[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]")
run(["-i", out169, "-filter_complex", fc1, "-map", "[v]", "-map", "0:a",
     "-c:v", "libx264", "-crf", "20", "-c:a", "copy", out11], "1x1")

for f in (out169, out916, out11):
    print(" ->", f, os.path.getsize(f) // 1024, "KB")
