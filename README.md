# Graniac

Physics-based film grain synthesis using the inhomogeneous Boolean model.

Unlike overlay-based tools that layer noise on top of an image, this renderer
**reconstructs the image from simulated grain** — the output pixel values
emerge from the statistical density of modeled silver halide crystals, filtered
through a Gaussian kernel representing the optical enlargement process and
human vision. This is the same fundamental approach described by Nik Silver
Efex's marketing ("recreates the image using the grain settings") but
implemented from the academic foundation.

## How It Works

### The Physics

A photographic film emulsion consists of silver halide crystals suspended in
gelatin. When photons hit a crystal, it becomes developable and turns into
an opaque metallic silver particle. The final image is a binary function:
opaque where grains developed, transparent where they didn't. Continuous tone
is the *statistical density* of these grains, observed through an optical
system that averages over many grains per perceived pixel.

### The Boolean Model

We model grain as an **inhomogeneous Boolean model** (Newson et al., IPOL 2017):

1. **Poisson process**: Grain centers are scattered across the image plane
   with density λ(x,y) that varies per pixel to match the input gray level.
   Bright areas get more grains (higher λ), dark areas get fewer.

2. **Grain disks**: Each grain is a disk with radius drawn from a log-normal
   distribution (matching real crystal size distributions). The ratio σ_r/μ_r
   controls "clumping" — a key visual signature of specific film stocks.

3. **Monte Carlo filtering**: The binary model is convolved with a Gaussian
   kernel via Monte Carlo integration. For each output pixel, N random points
   are sampled from the Gaussian, each tested against the Boolean model, and
   the results averaged. This produces continuous-tone output with authentic
   grain texture.

### Why This Looks Different From Noise Overlays

- **Grain IS the image**: The output emerges from grain density, not
  `image + noise`. Grain interacts with edges and textures naturally.
- **Physically correct tonal response**: Grain variance follows p(1-p),
  peaking in the midtones — matching real film's behavior.
- **Organic clumping**: Log-normal radius distributions produce the irregular
  grain clusters that distinguish real film from digital noise.
- **Per-channel independence**: Color grain applies the model independently
  to each emulsion layer with different parameters (blue layer = largest
  grains), producing authentic chromatic grain variation.
- **Resolution independence**: The model is defined in continuous space.
  The zoom parameter renders grain at any resolution, even down to
  individual grain scale.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ with NumPy, Numba, Pillow, and SciPy.

## Two Renderers

This project includes **two rendering engines** for different use cases:

### Fast Analytical Renderer (`--fast`)
Derives the mean, variance, and spatial correlation of the Boolean model
analytically, then synthesizes grain as signal-dependent filtered Gaussian
noise. **~100-500x faster** than Monte Carlo. Use for:
- Iterating on parameters and profiles
- Batch processing large images
- Real-time preview workflows
- Any image where individual grains don't need to be resolved (normal case)

### Monte Carlo Boolean Model (default)
Directly simulates the physical Boolean model grain-by-grain using Monte
Carlo integration. Slower but produces maximum realism with authentic
non-Gaussian grain statistics (organic clumping, binary grain character).
Use for:
- Final reference-quality output
- Extreme zoom where individual grains should be visible
- Very coarse grain (Delta 3200) where clumping character matters most
- Validating the fast renderer's output

## Quick Start

```bash
# FAST: B&W with Kodak Tri-X grain (~0.1s for 1024x1024)
python render.py photo.jpg -o grainy.jpg --profile tri-x --bw --fast

# FAST: Color Portra 400 (~0.5s for 1024x1024)
python render.py photo.jpg -o grainy.jpg --profile portra400 --fast

# MC: Maximum quality B&W (30-60s for 1024x1024)
python render.py photo.jpg -o hq.png --profile tri-x --bw --mc 200

# MC: Quick preview (fewer samples)
python render.py photo.jpg -o preview.jpg --profile hp5 --bw --mc 30

# Custom parameters
python render.py photo.jpg -o custom.jpg --mu-r 0.06 --sigma-r 0.02 --fast

# List all film profiles
python render.py --list-profiles
```

