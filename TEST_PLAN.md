# GrainRX Test Plan

## Executive Summary

This test plan documents the QA activities for GrainRX, a physics-based film grain synthesis application. The application implements the inhomogeneous Boolean model for realistic film grain rendering.

**Status**: Requirements are clear and well-documented, enabling comprehensive test case derivation.

---

## 1. Requirements Analysis

### 1.1 Core Functionality
- ✅ Apply film grain to images using physics-based Boolean model
- ✅ Support both Monte Carlo (MC) and Fast analytical rendering modes
- ✅ Provide multiple film stock profiles (B&W and color)
- ✅ Support grayscale and color image processing
- ✅ Implement post-processing options (characteristic curve, visibility modulation)

### 1.2 Key Parameters
- Grain geometry: mean radius (μ_r), radius std dev (σ_r), filter sigma
- Rendering quality: MC samples, zoom factor, random seed
- Modes: fast analytical vs Monte Carlo, B&W vs color
- Post-processing: characteristic curve, visibility modulation

### 1.3 Output Requirements
- Support multiple image formats (PNG, JPEG, TIFF)
- Maintain image dimensions or apply zoom scaling
- Preserve color channels for color images
- Ensure reproducible results with fixed seed

---

## 2. Test Coverage

### 2.1 Unit Tests

#### Film Profiles Module (`film_grain/profiles.py`)
| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UP001 | Load all film profiles | All 20+ profiles load successfully |
| UP002 | Get profile by name (case-insensitive) | `get_profile("tri-x")` returns Tri-X profile |
| UP003 | Get profile with spaces/hyphens | `get_profile("Kodak Tri-X 400")` works |
| UP004 | List all profiles | `list_profiles()` prints formatted table |
| UP005 | Invalid profile name | Raises KeyError with helpful message |
| UP006 | B&W vs color profile distinction | Color profiles have `color=True` and channel-specific parameters |

#### Renderer Module (`film_grain/renderer.py`)
| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UR001 | Grayscale rendering with MC | Output has same dimensions as input |
| UR002 | Color rendering with MC | Output has 3 channels, same dimensions |
| UR003 | Fast grayscale rendering | Output matches MC within tolerance (see UT007) |
| UR004 | Fast color rendering | Output matches MC within tolerance |
| UR005 | Reproducibility with fixed seed | Same input + seed = identical output |
| UR006 | Different seeds produce different results | Different seeds yield visually distinct grain |
| UR007 | Tolerance test (MC vs Fast) | Fast renderer within 5% RMS error of MC for normal cases |
| UR008 | Zoom factor | `zoom=2.0` produces 2x dimensions |
| UR009 | Grain parameters affect output | Different μ_r, σ_r produce visibly different grain |
| UR010 | Empty/black image handling | Returns uniform black output |
| UR011 | White image handling | Returns appropriate grain pattern |

#### Fast Renderer Module (`film_grain/renderer_fast.py`)
| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UF001 | Kernel computation | Spatial correlation kernel has correct shape |
| UF002 | Variance LUT computation | Signal-dependent amplitude matches theory |
| UF003 | FFT convolution | Correct spatial filtering behavior |
| UF004 | Performance | Fast renderer 100x faster than MC for 1024x1024 |

#### Post-Processing Module (`film_grain/postprocess.py`)
| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UPP001 | Characteristic curve | S-curve applied to input tones |
| UPP002 | Visibility modulation | Grain reduced in deep shadows and bright highlights |
| UPP003 | Chromatic aberration | Subtle per-channel spatial offsets |

#### RNG Module (`film_grain/rng.py`)
| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| URNG001 | Cell seed reproducibility | Same cell coordinates + global seed = same local seed |
| URNG002 | Poisson sampling | Mean matches λ parameter over many samples |
| URNG003 | Log-normal sampling | Distribution matches expected grain size distribution |

### 2.2 Integration Tests

#### IT001: End-to-End B&W Rendering
**Input**: `testimage.png` (1304x1304 RGB)  
**Command**: `python render.py testimage.png -o test_bw.png --profile tri-x --bw --fast`  
**Expected**: 
- Output file created
- Dimensions match input (1304x1304)
- Grayscale output with visible Tri-X grain pattern

