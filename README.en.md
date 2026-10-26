# Warehouse Labels

[Deutsch](README.de.md) · **English** · [Hrvatski](README.hr.md) · [Overview](README.md)

[![Seite veröffentlichen](https://github.com/Beddy86/LorencicLabel/actions/workflows/veroeffentlichen.yml/badge.svg)](https://github.com/Beddy86/LorencicLabel/actions/workflows/veroeffentlichen.yml)

**Live:** https://beddy86.github.io/LorencicLabel/  ·  open on the phone and choose "Add to Home Screen"

Larger warehouse labels for stocktaking and shelves, instead of the small SAP labels: product photo, large article number, Code 128 barcode of the material number, description, and optionally storage bin and catalogue page. The labels come out as a PDF.

There are two ways to use it:

| | Web version | Windows program |
|---|---|---|
| Runs | in the browser, phone included | locally on the PC (Python) |
| Installation | none, just a web space or a link | once: Python and packages |
| Photos | 3,501 catalogue photos built in, own photos can be picked | catalogue photos, own photos, download from lorencic.at |
| Good for | quick use on the phone, many colleagues | big runs (hundreds of labels), Excel lists |

## Contents

- [Quick start (web version)](#quick-start-web-version)
- [Input](#input)
- [The dropdowns](#the-dropdowns)
- [Photos](#photos)
- [Storage bin and catalogue page](#storage-bin-and-catalogue-page)
- [Collective labels](#collective-labels)
- [Printing](#printing)
- [Hosting the web version on your own web space (e.g. WordPress)](#hosting-the-web-version-on-your-own-web-space-eg-wordpress)
- [Updating the data](#updating-the-data)
- [Publishing automatically (GitHub Pages)](#publishing-automatically-github-pages)
- [Windows program](#windows-program)
- [Troubleshooting](#troubleshooting)
- [Technical notes](#technical-notes)
- [Repository layout](#repository-layout)

## Quick start (web version)

1. Open the page.
2. Type the article numbers into the field, one per line, for example:
   ```
   Z100
   Z1425165*3
   ZM41014-RALH50
   ```
3. Pick a format and tap **Etiketten erstellen** (create labels).
4. Tap **PDF speichern** (save PDF) and print.

The bottom of the page shows how many articles and photos were loaded. If there is no number, the article list did not load (see [Troubleshooting](#troubleshooting)).

The interface is in German. The labels in this guide use the same names as the buttons.

## Input

Separate entries with a line break, a space or a comma. Upper and lower case do not matter.

| Notation | Meaning |
|---|---|
| `Z100` | one label for Z100 |
| `Z100*3` | three labels for Z100 |
| `Z100@A-12-03` | Z100 with storage bin `A-12-03` entered by hand |
| `Z100@A-12-03*2` | two labels with that storage bin |

Numbers that are not in the article list are skipped and listed after the PDF is created.

## The dropdowns

| Field | Choices |
|---|---|
| **Format** | 16.5 × 6.3 cm (default) · shelf stopper 10 × 4 cm · Mini 5.6 × 2.5 cm · Avery Zweckform 3475 / 64 2280 (70 × 36 mm, 24 per sheet) · Avery Zweckform 3481 / 42 0778 (70 × 41 mm, 21 per sheet) · A4 landscape · A5 landscape · custom size (width × height in mm, 20 to 400) |
| **Art** (type) | single labels, or collective label (see below) |
| **Seitenlayout** (page layout) | several labels per A4 page with crop marks, or one label per page |
| **Rahmen** (frame) | frame around each label, or none |
| **Lagerplatz** (storage bin) | print on the label, or not |
| **Katalogseite** (catalogue page) | print on the label, or not |
| **Fotos** | print all articles, or only articles that have a photo |
| **Druckerrand** (printer margin) | only shown for Avery sheets, see [Printing](#printing) |

The Avery formats are pre-cut label sheets. They are always printed as a grid on A4, without crop marks.

## Photos

The web version ships with the catalogue photos. If one is missing, the label is printed without a photo and the article appears under **Ohne Foto gedruckt** (printed without photo).

- **Add one by one:** tap **Foto wählen** (choose photo) there (gallery or camera), then **Mit den neuen Fotos neu erstellen** (recreate with the new photos).
- **Several at once:** under **Eigene Fotos und Lagerplätze** (own photos and storage bins) load photos. The file name is the article number, for example `Z100.jpg`. Own photos take priority over catalogue photos.
- **Only print with a photo:** in the **Fotos** field choose "Nur Artikel mit Foto drucken". Articles without a photo are then skipped and listed.

White borders around a photo are cut off automatically, transparent backgrounds become white.

## Storage bin and catalogue page

- The catalogue page comes from the article list (column `Katalogseite`).
- The storage bin is either entered by hand (`Z100@A-12-03`) or loaded from a list: under **Eigene Fotos und Lagerplätze** pick an Excel or CSV file with the columns `Material` and `Lagerplatz` (optionally `Katalogseite`). Column names are matched regardless of case, `Platz` and `LGPBE` work too.
- If a small label has no room for it, the footer line is left out. The description has priority.

## Collective labels

One A4 portrait sheet per article group, for example all sizes of a work trouser: photo, number stem and common description at the top, then one row per size with article number, size and barcode.

1. Choose "Sammeletikett" under **Art**.
2. **Each line is one sheet**, all numbers in one line belong together:
   ```
   ZM41014-RALH50 ZM41014-RALH52 ZM41014-RALH54
   ZM42014-RABH50 ZM42014-RABH52
   ```
3. The photo comes from the first article in the line that has one. More than 9 articles in a group continue on further pages.

The text that is the same for all articles is summarised at the top, only the differences (for example `Gr. 50`) appear in the row. This works best when the descriptions are structured with commas.

## Printing

- When printing, choose **100 % / "actual size"**, not "fit to page". Otherwise the dimensions are wrong.
- For label sheets (Avery) first print **a test page on plain paper** and hold it against the sheet in front of a light.
- **Printer margin:** many printers do not print all the way to the left and right paper edge. For the Avery formats the page moves the content of the outer columns inwards so nothing is cut off. The default is 6 mm. If nothing is cut off on your printer you can reduce the value; if something still is, increase it.
- **Barcode scanners:** on very small labels (Mini 5.6 × 2.5 cm) the bars are narrow. Scan a test label before printing a large batch.

## Hosting the web version on your own web space (e.g. WordPress)

The web version is plain HTML and needs no server with PHP or a database.

1. Copy these files into a folder `etiketten` on the web space (FTP or the hosting file manager): `index.html`, `manifest.json`, the four icons (`*.png`), `liste.json` and the folder `fotos/`. About 47 MB in total.
2. The folder must sit **next to** `wp-content`, not in the media library. WordPress does not accept these file types (`.json`, `.txt`) there.
3. Open `https://your-domain.com/etiketten/`.
4. To show it inside a WordPress page, embed `/etiketten/` with an iframe.

Notes:

- The page loads two libraries from `cdnjs.cloudflare.com` (jsPDF to create the PDF, SheetJS to read Excel). If a firewall blocks that, put the two files on your web space and point the two `<script src=…>` lines in `index.html` to them.
- The company logo in the header is embedded in `index.html` (Base64). To replace it, change the line `<img class="logo" …>`.
- Without protection anyone can open the page. If that is not wanted, set up directory protection (password) for `/etiketten/` in your hosting.
- Everything runs in the browser. Entered numbers and photos are not uploaded anywhere.
- If you serve the page through GitHub Pages (see below) you need none of this.

## Updating the data

The repo has two sources:

| Source | Content |
|---|---|
| `data/preisliste_artikel.csv` | Article list. Columns `Material;Materiallangtext;WGR;LGR;BME;Katalogseite` (semicolon, UTF-8). An empty catalogue page is `-`. |
| `data/bilder/` | New or replaced photos. File name = article number, e.g. `Z1234567.jpg` (JPG or PNG). |

The base set of catalogue photos is already packed in `fotos/`. Photos from `data/bilder/` are added on top and take priority.

**Adding a new article**

1. Append a line to `data/preisliste_artikel.csv`.
2. Optionally put the photo in `data/bilder/`.
3. Commit and push. GitHub then rebuilds the page (see [Publishing automatically](#publishing-automatically-github-pages)).

**Building by hand** (for testing or for your own web space), in the repo root:

```bash
python3 tools/build_web_data.py
```

The script needs only Python 3, no extra packages. It writes `liste.json` and adds to `fotos/`. Existing photo packs stay unchanged, new photos go into new packs. `--kompakt` rewrites all packs (removes outdated photos). All options: `python3 tools/build_web_data.py --help`.

## Publishing automatically (GitHub Pages)

The page lives at **https://beddy86.github.io/LorencicLabel/**. The workflow `.github/workflows/veroeffentlichen.yml` rebuilds it on every push to `main`: it takes `index.html` with icons, the base set in `fotos/`, then `data/preisliste_artikel.csv` and `data/bilder/`, and publishes the result.

**Set up once**

1. In the repo go to **Settings → Pages** and choose "GitHub Actions" under **Source**.
2. In the **Actions** tab start the workflow **Seite veröffentlichen** once by hand (**Run workflow**) or make any push.

**From then on** a push is enough. The **Actions** tab shows progress and any errors. The workflow does not start for changes to READMEs or the Windows program only.

**Install on the phone:** open the page in the browser and choose "Add to Home Screen". It then starts like an app with a red icon.

## Windows program

For large runs and Excel lists. Everything runs locally, no port is opened to the outside (the window listens on `127.0.0.1` only). Only the photo search on lorencic.at goes to the internet.

**Install once**

1. Install Python 3 from python.org and tick "Add Python to PATH".
2. Copy the folder `desktop/` to the PC, for example to `C:\Etiketten`. The program finds the article list in the `data/` folder of the repo. If `desktop/` is on the PC by itself, put the file `preisliste_artikel.csv` next to it.
3. Double-click `Einmal_installieren.bat`. It installs `openpyxl`, `reportlab` and `pillow` (see `requirements.txt`).

**Start**

Double-click `Etiketten_starten.bat`. A black window opens (leave it open) and the browser shows the same interface as the web version. PDFs are saved in the folder `ausgabe`.

In addition:

- Missing photos are fetched from lorencic.at (option in the interface) and kept in `bilder/_web/`.
- Put your own photos in the folder `bilder/`, as `Z100.jpg`. They take priority.
- Long runs show their progress.
- Photos that were found are remembered in `bild_cache.json`. If a photo is no longer right, delete that file.

**Command line**

```bash
# single articles, several per A4 page
python3 desktop/etiketten.py --artikel Z100 Z5-1 Z170000 -o labels.pdf --a4

# whole Excel list (columns Material, Materiallangtext, optional Lagerplatz, Katalogseite)
python3 desktop/etiketten.py list.xlsx -o labels.pdf

# another format, only with photo
python3 desktop/etiketten.py --artikel-datei numbers.txt --format avery3481 --nur-mit-foto -o avery.pdf

# custom size 90 x 45 mm
python3 desktop/etiketten.py --artikel Z100 --breite 90 --hoehe 45 -o custom.pdf

# collective label, each --sammel group is one sheet
python3 desktop/etiketten.py --sammel ZM41014-RALH50 ZM41014-RALH52 --sammel ZM42014-RABH50 -o collective.pdf
```

All options: `python3 desktop/etiketten.py --help`. Formats: `165x63`, `a4`, `a5`, `stopper`, `mini`, `avery3475`, `avery3481`.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| "Artikelliste konnte nicht geladen werden" | `liste.json` or `fotos/` is missing on the server, or the hosting blocks `.json` / `.txt`. Check the folder structure and open the files directly in the browser. |
| Blank page, nothing reacts | The scripts from `cdnjs.cloudflare.com` are blocked. See the firewall note above. |
| Photo missing | There is no catalogue photo. Choose your own photo or put `Z….jpg` in `bilder/`. |
| Windows program: certificate error (SSL) | Company network with its own certificate inspection. The program only works around that for lorencic.at. Use the latest `etiketten.py`. |
| Label without a photo although there is one online | Delete `bild_cache.json` and create again. |
| `PDF speichern` does nothing | The browser blocks downloads. Allow the pop-up and download prompt of the browser. |
| Avery: photo on the left or barcode on the right is cut off | Increase the printer margin (default 6 mm). |
| Special characters turn into a question mark | Characters outside the standard character set (Windows-1252) cannot be shown in the font. `²` and `³` are printed as `2` and `3`. |
| Barcode does not scan | Print at 100 %, choose a larger format, check that the scanner reads Code 128. |

## Technical notes

- Barcode: Code 128, character set B, switching automatically to C for longer digit runs.
- Web version: a single `index.html`, the PDF is created with jsPDF in the browser, data as `liste.json` and photo packs (`fotos/pNNN.txt`, Base64, about 300 KB each, with `fotos/index.json`). Photos are only loaded when needed.
- Windows program: Python with reportlab, Pillow and openpyxl, interface as a small local web server.
- The layout of both versions is the same and was ported line by line. If you change a layout, change it in both (`desktop/etiketten.py` and `index.html`).

## Repository layout

```
index.html, manifest.json, *.png   the page (with phone icons)
liste.json, fotos/                 base set of the data, already packed
data/preisliste_artikel.csv        article list (source)
data/bilder/                       new and own photos (source)
tools/build_web_data.py            builds liste.json and fotos/
desktop/                           Windows program
.github/workflows/                 automatic publishing
```

## License

All rights reserved, see [LICENSE](LICENSE). The page may be used. Copying, modifying and distributing the code and the data is not allowed without written permission. The article list and catalogue photos come from lorencic.at.
