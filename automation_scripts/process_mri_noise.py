import cv2
import numpy as np
import os
from pathlib import Path

def add_gaussian_noise(image, mean=0, std_dev=10):
    """Add Gaussian noise to an RGB image."""
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    noisy_image = image.astype(np.float32) + noise
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    return noisy_image

def add_salt_pepper_noise(image, amount=0.01):
    """Add salt and pepper noise (siyah beyaz noktalar)."""
    noisy = image.copy()
    
    # Salt (beyaz noktalar)
    num_salt = int(amount * image.size * 0.5)
    coords = [np.random.randint(0, i - 1, num_salt) for i in image.shape[:2]]
    if len(image.shape) == 3:
        noisy[coords[0], coords[1], :] = 255
    else:
        noisy[coords[0], coords[1]] = 255
    
    # Pepper (siyah noktalar)
    num_pepper = int(amount * image.size * 0.5)
    coords = [np.random.randint(0, i - 1, num_pepper) for i in image.shape[:2]]
    if len(image.shape) == 3:
        noisy[coords[0], coords[1], :] = 0
    else:
        noisy[coords[0], coords[1]] = 0
    
    return noisy

def add_uniform_noise(image, low=-10, high=10):
    """Add uniform noise (her değer eşit olasılıkla)."""
    noise = np.random.uniform(low, high, image.shape).astype(np.float32)
    noisy_image = image.astype(np.float32) + noise
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    return noisy_image

def add_speckle_noise(image, var=0.01):
    """Add speckle noise (multiplicative noise - MRI'da yaygın)."""
    noise = np.random.randn(*image.shape) * var
    noisy = image.astype(np.float32) * (1 + noise)
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def add_poisson_noise(image):
    """Add Poisson noise (shot noise - sensör kaynaklı)."""
    vals = len(np.unique(image))
    vals = 2 ** np.ceil(np.log2(vals))
    noisy = np.random.poisson(image.astype(np.float32) / 255.0 * vals) / vals * 255
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def add_rician_noise(image, std_dev=10):
    """Add Rician noise (MRI magnitude images için gerçekçi)."""
    noise_real = np.random.normal(0, std_dev, image.shape)
    noise_imag = np.random.normal(0, std_dev, image.shape)
    
    noisy = np.sqrt((image.astype(np.float32) + noise_real)**2 + noise_imag**2)
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def add_mixed_noise(image, gaussian_std=5, salt_pepper_amount=0.005):
    """Gaussian + Salt&Pepper karışımı (gerçekçi MRI noise)."""
    # Önce Gaussian
    noisy = add_gaussian_noise(image, std_dev=gaussian_std)
    # Sonra Salt&Pepper
    noisy = add_salt_pepper_noise(noisy, amount=salt_pepper_amount)
    return noisy

def apply_median_filter(image, kernel_size=3):
    """Apply a median filter to reduce noise."""
    return cv2.medianBlur(image, kernel_size)

def upscale_image(image, target_size=(512, 512), method='bicubic'):
    """Upscale an image using bicubic or other interpolation."""
    method_map = {
        'bicubic': cv2.INTER_CUBIC,
        'lanczos': cv2.INTER_LANCZOS4,
        'bilinear': cv2.INTER_LINEAR,
        'nearest': cv2.INTER_NEAREST
    }
    interpolation = method_map.get(method, cv2.INTER_CUBIC)
    return cv2.resize(image, target_size, interpolation=interpolation)