#### IT002: End-to-End Color Rendering
**Input**: `testimage.png` (1304x1304 RGB)  
**Command**: `python render.py testimage.png -o test_color.png --profile portra400 --fast`  
**Expected**: 
- Output file created
- 3 color channels preserved
- Per-channel grain with Portra 400 characteristics

#### IT003: Monte Carlo High Quality
**Input**: `testimage.png` (1304x1304 RGB)  
**Command**: `python render.py testimage.png -o test_mc.png --profile tri-x --bw --mc 200`  
**Expected**: 
- Output file created with maximum quality grain
- Render time ~30-60s for this image size
- Organic clumping visible in grain structure

#### IT004: Custom Parameters
**Input**: `testimage.png`  
**Command**: `python render.py testimage.png -o test_custom.png --mu-r 0.05 --sigma-r 0.02 --fast`  
**Expected**: 
- Output uses custom grain parameters instead of profile defaults

#### IT005: Post-Processing Pipeline
**Input**: `testimage.png`  
**Command**: `python render.py testimage.png -o test_post.png --profile tri-x --bw --hd-curve --visibility --fast`  
**Expected**: 
- Characteristic curve applied to input
- Visibility modulation applied to output
- Grain appropriately weighted by tonal zone

#### IT006: Zoom Rendering
**Input**: `testimage.png`  
**Command**: `python render.py testimage.png -o test_zoom.png --profile tri-x --bw --zoom 2.0 --fast`  
**Expected**: 
- Output dimensions = 2608x2608 (2x input)
- Grain rendered at higher resolution

#### IT007: Reproducibility Test
**Input**: `testimage.png`  
**Commands**:
```bash
python render.py testimage.png -o rep1.png --profile tri-x --bw --seed 42 --fast
python render.py testimage.png -o rep2.png --profile tri-x --bw --seed 42 --fast
```
**Expected**: `rep1.png` and `rep2.png` are identical

#### IT008: Format Support
**Input**: `testimage.png`  
**Commands**:
```bash
python render.py testimage.png -o test.jpg --profile tri-x --bw --fast
python render.py testimage.png -o test.tiff --profile tri-x --bw --fast
```
**Expected**: All formats produce valid output files

### 2.3 Performance Tests

| Test ID | Description | Threshold |
|---------|-------------|-----------|
| PT001 | Fast renderer 512x512 B&W | < 0.1s |
| PT002 | Fast renderer 1024x1024 color | < 0.5s |
| PT003 | MC renderer 512x512 B&W (n_mc=100) | ~5-15s |
| PT004 | MC renderer 1024x1024 B&W (n_mc=100) | ~20-60s |

### 2.4 Edge Cases

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| EC001 | Very small image (8x8) | Renders without error |
| EC002 | Single pixel image | Returns uniform grain |
| EC003 | Extreme zoom (zoom=0.1) | Downscaled output |
| EC004 | Extreme grain (mu_r=0.2) | Handles large grains |
| EC005 | Zero sigma_r (constant radius) | Renders with uniform grain size |
| EC006 | RGBA input image | Alpha channel dropped, RGB processed |
| EC007 | Grayscale input | Processes without conversion |

---

## 3. Test Procedures

