# Noise Experiment Results

This directory contains outputs from various noise generation experiments aimed at achieving perceptually consistent noise across different image resolutions (128, 256, 512).

## Experiment Types

### 1. Fixed Grain Noise (Recommended)
**Script:** `automation_scripts/fixed_grain_noise.py`
**Output:** `fixed_grain_output/`, `fixed_grain_low_sigma/`, `fixed_grain_sigma_8/`

**Logic:**
- Noise is generated at a fixed base resolution (e.g., 128x128).
- It is then **upscaled** to the target image size using **Nearest Neighbor** interpolation.
- This creates "blocky" noise pixels that maintain the same physical size relative to the image content, regardless of resolution.
- **Result:** Identical texture/grain size across all resolutions. No blur.

**Best Settings:**
- Sigma: 8 (for subtle noise) or 15 (for visible noise)
- Base Resolution: 128

### 2. Perceptual / Power-Law Scaling
**Script:** `automation_scripts/perceptual_noise_final.py`
**Output:** `perceptual_noise_test/`, `power_law_v2/`

**Logic:**
- Noise is added independently to each resolution.
- Standard deviation is scaled using a power law: `std = base_std * (size/base_size)^alpha`
- **Result:** Good mathematical consistency, but can look different visually due to pixel density.

### 3. Linear Scaling
**Script:** `automation_scripts/linear_noise_test.py`
**Output:** `linear_noise_output/`, `linear_noise_v2/`

**Logic:**
- Standard deviation scales linearly with resolution.
- **Result:** Often results in too much noise at high resolutions (512x512).

## Comparison

| Method | 128x128 | 512x512 | Consistency |
|--------|---------|---------|-------------|
| **Fixed Grain** | Native Noise | 4x4 Pixel Blocks | ⭐⭐⭐ Best (Texture matches) |
| **Power-Law** | Low Sigma | High Sigma | ⭐⭐ Good (Intensity matches) |
| **Linear** | Low Sigma | Very High Sigma | ⭐ Poor (Too noisy at 512) |
