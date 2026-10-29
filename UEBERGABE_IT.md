# Übergabe an die IT – Lageretiketten und Abholung erfassen

Stand: 29.10.2026 · Ansprechpartner Fachbereich: Peter Müller (PMU)

## 1. Was ist das?

Zwei kleine Web-Anwendungen für das Lager. Sie laufen komplett im Browser (Handy oder PC), es gibt **keinen eigenen Server und keine Datenbank**.

| Anwendung | Datei | Zweck |
|---|---|---|
| Lageretiketten | `index.html` | Etiketten als PDF drucken: Foto, Artikelnummer, Code-128-Barcode, Bezeichnung. Formate: Regalstopper 10×4 cm, Avery 3481 (70×41 mm), A4 quer, A5 quer, eigene Größe. Sammeletiketten (mehrere Artikel auf einem Etikett). Barcode-Scanner mit Handy-Kamera. |
| Abholung erfassen | `abholung.html` | Lagermitarbeiter scannen Artikel, die abgeholt werden. Ergebnis: PDF (Beleg) plus Textdatei zum Einfügen in VA01. Versand per Mail vom Handy. |

Aktuell läuft beides auf GitHub Pages: https://beddy86.github.io/LorencicLable/ (Quellcode: Repository `Beddy86/LorencicLable`).

## 2. Technischer Aufbau

- Reines HTML/JavaScript, jede Seite ist eine einzige Datei. Kein Build-Schritt für den Code selbst.
- Externe Bibliotheken, zur Laufzeit von CDN geladen:
  - jsPDF 2.5.1 (cdnjs.cloudflare.com) – PDF-Erzeugung
  - SheetJS 0.18.5 (cdnjs.cloudflare.com) – Excel/CSV lesen (nur `index.html`)
  - ZXing 0.21.3 (cdn.jsdelivr.net) – Barcode-Erkennung, falls der Browser keinen eigenen Detektor hat (iPhone)
  - Tesseract.js 5.1.1 und Sprachdaten `@tesseract.js-data/eng` (cdn.jsdelivr.net) – Texterkennung als Reserve im Foto-Modus, wird erst bei Bedarf geladen (ca. 5–10 MB)
  - **Für ein internes System sollten diese Bibliotheken lokal abgelegt werden**, wenn die Handys keinen freien Internetzugang haben oder CDNs gesperrt sind.
- Code-128-Barcode und Seitenaufbau sind selbst programmiert (keine Barcode-Bibliothek).
- Anforderung an den Webserver: statische Dateien ausliefern, **HTTPS ist Pflicht** (der Browser erlaubt die Kamera nur über HTTPS).
- Gespeichert wird nur im Browser des Geräts (`localStorage`): offene Abholliste, gewählter Ersteller und Empfänger.

## 3. Dateien und Datenfluss

```
index.html            Etiketten-Seite
abholung.html         Abholung-Seite
liste.json            Artikelliste  [Material, Bezeichnung, Kategorie]   (wird erzeugt)
ean.json              EAN-Zuordnung für den Scanner                       (wird erzeugt)
fotos/index.json      Verzeichnis der Foto-Pakete                         (wird erzeugt)
fotos/pNNN.txt        Fotos als Base64, in Paketen zu ca. 300 KB          (wird erzeugt)
manifest.json, *.png  Icons / Startbildschirm-Symbol am Handy
data/
  preisliste_artikel.csv   Quelle: Artikelstamm (Semikolon, Spalten Material;Materiallangtext;WGR;LGR;BME;Katalogseite)
  ean.csv                  Quelle: EAN-Zuordnung (Material;EAN;Typ) aus SAP, Tabelle MEAN
  bilder/<Artikel>.jpg     neue Fotos, Dateiname = Artikelnummer
tools/
  build_web_data.py        erzeugt liste.json, ean.json, fotos/* aus data/*
  ean_importieren.py       übernimmt einen SE16N-Export (MEAN) in data/ean.csv
.github/workflows/veroeffentlichen.yml   baut und veröffentlicht automatisch bei jedem Push
desktop/                   (optional) Windows-Programm mit gleicher Funktion, nicht aktuell
```

Die Seiten laden `liste.json`, `ean.json` und die Foto-Pakete beim Start per `fetch` vom selben Server. Es gibt keine weiteren Schnittstellen.

## 4. Betrieb auf eigenem Server

1. Repository klonen, Python 3.12 und `pip install openpyxl` (nur für die EAN-Übernahme).
2. Daten erzeugen: `python3 tools/build_web_data.py data/preisliste_artikel.csv --bilder data/bilder --out _site`
   (legt auch `abholung.html`-Kopie, `liste.json`, `ean.json` und `fotos/` in `_site/` ab; `index.html`, `manifest.json`, `*.png` und den Ordner `fotos` vorher dorthin kopieren, siehe Workflow-Datei `.github/workflows/veroeffentlichen.yml`, Schritt „Seite zusammenbauen“).
