#!/usr/bin/env python3
"""
GrainRX CLI - Command-line interface for physics-based film grain rendering.

This module provides the entry point for the `grainrx` command when installed as a package.

Usage examples:

  # B&W Tri-X look
  grainrx photo.jpg -o grainy.jpg --profile tri-x --bw

  # Color Portra 400
  grainrx photo.jpg -o grainy.jpg --profile portra400

  # FAST analytical renderer (~100-500x faster, great for iteration)
  grainrx photo.jpg -o grainy.jpg --profile tri-x --bw --fast

  # Custom parameters, high quality (Monte Carlo)
  grainrx photo.jpg -o grainy.jpg --mu-r 0.06 --sigma-r 0.02 --mc 200

  # Quick preview (fewer MC samples)
  grainrx photo.jpg -o preview.jpg --profile hp5 --bw --mc 30

  # Fast color grain on a large image
  grainrx photo.jpg -o grain.jpg --profile portra400 --fast

  # List available film profiles
  grainrx --list-profiles
"""

import argparse
import sys
import time
import numpy as np
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

from . import (
    render_grayscale, render_color, warmup_jit,
    render_grayscale_fast, render_color_fast,
    get_profile, list_profiles,
    apply_characteristic_curve,
    apply_visibility_modulation,
)


def load_image(path):
    """Load an image as a numpy array."""
    img = Image.open(path)
    if img.mode == 'RGBA':
        # Drop alpha
        img = img.convert('RGB')
    elif img.mode == 'L':
        pass  # already grayscale
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    return np.array(img)


def save_image(array, path):
    """Save a numpy array as an image."""
    img = Image.fromarray(array)
    # Determine format from extension
    ext = Path(path).suffix.lower()
    if ext in ('.jpg', '.jpeg'):
        img.save(path, quality=95)
    elif ext == '.png':
        img.save(path)
    elif ext == '.tiff' or ext == '.tif':
        img.save(path)
    else:
        img.save(path)
    print(f"Saved: {path}")


