import asyncio
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import List, Optional

import edge_tts
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field

VIDEOS_DIR = Path(os.environ.get("VIDEOS_DIR", "/data/videos"))
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")

app = FastAPI(
    title="Tim Konten AI - Free Video Motion Renderer (9:16)",
    description="Mesin render video motion 9:16 (.mp4) + Voiceover Bahasa Indonesia gratis di VPS",
    version="1.0.0",
)

app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")


class SceneItem(BaseModel):
    scene_no: int = 1
    duration: float = 4.0
    text: str = Field(..., description="Teks utama di layar (maks 8 kata)")
    narration: Optional[str] = Field(None, description="Kalimat voiceover untuk scene ini")
    bg_color: str = "#1F4E5F"
    text_color: str = "#FFFFFF"


class RenderRequest(BaseModel):
    id_konten: str = "K-01"
    pilar: str = "Konten Usaha"
    topik: str = ""
    voice: str = "id-ID-GadisNeural"
    voiceover_full: Optional[str] = None
    scenes: List[SceneItem]


def hex_to_rgb(hex_color: str, default=(31, 78, 95)):
    c = (hex_color or "").strip().lstrip("#")
    if len(c) == 6:
        try:
            return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            return default
    return default


def darken_rgb(rgb, factor=0.65):
    return tuple(max(0, min(255, int(v * factor))) for v in rgb)


def lighten_rgb(rgb, factor=1.25):
    return tuple(max(0, min(255, int(v * factor + 25))) for v in rgb)


