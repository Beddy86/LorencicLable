#!/usr/bin/env python3
"""Eingabefenster für die Lageretiketten (läuft im Browser, nur auf diesem Rechner).

Start per Doppelklick auf  Etiketten_starten.bat  (oder: python etiketten_fenster.py).
Im Ordner müssen liegen: etiketten.py, eine Artikelliste und der Ordner "bilder".
Artikelliste, in dieser Reihenfolge gesucht:
  artikelliste.xlsx / artikelliste.csv (z. B. SAP-Export)  ->  preisliste_artikel.csv
Fertige PDFs werden zusätzlich im Ordner "ausgabe" abgelegt.
"""
import json
import os
import re
import sys
import threading
import uuid
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)
import etiketten as E  # noqa: E402

OUT = os.path.join(HERE, "ausgabe")
BILDER = os.path.join(HERE, "bilder")
os.makedirs(OUT, exist_ok=True)
LOCK = threading.Lock()

DATEN = os.path.join(os.path.dirname(HERE), "data")      # Repo-Struktur: ../data/preisliste_artikel.csv
LISTE = next((p for d in (HERE, DATEN) for n in ("artikelliste.xlsx", "artikelliste.csv", "preisliste_artikel.csv")
              for p in [os.path.join(d, n)] if os.path.exists(p)), None)
LOOKUP = {}
if LISTE:
    for mat, text, _ in E.read_rows(LISTE):
        LOOKUP[mat.upper()] = (mat, text)