def rgb_to_gray(rgb):
    """Convert RGB to luminance (Rec. 709 weights)."""
    return (0.2126 * rgb[:, :, 0] +
            0.7152 * rgb[:, :, 1] +
            0.0722 * rgb[:, :, 2]).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(
        description="GrainRX: Physics-based film grain rendering using the Boolean model.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('input', nargs='?', help='Input image path')
    parser.add_argument('-o', '--output', default='output_grain.png',
                        help='Output image path (default: output_grain.png)')

    # Film profile
    parser.add_argument('--profile', '-p', default=None,
                        help='Film stock profile name (e.g., tri-x, portra400)')
    parser.add_argument('--list-profiles', action='store_true',
                        help='List all available film profiles and exit')

    # Custom grain parameters (override profile)
    parser.add_argument('--mu-r', type=float, default=None,
                        help='Mean grain radius in input pixels (e.g., 0.05)')
    parser.add_argument('--sigma-r', type=float, default=None,
                        help='Grain radius std dev (e.g., 0.01). 0 = constant.')
    parser.add_argument('--filter-sigma', type=float, default=None,
                        help='Gaussian filter sigma in output pixels (default: 0.8)')

    # Rendering options
    parser.add_argument('--mc', type=int, default=100,
                        help='Monte Carlo samples per pixel (default: 100)')
    parser.add_argument('--zoom', type=float, default=1.0,
                        help='Output zoom factor (default: 1.0)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')

    # Mode
    parser.add_argument('--bw', action='store_true',
                        help='Convert to B&W before applying grain')
    parser.add_argument('--fast', action='store_true',
                        help='Use fast analytical renderer (~100-500x faster). '
                             'Excellent for fine-to-moderate grain. Use MC '
                             'renderer (default) for extreme zoom or very '
                             'coarse grain where individual grains must be visible.')

    # Post-processing
    parser.add_argument('--hd-curve', action='store_true',
                        help='Apply characteristic curve (H&D) to input')
    parser.add_argument('--visibility', action='store_true',
                        help='Apply perceptual visibility modulation')

    # Resize for speed
    parser.add_argument('--max-dim', type=int, default=None,
                        help='Resize longest edge to this before rendering '
                             '(for faster previews)')

    args = parser.parse_args()

    if args.list_profiles:
        list_profiles()
        return

    if args.input is None:
        parser.error("Input image path is required (unless using --list-profiles)")

    # ---- Load image ----
    print(f"Loading {args.input}...")
    image = load_image(args.input)
    print(f"  Image: {image.shape[1]}x{image.shape[0]}, {image.dtype}")

    # ---- Optional resize ----
    if args.max_dim is not None:
        h, w = image.shape[:2]
        longest = max(h, w)
        if longest > args.max_dim:
            scale = args.max_dim / longest
            new_h = int(h * scale)
            new_w = int(w * scale)
            pil_img = Image.fromarray(image)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
            image = np.array(pil_img)
            print(f"  Resized to: {new_w}x{new_h}")

    # ---- Determine parameters ----
    profile = None
    if args.profile:
        try:
            profile = get_profile(args.profile)
            print(f"  Profile: {profile.name}")
            print(f"  {profile.description}")
        except KeyError as e:
            print(f"Error: {e}")
            return

    # Determine grain parameters
    if args.mu_r is not None:
        mu_r = args.mu_r
        sigma_r = args.sigma_r if args.sigma_r is not None else 0.0
        filter_sigma = args.filter_sigma or 0.8
        is_color_grain = False
        channel_mu_r = [mu_r, mu_r, mu_r]
        channel_sigma_r = [sigma_r, sigma_r, sigma_r]
    elif profile is not None:
        mu_r = profile.mu_r
        sigma_r = profile.sigma_r
        filter_sigma = args.filter_sigma or profile.filter_sigma
        is_color_grain = profile.color
        channel_mu_r = profile.channel_mu_r
        channel_sigma_r = profile.channel_sigma_r
    else:
        # Default: moderate grain
        print("  No profile or custom params specified, using defaults (Tri-X style)")
        mu_r = 0.07
        sigma_r = 0.025
        filter_sigma = 0.8
        is_color_grain = False
        channel_mu_r = [mu_r, mu_r, mu_r]
        channel_sigma_r = [sigma_r, sigma_r, sigma_r]

    if args.filter_sigma is not None:
        filter_sigma = args.filter_sigma

    use_fast = args.fast

    # ---- JIT warmup (only needed for MC renderer) ----
    if not use_fast:
        print("\nCompiling (first run only)...")
        t0 = time.time()
        warmup_jit()
        print(f"  JIT compiled in {time.time() - t0:.1f}s\n")
    else:
        print(f"\nUsing fast analytical renderer\n")

    # ---- Convert to B&W if requested ----
    is_grayscale = (image.ndim == 2)
    if args.bw and not is_grayscale:
        print("Converting to B&W...")
        image = rgb_to_gray(image)
        is_grayscale = True

    # ---- Apply characteristic curve ----
    if args.hd_curve:
        print("Applying characteristic curve...")
        if is_grayscale:
            img_f = image.astype(np.float64) / 255.0
            img_f = apply_characteristic_curve(img_f)
            image = np.clip(img_f * 255, 0, 255).astype(np.uint8)
        else:
            img_f = image.astype(np.float64) / 255.0
            for ch in range(3):
                img_f[:, :, ch] = apply_characteristic_curve(img_f[:, :, ch])
            image = np.clip(img_f * 255, 0, 255).astype(np.uint8)

    # ---- Render grain ----
    renderer_name = "analytical" if use_fast else "Monte Carlo"
    print(f"Rendering film grain ({renderer_name})...")
    t_start = time.time()

    original_norm = image.astype(np.float64) / 255.0

    if use_fast:
        # --- Fast analytical renderer ---
        if is_grayscale:
            result = render_grayscale_fast(
                image, mu_r, sigma_r, filter_sigma,
                zoom=args.zoom, seed=args.seed
            )
        else:
            if is_color_grain:
                result = render_color_fast(
                    image, channel_mu_r, channel_sigma_r, filter_sigma,
                    zoom=args.zoom, seed=args.seed
                )
            else:
                result = render_color_fast(
                    image,
                    [mu_r, mu_r, mu_r],
                    [sigma_r, sigma_r, sigma_r],
                    filter_sigma,
                    zoom=args.zoom, seed=args.seed
                )
    else:
        # --- Monte Carlo Boolean model renderer ---
        if is_grayscale:
            result = render_grayscale(
                image, mu_r, sigma_r, filter_sigma,
                n_mc=args.mc, zoom=args.zoom, seed=args.seed
            )
        elif args.bw:
            result = render_grayscale(
                image, mu_r, sigma_r, filter_sigma,
                n_mc=args.mc, zoom=args.zoom, seed=args.seed
            )
        else:
            if is_color_grain:
                result = render_color(
                    image, channel_mu_r, channel_sigma_r, filter_sigma,
                    n_mc=args.mc, zoom=args.zoom, seed=args.seed
                )
            else:
                result = render_color(
                    image,
                    [mu_r, mu_r, mu_r],
                    [sigma_r, sigma_r, sigma_r],
                    filter_sigma,
                    n_mc=args.mc, zoom=args.zoom, seed=args.seed
                )

    total = time.time() - t_start
    print(f"\nTotal render time: {total:.1f}s")

    # ---- Apply visibility modulation ----
    if args.visibility:
        print("Applying perceptual visibility modulation...")
        result_f = result.astype(np.float64) / 255.0
        
        # If zoom was applied, resize original_norm to match output dimensions
        if args.zoom != 1.0:
            orig_pil = Image.fromarray((original_norm * 255).astype(np.uint8))
            new_h, new_w = result_f.shape[:2]
            orig_pil = orig_pil.resize((new_w, new_h), Image.BILINEAR)
            original_norm_resized = np.array(orig_pil).astype(np.float64) / 255.0
        else:
            original_norm_resized = original_norm
        
        if result_f.ndim == 2:
            result_f = apply_visibility_modulation(result_f, original_norm_resized)
        else:
            for ch in range(3):
                result_f[:, :, ch] = apply_visibility_modulation(
                    result_f[:, :, ch], original_norm_resized[:, :, ch]
                )
        result = np.clip(result_f * 255, 0, 255).astype(np.uint8)

    # ---- Save ----
    save_image(result, args.output)


if __name__ == '__main__':
    main()