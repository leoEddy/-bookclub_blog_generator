#!/usr/bin/env python3
import os
import datetime
import click
import frontmatter
from fetcher import BookFetcher

@click.command()
def generate():
    # Prompt for ISBN(s)
    isbn_input = click.prompt("Enter ISBN(s), separated by spaces")
    isbn_list = isbn_input.split()

    # Initialize fetcher and ensure working directory
    fetcher = BookFetcher()
    script_dir = os.path.dirname(__file__)
    os.chdir(script_dir)
    os.makedirs("_posts", exist_ok=True)

    for isbn in isbn_list:
        meta = fetcher.fetch_by_isbn(isbn)
        # Skip ISBNs with no metadata
        if not meta.get("title"):
            click.echo(f"⚠️  No data found for ISBN {isbn}, skipping.")
            continue

        date = datetime.date.today().isoformat()
        post = frontmatter.Post(
            content=meta.get("description", ""),
            **{
                "title": meta.get("title", ""),
                "date": date,
                "original_publication_date": meta.get("original_publication_date", ""),
                "author": meta.get("authors", []),
                "cover_image": meta.get("cover", "")
            }
        )
        content = frontmatter.dumps(post)
        filename = f"_posts/{date}-{isbn}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        click.echo(f"Generated {filename}")

if __name__ == "__main__":
    generate()