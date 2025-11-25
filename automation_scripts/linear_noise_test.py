#!/usr/bin/env python3
"""
Linear Noise Scaling Test
Sigma scales linearly with resolution: sigma = base_std * (res / base_res)
"""

import numpy as np
import cv2
import os
import argparse
from pathlib import Path


def add_scaled_noise(image, base_std=20, base_res=128):
    """
    Görüntü boyutuna göre gürültü (noise) miktarını ölçekler.
    
    Args:
        image: Giriş resmi (numpy array)
        base_std: Referans çözünürlük (128) için istediğiniz standart sapma
        base_res: Referans alınan en küçük çözünürlük (örn: 128)
    """
    h, w, c = image.shape
    current_res = w  # Kare olduğunu varsayıyoruz
    
    # Ölçekleme faktörü (Lineer artış)
    scale_factor = current_res / base_res
    
    # Yeni sigma değeri
    sigma = base_std * scale_factor
    
    print(f"Resim Boyutu: {current_res}x{current_res} | Kullanılan Sigma: {sigma:.2f}")
    
    # Gaussian Noise oluştur (Mean=0, Std=sigma)
    noise = np.random.normal(0, sigma, (h, w, c))
    
    # Gürültüyü ekle
    noisy_image = image.astype(np.float32) + noise
    
    # 0-255 arasına sıkıştır (Clipping) ve uint8'e çevir
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    return noisy_image


def main():
    parser = argparse.ArgumentParser(description="Linear noise scaling test")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory")
    parser.add_argument("--output_dir", type=str, default="linear_noise_test", help="Output directory")
    parser.add_argument("--base_std", type=float, default=15.0, help="Base std for 128x128")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    sizes = [128, 256, 512]
    noisy_images = {}
    
    for size in sizes:
        # Find input image
        subdir = Path(args.input_dir) / f"Te-gl_0018_{size}"
        if not subdir.exists():
            print(f"⚠️  Skipping {size}: {subdir} not found")
            continue
        
        image_files = list(subdir.glob("*.jpg")) + list(subdir.glob("*.png"))
        if not image_files:
            print(f"⚠️  Skipping {size}: No images found")
            continue
        
        # Load image
        img = cv2.imread(str(image_files[0]))
        if img is None:
            print(f"❌ Failed to load {size}")
            continue
        
        # Add noise with linear scaling
        noisy = add_scaled_noise(img, base_std=args.base_std, base_res=128)
        
        # Save
        cv2.imwrite(os.path.join(args.output_dir, f"original_{size}.png"), img)
        cv2.imwrite(os.path.join(args.output_dir, f"noisy_{size}.png"), noisy)
        noisy_images[size] = noisy
    
    # Create comparison
    if noisy_images:
        print("\n📊 Creating comparison...")
        comparison_imgs = []
        for size in sorted(noisy_images.keys()):
            img = noisy_images[size]
            resized = cv2.resize(img, (256, 256), interpolation=cv2.INTER_CUBIC)
            
            # Calculate sigma for display
            sigma = args.base_std * (size / 128)
            cv2.putText(resized, f"{size}x{size}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(resized, f"sigma={sigma:.1f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            comparison_imgs.append(resized)
        
        comparison = np.hstack(comparison_imgs)
        cv2.imwrite(os.path.join(args.output_dir, "comparison_noisy.png"), comparison)
        print(f"✅ Done! Check {args.output_dir}/comparison_noisy.png")


if __name__ == "__main__":
    main()
