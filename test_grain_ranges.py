#!/usr/bin/env python3
"""Comprehensive test suite for grain parameter ranges.

This module provides tools to:
- Test single parameters across ranges
- Calculate grain metrics (variance, local contrast, edge preservation)
- Score film profiles for realism
- Generate test cases across categories (fine, moderate, coarse, extreme)
- Identify excessive grain thresholds
"""

import numpy as np
from PIL import Image
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from film_grain.renderer import render_grayscale
from film_grain.profiles import PROFILES as FILM_PROFILES


class GrainParameterTester:
    """Test framework for grain parameter validation."""
    
    def __init__(self):
        self.test_results = []
        
    def create_test_image(self, pattern='gradient', size=(512, 512)):
        """Create a test image with specific patterns.
        
        Args:
            pattern: Type of test pattern ('gradient', 'checkerboard', 'noise', 'edges')
            size: Image dimensions (width, height)
            
        Returns:
            PIL Image object
        """
        width, height = size
        
        if pattern == 'gradient':
            # Create horizontal luminance gradient
            img_array = np.linspace(20, 230, width, dtype=np.float32)
            img_array = np.tile(img_array, (height, 1))
            
        elif pattern == 'checkerboard':
            # Create 8x8 checkerboard pattern
            tile_size = width // 8
            img_array = np.zeros((height, width), dtype=np.float32)
            for i in range(8):
                for j in range(8):
                    if (i + j) % 2 == 0:
                        img_array[i*tile_size:(i+1)*tile_size, 
                                 j*tile_size:(j+1)*tile_size] = 200
                    else:
                        img_array[i*tile_size:(i+1)*tile_size, 
                                 j*tile_size:(j+1)*tile_size] = 50
                        
        elif pattern == 'noise':
            # Create low-contrast noise
            img_array = np.random.uniform(100, 150, (height, width)).astype(np.float32)
            
        elif pattern == 'edges':
            # Create image with sharp edges
            img_array = np.ones((height, width), dtype=np.float32) * 100
            # Add vertical and horizontal lines
            img_array[:, width//2] = 255
            img_array[height//2, :] = 255
            # Add circles
            y, x = np.ogrid[:height, :width]
            mask = (x - width//3)**2 + (y - height//3)**2 < (min(width, height)//4)**2
            img_array[mask] = 255
            
        else:
            raise ValueError(f"Unknown pattern: {pattern}")
            
        # Normalize to 0-255 range
        img_array = np.clip(img_array, 0, 255).astype(np.float32)
        
        return Image.fromarray(img_array.astype(np.uint8), mode='L')
    
    def calculate_grain_metrics(self, original_img, grain_img):
        """Calculate metrics to quantify grain appearance.
        
        Args:
            original_img: Original PIL Image
            grain_img: Grain-added PIL Image
            
        Returns:
            Dictionary of metric values
        """
        orig = np.array(original_img, dtype=np.float32)
        grain = np.array(grain_img, dtype=np.float32)
        
        metrics = {}
        
        # 1. Overall variance (grain strength)
        diff = grain - orig
        metrics['variance'] = float(np.var(diff))
        metrics['std_dev'] = float(np.std(diff))
        
        # 2. Local contrast enhancement
        # Calculate local standard deviation with 3x3 window
        from scipy.ndimage import uniform_filter
        local_mean = uniform_filter(grain, size=3)
        local_var = uniform_filter(grain**2, size=3) - local_mean**2
        local_var = np.maximum(local_var, 0)
        local_std = np.sqrt(local_var)
        
        metrics['mean_local_contrast'] = float(np.mean(local_std))
        metrics['max_local_contrast'] = float(np.max(local_std))
        
        # 3. Edge preservation (comparing edge strength before/after)
        from scipy.ndimage import sobel
        orig_edges = np.abs(sobel(orig, axis=0)) + np.abs(sobel(orig, axis=1))
        grain_edges = np.abs(sobel(grain, axis=0)) + np.abs(sobel(grain, axis=1))
        
        metrics['edge_preservation'] = float(
            np.mean(grain_edges[orig_edges > 10]) / 
            (np.mean(orig_edges[orig_edges > 10]) + 1e-6)
        )
        
        # 4. Grain size estimation (autocorrelation)
        # Calculate 2D autocorrelation of the difference
        diff_norm = diff - np.mean(diff)
        autocorr = np.fft.fftshift(np.fft.ifft2(
            np.fft.fft2(diff_norm) * np.fft.fft2(diff_norm).conj()
        ).real)
        
        # Find first zero crossing to estimate grain size
        center_y, center_x = autocorr.shape[0]//2, autocorr.shape[1]//2
        row_profile = autocorr[center_y, center_x:]
        zero_crossings = np.where(np.diff(np.sign(row_profile)))[0]
        
        if len(zero_crossings) > 0:
            first_zero = zero_crossings[0]
            # Convert to approximate grain size (pixels)
            metrics['estimated_grain_size'] = float(first_zero * 2)  # Approximation
        else:
            metrics['estimated_grain_size'] = float(autocorr.shape[1] / 4)
        
        # 5. Histogram analysis
        hist, _ = np.histogram(grain.flatten(), bins=256, range=(0, 256))
        hist = hist / hist.sum()
        
        # Entropy (disorder/complexity)
        metrics['entropy'] = float(-np.sum(hist * np.log2(hist + 1e-10)))
        
        # Spread (difference between 95th and 5th percentile)
        metrics['spread'] = float(np.percentile(grain, 95) - np.percentile(grain, 5))
        
        return metrics
    
    def test_parameter_combination(self, mu_r, sigma_r, filter_sigma, 
                                    zoom=1.0, pattern='gradient'):
        """Test a specific parameter combination.
        
        Args:
            mu_r: Mean grain radius
            sigma_r: Grain radius std dev
            filter_sigma: Filter sigma in output pixels
            zoom: Output resolution multiplier
            pattern: Test image pattern
            
        Returns:
            Dictionary with parameters and metrics
        """
        test_img = self.create_test_image(pattern=pattern)
        
        # Render with grain
        grain_img = render_grayscale(
            np.array(test_img),  # Convert PIL Image to numpy array
            mu_r=mu_r,
            sigma_r=sigma_r,
            filter_sigma=filter_sigma,
            zoom=zoom
        )
        
        metrics = self.calculate_grain_metrics(test_img, grain_img)
        
        result = {
            'mu_r': mu_r,
            'sigma_r': sigma_r,
            'filter_sigma': filter_sigma,
            'zoom': zoom,
            'pattern': pattern,
            'metrics': metrics
        }
        
        self.test_results.append(result)
        return result
    
    def find_excessive_grain_thresholds(self):
        """Test a range of parameters to find excessive grain thresholds.
        
        Returns:
            Dictionary with threshold analysis
        """
        print("\n" + "="*60)
        print("Testing parameter ranges for excessive grain")
        print("="*60)
        
        # Test mu_r values (grain size)
        mu_r_values = [0.01, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15, 0.20]
        
        print("\nTesting mu_r (mean grain radius):")
        print("-" * 40)
        
        for mu_r in mu_r_values:
            result = self.test_parameter_combination(
                mu_r=mu_r,
                sigma_r=mu_r * 0.3,  # Typical ratio
                filter_sigma=0.8,
                pattern='checkerboard'
            )
            
            metrics = result['metrics']
            print(f"mu_r={mu_r:.3f}: variance={metrics['variance']:.2f}, "
                  f"grain_size≈{metrics['estimated_grain_size']:.1f}px, "
                  f"contrast={metrics['mean_local_contrast']:.2f}")
        
        # Test sigma_r values (clumping)
        print("\nTesting sigma_r (grain clumping):")
        print("-" * 40)
        
        sigma_r_values = [0.0, 0.01, 0.03, 0.05, 0.08, 0.10, 0.15]
        
        for sigma_r in sigma_r_values:
            result = self.test_parameter_combination(
                mu_r=0.07,
                sigma_r=sigma_r,
                filter_sigma=0.8,
                pattern='checkerboard'
            )
            
            metrics = result['metrics']
            ratio = sigma_r / 0.07 if 0.07 > 0 else 0
            print(f"sigma_r={sigma_r:.3f} (ratio={ratio:.2f}): "
                  f"variance={metrics['variance']:.2f}, entropy={metrics['entropy']:.2f}")
        
        # Test filter_sigma values
        print("\nTesting filter_sigma (grain softness):")
        print("-" * 40)
        
        filter_values = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
        
        for filter_sigma in filter_values:
            result = self.test_parameter_combination(
                mu_r=0.07,
                sigma_r=0.02,
                filter_sigma=filter_sigma,
                pattern='edges'
            )
            
            metrics = result['metrics']
            print(f"filter_sigma={filter_sigma:.1f}: "
                  f"edge_preservation={metrics['edge_preservation']:.3f}, "
                  f"grain_size≈{metrics['estimated_grain_size']:.1f}px")
        
        return self.analyze_thresholds()
    
    def analyze_thresholds(self):
        """Analyze test results to identify problematic parameters."""
        print("\n" + "="*60)
        print("Threshold Analysis")
        print("="*60)
        
        # Group results by pattern
        patterns = {}
        for result in self.test_results:
            pattern = result['pattern']
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append(result)
        
        for pattern, results in patterns.items():
            print(f"\n{pattern.upper()} pattern:")
            
            # Find highest variance cases
            sorted_results = sorted(results, key=lambda x: x['metrics']['variance'], reverse=True)
            
            print("  Highest variance cases:")
            for result in sorted_results[:3]:
                metrics = result['metrics']
                print(f"    mu_r={result['mu_r']:.3f}, sigma_r={result['sigma_r']:.3f}: "
                      f"variance={metrics['variance']:.2f}")
        
        return patterns
    
    def test_profile_realism(self):
        """Score film profiles for realism based on parameter ranges."""
        print("\n" + "="*60)
        print("Film Profile Realism Scores")
        print("="*60)
        
        scores = {}
        
        for profile_name, profile in FILM_PROFILES.items():
            mu_r = profile.mu_r
            sigma_r = profile.sigma_r
            
            # Calculate realism score (0-100)
            score = 100
            
            # Penalty for extreme mu_r
            if mu_r < 0.01:
                score -= 20  # Too fine, may be invisible
            elif mu_r > 0.15:
                score -= 40  # Excessive grain
            elif mu_r > 0.12:
                score -= 20  # Very coarse
            
            # Penalty for extreme sigma_r/mu_r ratio
            if mu_r > 0:
                ratio = sigma_r / mu_r
                if ratio > 1.5:
                    score -= 30  # Extreme clumping
                elif ratio > 1.0:
                    score -= 15  # Moderate clumping
            
            # Penalty for very small filter_sigma
            filter_sigma = getattr(profile, 'filter_sigma', 0.8)
            if filter_sigma < 0.5:
                score -= 20  # May show individual grains
            
            scores[profile_name] = {
                'score': max(0, score),
                'mu_r': mu_r,
                'sigma_r': sigma_r,
                'filter_sigma': filter_sigma
            }
            
            print(f"{profile_name:20s}: {scores[profile_name]['score']:3d}/100 "
                  f"(mu_r={mu_r:.3f}, sigma_r={sigma_r:.3f})")
        
        return scores
    
    def generate_test_cases(self):
        """Generate comprehensive test cases across categories."""
        print("\n" + "="*60)
        print("Generated Test Cases")
        print("="*60)
        
        test_cases = {
            'fine_grain': [
                {'mu_r': 0.015, 'sigma_r': 0.003, 'filter_sigma': 0.8, 'description': 'Fine grain (Pan F+)'},
                {'mu_r': 0.025, 'sigma_r': 0.005, 'filter_sigma': 0.8, 'description': 'Fine grain (T-Max 100)'},
            ],
            'moderate_grain': [
                {'mu_r': 0.04, 'sigma_r': 0.008, 'filter_sigma': 0.8, 'description': 'Moderate grain (Portra 400)'},
                {'mu_r': 0.07, 'sigma_r': 0.025, 'filter_sigma': 0.8, 'description': 'Moderate grain (Tri-X)'},
            ],
            'coarse_grain': [
                {'mu_r': 0.10, 'sigma_r': 0.04, 'filter_sigma': 0.8, 'description': 'Coarse grain (HP5+)'},
                {'mu_r': 0.12, 'sigma_r': 0.05, 'filter_sigma': 0.8, 'description': 'Coarse grain (Delta 3200)'},
            ],
            'extreme_grain': [
                {'mu_r': 0.15, 'sigma_r': 0.06, 'filter_sigma': 0.8, 'description': 'Extreme grain (warning)'},
                {'mu_r': 0.20, 'sigma_r': 0.08, 'filter_sigma': 0.8, 'description': 'Excessive grain (problematic)'},
            ]
        }
        
        for category, cases in test_cases.items():
            print(f"\n{category.upper()}:")
            
            for case in cases:
                result = self.test_parameter_combination(
                    mu_r=case['mu_r'],
                    sigma_r=case['sigma_r'],
                    filter_sigma=case['filter_sigma'],
                    pattern='checkerboard'
                )
                
                metrics = result['metrics']
                print(f"  {case['description']}")
                print(f"    variance={metrics['variance']:.2f}, "
                      f"entropy={metrics['entropy']:.2f}, "
                      f"contrast={metrics['mean_local_contrast']:.2f}")
        
        return test_cases


def main():
    """Run comprehensive grain parameter testing."""
    print("="*60)
    print("Grain Parameter Range Testing Suite")
    print("="*60)
    
    tester = GrainParameterTester()
    
    # Run all tests
    tester.find_excessive_grain_thresholds()
    tester.test_profile_realism()
    tester.generate_test_cases()
    
    # Save results to file
    import json
    
    output_data = {
        'test_results': tester.test_results,
        'threshold_analysis': tester.analyze_thresholds()
    }
    
    with open('test_grain_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    print(f"\nResults saved to: test_grain_results.json")
    print(f"Total test cases run: {len(tester.test_results)}")


if __name__ == '__main__':
    main()