### 3.1 Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Verify installation
python render.py --list-profiles
```

### 3.2 Running Tests

#### Automated Tests (to be implemented)
Create `tests/test_renderer.py` with pytest tests for all unit tests.

#### Manual Tests
1. **Visual Inspection**: Compare output images to expected grain patterns
2. **Dimension Check**: Verify output dimensions match expectations
3. **Format Verification**: Open output files in image viewer
4. **Performance Timing**: Use `time` command or built-in timing

### 3.3 Test Data
- **Input**: `testimage.png` (1304x1304 RGB, 2.3MB)
- **Reference Outputs**: Store in `tests/reference/` directory
- **Test Outputs**: Store in `tests/output/` directory

---

## 4. Defect Tracking

### Severity Levels
- **Critical**: Application crashes, incorrect core algorithm, data loss
- **High**: Wrong output format, parameter not applied, performance regression
- **Medium**: Visual quality issues, edge case failures
- **Low**: Minor UI issues, documentation gaps

### Known Issues
None at this time.

---

## 5. Deliverables

### 5.1 Test Plan Document (this file)
✅ Completed

### 5.2 Test Results
- [ ] Run all integration tests
- [ ] Record performance metrics
- [ ] Document any defects found

### 5.3 Test Reports
- [ ] Summary report with pass/fail counts
- [ ] Detailed defect reports
- [ ] Performance comparison report

---

## 6. Questions for Clarification

### 6.1 Requirements Clarification
**Question**: What is the expected RMS error tolerance between fast and Monte Carlo renderers?

**Context**: UT007 requires a quantitative tolerance, but the documentation states "excellent approximation" without specific numbers.

**Recommendation**: Establish tolerance based on visual inspection or published benchmarks.

### 6.2 Test Automation
**Question**: Should test images be committed to the repository?

**Context**: `testimage.png` is currently in the project directory but not tracked by git.

**Recommendation**: Add to `.gitignore` as user-generated content, create smaller test images for automated tests.

### 6.3 Performance Baselines
**Question**: Are the performance numbers in the README measured on specific hardware?

**Context**: Performance tests need consistent hardware context for meaningful comparison.

**Recommendation**: Document test hardware specifications or use relative comparisons.

---

## 7. Git Status and Commit

### Current State
- **Branch**: `graniac`
- **Modified Files**: 
  - `README.md` (rebranding to GrainRX)
  - `film_grain/__init__.py` (rebranding)
  - `render.py` (rebranding)
  - `output_grain.png` (test output, should be in .gitignore)

### Actions Required
1. ✅ Created `.gitignore` file
2. ⏳ Add test image to `.gitignore`
3. ⏳ Commit rebranding changes
4. ⏳ Remove `output_grain.png` from tracking

### Recommended Git Commands
```bash
# Add .gitignore
git add .gitignore

# Remove output files from tracking
git rm --cached output_grain.png

# Stage modified files
git add README.md film_grain/__init__.py render.py

# Commit changes
git commit -m "Rebrand application to GrainRX"

# Verify status
git status
```

---

## 8. Next Steps

1. **Immediate**:
   - [ ] Commit current changes to git
   - [ ] Run integration tests with `testimage.png`
   - [ ] Document test results

2. **Short-term**:
   - [ ] Implement automated unit tests
   - [ ] Create reference output images for comparison
   - [ ] Set up CI/CD pipeline

3. **Long-term**:
   - [ ] Performance regression testing
   - [ ] Visual quality metrics
   - [ ] User acceptance testing

---

## Appendix A: Film Profiles Reference

### Black & White Stocks
- `tri-x`: Kodak Tri-X 400 (μ_r=0.07, σ_r=0.025)
- `tmax100`: Kodak T-Max 100 (μ_r=0.03, σ_r=0.005)
- `hp5`: Ilford HP5 Plus 400 (μ_r=0.065, σ_r=0.02)
- `delta3200`: Ilford Delta 3200 (μ_r=0.12, σ_r=0.05)

### Color Stocks
- `portra400`: Kodak Portra 400 (μ_r=0.04, σ_r=0.008)
- `ektar100`: Kodak Ektar 100 (μ_r=0.025, σ_r=0.004)
- `ultramax400`: Kodak Ultramax 400 (μ_r=0.055, σ_r=0.016)

---

## Appendix B: Command Reference

```bash
# List all profiles
python render.py --list-profiles

# Fast B&W rendering
python render.py input.jpg -o output.png --profile tri-x --bw --fast

# Fast color rendering
python render.py input.jpg -o output.png --profile portra400 --fast

# Monte Carlo high quality
python render.py input.jpg -o output.png --profile tri-x --bw --mc 200

# Custom parameters
python render.py input.jpg -o output.png --mu-r 0.05 --sigma-r 0.02 --fast

# With post-processing
python render.py input.jpg -o output.png --profile tri-x --bw --hd-curve --visibility --fast
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-04-17  
**QA Engineer**: AI Assistant  
**Status**: Ready for Execution