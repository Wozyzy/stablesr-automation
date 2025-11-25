import os
import subprocess
import random
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

# Girdi klasörleri
BASE_INPUT_DIRS = {
    128: Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Datasets/Te-gl_0018/Te-gl_0018_128"),
    256: Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Datasets/Te-gl_0018/Te-gl_0018_256"),
    512: Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Datasets/Te-gl_0018/Te-gl_0018_512"),
}

# Çıktıların toplanacağı ana klasör
OUTPUT_ROOT = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/StableSR_seed_sweep")

# Sabit ayarlar
DDPM_STEPS = 50
DEC_W = 0.5
N_SAMPLES = 1
COLORFIX = "wavelet"

# Deney ayarları
UPSCALES = [2.0, 4.0]
NUM_REPEATS = 5
SEED_MODES = ["fixed", "random"] # fixed=42, random=rastgele

# ================== YARDIMCI FONKSİYON ==================

def run_seed_experiment(base_res: int):
    init_dir = BASE_INPUT_DIRS[base_res]
    if not init_dir.exists():
        print(f"[⚠️] Input dir yok: {init_dir} (base_res={base_res}), SKIP")
        return

    print(f"\n======================")
    print(f"▶ Base resolution: {base_res}x{base_res}")
    print(f"======================")

    for scale in UPSCALES:
        for mode in SEED_MODES:
            print(f"\n--- Mode: {mode.upper()}, Scale: {scale}x ---")
            
            for i in range(NUM_REPEATS):
                # Seed belirle
                if mode == "fixed":
                    current_seed = 42
                else:
                    current_seed = -1 # Model kendisi random atayacak
                
                # Klasör yapısı: Output / Mode / baseRes_xScale / run_i
                # Örn: .../fixed/base128_x2p0/run_0
                folder_name = f"base{base_res}_x{scale}".replace(".", "p")
                outdir = OUTPUT_ROOT / mode / folder_name / f"run_{i}"
                outdir.mkdir(parents=True, exist_ok=True)

                print(f"[ℹ️] Run {i+1}/{NUM_REPEATS} (Seed: {current_seed}) -> {outdir}")

                cmd = [
                    PYTHON_BIN,
                    str(STABLESR_ROOT / "scripts/sr_val_ddpm_text_T_vqganfin_oldcanvas.py"),
                    "--config", str(CONFIG_PATH),
                    "--ckpt", str(CKPT_PATH),
                    "--vqgan_ckpt", str(VQGAN_CKPT_PATH),
                    "--init-img", str(init_dir),
                    "--outdir", str(outdir),
                    "--ddpm_steps", str(DDPM_STEPS),
                    "--dec_w", str(DEC_W),
                    "--seed", str(current_seed),
                    "--n_samples", str(N_SAMPLES),
                    "--colorfix_type", COLORFIX,
                    "--upscale", str(scale),
                    "--precision", "full",
                ]

                # Çalıştır
                result = subprocess.run(
                    cmd,
                    cwd=str(STABLESR_ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # Log kaydet
                log_file = outdir / "log.txt"
                with log_file.open("w") as f:
                    f.write(result.stdout)

                if result.returncode != 0:
                    print(f"[❌] Hata oluştu! Log: {log_file}")

# ================== ANA AKIŞ ==================

if __name__ == "__main__":
    print("### StableSR Seed Sweep (Fixed vs Random) ###")
    print(f"Upscales: {UPSCALES}")
    print(f"Repeats: {NUM_REPEATS}")
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    for base_res in [128, 256, 512]:
        run_seed_experiment(base_res)

    print("\n### Bitti. ###")
    print(f"Çıktılar: {OUTPUT_ROOT}")
