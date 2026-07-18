import os
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

def parse_tooltip_text(text):
    text = text.strip()
    if text.startswith("No contributions"):
        return 0
    match = re.match(r"^([0-9,]+)\s+contribution", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0

def main():
    username = "MJenius"
    url = f"https://github.com/users/{username}/contributions"
    print(f"Fetching contribution calendar for user: {username} from {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching contribution calendar: {e}")
        sys.exit(1)
        
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all ContributionCalendar-day tds
    tds = soup.find_all("td", class_="ContributionCalendar-day")
    if not tds:
        print("Error: Could not find contribution cells in the response. GitHub's HTML structure might have changed.")
        sys.exit(1)
        
    days = []
    print(f"Found {len(tds)} contribution days. Extracting data...")
    
    for td in tds:
        date_str = td.get("data-date")
        level_str = td.get("data-level")
        td_id = td.get("id")
        
        if not date_str:
            continue
            
        level = int(level_str) if level_str else 0
        
        # Scrape counts from corresponding tooltips
        count = 0
        if td_id:
            tooltip = soup.find("tool-tip", {"for": td_id})
            if tooltip:
                tooltip_text = tooltip.get_text()
                count = parse_tooltip_text(tooltip_text)
            else:
                # Self-healing fallback mapping if tooltip not found
                level_to_count = {0: 0, 1: 1, 2: 4, 3: 8, 4: 12}
                count = level_to_count.get(level, 0)
        else:
            # Fallback if no td_id
            level_to_count = {0: 0, 1: 1, 2: 4, 3: 8, 4: 12}
            count = level_to_count.get(level, 0)
            
        days.append({
            "date": date_str,
            "level": level,
            "count": count
        })
        
    # Sort days chronologically
    days_sorted = sorted(days, key=lambda x: x["date"])
    
    # Compute stats
    total_contributions = sum(d["count"] for d in days_sorted)
    
    # Streaks
    longest_streak = 0
    temp_streak = 0
    best_day = {"date": "", "count": 0}
    
    for d in days_sorted:
        # Longest streak
        if d["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
            
        # Best day
        if d["count"] > best_day["count"]:
            best_day = {"date": d["date"], "count": d["count"]}
            
    # Current streak
    current_streak = 0
    idx = len(days_sorted) - 1
    if idx >= 0:
        start_idx = idx
        # If today has 0, but yesterday has > 0, count from yesterday
        if days_sorted[idx]["count"] == 0:
            if idx > 0 and days_sorted[idx-1]["count"] > 0:
                start_idx = idx - 1
                
        # Count backwards
        for i in range(start_idx, -1, -1):
            if days_sorted[i]["count"] > 0:
                current_streak += 1
            else:
                break
                
    # Monthly totals
    monthly_totals = {}
    for d in days_sorted:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        key = dt.strftime("%b %Y") # e.g. "Jul 2025"
        monthly_totals[key] = monthly_totals.get(key, 0) + d["count"]
        
    data = {
        "username": username,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "days": days_sorted
    }
    
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    
    output_path = "data/contributions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Scraped and analyzed contributions successfully. Saved stats to {output_path}")
    print(f"Total Contributions: {total_contributions}")
    print(f"Current Streak: {current_streak} days")
    print(f"Longest Streak: {longest_streak} days")
    print(f"Best Day: {best_day['date']} ({best_day['count']} contributions)")

if __name__ == "__main__":
    main()
