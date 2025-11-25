# Automation Scripts

This directory contains automation scripts for running StableSR experiments.

## Scripts

### Core StableSR Automation
- **`automate_stablesr.py`**: Generates multiple copies and downscaled versions of an input image, then runs StableSR
- **`run_sweep.py`**: Runs StableSR across different base resolutions (128, 256, 512) and upscale factors (1.0x to 5.0x)
- **`run_seed_sweep.py`**: Compares fixed vs. random seeds for 2x and 4x upscales with 5 repeats
- **`run_cat_sweep.py`**: Parameter sweep on a single image to optimize StableSR settings (ddpm_steps, dec_w, colorfix_type)

### Noise Processing
- **`simple_gaussian_noise.py`**: Adds Gaussian noise to images at multiple resolutions with manual std_dev control
- **`consistent_gaussian_noise.py`**: Adds noise at 512x512 then downscales for visual consistency across resolutions
- **`process_mri_noise.py`**: MRI-specific noise processing with multiple noise types (Rician, Gaussian, etc.)

## Usage Examples

```bash
# Resolution sweep
python run_sweep.py

# Seed comparison
python run_seed_sweep.py

# Consistent noise addition
python consistent_gaussian_noise.py --input_image /path/to/image.png --output_dir results
```
