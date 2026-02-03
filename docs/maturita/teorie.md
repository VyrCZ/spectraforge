# Teoretická část

Tato kapitola shrnuje teoretická východiska nutná pro pochopení problematiky moderních světelných systémů, hardwarové architektury a softwarového inženýrství použitého v praktické části práce.

## 1. Moderní světelné systémy

### 1.1 Historie a vývoj LED technologie

Technologie LED (Light Emitting Diode) prošla od svého objevu v první polovině 20. století dramatickým vývojem. První prakticky využitelnou LED diodu emitující viditelné červené spektrum vyvinul v roce 1962 Nick Holonyak Jr. Po desetiletí byly diody omezeny pouze na červenou a později zelenou barvu s nízkou svítivostí, což je předurčovalo pouze pro indikační účely.

Zlom nastal v 90. letech 20. století, kdy **Shuji Nakamura, Isamu Akasaki a Hiroshi Amano** vynalezli vysoce účinnou modrou LED diodu na bázi nitridu gallitého (GaN). Tento objev, oceněný Nobelovou cenou za fyziku, umožnil vznik bílého světla (kombinací modrého světla a žlutého luminoforu) a plnobarevných RGB displejů a pásků. Dnešní moderní LED systémy se vyznačují vysokou účinností (lm/W), dlouhou životností a možností digitálního řízení.

### 1.2 LED mapping vs. projekce

V oblasti vizuálního umění a scénografie se často setkáváme se dvěma přístupy k osvětlování objektů:

* **Video mapping (Projekce):** Využívá výkonné projektory k promítání obrazu na 3D objekt. Výhodou je vysoké rozlišení a možnost měnit obsah bez zásahu do objektu. Nevýhodou je nutnost tmy (nízký kontrast za dne), stínění diváky a vysoká cena profesionálních projektorů.
* **LED mapping (Pixel mapping):** Spočívá v osazení samotného objektu světelnými zdroji (LED pásky, pixely). .
* **Výhody:** Vysoký jas a kontrast (viditelné i za denního světla), diváci nemohou vrhat stín do obrazu, možnost vytvářet 3D volumetrické efekty.
* **Nevýhody:** Nižší rozlišení (dané hustotou LED) a náročná instalace kabeláže. Tato práce se zaměřuje právě na tuto metodu.

---

## 2. Technologie adresovatelných LED

### 2.1 Princip fungování (čipy WS281x, SK6812)

Adresovatelné LED diody, často označované jako "NeoPixel" (obchodní název společnosti Adafruit), integrují v pouzdře velikosti 5050 (5x5 mm) nejen samotné čipy pro červenou, zelenou a modrou barvu, ale také **integrovaný obvod (IC)** pro řízení.

Nejrozšířenějším typem je řada **WS2812B** (a její klony jako SK6812). Každá dioda funguje jako posuvný registr. Data jsou posílána sériově do první diody, ta si "odkrojí" prvních 24 bitů (8 bitů pro každý kanál G, R, B) pro nastavení své barvy pomocí PWM (Pulse Width Modulation) a zbytek dat přeposílá tvarovaným výstupem do diody následující. To umožňuje řídit stovky diod pomocí jediného datového pinu mikrokontroléru.

### 2.2 Komunikační protokoly a časování

Komunikace s čipy WS281x je specifická tím, že nepoužívá hodinový signál (clock), jako je tomu u protokolů SPI nebo I2C. Jedná se o asynchronní sériový protokol, který je extrémně závislý na přesném časování.

Logická nula a jednička jsou kódovány délkou pulzu (NZR – Non-Return-to-Zero):

* **Logická 0:** Krátký pulz v logické 1 (cca ) následovaný delším úsekem v logické 0.
* **Logická 1:** Dlouhý pulz v logické 1 (cca ) následovaný kratším úsekem v logické 0.

Celková perioda jednoho bitu je přibližně , což odpovídá frekvenci datového toku . Jakákoliv odchylka v řádu stovek nanosekund může způsobit chybu v přenosu, což klade vysoké nároky na řídicí hardware.

### 2.3 Problematika napájení a distribuce signálu

Při návrhu LED instalací je nutné řešit dva fyzikální problémy:

1. **Úbytek napětí (Voltage Drop):** Vedení na flexibilních PCB páscích má nezanedbatelný odpor. Dle Ohmova zákona 

 dochází při průchodu proudu k poklesu napětí. Pokud napětí na konci pásku klesne pod cca 3.5V, modrá složka LED přestane svítit a barvy se zkreslí do červena. Řešením je paralelní injektáž napájení (power injection) každých několik metrů.
2. **Logické úrovně:** Čipy WS2812 obvykle vyžadují logickou úroveň datového signálu minimálně  (tedy cca 3.5V při 5V napájení). Raspberry Pi však pracuje s logikou 3.3V. Přímé připojení může fungovat nestabilně, proto je nutné použít převodník logických úrovní (Level Shifter), např. 74AHCT125.

---

## 3. Hardwarová platforma

### 3.1 Architektura Raspberry Pi (proč jsem si ho vybral)

Pro řízení systému byl zvolen jednodeskový počítač **Raspberry Pi** (model 4/5). Na rozdíl od mikrokontrolérů (Arduino, ESP32), které spouští kód přímo na "železe" (bare metal), běží na Raspberry Pi plnohodnotný operační systém Linux (Debian/Raspberry Pi OS).

**Důvody volby pro tuto práci:**

* **Výkon:** Čtyřjádrový procesor ARM Cortex-A72 umožňuje provádět náročné výpočty (např. FFT analýzu zvuku) v reálném čase, což by u slabších mikrokontrolérů bylo problematické.
* **Konektivita:** Integrované Wi-Fi a Ethernet pro provoz webového serveru.
* **Python ekosystém:** Dostupnost knihoven pro zpracování multimédií a vědecké výpočty.