3. Den Inhalt von `_site/` auf einen HTTPS-Webserver legen.

Der Workflow auf GitHub ist die Referenz, welche Dateien ausgeliefert werden müssen.

## 5. Laufende Pflege (Fachbereich)

| Aufgabe | Vorgehen |
|---|---|
| Neue Artikel / geänderte Bezeichnung | Zeile in `data/preisliste_artikel.csv` ergänzen bzw. ändern |
| Neues Foto | JPG als `data/bilder/<Artikelnummer>.jpg` ablegen |
| EAN-Zuordnung aktualisieren | SE16N, Tabelle MEAN exportieren, dann `python3 tools/ean_importieren.py MEAN.xlsx` |
| Veröffentlichen | Push nach `main`, der Workflow baut und veröffentlicht in 1–2 Minuten |

Bisher wurde das über Claude (KI-Assistent) erledigt: Mails „Artikelanlage“ / „Artikelfoto“ werden eingelesen, die Daten gebaut und gepusht. Das kann die IT übernehmen oder automatisieren (z. B. Anlage-Mail → CSV-Zeile).

## 6. Einstellungen in `abholung.html` (zum Anpassen)

- **Ersteller-Liste:** `<select id="mitarbeiter">` (PMU, KSC, TVA, MRO, SPA, AVU)
- **Empfänger-Liste:** `<select id="empf">` (vier Mailadressen)
- **Mail-Betreff:** Konstante `betreff = 'ABHOLUNG HANDYSCAN'` in der Funktion des Senden-Knopfs
- **PDF-Layout:** Funktion `baueBlatt()` (Spalten Pos, Artikelnummer, Menge, Bezeichnung)
- **Textdatei für VA01:** pro Zeile `Material<TAB>Menge`, Dateiname = PDF-Name + `_VA01.txt`

## 7. Bekannte Einschränkungen (wichtig für ein internes System)

1. **Mailversand vom Handy:** Der Versand nutzt die Teilen-Funktion des Browsers (Web Share API). Dabei gilt:
   - **Betreff und Empfänger lassen sich nicht vorbefüllen** (iOS Mail ignoriert sie beim Teilen von Dateien). Deshalb steht „ABHOLUNG HANDYSCAN“ im Dateinamen und in der ersten Textzeile, und eine Outlook-Regel sortiert die Mails ein. Der Empfänger wird in die Zwischenablage kopiert.
   - **Saubere Lösung für das eigene System:** Die Seite schickt PDF + Textdatei per HTTPS an einen internen Endpunkt, der die Mail über den Exchange-/SMTP-Server verschickt (fester Betreff, fester Empfänger, ohne Handy-Mailprogramm). Dafür braucht es einen kleinen Server-Teil.
2. **Alte Etiketten** sind teilweise verblasst. Der Scanner rechnet dafür das Kamerabild auf (Kontrast, Schärfe, Schwellwert), der Foto-Knopf und die Texterkennung sind Reserve. Sehr schlechte Etiketten bleiben schwierig; Artikelnummer kann immer von Hand eingegeben werden.
3. **EAN-Zuordnung** ist ein Stand aus SAP (MEAN). Sie muss bei neuen Artikeln/EANs nachgezogen werden.
4. **Datenschutz:** Es werden keine Personendaten an Dritte geschickt. Alle Daten bleiben im Browser bzw. gehen nur über die vom Mitarbeiter ausgelöste Mail. Die Bibliotheken kommen von öffentlichen CDNs (siehe Punkt 2).
5. **Fotos** liegen als Base64 im Repository (aktuell ca. 49 MB). Bei sehr vielen Artikeln lohnt sich eine Auslieferung als normale Bilddateien.

## 8. Mögliche Integration in euer System

- `index.html` und `abholung.html` lassen sich als eigenständige Seiten in ein Intranet einbinden (iframe oder eigener Pfad).
- Die Abholung könnte statt PDF/Mail direkt einen **Kundenauftrag in SAP anlegen** (VA01 per BAPI/OData) – die Positionen liegen schon als Liste `Material, Menge` vor.
- Die Artikelliste (`liste.json`) und EAN-Zuordnung (`ean.json`) könnten direkt aus SAP generiert werden statt aus CSV-Dateien.

## 9. Test nach Änderungen

- Seite am Handy über HTTPS öffnen, „Artikel scannen“: Kamera-Freigabe muss kommen.
- Einen Barcode scannen, Artikel erscheint mit Bezeichnung.
- „Nur PDF speichern“ prüfen: Spalten Pos, Artikelnummer, Menge, Bezeichnung.
- Versand: PDF und `_VA01.txt` müssen an der Mail hängen.
