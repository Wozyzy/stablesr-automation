# Report Generators

This directory contains scripts for generating PDF and PowerPoint reports from StableSR experiment outputs.

## Scripts

### PDF Report Generators
- **`generate_report.py`**: Creates PDF reports for resolution sweep experiments
  - Displays input and output images side-by-side
  - Organized by scale and resolution
  
- **`generate_seed_report.py`**: Creates PDF reports for seed sweep experiments
  - Compares fixed vs. random seeds
  - Shows input image alongside multiple runs
  
- **`generate_cat_report.py`**: Creates PDF reports for parameter sweep experiments
  - Grid layout: dec_w (rows) vs. ddpm_steps (columns)
  - One page per colorfix_type

### PowerPoint Report Generators
- **`generate_report_pptx.py`**: Creates PowerPoint reports for resolution sweeps
  - One slide per scale
  
- **`generate_seed_report_pptx.py`**: Creates PowerPoint reports for seed sweeps
  - One slide per setting (mode, resolution, scale)

## Usage Examples

```bash
# Generate resolution sweep PDF
python generate_report.py \
  --input_dir /path/to/sweep/output \
  --ref_dir /path/to/reference/images \
  --output_pdf report.pdf

# Generate seed sweep PDF with references
python generate_seed_report.py \
  --input_dir /path/to/seed/sweep \
  --ref_dir /path/to/reference \
  --output_pdf seed_report.pdf

# Generate PowerPoint report
python generate_report_pptx.py \
  --input_dir /path/to/sweep/output \
  --output_pptx presentation.pptx
```

## Requirements

- `matplotlib` - For PDF generation
- `python-pptx` - For PowerPoint generation
- `Pillow` - For image processing
