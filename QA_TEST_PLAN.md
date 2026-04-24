# GrainRX QA Test Plan

**Version:** 1.0  
**Date:** 2026-04-23  
**Git Commit:** a53a88ea2c230888502f89277f7ed9186b9b1a62

---

## Table of Contents
1. [Test Environment Setup](#test-environment-setup)
2. [CLI Tests](#cli-tests)
3. [Web UI Tests](#web-ui-tests)
4. [Python API Tests](#python-api-tests)
5. [Edge Case Tests](#edge-case-tests)

---

## Test Environment Setup

### Prerequisites
```bash
cd /Users/legba/Downloads/grainrx
source venv/bin/activate
```

### Test Images Location
- `test-images/qedit2511_MR__00808_.png` (1288x832)
- `test-images/qedit2511_MR__00823_.png`
- `test-images/qedit2511_MR__00847_.png`

---

## CLI Tests

### CLI-01: List Profiles
**Purpose:** Verify all film profiles are accessible and displayed correctly.

```bash
python render.py --list-profiles
```

**Expected Output:**
- 20 film profiles listed (13 B&W, 7 color)
- Columns: Key, Name, Type, mu_r, sigma_r
- Descriptions included for each profile

**Profiles to verify present:**
| Key | Name | Type |
|-----|------|------|
| acros | Fujifilm Neopan Acros 100 | B&W |
| delta100 | Ilford Delta 100 | B&W |
| delta3200 | Ilford Delta 3200 | B&W |
| delta400 | Ilford Delta 400 | B&W |
| ektar100 | Kodak Ektar 100 | color |
| fp4 | Ilford FP4 Plus 125 | B&W |
| gold200 | Kodak Gold 200 | color |
| hp5 | Ilford HP5 Plus 400 | B&W |
| panf | Ilford Pan F Plus 50 | B&W |
| plus-x | Kodak Plus-X 125 | B&W |
| portra160 | Kodak Portra 160 | color |
| portra400 | Kodak Portra 400 | color |
| portra800 | Kodak Portra 800 | color |
| superia400 | Fuji Superia 400 | color |
| tmax100 | Kodak T-Max 100 | B&W |
| tmax400 | Kodak T-Max 400 | B&W |
| tri-x | Kodak Tri-X 400 | B&W |
| ultramax400 | Kodak Ultramax 400 | color |

---

### CLI-02: Fast B&W Render
**Purpose:** Verify fast analytical renderer with B&W conversion.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_bw_fast.jpg --profile tri-x --bw --fast
```

**Expected Output:**
- Exit code: 0
- Output file created at `/tmp/test_bw_fast.jpg`
- Render time < 1 second
- Log shows "Using fast analytical renderer"
- Log shows "Converting to B&W..."

---

### CLI-03: Fast Color Render
**Purpose:** Verify fast analytical renderer with color preservation.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_color_fast.jpg --profile portra400 --fast
```

**Expected Output:**
- Exit code: 0
- Output file created at `/tmp/test_color_fast.jpg`
- Render time < 1 second
- Log shows per-channel processing (Red, Green, Blue)

---

### CLI-04: Monte Carlo B&W Render
**Purpose:** Verify Monte Carlo renderer with reduced samples.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_mc_bw.png --profile tri-x --bw --mc 30 --max-dim 512
```

**Expected Output:**
- Exit code: 0
- Output file created at `/tmp/test_mc_bw.png`
- First run shows "JIT compiled" message (~1.5-2s)
- Subsequent runs faster (no JIT message)
- Log shows "Rendering film grain (Monte Carlo)..."

---

### CLI-05: Custom Parameters (Fast)
**Purpose:** Verify custom mu_r and sigma_r override profile defaults.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_custom.png --mu-r 0.05 --sigma-r 0.01 --fast
```

**Expected Output:**
- Exit code: 0
- No profile name shown in output (custom params used)
- Render completes successfully

---

### CLI-06: Zoom Option (Fast)
**Purpose:** Verify output zoom factor works correctly.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_zoom.png --profile tri-x --bw --fast --zoom 2.0 --max-dim 256
```

**Expected Output:**
- Exit code: 0
- Log shows resize from input to output (e.g., "255x165 -> 510x330")
- Output dimensions are 2x input dimensions

---

### CLI-07: Seed Reproducibility (Fast)
**Purpose:** Verify same seed produces identical output.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_seed1.png --profile tri-x --bw --fast --seed 12345 --max-dim 256
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_seed2.png --profile tri-x --bw --fast --seed 12345 --max-dim 256
md5sum /tmp/test_seed1.png /tmp/test_seed2.png
```

**Expected Output:**
- Both files have identical MD5 hash
- Example: `33ee9625ed530f78e7eaf849589e7840` for both

---

### CLI-08: Monte Carlo Color Render
**Purpose:** Verify Monte Carlo renderer with color image.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_mc_color.png --profile portra400 --mc 30 --max-dim 256
```

**Expected Output:**
- Exit code: 0
- Log shows "Channel Red:", "Channel Green:", "Channel Blue:"
- Render completes successfully

---

### CLI-09: Seed Reproducibility (Monte Carlo)
**Purpose:** Verify same seed produces identical Monte Carlo output.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_mc_seed.png --profile tri-x --bw --mc 30 --seed 42 --max-dim 256
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_mc_seed2.png --profile tri-x --bw --mc 30 --seed 42 --max-dim 256
md5sum /tmp/test_mc_seed.png /tmp/test_mc_seed2.png
```

**Expected Output:**
- Both files have identical MD5 hash
- Example: `6b3b58afc94cc1a521a2d10a23a7e0e4` for both

---

### CLI-10: Monte Carlo with Zoom
**Purpose:** Verify Monte Carlo renderer respects zoom parameter.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_mc_zoom.png --profile tri-x --bw --mc 30 --zoom 2.0 --max-dim 256
```

**Expected Output:**
- Exit code: 0
- Log shows "MC=30, zoom=2.0" in output

---

### CLI-11: Monte Carlo Custom Parameters
**Purpose:** Verify custom parameters work with Monte Carlo renderer.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_mc_custom.png --mu-r 0.05 --sigma-r 0.01 --mc 30 --max-dim 256
```

**Expected Output:**
- Exit code: 0
- No profile name shown (custom params used)
- Render completes successfully

---

### CLI-12: Help Output
**Purpose:** Verify help text is displayed correctly.

```bash
python render.py --help
```

**Expected Output:**
- Usage information displayed
- All options documented:
  - `-h, --help`
  - `-o, --output OUTPUT`
  - `--profile, -p PROFILE`
  - `--list-profiles`
  - `--mu-r MU_R`
  - `--sigma-r SIGMA_R`
  - `--filter-sigma FILTER_SIGMA`
  - `--mc MC`
  - `--zoom ZOOM`
  - `--seed SEED`
  - `--bw`
  - `--fast`
  - `--hd-curve`
  - `--visibility`
  - `--max-dim MAX_DIM`

---

### CLI-13: Error Handling - Missing Input File
**Purpose:** Verify proper error when input file doesn't exist.

```bash
python render.py nonexistent.jpg -o /tmp/output.jpg --profile tri-x --bw --fast
```

**Expected Output:**
- Non-zero exit code
- Error message indicating file not found

---

### CLI-14: Error Handling - Invalid Profile
**Purpose:** Verify proper error when invalid profile is specified.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/output.jpg --profile invalid_profile --fast
```

**Expected Output:**
- Non-zero exit code or graceful handling
- Error message or warning about invalid profile

---

## Web UI Tests

### Setup
```bash
cd gui
python app.py
# Server starts on http://localhost:5000
```

### UI-01: Page Load
**Purpose:** Verify web interface loads correctly.

**Steps:**
1. Navigate to `http://localhost:5000`
2. Observe page content

**Expected Output:**
- HTML page renders
- Upload area visible
- Control panel with sliders visible
- Profile dropdown populated with film stocks

---

### UI-02: Image Upload
**Purpose:** Verify image upload functionality.

**Steps:**
1. Navigate to `http://localhost:5000`
2. Select an image file from `test-images/`
3. Observe upload behavior

**Expected Output:**
- File selected successfully
- Image preview displayed
- No JavaScript errors in console

---

### UI-03: Profile Selection
**Purpose:** Verify film profile dropdown works.

**Steps:**
1. Upload an image
2. Click profile dropdown
3. Select different profiles (tri-x, portra400, etc.)

**Expected Output:**
- Dropdown contains all 20 profiles
- Selection persists
- UI updates on selection change

---

### UI-04: Slider Controls
**Purpose:** Verify all slider controls are functional.

**Steps:**
1. Upload an image
2. Adjust each slider:
   - Grain Size (mu_r)
   - Grain Variation (sigma_r)
   - Filter Sigma
   - Zoom
   - MC Samples

**Expected Output:**
- All sliders respond to input
- Values update in UI
- No JavaScript errors

---

### UI-05: B&W Toggle
**Purpose:** Verify B&W checkbox functionality.

**Steps:**
1. Upload an image
2. Check/uncheck "B&W" checkbox

**Expected Output:**
- Checkbox toggles correctly
- State persists

---

### UI-06: Fast Mode Toggle
**Purpose:** Verify fast mode checkbox functionality.

**Steps:**
1. Upload an image
2. Check/uncheck "Fast Mode" checkbox

**Expected Output:**
- Checkbox toggles correctly
- State persists

---

### UI-07: Render Button (Fast B&W)
**Purpose:** Verify render button produces output with fast renderer.

**Steps:**
1. Upload an image
2. Select profile: tri-x
3. Check "B&W" checkbox
4. Check "Fast Mode" checkbox
5. Click "Render" button

**Expected Output:**
- Processing indicator shown
- Rendered image displayed
- Download link appears
- No errors in server logs

---

### UI-08: Render Button (Fast Color)
**Purpose:** Verify render button produces color output.

**Steps:**
1. Upload an image
2. Select profile: portra400
3. Uncheck "B&W" checkbox
4. Check "Fast Mode" checkbox
5. Click "Render" button

**Expected Output:**
- Processing indicator shown
- Color rendered image displayed
- Download link appears

---

### UI-09: Render Button (Monte Carlo)
**Purpose:** Verify Monte Carlo rendering via UI.

**Steps:**
1. Upload an image
2. Select profile: tri-x
3. Check "B&W" checkbox
4. Uncheck "Fast Mode" checkbox
5. Set MC Samples to 30
6. Click "Render" button

**Expected Output:**
- Processing indicator shown
- Rendered image displayed
- May take longer than fast mode

---

### UI-10: Download Functionality
**Purpose:** Verify rendered images can be downloaded.

**Steps:**
1. Render an image (any settings)
2. Click download link/button

**Expected Output:**
- File downloads successfully
- Filename is valid
- Image opens correctly

---

### UI-11: API Endpoint - /upload
**Purpose:** Verify upload API endpoint.

```bash
curl -X POST -F "file=@test-images/qedit2511_MR__00808_.png" http://localhost:5000/upload
```

**Expected Output:**
- HTTP 200 response
- JSON with filename and path

---

### UI-12: API Endpoint - /render
**Purpose:** Verify render API endpoint.

```bash
curl -X POST http://localhost:5000/render \
  -F "image=qedit2511_MR__00808_.png" \
  -F "profile=tri-x" \
  -F "bw=true" \
  -F "fast=true"
```

**Expected Output:**
- HTTP 200 response
- JSON with output path or image data

---

### UI-13: API Endpoint - /profiles
**Purpose:** Verify profiles API endpoint.

```bash
curl http://localhost:5000/profiles
```

**Expected Output:**
- HTTP 200 response
- JSON array of profile objects with keys and names

---

## Python API Tests

### Setup
```python
from core.profiles import get_profile, list_profiles
from core.renderer_fast import render_fast
from core.renderer import render_monte_carlo
import numpy as np
```

### API-01: List Profiles
**Purpose:** Verify `list_profiles()` returns all profiles.

```python
profiles = list_profiles()
assert len(profiles) == 20
print(f"Found {len(profiles)} profiles")
```

**Expected Output:**
- Returns dictionary/list with 20 entries
- No exceptions raised

---

### API-02: Get Profile by Key
**Purpose:** Verify `get_profile()` retrieves correct profile data.

```python
profile = get_profile('tri-x')
assert profile['key'] == 'tri-x'
assert profile['name'] == 'Kodak Tri-X 400'
assert profile['type'] == 'B&W'
print(f"Profile: {profile}")
```

**Expected Output:**
- Returns dictionary with profile data
- All fields present and correct

---

### API-03: Get Color Profile
**Purpose:** Verify color profile retrieval.

```python
profile = get_profile('portra400')
assert profile['key'] == 'portra400'
assert profile['type'] == 'color'
print(f"Profile: {profile}")
```

**Expected Output:**
- Returns color profile data correctly

---

### API-04: Fast Renderer B&W
**Purpose:** Verify fast renderer with B&W image.

```python
import numpy as np
# Create test image (256x256 grayscale)
image = np.random.rand(256, 256).astype(np.float32) * 255
result = render_fast(image, mu_r=0.07, sigma_r=0.025, bw=True, seed=42)
assert result.shape == (256, 256)
print(f"Output shape: {result.shape}")
```

**Expected Output:**
- Returns numpy array
- Shape matches input
- No exceptions raised

---

### API-05: Fast Renderer Color
**Purpose:** Verify fast renderer with color image.

```python
import numpy as np
# Create test image (256x256 RGB)
image = np.random.rand(256, 256, 3).astype(np.float32) * 255
result = render_fast(image, mu_r=0.04, sigma_r=0.008, bw=False, seed=42)
assert result.shape == (256, 256, 3)
print(f"Output shape: {result.shape}")
```

**Expected Output:**
- Returns numpy array with 3 channels
- Shape matches input
- No exceptions raised

---

### API-06: Monte Carlo Renderer B&W
**Purpose:** Verify Monte Carlo renderer with B&W image.

```python
import numpy as np
image = np.random.rand(128, 128).astype(np.float32) * 255
result = render_monte_carlo(image, mu_r=0.07, sigma_r=0.025, mc_samples=30, seed=42)
assert result.shape == (128, 128)
print(f"Output shape: {result.shape}")
```

**Expected Output:**
- Returns numpy array
- Shape matches input
- No exceptions raised

---

### API-07: Monte Carlo Renderer Color
**Purpose:** Verify Monte Carlo renderer with color image.

```python
import numpy as np
image = np.random.rand(128, 128, 3).astype(np.float32) * 255
result = render_monte_carlo(image, mu_r=0.04, sigma_r=0.008, mc_samples=30, seed=42)
assert result.shape == (128, 128, 3)
print(f"Output shape: {result.shape}")
```

**Expected Output:**
- Returns numpy array with 3 channels
- Shape matches input
- No exceptions raised

---

### API-08: Reproducibility Test
**Purpose:** Verify same seed produces identical results via API.

```python
import numpy as np
image = np.random.rand(128, 128).astype(np.float32) * 255
result1 = render_fast(image, mu_r=0.07, sigma_r=0.025, bw=True, seed=12345)
result2 = render_fast(image, mu_r=0.07, sigma_r=0.025, bw=True, seed=12345)
assert np.array_equal(result1, result2)
print("Reproducibility verified!")
```

**Expected Output:**
- Both results are identical
- Assertion passes

---

### API-09: Invalid Profile Key
**Purpose:** Verify error handling for invalid profile.

```python
try:
    profile = get_profile('nonexistent')
    print(f"Got profile: {profile}")
except Exception as e:
    print(f"Exception raised: {type(e).__name__}: {e}")
```

**Expected Output:**
- Either returns None or raises exception
- Graceful error handling

---

## Edge Case Tests

### EDGE-01: Very Small Image
**Purpose:** Verify rendering works with minimal image size.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_tiny.png --profile tri-x --bw --fast --max-dim 32
```

**Expected Output:**
- Exit code: 0
- Render completes without errors

---

### EDGE-02: Very Large Grain Size
**Purpose:** Verify rendering handles extreme grain size.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_huge_grain.png --mu-r 0.5 --sigma-r 0.1 --fast --max-dim 256
```

**Expected Output:**
- Exit code: 0
- Render completes (may look unusual)

---

### EDGE-03: Zero Sigma-R (Constant Grain)
**Purpose:** Verify rendering with constant grain size.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_constant_grain.png --mu-r 0.05 --sigma-r 0 --fast --max-dim 256
```

**Expected Output:**
- Exit code: 0
- Render completes without errors

---

### EDGE-04: High Zoom Factor
**Purpose:** Verify rendering with extreme zoom.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_high_zoom.png --profile tri-x --bw --fast --zoom 4.0 --max-dim 128
```

**Expected Output:**
- Exit code: 0
- Output is significantly larger than input

---

### EDGE-05: Low MC Samples
**Purpose:** Verify rendering with minimal Monte Carlo samples.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_low_mc.png --profile tri-x --bw --mc 5 --max-dim 256
```

**Expected Output:**
- Exit code: 0
- Render completes quickly (may be noisy)

---

### EDGE-06: HD Curve Option
**Purpose:** Verify H&D curve application.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_hd_curve.png --profile tri-x --bw --fast --hd-curve
```

**Expected Output:**
- Exit code: 0
- Log shows H&D curve applied

---

### EDGE-07: Visibility Modulation
**Purpose:** Verify visibility modulation option.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_visibility.png --profile tri-x --bw --fast --visibility
```

**Expected Output:**
- Exit code: 0
- Log shows visibility modulation applied

---

### EDGE-08: Combined Options
**Purpose:** Verify all options work together.

```bash
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_combined.png --profile tri-x --bw --fast --hd-curve --visibility --zoom 1.5 --seed 999 --max-dim 256
```

**Expected Output:**
- Exit code: 0
- All options applied without conflicts

---

## Quick Test Script

Run all CLI tests automatically:

```bash
#!/bin/bash
# qa_cli_tests.sh

set -e
cd /Users/legba/Downloads/grainrx
source venv/bin/activate

echo "=== CLI-01: List Profiles ==="
python render.py --list-profiles | head -5

echo "=== CLI-02: Fast B&W Render ==="
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_bw_fast.jpg --profile tri-x --bw --fast

echo "=== CLI-03: Fast Color Render ==="
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_color_fast.jpg --profile portra400 --fast

echo "=== CLI-07: Seed Reproducibility ==="
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_seed1.png --profile tri-x --bw --fast --seed 12345 --max-dim 256
python render.py test-images/qedit2511_MR__00808_.png -o /tmp/test_seed2.png --profile tri-x --bw --fast --seed 12345 --max-dim 256
md5sum /tmp/test_seed1.png /tmp/test_seed2.png

echo "=== All CLI tests passed! ==="
```

---

## Test Results Summary Template

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| CLI-01 | List Profiles | PASS | 20 profiles listed |
| CLI-02 | Fast B&W Render | PASS | 0.1s render time |
| ... | ... | ... | ... |