#!/usr/bin/env python3
"""
Script to migrate articles from Log.md to Hugo content files.

Usage:
    python migrate_log_to_hugo.py [--log-file LOG.md] [--output-dir website/content/articles]

The script parses Log.md entries and creates individual Markdown files
with YAML frontmatter for each article.
"""

import re
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def parse_log_md(log_content: str) -> list[dict]:
    """Parse Log.md content and extract article entries."""
    articles = []

    # Pattern to match article entries in Log.md
    # Looks for ### [filename.pdf](path) followed by bullet points
    pattern = r'### \[([^\]]+)\]\(([^)]+)\)\s*\n([^#]+?)(?=\n### |\n---|\Z)'

    matches = re.findall(pattern, log_content, re.DOTALL)

    for match in matches:
        filename, path, content = match

        # Extract metadata from bullet points
        metadata = {}
        bullet_pattern = r'- \*\*([^*]+)\*\*:\s*(.+?)(?=\n- \*\*|\n\s*\n|$)'
        bullet_matches = re.findall(bullet_pattern, content, re.DOTALL)

        for key, value in bullet_matches:
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()

            if key == 'key_topics':
                # Parse comma-separated topics
                topics = [t.strip().strip('[]') for t in value.split(',')]
                metadata['tags'] = topics
            elif key == 'date_organized':
                metadata['date_organized'] = value
            else:
                metadata[key] = value

        # Extract year from filename if not in metadata
        year = metadata.get('year')
        if not year:
            year_match = re.search(r'(\d{4})', filename)
            if year_match:
                year = year_match.group(1)
                metadata['year'] = year

        # Determine category from path
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 2:
            category = path_parts[0]
            subcategory = path_parts[1] if len(path_parts) > 2 else None

            if category == 'Comp_Bio':
                if subcategory:
                    metadata['categories'] = [f'comp_bio/{subcategory.lower()}']
                else:
                    metadata['categories'] = ['comp_bio']
            else:
                metadata['categories'] = [category.lower()]
        else:
            metadata['categories'] = ['others']

        # Generate PDF URL
        metadata['pdf_url'] = f'/pdfs/{path.strip()}'

        # Create slug from filename
        slug = filename.replace('.pdf', '').lower().replace(' ', '-').replace('_', '-')
        metadata['slug'] = slug

        articles.append({
            'filename': filename,
            'title': filename.replace('.pdf', '').replace('_', ' '),
            'slug': slug,
            'metadata': metadata
        })

    return articles


def create_frontmatter(article: dict, include_content: bool = False) -> str:
    """Create YAML frontmatter for a Hugo article."""
    meta = article['metadata']

    lines = [
        '---',
        f"title: \"{article['title']}\"",
        f"date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}",
        'draft: false',
    ]

    # Add categories
    categories = meta.get('categories', [])
    if categories:
        lines.append(f"categories: [{', '.join(f'\"{c}\"' for c in categories)}]")

    # Add tags
    tags = meta.get('tags', [])
    if tags:
        lines.append(f"tags: [{', '.join(f'\"{t}\"' for t in tags)}]")

    # Add year
    if meta.get('year'):
        lines.append(f"year: {meta['year']}")

    # Add PDF URL
    if meta.get('pdf_url'):
        lines.append(f'pdf_url: "{meta["pdf_url"]}"')

    # Add source
    if meta.get('source'):
        lines.append(f'source: "{meta["source"]}"')

    # Add description/summary
    if meta.get('summary'):
        # Handle multiline summary
        lines.append('description: |')
        for line in meta['summary'].split('\n'):
            lines.append(f'  {line.strip()}')

    lines.append('---')

    # Add minimal content body (Hugo requires content after frontmatter)
    summary = meta.get('summary', '').strip()
    if summary:
        lines.append('')
        lines.append(summary)
        lines.append('')
    else:
        lines.append('')
        lines.append(f"_{article['title']}_ - A research article on {', '.join(tags[:3]) if tags else 'various topics'}.")
        lines.append('')

    return '\n'.join(lines)


def migrate_articles(log_file: str, output_dir: str, dry_run: bool = True):
    """Migrate articles from Log.md to Hugo content files."""
    # Read Log.md
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # Parse articles
    articles = parse_log_md(log_content)

    print(f"\nFound {len(articles)} articles to migrate.\n")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for article in articles:
        slug = article['slug']
        meta = article['metadata']

        # Create filename without year prefix (year prefixes cause Hugo processing issues)
        filename = f"{slug}.md"
        filepath = output_path / filename

        # Check if file already exists
        if filepath.exists():
            print(f"  [SKIP] {filename} (already exists)")
            skipped += 1
            continue

        # Create content
        frontmatter = create_frontmatter(article)

        if dry_run:
            print(f"  [DRY-RUN] Would create: {filename}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
            print(f"  [CREATE] {filename}")

        created += 1

    print(f"\n{'Would create' if dry_run else 'Created'} {created} files.")
    if skipped > 0:
        print(f"Skipped {skipped} existing files.")

    return created, skipped


def main():
    parser = argparse.ArgumentParser(
        description='Migrate articles from Log.md to Hugo content files'
    )
    parser.add_argument(
        '--log-file', '-l',
        default='Log.md',
        help='Path to Log.md file (default: Log.md)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='website/content/articles',
        help='Output directory for Hugo content files (default: website/content/articles)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without creating files'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing files'
    )

    args = parser.parse_args()

    # Check if log file exists
    if not os.path.exists(args.log_file):
        print(f"Error: Log file '{args.log_file}' not found.")
        return 1

    print(f"Migrating articles from {args.log_file}")
    print(f"Output directory: {args.output_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (no files will be created)\n")

    created, skipped = migrate_articles(
        args.log_file,
        args.output_dir,
        dry_run=args.dry_run or not args.force
    )

    if not args.dry_run and not args.force:
        print("\nTo actually create files, run with --force or without --dry-run")

    return 0


if __name__ == '__main__':
    exit(main())
