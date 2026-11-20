# Born here, died there

A map of where artists who have exhibited at **mumok** (Museum moderner Kunst Stiftung Ludwig Wien) were born and where they died. Every line is one artist, drawn from birthplace to place of death.

**Live page:** open `index.html`, or enable GitHub Pages (see below).

Group: Simon Winkler, Aisling Scroggs, Jessica Kraft, Johannes Bruckner

## What the page shows

- 566 artists have both a birthplace and a place of death on record. 523 of them could be placed on the map.
- 346 died in their home country and 177 died in another country.
- **Blue box:** a birthplace. **Orange box:** a place of death. Box size grows with the number of artists.
- **Line:** one artist, from birthplace to place of death. Lines bend to the left of their direction. Dark bundles are many faint lines stacked on similar routes.
- **Country menu:** colours a country's lines (blue = born there, orange = died there) and lists the artists below the map.
- **Hover** a line or box for names. **Click** to keep the details below the map. Drag to pan, Ctrl + scroll or pinch to zoom.

## Method

1. **Cleaning** (`scripts/propose_changes.py`, `scripts/apply_changes.py`). The source list (`data/source/artist_mumok.csv`, 1,533 records) was checked for spelling, whitespace, missing English translations and malformed fields. Every proposed change is listed in `data/proposed_changes_v1.csv`. Only reviewed groups were applied (115 changes, logged in `data/changelog_v1.csv`). Countries follow today's borders, with the historical name kept in a note column. Suspect facts (for example wrong birth years) are flagged, not changed.
2. **Locating places** (`scripts/geocode.js`, `scripts/place_aliases.json`). Birth and death places were matched to [GeoNames](https://www.geonames.org/) towns of over 1,000 inhabitants via the `all-the-cities` package. Older names were matched to their current entry (Czernowitz to Chernivtsi, for example). Villages missing from GeoNames are shown at the nearest town and marked in the tooltip. The full match log is in `data/place_matching_report_v2.csv`.
3. **Map** (`scripts/template.html`, `scripts/build_site.py`). A Natural Earth projection drawn with d3. Land is a 1° pixel raster from Natural Earth (`data/land_world1.json`). Lines are smooth curves on top.

## Rebuild

```bash
npm install                       # all-the-cities, world-atlas, topojson-client
npm run geocode                   # optional: re-match places
npm run land                      # optional: re-rasterise land
npm run build                     # writes data/map_data.json and index.html
```

## Publish with GitHub Pages

Repository **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, folder `/ (root)`. The page appears at `https://smoaf.github.io/datavizmumok/` after a minute.

## Sources

- Artist list: mumok Wien (`data/source/artist_mumok.csv`)
- Places: GeoNames via [all-the-cities](https://www.npmjs.com/package/all-the-cities)
- Land: Natural Earth via [world-atlas](https://www.npmjs.com/package/world-atlas)
- Fonts: IBM Plex Mono (Google Fonts). Charts: d3 v7.
