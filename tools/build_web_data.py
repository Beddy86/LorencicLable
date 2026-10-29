#!/usr/bin/env python3
"""Erzeugt die Datendateien der Web-Version: liste.json, fotos/index.json, fotos/pNNN.txt.
Builds the data files of the web version.  /  Izrađuje podatkovne datoteke web verzije.

Inkrementell / incremental / inkrementalno:
  Bereits vorhandene Foto-Pakete bleiben unverändert. Neue oder geänderte Fotos aus --bilder
  kommen in neue Pakete. So ändert sich pro Update nur wenig im Repo.
  Existing photo packs stay untouched; new or changed photos go into new packs.
  Postojeći paketi ostaju nepromijenjeni; nove ili izmijenjene fotografije idu u nove pakete.

Aufruf / Usage / Pokretanje (im Repo-Hauptordner / from the repo root / iz glavne mape):
  python3 tools/build_web_data.py

Optionen / options / opcije:
  liste        CSV (Standard / default: data/preisliste_artikel.csv)
  --bilder     Ordner mit Fotos, Dateiname = Artikelnummer (Standard: data/bilder)
  --out        Zielordner mit index.html (Standard: .)
  --kompakt    alle Pakete neu schreiben (entfernt veraltete Fotos aus den Paketen)
  --paket      Zielgröße eines Pakets in Bytes (Standard 300000)
"""
import argparse, base64, csv, glob, json, os, re, sys

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("liste", nargs="?", default="data/preisliste_artikel.csv")
ap.add_argument("--bilder", nargs="*", default=["data/bilder"])
ap.add_argument("--out", default=".")
ap.add_argument("--kompakt", action="store_true")
ap.add_argument("--paket", type=int, default=300_000)
a = ap.parse_args()

if not os.path.exists(a.liste):
    sys.exit(f"Liste nicht gefunden / list not found / popis nije pronađen: {a.liste}")
fotodir = os.path.join(a.out, "fotos")
os.makedirs(fotodir, exist_ok=True)

# ---- Artikelliste -> liste.json
rows = []
with open(a.liste, newline="", encoding="utf-8-sig") as f:
    r = csv.reader(f, delimiter=";")
    next(r)
    for x in r:
        if x and x[0].strip():
            k = x[5].strip() if len(x) > 5 else ""
            rows.append([x[0].strip(), x[1].strip() if len(x) > 1 else "", "" if k in ("-", "") else k])
with open(os.path.join(a.out, "liste.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))

# ---- EAN-Zuordnung (optional) -> ean.json  (EAN ohne führende Nullen -> Material)
_ean = os.path.join(os.path.dirname(os.path.abspath(a.liste)), "ean.csv")
if os.path.exists(_ean):
    _m = {}
    with open(_ean, encoding="utf-8-sig", newline="") as f:
        for r in csv.reader(f, delimiter=";"):
            if r and r[0] != "Material" and len(r) > 1 and r[1].strip().lstrip("0"):
                _m[r[1].strip().lstrip("0")] = r[0].strip()
    with open(os.path.join(a.out, "ean.json"), "w", encoding="utf-8") as f:
        json.dump(_m, f, separators=(",", ":"))
    print(f"{len(_m)} EAN-Zuordnungen -> ean.json")

# ---- Zusatzseite abholung.html (Abholungen erfassen) in den Zielordner kopieren
import shutil
_ab = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "abholung.html")
if os.path.exists(_ab) and os.path.abspath(a.out) != os.path.dirname(_ab):
    shutil.copy(_ab, os.path.join(a.out, "abholung.html"))

# ---- Fotos
safe = lambda m: re.sub(r'[\\/:*?"<>|]', "_", m)
bysafe = {}
for m, _, _ in rows:
    bysafe.setdefault(safe(m).upper(), m)

idx_path = os.path.join(fotodir, "index.json")
idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
_packs = {}

def pack_bytes(n):
    if n not in _packs:
        with open(os.path.join(fotodir, f"p{n:03d}.txt")) as f:
            _packs[n] = base64.b64decode(f.read())
    return _packs[n]

def foto_bytes(m):
    n, off, ln = idx[m]
    return pack_bytes(n)[off:off + ln]

neu = {}
for d in a.bilder:
    for p in sorted(glob.glob(os.path.join(d, "*"))):
        stem, ext = os.path.splitext(os.path.basename(p))
        if not os.path.isfile(p) or ext.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        m = bysafe.get(stem.upper(), stem)
        b = open(p, "rb").read()
        if m in idx and foto_bytes(m) == b:
            continue                                   # schon drin, unverändert
        neu[m] = b

def schreibe(items, start):
    """items: dict Material -> bytes; schreibt Pakete ab Nummer start, ergänzt idx; gibt nächste Nummer zurück."""
    pack, cur = start, bytearray()
    def flush():
        nonlocal pack, cur
        if cur:
            with open(os.path.join(fotodir, f"p{pack:03d}.txt"), "w") as f:
                f.write(base64.b64encode(cur).decode())
            pack += 1
            cur = bytearray()
    for m in sorted(items):
        b = items[m]
        if cur and len(cur) + len(b) > a.paket:
            flush()
        idx[m] = [pack, len(cur), len(b)]
        cur += b
    flush()
    return pack

if a.kompakt:
    alle = {m: foto_bytes(m) for m in idx}
    alle.update(neu)
    for old in glob.glob(os.path.join(fotodir, "p*.txt")):
        os.remove(old)
    _packs.clear(); idx.clear()
    nxt = schreibe(alle, 0)
else:
    nxt = max((v[0] for v in idx.values()), default=-1) + 1
    nxt = schreibe(neu, nxt) if neu else nxt

with open(idx_path, "w") as f:
    json.dump(idx, f, separators=(",", ":"))
print(f"{len(rows)} Artikel, {len(idx)} Fotos ({len(neu)} neu/geändert) -> {a.out}")