def load_font(size: int, bold: bool = True):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = (text or "").strip().split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        test_line = f"{current} {word}"
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def create_scene_image(
    output_path: Path,
    scene: SceneItem,
    total_scenes: int,
    pilar: str,
    topik: str,
    subtitle_text: str,
    width: int = 768,
    height: int = 1366,
):
    base_rgb = hex_to_rgb(scene.bg_color)
    dark_rgb = darken_rgb(base_rgb, 0.55)
    accent_rgb = lighten_rgb(base_rgb, 1.2)
    text_rgb = hex_to_rgb(scene.text_color, default=(255, 255, 255))

    img = Image.new("RGB", (width, height), dark_rgb)
    draw = ImageDraw.Draw(img)

    # Vertical gradient background
    for y in range(height):
        ratio = y / float(height)
        r = int(base_rgb[0] * (1 - ratio) + dark_rgb[0] * ratio)
        g = int(base_rgb[1] * (1 - ratio) + dark_rgb[1] * ratio)
        b = int(base_rgb[2] * (1 - ratio) + dark_rgb[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Soft decorative circles
    draw.ellipse([width - 240, -100, width + 140, 280], fill=accent_rgb)
    draw.ellipse([-140, height - 340, 220, height + 20], fill=accent_rgb)

    font_badge = load_font(24, bold=True)
    font_topic = load_font(22, bold=False)
    font_main = load_font(52, bold=True)
    font_sub = load_font(27, bold=False)

    safe_left = 72
    safe_right = width - 72
    safe_width = safe_right - safe_left

    # Top pillar pill badge
    pilar_label = f"  {(pilar or 'KONTEN USAHA').upper()}  •  SCENE {scene.scene_no}/{total_scenes}  "
    badge_bbox = draw.textbbox((0, 0), pilar_label, font=font_badge)
    badge_w = (badge_bbox[2] - badge_bbox[0]) + 28
    badge_h = 50
    badge_x = safe_left
    badge_y = 110
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=25,
        fill=(255, 255, 255),
    )
    draw.text((badge_x + 14, badge_y + 11), pilar_label, font=font_badge, fill=dark_rgb)

    # Topic header if present
    if topik:
        topic_lines = wrap_text(draw, topik, font_topic, safe_width)[:2]
        ty = badge_y + badge_h + 24
        for tline in topic_lines:
            draw.text((safe_left, ty), tline, font=font_topic, fill=(225, 235, 240))
            ty += 30

    # Center card container
    main_lines = wrap_text(draw, scene.text, font_main, safe_width - 64)
    line_height = 68
    total_text_h = len(main_lines) * line_height
    card_top = max(310, (height // 2) - (total_text_h // 2) - 85)
    card_bottom = min(height - 320, card_top + total_text_h + 130)

    draw.rounded_rectangle(
        [safe_left, card_top, safe_right, card_bottom],
        radius=32,
        fill=darken_rgb(dark_rgb, 0.72),
        outline=accent_rgb,
        width=3,
    )

    curr_y = card_top + ((card_bottom - card_top - total_text_h) // 2)
    for line in main_lines:
        lb = draw.textbbox((0, 0), line, font=font_main)
        lw = lb[2] - lb[0]
        lx = safe_left + ((safe_width - lw) // 2)
        draw.text((lx, curr_y), line, font=font_main, fill=text_rgb)
        curr_y += line_height

    # Bottom subtitle box (narration caption)
    if subtitle_text:
        sub_lines = wrap_text(draw, subtitle_text, font_sub, safe_width - 48)[:3]
        sub_h = len(sub_lines) * 36 + 34
        sub_top = height - 255
        draw.rounded_rectangle(
            [safe_left, sub_top, safe_right, sub_top + sub_h],
            radius=20,
            fill=(15, 23, 30),
        )
        sy = sub_top + 16
        for sline in sub_lines:
            sb = draw.textbbox((0, 0), sline, font=font_sub)
            sw = sb[2] - sb[0]
            sx = safe_left + ((safe_width - sw) // 2)
            draw.text((sx, sy), sline, font=font_sub, fill=(255, 243, 176))
            sy += 36

    # Progress bar at the bottom
    bar_y = height - 95
    draw.rounded_rectangle([safe_left, bar_y, safe_right, bar_y + 12], radius=6, fill=darken_rgb(dark_rgb, 0.5))
    prog_w = int(safe_width * (float(scene.scene_no) / float(max(1, total_scenes))))
    draw.rounded_rectangle([safe_left, bar_y, safe_left + prog_w, bar_y + 12], radius=6, fill=(255, 255, 255))

    img.save(str(output_path), format="PNG")


async def synthesize_tts(text: str, voice: str, out_mp3: Path) -> bool:
    clean_text = (text or "").strip()
    if not clean_text:
        return False
    for _ in range(2):
        try:
            communicate = edge_tts.Communicate(clean_text, voice)
            await communicate.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 200:
                return True
        except Exception:
            await asyncio.sleep(0.5)
    return False


def get_audio_duration(audio_path: Path) -> float:
    try:
        res = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return max(1.5, float(res.stdout.strip()))
    except Exception:
        return 4.0


def cleanup_old_videos(max_age_days: int = 7):
    cutoff = time.time() - (max_age_days * 86400)
    for f in VIDEOS_DIR.glob("*.mp4"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except Exception:
            pass


@app.get("/health")
async def health():
    return {"status": "ok", "service": "motion-renderer", "videos_dir": str(VIDEOS_DIR)}


@app.post("/render")
async def render_video(req: RenderRequest, request: Request):
    if not req.scenes:
        raise HTTPException(status_code=400, detail="Daftar scenes tidak boleh kosong")

    cleanup_old_videos()
    tmpdir = Path(tempfile.mkdtemp(prefix="motion_"))

    try:
        total_scenes = len(req.scenes)
        full_sentences = []
        if req.voiceover_full:
            raw_parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", req.voiceover_full.strip()) if s.strip()]
            full_sentences = raw_parts

        segment_files = []
        total_duration = 0.0

        for idx, scene in enumerate(req.scenes):
            narration = (scene.narration or "").strip()
            if not narration:
                if idx < len(full_sentences):
                    narration = full_sentences[idx]
                else:
                    narration = scene.text

            img_path = tmpdir / f"scene_{idx}.png"
            audio_path = tmpdir / f"scene_{idx}.mp3"
            seg_path = tmpdir / f"seg_{idx}.mp4"

            has_tts = await synthesize_tts(narration, req.voice or "id-ID-GadisNeural", audio_path)
            if has_tts:
                dur = round(get_audio_duration(audio_path) + 0.45, 2)
            else:
                dur = max(2.5, float(scene.duration or 4.0))

            total_duration += dur

            create_scene_image(
                output_path=img_path,
                scene=scene,
                total_scenes=total_scenes,
                pilar=req.pilar,
                topik=req.topik,
                subtitle_text=narration,
            )

            fade_out_start = max(0.4, round(dur - 0.35, 2))
            if idx % 2 == 0:
                crop_expr = f"crop=720:1280:'(in_w-out_w)*(t/{dur})':'(in_h-out_h)*(t/{dur})'"
            else:
                crop_expr = f"crop=720:1280:'(in_w-out_w)*(1-t/{dur})':'(in_h-out_h)*(t/{dur})'"

            vf = f"{crop_expr},fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out_start}:d=0.3,format=yuv420p"

            if has_tts:
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-framerate",
                    "24",
                    "-t",
                    str(dur),
                    "-i",
                    str(img_path),
                    "-i",
                    str(audio_path),
                    "-filter_complex",
                    f"[0:v]{vf}[v];[1:a]apad=pad_dur=0.45[a]",
                    "-map",
                    "[v]",
                    "-map",
                    "[a]",
                    "-t",
                    str(dur),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    str(seg_path),
                ]
            else:
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-framerate",
                    "24",
                    "-t",
                    str(dur),
                    "-i",
                    str(img_path),
                    "-f",
                    "lavfi",
                    "-t",
                    str(dur),
                    "-i",
                    "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-vf",
                    vf,
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-shortest",
                    str(seg_path),
                ]

            subprocess.run(cmd, check=True, capture_output=True)
            segment_files.append(seg_path)

        concat_list = tmpdir / "concat.txt"
        concat_list.write_text("\n".join([f"file '{p.name}'" for p in segment_files]), encoding="utf-8")

        safe_id = re.sub(r"[^A-Za-z0-9_-]", "", req.id_konten or "K01")
        filename = f"{safe_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
        final_path = VIDEOS_DIR / filename

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-movflags",
                "+faststart",
                str(final_path),
            ],
            cwd=str(tmpdir),
            check=True,
            capture_output=True,
        )

        base_url = PUBLIC_BASE_URL
        if not base_url:
            forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
            forwarded_host = request.headers.get("x-forwarded-host", request.headers.get("host", "localhost:8000"))
            base_url = f"{forwarded_proto}://{forwarded_host}"

        video_url = f"{base_url}/videos/{filename}"

        return {
            "status": "success",
            "id_konten": req.id_konten,
            "filename": filename,
            "video_url": video_url,
            "duration_sec": round(total_duration, 1),
        }
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
        raise HTTPException(status_code=500, detail=f"FFmpeg render error: {err_msg[-500:]}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
