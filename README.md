# Chinese Idiom Dictionary (成语词典英文版)

A free, English-language reference for classical Chinese idioms (成语 / chéngyǔ). Each entry includes pinyin, literal translation, English meaning, origin story, example sentences, and related idioms.

Built as a **programmatic SEO site**: every idiom gets its own static HTML page optimized for Google search, targeting long-tail queries like "what does 守株待兔 mean" and "shou zhu dai tu translation".

## Project Structure

```
idiom-dict/
├── idioms/
│   └── idioms.json         # Source data: all idiom entries
├── templates/
│   ├── page.html          # Single idiom page template
│   ├── index.html         # Homepage (all idioms grid)
│   ├── categories.html    # Browse by category
│   └── about.html         # About page
├── scripts/
│   └── generate.py        # Static site generator (no deps, pure Python)
└── public/                # Generated output (deploy this folder)
    ├── index.html
    ├── categories.html
    ├── about.html
    ├── sitemap.xml
    ├── robots.txt
    └── idiom/
        ├── shou-zhu-dai-tu.html
        ├── hua-she-tian-zu.html
        └── ... (50 pages currently)
```

## Local Preview

```bash
cd public
python3 -m http.server 8000
# open http://localhost:8000
```

## Regenerate the Site

After editing `idioms/idioms.json` or any template:

```bash
python3 scripts/generate.py
```

The generator has **zero external dependencies** — uses only Python 3 standard library.

## Deployment (Free Hosting Options)

### Option A: Cloudflare Pages (recommended — free, fast, CDN)
1. Push this repo to GitHub
2. Go to https://pages.cloudflare.com
3. Connect your GitHub repo
4. Set build output directory to `public`
5. Deploy — Cloudflare gives you a free `*.pages.dev` domain

### Option B: GitHub Pages
1. Push this repo to GitHub
2. Settings → Pages → Source: main branch, /public folder
3. Site goes live at `username.github.io/idiom-dict`

### Option C: Netlify
1. Drag and drop the `public/` folder onto https://app.netlify.com/drop

## SEO Features

- ✅ Per-page `<title>`, meta description, keywords
- ✅ Canonical URLs
- ✅ Open Graph + Twitter Card meta tags
- ✅ JSON-LD structured data (Article schema) on every idiom page
- ✅ Breadcrumb navigation
- ✅ XML sitemap with all URLs
- ✅ robots.txt with sitemap reference
- ✅ Semantic HTML5 (header, main, section, footer)
- ✅ Mobile-first responsive design
- ✅ Internal linking between related idioms
- ✅ Clean URL structure (`/idiom/{pinyin-slug}.html`)
- ✅ Fast load (no JS frameworks, no external CSS, ~9KB per page)

## Roadmap

### v1.0 (current — MVP)
- 50 commonly-known idioms
- 4 page types (home, idiom, categories, about)
- Basic search (client-side filter)
- Full SEO infrastructure

### v1.1 (next)
- [ ] Expand to 500 idioms (priority: most-searched)
- [ ] Add pinyin tone-number alternative (e.g. `shou3 zhu1 dai4 tu4`)
- [ ] Add Chinese-character stroke order diagrams
- [ ] Add "idiom of the day" widget
- [ ] Add pagination on homepage when >100 idioms

### v2.0
- [ ] 2000+ idioms
- [ ] Hanzi-to-pinyin auto-conversion via pypinyin
- [ ] Audio pronunciation (TTS)
- [ ] Example sentences sourced from real Chinese literature
- [ ] Bilingual mode (中英对照)
- [ ] Anki flashcard export
- [ ] API endpoint (JSON) for each idiom

## Monetization (Once Traffic Arrives)

1. **Google AdSense** — primary revenue (apply after 3+ months of content + traffic)
2. **Ezoic / Mediavine** — better RPM once traffic hits 10k/month
3. **Affiliate links** to Chinese learning products (Pleco, Skritter, Duolingo)
4. **Premium tier** — PDF cheat sheets, Anki decks, full audio pack
5. **API access** — sell idiom data API on RapidAPI

## License

- Source code: MIT
- Idiom data: Public domain (classical Chinese idioms and their origins are over 2000 years old)
- English translations & examples: CC-BY 4.0

## Stats

- 50 idioms
- 29 categories
- 50 static HTML pages
- Total output size: ~600KB
- Generation time: <1 second
