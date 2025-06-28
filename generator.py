# generator.py

import os
import shutil
import markdown
import datetime
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# ---------- CONFIG ----------
CONTENT_DIR = "content"
OUTPUT_DIR = "docs"  # formerly "site"
TEMPLATE_DIR = "templates"
ARTICLE_OUT_DIR = os.path.join(OUTPUT_DIR, "articles")
ASSETS_SRC = "assets"
ASSETS_DEST = os.path.join(OUTPUT_DIR, "assets")

# ---------- INIT ----------
md = markdown.Markdown(extensions=['meta'])
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def parse_article(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    if raw.startswith('---'):
        frontmatter, body = raw.split('---', 2)[1:]
        metadata = yaml.safe_load(frontmatter.strip())
    else:
        metadata = {}
        body = raw
    html = markdown.markdown(body)
    return metadata, html

def generate_article_pages(articles):
    os.makedirs(ARTICLE_OUT_DIR, exist_ok=True)
    template = env.get_template("article.html")
    for article in articles:
        html = template.render(article=article)
        filename = f"{article['slug']}.html"
        with open(os.path.join(ARTICLE_OUT_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(html)

def generate_index(articles):
    template = env.get_template("index.html")
    html = template.render(articles=articles)
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)

def generate_archive(articles):
    template = env.get_template("archive.html")
    os.makedirs(ARTICLE_OUT_DIR, exist_ok=True)
    html = template.render(articles=articles)
    with open(os.path.join(ARTICLE_OUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)

def clean_output():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Preserve CNAME file
    if os.path.exists("CNAME"):
        shutil.copy("CNAME", os.path.join(OUTPUT_DIR, "CNAME"))

    # Copy static assets
    if os.path.exists(ASSETS_SRC):
        shutil.copytree(ASSETS_SRC, ASSETS_DEST)

def slugify(title):
    return title.lower().replace(" ", "-").replace(",", "").replace("'", "").replace(".", "").replace("?", "")

def main():
    clean_output()
    articles = []
    for md_file in sorted(Path(CONTENT_DIR).glob("*.md"), reverse=True):
        metadata, content_html = parse_article(md_file)
        if 'title' not in metadata or 'date' not in metadata:
            continue  # skip invalid articles
        slug = slugify(metadata['title'])
        articles.append({
            'title': metadata['title'],
            'date': metadata['date'],
            'summary': metadata.get('summary', ""),
            'slug': slug,
            'content': content_html
        })
    generate_article_pages(articles)
    generate_index(articles)
    generate_archive(articles)

if __name__ == "__main__":
    main()
