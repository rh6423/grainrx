# Film Profile Parameter Calibration

This document describes how the grain parameters for each film stock were derived and calibrated.

## Overview

GrainRX models film grain using the **inhomogeneous Boolean model** (Newson et al., IPOL 2017). Each film profile is characterized by:

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| Mean radius | μ_r | Average grain radius in input pixel units |
| Radius std dev | σ_r | Standard deviation of grain radius (controls clumping) |
| Filter sigma | σ_f | Gaussian filter width modeling optical enlargement |

For color films, separate parameters are provided for each emulsion layer (R, G, B channels).

## Parameter Derivation Methodology

### 1. Published Measurements as Starting Point

Base values were informed by peer-reviewed literature on film grain characterization:

- **Newson et al., IPOL 2017**: "Realistic Film Grain Rendering" provides measured grain statistics for several films including Tri-X 400, HP5, and T-Max 100.
- **Zhang et al., SIGGRAPH 2023**: "Film Grain Rendering and Parameter Estimation" includes analytical methods for extracting grain parameters from scans.

### 2. Visual Calibration Against Reference Scans

Parameters were tuned by comparing rendered output to reference film scans:

**Reference conditions:**
- Film format: 35mm
- Scan resolution: 4000 DPI (approximately 5700 × 3800 pixels)
- Development: C-41 for color, D-76 for B&W at box speed

**Calibration targets:**
1. **Grain coarseness**: Match perceived grain size at native ISO
2. **Clumping behavior**: Match σ_r/μ_r ratio to achieve characteristic grain texture
3. **Per-channel variation**: For color films, match relative grain visibility between layers

### 3. Relative Scaling Within Product Lines

Within each manufacturer's lineup, parameters were scaled proportionally:

- **ISO scaling**: Higher ISO → larger μ_r (more silver halide needed for sensitivity)
- **Technology differences**: T-grain/core-shell films have lower σ_r than traditional cubic crystals at equivalent speed
- **Layer structure**: Color negative films follow the pattern: blue layer > green layer > red layer in grain size

## Parameter Reference Table

### Black & White Films

| Film | ISO | μ_r | σ_r | σ_r/μ_r | Notes |
|------|-----|-----|-----|---------|-------|
| Kodak Tri-X 400 | 400 | 0.070 | 0.025 | 0.36 | Iconic clumping, photojournalism standard |
| Kodak T-Max 100 | 100 | 0.030 | 0.005 | 0.17 | Tabular grain, minimal clumping |
| Kodak T-Max 400 | 400 | 0.050 | 0.010 | 0.20 | Modern fine grain at ISO 400 |
| Kodak Plus-X 125 | 125 | 0.040 | 0.012 | 0.30 | Classic traditional grain |
| Ilford HP5 Plus | 400 | 0.065 | 0.020 | 0.31 | Slightly finer than Tri-X |
| Ilford Delta 100 | 100 | 0.025 | 0.004 | 0.16 | Core-shell, ultra-fine |
| Ilford Delta 400 | 400 | 0.045 | 0.009 | 0.20 | Modern, finer than HP5 |
| Ilford Delta 3200 | 3200 | 0.120 | 0.050 | 0.42 | Extreme grain, heavy clumping |
| Ilford FP4 Plus | 125 | 0.035 | 0.008 | 0.23 | Classic fine grain |
| Ilford Pan F Plus | 50 | 0.020 | 0.003 | 0.15 | Nearly grainless |
| Fuji Neopan Acros | 100 | 0.028 | 0.005 | 0.18 | Exceptionally fine |

### Color Negative Films

| Film | ISO | μ_r (avg) | σ_r (avg) | Notes |
|------|-----|-----------|-----------|-------|
| Kodak Portra 160 | 160 | 0.035 | 0.006 | Ultra-fine, portrait standard |
| Kodak Portra 400 | 400 | 0.042 | 0.009 | Fine grain, warm tones |
| Kodak Portra 800 | 800 | 0.062 | 0.016 | Noticeable but pleasing |
| Kodak Ektar 100 | 100 | 0.026 | 0.004 | World's finest grain color negative |
| Fuji Superia 400 | 400 | 0.056 | 0.015 | Punchy consumer film |
| Kodak Gold 200 | 200 | 0.047 | 0.012 | Warm cast, visible grain |
| Kodak Ultramax 400 | 400 | 0.057 | 0.016 | Characterful budget film |

### Per-Channel Parameters (Color Films)

For color films, the three emulsion layers have different characteristics:

| Film | Channel | μ_r | σ_r | Relative Size |
|------|---------|-----|-----|---------------|
| Portra 400 | Red | 0.035 | 0.006 | Smallest (bottom layer) |
| Portra 400 | Green | 0.040 | 0.008 | Medium (middle layer) |
| Portra 400 | Blue | 0.050 | 0.012 | Largest (top layer) |

The blue-sensitive layer is always largest because it sits on top of the emulsion stack and requires larger crystals to capture enough light after passing through upper layers.

## Validation

### Statistical Agreement Test

The `tests/test_renderer_agreement.py` file validates that the fast analytical renderer produces statistically equivalent results to the Monte Carlo Boolean model:

```bash
pytest tests/test_renderer_agreement.py -v
```

This test verifies that per-pixel means converge between renderers, confirming the analytical approximation preserves the signal-dependent tonal response.

### Visual Validation

Sample outputs in `examples/` demonstrate characteristic grain for each profile. Compare against reference scans to validate visual accuracy.

## Limitations and Future Work

1. **Push/pull processing**: Current parameters assume box-speed development. Pushed films would need adjusted parameters (typically larger effective grain).

2. **Scanner variability**: Different scanners produce different apparent grain due to interpolation and noise characteristics. Parameters calibrated for 4000 DPI may need adjustment for other resolutions.

3. **Enlargement effects**: The filter_sigma parameter models optical enlargement but is currently fixed per profile. Real enlargements vary based on printer lens quality and technique.

4. **Measured reference data**: Future versions could include direct measurements from scanned film strips using the methodology from Zhang et al. (2023).

## References

1. Newson, Faraj, Delon, Galerne. "Realistic Film Grain Rendering." *Image Processing On Line*, 7 (2017), pp. 165–183. https://doi.org/10.5201/ipol.2017.192

2. Zhang, Wang, Tian, Pappas. "Film Grain Rendering and Parameter Estimation." *ACM Trans. Graph.* 42(4), SIGGRAPH 2023.

3. Yedlin, Steve. "On Film Grain Emulation." https://www.yedlin.net/NerdyFilmTechStuff/OnFilmGrainEmulation.html

4. Dube, C., et al. "Characterization of Film Grain." *Journal of the SMPTE*, various issues.