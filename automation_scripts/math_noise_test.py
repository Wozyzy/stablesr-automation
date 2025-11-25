#!/usr/bin/env python3
"""
Math-Based Noise Addition (Pure Matrix Repetition)

This script adds noise using pure matrix mathematics (numpy repeat) instead of image resizing.
It ensures that the noise pattern is mathematically identical across resolutions by repeating
the base noise pixels exactly.

Logic:
1. Generate random noise at base resolution (e.g., 128x128)
2. Repeat each pixel N times (e.g., 4 times for 512x512) using numpy.repeat
3. Add to image

This is equivalent to Nearest Neighbor interpolation but implemented purely mathematically.
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path


def add_math_noise(image, sigma=20, base_res=128):
    """
    Add noise using pure matrix repetition (no cv2.resize).
    
    Args:
        image: Input image (H, W, C)
        sigma: Noise standard deviation
        base_res: Base resolution for noise generation
    """
    h, w, c = image.shape
    
    # Calculate scale factor (e.g., 512 / 128 = 4)
    # This tells us how many times to repeat each noise cell
    scale_factor = max(1, w // base_res)
    
    # 1. Generate Base Random Matrix (128x128)
    # We generate enough rows/cols to cover the image after repetition
    base_h = int(np.ceil(h / scale_factor))
    base_w = int(np.ceil(w / scale_factor))
    
    noise_base = np.random.normal(0, sigma, (base_h, base_w, c)).astype(np.float32)
    
    # 2. Matrix Repetition (Kronecker Logic)
    # axis=0 (rows) and axis=1 (cols) are repeated scale_factor times
    # Example: [A, B] -> [A, A, A, A, B, B, B, B]
    if scale_factor > 1:
        noise_pattern = noise_base.repeat(scale_factor, axis=0).repeat(scale_factor, axis=1)
    else:
        noise_pattern = noise_base
    
    # Crop if dimensions don't match exactly (e.g. if 512 not divisible by base)
    noise_pattern = noise_pattern[:h, :w, :]
    
    # 3. Add Noise to Image
    noisy_image = image.astype(np.float32) + noise_pattern
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    return noisy_image


def main():
    parser = argparse.ArgumentParser(description="Add math-based (matrix repeat) noise")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing Te-gl_0018_128, etc.")
    parser.add_argument("--output_dir", type=str, default="noise/math_noise_output", help="Output directory")
    parser.add_argument("--sigma", type=float, default=25.0, help="Noise intensity (standard deviation)")
    parser.add_argument("--base_res", type=int, default=128, help="Base resolution for noise grain")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"📝 Configuration:")
    print(f"   Sigma: {args.sigma}")
    print(f"   Base Resolution: {args.base_res}")
    print(f"   Method: Matrix Repetition (numpy.repeat)")
    
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
        
        # Add math noise
        noisy = add_math_noise(img, sigma=args.sigma, base_res=args.base_res)
        
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
            # Use nearest neighbor for preview to keep the blocky look
            resized = cv2.resize(img, (comparison_height, comparison_height), 
                                interpolation=cv2.INTER_NEAREST)
            
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
