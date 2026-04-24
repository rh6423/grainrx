### Plan Overview

1.  **Directory Structure**: Create a folder `ComfyUI-GrainRX` inside your `ComfyUI/custom_nodes/` directory.
2.  **Dependency Management**: Copy the `film_grain` package into the plugin directory so it works standalone without global installation.
3.  **Node Implementation (`nodes.py`)**: Create a Python class that inherits from ComfyUI's node structure, defining inputs (Image, Profile, Parameters) and outputs (Grainy Image).
4.  **Registration (`__init__.py`)**: Register the node so ComfyUI can find it.
5.  **Dependencies (`requirements.txt`)**: List `numpy`, `Pillow`, and `numba`.

### Step 1: Directory Structure

You will need to create the following structure:

```text
ComfyUI/custom_nodes/ComfyUI-GrainRX/
├── __init__.py
├── nodes.py
├── requirements.txt
└── film_grain/          # (Copy your existing film_grain folder here)
    ├── __init__.py
    ├── renderer.py
    ├── renderer_fast.py
    └── ...
```

### Step 2: Node Implementation (`nodes.py`)

This file defines the node. It handles converting ComfyUI's tensor format `[Batch, Height, Width, Channels]` (float32, 0-1 range) into NumPy arrays for GrainRX, and then converts the result back.

```python
# nodes.py
import torch
import numpy as np
from PIL import Image
from .film_grain import (
    render_grayscale_fast, 
    render_color_fast, 
    get_profile,
    warmup_jit
)

class GrainRXNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "profile": (["tri-x", "hp5", "tmax100", "delta3200", "panf", 
                              "portra400", "ektar100", "superia400", "ultramax400"],),
                "renderer": (["fast", "mc"],),
                "mu_r": ("FLOAT", {"default": 0.07, "min": 0.01, "max": 0.2, "step": 0.001}),
                "sigma_r": ("FLOAT", {"default": 0.03, "min": 0.0, "max": 0.1, "step": 0.001}),
                "filter_sigma": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 2.0, "step": 0.1}),
                "mc_samples": ("INT", {"default": 100, "min": 10, "max": 500, "step": 10}),
                "zoom": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 4.0, "step": 0.1}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 0xffffffffffffffff}),
                "bw_mode": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "image/effects/film"

    def process(self, image, profile, renderer, mu_r, sigma_r, filter_sigma, 
                mc_samples, zoom, seed, bw_mode):
        
        # Warmup JIT once (handled by import usually, but safe to ensure)
        if renderer == "mc":
            warmup_jit()

        # Convert ComfyUI Tensor [B, H, W, C] -> NumPy [H, W, C] uint8
        # ComfyUI uses float32 0-1, we need uint8 0-255 for GrainRX
        img_np = (image[0].cpu().numpy() * 255.0).astype(np.uint8)

        profile_obj = get_profile(profile)
        
        # Select renderer and parameters
        if bw_mode:
            # Convert to grayscale manually if needed, or let GrainRX handle it?
            # README suggests passing gray image to render_grayscale_fast
            gray = np.dot(img_np[..., :3], [0.2126, 0.7152, 0.0722]).astype(np.uint8)
            
            if renderer == "fast":
                result = render_grayscale_fast(
                    gray, mu_r, sigma_r, 
                    filter_sigma=filter_sigma, 
                    zoom=zoom, seed=seed
                )
            else:
                # MC mode for B&W
                # Note: You might need to expose mc_samples in the fast renderer or handle it here
                result = render_grayscale(
                    gray, mu_r, sigma_r, 
                    n_mc=mc_samples, zoom=zoom, seed=seed
                )
        else:
            if renderer == "fast":
                result = render_color_fast(
                    img_np, 
                    profile_obj.channel_mu_r, 
                    profile_obj.channel_sigma_r,
                    filter_sigma=filter_sigma,
                    zoom=zoom, seed=seed
                )
            else:
                result = render_color(
                    img_np, 
                    profile_obj.channel_mu_r, 
                    profile_obj.channel_sigma_r,
                    n_mc=mc_samples, zoom=zoom, seed=seed
                )

        # Convert result back to ComfyUI Tensor [B, H, W, C] float32 0-1
        # GrainRX likely returns uint8 or float 0-255. Assuming uint8 based on typical PIL usage.
        if result.dtype != np.uint8:
            result = (result / 255.0).astype(np.float32)
        else:
            result = result.astype(np.float32) / 255.0
            
        # Add batch dimension back
        output_tensor = torch.from_numpy(result)[None, ...]
        
        return (output_tensor,)

# Map the node to ComfyUI
NODE_CLASS_MAPPINGS = {
    "GrainRX": GrainRXNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrainRX": "GrainRX Film Grain"
}
```

### Step 3: Registration (`__init__.py`)

This file tells ComfyUI where to find the nodes.

```python
# __init__.py
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
```

### Step 4: Dependencies (`requirements.txt`)

```text
numpy
Pillow
numba
```
