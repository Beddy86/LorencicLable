# Lageretiketten

**Deutsch** · [English](README.en.md) · [Hrvatski](README.hr.md) · [Übersicht](README.md)

[![Seite veröffentlichen](https://github.com/Beddy86/LorencicLable/actions/workflows/veroeffentlichen.yml/badge.svg)](https://github.com/Beddy86/LorencicLable/actions/workflows/veroeffentlichen.yml)

**Live:** https://beddy86.github.io/LorencicLable/  ·  am Handy öffnen und „Zum Home-Bildschirm hinzufügen"

Größere Lageretiketten für Inventur und Regal, statt der kleinen SAP-Etiketten: Produktfoto, Artikelnummer groß, Barcode (Code 128) der Materialnummer, Bezeichnung, optional Lagerplatz und Katalogseite. Die Etiketten kommen als PDF heraus.

Es gibt zwei Wege, das zu nutzen:

| | Web-Version | Windows-Programm |
|---|---|---|
| Läuft | im Browser, auch am Handy | lokal auf dem PC (Python) |
| Installation | keine, nur einen Webspace oder Link | einmalig Python + Pakete |
| Fotos | 3.501 Katalogfotos eingebaut, eigene Fotos wählbar | Katalogfotos, eigene Fotos, Download von lorencic.at |
| Gut für | schnell am Handy, viele Kollegen | große Läufe (hunderte Etiketten), Excel-Listen |

## Inhalt

- [Schnellstart Web-Version](#schnellstart-web-version)
- [Eingabe](#eingabe)
- [Die Auswahlfelder](#die-auswahlfelder)
- [Fotos](#fotos)
- [Lagerplatz und Katalogseite](#lagerplatz-und-katalogseite)
- [Sammeletiketten](#sammeletiketten)
- [Drucken](#drucken)
- [Web-Version auf dem eigenen Webspace (z. B. WordPress)](#web-version-auf-dem-eigenen-webspace-z-b-wordpress)
- [Daten aktualisieren](#daten-aktualisieren)
- [Automatisch veröffentlichen (GitHub Pages)](#automatisch-veröffentlichen-github-pages)
- [Windows-Programm](#windows-programm)
- [Fehlersuche](#fehlersuche)
- [Technik](#technik)
- [Aufbau des Repos](#aufbau-des-repos)

## Schnellstart Web-Version

1. Seite öffnen.
2. Artikelnummern ins Feld schreiben, eine pro Zeile, zum Beispiel:
   ```
   Z100
   Z1425165*3
   ZM41014-RALH50
   ```
3. Format wählen, **Etiketten erstellen** tippen.
4. **PDF speichern** tippen und drucken.

Unten auf der Seite steht, wie viele Artikel und Fotos geladen sind. Steht dort keine Zahl, ist die Artikelliste nicht geladen (siehe [Fehlersuche](#fehlersuche)).

## Eingabe

Trennen geht mit Zeilenumbruch, Leerzeichen oder Komma. Die Groß-/Kleinschreibung ist egal.

| Schreibweise | Bedeutung |
|---|---|
| `Z100` | ein Etikett für Z100 |
| `Z100*3` | drei Etiketten für Z100 |
| `Z100@A-12-03` | Z100 mit Lagerplatz `A-12-03` von Hand |
| `Z100@A-12-03*2` | zwei Etiketten mit diesem Lagerplatz |

Nummern, die nicht in der Artikelliste stehen, werden übersprungen und nach dem Erstellen aufgelistet.

## Die Auswahlfelder

| Feld | Auswahl |
|---|---|
| **Format** | 16,5 × 6,3 cm (Standard) · Regalstopper 10 × 4 cm · Mini 5,6 × 2,5 cm · Avery Zweckform 3475 / 64 2280 (70 × 36 mm, 24 pro Bogen) · Avery Zweckform 3481 / 42 0778 (70 × 41 mm, 21 pro Bogen) · A4 quer · A5 quer · Eigene Größe (Breite × Höhe in mm, 20 bis 400) |
| **Art** | Einzeletiketten oder Sammeletikett (siehe unten) |
| **Seitenlayout** | mehrere Etiketten pro A4-Seite mit Schnittmarken, oder ein Etikett pro Seite |
| **Rahmen** | Rahmen um jedes Etikett, oder ohne |
| **Lagerplatz** | aufs Etikett drucken, oder nicht |
| **Katalogseite** | aufs Etikett drucken, oder nicht |
| **Fotos** | alle Artikel drucken, oder nur Artikel mit Foto |
| **Druckerrand** | erscheint nur bei Avery-Bögen, siehe [Drucken](#drucken) |

Die Avery-Formate sind fertig gestanzte Etikettenbögen. Dort wird immer ein Raster auf A4 gedruckt, ohne Schnittmarken.

## Fotos

Die Web-Version bringt die Katalogfotos mit. Fehlt eines, wird das Etikett ohne Foto gedruckt und der Artikel steht danach unter **Ohne Foto gedruckt**.

- **Einzeln nachreichen:** dort **Foto wählen** tippen (Galerie oder Kamera), danach **Mit den neuen Fotos neu erstellen**.
- **Mehrere auf einmal:** unter **Eigene Fotos und Lagerplätze** Fotos laden. Der Dateiname ist die Artikelnummer, zum Beispiel `Z100.jpg`. Eigene Fotos haben Vorrang vor den Katalogfotos.
- **Nur mit Foto drucken:** im Feld **Fotos** die Option „Nur Artikel mit Foto drucken" wählen. Artikel ohne Foto werden dann übersprungen und aufgelistet.

Weiße Ränder am Foto werden automatisch abgeschnitten, transparente Hintergründe werden weiß.

## Lagerplatz und Katalogseite

- Die Katalogseite kommt aus der Artikelliste (Spalte `Katalogseite`).
- Den Lagerplatz gibst du entweder von Hand an (`Z100@A-12-03`) oder lädst eine Liste: unter **Eigene Fotos und Lagerplätze** eine Excel- oder CSV-Datei mit den Spalten `Material` und `Lagerplatz` (optional `Katalogseite`). Spaltennamen werden ohne Rücksicht auf Groß-/Kleinschreibung erkannt, auch `Platz` und `LGPBE` gehen.
- Ist auf einem kleinen Etikett kein Platz dafür, entfällt die Fußzeile. Die Bezeichnung hat Vorrang.

## Sammeletiketten

Ein Blatt A4 hochkant pro Artikelgruppe, zum Beispiel alle Größen einer Arbeitshose: oben Foto, Nummernstamm und gemeinsame Beschreibung, darunter pro Größe eine Zeile mit Artikelnummer, Größe und Barcode.

1. Bei **Art** „Sammeletikett" wählen.
2. **Jede Zeile ist ein Blatt**, alle Nummern einer Zeile gehören zusammen:
   ```
   ZM41014-RALH50 ZM41014-RALH52 ZM41014-RALH54
   ZM42014-RABH50 ZM42014-RABH52
   ```
3. Das Foto stammt vom ersten Artikel der Zeile, der eines hat. Bei mehr als 9 Artikeln pro Gruppe gibt es weitere Seiten.

Der Text, der bei allen Artikeln gleich ist, wird oben zusammengefasst, nur die Unterschiede (zum Beispiel `Gr. 50`) stehen in der Zeile. Das klappt am besten, wenn die Bezeichnungen mit Komma gegliedert sind.

## Drucken

- Beim Drucken **100 % / „Tatsächliche Größe"** wählen, nicht „An Seite anpassen". Sonst stimmen die Maße nicht mehr.
- Bei Etikettenbögen (Avery) zuerst **eine Probeseite auf normalem Papier** drucken und gegen den Bogen ins Licht halten.
- **Druckerrand:** Viele Drucker drucken links und rechts nicht bis zum Papierrand. Bei den Avery-Formaten schiebt die Seite den Inhalt der äußeren Spalten nach innen, damit nichts abgeschnitten wird. Standard sind 6 mm. Wird bei dir nichts abgeschnitten, kannst du den Wert verkleinern, wird noch etwas abgeschnitten, vergrößern.
- **Barcode-Scanner:** Auf sehr kleinen Etiketten (Mini 5,6 × 2,5 cm) sind die Striche schmal. Vor einer großen Menge eine Probe scannen.

## Web-Version auf dem eigenen Webspace (z. B. WordPress)

Die Web-Version ist reines HTML und braucht keinen Server mit PHP oder Datenbank.

1. Diese Dateien in einen Ordner `etiketten` auf dem Webspace kopieren (FTP oder Dateimanager des Hostings): `index.html`, `manifest.json`, die vier Icons (`*.png`), `liste.json` und den Ordner `fotos/`. Zusammen etwa 47 MB.
2. Der Ordner muss **neben** `wp-content` liegen, nicht in der Mediathek. WordPress nimmt die Datentypen (`.json`, `.txt`) dort nicht an.
3. Aufrufen: `https://deine-domain.at/etiketten/`.
4. Soll sie in einer WordPress-Seite erscheinen, per iframe auf `/etiketten/` einbetten.

Hinweise:

- Die Seite lädt zwei Bibliotheken von `cdnjs.cloudflare.com` (jsPDF zum Erzeugen des PDFs, SheetJS zum Lesen von Excel). Blockiert eine Firewall das, die beiden Dateien auf den Webspace legen und die zwei `<script src=…>`-Zeilen in `index.html` darauf zeigen lassen.
- Das Firmenlogo im Kopf ist direkt in `index.html` eingebettet (Base64). Zum Austauschen die Zeile `<img class="logo" …>` ersetzen.
- Ohne Schutz kann jeder die Seite aufrufen. Soll das nicht sein, im Hosting einen Verzeichnisschutz (Passwort) für `/etiketten/` einrichten.
- Alles läuft im Browser. Eingegebene Nummern und Fotos werden nirgends hochgeladen.
- Wer die Seite über GitHub Pages ausliefert (siehe unten), braucht das alles nicht.

## Daten aktualisieren

Im Repo gibt es zwei Quellen:

| Quelle | Inhalt |
|---|---|
| `data/preisliste_artikel.csv` | Artikelliste. Spalten `Material;Materiallangtext;WGR;LGR;BME;Katalogseite` (Semikolon, UTF-8). Bei fehlender Katalogseite steht `-`. |
| `data/bilder/` | Neue oder ersetzte Fotos. Dateiname = Artikelnummer, z. B. `Z1234567.jpg` (JPG oder PNG). |

Der Grundbestand an Katalogfotos liegt fertig verpackt in `fotos/`. Fotos aus `data/bilder/` kommen oben drauf und haben Vorrang.

**Neuen Artikel hinzufügen**

1. Eine Zeile an `data/preisliste_artikel.csv` anhängen.
2. Optional das Foto in `data/bilder/` legen.
3. Committen und pushen. Danach baut GitHub die Seite neu (siehe [Automatisch veröffentlichen](#automatisch-veröffentlichen-github-pages)).

**Von Hand bauen** (zum Testen oder für einen eigenen Webspace), im Hauptordner des Repos:

```bash
python3 tools/build_web_data.py
```

Das Skript braucht nur Python 3, keine zusätzlichen Pakete. Es schreibt `liste.json` und ergänzt `fotos/`. Bestehende Foto-Pakete bleiben unverändert, neue Fotos kommen in neue Pakete. Mit `--kompakt` werden alle Pakete neu geschrieben (entfernt veraltete Fotos). Alle Optionen: `python3 tools/build_web_data.py --help`.

## Automatisch veröffentlichen (GitHub Pages)

Die Seite liegt unter **https://beddy86.github.io/LorencicLable/**. Der Workflow `.github/workflows/veroeffentlichen.yml` baut sie bei jedem Push auf `main` neu: Er nimmt `index.html` mit Icons, den Grundbestand in `fotos/`, dann `data/preisliste_artikel.csv` und `data/bilder/`, und veröffentlicht das Ergebnis.

**Einmalig einrichten**

1. Im Repo unter **Settings → Pages** bei **Source** „GitHub Actions" wählen.
2. Im Reiter **Actions** den Workflow **Seite veröffentlichen** einmal von Hand starten (**Run workflow**) oder einen beliebigen Push machen.

**Ab dann** genügt ein Push. Den Fortschritt und eventuelle Fehler zeigt der Reiter **Actions**. Der Workflow startet nicht bei reinen Änderungen an READMEs und am Windows-Programm.

**Am Handy installieren:** Seite im Browser öffnen und „Zum Home-Bildschirm hinzufügen" wählen. Dann startet sie wie eine App mit rotem Icon.

## Windows-Programm

Für große Läufe und Excel-Listen. Alles läuft lokal, es wird kein Port nach außen geöffnet (das Fenster hört nur auf `127.0.0.1`). Nur die Fotosuche auf lorencic.at geht ins Internet.

**Einmalig installieren**

1. Python 3 von python.org installieren, dabei „Add Python to PATH" ankreuzen.
2. Den Ordner `desktop/` auf den PC kopieren, zum Beispiel nach `C:\Etiketten`. Die Artikelliste findet das Programm im Ordner `data/` des Repos. Liegt der Ordner `desktop/` allein auf dem PC, die Datei `preisliste_artikel.csv` daneben legen.
3. `Einmal_installieren.bat` doppelklicken. Das installiert `openpyxl`, `reportlab` und `pillow` (siehe `requirements.txt`).

**Starten**

`Etiketten_starten.bat` doppelklicken. Ein schwarzes Fenster öffnet sich (offen lassen) und der Browser zeigt dieselbe Oberfläche wie die Web-Version. Die PDFs landen im Ordner `ausgabe`.

Dazu kommt:

- Fehlende Fotos werden von lorencic.at geholt (Option in der Oberfläche) und in `bilder/_web/` gemerkt.
- Eigene Fotos in den Ordner `bilder/` legen, `Z100.jpg`. Sie haben Vorrang.
- Lange Läufe zeigen den Fortschritt an.
- Gefundene Fotos merkt sich das Programm in `bild_cache.json`. Stimmt ein Foto nicht mehr, die Datei löschen.

**Kommandozeile**

```bash
# einzelne Artikel, mehrere pro A4-Seite
python3 desktop/etiketten.py --artikel Z100 Z5-1 Z170000 -o etiketten.pdf --a4

# ganze Excel-Liste (Spalten Material, Materiallangtext, optional Lagerplatz, Katalogseite)
python3 desktop/etiketten.py liste.xlsx -o etiketten.pdf

# anderes Format, nur mit Foto
python3 desktop/etiketten.py --artikel-datei nummern.txt --format avery3481 --nur-mit-foto -o avery.pdf

# eigene Größe 90 x 45 mm
python3 desktop/etiketten.py --artikel Z100 --breite 90 --hoehe 45 -o eigene.pdf

# Sammeletikett, jede --sammel-Gruppe ein Blatt
python3 desktop/etiketten.py --sammel ZM41014-RALH50 ZM41014-RALH52 --sammel ZM42014-RABH50 -o sammel.pdf
```

Alle Optionen: `python3 desktop/etiketten.py --help`. Formate: `165x63`, `a4`, `a5`, `stopper`, `mini`, `avery3475`, `avery3481`.

## Fehlersuche

| Problem | Ursache und Lösung |
|---|---|
| „Artikelliste konnte nicht geladen werden" | `liste.json` oder `fotos/` fehlt auf dem Server, oder das Hosting blockiert `.json` / `.txt`. Ordnerstruktur prüfen, die Dateien direkt im Browser aufrufen. |
| Weiße Seite, nichts reagiert | Die Skripte von `cdnjs.cloudflare.com` werden blockiert. Siehe Hinweis zur Firewall oben. |
| Foto fehlt | Es gibt kein Katalogfoto. Eigenes Foto wählen oder `Z….jpg` in `bilder/` legen. |
| Beim Windows-Programm Zertifikatsfehler (SSL) | Firmennetz mit eigener Zertifikatsprüfung. Das Programm weicht dafür nur bei lorencic.at aus. Neueste Version von `etiketten.py` nehmen. |
| Etikett ohne Foto, obwohl es online eines gibt | `bild_cache.json` löschen und neu erstellen. |
| `PDF speichern` tut nichts | Browser blockiert Downloads. Pop-up- und Download-Hinweis des Browsers erlauben. |
| Avery: Foto links oder Barcode rechts abgeschnitten | Druckerrand vergrößern (Standard 6 mm). |
| Sonderzeichen sind ein Fragezeichen | Zeichen außerhalb des Standard-Zeichensatzes (Windows-1252) können in der Schrift nicht dargestellt werden. `²` und `³` werden als `2` und `3` gedruckt. |
| Barcode lässt sich nicht scannen | Etikett mit 100 % drucken, größeres Format wählen, Scanner auf Code 128 prüfen. |

## Technik

- Barcode: Code 128, Zeichensatz B, bei längeren Ziffernfolgen automatisch C.
- Web-Version: eine einzige `index.html`, PDF mit jsPDF im Browser erzeugt, Daten als `liste.json` und Foto-Pakete (`fotos/pNNN.txt`, Base64, je etwa 300 KB, mit `fotos/index.json`). Fotos werden nur geladen, wenn sie gebraucht werden.
- Windows-Programm: Python mit reportlab, Pillow und openpyxl, Oberfläche als kleiner lokaler Webserver.
- Das Layout der beiden Versionen ist dasselbe und wurde Zeile für Zeile übertragen. Ändert sich ein Layout, in beiden anpassen (`desktop/etiketten.py` und `index.html`).

## Aufbau des Repos

```
index.html, manifest.json, *.png   die Seite (mit Handy-Icons)
liste.json, fotos/                 Grundbestand der Daten, fertig verpackt
data/preisliste_artikel.csv        Artikelliste (Quelle)
data/bilder/                       neue und eigene Fotos (Quelle)
tools/build_web_data.py            baut liste.json und fotos/
desktop/                           Windows-Programm
.github/workflows/                 automatische Veröffentlichung
```

## Lizenz

Alle Rechte vorbehalten, siehe [LICENSE](LICENSE). Die Seite darf benutzt werden. Kopieren, Ändern und Weitergeben des Codes und der Daten ist ohne schriftliche Zustimmung nicht erlaubt. Artikelliste und Katalogfotos stammen von lorencic.at.
