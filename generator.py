#!/usr/bin/env python3
import os
import datetime
import click
from jinja2 import Environment, FileSystemLoader
from fetcher import BookFetcher

script_dir = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader(script_dir))
tmpl = env.get_template('template.md.j2')

@click.argument("isbn_list", nargs=-1)
@click.command()
def generate(isbn_list):
    # If no ISBNs were passed as arguments, prompt interactively
    if not isbn_list:
        isbn_input = click.prompt("Enter ISBN(s), separated by spaces")
        #isbn_input = '0679728899'
        #isbn_list = isbn_input.split()

    # Initialize fetcher and ensure working directory
    fetcher = BookFetcher()
    os.chdir(script_dir)
    os.makedirs("_posts", exist_ok=True)

    for isbn in isbn_list:
        meta = fetcher.fetch_by_isbn(isbn)
        # Skip ISBNs with no metadata
        if not meta.get("title"):
            click.echo(f"⚠️  No data found for ISBN {isbn}, skipping.")
            continue

        # Render post using Jinja2 template
        date = datetime.date.today().isoformat()
        rendered = tmpl.render(
            title=meta.get("title", ""),
            authors=meta.get("authors", []),
            cover=meta.get("cover", ""),
            description=meta.get("description", ""),
            first_sentence=meta.get("first_sentence", "")
        )
        filename = f"_posts/{date}-{isbn}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(rendered)

        click.echo(f"Generated {filename}")

if __name__ == "__main__":
    generate()