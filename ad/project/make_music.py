"""Generate a cinematic atmospheric music bed (stdlib wave synth), timed to the cut:
dark A-minor for the problem (0-9s) -> bright C lift + riser/impact at the 'Meet UTOS'
turn (~9s) -> warm F resolve + shimmer at the close (~23s+)."""
import wave, struct, math, os

SR = 44100
DUR = 30.6
N = int(SR * DUR)
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
os.makedirs(OUT, exist_ok=True)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return smooth((t - a) / (b - a)) if b > a else (1.0 if t >= b else 0.0)


def seg(t, a, b, c, d):
    return ramp(t, a, b) * (1 - ramp(t, c, d))


Am = [110.0, 130.81, 164.81, 220.0]    # A minor (dark)
Cm = [130.81, 164.81, 196.0, 261.63]   # C major (lift)
Fm = [174.61, 220.0, 261.63, 349.23]   # F major (warm close)
TWO_PI = 2 * math.pi

frames = bytearray()
for i in range(N):
    t = i / SR
    gA = seg(t, 0.0, 2.0, 8.6, 10.2)
    gC = seg(t, 8.9, 10.4, 22.5, 24.2)
    gF = seg(t, 22.8, 24.2, 29.6, 30.6)
    pad = 0.0
    for f in Am:
        pad += gA * (math.sin(TWO_PI * f * t) + 0.6 * math.sin(TWO_PI * f * 1.003 * t + 1.7))
    for f in Cm:
        pad += gC * (math.sin(TWO_PI * f * t) + 0.6 * math.sin(TWO_PI * f * 1.003 * t + 1.1))
    for f in Fm:
        pad += gF * (math.sin(TWO_PI * f * t) + 0.6 * math.sin(TWO_PI * f * 1.003 * t + 0.5))
    pad /= 6.4
    pad *= 0.85 + 0.15 * math.sin(TWO_PI * 0.12 * t)            # slow shimmer LFO
    subf = 55.0 * gA + 65.41 * gC + 87.31 * gF                 # sub drone follows the root
    sub = 0.55 * math.sin(TWO_PI * subf * t) * (0.7 + 0.3 * math.sin(TWO_PI * 0.5 * t)) if subf > 1 else 0.0
    extra = 0.0
    if 7.2 < t < 9.05:                                          # riser into the reveal
        k = (t - 7.2) / 1.85
        extra += 0.33 * k * k * math.sin(TWO_PI * (180 + 700 * k) * t)
    if 9.0 <= t < 9.7:                                          # soft impact at the turn
        b = (t - 9.0) / 0.7
        extra += 0.8 * math.exp(-5 * b) * math.sin(TWO_PI * 58 * t)
    gsh = seg(t, 24.0, 25.6, 29.6, 30.6)                        # high shimmer at close
    sh = gsh * 0.13 * math.sin(TWO_PI * 523.25 * t) * (0.6 + 0.4 * math.sin(TWO_PI * 0.3 * t))
    s = pad * 0.55 + sub * 0.5 + extra * 0.5 + sh
    s *= ramp(t, 0.0, 1.3) * (1 - ramp(t, 29.4, 30.6))         # master fade in/out
    s *= 0.6
    s = max(-1.0, min(1.0, s))
    v = int(s * 29000)
    frames += struct.pack("<hh", v, v)

with wave.open(os.path.join(OUT, "bed.wav"), "w") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(bytes(frames))
print("bed.wav %.1fs" % DUR)
