#!/usr/bin/env python3
"""Übernimmt einen SE16N-Export der Tabelle MEAN (Excel/CSV) in data/ean.csv.
Imports an SE16N export of table MEAN into data/ean.csv.  /  Uvozi SE16N izvoz tablice MEAN u data/ean.csv.

  python3 tools/ean_importieren.py MEAN.xlsx

Spalten / columns: Material, EAN/UPC-Code (optional Tp). Bestehende Einträge bleiben, neue/geänderte werden ergänzt.
Danach / then: python3 tools/build_web_data.py
"""
import csv, os, sys
import openpyxl

if len(sys.argv) < 2:
    sys.exit(__doc__)
src = sys.argv[1]
if src.lower().endswith((".xlsx", ".xlsm")):
    ws = openpyxl.load_workbook(src, data_only=True).active
    rows = [[("" if c is None else str(c).strip()) for c in r] for r in ws.iter_rows(values_only=True)]
else:
    with open(src, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";" if ";" in f.readline() else ","))
head = [h.lower() for h in rows[0]]
def col(*n):
    for x in n:
        if x in head:
            return head.index(x)
    sys.exit("Spalte nicht gefunden: " + "/".join(n))
iM, iE = col("material", "matnr"), col("ean/upc-code", "ean11", "ean")
iT = next((head.index(x) for x in ("tp", "eantp", "typ") if x in head), None)

ziel = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ean.csv")
bestand = {}
if os.path.exists(ziel):
    with open(ziel, encoding="utf-8-sig", newline="") as f:
        for r in csv.reader(f, delimiter=";"):
            if r and r[0] != "Material":
                bestand[r[1]] = r
neu = 0
for r in rows[1:]:
    if len(r) <= max(iM, iE) or not r[iM] or not r[iE]:
        continue
    eintrag = [r[iM], r[iE], r[iT] if iT is not None and len(r) > iT else ""]
    if bestand.get(r[iE]) != eintrag:
        neu += 1
    bestand[r[iE]] = eintrag
with open(ziel, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(["Material", "EAN", "Typ"])
    w.writerows(sorted(bestand.values()))
print(f"{neu} neu/geändert, {len(bestand)} gesamt -> {ziel}")
