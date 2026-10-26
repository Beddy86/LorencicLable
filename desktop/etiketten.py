#!/usr/bin/env python3
"""Lageretiketten mit Produktbild, Artikelnummer, Barcode (Code 128) und
Bezeichnung aus einer SAP-Excel erzeugen. Standard: 16,5 x 6,3 cm
(weitere Formate: --format a4 / a5 / stopper / mini / avery3475 / avery3481).

Beispiele:
  python3 etiketten.py --artikel Z100 Z5-1 Z170000 -o etiketten.pdf --a4
      (einzelne Artikel; Bezeichnung aus preisliste_artikel.csv im selben Ordner)
  python3 etiketten.py SOLA.xlsx -o etiketten.pdf
  python3 etiketten.py SOLA.xlsx -o etiketten.pdf --nur-bestand
  python3 etiketten.py artikelstamm.xlsx -o etiketten.pdf --block 500 --max 5

Excel-Spalten: "Material", "Materiallangtext" (optional "Best. ges.").
CSV (Material;Bezeichnung) geht ebenfalls.

Bilder, in dieser Reihenfolge:
  1. Ordner bilder/<Material>.jpg|png  (eigene Bilder haben Vorrang)
  2. Download von lorencic.at (Suche nach Artikelnr. -> Produktseite -> Bild),
     gespeichert in bilder/_web/, Zuordnung in bild_cache.json (wiederaufnehmbar)
  Fehlt ein Bild, wird das Etikett ohne Bild gedruckt; die Artikel ohne Bild
  stehen danach in ohne_bild.csv.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import openpyxl
from PIL import Image, ImageChops
from reportlab.graphics.barcode.code128 import Code128
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

BASE = "https://www.lorencic.at/"
# Formate: Breite x Höhe in mm (Zeichenfläche quer), Seite hochkant drehen ja/nein
FORMATS = {
    "165x63": (165, 63, False),   # 16,5 x 6,3 cm
    "a4": (297, 210, False),      # ganze A4-Seite quer, 1 Etikett pro Blatt
    "stopper": (100, 40, False),  # Regalstopper 10 x 4 cm
    "avery3475": (70, 36, False), # Avery Zweckform 3475 / 64 2280: 70 x 36 mm, 24 pro A4-Bogen
    "avery3481": (70, 41, False), # Avery Zweckform 3481 / 42 0778: 70 x 41 mm, 21 pro A4-Bogen
    "mini": (56, 25, False),      # 5,6 x 2,5 cm (Größenvergleich / kleine Regalschilder)
    "a5": (210, 148, False),      # ganze A5-Seite quer (mit --a4: 2 Stück pro A4-Blatt)
}
# Layout-Parameter je Format (Barcode bewusst niedrig, Artikelnummer groß)
PARAMS = {
    "165x63": dict(platz=14, M=4, bar_h=10, num_max=64, num_min=48, desc_max=16, desc_min=8, img_min=42),
    "avery3475": dict(platz=8, M=3, bar_h=8, num_max=34, num_min=18, desc_max=9, desc_min=5, img_min=14),
    "avery3481": dict(platz=9, M=3, bar_h=9, num_max=36, num_min=18, desc_max=10, desc_min=5, img_min=14),
    "mini": dict(platz=6, M=2, bar_h=5, num_max=22, num_min=12, desc_max=6, desc_min=4, img_min=13),
    "stopper": dict(platz=9, M=2.5, bar_h=7, num_max=40, num_min=28, desc_max=10, desc_min=6, img_min=24),
}
INSET = {"a4": 8, "a5": 6, "mini": 0.8, "avery3475": 2, "avery3481": 2}
HOCH = set()                  # nur "custom", wenn hochformatig
GROSS = {"a4", "a5"}          # Formate mit dem 'großen' Layout (Nummer oben, Foto links, Text rechts)


def register_custom(w_mm, h_mm):
    """Eigene Abmessung (mm): Layout und Schriftgrößen werden aus Breite/Höhe abgeleitet."""
    w_mm, h_mm = float(w_mm), float(h_mm)
    if not (20 <= w_mm <= 400 and 20 <= h_mm <= 400):
        sys.exit("Abmessungen müssen zwischen 20 und 400 mm liegen.")
    FORMATS["custom"] = (w_mm, h_mm, False)
    INSET["custom"] = 6 if min(w_mm, h_mm) >= 100 else 2
    GROSS.discard("custom")
    HOCH.discard("custom")
    if w_mm / h_mm >= 1.8:                         # flach: Foto links, rechts Barcode/Nummer/Text
        PARAMS["custom"] = dict(
            platz=max(5, 0.22 * h_mm), M=max(2, 0.07 * h_mm, INSET["custom"] + 1.5), bar_h=max(5, 0.18 * h_mm),
            num_max=max(12, 1.0 * h_mm), num_min=max(10, 0.55 * h_mm), desc_max=max(6, 0.25 * h_mm),
            desc_min=max(4, 0.12 * h_mm), img_min=min(0.6 * h_mm, 0.4 * w_mm))
    elif h_mm / w_mm >= 1.2:                       # hochformatig
        HOCH.add("custom")
    else:                                          # eher quadratisch/leicht quer: Nummer oben, Foto links, Text rechts
        GROSS.add("custom")
    return "custom"


DRUCKERRAND = 6              # mm: so weit vom Papierrand darf bei Etikettenbögen gedruckt werden (links/rechts)
BOGEN = {"avery3475", "avery3481"}           # fertig gestanzte Etikettenbögen: immer Raster auf A4, ohne Schnittmarken             # Abstand Rahmen zur Schnittkante in mm (Standard 1,5; A4: Druckerrand)
PLATZ = {}                    # Material -> Lagerplatz (aus der Artikelliste, Spalte "Lagerplatz"/"Platz")
SHOW_PLATZ = True
KATALOG = {}                  # Material -> Katalogseite (Spalte "Katalogseite")
SHOW_KATALOG = True
PAUSE = 0.4                   # Sekunden zwischen Web-Abfragen (Server schonen)


# ----------------------------------------------------------------- Layout
def latin(text):
    return text.encode("cp1252", errors="replace").decode("cp1252")


def fit_font(text, font, size, max_w, min_size=8):
    while size > min_size and stringWidth(text, font, size) > max_w:
        size -= 1
    return size


def wrap(text, font, size, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if stringWidth(t, font, size) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def load_image(path):
    """Bild laden, Transparenz auf Weiß setzen, weißen Rand abschneiden."""
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, "white")
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    diff = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255)))
    box = diff.convert("L").point(lambda p: 255 if p > 12 else 0).getbbox()
    if box:
        img = img.crop(box)
    return img


def draw_image(c, img, x, y, bw, bh):
    iw, ih = img.size
    s = min(bw / iw, bh / ih)
    w, h = iw * s, ih * s
    c.drawImage(ImageReader(img), x + (bw - w) / 2, y + (bh - h) / 2, w, h)


def footer_of(material):
    platz = PLATZ.get(material, "") if SHOW_PLATZ else ""
    kat = KATALOG.get(material, "") if SHOW_KATALOG else ""
    return platz, kat


def draw_platz(c, platz, kat, x, y, size, max_w):
    """Fußzeile: links 'Platz: ...' (fett), rechts 'Katalog: ...'; Schrift passt sich der Breite an."""
    left = "Platz: " + platz if platz else ""
    right = "Katalog: " + kat if kat else ""
    if not platz:                                  # nur Katalogseite: links bündig
        left, right = right, ""
    fl = "Helvetica-Bold" if platz else "Helvetica"
    while size > 5 and (stringWidth(left, fl, size) + (stringWidth(right, "Helvetica", size) + size * 1.5 if right else 0)) > max_w:
        size -= 0.5
    c.setFont(fl, size)
    c.drawString(x, y, left)
    if right:
        c.setFont("Helvetica", size)
        c.drawRightString(x + max_w, y, right)


def draw_label(c, material, text, img_path, W, H, fmt="165x63"):
    if fmt in HOCH:
        draw_label_hoch(c, material, text, img_path, W, H)
    elif fmt in GROSS:
        draw_label_gross(c, material, text, img_path, W, H)
    else:
        draw_label_breit(c, material, text, img_path, W, H, PARAMS.get(fmt, PARAMS["165x63"]))


def draw_label_breit(c, material, text, img_path, W, H, p):
    """Flaches Etikett: Bild links über die volle Höhe, rechts Nummer/Barcode/Text."""
    M = p["M"] * mm
    top = H - M
    x = M
    if img_path:
        try:
            img = load_image(img_path)
            box_h = H - 2 * M
            # breite Fotos (Wasserwaage) bekommen mehr Platz, hohe bleiben bei 42 mm
            # rechts bleibt mindestens so viel Platz, dass Barcode (0,7 mm je Modul)
            # und Nummer (48 pt) sicher passen; der Rest geht ans Bild
            min_right = max(stringWidth(material, "Helvetica-Bold", p["num_min"]),
                            Code128(material, barWidth=1, barHeight=1, quiet=False).width * 0.7 * mm)
            avail = W - 2 * M - 5 * mm - min_right
            box_w = max(p["img_min"] * mm, min(avail, box_h * img.size[0] / img.size[1]))
            draw_image(c, img, M, M, box_w, box_h)
            x = M + box_w + 5 * mm
        except Exception as e:
            print(f"  Bild nicht lesbar ({img_path}): {e}")
    w = W - M - x

    # oben: Barcode (kompakt), darunter: Artikelnummer so groß wie möglich
    bar_h = p["bar_h"] * mm
    probe = Code128(material, barWidth=1, barHeight=bar_h, quiet=False)
    bw = min(w / probe.width, 1.0 * mm)
    Code128(material, barWidth=bw, barHeight=bar_h, quiet=False).drawOn(c, x, top - bar_h)

    size = fit_font(material, "Helvetica-Bold", p["num_max"], w)
    gap = 3 * mm if p["M"] >= 4 else 2 * mm
    base = top - bar_h - gap - size * 0.72      # Versalhöhe ca. 0,72 em
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, base, material)

    y0 = base - gap
    platz, kat = footer_of(material)
    if (platz or kat) and (y0 - M - p["platz"] * 1.5) < p["desc_min"] * 1.3:
        platz = kat = ""                           # zu klein für Fußzeile: Bezeichnung hat Vorrang
    plat_h = p["platz"] * 1.5 if (platz or kat) else 0
    avail = y0 - M - plat_h
    if platz or kat:
        draw_platz(c, platz, kat, x, M + p["platz"] * 0.15, p["platz"], w)
    size = p["desc_max"]
    lines = wrap(text, "Helvetica", size, w)
    while (len(lines) > 3 or len(lines) * size * 1.15 > avail) and size > p["desc_min"]:
        size -= 1
        lines = wrap(text, "Helvetica", size, w)
    lines = lines[:max(0, int(avail / (size * 1.15)))]          # nichts über den Rand hinaus drucken
    c.setFont("Helvetica", size)
    y = y0 - size * 0.8
    for ln in lines:
        c.drawString(x, y, ln)
        y -= size * 1.15


def draw_label_hoch(c, material, text, img_path, W, H):
    """Hochformat: Nummer oben, Foto darunter, dann Bezeichnung, Platz/Katalog, Barcode ganz unten."""
    M = max(4 * mm, 0.05 * W, (INSET.get("custom", 2) + 2) * mm)
    inner = W - 2 * M
    top = H - M
    ns = fit_font(material, "Helvetica-Bold", 0.25 * W, inner, min_size=10)
    c.setFont("Helvetica-Bold", ns)
    c.drawString(M, top - ns * 0.72, material)
    y_num = top - ns * 0.72 - 4 * mm

    bar_h = max(8 * mm, 0.08 * H)
    probe = Code128(material, barWidth=1, barHeight=bar_h, quiet=False)
    bw = min(inner / probe.width, 1.0 * mm)
    Code128(material, barWidth=bw, barHeight=bar_h, quiet=False).drawOn(c, M, M)

    y = M + bar_h + 3 * mm
    platz, kat = footer_of(material)
    if platz or kat:
        ps = max(7, 0.05 * W)
        draw_platz(c, platz, kat, M, y, ps, inner)
        y += ps * 1.6
    ds = max(8, 0.06 * W)
    lines = wrap(text, "Helvetica", ds, inner)
    while len(lines) > 4 and ds > 6:
        ds -= 1
        lines = wrap(text, "Helvetica", ds, inner)
    y_top = y + len(lines) * ds * 1.15 + 2 * mm
    c.setFont("Helvetica", ds)
    yy = y_top - ds * 0.8
    for ln in lines:
        c.drawString(M, yy, ln)
        yy -= ds * 1.15
    if img_path and y_num - (y_top + 2 * mm) > 10 * mm:
        try:
            draw_image(c, load_image(img_path), M, y_top + 2 * mm, inner, y_num - y_top - 2 * mm)
        except Exception as e:
            print(f"  Bild nicht lesbar ({img_path}): {e}")


def draw_label_gross(c, material, text, img_path, W, H):
    """A4 quer: Artikelnummer riesig oben, darunter links Foto, rechts Bezeichnung, Barcode klein unten rechts."""
    k = min(1.0, W / (297 * mm), H / (210 * mm))   # A5 = 0,71 x A4-Maße
    M = 16 * mm * k
    inner_w = W - 2 * M
    top = H - M
    size = fit_font(material, "Helvetica-Bold", 150 * k, inner_w, min_size=16)
    c.setFont("Helvetica-Bold", size)
    c.drawString(M, top - size * 0.72, material)
    zone_top = top - size * 0.72 - 10 * mm * k
    zone_bot = M
    zone_h = zone_top - zone_bot

    x_right = M
    if img_path:
        try:
            img = load_image(img_path)
            box_w = min(inner_w * 0.5, zone_h * img.size[0] / img.size[1])
            box_w = max(box_w, inner_w * 0.3)
            draw_image(c, img, M, zone_bot, box_w, zone_h)
            x_right = M + box_w + 10 * mm * k
        except Exception as e:
            print(f"  Bild nicht lesbar ({img_path}): {e}")
    w = W - M - x_right

    bar_h = 16 * mm * k
    probe = Code128(material, barWidth=1, barHeight=bar_h, quiet=False)
    bw = min(w / probe.width, 1.0 * mm)
    Code128(material, barWidth=bw, barHeight=bar_h, quiet=False).drawOn(c, x_right, zone_bot)

    y0 = zone_top
    platz, kat = footer_of(material)
    ps = 44 * k
    plat_h = ps * 1.5 if (platz or kat) else 0
    if platz or kat:
        draw_platz(c, platz, kat, x_right, zone_bot + bar_h + 5 * mm * k, ps, w)
    avail = y0 - (zone_bot + bar_h + 6 * mm * k + plat_h)
    size = 40 * k
    lines = wrap(text, "Helvetica", size, w)
    while (len(lines) > 5 or len(lines) * size * 1.15 > avail) and size > 10:
        size -= 1
        lines = wrap(text, "Helvetica", size, w)
    c.setFont("Helvetica", size)
    y = y0 - size * 0.8
    for ln in lines:
        c.drawString(x_right, y, ln)
        y -= size * 1.15


def crop_marks(c, x0, y0, cw, ch, cols, rows):
    """Schnittmarken im Rand um das Etikettenraster."""
    c.setStrokeColorRGB(0.35, 0.35, 0.35)
    c.setLineWidth(0.3)
    gx0, gx1 = x0, x0 + cols * cw
    gy0, gy1 = y0, y0 + rows * ch
    for k in range(rows + 1):             # waagrechte Schnitte: Marken links/rechts
        y = gy0 + k * ch
        c.line(gx0 - 8 * mm, y, gx0 - 2 * mm, y)
        c.line(gx1 + 2 * mm, y, gx1 + 8 * mm, y)
    for k in range(cols + 1):             # senkrechte Schnitte: Marken oben/unten
        x = gx0 + k * cw
        c.line(x, gy1 + 2 * mm, x, gy1 + 8 * mm)
        c.line(x, gy0 - 8 * mm, x, gy0 - 2 * mm)


def build_pdf(rows, images, out, fmt="165x63", quer=False, a4=False, rahmen=True):
    w_mm, h_mm, hochkant = FORMATS[fmt]
    W, H = w_mm * mm, h_mm * mm
    hochkant = hochkant and not quer
    pw, ph = (H, W) if hochkant else (W, H)          # Seitengröße eines Etiketts
    if fmt == "a4":
        a4 = False                                    # Etikett ist schon eine ganze A4-Seite
    if fmt in BOGEN:
        a4 = True
    if a4 and (pw > 210 * mm or ph > 297 * mm):
        a4 = False                                    # passt nicht auf A4: ein Etikett pro Seite
    inset = INSET.get(fmt, 1.5) * mm

    if not a4:
        c = canvas.Canvas(out, pagesize=(pw, ph))
        cols = rows_n = 1
        x0 = y0 = 0
    else:
        A4W, A4H = 210 * mm, 297 * mm
        c = canvas.Canvas(out, pagesize=(A4W, A4H))
        cols = int(A4W // pw)
        rows_n = int(A4H // ph)
        if cols < 1 or rows_n < 1:
            sys.exit("Etikett passt nicht auf A4.")
        x0 = (A4W - cols * pw) / 2
        y0 = (A4H - rows_n * ph) / 2
    per_page = cols * rows_n

    for i, (mat, text) in enumerate(rows):
        pos = i % per_page
        if a4 and pos == 0 and fmt not in BOGEN:
            crop_marks(c, x0, y0, pw, ph, cols, rows_n)
        r, col = divmod(pos, cols)
        ox = x0 + col * pw
        oy = y0 + (rows_n - 1 - r) * ph               # Zeile 0 = oben
        c.saveState()
        Wl = W
        if fmt in BOGEN:                  # Bogen ohne Seitenrand: Drucker druckt am Rand nicht -> Inhalt der Randspalten nach innen
            ins = max(0.0, DRUCKERRAND * mm - inset)
            shl = ins if col == 0 else 0
            shr = ins if col == cols - 1 else 0
            ox += shl
            Wl = W - shl - shr
        c.translate(ox, oy)
        if hochkant:                      # Inhalt um 90° drehen: 100 x 150 hochkant
            c.translate(H, 0)
            c.rotate(90)
        if rahmen:                        # Rahmen 1,5 mm innerhalb der Schnittkante
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(1)
            c.roundRect(inset, inset, Wl - 2 * inset, H - 2 * inset, 2 * mm, stroke=1, fill=0)
        draw_label(c, latin(mat), latin(text), images.get(mat), Wl, H, fmt)
        c.restoreState()
        if pos == per_page - 1 or i == len(rows) - 1:
            c.showPage()
    c.save()



# ------------------------------------------------------------ Sammeletikett
def split_groups(group):
    """Gemeinsamen Beschreibungsteil und je Artikel die abweichenden Teile (z. B. 'Gr. 50') bestimmen."""
    segs = [[x.strip() for x in t.split(",")] for _, t in group]
    common = [x for x in segs[0] if all(x in sg for sg in segs[1:])] if len(group) > 1 else segs[0]
    diffs = [", ".join(x for x in sg if x not in common) for sg in segs]
    return ", ".join(common), diffs


def draw_sammel_page(c, group, img_path, W, H, page_no, pages, rows_here, first_row, rahmen, inset):
    M = 16 * mm
    inner = W - 2 * M
    mats = [m for m, _ in group]
    prefix = os.path.commonprefix(mats) if len(mats) > 1 else mats[0]
    beschr, diffs = split_groups(group)
    if rahmen:
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        c.roundRect(inset, inset, W - 2 * inset, H - 2 * inset, 3 * mm, stroke=1, fill=0)
    top = H - M
    # Kopf: links Foto, rechts Nummernstamm und Beschreibung
    head_h = 78 * mm
    x_txt = M
    if img_path:
        try:
            img = load_image(img_path)
            bw = min(inner * 0.42, head_h * img.size[0] / img.size[1])
            draw_image(c, img, M, top - head_h, max(bw, inner * 0.25), head_h)
            x_txt = M + max(bw, inner * 0.25) + 8 * mm
        except Exception as e:
            print(f"  Bild nicht lesbar ({img_path}): {e}")
    w = W - M - x_txt
    ptxt = prefix + ("…" if len(mats) > 1 else "")
    size = fit_font(ptxt, "Helvetica-Bold", 40, w, min_size=14)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x_txt, top - size * 0.8, ptxt)
    ds = 17
    lines = wrap(latin(beschr), "Helvetica", ds, w)
    while len(lines) > 6 and ds > 9:
        ds -= 1
        lines = wrap(latin(beschr), "Helvetica", ds, w)
    c.setFont("Helvetica", ds)
    y = top - size * 0.8 - 8 * mm - ds * 0.8
    for ln in lines:
        c.drawString(x_txt, y, ln)
        y -= ds * 1.2
    if pages > 1:
        c.setFont("Helvetica", 9)
        c.drawRightString(W - M, top - head_h - 2 * mm, f"Seite {page_no}/{pages}")
    # Zeilen: Variante | Artikelnummer | Barcode
    y_top = top - head_h - 6 * mm
    row_h = min(24 * mm, (y_top - M) / max(rows_here, 1))
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.4)
    for k in range(rows_here):
        i = first_row + k
        yb = y_top - (k + 1) * row_h
        c.line(M, yb, W - M, yb)
        mat = latin(mats[i])
        c.setFillColorRGB(0, 0, 0)
        ns = fit_font(mat, "Helvetica-Bold", 20, inner * 0.46, min_size=10)
        c.setFont("Helvetica-Bold", ns)
        c.drawString(M, yb + row_h / 2 + 1.5 * mm, mat)
        if diffs[i]:
            c.setFont("Helvetica", 12)
            c.drawString(M, yb + row_h / 2 - 5 * mm, latin(diffs[i])[:60])
        bh = row_h * 0.62
        probe = Code128(mat, barWidth=1, barHeight=bh, quiet=False)
        bwm = min(inner * 0.5 / probe.width, 1.0 * mm)
        bc = Code128(mat, barWidth=bwm, barHeight=bh, quiet=False)
        bc.drawOn(c, W - M - bc.width, yb + (row_h - bh) / 2)


def build_sammel_pdf(groups, images, out, rahmen=True):
    """Je Gruppe (Liste aus (Material, Bezeichnung)) ein A4-Blatt hochkant mit Foto, Beschreibung,
    Artikelnummern und je einem Barcode pro Variante. Viele Varianten: weitere Seiten."""
    W, H = 210 * mm, 297 * mm
    c = canvas.Canvas(out, pagesize=(W, H))
    per_page = 9
    for group in groups:
        img = next((images[m] for m, _ in group if m in images), None)
        pages = max(1, -(-len(group) // per_page))
        for p in range(pages):
            first = p * per_page
            draw_sammel_page(c, group, img, W, H, p + 1, pages, min(per_page, len(group) - first), first, rahmen, 8 * mm)
            c.showPage()
    c.save()


# ------------------------------------------------------------------ Daten
def read_rows(path):
    rows = []
    if path.lower().endswith((".xlsx", ".xlsm")):
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        it = ws.iter_rows(values_only=True)
        head = [str(h or "").strip().lower() for h in next(it)]

        def col(*names):
            for n in names:
                if n in head:
                    return head.index(n)
            return None

        i_mat = col("material", "materialnummer", "artikelnummer")
        i_txt = col("materiallangtext", "materialkurztext", "kurztext", "bezeichnung")
        i_bst = col("best. ges.", "bestand", "best.ges.")
        i_pl = col("lagerplatz", "platz", "lgpbe", "lagerplatz (lgpbe)")
        i_kat = col("katalogseite", "katalog seite", "lorencic katalog 2024 seite", "katalog")
        if i_mat is None or i_txt is None:
            sys.exit("Spalten 'Material' und 'Materiallangtext' nicht gefunden.")
        for r in it:
            if r[i_mat]:
                bst = r[i_bst] if i_bst is not None else None
                rows.append((str(r[i_mat]).strip(), str(r[i_txt] or "").strip(), bst))
                if i_pl is not None and r[i_pl] not in (None, ""):
                    PLATZ[latin(str(r[i_mat]).strip())] = latin(str(r[i_pl]).strip())
                if i_kat is not None and str(r[i_kat] or "").strip() not in ("", "-"):
                    KATALOG[latin(str(r[i_mat]).strip())] = latin(str(r[i_kat]).strip())
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            first = f.readline()            # Trennzeichen an der Kopfzeile erkennen (nicht am Text)
            f.seek(0)
            delim = ";" if first.count(";") >= first.count(",") else ","
            head = [h.strip().lower() for h in first.split(delim)]
            i_pl = next((head.index(n) for n in ("lagerplatz", "platz", "lgpbe") if n in head), None)
            i_kat = next((head.index(n) for n in ("katalogseite", "katalog seite", "lorencic katalog 2024 seite") if n in head), None)
            for r in csv.reader(f, delimiter=delim):
                if r and r[0].strip() and r[0].strip().lower() not in ("material", "materialnummer", "artikelnummer"):
                    rows.append((r[0].strip(), r[1].strip() if len(r) > 1 else "", None))
                    if i_pl is not None and len(r) > i_pl and r[i_pl].strip():
                        PLATZ[latin(r[0].strip())] = latin(r[i_pl].strip())
                    if i_kat is not None and len(r) > i_kat and r[i_kat].strip() not in ("", "-"):
                        KATALOG[latin(r[0].strip())] = latin(r[i_kat].strip())
    return rows


# ------------------------------------------------------------------ Bilder
def http_get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Inventur-Etiketten)"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" not in str(e):
            raise
        # Zertifikat abgelaufen/unbekannt (z. B. Firmen-Laptop): nur für die eigene Firmenseite ohne Prüfung
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        r = urllib.request.urlopen(req, timeout=30, context=ctx)
    with r:
        data = r.read()
        charset = r.headers.get_content_charset() or "utf-8"
    return data if binary else data.decode(charset, "replace")


def find_image_url(mat):
    """Artikelnr.-Suche -> erste Produktseite im Ergebnis -> großes Bild."""
    html = http_get(BASE + "?" + urllib.parse.urlencode({"q": mat, "filter": "prdnr"}))
    i = html.find("Ergebnisse")                 # Navigation/Kategorien überspringen
    m = re.search(r'href="([^"#?]*?_\d+_3\.htm)"', html[i:] if i >= 0 else "")
    if not m:
        return None
    time.sleep(PAUSE)
    page_url = urllib.parse.urljoin(BASE, m.group(1))
    page = http_get(page_url)
    # Sicherheitscheck: Artikelnummer muss auf der Produktseite vorkommen
    if not re.search(r"(?<![A-Za-z0-9])" + re.escape(mat) + r"(?![A-Za-z0-9])", page, re.I):
        return None
    m = re.search(r'href="([^"]*0cache/[0-9a-f]{32}\.jpg)"', page) or \
        re.search(r'src="([^"]*0cache/[0-9a-f]{32}\.jpg)"', page)
    return urllib.parse.urljoin(page_url, m.group(1)) if m else None


def resolve_images(rows, bilder, download, progress=None, workers=4):
    """Bild je Material finden: erst Ordner 'bilder', dann (optional) lorencic.at, parallel mit wenigen Threads.
    progress(done, total) wird nach jedem abgefragten Artikel aufgerufen."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    web_dir = os.path.join(bilder, "_web")
    os.makedirs(web_dir, exist_ok=True)
    cache_file = "bild_cache.json"
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}
    images, missing, todo = {}, [], []

    def local_of(mat):
        sname = re.sub(r'[\\/:*?"<>|]', "_", mat)      # '/' u. ä. im Dateinamen ersetzen
        return next((p for e in ("jpg", "jpeg", "png")
                     for p in [os.path.join(bilder, f"{sname}.{e}")] if os.path.exists(p)), None)

    for mat, _ in rows:
        local = local_of(mat)
        if local:
            images[mat] = local
        elif download and mat not in todo:
            todo.append(mat)

    def work(mat):
        url = cache.get(mat)
        if not url:
            try:
                url = find_image_url(mat)
            except Exception as e:
                print(f"  {mat}: Abfrage fehlgeschlagen ({e})")
                url = None
            time.sleep(PAUSE)
        f = None
        if url:
            f = os.path.join(web_dir, hashlib.md5(url.encode()).hexdigest() + ".jpg")
            if not os.path.exists(f):
                try:
                    open(f, "wb").write(http_get(url, binary=True))
                    time.sleep(PAUSE)
                except Exception as e:
                    print(f"  {mat}: Bild-Download fehlgeschlagen ({e})")
                    f = None
        return mat, url, f

    if todo:
        lock, done = threading.Lock(), 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for fut in as_completed([ex.submit(work, m) for m in todo]):
                mat, url, f = fut.result()
                with lock:
                    done += 1
                    if url:
                        cache[mat] = url                 # nur Treffer merken, Fehlschläge werden neu versucht
                    if f and os.path.exists(f):
                        images[mat] = f
                    if done % 50 == 0:
                        json.dump(cache, open(cache_file, "w"))
                        print(f"  {done}/{len(todo)} Artikel geprüft", flush=True)
                if progress:
                    progress(done, len(todo))
        json.dump(cache, open(cache_file, "w"))

    for mat, text in rows:
        if mat not in images:
            missing.append((mat, text))
    return images, missing


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quelle", nargs="?", default="preisliste_artikel.csv",
                    help="Excel (.xlsx) oder CSV mit Material und Bezeichnung "
                         "(Standard: preisliste_artikel.csv im selben Ordner)")
    ap.add_argument("--artikel", nargs="+", metavar="NR",
                    help="nur diese Artikelnummern drucken, z. B. --artikel Z100 Z5-1 "
                         "(zweimal angegeben = zwei Etiketten)")
    ap.add_argument("--artikel-datei", metavar="DATEI",
                    help="Textdatei mit einer Artikelnummer pro Zeile")
    ap.add_argument("-o", "--out", default="etiketten.pdf")
    ap.add_argument("--bilder", default="bilder", help="Ordner mit eigenen Bildern (Standard: bilder)")
    ap.add_argument("--ohne-download", action="store_true", help="keine Bilder von lorencic.at laden")
    ap.add_argument("--nur-bestand", action="store_true", help="nur Artikel mit 'Best. ges.' > 0")
    ap.add_argument("--format", choices=list(FORMATS), default="165x63",
                    help="165x63 = 16,5 x 6,3 cm (Standard), a4 / a5 = ganze Seite quer, mini = 5,6 x 2,5 cm, avery3475 / avery3481 = Avery 70 x 36 / 70 x 41 mm Bogen, stopper = Regalstopper 10 x 4 cm")
    ap.add_argument("--ohne-rahmen", action="store_true", help="keinen Rahmen um die Etiketten zeichnen")
    ap.add_argument("--a4", action="store_true",
                    help="mehrere Etiketten pro A4-Seite mit Schnittmarken (165x63: 4 pro Seite)")
    ap.add_argument("--sammel", action="append", nargs="+", metavar="NR",
                    help="Sammeletikett (A4 hochkant): Artikelnummern einer Gruppe; Option mehrfach = mehrere Sammeletiketten")
    ap.add_argument("--breite", type=float, metavar="MM", help="eigene Breite in mm (zusammen mit --hoehe)")
    ap.add_argument("--hoehe", type=float, metavar="MM", help="eigene Höhe in mm (zusammen mit --breite)")
    ap.add_argument("--druckerrand", type=float, default=6, metavar="MM",
                    help="Etikettenbögen: Abstand zum Papierrand links/rechts, den dein Drucker nicht bedruckt (Standard 6)")
    ap.add_argument("--nur-mit-foto", action="store_true", help="nur Etiketten für Artikel drucken, zu denen ein Foto gefunden wird")
    ap.add_argument("--ohne-platz", action="store_true", help="Lagerplatz nicht aufs Etikett drucken")
    ap.add_argument("--ohne-katalog", action="store_true", help="Katalogseite nicht aufs Etikett drucken")
    ap.add_argument("--block", type=int, default=500, help="Etiketten pro PDF (Standard 500)")
    ap.add_argument("--max", type=int, help="nur die ersten N Artikel (zum Testen)")
    a = ap.parse_args()

    if not os.path.exists(a.quelle):         # Repo-Struktur: Liste auch in ../data suchen
        alt = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", a.quelle)
        if os.path.exists(alt):
            a.quelle = alt
    if not os.path.exists(a.quelle):
        sys.exit(f"Liste '{a.quelle}' nicht gefunden. Lege sie in den Ordner oder gib den Dateinamen an.")
    if a.breite or a.hoehe:
        if not (a.breite and a.hoehe):
            sys.exit("Bitte --breite und --hoehe zusammen angeben.")
        a.format = register_custom(a.breite, a.hoehe)
    global SHOW_PLATZ, SHOW_KATALOG, DRUCKERRAND
    DRUCKERRAND = a.druckerrand
    SHOW_PLATZ = not a.ohne_platz
    SHOW_KATALOG = not a.ohne_katalog
    rows = read_rows(a.quelle)
    if a.nur_bestand:
        rows = [r for r in rows if r[2] and float(r[2]) > 0]
    rows = [(m, t) for m, t, _ in rows]

    if a.sammel:
        lookup = {m.upper(): (m, t) for m, t in rows}
        groups = []
        for g in a.sammel:
            grp = [lookup[n.upper()] for n in g if n.upper() in lookup]
            for n in g:
                if n.upper() not in lookup:
                    print(f"  Achtung: {n} steht nicht in {a.quelle} und wird übersprungen")
            if grp:
                groups.append(grp)
        images, missing = resolve_images([r for g in groups for r in g], a.bilder, not a.ohne_download)
        build_pdf_sammel = build_sammel_pdf(groups, images, a.out, not a.ohne_rahmen)
        print(f"{len(groups)} Sammeletikett(en) -> {a.out}")
        return

    wanted = list(a.artikel or [])
    if a.artikel_datei:
        wanted += [z.strip() for z in open(a.artikel_datei, encoding="utf-8-sig") if z.strip()]
    if wanted:                                  # nur die genannten Artikel, in dieser Reihenfolge
        lookup = {m.upper(): (m, t) for m, t in rows}
        picked = []
        for nr in wanted:
            if nr.upper() in lookup:
                picked.append(lookup[nr.upper()])
            else:
                print(f"  Achtung: {nr} steht nicht in {a.quelle} und wird übersprungen")
        rows = picked
    if a.max:
        rows = rows[:a.max]
    print(f"{len(rows)} Artikel")

    images, missing = resolve_images(rows, a.bilder, not a.ohne_download)
    if a.nur_mit_foto:
        rows = [r for r in rows if r[0] in images]
        print(f"nur mit Foto: {len(rows)} Etiketten, {len(missing)} Artikel ohne Foto übersprungen")

    base, ext = os.path.splitext(a.out)
    blocks = [rows[i:i + a.block] for i in range(0, len(rows), a.block)] or [[]]
    for i, blk in enumerate(blocks, 1):
        out = a.out if len(blocks) == 1 else f"{base}_{i:03d}{ext}"
        build_pdf(blk, images, out, a.format, False, a.a4, not a.ohne_rahmen)
        print(f"{len(blk)} Etikett(en) -> {out}")

    with open("ohne_bild.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Material", "Bezeichnung"])
        w.writerows(missing)
    print(f"{len(rows) if a.nur_mit_foto else len(rows) - len(missing)} mit Bild, {len(missing)} ohne Bild (siehe ohne_bild.csv)")


if __name__ == "__main__":
    main()
