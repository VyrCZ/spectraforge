Zde je návrh teoretické části. Text je psán odborným, akademickým stylem, který odpovídá úrovni maturitní práce, a plynule navazuje na praktickou část.

---

# Teoretická část

## 1. Moderní světelné systémy

Osvětlovací technika prošla v posledních dekádách revoluční proměnou, která posunula vnímání světla z pouhého funkčního prvku na klíčový nástroj uměleckého vyjádření a designu. Moderní systémy již nejsou omezeny na statické svícení, ale stávají se dynamickými instalacemi schopnými reagovat na okolní podněty, hudbu či interakci s uživatelem.

### 1.1 Historie a vývoj LED technologie

Zkratka LED označuje diodu emitující světlo (Light Emitting Diode). Princip elektroluminiscence, na kterém tyto polovodičové součástky fungují, byl objeven již na počátku 20. století, avšak první prakticky využitelnou červenou LED diodu vyvinul až v roce 1962 Nick Holonyak. Zásadním zlomem byl vynález modré LED diody v 90. letech, za který získal Shuji Nakamura Nobelovu cenu. Tato inovace umožnila kombinací s luminoforem vznik bílého světla a otevřela cestu k plnobarevnému RGB míchání. Zatímco původní diody sloužily pouze jako indikační prvky, dnešní technologie umožňuje miniaturizaci a integraci řídicích čipů přímo do pouzdra diody, což vedlo ke vzniku tzv. digitálních či adresovatelných LED pásků.

### 1.2 LED mapping vs. projekce

V oblasti vizuálního umění se často setkáváme se dvěma přístupy: video mappingem a LED mappingem. Video mapping využívá projektory k promítání obrazu na existující povrchy. Tato metoda je závislá na vnějších světelných podmínkách (vyžaduje tmu) a přímé viditelnosti mezi projektorem a objektem. Naproti tomu LED mapping, neboli volumetrické zobrazování, vytváří obraz přímo na povrchu objektu nebo v jeho objemu pomocí sítě světelných bodů. Výhodou tohoto přístupu je extrémní jas, nezávislost na okolním osvětlení a možnost vytvářet 3D struktury, které lze pozorovat ze všech úhlů bez rizika stínění obrazu divákem.

## 2. Technologie adresovatelných LED

Adresovatelné LED diody představují specifickou kategorii osvětlení, kde každý světelný bod (pixel) může být ovládán nezávisle na ostatních, ačkoliv jsou všechny zapojeny na společném datovém vodiči.

### 2.1 Princip fungování (čipy WS281x, SK6812)

Nejrozšířenějším standardem v oblasti hobby i poloprofesionálních instalací jsou čipy rodiny WS2812B (často označované jako NeoPixel) nebo jejich klony SK6812. Každá taková LED dioda obsahuje uvnitř svého pouzdra nejen samotné čipy pro červenou, zelenou a modrou barvu, ale také miniaturní integrovaný obvod. Tento řadič přijímá data ze vstupního pinu, odebere prvních 24 bitů (8 bitů pro každou barvu) pro vlastní nastavení, a zbytek dat zesílí a pošle na výstupní pin k další diodě v řetězci. Díky tomu je možné ovládat stovky až tisíce diod pomocí jediného datového pinu mikrokontroléru.

### 2.2 Komunikační protokoly a časování

Komunikace s těmito čipy probíhá pomocí asynchronního sériového protokolu typu NRZ (Non-Return-to-Zero). Protokol je velmi citlivý na časování, protože nepoužívá hodinový signál (clock). Logická nula a logická jednička jsou definovány délkou trvání pulzu v rámci pevně daného časového okna, obvykle v řádech stovek nanosekund. [🎨 obrázek časového diagramu protokolu WS2812, ukazující rozdíl v délce pulzu pro 0 a 1] Například u čipu WS2812B trvá přenos jednoho bitu 1,25 µs. Pokud řídicí systém nedokáže dodržet toto striktní časování, dochází k chybám v zobrazení nebo k blikání celé instalace. Signál "Reset", který odděluje jednotlivé snímky, je definován jako stav nízké úrovně napětí po dobu delší než 50 µs.

### 2.3 Problematika napájení a distribuce signálu

