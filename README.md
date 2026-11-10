# George Entwistle Driveways & Paving

Production: https://entwistlepaving.co.uk/
Netlify project: `entwistlepaving` (`a7a6bf48-30d1-4a3c-85d3-9c6a6a46ad69`).

Run `python3 build.py` to build all pages into `dist/`. No package installation or external build dependencies are required. Netlify runs the same command and publishes `dist/` when `main` changes.

## Editing

- `build.py`: shared HTML, page copy, navigation, structured data, sitemap and legacy URL redirects.
- `brand_content.py`: original full-width photo hero, five-face logo motif and expanded supporting page content.
- `content/services.json`: five service pages and FAQs.
- `content/photos.json`: accurate captions, alt text, categories and responsive file variants for 37 unique photos. Nine new photographs were added in November 2026. One exact duplicate from the old live gallery was omitted.
- `assets/site.css`, `assets/brand.css` and `assets/site.js`: responsive presentation, exact logo palette, condensed Anton headings, reduced-motion-aware logo assembly, navigation, gallery filters and accessible photo viewer.
- `assets/photos/`: pre-generated 480px, 960px and larger WebP variants. Preserve original aspect ratios and do not upscale.
- `images/`: original public image URLs retained for existing external links; pages use the optimised assets.

The site is rendered HTML and remains readable without JavaScript. Contact actions open the phone dialler or the visitor's email app. There is no contact submission form or analytics integration. Do not add unverified ratings, opening hours, addresses, project locations, accreditation or guarantees.

## Search Console

Production property: `sc-domain:entwistlepaving.co.uk`; sitemap: https://entwistlepaving.co.uk/sitemap.xml. Use only `maderealdesign@gmail.com` and verify that exact identity before every Search Console write.
