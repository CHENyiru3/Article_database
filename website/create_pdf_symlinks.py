#!/usr/bin/env python3
"""Create symlinks for PDFs in the static directory."""

import os
from pathlib import Path

BASE_DIR = Path("/Users/chen_yiru/Desktop/home/Academic_thing/Collection_by_year/Academic_Database")
STATIC_PDFS = BASE_DIR / "website" / "static" / "pdfs"

def create_symlinks():
    # Create static/pdfs directory
    STATIC_PDFS.mkdir(parents=True, exist_ok=True)

    categories = ["Biological", "CS_AI", "Comp_Bio/Analysis", "Comp_Bio/Modelling"]

    for category in categories:
        src_dir = BASE_DIR / category
        if not src_dir.exists():
            print(f"Warning: {src_dir} does not exist")
            continue

        # Create category directory in static/pdfs
        dst_dir = STATIC_PDFS / category
        dst_dir.mkdir(parents=True, exist_ok=True)

        # Create symlinks for each PDF
        for pdf_file in src_dir.glob("*.pdf"):
            dst_path = dst_dir / pdf_file.name
            if dst_path.exists() or dst_path.is_symlink():
                print(f"  [SKIP] {pdf_file.name}")
            else:
                try:
                    os.symlink(pdf_file, dst_path)
                    print(f"  [LINK] {category}/{pdf_file.name}")
                except Exception as e:
                    print(f"  [ERROR] {pdf_file.name}: {e}")

    print(f"\nSymlinks created in {STATIC_PDFS}")

if __name__ == "__main__":
    create_symlinks()