## Parameters

### Grain Geometry

| Parameter | Flag | Default | Description |
|-----------|------|---------|-------------|
| Mean radius | `--mu-r` | Profile-dependent | Average grain radius in input pixel units. Larger = coarser grain. Typical range: 0.02 (Pan F) to 0.12 (Delta 3200). |
| Radius std dev | `--sigma-r` | Profile-dependent | Standard deviation of grain radius. Controls clumping. 0 = all grains identical (modern T-grain look). Higher = more organic, irregular clumping (classic look). |
| Filter sigma | `--filter-sigma` | 0.8 | Gaussian filter width in output pixels. Models the optical system. Lower = sharper individual grains. Higher = smoother, blended look. |

### Rendering Quality

| Parameter | Flag | Default | Description |
|-----------|------|---------|-------------|
| MC samples | `--mc` | 100 | Monte Carlo samples per pixel. More = smoother output but slower. 30 = quick preview, 100 = good quality, 200+ = reference quality. |
| Zoom | `--zoom` | 1.0 | Output resolution multiplier. 2.0 = double resolution (can see finer grain detail). |
| Seed | `--seed` | 42 | Random seed. Same seed = same grain pattern (reproducible). |

### Modes & Post-Processing

| Flag | Description |
|------|-------------|
| `--fast` | Use fast analytical renderer (~100-500x faster than MC) |
| `--bw` | Convert to grayscale before applying grain |
| `--hd-curve` | Apply film characteristic curve (S-curve) to input |
| `--visibility` | Apply perceptual visibility modulation (reduces grain in deep shadows and bright highlights) |
| `--max-dim N` | Resize longest edge to N pixels before rendering (for fast previews) |

## Film Profiles

Run `python render.py --list-profiles` for the full list. Highlights:

**B&W stocks:**
- `tri-x` — Kodak Tri-X 400: iconic photojournalism grain, pronounced clumping
- `hp5` — Ilford HP5 Plus 400: classic British character
- `tmax100` — Kodak T-Max 100: ultra-fine tabular grain
- `delta3200` — Ilford Delta 3200: extreme grain, heavy clumping
- `panf` — Ilford Pan F Plus 50: nearly grainless

**Color stocks:**
- `portra400` — Kodak Portra 400: fine grain, warm, per-channel variation
- `ektar100` — Kodak Ektar 100: world's finest grain color negative
- `superia400` — Fuji Superia 400: punchy consumer film grain
- `ultramax400` — Kodak Ultramax 400: characterful budget grain

## Python API

```python
import numpy as np
from PIL import Image
from film_grain import (
    render_grayscale, render_color, warmup_jit,       # MC renderer
    render_grayscale_fast, render_color_fast,           # Fast renderer
    get_profile,
    apply_visibility_modulation,
)

img = np.array(Image.open("photo.jpg"))
profile = get_profile("tri-x")

# --- Fast analytical renderer (recommended for most uses) ---
gray = np.dot(img[..., :3], [0.2126, 0.7152, 0.0722]).astype(np.uint8)
result = render_grayscale_fast(gray, profile.mu_r, profile.sigma_r, seed=42)

# Fast color grain
result = render_color_fast(img, profile.channel_mu_r, profile.channel_sigma_r)

# --- Monte Carlo renderer (maximum quality) ---
warmup_jit()  # JIT compile once
result = render_grayscale(gray, profile.mu_r, profile.sigma_r, n_mc=100)

# Color MC render with per-channel grain
result = render_color(img, profile.channel_mu_r, profile.channel_sigma_r)
```

## Performance

The first run of the MC renderer includes Numba JIT compilation (~5-15 seconds).
The fast renderer has no warmup penalty.

### Fast Analytical Renderer (`--fast`)

