"""CSV exporter with UTF-8 BOM support for Excel compatibility."""

import csv
import os

from config import OUTPUT_DIR


FIELDNAMES = ["stt", "title", "content", "date", "forum", "post_url", "content_type"]


def export_to_csv(posts: list[dict], filename: str) -> str:
    """Export posts to CSV with UTF-8 BOM.
    
    Args:
        posts: List of post dicts
        filename: Output filename (without path)
    
    Returns:
        Full path to the created CSV file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        
        for i, post in enumerate(posts, 1):
            row = {**post, "stt": i}
            writer.writerow(row)
    
    return filepath


def generate_filename(username: str, userid: str) -> str:
    """Generate output filename from user info."""
    safe_name = username.replace(" ", "_").replace("/", "_")
    return f"{safe_name}_{userid}_posts.csv"


def generate_combined_filename() -> str:
    """Generate filename for combined multi-user results."""
    return "combined_posts.csv"
