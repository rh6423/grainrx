#!/usr/bin/env python3
"""
GrainRX UI - FastAPI Backend

A modular web interface for testing and tuning film grain parameters.
Designed to be reusable by other UIs (ComfyUI, Photoshop plugin, etc.).
"""

import io
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from PIL import Image

# Add parent directory to path for film_grain import
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    render_grayscale, render_color,
    render_grayscale_fast, render_color_fast,
    get_profile, warmup_jit
)
from core.profiles import PROFILES

app = FastAPI(title="GrainRX UI", version="1.0.0")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Serve index.html at root
@app.get("/", response_class=None)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


def load_image(image_data: bytes) -> np.ndarray:
    """Load image from bytes, return as numpy array."""
    img = Image.open(io.BytesIO(image_data))
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    elif img.mode != 'RGB' and img.mode != 'L':
        img = img.convert('RGB')
    return np.array(img)


def save_temp_image(array: np.ndarray, ext: str = '.png') -> str:
    """Save image to temp file, return filename."""
    filename = f"{uuid.uuid4().hex}{ext}"
    path = OUTPUT_DIR / filename
    img = Image.fromarray(array)
    img.save(path)
    return filename


@app.get("/api/")
async def api_root():
    return {"message": "GrainRX UI API", "version": "1.0.0"}


@app.get("/profiles")
async def get_film_profiles():
    """Get list of available film profiles."""
    profiles = []
    for name in sorted(PROFILES.keys()):
        p = PROFILES[name]
        profiles.append({
            "name": name,
            "display_name": p.name,
            "description": p.description,
            "mu_r": p.mu_r,
            "sigma_r": p.sigma_r,
            "filter_sigma": getattr(p, 'filter_sigma', 0.8),
            "color": p.color,
            "channel_mu_r": p.channel_mu_r if p.color else None,
        })
    return {"profiles": profiles}


@app.post("/render")
async def render_grain(
    image: UploadFile = File(...),
    profile: str = Form("tri-x"),
    renderer: str = Form("fast"),
    mu_r: float = Form(0.07),
    sigma_r: float = Form(0.025),
    filter_sigma: float = Form(0.8),
    mc_samples: int = Form(100),
    zoom: float = Form(1.0),
    seed: int = Form(42),
    bw_mode: bool = Form(False),
    save_result: bool = Form(False),
):
    """Render film grain on uploaded image."""
    try:
        # Read and load image
        image_data = await image.read()
        original_image = load_image(image_data)
        
        is_grayscale = (original_image.ndim == 2)
        
        # Convert to B&W if requested
        if bw_mode and not is_grayscale:
            rgb_to_gray = lambda img: (
                0.2126 * img[:, :, 0] + 
                0.7152 * img[:, :, 1] + 
                0.0722 * img[:, :, 2]
            ).astype(np.uint8)
            original_image = rgb_to_gray(original_image)
            is_grayscale = True
        
        # Get profile parameters (optional override)
        try:
            profile_obj = get_profile(profile)
            use_profile_params = True
        except KeyError:
            use_profile_params = False
        
        # Determine grain parameters
        if use_profile_params:
            p_mu_r = profile_obj.mu_r
            p_sigma_r = profile_obj.sigma_r
            is_color_grain = profile_obj.color
            channel_mu_r = profile_obj.channel_mu_r if is_color_grain else [mu_r, mu_r, mu_r]
            channel_sigma_r = profile_obj.channel_sigma_r if is_color_grain else [sigma_r, sigma_r, sigma_r]
        else:
            p_mu_r = mu_r
            p_sigma_r = sigma_r
            is_color_grain = False
            channel_mu_r = [mu_r, mu_r, mu_r]
            channel_sigma_r = [sigma_r, sigma_r, sigma_r]
        
        # Use form values if provided, otherwise profile defaults
        final_mu_r = mu_r if mu_r != 0.07 else p_mu_r
        final_sigma_r = sigma_r if sigma_r != 0.025 else p_sigma_r
        
        # Warmup JIT for MC renderer
        if renderer == "mc":
            warmup_jit()
        
        # Render
        start_time = time.time()
        
        if renderer == "fast":
            if is_grayscale:
                result = render_grayscale_fast(
                    original_image, final_mu_r, final_sigma_r,
                    filter_sigma=filter_sigma, zoom=zoom, seed=seed
                )
            else:
                if is_color_grain:
                    result = render_color_fast(
                        original_image, channel_mu_r, channel_sigma_r,
                        filter_sigma=filter_sigma, zoom=zoom, seed=seed
                    )
                else:
                    result = render_color_fast(
                        original_image, [final_mu_r]*3, [final_sigma_r]*3,
                        filter_sigma=filter_sigma, zoom=zoom, seed=seed
                    )
        else:  # MC renderer
            if is_grayscale:
                result = render_grayscale(
                    original_image, final_mu_r, final_sigma_r,
                    filter_sigma=filter_sigma, n_mc=mc_samples, zoom=zoom, seed=seed
                )
            else:
                if is_color_grain:
                    result = render_color(
                        original_image, channel_mu_r, channel_sigma_r,
                        filter_sigma=filter_sigma, n_mc=mc_samples, zoom=zoom, seed=seed
                    )
                else:
                    result = render_color(
                        original_image, [final_mu_r]*3, [final_sigma_r]*3,
                        filter_sigma=filter_sigma, n_mc=mc_samples, zoom=zoom, seed=seed
                    )
        
        render_time = time.time() - start_time
        
        # Save or return temp filename
        if save_result:
            output_filename = f"grainrx_{uuid.uuid4().hex}.png"
            output_path = OUTPUT_DIR / output_filename
            Image.fromarray(result).save(output_path)
            result_url = f"/outputs/{output_filename}"
        else:
            temp_filename = save_temp_image(result)
            result_url = f"/outputs/{temp_filename}"
        
        return {
            "success": True,
            "result_url": result_url,
            "render_time": round(render_time, 2),
            "renderer": renderer,
            "parameters": {
                "profile": profile,
                "mu_r": final_mu_r,
                "sigma_r": final_sigma_r,
                "filter_sigma": filter_sigma,
                "mc_samples": mc_samples if renderer == "mc" else None,
                "zoom": zoom,
                "seed": seed,
                "bw_mode": bw_mode,
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/outputs/{filename}")
async def get_output(filename: str):
    """Retrieve a saved output image."""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "File not found"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)