#!/usr/bin/env python3
"""Autonomous free I2V distillery — Wan2 → LTX → PIL+ffmpeg self-healing."""
import os
import sys
import time
import subprocess
from enum import Enum
from pathlib import Path

class PipelineOntology(Enum):
    WAN2_PRIMARY = "Wan-AI/Wan2.1-1.3B-I2V"
    LTX_SECONDARY = "Lightricks/LTX-Video"
    PIL_CONTINGENCY = "LOCAL_PIL_FFMPEG_FALLBACK"

class SelfHealingOrchestrator:
    def __init__(self, input_image: str, prompt: str, output_dir: str = None):
        self.input_image = Path(input_image).resolve()
        self.prompt = prompt
        default_out = Path.home() / "workspace" / "output"
        self.output_dir = Path(output_dir) if output_dir else default_out
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "tmp_frames").mkdir(parents=True, exist_ok=True)
        self.target_output = self.output_dir / "rendered_motion.mp4"
        self.state = PipelineOntology.WAN2_PRIMARY
        self.engine_used = None
        self.log_path = self.output_dir / "pipeline.log"

    def log_state(self, msg: str, level: str = "INFO"):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{level}] [{self.state.name}]: {msg}"
        print(line, flush=True)
        try:
            with open(self.log_path, "a") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def _extract_result_path(self, result):
        """Gradio clients return str, tuple, or nested paths."""
        if result is None:
            return None
        if isinstance(result, (str, Path)) and Path(result).exists():
            return str(result)
        if isinstance(result, (list, tuple)):
            for item in result:
                p = self._extract_result_path(item)
                if p:
                    return p
        if isinstance(result, dict):
            for v in result.values():
                p = self._extract_result_path(v)
                if p:
                    return p
        return None

    def execute_wan2_primary(self) -> bool:
        self.log_state("Initiating Wan2.1 I2V Generation...")
        try:
            from gradio_client import Client, handle_file
            client = Client("Wan-AI/Wan2.1-1.3B-I2V")
            # Try common API names
            for api in ("/generate", "/predict", None):
                try:
                    kwargs = dict(
                        input_image=handle_file(str(self.input_image)),
                        prompt=self.prompt,
                    )
                    if api:
                        result = client.predict(**kwargs, api_name=api)
                    else:
                        result = client.predict(**kwargs)
                    path = self._extract_result_path(result)
                    if path:
                        os.replace(path, self.target_output)
                        self.engine_used = "WAN2_PRIMARY"
                        return True
                except TypeError:
                    # different signature — try minimal
                    try:
                        result = client.predict(handle_file(str(self.input_image)), self.prompt, api_name=api or "/predict")
                        path = self._extract_result_path(result)
                        if path:
                            os.replace(path, self.target_output)
                            self.engine_used = "WAN2_PRIMARY"
                            return True
                    except Exception as e2:
                        self.log_state(f"Wan2 api try failed: {e2}", level="WARN")
                except Exception as e:
                    self.log_state(f"Wan2 attempt ({api}): {e}", level="WARN")
        except Exception as e:
            self.log_state(f"Primary Wan2 execution failed: {e}", level="WARN")
        return False

    def execute_ltx_secondary(self) -> bool:
        self.log_state("Transitioning to Secondary Engine: LTX-Video...")
        try:
            from gradio_client import Client, handle_file
            client = Client("Lightricks/LTX-Video")
            for api in ("/predict", "/generate", None):
                try:
                    kwargs = dict(
                        input_image=handle_file(str(self.input_image)),
                        prompt=self.prompt,
                    )
                    if api:
                        result = client.predict(**kwargs, api_name=api)
                    else:
                        result = client.predict(**kwargs)
                    path = self._extract_result_path(result)
                    if path:
                        os.replace(path, self.target_output)
                        self.engine_used = "LTX_SECONDARY"
                        return True
                except Exception as e:
                    self.log_state(f"LTX attempt ({api}): {e}", level="WARN")
        except Exception as e:
            self.log_state(f"Secondary LTX execution failed: {e}", level="WARN")
        return False

    def execute_pil_contingency(self) -> bool:
        self.log_state("Deploying Final Fallback: PIL Motion Engine...", level="WARN")
        try:
            from PIL import Image, ImageEnhance, ImageDraw, ImageFont

            img = Image.open(self.input_image).convert("RGB")
            width, height = img.size
            # max 1280 edge for speed
            max_edge = 1280
            if max(width, height) > max_edge:
                scale = max_edge / max(width, height)
                width, height = int(width * scale), int(height * scale)
            width, height = width - (width % 2), height - (height % 2)
            if width < 2 or height < 2:
                width, height = 1280, 720
            img = img.resize((width, height), Image.Resampling.LANCZOS)

            frames_dir = self.output_dir / "tmp_frames"
            frames_dir.mkdir(exist_ok=True)
            for f in frames_dir.glob("*.png"):
                f.unlink()

            total_frames = 60  # 2s @ 30fps
            for i in range(total_frames):
                zoom = 1.0 + (i * 0.003)
                crop_w = max(2, int(width / zoom) - (int(width / zoom) % 2))
                crop_h = max(2, int(height / zoom) - (int(height / zoom) % 2))
                left = max(0, (width - crop_w) // 2)
                top = max(0, (height - crop_h) // 2)
                frame = img.crop((left, top, left + crop_w, top + crop_h)).resize((width, height), Image.Resampling.LANCZOS)
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(1.0 + (0.08 * (i / total_frames)))
                # subtle pan
                if i % 2 == 0:
                    frame = frame.transform(frame.size, Image.AFFINE, (1, 0, i * 0.15, 0, 1, 0), fillcolor=(0, 0, 0))
                draw = ImageDraw.Draw(frame)
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                except Exception:
                    font = ImageFont.load_default()
                draw.text((16, height - 36), "I2V FREE · PIL+FFmpeg contingency", fill=(200, 210, 220), font=font)
                frame.save(frames_dir / f"frame_{i:04d}.png")

            ffmpeg_cmd = [
                "ffmpeg", "-y", "-framerate", "30",
                "-i", str(frames_dir / "frame_%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
                str(self.target_output),
            ]
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            for f in frames_dir.glob("*.png"):
                f.unlink()
            try:
                frames_dir.rmdir()
            except OSError:
                pass
            self.engine_used = "PIL_CONTINGENCY"
            return self.target_output.exists() and self.target_output.stat().st_size > 0
        except Exception as e:
            self.log_state(f"Contingency Engine Critical Failure: {e}", level="ERROR")
            return False

    def trigger_instant_sync(self):
        uploader_script = Path.home() / ".local/bin/auto_uploader.sh"
        if uploader_script.exists():
            self.log_state("Triggering instant sync hook to Drive and GitHub...")
            subprocess.run(["bash", str(uploader_script)], check=False)
        else:
            self.log_state("Uploader hook missing — skip sync", level="WARN")

    def run_autonomous_loop(self):
        self.log_state("Autonomous State Machine initialized.")
        self.log_state(f"Input: {self.input_image} exists={self.input_image.exists()}")
        while self.state is not None:
            if self.state == PipelineOntology.WAN2_PRIMARY:
                if self.execute_wan2_primary():
                    self.log_state(f"SUCCESS: Render exported to {self.target_output}")
                    self.trigger_instant_sync()
                    return 0
                self.state = PipelineOntology.LTX_SECONDARY

            elif self.state == PipelineOntology.LTX_SECONDARY:
                if self.execute_ltx_secondary():
                    self.log_state(f"SUCCESS: Render exported via Secondary Engine to {self.target_output}")
                    self.trigger_instant_sync()
                    return 0
                self.state = PipelineOntology.PIL_CONTINGENCY

            elif self.state == PipelineOntology.PIL_CONTINGENCY:
                if self.execute_pil_contingency():
                    self.log_state(f"SUCCESS: Contingency Render compiled at {self.target_output}")
                    self.trigger_instant_sync()
                    return 0
                self.log_state("ALL ONTOLOGICAL PATHWAYS EXHAUSTED.", level="CRITICAL")
                return 1
        return 1

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "workspace" / "input_frame.png")
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Cinematic realistic motion, dynamic light shift, 4k continuous movement"
    out = sys.argv[3] if len(sys.argv) > 3 else str(Path.home() / "workspace" / "output")
    engine = SelfHealingOrchestrator(input_image=img, prompt=prompt, output_dir=out)
    code = engine.run_autonomous_loop()
    sys.exit(code)
