#!/usr/bin/env python3
"""$0 free local MP4: PIL frames + ffmpeg."""
import argparse, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="renders/free-demo.mp4")
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = out.parent / "_frames"
    frames_dir.mkdir(exist_ok=True)
    for p in frames_dir.glob("*.png"): p.unlink()
    W, H, FPS = 1280, 720, 30
    font_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    font_f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    cards = [
        ("FREE RENDER", "Open-source path - $0 per render", (14,19,26), (91,140,255)),
        ("HyperFrames CLI", "Apache-2.0  HTML to MP4 local", (20,27,36), (61,214,140)),
        ("FFmpeg Local", "Cuts  fades  captions  concat", (10,16,24), (245,165,36)),
        ("Verified LIVE", "Distillery pre-launch PASS", (14,19,26), (232,238,246)),
    ]
    fi = 0
    dur = int(2.0 * FPS)
    for title, sub, bg, fg in cards:
        for t in range(dur):
            fade = 1.0
            if t < 8: fade = t / 8.0
            if t > dur - 8: fade = (dur - 1 - t) / 8.0
            img = Image.new("RGB", (W, H), bg)
            d = ImageDraw.Draw(img)
            bb = d.textbbox((0, 0), title, font=font_l)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            d.text(((W - tw) // 2, H // 2 - th - 16), title, fill=fg, font=font_l)
            bb2 = d.textbbox((0, 0), sub, font=font_s)
            tw2 = bb2[2] - bb2[0]
            d.text(((W - tw2) // 2, H // 2 + 36), sub, fill=(232, 238, 246), font=font_s)
            d.text((40, H - 48), "Video Skills Distillery | FREE RENDER PATH", fill=(139, 156, 179), font=font_f)
            if fade < 1:
                img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.05, fade))
            img.save(frames_dir / f"f{fi:05d}.png")
            fi += 1
    r = subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", str(frames_dir / "f%05d.png"),
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", "-shortest", str(out),
    ], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-1200:])
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,codec_name,codec_type:format=duration,size",
        "-of", "json", str(out),
    ], text=True))
    Path(str(out) + ".probe.json").write_text(json.dumps(probe, indent=2))
    print(json.dumps({"ok": True, "out": str(out), "bytes": out.stat().st_size, "frames": fi, "probe": probe}))

if __name__ == "__main__":
    main()
