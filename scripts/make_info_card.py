import os
import sys
from PIL import Image

def main():
    prepped_path = "Formal Profile Photo.png"
    output_path = "info-card.svg"
    
    # Default fallback height
    svg_height = 460
    
    # Calculate exact height to match the logo image aspect ratio
    logo_path = "image.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            img_w, img_h = img.size
            img_aspect = img_w / img_h
            img_w_svg = 340
            img_h_svg = int(img_w_svg / img_aspect)
            padding_top = 55
            padding_bottom = 15
            svg_height = padding_top + img_h_svg + padding_bottom
            print(f"Calculated height to match logo: {svg_height}px")
        except Exception as e:
            print(f"Warning: Failed to calculate height from logo: {e}. Using fallback: {svg_height}px")
    elif os.path.exists(prepped_path):
        try:
            img = Image.open(prepped_path)
            char_aspect = 0.50
            target_width = 110
            img_w, img_h = img.size
            img_aspect = img_w / img_h
            target_height = int(target_width / (img_aspect / char_aspect))
            row_height = 5.0
            padding_top = 55
            padding_bottom = 15
            svg_height = int(padding_top + target_height * row_height + padding_bottom)
            print(f"Calculated height to match ASCII portrait: {svg_height}px")
        except Exception as e:
            print(f"Warning: Failed to calculate height from photo: {e}. Using fallback: {svg_height}px")
            
    is_static = os.environ.get("STATIC") == "1"
    
    # Card details
    details = [
        {"key": "OS", "val": "Windows 11 / Ubuntu 22.04 LTS"},
        {"key": "Host", "val": "MJenius Local Workspace"},
        {"key": "Kernel", "val": "Python 3.11 / Node.js v20"},
        {"key": "Uptime", "val": "Active and coding daily"},
        {"key": "Shell", "val": "powershell.exe / zsh"},
        {"key": "Role", "val": "AI &amp; Full-Stack Engineer"},
        {"key": "Stack", "val": "Python, Next.js, React, FastAPI, Docker"},
        {"key": "Focus", "val": "Applied ML, Computer Vision, AI Agents"},
        {"key": "Links", "val": "mjenius.github.io/Portfolio/"},
        {"key": "Status", "val": "Building production AI systems"}
    ]
    
    # Build lines list
    lines = []
    # Title line
    lines.append({"type": "title", "val": "mjenius@github"})
    # Separator
    lines.append({"type": "sep", "val": "--------------"})
    # Fields
    for d in details:
        lines.append({"type": "field", "key": d["key"], "val": d["val"]})
        
    svg_width = 490
    
    # SVG construction
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    
    # CSS Styles
    svg.append('  <style>')
    svg.append('    .card-text {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append('      font-size: 13.5px;')
    svg.append('      fill: #e6edf3;')
    svg.append('    }')
    svg.append('    .window-title {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append('      font-size: 11px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .title-line {')
    svg.append('      fill: #58a6ff; /* soft terminal blue */')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    svg.append('    .sep-line {')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .key-text {')
    svg.append('      fill: #79c0ff; /* cyan-blue key */')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    svg.append('    .val-text {')
    svg.append('      fill: #c9d1d9; /* light gray val */')
    svg.append('    }')
    
    # Add animations if not static
    if not is_static:
        svg.append('    @keyframes fadeInUp {')
        svg.append('      from {')
        svg.append('        opacity: 0;')
        svg.append('        transform: translateY(8px);')
        svg.append('      }')
        svg.append('      to {')
        svg.append('        opacity: 1;')
        svg.append('        transform: translateY(0);')
        svg.append('      }')
        svg.append('    }')
        svg.append('    .animated-line {')
        svg.append('      opacity: 0;')
        svg.append('      animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;')
        svg.append('      transform-box: fill-box;')
        svg.append('      transform-origin: center;')
        svg.append('    }')
        
        # Stagger animations
        for i in range(len(lines)):
            delay = 0.15 + i * 0.08
            svg.append(f'    .line-{i} {{ animation-delay: {delay:.2f}s; }}')
            
    svg.append('  </style>')
    
    # Background card
    svg.append(f'  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="8" fill="#0d1117" stroke="#30363d" stroke-width="1" />')
    
    # Window controls (macOS style window control dots)
    svg.append('  <circle cx="20" cy="20" r="5" fill="#ff5f56" />')
    svg.append('  <circle cx="36" cy="20" r="5" fill="#ffbd2e" />')
    svg.append('  <circle cx="52" cy="20" r="5" fill="#27c93f" />')
    svg.append(f'  <text x="72" y="24" class="window-title">mjenius@github: ~/profile.sh</text>')
    svg.append(f'  <line x1="0" y1="40" x2="{svg_width}" y2="40" stroke="#30363d" stroke-width="1" />')
    
    # Terminal text container
    content_y_start = 70
    line_spacing = 23
    
    svg.append(f'  <g>')
    for i, line in enumerate(lines):
        y_pos = content_y_start + i * line_spacing
        anim_class = f' animated-line line-{i}' if not is_static else ''
        
        if line["type"] == "title":
            svg.append(f'    <text x="25" y="{y_pos}" class="card-text title-line{anim_class}">{line["val"]}</text>')
        elif line["type"] == "sep":
            svg.append(f'    <text x="25" y="{y_pos}" class="card-text sep-line{anim_class}">{line["val"]}</text>')
        elif line["type"] == "field":
            svg.append(f'    <text x="25" y="{y_pos}" class="card-text{anim_class}">')
            svg.append(f'      <tspan class="key-text">{line["key"]}</tspan>')
            svg.append(f'      <tspan fill="#8b949e">: </tspan>')
            svg.append(f'      <tspan class="val-text">{line["val"]}</tspan>')
            svg.append(f'    </text>')
    svg.append('  </g>')
    
    svg.append('</svg>')
    
    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Info card SVG successfully generated and saved to {output_path}")

if __name__ == "__main__":
    main()