def process_single_image(image_path, output_dir,
                         noise_type='gaussian', noise_param=5, 
                         median_kernel=3, upscale_method='bicubic'):
    """Process a single image: add noise → filter → upscale."""
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not read {image_path}")
        return
    
    # Step 1. Add noise (farklı türler)
    if noise_type == 'gaussian':
        noisy = add_gaussian_noise(image, std_dev=noise_param)
    elif noise_type == 'salt_pepper':
        noisy = add_salt_pepper_noise(image, amount=noise_param)
    elif noise_type == 'uniform':
        noisy = add_uniform_noise(image, low=-noise_param, high=noise_param)
    elif noise_type == 'speckle':
        noisy = add_speckle_noise(image, var=noise_param)
    elif noise_type == 'poisson':
        noisy = add_poisson_noise(image)
    elif noise_type == 'rician':
        noisy = add_rician_noise(image, std_dev=noise_param)
    elif noise_type == 'mixed':
        noisy = add_mixed_noise(image, gaussian_std=noise_param, salt_pepper_amount=0.005)
    else:
        print(f"⚠️ Unknown noise type: {noise_type}, using Gaussian")
        noisy = add_gaussian_noise(image, std_dev=noise_param)
    
    # Step 2. Apply median filter
    filtered = apply_median_filter(noisy, median_kernel)
    
    # Step 3. Upscale to 512×512
    upscaled = upscale_image(filtered, (512, 512), method=upscale_method)
    
    # Create output subfolders
    noisy_dir = os.path.join(output_dir, "noisy_256")
    filtered_dir = os.path.join(output_dir, "filtered_256")
    upscaled_dir = os.path.join(output_dir, "upscaled_512")
    
    os.makedirs(noisy_dir, exist_ok=True)
    os.makedirs(filtered_dir, exist_ok=True)
    os.makedirs(upscaled_dir, exist_ok=True)
    
    # Save results
    filename = Path(image_path).name
    cv2.imwrite(os.path.join(noisy_dir, filename), noisy)
    cv2.imwrite(os.path.join(filtered_dir, filename), filtered)
    cv2.imwrite(os.path.join(upscaled_dir, filename), upscaled)
    
    print(f"✅ Processed: {filename}")

def process_dataset(input_folder, output_folder,
                    noise_type='gaussian', noise_param=5,
                    median_kernel=3, upscale_method='bicubic'):
    """Process all images in the input folder."""
    
    os.makedirs(output_folder, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"📊 Found {len(image_files)} images in '{input_folder}'")
    print(f"🔊 Noise type: {noise_type}")
    print(f"🔊 Noise parameter: {noise_param}")
    print(f"🧹 Median kernel: {median_kernel}")
    print(f"⬆️ Upscale method: {upscale_method}")
    print("="*60)
    
    for idx, img_file in enumerate(image_files, 1):
        img_path = os.path.join(input_folder, img_file)
        print(f"[{idx}/{len(image_files)}] Processing {img_file}")
        process_single_image(img_path, output_folder,
                             noise_type=noise_type,
                             noise_param=noise_param,
                             median_kernel=median_kernel,
                             upscale_method=upscale_method)
    
    print("\n✅ All images processed successfully!")
    print(f"Results saved in '{output_folder}'")
    print("   ├── noisy_256/")
    print("   ├── filtered_256/")
    print("   └── upscaled_512/")

# ==================== MAIN PROGRAM ====================

if __name__ == "__main__":
    print("="*60)
    print("🧠 MRI RGB Pipeline: Noise → Filter → Bicubic Upscale")
    print("="*60)
    
     # === Parameters ===
    # Noise türleri: 'gaussian', 'salt_pepper', 'uniform', 'speckle', 'poisson', 'rician', 'mixed'
    noise_type = 'rician'      # ⭐ MRI için en gerçekçi
    noise_param = 5     # Rician için std_dev
    median_kernel = 3
    upscale_method = 'bicubic'

    # === Directories ===
    input_folder = "/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Dataset_LR_256x256"
    output_folder = "/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Dataset_Upscaled512x512/latest_rician_noise2=std5"
    
   
    
    process_dataset(
        input_folder=input_folder,
        output_folder=output_folder,
        noise_type=noise_type,
        noise_param=noise_param,
        median_kernel=median_kernel,
        upscale_method=upscale_method
    )
    
    print("\n" + "="*60)
    print("📝 Noise Types Guide:")
    print("  • gaussian  : Smooth, yumuşak noise (klasik)")
    print("  • rician    : MRI magnitude için gerçekçi ⭐")
    print("  • speckle   : Multiplicative, dokulu noise")
    print("  • salt_pepper: Siyah-beyaz noktalar")
    print("  • uniform   : Her değer eşit olasılıkla")
    print("  • poisson   : Shot noise (sensör)")
    print("  • mixed     : Gaussian + Salt&Pepper")
    print("="*60)