PAGE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lageretiketten</title>
<style>
  :root { --rot:#d4141c; --text:#1d1d1f; --grau:#6b6b70; --linie:#d9d9de; --bg:#f4f4f6; --karte:#fff; }
  * { box-sizing: border-box; }
  body { margin:0; font:16px/1.45 system-ui, "Segoe UI", Arial, sans-serif; color:var(--text); background:var(--bg); }
  header { background:var(--rot); color:#fff; padding:18px 24px; }
  header h1 { margin:0; font-size:22px; font-weight:700; letter-spacing:.2px; }
  header p { margin:2px 0 0; opacity:.9; font-size:14px; }
  main { max-width:760px; margin:24px auto; padding:0 16px; }
  .karte { background:var(--karte); border:1px solid var(--linie); border-radius:12px; padding:20px; margin-bottom:16px; }
  label.titel { display:block; font-weight:600; margin-bottom:6px; }
  textarea { width:100%; min-height:170px; font:17px/1.5 ui-monospace, Consolas, monospace; padding:12px;
             border:1px solid var(--linie); border-radius:8px; resize:vertical; }
  textarea:focus { outline:2px solid var(--rot); outline-offset:1px; }
  .hinweis { color:var(--grau); font-size:14px; margin:6px 0 0; }
  .optionen { display:grid; grid-template-columns:1fr 1fr; gap:10px 24px; margin-top:16px; }
  .optionen label { display:flex; gap:8px; align-items:center; cursor:pointer; }
  .optionen label.feld { flex-direction:column; align-items:stretch; gap:4px; font-weight:600; font-size:14px; }
  .optionen select, .optionen input[type=number] { font:16px system-ui, "Segoe UI", Arial, sans-serif; padding:9px 10px; border:1px solid var(--linie);
        border-radius:8px; background:#fff; color:var(--text); font-weight:400; }
  .optionen select { width:100%; min-width:0; }
  .optionen label.feld { min-width:0; }
  .optionen { grid-template-columns:minmax(0,1fr) minmax(0,1fr); }
  .optionen input[type=number] { width:90px; }
  .zeile { font-weight:400; display:flex; gap:8px; align-items:center; }
  .optionen .voll { grid-column:1 / -1; }
  button { background:var(--rot); color:#fff; border:0; border-radius:8px; padding:14px 26px; font-size:17px;
           font-weight:600; cursor:pointer; margin-top:18px; }
  button:disabled { opacity:.6; cursor:wait; }
  .ok { border-left:5px solid #1a7f37; } .warn { border-left:5px solid #b7791f; } .fehler { border-left:5px solid var(--rot); }
  .pdf { display:inline-block; background:#1a7f37; color:#fff; text-decoration:none; padding:12px 22px;
         border-radius:8px; font-weight:600; margin:10px 0 4px; }
  .muted { color:var(--grau); } code { background:#eee; padding:1px 5px; border-radius:4px; }
  ul { margin:6px 0 0; padding-left:20px; } footer { color:var(--grau); font-size:13px; text-align:center; margin:8px 0 24px; }
</style></head>
<body>
<header><h1>Lageretiketten</h1><p>Artikelnummern eingeben, Etiketten als PDF erstellen</p></header>
<main>
  <div class="karte">
    <label class="titel" for="art">Artikelnummern (eine pro Zeile)</label>
    <textarea id="art" placeholder="Z100&#10;Z5-1&#10;Z170000*3" autofocus></textarea>
    <p class="hinweis">Mehrere Etiketten für einen Artikel: <code>Z170000*3</code> = dreimal.
       Trennen geht mit Zeilenumbruch, Leerzeichen oder Komma.</p>
    <div class="optionen">
      <label class="feld voll">Format
        <select id="fmt">
          <option value="165x63" selected>16,5 × 6,3 cm (Standard)</option>
          <option value="stopper">Regalstopper 10 × 4 cm</option>
          <option value="mini">Mini 5,6 × 2,5 cm</option>
          <option value="avery3475">Avery 3475 / 64 2280 (70 × 36 mm, 24 pro Bogen)</option>
          <option value="avery3481">Avery 3481 / 42 0778 (70 × 41 mm, 21 pro Bogen)</option>
          <option value="a4">A4 quer (1 Etikett pro Blatt)</option>
          <option value="a5">A5 quer (mit A4-Haken: 2 pro Blatt)</option>
          <option value="custom">Eigene Größe …</option>
        </select></label>
      <label class="feld voll" id="eigen" style="display:none">Eigene Größe
        <span class="zeile"><input type="number" id="cw" value="100" min="20" max="400" step="0.5"> mm breit ×
        <input type="number" id="ch" value="50" min="20" max="400" step="0.5"> mm hoch</span></label>
      <label class="feld">Art
        <select id="art_typ">
          <option value="einzel" selected>Einzeletiketten</option>
          <option value="sammel">Sammeletikett (A4, Zeile = Blatt)</option>
        </select></label>
      <label class="feld">Seitenlayout
        <select id="a4">
          <option value="1" selected>Mehrere pro A4 (Schnittmarken)</option>
          <option value="0">Ein Etikett pro Seite</option>
        </select></label>
      <label class="feld">Rahmen
        <select id="rahmen">
          <option value="1" selected>Rahmen um jedes Etikett</option>
          <option value="0">Ohne Rahmen</option>
        </select></label>
      <label class="feld">Lagerplatz
        <select id="platz">
          <option value="1" selected>Aufs Etikett drucken</option>
          <option value="0">Nicht drucken</option>
        </select></label>
      <label class="feld">Katalogseite
        <select id="katalog">
          <option value="1" selected>Aufs Etikett drucken</option>
          <option value="0">Nicht drucken</option>
        </select></label>
      <label class="feld">Fotos
        <select id="fotos">
          <option value="dl" selected>Fehlende von lorencic.at holen</option>
          <option value="lokal">Nur vorhandene (kein Download)</option>
          <option value="nur_dl">Nur mit Foto drucken (fehlende holen)</option>
          <option value="nur_lokal">Nur mit Foto drucken (kein Download)</option>
        </select></label>
      <label class="feld" id="randbox" style="display:none">Druckerrand (Avery-Bögen)
        <span class="zeile"><input type="number" id="rand" value="6" min="0" max="15" step="0.5"> mm</span></label>
    </div>
    <p class="hinweis">Lagerplatz kommt aus der Spalte "Lagerplatz" der Artikelliste oder von Hand: <code>Z100@A-12-03</code>.
       Druckerrand: so viel Rand lässt dein Drucker links/rechts frei; wird nichts mehr abgeschnitten, kann der Wert kleiner werden.</p>
    <button id="go">Etiketten erstellen</button>
  </div>
  <div id="res"></div>
  <footer>Artikelliste: {{LISTE}}</footer>
</main>
<script>
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function umschalten() {
  const f = $('fmt').value;
  $('eigen').style.display = f === 'custom' ? '' : 'none';
  $('randbox').style.display = f.startsWith('avery') ? '' : 'none';
}
$('fmt').onchange = umschalten; umschalten();
const liste = a => '<ul>' + a.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul>';
function zeige(d) {
  let h = '';
  if (!d.ok) {
    h = '<div class="karte fehler"><b>' + esc(d.meldung) + '</b>' + (d.fehlend && d.fehlend.length ?
        '<p>Nicht in der Liste:</p>' + liste(d.fehlend) : '') + '</div>';
  } else {
    h = '<div class="karte ok"><b>' + d.anzahl + ' Etikett' + (d.anzahl == 1 ? '' : 'en') + ' erstellt</b><br>' +
        '<a class="pdf" href="' + d.pdf + '" target="_blank">PDF öffnen und drucken</a>' +
        '<div class="muted">Gespeichert in: ' + esc(d.datei) + '</div></div>';
    if (d.fehlend.length) h += '<div class="karte warn"><b>Nicht in der Liste (übersprungen):</b>' + liste(d.fehlend) + '</div>';
    if (d.uebersprungen && d.uebersprungen.length) h += '<div class="karte warn"><b>Ohne Foto übersprungen (nicht gedruckt):</b>' + liste(d.uebersprungen) + '</div>';
    if (d.ohne_bild.length) h += '<div class="karte warn"><b>Ohne Foto gedruckt:</b>' + liste(d.ohne_bild) + '</div>';
  }
  $('res').innerHTML = h;
}
$('go').onclick = async () => {
  const btn = $('go'); btn.disabled = true;
  $('res').innerHTML = '<div class="karte"><span class="muted">Etiketten werden erstellt …</span></div>';
  try {
    const r = await fetch('/api/erstellen', { method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ artikel: $('art').value, a4: $('a4').value === '1', rahmen: $('rahmen').value === '1',
        download: $('fotos').value.endsWith('dl'), platz: $('platz').value === '1', breite: $('cw').value,
        sammel: $('art_typ').value === 'sammel', rand: $('rand').value, hoehe: $('ch').value,
        nur_foto: $('fotos').value.startsWith('nur'), katalog: $('katalog').value === '1',
        format: $('fmt').value }) });
    const d = await r.json();
    if (!d.job) { zeige(d); btn.disabled = false; return; }
    const poll = async () => {
      try {
        const s = await (await fetch('/api/status/' + d.job)).json();
        if (s.state === 'fertig') { zeige(s.result); btn.disabled = false; return; }
        const t = s.total ? ' Fotos geprüft: ' + s.done + ' von ' + s.total : '';
        $('res').innerHTML = '<div class="karte"><span class="muted">Etiketten werden erstellt …' + t +
          '<br>Das kann bei vielen Artikeln einige Minuten dauern. Fenster bitte offen lassen.</span></div>';
      } catch (e) { /* kurzer Aussetzer, einfach weiter fragen */ }
      setTimeout(poll, 800);
    };
    poll();
  } catch (e) {
    $('res').innerHTML = '<div class="karte fehler"><b>Fehler:</b> ' + esc(e) + '</div>';
    btn.disabled = false;
  }
};
</script></body></html>
"""


def parse(text):
    out = []
    for tok in re.split(r"[\s,;]+", text.strip()):
        if not tok:
            continue
        n, platz = 1, ""
        m = re.match(r"^(.+?)\*(\d+)$", tok)             # Anzahl am Ende: Z100*3 oder Z100@A-12*3
        if m:
            tok, n = m.group(1), min(int(m.group(2)), 500)
        if "@" in tok:                                 # Z100@A-12-03 = Lagerplatz von Hand
            tok, platz = tok.split("@", 1)
        out.append((tok, n, platz))
    return out


def erstellen_sammel(data, progress=None):
    groups, fehlend = [], []
    for line in data.get("artikel", "").splitlines():
        grp = []
        for nr, _n, _p in parse(line):
            if nr.upper() in LOOKUP:
                if LOOKUP[nr.upper()] not in grp:
                    grp.append(LOOKUP[nr.upper()])
            else:
                fehlend.append(nr)
        if grp:
            groups.append(grp)
    if not groups:
        return {"ok": False, "fehlend": fehlend, "meldung": "Keine gültigen Artikelnummern eingegeben."}
    with LOCK:
        images, missing = E.resolve_images([r for g in groups for r in g], BILDER, bool(data.get("download")), progress)
        name = datetime.now().strftime("Sammeletiketten_%Y%m%d_%H%M%S.pdf")
        pfad = os.path.join(OUT, name)
        E.build_sammel_pdf(groups, images, pfad, bool(data.get("rahmen")))
    ohne_gruppen = sorted({g[0][0] for g in groups if not any(m in images for m, _ in g)})
    return {"ok": True, "anzahl": len(groups), "pdf": "/pdf/" + name, "datei": pfad, "fehlend": fehlend,
            "ohne_bild": ohne_gruppen, "uebersprungen": []}


def erstellen(data, progress=None):
    if not LOOKUP:
        return {"ok": False, "meldung": "Keine Artikelliste gefunden (preisliste_artikel.csv fehlt im Ordner)."}
    if data.get("sammel"):
        return erstellen_sammel(data, progress)
    rows, fehlend = [], []
    E.SHOW_PLATZ = bool(data.get("platz", True))
    E.SHOW_KATALOG = bool(data.get("katalog", True))
    try:
        E.DRUCKERRAND = min(15.0, max(0.0, float(data.get("rand", 6))))
    except (TypeError, ValueError):
        E.DRUCKERRAND = 6.0
    for nr, n, platz in parse(data.get("artikel", "")):
        if nr.upper() in LOOKUP:
            if platz:
                E.PLATZ[E.latin(LOOKUP[nr.upper()][0])] = E.latin(platz)
            rows += [LOOKUP[nr.upper()]] * n
        else:
            fehlend.append(nr)
    if not rows:
        return {"ok": False, "fehlend": fehlend,
                "meldung": "Keine gültigen Artikelnummern eingegeben." if not fehlend else "Keine der Nummern steht in der Liste."}
    fmt = data.get("format") if data.get("format") in E.FORMATS or data.get("format") == "custom" else "165x63"
    if fmt == "custom":
        try:
            w, h = float(data.get("breite")), float(data.get("hoehe"))
        except (TypeError, ValueError):
            return {"ok": False, "fehlend": [], "meldung": "Bitte Breite und Höhe in mm eingeben."}
        if not (20 <= w <= 400 and 20 <= h <= 400):
            return {"ok": False, "fehlend": [], "meldung": "Die Abmessungen müssen zwischen 20 und 400 mm liegen."}
        E.register_custom(w, h)
    with LOCK:
        images, missing = E.resolve_images([(m, t) for m, t in rows], BILDER, bool(data.get("download")), progress)
        nur_foto = bool(data.get("nur_foto"))
        if nur_foto:
            rows = [r for r in rows if r[0] in images]
            if not rows:
                return {"ok": False, "fehlend": [], "meldung": "Zu keinem der Artikel wurde ein Foto gefunden – nichts zu drucken."}
        name = datetime.now().strftime("Etiketten_%Y%m%d_%H%M%S.pdf")
        pfad = os.path.join(OUT, name)
        E.build_pdf(rows, images, pfad, fmt, False, bool(data.get("a4")), bool(data.get("rahmen")))
    ohne = sorted({m for m, _ in missing})
    return {"ok": True, "anzahl": len(rows), "pdf": "/pdf/" + name, "datei": pfad,
            "fehlend": fehlend, "ohne_bild": [] if nur_foto else ohne, "uebersprungen": ohne if nur_foto else []}


JOBS = {}


def start_job(data):
    """Erstellung im Hintergrund starten (die Fotosuche kann bei vielen Artikeln Minuten dauern)."""
    jid = uuid.uuid4().hex[:12]
    job = JOBS[jid] = {"state": "laeuft", "done": 0, "total": 0, "result": None}

    def progress(done, total):
        job["done"], job["total"] = done, total

    def run():
        try:
            job["result"] = erstellen(data, progress)
        except Exception as e:
            job["result"] = {"ok": False, "meldung": f"Fehler: {e}"}
        job["state"] = "fertig"

    threading.Thread(target=run, daemon=True).start()
    return jid


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (ConnectionError, OSError):          # Browser hat die Verbindung schon geschlossen
            pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            if LISTE:
                info = f"{LISTE} ({len(LOOKUP):,} Artikel)".replace(",", ".")
            else:
                info = "keine gefunden!"
            self._send(200, PAGE.replace("{{LISTE}}", info).encode("utf-8"), "text/html; charset=utf-8")
        elif self.path.startswith("/api/status/"):
            job = JOBS.get(self.path.rsplit("/", 1)[-1])
            if not job:
                return self._send(404, b'{"state": "unbekannt"}', "application/json")
            self._send(200, json.dumps(job).encode("utf-8"), "application/json")
        elif self.path.startswith("/pdf/"):
            name = os.path.basename(unquote(self.path[5:]))
            f = os.path.join(OUT, name)
            if name.endswith(".pdf") and os.path.isfile(f):
                self._send(200, open(f, "rb").read(), "application/pdf")
            else:
                self._send(404, b"nicht gefunden", "text/plain")
        else:
            self._send(404, b"nicht gefunden", "text/plain")

    def do_POST(self):
        if self.path != "/api/erstellen":
            return self._send(404, b"nicht gefunden", "text/plain")
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            res = {"job": start_job(data)}
        except Exception as e:                      # Fehler im Fenster anzeigen statt abstürzen
            res = {"ok": False, "meldung": f"Fehler: {e}"}
        self._send(200, json.dumps(res).encode("utf-8"), "application/json")


def main():
    server = None
    for port in range(8765, 8776):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if not server:
        sys.exit("Kein freier Port gefunden.")
    url = f"http://127.0.0.1:{port}/"
    print(f"Lageretiketten läuft: {url}")
    print("Dieses schwarze Fenster offen lassen. Zum Beenden: Fenster schließen oder Strg+C.")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
