import cv2
import numpy as np
import os
import argparse

def add_gaussian_noise(image, mean=0, std_dev=25):
    """Add Gaussian noise to an RGB image."""
    # Generate Gaussian noise
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    
    # Add noise to image
    noisy_image = image.astype(np.float32) + noise
    
    # Clip values to 0-255 range and convert back to uint8
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    return noisy_image

def main():
    parser = argparse.ArgumentParser(description="Add Gaussian noise at max resolution and downscale for consistency.")
    parser.add_argument("--input_image", type=str, required=True, help="Path to input image")
    parser.add_argument("--output_dir", type=str, default="consistent_noise_outputs", help="Output directory")
    parser.add_argument("--std_dev", type=float, default=25.0, help="Standard deviation of noise (applied at 512x512)")
    
    args = parser.parse_args()
    
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Parameters
    max_size = 512
    std_dev = args.std_dev
    sizes = [128, 256, 512]
    
    # Load input image
    print(f"Loading input image: {args.input_image}")
    img_input = cv2.imread(args.input_image)
    if img_input is None:
        print(f"❌ Error: Could not load image from {args.input_image}")
        return
    
    # 1. Create base image at MAX size (512x512)
    print(f"Resizing input to {max_size}x{max_size}...")
    img_512 = cv2.resize(img_input, (max_size, max_size), interpolation=cv2.INTER_CUBIC)
    
    # 2. Add noise at MAX resolution
    print(f"Adding Gaussian noise (std_dev={std_dev}) at {max_size}x{max_size}...")
    noisy_512 = add_gaussian_noise(img_512, std_dev=std_dev)
    
    # Save 512x512 versions
    cv2.imwrite(os.path.join(output_dir, "original_512.png"), img_512)
    cv2.imwrite(os.path.join(output_dir, "noisy_512.png"), noisy_512)
    print(f"  ✓ Saved 512x512")
    
    noisy_images = {512: noisy_512}
    
    # 3. Downscale the NOISY image to other sizes
    # This ensures the noise texture scales down exactly with the image
    for size in [256, 128]:
        print(f"\nDownscaling to {size}x{size}...")
        
        # Downscale clean image (from clean 512)
        img_small = cv2.resize(img_512, (size, size), interpolation=cv2.INTER_CUBIC)
        
        # Downscale NOISY image (from noisy 512)
        noisy_small = cv2.resize(noisy_512, (size, size), interpolation=cv2.INTER_CUBIC)
        
        # Save
        cv2.imwrite(os.path.join(output_dir, f"original_{size}.png"), img_small)
        cv2.imwrite(os.path.join(output_dir, f"noisy_{size}.png"), noisy_small)
        
        noisy_images[size] = noisy_small
        print(f"  ✓ Saved {size}x{size} (downscaled from noisy 512)")
    
    # Create comparison image
    print("\nCreating comparison image...")
    
    # Normalize all to same height for comparison (use 256 as reference)
    comparison_height = 256
    comparison_imgs = []
    
    # Sort sizes to show 128 -> 256 -> 512
    for size in sorted(sizes):
        img = noisy_images[size]
        # Resize to comparison height while maintaining aspect ratio
        resized = cv2.resize(img, (comparison_height, comparison_height), interpolation=cv2.INTER_CUBIC)
        
        # Add text label
        labeled = resized.copy()
        cv2.putText(labeled, f"{size}x{size}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(labeled, "from 512", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        comparison_imgs.append(labeled)
    
    # Concatenate horizontally
    comparison = np.hstack(comparison_imgs)
    cv2.imwrite(os.path.join(output_dir, "comparison_noisy.png"), comparison)

    print(f"\n✅ Done! Results saved to '{output_dir}' directory.")
    print(f"\n📝 Method: Noise added ONLY at 512x512, then downscaled.")
    print(f"   This guarantees visually identical noise texture across resolutions.")
    print(f"\n📊 Comparison image: {output_dir}/comparison_noisy.png")

if __name__ == "__main__":
    main()
