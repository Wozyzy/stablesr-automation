#!/usr/bin/env python3
"""
Fixed Grain Noise Addition

This script adds Gaussian noise with a FIXED grain size across all resolutions.
It achieves this by:
1. Generating noise at a base resolution (default 128x128)
2. Upscaling the noise to the target resolution using Nearest Neighbor interpolation
3. Adding this "blocky" noise to the image

This ensures the noise texture looks identical (same grain size) regardless of image resolution.
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path


def add_fixed_grain_noise(image, sigma=25, base_res=128):
    """
    Add noise with fixed grain size locked to base_res.
    
    Args:
        image: Input image (H, W, C)
        sigma: Noise standard deviation (intensity)
        base_res: Base resolution for noise generation (e.g., 128)
    """
    h, w, c = image.shape
    
    # 1. Generate noise at BASE resolution (128x128)
    # We use the aspect ratio of the target image to match dimensions correctly
    aspect_ratio = w / h
    base_w = base_res
    base_h = int(base_res / aspect_ratio)
    
    noise_small = np.random.normal(0, sigma, (base_h, base_w, c)).astype(np.float32)
    
    # 2. Upscale noise to target resolution using NEAREST NEIGHBOR
    # This keeps the noise "blocky" and prevents blurring
    noise_scaled = cv2.resize(noise_small, (w, h), interpolation=cv2.INTER_NEAREST)
    
    # 3. Add noise
    noisy_image = image.astype(np.float32) + noise_scaled
    
    # 4. Clip to valid range
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    return noisy_image


def main():
    parser = argparse.ArgumentParser(description="Add fixed-grain Gaussian noise across resolutions")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing Te-gl_0018_128, etc.")
    parser.add_argument("--output_dir", type=str, default="fixed_grain_noise_output", help="Output directory")
    parser.add_argument("--sigma", type=float, default=25.0, help="Noise intensity (standard deviation)")
    parser.add_argument("--base_res", type=int, default=128, help="Base resolution for noise grain (default: 128)")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"📝 Configuration:")
    print(f"   Sigma: {args.sigma}")
    print(f"   Base Resolution: {args.base_res}x{args.base_res}")
    print(f"   Method: Generate at {args.base_res} -> Upscale (Nearest) -> Add")
    
    sizes = [128, 256, 512]
    noisy_images = {}
    
    for size in sizes:
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
        print(f"Processing {size}x{size}...")
        
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ❌ Failed to load")
            continue
        
        # Add fixed grain noise
        noisy = add_fixed_grain_noise(img, sigma=args.sigma, base_res=args.base_res)
        
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
                                interpolation=cv2.INTER_NEAREST) # Use nearest for preview too to keep grain sharp
            
            # Add labels
            cv2.putText(resized, f"{size}x{size}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(resized, f"sigma={args.sigma}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            comparison_imgs.append(resized)
        
        comparison = np.hstack(comparison_imgs)
        comparison_path = os.path.join(args.output_dir, "comparison_noisy.png")
        cv2.imwrite(comparison_path, comparison)
        print(f"  ✓ Saved: {comparison_path}")
    
    print(f"\n✅ Done! Results in: {args.output_dir}/")


if __name__ == "__main__":
    main()
