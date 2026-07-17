#!/usr/bin/env python3
"""
Chinese Idiom Dictionary — Static Site Generator
Generates all HTML pages from idioms.json + templates/.
"""
import json
import os
import html
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "idioms"
OUTPUT_DIR = BASE_DIR / "docs"
DOMAIN = "https://chinese-idioms.example.com"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(name):
    with open(TEMPLATE_DIR / name, "r", encoding="utf-8") as f:
        return f.read()


def safe(text):
    """HTML escape user-facing text but keep apostrophes readable."""
    if not text:
        return ""
    return html.escape(str(text), quote=False).replace("'", "&#39;")


def slugify_category(cat):
    """Make a URL-safe id from a category name."""
    return cat.lower().replace(" ", "-").replace("&", "and")


def build_related_links(idiom_list, names):
    """Build HTML <li> links for similar/opposite idiom lists."""
    by_chinese = {i["chinese"]: i for i in idiom_list}
    items = []
    for name in names:
        if name in by_chinese:
            i = by_chinese[name]
            items.append(
                f'<li><a href="{i["id"]}.html">{safe(i["chinese"])}</a>'
                f'<span class="pinyin-small">{safe(i["pinyin"])}</span></li>'
            )
        else:
            # Idiom not in dataset yet — show as plain text
            items.append(f'<li>{safe(name)} <span class="pinyin-small">(not yet in dictionary)</span></li>')
    return "\n      ".join(items) if items else "<li><em>None documented yet.</em></li>"


def render_idiom_page(idiom, all_idioms, template):
    meaning_short = idiom["meaning"][:140] + ("…" if len(idiom["meaning"]) > 140 else "")
    similar_links = build_related_links(all_idioms, idiom.get("similar", []))
    opposite_links = build_related_links(all_idioms, idiom.get("opposite", []))
    char_count = len(idiom["chinese"])

    replacements = {
        "{{ID}}": idiom["id"],
        "{{CHINESE}}": safe(idiom["chinese"]),
        "{{PINYIN}}": safe(idiom["pinyin"]),
        "{{LITERAL}}": safe(idiom["literal"]),
        "{{MEANING}}": safe(idiom["meaning"]),
        "{{MEANING_SHORT}}": safe(meaning_short),
        "{{ORIGIN}}": safe(idiom["origin"]),
        "{{EXAMPLE_ZH}}": safe(idiom["example_zh"]),
        "{{EXAMPLE_EN}}": safe(idiom["example_en"]),
        "{{CATEGORY}}": safe(idiom["category"]),
        "{{CATEGORY_ID}}": slugify_category(idiom["category"]),
        "{{SIMILAR_LINKS}}": similar_links,
        "{{OPPOSITE_LINKS}}": opposite_links,
        "{{CHAR_COUNT}}": str(char_count),
    }
    out = template
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def render_index_page(idioms, template):
    # Sort by pinyin alphabetically
    sorted_idioms = sorted(idioms, key=lambda x: x["pinyin"].lower())
    cards = []
    for i in sorted_idioms:
        meaning_short = i["meaning"][:100] + ("…" if len(i["meaning"]) > 100 else "")
        cards.append(
            f'<a class="idiom-card" href="idiom/{i["id"]}.html">'
            f'<div class="ch">{safe(i["chinese"])}</div>'
            f'<div class="py">{safe(i["pinyin"])}</div>'
            f'<div class="mean">{safe(meaning_short)}</div>'
            f'</a>'
        )
    categories = sorted({i["category"] for i in idioms})
    return template.replace("{{COUNT}}", str(len(idioms))) \
                   .replace("{{CATEGORY_COUNT}}", str(len(categories))) \
                   .replace("{{IDIOM_CARDS}}", "\n      ".join(cards))


def render_categories_page(idioms, template):
    by_cat = {}
    for i in idioms:
        by_cat.setdefault(i["category"], []).append(i)
    blocks = []
    for cat in sorted(by_cat.keys()):
        items = by_cat[cat]
        cat_id = slugify_category(cat)
        items_html = []
        for i in sorted(items, key=lambda x: x["pinyin"].lower()):
            items_html.append(
                f'<a href="idiom/{i["id"]}.html">'
                f'<span class="ch">{safe(i["chinese"])}</span>'
                f'<span class="py">{safe(i["pinyin"])}</span>'
                f'</a>'
            )
        block = (
            f'<div class="category-block" id="{cat_id}">\n'
            f'  <h2>{safe(cat)}</h2>\n'
            f'  <div class="count">{len(items)} idiom{"s" if len(items) != 1 else ""}</div>\n'
            f'  <div class="idiom-list">\n    {"    ".join(items_html)}\n  </div>\n'
            f'</div>'
        )
        blocks.append(block)
    return template.replace("{{CATEGORY_BLOCKS}}", "\n    ".join(blocks))


def render_sitemap(idioms):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    urls = [
        f"  <url>\n    <loc>{DOMAIN}/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>",
        f"  <url>\n    <loc>{DOMAIN}/categories.html</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>",
        f"  <url>\n    <loc>{DOMAIN}/about.html</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>",
    ]
    for i in idioms:
        urls.append(
            f"  <url>\n    <loc>{DOMAIN}/idiom/{i['id']}.html</loc>\n"
            f"    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>"
        )
    body = "\n".join(urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n"
    )


def render_robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {DOMAIN}/sitemap.xml\n"
    )


def main():
    print("Loading data...")
    idioms = load_json(DATA_DIR / "idioms.json")
    print(f"  → {len(idioms)} idioms loaded")

    print("Loading templates...")
    page_tpl = load_template("page.html")
    index_tpl = load_template("index.html")
    cats_tpl = load_template("categories.html")
    about_tpl = load_template("about.html")

    # Clean output dir
    if OUTPUT_DIR.exists():
        import shutil
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "idiom").mkdir(parents=True, exist_ok=True)

    print("Generating idiom pages...")
    for idiom in idioms:
        page = render_idiom_page(idiom, idioms, page_tpl)
        out_path = OUTPUT_DIR / "idiom" / f"{idiom['id']}.html"
        out_path.write_text(page, encoding="utf-8")
    print(f"  → {len(idioms)} idiom pages generated")

    print("Generating index page...")
    index_html = render_index_page(idioms, index_tpl)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")

    print("Generating categories page...")
    cats_html = render_categories_page(idioms, cats_tpl)
    (OUTPUT_DIR / "categories.html").write_text(cats_html, encoding="utf-8")

    print("Copying about page...")
    (OUTPUT_DIR / "about.html").write_text(about_tpl, encoding="utf-8")

    print("Generating sitemap.xml...")
    sitemap = render_sitemap(idioms)
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print("Generating robots.txt...")
    (OUTPUT_DIR / "robots.txt").write_text(render_robots(), encoding="utf-8")

    print()
    print("=" * 50)
    print(f"✓ Done! {len(idioms)} idiom pages + index + categories + about + sitemap")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 50)
    print()
    print("To preview locally:")
    print(f"  cd {OUTPUT_DIR} && python3 -m http.server 8000")
    print(f"  then open http://localhost:8000")


if __name__ == "__main__":
    main()
