## Python API

The public API lives in the `core` package:

```python
import numpy as np
from PIL import Image
from core import (
    render_grayscale, render_color, warmup_jit,       # MC renderer
    render_grayscale_fast, render_color_fast,         # Fast renderer
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

### CLI

Two equivalent entry points:

```bash
# Direct script invocation (works from a clone, no install needed)
python render.py photo.jpg -o grainy.jpg --profile tri-x --bw --fast

# Installed console script (after `pip install .`)
grainrx photo.jpg -o grainy.jpg --profile tri-x --bw --fast
```
