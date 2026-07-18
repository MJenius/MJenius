import os
import sys
from PIL import Image

def main():
    image_path = "image.png"
    output_path = "logo.svg"
    
    if not os.path.exists(image_path):
        print(f"Error: Logo file '{image_path}' not found in the workspace root.")
        sys.exit(1)
        
    print(f"Loading logo image from: {image_path}")
    img = Image.open(image_path)
    
    # 1. Monospace character aspect ratio correction (width / height of monospace char ~0.60)
    target_width = 110
    target_height = 68  # 68 rows * 5px row_height = 340px text height
    
    # Resize the image to the target grid
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    img_gray = img_resized.convert("L")
    
    # 2. Extract stroke pixels and normalize contrast to span the ASCII ramp
    import numpy as np
    pixel_values = np.array(img_gray).flatten().tolist()
    stroke_pixels = [p for p in pixel_values if p > 15]
    if stroke_pixels:
        min_val = min(stroke_pixels)
        max_val = max(stroke_pixels)
        if max_val > min_val:
            # Map logo strokes to range 40-255, keep background at 0
            img_gray = img_gray.point(lambda p: int((p - min_val) / (max_val - min_val) * 215 + 40) if p > 15 else 0)
            
    pixels = img_gray.load()
    
    # 3. Ramp selection: bright (dense) to dark (sparse)
    # Background (0) maps to space, bright strokes map to dense characters
    RAMP = " .`:-=+*cs#%@"
    
    ascii_rows = []
    for y in range(target_height):
        row_chars = []
        for x in range(target_width):
            brightness = pixels[x, y]
            # Map brightness directly: 0 -> space, 255 -> @
            idx = int(brightness / 256.0 * len(RAMP))
            row_chars.append(RAMP[idx])
        
        # XML escape special characters
        row_str = "".join(row_chars)
        row_str = row_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        ascii_rows.append(row_str)
        
    # SVG parameters
    svg_width = 370
    row_height = 5.0
    font_size = 5.0
    
    padding_top = 55
    padding_bottom = 15
    svg_height = padding_top + target_height * row_height + padding_bottom  # 55 + 340 + 15 = 410px
    
    is_static = os.environ.get("STATIC") == "1"
    
    # Stagger parameters
    start_delay = 0.05
    stagger_delay = 0.025
    row_dur = 0.25
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    
    # CSS Styles
    svg.append('  <style>')
    svg.append('    .ascii-text {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append(f'      font-size: {font_size}px;')
    svg.append(f'      line-height: {row_height}px;')
    svg.append('      font-weight: bold;')
    svg.append('      fill: #cbd5e1; /* slate-300 */')
    svg.append('      white-space: pre;')
    svg.append('    }')
    svg.append('    .window-title {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append('      font-size: 11px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('  </style>')
    
    # Definitions for ClipPaths and animations
    svg.append('  <defs>')
    if not is_static:
        for i in range(target_height):
            y_rect = padding_top + i * row_height - row_height + 1.0
            start = start_delay + i * stagger_delay
            svg.append(f'    <clipPath id="clip-{i}">')
            svg.append(f'      <rect x="0" y="{y_rect:.1f}" width="0" height="{row_height:.1f}">')
            svg.append(f'        <animate attributeName="width" from="0" to="{svg_width}" begin="{start:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />')
            svg.append('      </rect>')
            svg.append('    </clipPath>')
    svg.append('  </defs>')
    
    # Background card
    svg.append(f'  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="8" fill="#0d1117" stroke="#30363d" stroke-width="1" />')
    
    # Window controls (macOS style window control dots)
    svg.append('  <circle cx="20" cy="20" r="5" fill="#ff5f56" />')
    svg.append('  <circle cx="36" cy="20" r="5" fill="#ffbd2e" />')
    svg.append('  <circle cx="52" cy="20" r="5" fill="#27c93f" />')
    svg.append(f'  <text x="72" y="24" class="window-title">mjenius@github: ~/logo</text>')
    svg.append(f'  <line x1="0" y1="40" x2="{svg_width}" y2="40" stroke="#30363d" stroke-width="1" />')
    
    # Text lines
    for i, row in enumerate(ascii_rows):
        y_pos = padding_top + i * row_height
        clip_attr = f' clip-path="url(#clip-{i})"' if not is_static else ''
        svg.append(f'  <text x="12" y="{y_pos:.1f}" class="ascii-text" textLength="{svg_width - 24}" lengthAdjust="spacing"{clip_attr}>{row}</text>')
        
        # Cursor for each line (only if not static)
        if not is_static:
            start = start_delay + i * stagger_delay
            y_cursor = y_pos - font_size + 0.5
            svg.append(f'  <rect x="12" y="{y_cursor:.1f}" width="5" height="{font_size:.1f}" fill="#39d353" opacity="0">')
            svg.append(f'    <animate attributeName="x" from="12" to="{svg_width - 12}" begin="{start:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />')
            svg.append(f'    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.95;1" begin="{start:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />')
            svg.append('  </rect>')
            
    svg.append('</svg>')
    
    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"ASCII Logo SVG successfully generated and saved to {output_path}")
    print(f"Logo height: {svg_height}px (grid: {target_width}x{target_height})")

if __name__ == "__main__":
    main()