| Image Size | Channels | Time |
|-----------|----------|------|
| 512×512 | 1 (B&W) | ~0.04-0.08s |
| 1024×1024 | 1 (B&W) | ~0.1-0.2s |
| 1024×1024 | 3 (color) | ~0.3-0.5s |
| 2048×2048 | 3 (color) | ~1-2s |
| 4096×4096 | 3 (color) | ~4-8s |

### Monte Carlo Renderer (default)

Approximate times (8-core CPU, --mc 100, zoom 1.0):

| Image Size | Grain (mu_r) | Time |
|-----------|--------------|------|
| 512×512 | 0.07 (Tri-X) | ~5-15s |
| 1024×1024 | 0.07 (Tri-X) | ~20-60s |
| 2048×2048 | 0.07 (Tri-X) | ~2-5 min |
| 1024×1024 | 0.03 (T-Max 100) | ~30-90s |

Fine grain (small mu_r) is slower in MC mode because there are more cells.
Use `--fast` for iteration and `--mc 200` for final reference output.

## Algorithm Details

### Monte Carlo Renderer

Implements the **pixel-wise** variant of the Boolean model algorithm.
For each output pixel:

1. Draw N Gaussian offset vectors ξ_k ~ N(0, σ²I₂)
2. For each offset, map to input coordinates: (x,y) = (pixel + ξ_k) / zoom
3. Check if (x,y) is covered by any grain disk in the Boolean model:
   - Determine which cells are within r_max of (x,y)
   - For each cell, reproducibly generate grains using a hash of the cell
     coordinates as an RNG seed
   - Test point-in-disk for each grain (early exit on first hit)
4. Output = count of "covered" samples / N

The cell-based reproducible RNG is key: it allows any cell's grains to be
regenerated on demand without storing them, making the algorithm memory-efficient.

### Fast Analytical Renderer

Derives the filtered Boolean model's statistics in closed form, then
synthesizes matching noise:

1. **Grain kernel**: Compute h(x) = Gaussian(σ_filter) ⊛ E_r[disk(r)],
   the convolution of the average grain disk with the optical filter.
   For variable radii, the disk is averaged over the log-normal distribution.

2. **Variance LUT**: For each gray level u, compute the analytical variance:
   ```
   Var[v; u] = (1-u)² × ∫ φ₂(Δ) × [exp(λ(u) × A_int(|Δ|/s)) − 1] dΔ
   ```
   where φ₂ is the Gaussian autocorrelation, A_int is the disk intersection
   area, and λ(u) = −log(1−u) / E[πr²].

3. **Synthesis**: Generate white noise, filter with h (via FFT), scale
   per-pixel by √Var[v; u(pixel)]:
   ```
   output(p) = u(p) + σ(u(p)) × (h ⊛ W)(p) / std(h ⊛ W)
   ```

This separates the problem into spatial correlation (the kernel, independent
of gray level) and amplitude (the variance LUT, signal-dependent). The key
approximation is that the autocovariance *shape* is approximately constant
across gray levels — only its amplitude varies. This holds well when the
filter is wider than the grains, which is the normal photographic case.

## References

- Newson, Faraj, Delon, Galerne. "Realistic Film Grain Rendering."
  *Image Processing On Line*, 7 (2017), pp. 165–183.
  https://doi.org/10.5201/ipol.2017.192

- Newson, Delon, Galerne. "A Stochastic Film Grain Model for
  Resolution-Independent Rendering." *Computer Graphics Forum*, 2017.

- Zhang, Wang, Tian, Pappas. "Film Grain Rendering and Parameter Estimation."
  *ACM Trans. Graph.* 42(4), SIGGRAPH 2023.
  (Analytical speedup of the Boolean model — future optimization target.)

- Lesné, Newson. "Neural Film Grain Rendering."
  *Computer Graphics Forum*, 2025.

- Steve Yedlin, ASC. "On Film Grain Emulation."
  https://www.yedlin.net/NerdyFilmTechStuff/OnFilmGrainEmulation.html

## License

MIT
