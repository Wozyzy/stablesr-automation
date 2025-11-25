#!/usr/bin/env python3
"""
Perceptually Consistent Gaussian Noise Addition

This script adds Gaussian noise to images at different resolutions (128, 256, 512)
such that the noise appears visually similar across all sizes.

Key features:
- NO blur or detail loss (noise added independently to each resolution)
- Power-law scaling: std_dev ∝ resolution^α (default α=0.6)
- Automatic discovery of input images in standard directory structure
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path


def add_gaussian_noise(image, std_dev, mean=0):
    """Add Gaussian noise to an image."""
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    noisy = image.astype(np.float32) + noise
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy


def compute_scaled_std(base_std, base_size, target_size, alpha=0.6):
    """
    Scale std_dev using power law: std_target = base_std * (target_size / base_size)^alpha
    
    α = 0.0 : No scaling (same std for all sizes) - 128 will look very noisy
    α = 0.5 : Square root scaling - balanced
    α = 0.6 : Recommended - best perceptual match (default)
    α = 1.0 : Linear scaling - 512 will look very noisy
    """
    scale = (target_size / base_size) ** alpha
    return base_std * scale


def main():
    parser = argparse.ArgumentParser(
        description="Add perceptually consistent Gaussian noise across resolutions"
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Directory containing Te-gl_0018_128, Te-gl_0018_256, Te-gl_0018_512 subdirs"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="perceptual_noise_final",
        help="Output directory for noisy images"
    )
    parser.add_argument(
        "--base_std",
        type=float,
        default=15.0,
        help="Std dev for base resolution (256x256)"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.6,
        help="Power-law scaling exponent (0.5-0.7 recommended)"
    )
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Configuration
    base_size = 256
    sizes = [128, 256, 512]
    
    print(f"📝 Configuration:")
    print(f"   Base std_dev: {args.base_std}")
    print(f"   Scaling alpha: {args.alpha}")
    print(f"   Formula: std = {args.base_std} × (size/256)^{args.alpha}\n")
    
    noisy_images = {}
    
    for size in sizes:
        # Compute scaled std_dev
        std_dev = compute_scaled_std(args.base_std, base_size, size, args.alpha)
        
        # Find input image
        subdir_pattern = f"Te-gl_0018_{size}"
        subdir = Path(args.input_dir) / subdir_pattern
        
        if not subdir.exists():
            print(f"⚠️  Skipping {size}x{size}: {subdir} not found")
            continue
        
        # Find first image file
        image_files = list(subdir.glob("*.jpg")) + list(subdir.glob("*.png"))
        if not image_files:
            print(f"⚠️  Skipping {size}x{size}: No images in {subdir}")
            continue
        
        img_path = image_files[0]
        print(f"Processing {size}x{size} (std_dev={std_dev:.2f})...")
        print(f"  Input: {img_path.name}")
        
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ❌ Failed to load")
            continue
        
        # Add noise
        noisy = add_gaussian_noise(img, std_dev)
        
        # Save
        out_clean = os.path.join(args.output_dir, f"original_{size}.png")
        out_noisy = os.path.join(args.output_dir, f"noisy_{size}.png")
        
        cv2.imwrite(out_clean, img)
        cv2.imwrite(out_noisy, noisy)
        
        noisy_images[size] = noisy
        print(f"  ✓ Saved")
    
    # Create comparison
    if len(noisy_images) >= 2:
        print("\n📊 Creating comparison image...")
        comparison_height = 256
        comparison_imgs = []
        
        for size in sorted(noisy_images.keys()):
            img = noisy_images[size]
            resized = cv2.resize(img, (comparison_height, comparison_height), 
                                interpolation=cv2.INTER_CUBIC)
            
            # Add labels
            std_dev = compute_scaled_std(args.base_std, base_size, size, args.alpha)
            cv2.putText(resized, f"{size}x{size}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(resized, f"std={std_dev:.1f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            comparison_imgs.append(resized)
        
        comparison = np.hstack(comparison_imgs)
        comparison_path = os.path.join(args.output_dir, "comparison_noisy.png")
        cv2.imwrite(comparison_path, comparison)
        print(f"  ✓ Saved: {comparison_path}")
    
    print(f"\n✅ Done! Results in: {args.output_dir}/")
    print(f"\n💡 Tip: If noise doesn't look consistent, adjust --alpha (try 0.5-0.7)")


if __name__ == "__main__":
    main()
