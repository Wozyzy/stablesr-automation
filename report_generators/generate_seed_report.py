import os
import argparse
import re
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages

def parse_args():
    parser = argparse.ArgumentParser(description="Generate PDF report from StableSR Seed Sweep.")
    parser.add_argument("--input_dir", type=str, required=True, help="Root directory containing fixed/random folders.")
    parser.add_argument("--ref_dir", type=str, help="Directory containing reference input images (structure: ref_dir/128/img.png).")
    parser.add_argument("--output_pdf", type=str, default="seed_report.pdf", help="Path to save the output PDF.")
    return parser.parse_args()

def parse_folder_name(folder_name):
    # Expected format: base{res}_x{scale_str}
    match = re.match(r"base(\d+)_x(\d+)p(\d+)", folder_name)
    if match:
        res = int(match.group(1))
        scale = float(f"{match.group(2)}.{match.group(3)}")
        return res, scale
    return None, None

def find_hq_image(folder_path):
    if not os.path.exists(folder_path):
        return None
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "_lq" not in f:
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
    
    # Data Structure: data[mode][res][scale][run_index] = image_path
    data = {}
    modes = ["fixed", "random"]
    
    print(f"Scanning directory: {args.input_dir}")

    for mode in modes:
        mode_path = os.path.join(args.input_dir, mode)
        if not os.path.exists(mode_path):
            print(f"Warning: Mode directory '{mode}' not found.")
            continue
            
        data[mode] = {}
        
        for folder_name in os.listdir(mode_path):
            folder_path = os.path.join(mode_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            res, scale = parse_folder_name(folder_name)
            if res is None:
                continue
            
            if res not in data[mode]:
                data[mode][res] = {}
            if scale not in data[mode][res]:
                data[mode][res][scale] = {}
                
            # Scan runs
            for run_folder in os.listdir(folder_path):
                if not run_folder.startswith("run_"):
                    continue
                try:
                    run_idx = int(run_folder.split("_")[1])
                except ValueError:
                    continue
                    
                run_path = os.path.join(folder_path, run_folder)
                hq_img = find_hq_image(run_path)
                if hq_img:
                    data[mode][res][scale][run_idx] = hq_img

    # Generate PDF
    with PdfPages(args.output_pdf) as pdf:
        for mode in modes:
            if mode not in data:
                continue
                
            sorted_res = sorted(data[mode].keys())
            
            for res in sorted_res:
                sorted_scales = sorted(data[mode][res].keys())
                if not sorted_scales:
                    continue
                    
                # Determine max runs to set grid size (usually 5)
                max_runs = 5 
                
                # Create Figure for (Mode, Res)
                # Rows = Scales
                # Cols = 1 (Ref) + Runs
                num_rows = len(sorted_scales)
                num_cols = 1 + max_runs
                
                fig_width = 3 * num_cols
                fig_height = 3.5 * num_rows
                
                fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height), squeeze=False)
                
                # Main Title
                fig.suptitle(f"Mode: {mode.upper()} | Resolution: {res}", fontsize=20, fontweight='bold', y=0.98)
                
                # Find reference image for this resolution
                ref_img_path = find_ref_image(args.ref_dir, res)
                
                for r, scale in enumerate(sorted_scales):
                    # Plot Reference Image at Column 0
                    ax_ref = axes[r, 0]
                    if ref_img_path:
                        img = Image.open(ref_img_path)
                        ax_ref.imshow(img)
                        ax_ref.set_xlabel(f"{img.width}x{img.height}", fontsize=9)
                    else:
                        ax_ref.text(0.5, 0.5, "Ref Missing", ha='center', va='center')
                    ax_ref.set_xticks([])
                    ax_ref.set_yticks([])
                    
                    if r == 0:
                        ax_ref.set_title("Input", fontsize=14, fontweight='bold')
                    if r == 0 and 0 == 0: # Just to be consistent with loop below
                         pass

                    # Plot Runs at Columns 1..max_runs
                    for c in range(max_runs):
                        ax = axes[r, c + 1]
                        run_idx = c
                        
                        img_path = data[mode][res][scale].get(run_idx)
                        
                        if img_path:
                            img = Image.open(img_path)
                            ax.imshow(img)
                            ax.set_xlabel(f"{img.width}x{img.height}", fontsize=9)
                        else:
                            ax.text(0.5, 0.5, "Missing", ha='center', va='center')
                            
                        ax.set_xticks([])
                        ax.set_yticks([])
                        
                        # Row Label (Scale) - Only on the very first column (Ref column)
                        if c == -1: # Never true here, handled below
                            pass
                            
                        # Column Label (Run) - Only top row
                        if r == 0:
                            ax.set_title(f"Run {run_idx+1}", fontsize=14, fontweight='bold')

                    # Set Row Label on the Reference Column
                    axes[r, 0].set_ylabel(f"Scale {scale}x", fontsize=14, fontweight='bold', rotation=90, labelpad=10)

                plt.tight_layout()
                plt.subplots_adjust(top=0.92) # Make room for suptitle
                pdf.savefig(fig)
                plt.close(fig)
                print(f"Added page: {mode.upper()} - {res}")

    print(f"PDF Report saved to: {args.output_pdf}")

if __name__ == "__main__":
    main()
