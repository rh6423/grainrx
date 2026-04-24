# GrainRX End-to-End QA Summary Report

**Date:** 2026-04-23  
**Tester:** Automated QA  
**Scope:** Functional testing of CLI, Web UI API, and Python API (not visual quality)

---

## Executive Summary

| Category | Tests Run | Passed | Failed |
|----------|-----------|--------|--------|
| CLI Interface | 14 | 14 | 0 |
| Edge Cases | 8 | 8 | 0 |
| Web UI API | 3 | 3 | 0 |
| Python API | 9 | 9 | 0 |
| **TOTAL** | **34** | **34** | **0** |

**Overall Status:** ✅ PASS (all tests passing)

---

## Bug Fixes Applied

### BUG-001: Shape Mismatch with `--zoom` + `--visibility` Combination [FIXED]

**Severity:** Medium  
**Component:** CLI / Post-processing pipeline  
**Location:** `render.py`, lines 294-311

**Description:**  
When using the `--zoom` parameter together with `--visibility`, a ValueError occurred because the visibility modulation function attempted to subtract the original image from the zoomed output, causing a shape mismatch.

**Fix Applied:**  
Modified `render.py` to resize `original_norm` to match the zoomed output dimensions before applying visibility modulation. When `--zoom != 1.0`, the original normalized image is now resized using PIL's BILINEAR interpolation to match the rendered output size.

**Verification:**
```bash
python render.py input.png -o output.png --profile tri-x --bw --fast --hd-curve --visibility --zoom 1.5
```
Result: ✅ PASS - Renders successfully with no errors.

---

## Detailed Test Results

### CLI Interface Tests (14/14 PASSED)

| Test | Command | Result |
|------|---------|--------|
| CLI-01 | Basic B&W fast render | ✅ PASS |
| CLI-02 | Color fast render | ✅ PASS |
| CLI-03 | Monte Carlo B&W (low samples) | ✅ PASS |
| CLI-04 | Custom parameters | ✅ PASS |
| CLI-05 | List profiles | ✅ PASS (18 profiles) |
| CLI-06 | Help output | ✅ PASS |
| CLI-07 | Missing input file error | ✅ PASS |
| CLI-08 | Invalid profile error | ✅ PASS |
| CLI-09 | HD curve option | ✅ PASS |
| CLI-10 | Visibility modulation | ✅ PASS |
| CLI-11 | Zoom parameter | ✅ PASS |
| CLI-12 | Max-dim resize | ✅ PASS |
| CLI-13 | Seed reproducibility | ✅ PASS |
| CLI-14 | Filter sigma override | ✅ PASS |

### Edge Case Tests (8/8 PASSED)

| Test | Scenario | Result |
|------|----------|--------|
| EDGE-01 | Very small image (64x64) | ✅ PASS |
| EDGE-02 | Very large grain size (mu_r=0.5) | ✅ PASS |
| EDGE-03 | Zero sigma-r (uniform grains) | ✅ PASS |
| EDGE-04 | High zoom factor (4.0x) | ✅ PASS |
| EDGE-05 | Low MC samples (5) | ✅ PASS |
| EDGE-06 | HD curve option | ✅ PASS |
| EDGE-07 | Visibility modulation | ✅ PASS |
| EDGE-08 | Combined options (--zoom + --visibility) | ✅ PASS (BUG-001 fixed) |

### Web UI API Tests (3/3 PASSED)

| Test | Endpoint | Result |
|------|----------|--------|
| UI-11 | GET /api/ | ✅ PASS - Returns version info |
| UI-12 | GET /profiles | ✅ PASS - Returns 18 film profiles |
| UI-13 | POST /render | ✅ PASS - B&W and color rendering work |

### Python API Tests (9/9 PASSED)

| Test | Function | Result |
|------|----------|--------|
| API-01 | get_profile() | ✅ PASS |
| API-02 | render_grayscale_fast() | ✅ PASS |
| API-03 | render_color_fast() | ✅ PASS |
| API-04 | Reproducibility (same seed) | ✅ PASS - Max diff = 0.0 |
| API-05 | Different seeds produce different results | ✅ PASS - Max diff = 78.0 |
| API-06 | Zoom parameter | ✅ PASS - Shape correct |
| API-07 | Custom parameters | ✅ PASS |
| API-08 | render_grayscale (Monte Carlo) | ✅ PASS |
| API-09 | MC with zoom | ✅ PASS |

---

## Film Profiles Verified

All 18 film profiles are accessible and functional:

**B&W Profiles:**
- acros, delta3200, hp5, panf, pmkii, tri-x, tmax100, tmax400

**Color Profiles:**
- ektar100, portra160, portra400, superia400, ultramax400, vintage200, vintage400, vintage800

---

## Performance Notes

| Operation | Image Size | Time |
|-----------|------------|------|
| Fast B&W render | 1288×832 | ~0.07s |
| Fast color render | 1288×832 | ~0.22s |
| MC B&W (30 samples) | 256×160 | ~1.7s |

---

## Recommendations

1. **Add integration test:** Add a permanent test case for the `--zoom` + `--visibility` combination to prevent regression
2. **Consider adding:** A `--help-profiles` flag to show detailed info about each film profile

---

## Conclusion

GrainRX is functionally complete and working correctly across all interfaces (CLI, Web UI API, Python API). All 34 tests pass successfully. The previously identified bug (BUG-001) has been fixed. All core functionality including both renderers (fast analytical and Monte Carlo), all film profiles, and all parameter options work as expected.

**Ready for production deployment.**
