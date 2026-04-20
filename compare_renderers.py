#!/usr/bin/env python3
"""Compare Monte Carlo vs Fast analytical renderer outputs."""

import numpy as np
from PIL import Image
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from film_grain.renderer import render_grayscale
from film_grain.renderer_fast import render_grayscale_fast

def load_image(path):
    img = Image.open(path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    elif img.mode == 'L':
        pass
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    return np.array(img)

# Load test image
print("Loading testimage.png...")
test_img = load_image('testimage.png')

# Convert to B&W
def rgb_to_gray(rgb):
    return (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]).astype(np.uint8)

gray_img = rgb_to_gray(test_img)
print(f"Image: {gray_img.shape[1]}x{gray_img.shape[0]}")

# Test parameters (Tri-X defaults)
mu_r = 0.07
sigma_r = 0.025
filter_sigma = 0.8

print(f"\nParameters: mu_r={mu_r}, sigma_r={sigma_r}, filter_sigma={filter_sigma}")

# Render with MC renderer
print("\nRendering with Monte Carlo (n_mc=30)...")
mc_result = render_grayscale(gray_img, mu_r, sigma_r, filter_sigma, n_mc=30, seed=42)
mc_stats = {
    'mean': float(np.mean(mc_result)),
    'std': float(np.std(mc_result)),
    'variance': float(np.var(mc_result)),
    'min': float(np.min(mc_result)),
    'max': float(np.max(mc_result))
}
print(f"MC stats: mean={mc_stats['mean']:.1f}, std={mc_stats['std']:.1f}, variance={mc_stats['variance']:.1f}")

# Render with Fast renderer
print("\nRendering with Fast analytical...")
fast_result = render_grayscale_fast(gray_img, mu_r, sigma_r, filter_sigma, seed=42)
fast_stats = {
    'mean': float(np.mean(fast_result)),
    'std': float(np.std(fast_result)),
    'variance': float(np.var(fast_result)),
    'min': float(np.min(fast_result)),
    'max': float(np.max(fast_result))
}
print(f"Fast stats: mean={fast_stats['mean']:.1f}, std={fast_stats['std']:.1f}, variance={fast_stats['variance']:.1f}")

# Compare
print("\n" + "="*60)
print("COMPARISON")
print("="*60)
print(f"Variance ratio (Fast/MC): {fast_stats['variance']/mc_stats['variance']:.2f}x")
print(f"Std dev ratio (Fast/MC): {fast_stats['std']/mc_stats['std']:.2f}x")

# Save difference image
diff = np.abs(fast_result.astype(np.int16) - mc_result.astype(np.int16)).astype(np.uint8)
diff_img = Image.fromarray(diff)
diff_img.save('renderer_difference.png')
print(f"\nDifference image saved: renderer_difference.png")

# Save both outputs
Image.fromarray(mc_result).save('compare_mc.png')
Image.fromarray(fast_result).save('compare_fast.png')
print("Saved: compare_mc.png, compare_fast.png")

if fast_stats['variance'] > mc_stats['variance'] * 1.2:
    print("\n⚠️  WARNING: Fast renderer produces significantly more grain!")
else:
    print("\n✅ Both renderers produce similar grain amounts")