### 3.2 Způsoby nasazení softwaru

Moderní vývoj embedded aplikací se posouvá od manuální instalace k automatizaci.

* **Virtual Environments (venv):** Izolace závislostí Pythonu, aby nedocházelo ke konfliktům se systémovými balíčky.
* **Systemd služby:** Pro zajištění automatického spuštění aplikace po startu systému a jejího restartování v případě pádu.
* **Docker (volitelně):** Kontejnerizace celé aplikace, což zajišťuje konzistenci prostředí bez ohledu na verzi OS.

### 3.3 Konfigurace bezhlavého (headless) systému a AP

Systém je navržen jako "headless", tedy bez připojeného monitoru, klávesnice a myši. Správa probíhá vzdáleně přes protokol SSH.

Pro zajištění funkčnosti i v místech bez existující infrastruktury (např. venkovní instalace) je Raspberry Pi konfigurováno jako **Wi-Fi Access Point (AP)** pomocí nástroje `hostapd` a `dnsmasq`. Počítač vytvoří vlastní síť, ke které se uživatel připojí telefonem či notebookem a ovládá světla přes prohlížeč.

---

## 4. Softwarové řešení (Backend)

### 4.1 Jazyk Python v embedded systémech

Python je interpretovaný jazyk na vysoké úrovni. Jeho hlavní výhodou je čitelnost kódu a rychlost vývoje. V kontextu embedded systémů je často kritizován za nižší rychlost a přítomnost GIL (Global Interpreter Lock), který omezuje využití více vláken.

Pro tuto práci je však Python ideální volbou pro rychlý vývoj, obsáhlý ekosystém a JIT architektuře pro načítání efektů za běhu (runtime). Výkonově kritické části (komunikace s hardwarem, matematické operace) jsou napsány v jazyce C a Python je volá jako optimalizované knihovny (NumPy, rpi_ws281x).

### 4.2 Knihovna NeoPixel a přímý přístup k DMA

Jak bylo zmíněno v kapitole 2.2, časování WS2812 vyžaduje přesnost na stovky nanosekund. Operační systém Linux (který není v základu Real-Time OS) nemůže zaručit, že procesor nebude přerušen jinou úlohou právě v okamžiku odesílání dat, což by způsobilo blikání LED.

Tento problém řeší knihovna `rpi_ws281x` využitím **DMA (Direct Memory Access)**. DMA řadič umožňuje přenášet data z paměti RAM přímo na periferie (PWM modul nebo PCM) bez účasti procesoru (CPU).

* Signál je generován pomocí PWM (Pulse Width Modulation) modulu Raspberry Pi.
* Tímto způsobem získáme stabilní signál nezávislý na zátěži operačního systému.

### 4.3 Zpracování multimédií (FFmpeg, PyDub)

Pro vizualizaci hudby a videa je nutné dekódovat vstupní soubory.

* **FFmpeg:** Robustní framework pro práci s multimédii. V práci je využit pro extrakci audio stopy z video souborů nebo konverzi formátů.
* **PyDub / NumPy:** Slouží k načtení audio dat do paměti a jejich matematické analýze. Pro vizualizaci frekvenčního spektra se využívá **Rychlá Fourierova transformace (FFT)**, která převede signál z časové domény 

.

### 4.4 3D vizualizace dat pomocí PyVista

Při složitějším mappingu (např. LED pásek omotaný kolem sochy) 2D matice pixelů neodpovídá realitě.
Knihovna **PyVista** (wrapper nad VTK) umožňuje vytvořit virtuální 3D model instalace. Každému bodu v 3D prostoru (x, y, z) je přiřazen index LED diody. To umožňuje generovat efekty, které jsou prostorově koherentní (např. rovina světla procházející objektem), bez ohledu na to, jak je pásek fyzicky zapojen.

---

## 5. Řídicí rozhraní (Frontend)

### 5.1 Architektura klient-server (Flask)

Backend aplikace běží na frameworku **Flask**. Ten poskytuje webový server, který obsluhuje HTTP požadavky. Slouží primárně k:

1. Servírování statických souborů (HTML, CSS, JS) klientovi.
2. Poskytování REST API pro nastavení konfigurace, která nevyžaduje okamžitou odezvu (např. nahrávání souborů, změna počtu LED).

### 5.2 Real-time komunikace pomocí WebSockets (Socket.IO)

Pro ovládání efektů (změna barvy, jasu, přepínání módů) je standardní HTTP protokol nevhodný kvůli vysoké latenci (nutnost navázat spojení pro každý požadavek - 3-way handshake).

Proto je využita technologie **WebSockets** prostřednictvím knihovny **Socket.IO**.

* WebSockets udržují trvalé, obousměrné spojení (full-duplex) mezi klientem (prohlížečem) a serverem (RPi).
* To umožňuje odesílat příkazy s minimálním zpožděním (v řádu milisekund), což je klíčové pro pocit plynulého ovládání.

### 5.3 Uživatelské rozhraní (HTML/CSS/JS)

Frontend je navržen jako *Single Page Application* (SPA).

* **HTML5:** Definuje strukturu (tlačítka, posuvníky, color pickery).
* **CSS3 (Flexbox/Grid):** Zajišťuje responzivitu, aby bylo rozhraní použitelné jak na mobilním telefonu, tak na desktopu.
* **JavaScript:** Zpracovává vstupy uživatele a odesílá data přes Socket.IO na backend, aniž by se musela znovu načítat celá stránka.
