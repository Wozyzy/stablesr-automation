import os
import argparse
import re
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages

def parse_args():
    parser = argparse.ArgumentParser(description="Generate PDF report from StableSR outputs (HQ Only).")
    parser.add_argument("--input_dir", type=str, required=True, help="Root directory containing the base{res}_x{scale} folders.")
    parser.add_argument("--ref_dir", type=str, help="Directory containing reference input images.")
    parser.add_argument("--output_pdf", type=str, default="report_hq.pdf", help="Path to save the output PDF.")
    return parser.parse_args()

def parse_folder_name(folder_name):
    # Expected format: base{res}_x{scale_str}
    # e.g., base128_x1p5 -> res=128, scale=1.5
    match = re.match(r"base(\d+)_x(\d+)p(\d+)", folder_name)
    if match:
        res = int(match.group(1))
        scale = float(f"{match.group(2)}.{match.group(3)}")
        return res, scale
    
    # Try format without 'p' decimal (e.g. x1)
    match = re.match(r"base(\d+)_x(\d+)", folder_name)
    if match:
        res = int(match.group(1))
        scale = float(match.group(2))
        return res, scale
        
    return None, None

def find_hq_image(folder_path):
    if not os.path.exists(folder_path):
        return None

    for f in os.listdir(folder_path):
        if not f.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        
        # Skip LQ images
        if "_lq" in f:
            continue
            
        # Found HQ image
        return os.path.join(folder_path, f)
            
    return None

def find_ref_image(ref_dir, res):
    if not ref_dir:
        return None
    
    # Look for folder ending with _{res} or just {res}
    target_folder = None
    if os.path.exists(os.path.join(ref_dir, str(res))):
        target_folder = os.path.join(ref_dir, str(res))
    else:
        # Search for folder ending with _{res}
        for d in os.listdir(ref_dir):
            if d.endswith(f"_{res}") and os.path.isdir(os.path.join(ref_dir, d)):
                target_folder = os.path.join(ref_dir, d)
                break
    
    if not target_folder:
        return None

    for f in os.listdir(target_folder):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            return os.path.join(target_folder, f)
    return None

def main():
    args = parse_args()
    
    data = {} # Key: scale, Value: {res: hq_path}
    resolutions = set()
    scales = set()

    print(f"Scanning directory: {args.input_dir}")
    
    if not os.path.exists(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist.")
        return

    for folder_name in os.listdir(args.input_dir):
        folder_path = os.path.join(args.input_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        res, scale = parse_folder_name(folder_name)
        if res is None:
            continue
            
        hq_path = find_hq_image(folder_path)
        
        if scale not in data:
            data[scale] = {}
        
        data[scale][res] = hq_path
        resolutions.add(res)
        scales.add(scale)

    sorted_resolutions = sorted(list(resolutions))
    sorted_scales = sorted(list(scales))
    
    print(f"Found Resolutions: {sorted_resolutions}")
    print(f"Found Scales: {sorted_scales}")
    
    if not sorted_scales:
        print("No matching folders found.")
        return

    # Setup Plot
    # Rows = Scales
    # Cols = Resolutions
    
    num_rows = len(sorted_scales)
    num_cols = len(sorted_resolutions)
    
    # Calculate figure size
    # Each cell now has 2 images (Ref + HQ)
    # Width needs to be doubled roughly
    fig_width = 6 * num_cols 
    fig_height = 4 * num_rows
    
    fig = plt.figure(figsize=(fig_width, fig_height))
    
    # Create a grid: Rows x Cols
    outer_grid = GridSpec(num_rows, num_cols, figure=fig, wspace=0.1, hspace=0.2)

    for r, scale in enumerate(sorted_scales):
        for c, res in enumerate(sorted_resolutions):
            # Create inner grid for the cell (1x2: Ref, HQ)
            try:
                inner_grid = outer_grid[r, c].subgridspec(1, 2, wspace=0.05)
            except AttributeError:
                from matplotlib.gridspec import GridSpecFromSubplotSpec
                inner_grid = GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_grid[r, c], wspace=0.05)
            
            hq_path = data[scale].get(res)
            ref_path = find_ref_image(args.ref_dir, res)
            
            # Plot Reference (Left)
            ax_ref = fig.add_subplot(inner_grid[0, 0])
            if ref_path:
                img = Image.open(ref_path)
                ax_ref.imshow(img)
                ax_ref.set_xlabel(f"{img.width}x{img.height}", fontsize=9)
                ax_ref.set_title("Input", fontsize=10)
            else:
                ax_ref.text(0.5, 0.5, "Ref Missing", ha='center', va='center')
            ax_ref.set_xticks([])
            ax_ref.set_yticks([])
            
            # Plot HQ (Right)
            ax_hq = fig.add_subplot(inner_grid[0, 1])
            if hq_path:
                img = Image.open(hq_path)
                ax_hq.imshow(img)
                ax_hq.set_xlabel(f"{img.width}x{img.height}", fontsize=9)
                ax_hq.set_title("Output", fontsize=10)
            else:
                ax_hq.text(0.5, 0.5, "Missing", ha='center', va='center')
            ax_hq.set_xticks([])
            ax_hq.set_yticks([])
            
            # Column Header (Resolution) - Only on top row
            if r == 0:
                # Place text above the pair
                ax_ref.text(1.05, 1.2, f"Resolution {res}", transform=ax_ref.transAxes, ha='center', fontsize=16, fontweight='bold')

            # Row Label (Scale) - Only on left column
            if c == 0:
                ax_ref.set_ylabel(f"Scale {scale}x", fontsize=16, fontweight='bold', rotation=90, labelpad=20)

    plt.tight_layout()
    plt.savefig(args.output_pdf, dpi=150, bbox_inches='tight')
    print(f"PDF Report saved to: {args.output_pdf}")

if __name__ == "__main__":
    main()
