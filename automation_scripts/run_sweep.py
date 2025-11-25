import os
import subprocess
from pathlib import Path

# ================== AYARLAR ==================

# StableSR repo kökü (ŞU AN ZATEN BURDA ÇALIŞIYORSUN)
STABLESR_ROOT = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/StableSR")

# Python executable (ikuru-stablesr env)
PYTHON_BIN = "/home/nekodu-01/anaconda3/envs/ikuru-stablesr/bin/python"

# Model / config path'leri
CONFIG_PATH = STABLESR_ROOT / "configs/stableSRNew/v2-finetune_text_T_512.yaml"
CKPT_PATH = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/ComfyUI/models/checkpoints/stablesr_000117.ckpt")
VQGAN_CKPT_PATH = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/ComfyUI/models/checkpoints/vqgan_cfw_00011.ckpt")

# Girdi klasörleri: 128, 256, 512 için
# Bunları kendi klasör yapılarına göre düzenle
BASE_INPUT_DIRS = {
    128: Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Datasets/Te-gl_0018/Te-gl_0018_128"),
    256: Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Datasets/Te-gl_0018/Te-gl_0018_256"),
    512: Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/Brain_Tumor_MRI_Datasets/Te-gl_0018/Te-gl_0018_512"),
}

# Çıktıların toplanacağı ana klasör
OUTPUT_ROOT = Path("/home/nekodu-01/Interns-Comfy-Trials/ikuru/MRI_Dataset/StableSR_resolution_sweep")

# Seed + diffusion ayarları
DDPM_STEPS = 50
DEC_W = 0.5
SEED = 42
N_SAMPLES = 1
COLORFIX = "wavelet"

# Denenecek scale (upscale) faktörleri
UPSCALES = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

# ================== YARDIMCI FONKSİYON ==================

def run_stablesr_for_resolution(base_res: int):
    """
    Belirli bir taban çözünürlük (128, 256, 512) için
    tüm UPSCALES listesini tarar.
    """
    init_dir = BASE_INPUT_DIRS[base_res]
    if not init_dir.exists():
        print(f"[⚠️] Input dir yok: {init_dir} (base_res={base_res}), SKIP")
        return

    # Header removed for minimal output

    for scale in UPSCALES:
        # Örn: base_res=256, scale=2.0 → 'base256_x2.0'
        outdir = OUTPUT_ROOT / f"base{base_res}_x{scale}".replace(".", "p")
        outdir.mkdir(parents=True, exist_ok=True)

        print(f"[STARTED] base_res={base_res}, upscale={scale}")

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
            "--seed", str(SEED),
            "--n_samples", str(N_SAMPLES),
            "--colorfix_type", COLORFIX,
            "--upscale", str(scale),
            "--precision", "full", # <--- EKLENDI: Precision full olsun
        ]

        # Çalıştır
        result = subprocess.run(
            cmd,
            cwd=str(STABLESR_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Log'u kaydet (her kombinasyonun log'u olsun)
        log_file = outdir / "log.txt"
        with log_file.open("w") as f:
            f.write(result.stdout)

        if result.returncode == 0:
            print(f"[OK] base_res={base_res}, upscale={scale}")
        else:
            print(f"[ERROR] base_res={base_res}, upscale={scale} -> {log_file}")


# ================== ANA AKIŞ ==================

if __name__ == "__main__":
    print("### StableSR Resolution Sweep (128, 256, 512 × [1.0–5.0]) ###")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    for base_res in [128, 256, 512]:
        run_stablesr_for_resolution(base_res)

    print("\n### Bitti. Tüm çıktılar şu klasörde: ###")
    print(f"  {OUTPUT_ROOT}")
