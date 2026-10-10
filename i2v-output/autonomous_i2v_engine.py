#!/usr/bin/env python3
"""Ontological free I2V: multi-space primary → secondary → PIL contingency."""
import os, sys, time, subprocess
from enum import Enum
from pathlib import Path

class PipelineOntology(Enum):
    WAN2_PRIMARY = "preSalesAIAutomation/imagetovideo"  # Wan2.2 Faster Pro ZeroGPU (HTTP 200)
    SVD_ALT = "multimodalart/stable-video-diffusion"     # HTTP 200 classic I2V
    COG_SECONDARY = "THUDM/CogVideoX"                    # HTTP 200
    PIL_CONTINGENCY = "LOCAL_PIL_FFMPEG_FALLBACK"

# Ordered cascade of (space_id, api_names_to_try)
SPACE_CASCADE = [
    ("preSalesAIAutomation/imagetovideo", ["/generate", "/predict", None]),
    ("multimodalart/stable-video-diffusion", ["/predict", "/generate", None]),
    ("THUDM/CogVideoX", ["/predict", "/generate", None]),
    ("Wan-AI/Wan2.1", ["/generate", "/predict", None]),
]

class SelfHealingOrchestrator:
    def __init__(self, input_image: str, prompt: str, output_dir: str = None, skip_remote: bool = False):
        self.input_image = Path(input_image).resolve()
        self.prompt = prompt
        self.output_dir = Path(output_dir) if output_dir else Path.home() / "workspace" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_output = self.output_dir / "rendered_motion.mp4"
        self.skip_remote = skip_remote or os.environ.get("I2V_SKIP_REMOTE") == "1"
        self.engine_used = None
        self.log_path = self.output_dir / "pipeline.log"
        self.state = PipelineOntology.WAN2_PRIMARY

    def log_state(self, msg: str, level: str = "INFO"):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{level}] [{getattr(self.state,'name',self.state)}]: {msg}"
        print(line, flush=True)
        with open(self.log_path, "a") as f:
            f.write(line + "\n")

    def _extract_path(self, result):
        if result is None: return None
        if isinstance(result, (str, Path)) and Path(str(result)).exists():
            return str(result)
        if isinstance(result, (list, tuple)):
            for x in result:
                p = self._extract_path(x)
                if p: return p
        if isinstance(result, dict):
            for v in result.values():
                p = self._extract_path(v)
                if p: return p
        return None

    def execute_remote_space(self, space: str, apis) -> bool:
        self.log_state(f"Remote Space: {space}")
        try:
            from gradio_client import Client, handle_file
            import concurrent.futures
            def connect():
                return Client(space)
            with concurrent.futures.ThreadPoolExecutor(1) as ex:
                client = ex.submit(connect).result(timeout=30)
            for api in apis:
                try:
                    kwargs = {}
                    # multiple signature attempts
                    attempts = [
                        dict(input_image=handle_file(str(self.input_image)), prompt=self.prompt),
                        dict(image=handle_file(str(self.input_image)), prompt=self.prompt),
                        dict(img=handle_file(str(self.input_image)), prompt_text=self.prompt),
                    ]
                    for kw in attempts:
                        try:
                            if api:
                                result = client.predict(**kw, api_name=api)
                            else:
                                result = client.predict(*kw.values())
                            path = self._extract_path(result)
                            if path:
                                os.replace(path, self.target_output)
                                self.engine_used = space
                                return True
                        except TypeError:
                            continue
                        except Exception as e:
                            self.log_state(f"  predict fail api={api}: {type(e).__name__}: {e}", "WARN")
                except Exception as e:
                    self.log_state(f"  api loop: {e}", "WARN")
        except Exception as e:
            self.log_state(f"Space connect fail {space}: {e}", "WARN")
        return False

    def execute_pil_contingency(self) -> bool:
        self.log_state("PIL Motion Contingency (always-free guarantee)", "WARN")
        try:
            from PIL import Image, ImageEnhance, ImageDraw, ImageFont
            img = Image.open(self.input_image).convert("RGB")
            w, h = img.size
            max_e = 1280
            if max(w, h) > max_e:
                s = max_e / max(w, h)
                w, h = int(w * s), int(h * s)
            w, h = w - w % 2, h - h % 2
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            frames = self.output_dir / "tmp_frames"
            frames.mkdir(exist_ok=True)
            for f in frames.glob("*.png"): f.unlink()
            n = 60
            for i in range(n):
                zoom = 1.0 + i * 0.003
                cw = max(2, int(w / zoom) - int(w / zoom) % 2)
                ch = max(2, int(h / zoom) - int(h / zoom) % 2)
                left, top = (w - cw) // 2, (h - ch) // 2
                frame = img.crop((left, top, left + cw, top + ch)).resize((w, h), Image.Resampling.LANCZOS)
                frame = ImageEnhance.Brightness(frame).enhance(1.0 + 0.08 * (i / n))
                d = ImageDraw.Draw(frame)
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                except Exception:
                    font = ImageFont.load_default()
                d.text((12, h - 28), "FREE I2V contingency · PIL+FFmpeg", fill=(200, 210, 220), font=font)
                frame.save(frames / f"frame_{i:04d}.png")
            subprocess.run([
                "ffmpeg", "-y", "-framerate", "30",
                "-i", str(frames / "frame_%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                str(self.target_output)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for f in frames.glob("*.png"): f.unlink()
            try: frames.rmdir()
            except OSError: pass
            self.engine_used = "PIL_CONTINGENCY"
            return self.target_output.exists() and self.target_output.stat().st_size > 0
        except Exception as e:
            self.log_state(f"PIL critical: {e}", "ERROR")
            return False

    def trigger_instant_sync(self):
        up = Path.home() / ".local/bin/auto_uploader.sh"
        if up.exists():
            self.log_state("Trigger sync hook")
            subprocess.run(["bash", str(up)], check=False)

    def run_autonomous_loop(self):
        self.log_state("Autonomous I2V ontology start")
        self.log_state(f"input={self.input_image} exists={self.input_image.exists()}")
        if not self.skip_remote:
            for space, apis in SPACE_CASCADE:
                self.state = space
                if self.execute_remote_space(space, apis):
                    self.log_state(f"SUCCESS remote → {self.target_output}")
                    self.trigger_instant_sync()
                    return 0
        self.state = PipelineOntology.PIL_CONTINGENCY
        if self.execute_pil_contingency():
            self.log_state(f"SUCCESS contingency → {self.target_output}")
            self.trigger_instant_sync()
            return 0
        self.log_state("ALL PATHWAYS EXHAUSTED", "CRITICAL")
        return 1

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "workspace/input_frame.png")
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Cinematic realistic motion, dynamic light shift, continuous movement"
    out = sys.argv[3] if len(sys.argv) > 3 else str(Path.home() / "workspace/output")
    skip = os.environ.get("I2V_SKIP_REMOTE") == "1"
    # default: try remotes briefly; for CI use I2V_SKIP_REMOTE=1
    if "--skip-remote" in sys.argv:
        skip = True
    code = SelfHealingOrchestrator(img, prompt, out, skip_remote=skip).run_autonomous_loop()
    sys.exit(code)
