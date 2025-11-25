# StableSR Automation Tools

This repository contains automation scripts and report generators for StableSR experiments.

## Repository Contents

### 📁 automation_scripts/
Scripts for running experiments and processing images:
- **`run_sweep.py`**: Resolution sweep automation
- **`run_seed_sweep.py`**: Seed comparison automation
- **`fixed_grain_noise.py`**: (Recommended) Adds noise with fixed grain size across resolutions
- **`perceptual_noise_final.py`**: Adds noise with power-law scaling
- **`process_mri_noise.py`**: MRI-specific noise processing

### 📁 report_generators/
Tools for creating visual reports from experiment outputs:
- **`generate_report.py`**: PDF report generator for resolution sweeps
- **`generate_seed_report.py`**: PDF report generator for seed sweeps
- **`generate_report_pptx.py`**: PowerPoint report generator

### 📁 noise/
Results and documentation from noise generation experiments:
- Comparison of different noise scaling methods (Fixed Grain vs Linear vs Power-Law)
- Visual examples of noise consistency across resolutions

## Usage

### 1. Noise Generation (Recommended Method)
To add consistent "fixed grain" noise to images:

```bash
python automation_scripts/fixed_grain_noise.py \
  --input_dir path/to/images \
  --output_dir output_folder \
  --sigma 8 \
  --base_res 128
```

### 2. Running Sweeps
```bash
python automation_scripts/run_sweep.py
```

### 3. Generating Reports
```bash
python report_generators/generate_report.py \
  --input_dir path/to/sweep_output \
  --ref_dir path/to/reference_images \
  --output_pdf report.pdf
```

## Note
This repository does **not** contain:
- The core StableSR codebase
- Large datasets or experiment outputs (`data/`)
- Generated PDF/PPTX reports (`reports/`)
