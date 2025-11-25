# StableSR Experiment Workspace

This directory contains the StableSR repository and related automation/reporting tools.

## Directory Structure

```
StableSR/
├── StableSR/                    # Clean StableSR repository (Git repo)
├── automation_scripts/          # StableSR automation scripts
├── report_generators/           # PDF/PPTX report generators
├── reports/                     # Generated reports
├── outputs/                     # Test outputs and intermediate results
└── data/                        # Experiment data and reference images
    ├── StableSR_resolution_sweep/
    ├── StableSR_resolution_sweep_noisy/
    ├── StableSR_seed_sweep/
    ├── StableSR_seed_sweep_noisy/
    ├── cat_sweep/
    ├── Te-gl_0018/              # Reference images (clean)
    ├── Te-gl_0018_noisy/        # Reference images (noisy)
    └── 720vs128/
```

## Quick Start

### Running Experiments

```bash
# Resolution sweep
cd automation_scripts
python run_sweep.py

# Seed comparison
python run_seed_sweep.py

# Consistent noise processing
python consistent_gaussian_noise.py --input_image ../data/Te-gl_0018/Te-gl_0018_512/Te-gl_0018.png
```

### Generating Reports

```bash
# Generate resolution sweep PDF
cd report_generators
python generate_report.py \
  --input_dir ../data/StableSR_resolution_sweep \
  --ref_dir ../data/Te-gl_0018 \
  --output_pdf ../reports/resolution_report.pdf

# Generate seed sweep PDF
python generate_seed_report.py \
  --input_dir ../data/StableSR_seed_sweep_noisy \
  --ref_dir ../data/Te-gl_0018_noisy \
  --output_pdf ../reports/seed_report.pdf
```

## Components

- **StableSR**: Original repository, kept clean for Git operations
- **automation_scripts**: Scripts for running StableSR experiments
- **report_generators**: Tools for creating visual reports
- **reports**: All generated PDF and PowerPoint reports
- **outputs**: Temporary test outputs and intermediate results
- **data**: Experiment outputs and reference datasets

See README.md files in each directory for detailed documentation.