Při návrhu rozsáhlejších instalací je kritickým faktorem napájení. Každý pixel při plném jasu (bílá barva) odebírá přibližně 60 mA. Pro řetězec 200 LED diod to znamená odběr až 12 A, což běžné vodiče na LED páscích nedokážou přenést bez výrazného úbytku napětí. Tento úbytek se projevuje postupným červenáním a slábnutím jasu směrem ke konci pásku (modrá LED potřebuje nejvyšší napětí, proto zhasíná první). Řešením je injektáž napájení (power injection) na více místech instalace paralelním vedením. Dále je nutné řešit filtraci napěťových špiček pomocí kondenzátorů a přizpůsobení logických úrovní, jelikož LED pásky obvykle pracují s 5V logikou, zatímco moderní mikrokontroléry a Raspberry Pi využívají 3,3V.

### 2.4 Teorie barev v digitálním světě

Pro reprezentaci barev v počítačové grafice a LED technice se využívají různé barevné modely. Hardware LED diod pracuje s aditivním mícháním barev v modelu **RGB** (Red, Green, Blue). Smícháním těchto tří primárních barev v plné intenzitě vzniká bílé světlo, jejich absencí černá (tma).

Pro programování efektů je však model RGB často nevhodný, protože je pro člověka neintuitivní definovat barvu poměrem tří složek. Proto se využívá model **HSV** (Hue, Saturation, Value), který definuje barvu pomocí odstínu (úhel na barevném kruhu), sytosti a jasu. Tento model umožňuje snadnou implementaci efektů, jako je "duha", pouhou iterací hodnoty Hue, což by v RGB vyžadovalo složité přepočty.

### 2.5 Lidské vnímání jasu a barev

Lidské oko nevnímá intenzitu světla lineárně, ale logaritmicky (podle Weber-Fechnerova zákona). To znamená, že LED dioda nastavená na 50 % výkonu (hodnota 128 z 255) se lidskému oku jeví mnohem jasnější, spíše jako 80 % maximálního jasu. [🎨 graf porovnání lineární křivky a křivky s gamma korekcí] Aby byly přechody jasu plynulé a barvy věrné, je nutné aplikovat tzv. **gamma korekci**. Tento proces transformuje lineární vstupní hodnoty pomocí mocninné funkce (obvykle s exponentem gamma 2.2 až 2.8), čímž kompenzuje nelinearitu lidského zraku a zajišťuje přirozenější vizuální vjem.

## 3. Hardwarová platforma

Srdcem celého systému Spectraforge je jednodeskový počítač, který musí zvládat nejen komunikaci s LED diodami, ale také běh webového serveru a výpočty v reálném čase.

### 3.1 Architektura Raspberry Pi

Pro tento projekt bylo zvoleno Raspberry Pi (konkrétně model Zero 2 W nebo 3/4) namísto běžných mikrokontrolérů jako Arduino nebo ESP32. Hlavním důvodem je potřeba operačního systému Linux, který umožňuje běh pokročilých aplikací v jazyce Python, multitasking a snadnou správu souborů. Raspberry Pi disponuje dostatečným výpočetním výkonem (čtyřjádrový procesor) pro provádění Fast Fourierovy Transformace (FFT) pro audio analýzu v reálném čase, což by bylo na menších mikrokontrolérech obtížně realizovatelné souběžně s obsluhou sítě a webového rozhraní.

### 3.2 Způsoby nasazení softwaru

Software na platformě Linux je obvykle spravován jako služba (daemon). Využití init systému `systemd` zajišťuje, že aplikace se automaticky spustí po startu systému a v případě pádu je restartována. Pro izolaci závislostí a knihoven jazyka Python je využíváno virtuální prostředí (`venv`), které zabraňuje konfliktům mezi systémovými balíčky a balíčky vyžadovanými aplikací.

### 3.3 Konfigurace bezhlavého (headless) systému a AP

Většina instalací světelné techniky neumožňuje připojení monitoru, klávesnice a myši. Systém je proto konfigurován jako tzv. bezhlavý (headless), ovládaný vzdáleně pomocí protokolu SSH. Pro zajištění použitelnosti v terénu, kde nemusí být dostupná Wi-Fi síť, je Raspberry Pi nakonfigurováno tak, aby vytvářelo vlastní přístupový bod (Access Point). Uživatel se tak může připojit přímo k zařízení pomocí telefonu či notebooku a ovládat instalaci nezávisle na externí infrastruktuře.

## 4. Softwarové řešení (Backend)

Backendová část aplikace zajišťuje logiku řízení, zpracování dat a komunikaci s hardwarem.

### 4.1 Jazyk Python v embedded systémech

Python byl zvolen pro svou čitelnost, rozsáhlou ekosystém knihoven a rychlost vývoje. V kontextu embedded systémů je však nutné brát v úvahu jeho limity, zejména co se týče výkonu interpretovaného kódu a správy paměti (Garbage Collection), která může způsobovat nepravidelné zpoždění (jitter). Pro časově kritické operace je proto nutné využívat optimalizované knihovny napsané v jazyce C, které jsou z Pythonu pouze volány.

