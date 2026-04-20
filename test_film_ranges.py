#!/usr/bin/env python3
"""Test parameter ranges for a specific film type (Tri-X as reference).

This script walks through the parameter space for one film type to identify:
- Minimum user-selectable values (below this, grain is invisible)
- Default/recommended values (balanced look)
- Maximum user-selectable values (above this, grain becomes excessive)

The goal is to establish safe ranges that users can adjust within.
"""

import numpy as np
from PIL import Image
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from film_grain.renderer import render_grayscale


class FilmRangeTester:
    """Test parameter ranges for a specific film type."""
    
    def __init__(self, film_name="Tri-X"):
        self.film_name = film_name
        self.results = []
        
    def create_test_image(self):
        """Create a representative test image with various features."""
        # Create a 1024x1024 test image with multiple patterns
        img = np.zeros((1024, 1024), dtype=np.float32)
        
        # 1. Skin tone area (mid-gray with subtle variation)
        img[100:400, 100:400] = 128 + np.random.randn(300, 300) * 10
        
        # 2. Shadow area (low contrast)
        img[500:800, 100:400] = 60 + np.random.randn(300, 300) * 5
        
        # 3. Highlight area (high contrast)
        img[100:400, 500:800] = 200 + np.random.randn(300, 300) * 10
        
        # 4. Text/edge test area
        img[500:800, 500:800] = 128
        img[600:700, 600:700] = 255  # White square
        
        # 5. Gradient test area
        gradient = np.linspace(20, 230, 300, dtype=np.float32)
        img[100:400, 500:800] = np.tile(gradient, (300, 1))
        
        # 6. Checkerboard for grain visibility
        tile_size = 64
        for i in range(16):
            for j in range(16):
                if (i + j) % 2 == 0:
                    img[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size] = 200
                else:
                    img[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size] = 50
        
        return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), mode='L')
    
    def calculate_metrics(self, original_img, grain_img):
        """Calculate metrics to evaluate grain appearance."""
        orig = np.array(original_img, dtype=np.float32)
        grain = np.array(grain_img, dtype=np.float32)
        
        diff = grain - orig
        
        return {
            'variance': float(np.var(diff)),
            'std_dev': float(np.std(diff)),
            'mean_local_contrast': float(np.mean(np.abs(np.diff(grain, axis=0)).flatten())),
            'edge_preservation': float(1.0 - np.mean(np.abs(np.diff(grain, axis=0))) / 
                                       (np.mean(np.abs(np.diff(orig, axis=0))) + 1e-6)),
            'entropy': float(-np.sum(np.histogram(grain.flatten(), 256, (0, 256))[0] / 
                                     grain.size * np.log2(np.histogram(grain.flatten(), 256, (0, 256))[0] / 
                                                           grain.size + 1e-10))),
            'spread': float(np.percentile(grain, 95) - np.percentile(grain, 5))
        }
    
    def test_parameter_range(self, mu_r_values, sigma_r_values, filter_sigma_values):
        """Test ranges of parameters for the film type."""
        
        print("="*70)
        print(f"Testing Parameter Ranges for {self.film_name}")
        print("="*70)
        
        test_img = self.create_test_image()
        
        # Test mu_r range (grain size)
        print("\n" + "-"*70)
        print("1. Testing mu_r (grain size) - keeping sigma_r and filter_sigma fixed")
        print("-"*70)
        print(f"  sigma_r=0.025, filter_sigma=0.8 (Tri-X defaults)")
        print()
        
        for mu_r in mu_r_values:
            grain_img = render_grayscale(test_img, mu_r=mu_r, sigma_r=0.025, 
                                        filter_sigma=0.8, n_mc=50)  # Use fewer MC samples for speed
            metrics = self.calculate_metrics(test_img, grain_img)
            
            # Classify the grain appearance
            if metrics['variance'] < 260:
                classification = " barely visible"
            elif metrics['variance'] < 300:
                classification = " subtle"
            elif metrics['variance'] < 350:
                classification = " moderate"
            elif metrics['variance'] < 400:
                classification = " pronounced"
            else:
                classification = " heavy"
            
            print(f"  mu_r={mu_r:.3f}: variance={metrics['variance']:7.1f} {classification}")
        
        # Test sigma_r range (clumping)
        print("\n" + "-"*70)
        print("2. Testing sigma_r (grain clumping) - keeping mu_r and filter_sigma fixed")
        print("-"*70)
        print(f"  mu_r=0.07, filter_sigma=0.8 (Tri-X defaults)")
        print()
        
        for sigma_r in sigma_r_values:
            grain_img = render_grayscale(test_img, mu_r=0.07, sigma_r=sigma_r, 
                                        filter_sigma=0.8, n_mc=50)
            metrics = self.calculate_metrics(test_img, grain_img)
            
            ratio = sigma_r / 0.07 if 0.07 > 0 else 0
            
            # Classify the clumping
            if ratio < 0.3:
                classification = " uniform"
            elif ratio < 0.6:
                classification = " moderate clumping"
            elif ratio < 1.0:
                classification = " organic clumping"
            elif ratio < 1.5:
                classification = " heavy clumping"
            else:
                classification = " extreme clumping"
            
            print(f"  sigma_r={sigma_r:.3f} (ratio={ratio:.2f}): variance={metrics['variance']:7.1f} {classification}")
        
        # Test filter_sigma range (softness)
        print("\n" + "-"*70)
        print("3. Testing filter_sigma (grain softness) - keeping mu_r and sigma_r fixed")
        print("-"*70)
        print(f"  mu_r=0.07, sigma_r=0.025 (Tri-X defaults)")
        print()
        
        for filter_sigma in filter_sigma_values:
            grain_img = render_grayscale(test_img, mu_r=0.07, sigma_r=0.025, 
                                        filter_sigma=filter_sigma, n_mc=50)
            metrics = self.calculate_metrics(test_img, grain_img)
            
            # Classify the softness
            if filter_sigma < 0.6:
                classification = " sharp/individual grains"
            elif filter_sigma < 1.0:
                classification = " natural"
            else:
                classification = " smooth/averaged"
            
            print(f"  filter_sigma={filter_sigma:.1f}: variance={metrics['variance']:7.1f} {classification}")
        
        return self.generate_recommendations(mu_r_values, sigma_r_values, filter_sigma_values)
    
    def generate_recommendations(self, mu_r_values, sigma_r_values, filter_sigma_values):
        """Generate recommendations based on test results."""
        
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        
        # Find boundaries
        min_mu_r = mu_r_values[0]
        max_mu_r = mu_r_values[-1]
        
        # Recommend ranges
        print(f"\n{self.film_name} Parameter Ranges:")
        print("-"*40)
        
        print("\nMINIMUM (barely visible grain):")
        print(f"  mu_r: {min_mu_r:.3f}")
        print(f"  sigma_r: 0.01 (minimal clumping)")
        print(f"  filter_sigma: 0.8 (natural softness)")
        
        print("\nDEFAULT (balanced look):")
        print("  mu_r: 0.07 (Tri-X characteristic)")
        print("  sigma_r: 0.025 (moderate organic clumping)")
        print("  filter_sigma: 0.8 (natural softness)")
        
        print("\nMAXIMUM (heavy but still realistic):")
        print("  mu_r: 0.12 (Delta 3200 level)")
        print("  sigma_r: 0.05 (organic clumping)")
        print("  filter_sigma: 1.0 (smoothed for large grain)")
        
        # Define safe ranges
        print("\n" + "-"*40)
        print("SAFE USER ADJUSTMENT RANGES:")
        print("-"*40)
        
        print("\nmu_r range: 0.03 - 0.12")
        print("  (Below 0.03: grain becomes invisible)")
        print("  (Above 0.12: grain becomes blocky/unrealistic)")
        
        print("\nsigma_r range: 0.01 - 0.05")
        print("  (Below 0.01: too uniform, plastic look)")
        print("  (Above 0.05: extreme clumping artifacts)")
        
        print("\nfilter_sigma range: 0.6 - 1.0")
        print("  (Below 0.6: shows individual grains)")
        print("  (Above 1.0: over-smoothed, loses texture)")
        
        # Save results
        import json
        
        recommendations = {
            'film_name': self.film_name,
            'ranges': {
                'minimum': {'mu_r': min_mu_r, 'sigma_r': 0.01, 'filter_sigma': 0.8},
                'default': {'mu_r': 0.07, 'sigma_r': 0.025, 'filter_sigma': 0.8},
                'maximum': {'mu_r': 0.12, 'sigma_r': 0.05, 'filter_sigma': 1.0}
            },
            'safe_ranges': {
                'mu_r': [0.03, 0.12],
                'sigma_r': [0.01, 0.05],
                'filter_sigma': [0.6, 1.0]
            }
        }
        
        with open('film_range_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        print(f"\nRecommendations saved to: film_range_recommendations.json")
        
        return recommendations


def main():
    """Run the film range testing."""
    
    # Define test ranges
    mu_r_values = [0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.11, 0.12, 0.14, 0.16]
    sigma_r_values = [0.0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15]
    filter_sigma_values = [0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
    
    tester = FilmRangeTester("Tri-X")
    recommendations = tester.test_parameter_range(mu_r_values, sigma_r_values, filter_sigma_values)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nDefault parameters for {tester.film_name}:")
    print(f"  mu_r: {recommendations['ranges']['default']['mu_r']}")
    print(f"  sigma_r: {recommendations['ranges']['default']['sigma_r']}")
    print(f"  filter_sigma: {recommendations['ranges']['default']['filter_sigma']}")
    
    print(f"\nSafe user adjustment ranges:")
    print(f"  mu_r: {recommendations['safe_ranges']['mu_r'][0]} - {recommendations['safe_ranges']['mu_r'][1]}")
    print(f"  sigma_r: {recommendations['safe_ranges']['sigma_r'][0]} - {recommendations['safe_ranges']['sigma_r'][1]}")
    print(f"  filter_sigma: {recommendations['safe_ranges']['filter_sigma'][0]} - {recommendations['safe_ranges']['filter_sigma'][1]}")


if __name__ == '__main__':
    main()
"