# Skladišne etikete

[Deutsch](README.de.md) · [English](README.en.md) · **Hrvatski** · [Pregled](README.md)

[![Seite veröffentlichen](https://github.com/Beddy86/LorencicLable/actions/workflows/veroeffentlichen.yml/badge.svg)](https://github.com/Beddy86/LorencicLable/actions/workflows/veroeffentlichen.yml)

**Uživo:** https://beddy86.github.io/LorencicLable/  ·  otvorite na mobitelu i odaberite „Dodaj na početni zaslon"

Veće skladišne etikete za inventuru i police, umjesto malih SAP etiketa: fotografija proizvoda, veliki broj artikla, Code 128 barkod broja materijala, opis, a po želji i skladišno mjesto i stranica kataloga. Etikete se izrađuju kao PDF.

Postoje dva načina korištenja:

| | Web verzija | Windows program |
|---|---|---|
| Radi | u pregledniku, i na mobitelu | lokalno na računalu (Python) |
| Instalacija | nema, samo web prostor ili poveznica | jednom: Python i paketi |
| Fotografije | ugrađeno 3.501 fotografija iz kataloga, mogu se birati i vlastite | fotografije iz kataloga, vlastite, preuzimanje s lorencic.at |
| Prikladno za | brzo na mobitelu, mnogo kolega | velike serije (stotine etiketa), Excel popise |

## Sadržaj

- [Brzi početak (web verzija)](#brzi-početak-web-verzija)
- [Unos](#unos)
- [Padajući izbornici](#padajući-izbornici)
- [Fotografije](#fotografije)
- [Skladišno mjesto i stranica kataloga](#skladišno-mjesto-i-stranica-kataloga)
- [Zbirne etikete](#zbirne-etikete)
- [Ispis](#ispis)
- [Web verzija na vlastitom web prostoru (npr. WordPress)](#web-verzija-na-vlastitom-web-prostoru-npr-wordpress)
- [Ažuriranje podataka](#ažuriranje-podataka)
- [Automatska objava (GitHub Pages)](#automatska-objava-github-pages)
- [Windows program](#windows-program)
- [Rješavanje problema](#rješavanje-problema)
- [Tehničke napomene](#tehničke-napomene)
- [Struktura repozitorija](#struktura-repozitorija)

## Brzi početak (web verzija)

1. Otvorite stranicu.
2. U polje upišite brojeve artikala, jedan po retku, na primjer:
   ```
   Z100
   Z1425165*3
   ZM41014-RALH50
   ```
3. Odaberite format i dodirnite **Etiketten erstellen** (izradi etikete).
4. Dodirnite **PDF speichern** (spremi PDF) i ispišite.

Na dnu stranice piše koliko je artikala i fotografija učitano. Ako tamo nema broja, popis artikala nije učitan (vidi [Rješavanje problema](#rješavanje-problema)).

Sučelje je na njemačkom. U ovim uputama imena odgovaraju natpisima na tipkama.

## Unos

Unose odvojite novim retkom, razmakom ili zarezom. Velika i mala slova nisu bitna.

| Zapis | Značenje |
|---|---|
| `Z100` | jedna etiketa za Z100 |
| `Z100*3` | tri etikete za Z100 |
| `Z100@A-12-03` | Z100 sa skladišnim mjestom `A-12-03` unesenim ručno |
| `Z100@A-12-03*2` | dvije etikete s tim skladišnim mjestom |

Brojevi kojih nema na popisu artikala preskaču se i navode nakon izrade.

## Padajući izbornici

| Polje | Izbor |
|---|---|
| **Format** | 16,5 × 6,3 cm (standard) · stopper za policu 10 × 4 cm · Mini 5,6 × 2,5 cm · Avery Zweckform 3475 / 64 2280 (70 × 36 mm, 24 po arku) · Avery Zweckform 3481 / 42 0778 (70 × 41 mm, 21 po arku) · A4 položeno · A5 položeno · vlastita veličina (širina × visina u mm, od 20 do 400) |
| **Art** (vrsta) | pojedinačne etikete ili zbirna etiketa (vidi dolje) |
| **Seitenlayout** (raspored stranice) | više etiketa na A4 stranici s oznakama za rezanje, ili jedna etiketa po stranici |
| **Rahmen** (okvir) | okvir oko svake etikete, ili bez okvira |
| **Lagerplatz** (skladišno mjesto) | ispisati na etiketi, ili ne |
| **Katalogseite** (stranica kataloga) | ispisati na etiketi, ili ne |
| **Fotos** (fotografije) | ispisati sve artikle, ili samo artikle s fotografijom |
| **Druckerrand** (rub pisača) | prikazuje se samo kod Avery arka, vidi [Ispis](#ispis) |

Avery formati su gotovi izrezani arci s naljepnicama. Uvijek se ispisuju kao mreža na A4, bez oznaka za rezanje.

## Fotografije

Web verzija sadrži fotografije iz kataloga. Ako neka nedostaje, etiketa se ispisuje bez fotografije, a artikl se nakon toga pojavljuje pod **Ohne Foto gedruckt** (ispisano bez fotografije).

- **Dodati pojedinačno:** tamo dodirnite **Foto wählen** (odaberi fotografiju), iz galerije ili kamere, zatim **Mit den neuen Fotos neu erstellen** (ponovno izradi s novim fotografijama).
- **Više odjednom:** pod **Eigene Fotos und Lagerplätze** (vlastite fotografije i skladišna mjesta) učitajte fotografije. Naziv datoteke je broj artikla, na primjer `Z100.jpg`. Vlastite fotografije imaju prednost pred onima iz kataloga.
- **Ispisati samo s fotografijom:** u polju **Fotos** odaberite „Nur Artikel mit Foto drucken". Artikli bez fotografije se tada preskaču i navode.

Bijeli rubovi fotografije režu se automatski, a prozirna pozadina postaje bijela.

## Skladišno mjesto i stranica kataloga

- Stranica kataloga dolazi s popisa artikala (stupac `Katalogseite`).
- Skladišno mjesto unosite ručno (`Z100@A-12-03`) ili učitate popis: pod **Eigene Fotos und Lagerplätze** odaberite Excel ili CSV datoteku sa stupcima `Material` i `Lagerplatz` (po želji `Katalogseite`). Nazivi stupaca prepoznaju se bez obzira na velika i mala slova, vrijede i `Platz` i `LGPBE`.
- Ako na maloj etiketi nema mjesta, donji redak se izostavlja. Opis ima prednost.

## Zbirne etikete

Jedan A4 list uspravno po grupi artikala, na primjer sve veličine radnih hlača: gore fotografija, zajednički početak broja i zajednički opis, ispod toga po jedan redak za svaku veličinu s brojem artikla, veličinom i barkodom.

1. Pod **Art** odaberite „Sammeletikett".
2. **Svaki redak je jedan list**, svi brojevi u jednom retku pripadaju zajedno:
   ```
   ZM41014-RALH50 ZM41014-RALH52 ZM41014-RALH54
   ZM42014-RABH50 ZM42014-RABH52
   ```
3. Fotografija je s prvog artikla u retku koji je ima. Ako grupa ima više od 9 artikala, nastavlja se na sljedećim stranicama.

Tekst koji je isti za sve artikle sažet je gore, a u retku stoje samo razlike (na primjer `Gr. 50`). To najbolje radi kad su opisi strukturirani zarezima.

## Ispis

- Pri ispisu odaberite **100 % / „stvarna veličina"**, ne „prilagodi stranici". Inače dimenzije neće biti točne.
- Kod arka s naljepnicama (Avery) prvo ispišite **probnu stranicu na običnom papiru** i držite je uz arak prema svjetlu.
- **Rub pisača:** mnogi pisači ne ispisuju sve do lijevog i desnog ruba papira. Kod Avery formata stranica pomiče sadržaj vanjskih stupaca prema unutra kako ništa ne bi bilo odrezano. Zadano je 6 mm. Ako na vašem pisaču ništa nije odrezano, vrijednost možete smanjiti, a ako je i dalje nešto odrezano, povećati.
- **Čitači barkoda:** na vrlo malim etiketama (Mini 5,6 × 2,5 cm) crte su uske. Prije velike serije skenirajte probnu etiketu.

## Web verzija na vlastitom web prostoru (npr. WordPress)

Web verzija je običan HTML i ne treba poslužitelj s PHP-om ni bazu podataka.

1. Kopirajte ove datoteke u mapu `etiketten` na web prostoru (FTP ili upravitelj datoteka u hostingu): `index.html`, `manifest.json`, četiri ikone (`*.png`), `liste.json` i mapu `fotos/`. Ukupno oko 47 MB.
2. Mapa mora biti **pored** `wp-content`, ne u medijskoj biblioteci. WordPress tamo ne prihvaća ove vrste datoteka (`.json`, `.txt`).
3. Otvorite `https://vasa-domena.hr/etiketten/`.
4. Ako se treba prikazati unutar WordPress stranice, ugradite `/etiketten/` pomoću iframea.

Napomene:

- Stranica učitava dvije biblioteke s `cdnjs.cloudflare.com` (jsPDF za izradu PDF-a, SheetJS za čitanje Excela). Ako to blokira vatrozid, stavite obje datoteke na web prostor i dva retka `<script src=…>` u `index.html` usmjerite na njih.
- Logotip tvrtke u zaglavlju ugrađen je u `index.html` (Base64). Za zamjenu promijenite redak `<img class="logo" …>`.
- Bez zaštite stranicu može otvoriti svatko. Ako to nije željeno, u hostingu postavite zaštitu direktorija (lozinku) za `/etiketten/`.
- Sve se odvija u pregledniku. Uneseni brojevi i fotografije ne šalju se nikamo.
- Tko stranicu poslužuje preko GitHub Pages (vidi dolje), ne treba ništa od ovoga.

## Ažuriranje podataka

Repozitorij ima dva izvora:

| Izvor | Sadržaj |
|---|---|
| `data/preisliste_artikel.csv` | Popis artikala. Stupci `Material;Materiallangtext;WGR;LGR;BME;Katalogseite` (točka-zarez, UTF-8). Prazna stranica kataloga je `-`. |
| `data/bilder/` | Nove ili zamijenjene fotografije. Naziv datoteke = broj artikla, npr. `Z1234567.jpg` (JPG ili PNG). |

Osnovni skup fotografija iz kataloga već je spakiran u `fotos/`. Fotografije iz `data/bilder/` dodaju se povrh toga i imaju prednost.

**Dodavanje novog artikla**

1. Dodajte redak u `data/preisliste_artikel.csv`.
2. Po želji stavite fotografiju u `data/bilder/`.
3. Napravite commit i push. GitHub zatim ponovno izrađuje stranicu (vidi [Automatska objava](#automatska-objava-github-pages)).

**Ručna izrada** (za testiranje ili za vlastiti web prostor), u glavnoj mapi repozitorija:

```bash
python3 tools/build_web_data.py
```

Skripti treba samo Python 3, bez dodatnih paketa. Piše `liste.json` i dopunjuje `fotos/`. Postojeći paketi fotografija ostaju nepromijenjeni, nove fotografije idu u nove pakete. Opcija `--kompakt` ponovno piše sve pakete (uklanja zastarjele fotografije). Sve opcije: `python3 tools/build_web_data.py --help`.

## Automatska objava (GitHub Pages)

Stranica je na **https://beddy86.github.io/LorencicLable/**. Workflow `.github/workflows/veroeffentlichen.yml` ponovno je izrađuje pri svakom pushu na `main`: uzima `index.html` s ikonama, osnovni skup u `fotos/`, zatim `data/preisliste_artikel.csv` i `data/bilder/`, i objavljuje rezultat.

**Postavljanje jednom**

1. U repozitoriju otvorite **Settings → Pages** i pod **Source** odaberite „GitHub Actions".
2. Na kartici **Actions** jednom ručno pokrenite workflow **Seite veröffentlichen** (**Run workflow**) ili napravite bilo koji push.

**Od tada** je dovoljan push. Kartica **Actions** prikazuje napredak i moguće pogreške. Workflow se ne pokreće kad se mijenjaju samo README datoteke ili Windows program.

**Instalacija na mobitel:** otvorite stranicu u pregledniku i odaberite „Dodaj na početni zaslon". Tada se pokreće kao aplikacija s crvenom ikonom.

## Windows program

Za velike serije i Excel popise. Sve radi lokalno, prema van se ne otvara nijedan port (prozor sluša samo na `127.0.0.1`). Samo pretraga fotografija na lorencic.at ide na internet.

**Jednokratna instalacija**

1. Instalirajte Python 3 s python.org i označite „Add Python to PATH".
2. Kopirajte mapu `desktop/` na računalo, na primjer u `C:\Etiketten`. Program popis artikala pronalazi u mapi `data/` repozitorija. Ako je `desktop/` samostalno na računalu, stavite datoteku `preisliste_artikel.csv` pored nje.
3. Dvaput kliknite `Einmal_installieren.bat`. Instalira `openpyxl`, `reportlab` i `pillow` (vidi `requirements.txt`).

**Pokretanje**

Dvaput kliknite `Etiketten_starten.bat`. Otvara se crni prozor (ostavite ga otvorenim), a preglednik prikazuje isto sučelje kao web verzija. PDF-ovi se spremaju u mapu `ausgabe`.

Uz to:

- Fotografije koje nedostaju preuzimaju se s lorencic.at (opcija u sučelju) i pamte u `bilder/_web/`.
- Vlastite fotografije stavite u mapu `bilder/`, kao `Z100.jpg`. Imaju prednost.
- Duge serije prikazuju napredak.
- Pronađene fotografije program pamti u `bild_cache.json`. Ako fotografija više ne odgovara, obrišite tu datoteku.

**Naredbeni redak**

```bash
# pojedinačni artikli, više po A4 stranici
python3 desktop/etiketten.py --artikel Z100 Z5-1 Z170000 -o etikete.pdf --a4

# cijeli Excel popis (stupci Material, Materiallangtext, po želji Lagerplatz, Katalogseite)
python3 desktop/etiketten.py popis.xlsx -o etikete.pdf

# drugi format, samo s fotografijom
python3 desktop/etiketten.py --artikel-datei brojevi.txt --format avery3481 --nur-mit-foto -o avery.pdf

# vlastita veličina 90 x 45 mm
python3 desktop/etiketten.py --artikel Z100 --breite 90 --hoehe 45 -o vlastita.pdf

# zbirna etiketa, svaka --sammel grupa je jedan list
python3 desktop/etiketten.py --sammel ZM41014-RALH50 ZM41014-RALH52 --sammel ZM42014-RABH50 -o zbirna.pdf
```

Sve opcije: `python3 desktop/etiketten.py --help`. Formati: `165x63`, `a4`, `a5`, `stopper`, `mini`, `avery3475`, `avery3481`.

## Rješavanje problema

| Problem | Uzrok i rješenje |
|---|---|
| „Artikelliste konnte nicht geladen werden" | `liste.json` ili `fotos/` nedostaje na poslužitelju, ili hosting blokira `.json` / `.txt`. Provjerite strukturu mapa i otvorite datoteke izravno u pregledniku. |
| Prazna stranica, ništa ne reagira | Skripte s `cdnjs.cloudflare.com` su blokirane. Vidi napomenu o vatrozidu gore. |
| Nedostaje fotografija | Nema fotografije u katalogu. Odaberite vlastitu fotografiju ili stavite `Z….jpg` u `bilder/`. |
| Windows program: pogreška certifikata (SSL) | Mreža tvrtke s vlastitom provjerom certifikata. Program to zaobilazi samo za lorencic.at. Koristite najnoviji `etiketten.py`. |
| Etiketa bez fotografije iako je ima na internetu | Obrišite `bild_cache.json` i izradite ponovno. |
| `PDF speichern` ne radi ništa | Preglednik blokira preuzimanja. Dopustite skočni prozor i obavijest o preuzimanju u pregledniku. |
| Avery: fotografija lijevo ili barkod desno je odrezan | Povećajte rub pisača (zadano 6 mm). |
| Posebni znakovi postaju upitnik | Znakovi izvan standardnog skupa znakova (Windows-1252) ne mogu se prikazati u fontu. `²` i `³` ispisuju se kao `2` i `3`. |
| Barkod se ne skenira | Ispišite na 100 %, odaberite veći format, provjerite čita li čitač Code 128. |

## Tehničke napomene

- Barkod: Code 128, skup znakova B, kod duljih nizova brojki automatski prelazi na C.
- Web verzija: jedan `index.html`, PDF se izrađuje pomoću jsPDF-a u pregledniku, podaci kao `liste.json` i paketi fotografija (`fotos/pNNN.txt`, Base64, po oko 300 KB, uz `fotos/index.json`). Fotografije se učitavaju samo kad su potrebne.
- Windows program: Python s reportlab, Pillow i openpyxl, sučelje kao mali lokalni web poslužitelj.
- Raspored obje verzije je isti i prenesen je redak po redak. Ako mijenjate raspored, promijenite ga u obje (`desktop/etiketten.py` i `index.html`).

## Struktura repozitorija

```
index.html, manifest.json, *.png   stranica (s ikonama za mobitel)
liste.json, fotos/                 osnovni skup podataka, već spakiran
data/preisliste_artikel.csv        popis artikala (izvor)
data/bilder/                       nove i vlastite fotografije (izvor)
tools/build_web_data.py            izrađuje liste.json i fotos/
desktop/                           Windows program
.github/workflows/                 automatska objava
```

## Licenca

Još nije određena. Prije objave dodajte licencu (`LICENSE`).