### 4.2 Knihovna NeoPixel a přímý přístup k DMA

Protože operační systém Linux není systémem reálného času (RTOS) a může kdykoliv přerušit běh procesu kvůli jiným úlohám, není možné generovat signál pro WS2812B přímo "bit-bangingem" na procesoru. Knihovna `rpi_ws281x` tento problém obchází využitím DMA (Direct Memory Access). DMA řadič umožňuje přenášet data z paměti RAM přímo na GPIO piny pomocí PWM (Pulse Width Modulation) nebo PCM periférie bez intervence procesoru. Tím je zajištěno stabilní časování signálu nezávisle na zátěži CPU.

### 4.3 Zpracování multimédií (FFmpeg, PyDub)

Pro práci s audio a video soubory systém využívá nástroj FFmpeg, který slouží jako univerzální dekodér. Knihovny jako PyDub nebo ImageIO interně volají FFmpeg pro převod různých formátů (MP3, MP4, WAV) do surových dat (PCM pro audio, RGB matice pro video), se kterými může aplikace dále pracovat. Tento přístup zajišťuje širokou kompatibilitu s formáty souborů dodaných uživatelem.

### 4.4 3D vizualizace dat pomocí PyVista

Pro simulaci LED instalace na obrazovce je využívána knihovna PyVista, která poskytuje vysokoúrovňové rozhraní pro vizualizační toolkit VTK. Umožňuje efektivní vykreslování mračna bodů (point cloud) ve 3D prostoru, kde každý bod reprezentuje jednu LED diodu. To je klíčové pro vývoj a ladění 3D efektů bez nutnosti fyzického přístupu k hardwaru.

### 4.5 Dynamické načítání modulů a bezpečnostní rizika

Architektura aplikace využívá dynamické načítání modulů pomocí knihovny `importlib`, což umožňuje přidávat nové efekty za běhu. Tento flexibilní přístup však přináší bezpečnostní rizika. Spuštění kódu třetí strany (například efektu staženého z internetu) uvnitř aplikace dává tomuto kódu plná oprávnění uživatele, pod kterým server běží. V teoretické rovině by bezpečný systém měl využívat tzv. sandboxing, tedy izolaci spouštěného kódu v odděleném procesu s omezenými právy, aby se zabránilo přístupu k citlivým částem systému.

## 5. Řídicí rozhraní (Frontend)

Frontend představuje vrstvu, se kterou interaguje koncový uživatel. Musí být responzivní a poskytovat okamžitou zpětnou vazbu.

### 5.1 Architektura klient-server (Flask)

Jako webový server slouží framework Flask. Ten funguje na principu zpracování HTTP požadavků, kdy klient (prohlížeč) požádá o stránku nebo data a server odpoví. Tento model Request-Response je vhodný pro načítání statického obsahu a konfiguraci, ale je nedostatečný pro řízení v reálném čase kvůli vysoké režii a latenci každého spojení.

### 5.2 Real-time komunikace pomocí WebSockets (Socket.IO)

Pro okamžitou reakci světel na akce uživatele (např. spuštění hudby, změna jasu) je využit protokol WebSocket. Na rozdíl od HTTP vytváří WebSocket trvalé, obousměrné spojení mezi serverem a prohlížečem. Knihovna Socket.IO nad tímto protokolem staví abstrakci založenou na událostech (events). Díky tomu může server poslat zprávu klientovi ("přehrávání začalo") nebo klient serveru ("nastav barvu na červenou") s minimálním zpožděním v řádu milisekund. [🎨 diagram porovnání komunikace HTTP vs WebSocket]

### 5.3 Uživatelské rozhraní (HTML/CSS/JS)

Rozhraní je navrženo pomocí standardních webových technologií HTML5, CSS3 a čistého JavaScriptu (Vanilla JS). Vzhledem k povaze projektu není nutné využívat komplexní frontendové frameworky jako React nebo Vue. Důraz je kladen na responzivitu, aby bylo ovládání pohodlné jak na desktopu, tak na mobilních zařízeních, která se často používají pro ovládání instalací v terénu.

### 5.4 Formáty pro výměnu dat (JSON)

Pro strukturovanou výměnu dat mezi Python backendem a JavaScript frontendem se používá formát JSON (JavaScript Object Notation). Je to textový formát nezávislý na jazyce, který je snadno čitelný pro lidi i stroje. V projektu Spectraforge se do JSONu serializují konfigurace efektů, definice světelných show i seznamy souborů.