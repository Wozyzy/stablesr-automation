import os
import argparse
import re
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages

def parse_args():
    parser = argparse.ArgumentParser(description="Generate PDF report from Cat Parameter Sweep.")
    parser.add_argument("--input_dir", type=str, required=True, help="Root directory containing sweep folders.")
    parser.add_argument("--output_pdf", type=str, default="cat_report.pdf", help="Path to save the output PDF.")
    return parser.parse_args()

def parse_folder_name(folder_name):
    # Format: steps_{s}_dec_{w}_color_{c}
    match = re.match(r"steps_(\d+)_dec_([\d\.]+)_color_(\w+)", folder_name)
    if match:
        steps = int(match.group(1))
        dec_w = float(match.group(2))
        color = match.group(3)
        return steps, dec_w, color
    return None, None, None

def find_hq_image(folder_path):
    if not os.path.exists(folder_path):
        return None
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "_lq" not in f:
            return os.path.join(folder_path, f)
    return None

def main():
    args = parse_args()
    
    # Data Structure: data[color][dec_w][steps] = image_path
    data = {}
    colors = set()
    dec_ws = set()
    steps_set = set()
    
    print(f"Scanning directory: {args.input_dir}")
    
    if not os.path.exists(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist.")
        return

    for folder_name in os.listdir(args.input_dir):
        folder_path = os.path.join(args.input_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        s, d, c = parse_folder_name(folder_name)
        if s is None:
            continue
            
        hq_path = find_hq_image(folder_path)
        if hq_path:
            if c not in data:
                data[c] = {}
            if d not in data[c]:
                data[c][d] = {}
            data[c][d][s] = hq_path
            
            colors.add(c)
            dec_ws.add(d)
            steps_set.add(s)

    sorted_colors = sorted(list(colors))
    sorted_dec_ws = sorted(list(dec_ws))
    sorted_steps = sorted(list(steps_set))
    
    print(f"Colors: {sorted_colors}")
    print(f"Dec Ws: {sorted_dec_ws}")
    print(f"Steps: {sorted_steps}")

    with PdfPages(args.output_pdf) as pdf:
        for color in sorted_colors:
            # Create Figure for this Color
            # Rows = Dec W
            # Cols = Steps
            
            num_rows = len(sorted_dec_ws)
            num_cols = len(sorted_steps)
            
            if num_rows == 0 or num_cols == 0:
                continue
                
            fig_width = 3 * num_cols
            fig_height = 3.5 * num_rows
            
            fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height), squeeze=False)
            
            fig.suptitle(f"Color Fix: {color.upper()}", fontsize=24, fontweight='bold', y=0.98)
            
            for r, dec_w in enumerate(sorted_dec_ws):
                for c, steps in enumerate(sorted_steps):
                    ax = axes[r, c]
                    
                    img_path = data.get(color, {}).get(dec_w, {}).get(steps)
                    
                    if img_path:
                        img = Image.open(img_path)
                        ax.imshow(img)
                        ax.set_xlabel(f"{img.width}x{img.height}", fontsize=10)
                    else:
                        ax.text(0.5, 0.5, "Missing", ha='center', va='center')
                        
                    ax.set_xticks([])
                    ax.set_yticks([])
                    
                    # Row Label (Dec W)
                    if c == 0:
                        ax.set_ylabel(f"Dec W: {dec_w}", fontsize=14, fontweight='bold', rotation=90, labelpad=10)
                        
                    # Column Label (Steps) - Only top row
                    if r == 0:
                        ax.set_title(f"Steps: {steps}", fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.subplots_adjust(top=0.92)
            pdf.savefig(fig)
            plt.close(fig)
            print(f"Added page: {color.upper()}")

    print(f"PDF Report saved to: {args.output_pdf}")

if __name__ == "__main__":
    main()
