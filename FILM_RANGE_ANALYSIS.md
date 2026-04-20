# Tri-X Film Grain Parameter Analysis

## Test Results Summary

### mu_r (Grain Size) Testing
| mu_r | Variance | Classification |
|------|----------|----------------|
| 0.020 | 410.9 | heavy |
| 0.040 | 381.7 | pronounced |
| 0.060 | 385.3 | pronounced |
| 0.080 | 395.5 | pronounced |
| 0.100 | 410.7 | heavy |
| 0.120 | 428.6 | heavy |
| 0.140 | 446.6 | heavy |

**Observation**: Variance increases with mu_r, but the relationship isn't linear. The variance actually dips slightly around mu_r=0.04-0.06 before increasing again.

### sigma_r (Clumping) Testing
| sigma_r | Ratio | Variance | Classification |
|---------|-------|----------|----------------|
| 0.000 | 0.00 | 374.4 | uniform |
| 0.010 | 0.14 | 376.6 | uniform |
| 0.020 | 0.29 | 384.0 | uniform |
| 0.030 | 0.43 | 398.3 | moderate clumping |
| 0.050 | 0.71 | 462.5 | organic clumping |
| 0.070 | 1.00 | 610.9 | heavy clumping |
| 0.100 | 1.43 | 1051.1 | heavy clumping |

**Critical Threshold**: sigma_r/mu_r ratio > 1.0 shows dramatic variance increase (610→1051)

### filter_sigma (Softness) Testing
| filter_sigma | Variance | Classification |
|--------------|----------|----------------|
| 0.5 | 429.1 | sharp |
| 0.7 | 395.3 | natural |
| 0.9 | 398.0 | natural |
| 1.1 | 416.3 | smooth |
| 1.3 | 432.3 | smooth |

**Observation**: filter_sigma=0.7-0.9 provides the most natural grain appearance with lowest variance.

## Parameter Recommendations for Tri-X

### Minimum (Barely Visible Grain)
```
mu_r: 0.02
sigma_r: 0.01
filter_sigma: 0.8
```

### Default (Balanced Look - Tri-X Characteristic)
```
mu_r: 0.07
sigma_r: 0.025
filter_sigma: 0.8
```

### Maximum (Heavy but Realistic)
```
mu_r: 0.12
sigma_r: 0.05
filter_sigma: 1.0
```

## Safe User Adjustment Ranges

### mu_r: 0.03 - 0.12
- **Below 0.03**: Grain becomes invisible/unnatural
- **Above 0.12**: Grain becomes blocky/unrealistic (excessive)

### sigma_r: 0.01 - 0.05
- **Below 0.01**: Too uniform, plastic look
- **Above 0.05**: Extreme clumping artifacts (ratio > 0.71)

### filter_sigma: 0.6 - 1.0
- **Below 0.6**: Shows individual grains (only for extreme zoom)
- **Above 1.0**: Over-smoothed, loses texture

## Key Findings

1. **sigma_r/mu_r ratio is critical**: Keep ratio ≤ 1.0 to avoid extreme clumping artifacts
2. **filter_sigma=0.7-0.9** provides the most natural appearance
3. **mu_r has non-linear effects**: Variance dips around mu_r=0.04-0.06 before increasing
4. **Tri-X defaults (0.07, 0.025, 0.8)** are well-balanced and within safe ranges

## Implementation Notes

The validation system should:
1. Warn users when mu_r > 0.12 or sigma_r > 0.05
2. Check sigma_r/mu_r ratio and warn if > 1.0
3. Recommend filter_sigma between 0.6-1.0 for most use cases
4. Provide these ranges as guidance in the UI

## Next Steps

1. Update film profiles with these safe ranges
2. Add validation warnings for out-of-range parameters
3. Create UI sliders with these min/max values
4. Consider adding a "grain preview" feature to show real-time changes
"