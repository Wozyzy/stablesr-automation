import argparse
import os
import shutil
import subprocess
import sys
from PIL import Image
import math

def parse_args():
    parser = argparse.ArgumentParser(description="Automate StableSR with multiple scales and repeats.")
    parser.add_argument("--input_image", type=str, required=True, help="Path to the single input image.")
    parser.add_argument("--output_dir", type=str, required=True, help="Base directory for outputs.")
    parser.add_argument("--stablesr_script", type=str, default="scripts/sr_val_ddpm_text_T_vqganfin_oldcanvas.py", help="Path to the StableSR script.")
    parser.add_argument("--num_repeats", type=int, default=5, help="Number of times to repeat each variation.")
    
    # Capture unknown args to pass to the subprocess
    args, unknown = parser.parse_known_args()
    return args, unknown

def main():
    args, unknown_args = parse_args()

    if not os.path.exists(args.input_image):
        print(f"Error: Input image '{args.input_image}' not found.")
        sys.exit(1)

    # Setup directories
    temp_inputs_dir = os.path.join(args.output_dir, "temp_inputs")
    results_dir = os.path.join(args.output_dir, "results")
    
    if os.path.exists(temp_inputs_dir):
        shutil.rmtree(temp_inputs_dir)
    os.makedirs(temp_inputs_dir)
    
    os.makedirs(results_dir, exist_ok=True)

    # Load image
    try:
        img = Image.open(args.input_image).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    original_width, original_height = img.size
    print(f"Loaded image: {args.input_image} ({original_width}x{original_height})")

    # Define scales
    scales = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

    print(f"Generating {args.num_repeats} copies for each scale: {scales}")

    count = 0
    for scale in scales:
        if scale == 1.0:
            resized_img = img
            scale_name = "original"
        else:
            new_width = int(original_width / scale)
            new_height = int(original_height / scale)
            resized_img = img.resize((new_width, new_height), resample=Image.LANCZOS)
            scale_name = f"down_{scale}x"
        
        for i in range(args.num_repeats):
            filename = f"{scale_name}_{i+1}.png"
            save_path = os.path.join(temp_inputs_dir, filename)
            resized_img.save(save_path)
            count += 1
    
    print(f"Generated {count} input images in '{temp_inputs_dir}'.")

    # Construct command
    cmd = [
        sys.executable, args.stablesr_script,
        "--init-img", temp_inputs_dir,
        "--outdir", results_dir
    ]
    
    # Add pass-through arguments
    cmd.extend(unknown_args)

    print("\nRunning StableSR script...")
    print("Command:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        print("\nStableSR execution completed successfully.")
        print(f"Results should be in: {results_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\nError running StableSR script: {e}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nExecution interrupted.")
        sys.exit(1)

if __name__ == "__main__":
    main()
