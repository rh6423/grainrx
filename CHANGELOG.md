# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD pipeline with GitHub Actions for automated testing on push and PR
- Comprehensive pytest test suite:
  - `test_profiles.py` - Profile registry smoke tests
  - `test_reproducibility.py` - Deterministic seed verification
  - `test_renderer_agreement.py` - Fast vs MC statistical agreement (slow)
- Film profile parameter calibration documentation in `core/profiles.py`
- Sample output images in `examples/` directory demonstrating various film stocks
- Side-by-side comparison of fast analytical vs Monte Carlo renderers

### Changed
- Updated README with links to example outputs and renderer comparison

### Fixed
- Various minor documentation improvements

---

## [0.1.0] - 2024-01-01

### Added
- Initial release of GrainRX film grain synthesis tool
- Physics-based Boolean model implementation for realistic film grain
- Two rendering engines:
  - Fast analytical renderer (~100-500x faster)
  - Monte Carlo Boolean model (reference quality)
- Film stock profiles for popular B&W and color films:
  - Kodak: Tri-X, T-Max series, Portra series, Ektar, Gold, Ultramax
  - Ilford: HP5, Delta series, FP4, Pan F
  - Fujifilm: Neopan Acros, Superia
- Command-line interface with parameter controls
- Web-based GUI for interactive parameter exploration
- Python API for programmatic use

### Technical Details
- Implements the inhomogeneous Boolean model (Newson et al., IPOL 2017)
- Cell-based reproducible RNG for memory-efficient grain generation
- Signal-dependent variance matching real film's p(1-p) behavior
- Per-channel grain variation for color stocks
- H&D curve emulation option
- Perceptual visibility modulation