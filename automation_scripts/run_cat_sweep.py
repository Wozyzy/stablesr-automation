import os
import subprocess
import argparse
from pathlib import Path

# ================== AYARLAR ==================

# StableSR repo kökü
STABLESR_ROOT = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/StableSR")

# Python executable
PYTHON_BIN = "/home/nekodu-01/anaconda3/envs/ikuru-stablesr/bin/python"

# Model / config path'leri
CONFIG_PATH = STABLESR_ROOT / "configs/stableSRNew/v2-finetune_text_T_512.yaml"
CKPT_PATH = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/ComfyUI/models/checkpoints/stablesr_000117.ckpt")
VQGAN_CKPT_PATH = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/ComfyUI/models/checkpoints/vqgan_cfw_00011.ckpt")

# Parametre Aralıkları
STEPS_LIST = [20, 50, 100, 200]
DEC_W_LIST = [0.1, 0.3, 0.5, 0.7, 1.0]
COLORFIX_LIST = ["wavelet", "adain", "nofix"]

# Sabitler
UPSCALE = 4.0
SEED = -1
N_SAMPLES = 1

def parse_args():
    parser = argparse.ArgumentParser(description="Run parameter sweep for Cat image.")
    parser.add_argument("--input_image", type=str, required=True, help="Path to the single cat image (e.g. cat_128.png).")
    parser.add_argument("--output_root", type=str, required=True, help="Directory to save sweep results.")
    return parser.parse_args()

def main():
    args = parse_args()
    
    input_path = Path(args.input_image)
    if not input_path.exists():
        print(f"Error: Input image not found at {input_path}")
        return

    # Create a temp input dir because the script expects a directory, not a file
    # We will copy the image there
    temp_input_dir = Path(args.output_root) / "temp_input"
    temp_input_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy/Link the image
    temp_img_path = temp_input_dir / input_path.name
    if not temp_img_path.exists():
        import shutil
        shutil.copy(input_path, temp_img_path)
    
    print(f"Starting Parameter Sweep for: {input_path.name}")
    print(f"Output Root: {args.output_root}")
    
    total_runs = len(STEPS_LIST) * len(DEC_W_LIST) * len(COLORFIX_LIST)
    current_run = 0

    for steps in STEPS_LIST:
        for dec_w in DEC_W_LIST:
            for colorfix in COLORFIX_LIST:
                current_run += 1
                
                # Output folder name: steps_50_dec_0.5_wavelet
                folder_name = f"steps_{steps}_dec_{dec_w}_color_{colorfix}"
                outdir = Path(args.output_root) / folder_name
                outdir.mkdir(parents=True, exist_ok=True)
                
                print(f"\n[{current_run}/{total_runs}] Running: Steps={steps}, DecW={dec_w}, Color={colorfix}")
                
                cmd = [
                    PYTHON_BIN,
                    str(STABLESR_ROOT / "scripts/sr_val_ddpm_text_T_vqganfin_oldcanvas.py"),
                    "--config", str(CONFIG_PATH),
                    "--ckpt", str(CKPT_PATH),
                    "--vqgan_ckpt", str(VQGAN_CKPT_PATH),
                    "--init-img", str(temp_input_dir),
                    "--outdir", str(outdir),
                    "--ddpm_steps", str(steps),
                    "--dec_w", str(dec_w),
                    "--seed", str(SEED),
                    "--n_samples", str(N_SAMPLES),
                    "--colorfix_type", colorfix,
                    "--upscale", str(UPSCALE),
                    "--precision", "full",
                ]

                try:
                    result = subprocess.run(
                        cmd,
                        cwd=str(STABLESR_ROOT),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                    
                    # Save log
                    with (outdir / "log.txt").open("w") as f:
                        f.write(result.stdout)
                        
                    if result.returncode != 0:
                        print(f"  [❌] Failed! See log in {outdir}")
                    else:
                        print(f"  [✅] Done.")
                        
                except Exception as e:
                    print(f"  [❌] Exception: {e}")

    print("\nSweep Completed.")

if __name__ == "__main__":
    main()
