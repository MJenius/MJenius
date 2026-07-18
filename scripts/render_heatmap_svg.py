import os
import sys
import json
from datetime import datetime, timedelta

def main():
    json_path = "data/contributions.json"
    output_path = "contrib-heatmap.svg"
    
    if not os.path.exists(json_path):
        print(f"Error: JSON file '{json_path}' not found. Run fetch_contributions.py first.")
        sys.exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    days = data["days"]
    total = data["total"]
    current_streak = data["current_streak"]
    longest_streak = data["longest_streak"]
    best_day = data["best_day"]
    
    if not days:
        print("Error: No day data found in JSON.")
        sys.exit(1)
        
    # Convert dates to datetime objects
    day_objs = []
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        day_objs.append({
            "date": dt,
            "level": d["level"],
            "count": d["count"],
            "date_str": d["date"]
        })
        
    # Sort chronologically
    day_objs = sorted(day_objs, key=lambda x: x["date"])
    min_date = day_objs[0]["date"]
    
    # Calculate the Sunday of the first week of the calendar
    first_sunday = min_date - timedelta(days=(min_date.weekday() + 1) % 7)
    
    # Check if static rendering is requested
    is_static = os.environ.get("STATIC") == "1"
    
    # SVG parameters
    svg_width = 860
    svg_height = 200
    grid_x_start = 65
    grid_y_start = 60
    box_size = 10
    gap = 3
    step = box_size + gap # 13
    
    PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
    # 0: none, 1: low, 2: medium, 3: high, 4: very high, 5: neon best day
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    
    # CSS Styles
    svg.append('  <style>')
    svg.append('    .text-label {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append('      font-size: 9px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .window-title {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append('      font-size: 11px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .stats-text {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;')
    svg.append('      font-size: 10px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .stats-highlight {')
    svg.append('      fill: #58a6ff;')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    
    if not is_static:
        svg.append('    .day {')
        svg.append('      opacity: 0;')
        svg.append('      animation: slideDown 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;')
        svg.append('    }')
        svg.append('    @keyframes slideDown {')
        svg.append('      from {')
        svg.append('        opacity: 0;')
        svg.append('        transform: translateY(-4px);')
        svg.append('      }')
        svg.append('      to {')
        svg.append('        opacity: 1;')
        svg.append('        transform: translateY(0);')
        svg.append('      }')
        svg.append('    }')
        
        # Generate cell stagger classes
        # Col ranges 0 to 52, row ranges 0 to 6. Max (col+row) = 58
        for col in range(53):
            for row in range(7):
                delay = (col + row) * 0.015 + 0.1
                svg.append(f'    .d-{col}-{row} {{ animation-delay: {delay:.3f}s; }}')
    else:
        svg.append('    .day {')
        svg.append('      opacity: 1;')
        svg.append('    }')
        
    svg.append('  </style>')
    
    # Background card
    svg.append(f'  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="8" fill="#0d1117" stroke="#30363d" stroke-width="1" />')
    
    # Window controls (macOS style window control dots)
    svg.append('  <circle cx="20" cy="20" r="5" fill="#ff5f56" />')
    svg.append('  <circle cx="36" cy="20" r="5" fill="#ffbd2e" />')
    svg.append('  <circle cx="52" cy="20" r="5" fill="#27c93f" />')
    svg.append(f'  <text x="72" y="24" class="window-title">mjenius@github: ~/contributions.sh</text>')
    svg.append(f'  <line x1="0" y1="40" x2="{svg_width}" y2="40" stroke="#30363d" stroke-width="1" />')
    
    # Month Labels
    seen_months = set()
    month_y = 50
    for d in day_objs:
        col = (d["date"] - first_sunday).days // 7
        if col >= 53:
            continue
        month_key = d["date"].strftime("%b %Y")
        if month_key not in seen_months:
            seen_months.add(month_key)
            month_name = d["date"].strftime("%b")
            label_x = grid_x_start + col * step
            svg.append(f'  <text x="{label_x}" y="{month_y}" class="text-label">{month_name}</text>')
            
    # Day of Week Labels (left aligned, only labeling Mon, Wed, Fri to avoid clutter)
    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in day_labels.items():
        label_y = grid_y_start + row * step + 9
        svg.append(f'  <text x="50" y="{label_y}" class="text-label" text-anchor="end">{label}</text>')
        
    # Render Grid Cells
    for d in day_objs:
        days_diff = (d["date"] - first_sunday).days
        col = days_diff // 7
        row = days_diff % 7
        
        if col >= 53 or row >= 7:
            continue
            
        x = grid_x_start + col * step
        y = grid_y_start + row * step
        
        # Color mapping
        color = PALETTE[d["level"]]
        # If it's the best day, give it the level 5 neon green
        if d["date_str"] == best_day["date"] and d["count"] > 0:
            color = PALETTE[5]
            
        anim_class = f' d-{col}-{row}' if not is_static else ''
        tooltip_str = f'{d["count"]} contributions on {d["date_str"]}'
        
        svg.append(f'  <rect class="day{anim_class}" x="{x}" y="{y}" width="{box_size}" height="{box_size}" rx="2" ry="2" fill="{color}">')
        svg.append(f'    <title>{tooltip_str}</title>')
        svg.append('  </rect>')
        
    # Legend (Less -> More)
    legend_y = 165
    legend_text_y = legend_y + 9
    svg.append(f'  <text x="645" y="{legend_text_y}" class="text-label" text-anchor="end">Less</text>')
    for i, color in enumerate(PALETTE[:5]):
        lx = 655 + i * 13
        svg.append(f'  <rect x="{lx}" y="{legend_y}" width="{box_size}" height="{box_size}" rx="2" ry="2" fill="{color}" />')
    svg.append(f'  <text x="725" y="{legend_text_y}" class="text-label">More</text>')
    
    # Stats Footer (left aligned at grid start)
    footer_y = legend_text_y
    stats_msg = (
        f'Total: <tspan class="stats-highlight">{total:,}</tspan> contributions | '
        f'Streak: <tspan class="stats-highlight">{current_streak}</tspan> days '
        f'(longest: <tspan class="stats-highlight">{longest_streak}</tspan> days)'
    )
    svg.append(f'  <text x="{grid_x_start}" y="{footer_y}" class="stats-text">{stats_msg}</text>')
    
    svg.append('</svg>')
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Heatmap SVG successfully generated and saved to {output_path}")

if __name__ == "__main__":
    main()
