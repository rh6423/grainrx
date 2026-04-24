# Example Outputs

This directory contains sample outputs demonstrating GrainRX's film grain synthesis capabilities.

## Sample Images

| Image | Description |
|-------|-------------|
| `source_original.jpg` | Original source image (512×330) |
| `sample_trix_bw.jpg` | Kodak Tri-X 400 B&W grain (fast renderer) |
| `sample_portra400_color.jpg` | Kodak Portra 400 color grain (fast renderer) |
| `sample_delta3200_bw.jpg` | Ilford Delta 3200 B&W grain (fast renderer) |

## Fast vs Monte Carlo Comparison

| Image | Description |
|-------|-------------|
| `fast_trix_bw.png` | Tri-X 400 using fast analytical renderer (~0.007s at 256px max dimension) |
| `mc_trix_bw.png` | Tri-X 400 using Monte Carlo renderer, 100 samples (~0.3s) |
| `fast_vs_mc_comparison.png` | Side-by-side comparison of both renderers |

### Renderer Comparison Notes

The fast analytical renderer and Monte Carlo Boolean model produce visually similar results for most use cases:

**Fast Analytical Renderer:**
- ~100-500x faster than Monte Carlo
- Excellent for fine-to-moderate grain (Tri-X, HP5, Portra)
- Ideal for iteration, batch processing, and previews
- Uses signal-dependent filtered Gaussian noise

**Monte Carlo Boolean Model:**
- Maximum realism with authentic non-Gaussian statistics
- Better for extreme zoom where individual grains are visible
- Preserves organic clumping character in very coarse grain (Delta 3200)
- Use for reference-quality final output

### Where the Approximation Breaks Down

The fast renderer's approximation holds well when:
1. The optical filter is wider than individual grains (normal photographic case)
2. Grain density is moderate (not extremely sparse or dense)
3. You're viewing at normal enlargement sizes

The Monte Carlo renderer may be preferable when:
1. Rendering extreme zoom levels where individual grain disks should be visible
2. Using very coarse grain profiles like Delta 3200 where clumping character matters most
3. Needing maximum statistical fidelity for scientific/analytical purposes

## Reproducing These Examples

```bash
# B&W Tri-X 400 (fast)
python render.py source_original.jpg -o sample_trix_bw.jpg --profile tri-x --bw --fast --max-dim 512

# Color Portra 400 (fast)
python render.py source_original.jpg -o sample_portra400_color.jpg --profile portra400 --fast --max-dim 512

# B&W Delta 3200 (fast)
python render.py source_original.jpg -o sample_delta3200_bw.jpg --profile delta3200 --bw --fast --max-dim 512

# Monte Carlo comparison (slower)
python render.py source_original.jpg -o mc_trix_bw.png --profile tri-x --bw --mc 100 --max-dim 256
python render.py source_original.jpg -o fast_trix_bw.png --profile tri-x --bw --fast --max-dim 256