import cv2
import numpy as np
import os

def add_gaussian_noise(image, mean=0, std_dev=25):
    """Add Gaussian noise to an RGB image."""
    # Generate Gaussian noise
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    
    # Add noise to image
    noisy_image = image.astype(np.float32) + noise
    
    # Clip values to 0-255 range and convert back to uint8
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    return noisy_image

def create_dummy_image(width, height, color=(100, 100, 100)):
    """Create a dummy image with a circle in the center."""
    # Create background
    img = np.full((height, width, 3), color, dtype=np.uint8)
    
    # Draw a white circle
    center = (width // 2, height // 2)
    radius = width // 4
    cv2.circle(img, center, radius, (255, 255, 255), -1)
    
    # Draw a red rectangle
    cv2.rectangle(img, (10, 10), (width//3, height//3), (0, 0, 255), -1)
    
    return img

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Add Gaussian noise to an image at multiple resolutions.")
    parser.add_argument("--input_image", type=str, required=True, help="Path to input image")
    parser.add_argument("--output_dir", type=str, default="gaussian_test_outputs", help="Output directory")
    parser.add_argument("--std_128", type=float, default=8.0, help="Std dev for 128x128")
    parser.add_argument("--std_256", type=float, default=25.0, help="Std dev for 256x256")
    parser.add_argument("--std_512", type=float, default=50.0, help="Std dev for 512x512")
    
    args = parser.parse_args()
    
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Custom std_dev for each size
    std_devs = {
        128: args.std_128,
        256: args.std_256,
        512: args.std_512
    }
    
    sizes = [128, 256, 512]
    
    # Load input image
    print(f"Loading input image: {args.input_image}")
    img_input = cv2.imread(args.input_image)
    if img_input is None:
        print(f"❌ Error: Could not load image from {args.input_image}")
        return
    
    # Determine base size (use 256 as base)
    base_size = 256
    print(f"Resizing to base size {base_size}x{base_size}...")
    img_base = cv2.resize(img_input, (base_size, base_size), interpolation=cv2.INTER_CUBIC)
    
    noisy_images = {}
    clean_images = {}
    
    for size in sizes:
        std_dev = std_devs[size]
        
        print(f"\nProcessing {size}x{size} (std_dev={std_dev:.2f})...")
        
        # Resize base image to target size
        if size == base_size:
            img = img_base
        else:
            img = cv2.resize(img_base, (size, size), interpolation=cv2.INTER_CUBIC)
        
        # Add noise
        noisy = add_gaussian_noise(img, std_dev=std_dev)
        
        # Save
        cv2.imwrite(os.path.join(output_dir, f"original_{size}.png"), img)
        cv2.imwrite(os.path.join(output_dir, f"noisy_{size}.png"), noisy)
        
        clean_images[size] = img
        noisy_images[size] = noisy
        print(f"  ✓ Saved with std_dev={std_dev:.2f}")
    
    # Create comparison image (all 3 noisy images side-by-side)
    print("\nCreating comparison image...")
    
    # Normalize all to same height for comparison (use 256 as reference)
    comparison_height = 256
    comparison_imgs = []
    
    for size in sizes:
        img = noisy_images[size]
        # Resize to comparison height while maintaining aspect ratio
        resized = cv2.resize(img, (comparison_height, comparison_height), interpolation=cv2.INTER_CUBIC)
        
        # Add text label
        labeled = resized.copy()
        cv2.putText(labeled, f"{size}x{size}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(labeled, f"std={std_devs[size]:.1f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        comparison_imgs.append(labeled)
    
    # Concatenate horizontally
    comparison = np.hstack(comparison_imgs)
    cv2.imwrite(os.path.join(output_dir, "comparison_noisy.png"), comparison)

    print(f"\n✅ Done! Results saved to '{output_dir}' directory.")
    print(f"\nNoise levels (manually tuned):")
    for size in sizes:
        print(f"   - {size}x{size}: std_dev = {std_devs[size]:.2f}")
    print(f"\n📊 Comparison image: {output_dir}/comparison_noisy.png")

if __name__ == "__main__":
    main()
