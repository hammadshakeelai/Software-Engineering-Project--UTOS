"""Assemble the enriched UTOS ad (~30s, 11 beats): 8 Veo cinematic shots + real UI
+ captions, Veo watermark cropped, cross-dissolved. Silent pass; music added after."""
import os, subprocess

FF = r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
G = os.path.join(ROOT, "generated")
C = os.path.join(ROOT, "clips")
SEG = os.path.join(C, "seg")
EXP = os.path.join(ROOT, "exports")
for d in (SEG, EXP):
    os.makedirs(d, exist_ok=True)


def run(args, label=""):
    r = subprocess.run([FF, "-hide_banner", "-y"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR", label, "\n", r.stderr[-1800:]); raise SystemExit(1)
    print("ok", label)


def veo_seg(src, start, dur, text, out):
    """Veo clip -> 1080p30, scale+crop ~5% to drop the corner watermark, caption w/ fade."""
    ins = ["-ss", str(start), "-t", str(dur), "-i", src]
    base = "[0:v]scale=2016:1134:flags=lanczos,crop=1920:1080,fps=30,setpts=PTS-STARTPTS"
    if text:
        ins += ["-loop", "1", "-t", str(dur), "-i", text]
        fc = (base + "[bg];"
              f"[1:v]format=rgba,fade=in:st=0.3:d=0.4:alpha=1,fade=out:st={dur-0.55:.2f}:d=0.35:alpha=1[tx];"
              "[bg][tx]overlay=0:0,format=yuv420p[v]")
        run(ins + ["-filter_complex", fc, "-map", "[v]", "-an", "-r", "30",
                   "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], os.path.basename(out))
    else:
        run(ins + ["-vf", base + ",format=yuv420p", "-an", "-r", "30",
                   "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], os.path.basename(out))


def ui_seg(src, dur, text, out):
    ins = ["-t", str(dur), "-i", src]
    if text:
        ins += ["-loop", "1", "-t", str(dur), "-i", text]
        fc = ("[0:v]fps=30,setpts=PTS-STARTPTS[bg];"
              f"[1:v]format=rgba,fade=in:st=0.2:d=0.4:alpha=1,fade=out:st={dur-0.5:.2f}:d=0.3:alpha=1[tx];"
              "[bg][tx]overlay=0:0,format=yuv420p[v]")
        run(ins + ["-filter_complex", fc, "-map", "[v]", "-an", "-r", "30",
                   "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], os.path.basename(out))
    else:
        run(ins + ["-vf", "fps=30,setpts=PTS-STARTPTS,format=yuv420p", "-an", "-r", "30",
                   "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], os.path.basename(out))


def concat(parts, out):
    lst = out + ".txt"
    with open(lst, "w") as f:
        for p in parts:
            f.write("file '%s'\n" % p.replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", "30", out], os.path.basename(out))


def g(n): return os.path.join(G, n)
def c(n): return os.path.join(C, n)
def s(n): return os.path.join(SEG, n)

# ---- top-level segments (name, duration) ----
veo_seg(g("shot4_campus.mp4"),       0.5, 2.4, None,            s("a_campus.mp4"))
veo_seg(g("shot1_chaos_desk.mp4"),   0.6, 2.6, c("text_s1.png"), s("b_chaos.mp4"))
veo_seg(g("shot5_admin.mp4"),        0.8, 2.4, c("text_admin.png"), s("c_admin.mp4"))
veo_seg(g("shot2_red_collision.mp4"),1.0, 2.6, c("text_s2.png"), s("d_collision.mp4"))

ui_seg(c("ui_login.mp4"),     1.0, None,            s("e1.mp4"))
ui_seg(c("ui_timetable.mp4"), 3.0, c("text_s3.png"), s("e2.mp4"))
concat([s("e1.mp4"), s("e2.mp4")], s("e_reveal.mp4"))

veo_seg(g("shot6_solver.mp4"), 0.8, 2.3, c("text_solver.png"), s("f_solver.mp4"))

ui_seg(c("ui_dashboard.mp4"), 1.9, c("text_s4a.png"), s("g1.mp4"))
ui_seg(c("ui_versions.mp4"),  1.8, c("text_s4b.png"), s("g2.mp4"))
ui_seg(c("ui_reports.mp4"),   1.3, None,             s("g3.mp4"))
concat([s("g1.mp4"), s("g2.mp4"), s("g3.mp4")], s("g_workflow.mp4"))

ui_seg(c("ui_teacher.mp4"), 1.5, c("text_s5.png"), s("h1.mp4"))
ui_seg(c("ui_student.mp4"), 1.4, None,            s("h2.mp4"))
ui_seg(c("ui_facility.mp4"),1.3, None,            s("h3.mp4"))
concat([s("h1.mp4"), s("h2.mp4"), s("h3.mp4")], s("h_roles.mp4"))

veo_seg(g("shot7_hall.mp4"),       0.8, 2.4, c("text_hall.png"), s("i_hall.mp4"))
veo_seg(g("shot8_hero.mp4"),       0.5, 2.3, None,             s("j_hero.mp4"))
veo_seg(g("shot3_brand_hero.mp4"), 1.0, 3.5, c("text_close.png"), s("k_close.mp4"))

segs = [("a_campus.mp4",2.4),("b_chaos.mp4",2.6),("c_admin.mp4",2.4),("d_collision.mp4",2.6),
        ("e_reveal.mp4",4.0),("f_solver.mp4",2.3),("g_workflow.mp4",5.0),("h_roles.mp4",4.2),
        ("i_hall.mp4",2.4),("j_hero.mp4",2.3),("k_close.mp4",3.5)]

# ---- cross-dissolve chain ----
T = 0.35
ins, parts = [], []
for n, _ in segs:
    ins += ["-i", s(n)]
acc = segs[0][1]
prev = "[0:v]"
for k in range(1, len(segs)):
    off = acc - T
    out = "[v%d]" % k
    parts.append(f"{prev}[{k}:v]xfade=transition=fade:duration={T}:offset={off:.2f}{out}")
    acc = acc + segs[k][1] - T
    prev = out
total = acc
parts.append(f"{prev}fade=in:st=0:d=0.5,fade=out:st={total-0.6:.2f}:d=0.6,format=yuv420p[vf]")
master = os.path.join(EXP, "UTOS_ad_16x9_silent.mp4")
run(ins + ["-filter_complex", ";".join(parts), "-map", "[vf]", "-r", "30",
           "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", master], "MASTER")
print("TOTAL %.2fs ->" % total, master)
