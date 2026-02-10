# Praktická část
## 0. Úvod
Spectraforge je software pro řízení adresovatelných LED diod v reálném čase, navržený pro běh na platformě Raspberry Pi. Umožňuje jednoduché vytváření a přidávání světelných efektů a animací, obsahuje sadu dalších způsobů, jak interagovat s LED světly, například pomocí zvukových vstupů nebo předem nahraných světelných show, všechno ovladatelné přes webové rozhraní. Světla se dají umístit na 3D povrch, jako třeba stromek, nebo na 2D, například zeď. Tento software je určen pro umělce, vývojáře a nadšence do světelné techniky, kteří chtějí jednoduše vytvářet a spravovat světelné instalace. Software taky obsahuje nástroj pro simulaci LED diod na obrazovce, což usnadňuje vývoj a testování efektů bez nutnosti fyzického hardwaru.

//  obrázek stromku

## 1. Návod k použití
Tato sekce poskytuje krok za krokem návod k instalaci, základnímu nastavení, používání a vývoj efektů v softwaru Spectraforge.

### 1.1. Instalace a spuštění
Pro chod tohoto programu je potřeba mít nainstalovaný Python. Vývoj proběhl na verzi 3.10, byl ale testován i na verzi 3.13 a měl by fungovat i na nejnovější verzi (3.15 k datu psaní této práce). Do složky extrahujte obsah repozitáře, vytvořte si virtuální prostředí (doporučeno) a nainstalujte vyžadované moduly ze souboru `requirements.txt`. Po spuštění hlavního souboru `server.py` se spustí webový server, který je dostupný na adrese zařízení na portu 5000 (viditelná v konzoli po spuštění). Pro simulaci LED diod na obrazovce zároveň spusťte `led_simulator.py`. Pro nasazení do prostředí s hardwarem na Raspberry Pi je ještě potřeba nainstalovat knihovny pro NeoPixel (`pip3 install rpi_ws281x adafruit-circuitpython-neopixel`) pro komunikaci s LED diodami. Aplikace automaticky detekuje, zda běží na Raspberry Pi a podle toho použije správnou vrstvu pro komunikaci s LED diodami. Doporučené je také nastavit automatické spuštění aplikace po startu systému pomocí systemd služby, jak je popsáno v kapitole 3.2 teoretické části. ⚠️⚠️

### 1.2. Prvotní nastavení
Po prvním spuštění se načtou všechny efekty a první se začne přehrávat, bude však vypadat špatně. Je potřeba totiž nejdříve zkalibrovat pozice LED diod. 2D rozložení lze kalibrovat přímo v uživatelském rozhraní v sekci "Rozložení". Klikněte na tlačítko "Nové rozložení", zadejte název a počet LED diod. ⚠️⚠️ [Doplnit kompletnější instrukce k 2D kalibraci] ⚠️⚠️ [Doplnění 3D kalibrace]

### 1.3. Základní ovládání
Po úspěšném nastavení rozložení LED diod se můžete vrátit na hlavní stránku. Na ní můžete upravovat parametry aktuálního efektu, jako je rychlost, barva nebo intenzita, pokud je to daným efektem podporováno. Stisknutím na název efektu nebo na tlačítko "Efekty" v navigačním menu se dostanete na stránku s výběrem efektů. Zde můžete procházet dostupné efekty, seřazené dle vhodnosti pro dané rozložení (2D/3D). Kliknutím na efekt si jej zvolíte jako aktuální. Nové efekty lze přidávat v sekci "Nahrát", kde můžete kliknutím procházet soubory na vašem zařízení a nahrát je na server. Podporovány jsou python skripty jako efekty, audio soubory pro vizualizér, obrázkové a video soubory pro zobrazení na LED diodách a json soubory pro předem nahrané světelné show. Všechny tyto funkce jsou dostupné v načínacím menu.

### 1.4. Vývoj vlastních efektů
Pro vývoj vlastních efektů je potřeba mít základní znalosti jazyka Python. Efekty jsou implementovány jako samostatné moduly, které dědí z třídy `LightEffect`. Pro vytvoření nového efektu stačí vytvořit nový python soubor ve složce `effects` a implementovat následující:
Třída musí mít konstruktor, který přijímá dva parametry - renderer a coords, a musí zavolat konstruktor nadtřídy, ve kterém předá renderer, coords, název efektu pro zobrazení v aplikaci a typ efektu (Pouze 2D/3D, lépe vypadající jako 2D/3D nebo univerzální). Dále musí obsahovat metodu `update()`, která je volána v cyklu a kde se definuje chování efektu. Barvy jednotlivých LED diod (častěji nazývané pixely) jsou dostupné pomocí indexu objektu `self.renderer`, a jijich následné zobrazení je potřeba odeslat zavoláním `self.renderer.show()`. Pozice LED diod v prostoru jsou dostupné v seznamu `self.coords`, ve formátu seznamu XYZ souřadnic (pro 2D režim je Z vždy 0 pro jednoduchou kompatibilitu s 3D efekty)

#### 1.4.1. Parametry
Pokud chcete přidat parametry, které lze měnit z aplikace, použijte metodu `add_parameter()`, která vrací objekt parametru, ze kterého můžete získat aktuální hodnotu pomocí metody `get()`. Hodnoty parametrů jsou perzistentní a jejich hodnoty se ukládají do souboru s nastavením. Při jejich inicializaci musíte zadat název, typ parametru (číselný posuvník, výběr barvy, přepínač ano/ne, tlačítko) a výchozí hodnotu. Posuvník taky vyžaduje hodnoty min, max a step typu float (nebo int) a tlačítka mohou obsahovat argument onClick typu funkce, která se zavolá při kliknutí na tlačítko, nebo případně argumenty onDown a onUp pro funkce, které se zavolí samostatně při stisknutí a uvolnění tlačítka.

#### 1.4.2. Vývojové nástroje a omezení
Pro vývoj efektů je doporučeno používat režim pískoviště (sandbox mode), který se nachází v navigačním menu. Tento režim umožňuje automatické načtení změn při uložení souboru efektu bez nutnosti restartovat server (hot-reloading). Pro tento režim je třeba efekt přesunout do složky `sandbox`.
Je nutno podotknout několik následujících omezení a okolností pro správný vývoj efektů.

Funkce efektu `update()` je volána tak často, jak to dovolí výkon zařízení namísto pevné snímkovací frekvence (FPS). I když je omezení frekvence a zavedení "časovače" standartním postupem, většina efektů benefituje z maximální plynulosti a chod efektů by měl namísto používat svůj parametr rychlosti pro škálování rychlosti efektu.

Osy jsou definovány jako X - šířka, Y - výška, Z - hloubka. I když je obvyklejší používat osu Z pro výšku, v tomto systému je výška vždy osa Y, kvůli kompatibilitě 2D a 3D režimu.

Efekty mohou blokovat svůj chod (pomocí funkcí, jako je `time.sleep()`) bez problémů, protože efekt je spuštěn v samostatném vlákně. Náročné výpočty by však měly být optimalizovány, protože mohou způsobit snížení snímkovací frekvence a horší plynulost chodu celé aplikace.

Hodnoty souřadnic v `self.coords` nejsou normovány a mohou být v libovolném rozsahu a měřítku, včetně záporných hodnot. Pro výpočty vzdáleností a rychlostí je doporučeno používat relativní hodnoty (poměry) namísto absolutních hodnot.

#### 1.4.3. Příklad efektu
Níže je uveden příklad jednoduchého efektu "duha", používající schéma HSV pro plynulé přechody barev přes spektrum, s parametrem pro nastavení rychlosti a směru.
```python
class Rainbow(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Rainbow", EffectType.UNIVERSAL)
        # inicializace parametrů
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 1, min=1, max=20, step=0.1)
        self.reverse = self.add_parameter("Reverse", ParamType.CHECKBOX, False)
        self.current_y = 0 # hodnota sledující aktuální posun

    def update(self):
        self.current_y += (-1 if self.reverse.get() else 1) * self.speed.get() / 10 # aktualizace posunu, ovlivněno rychlostí a směrem
        if self.current_y > self.height:
            self.current_y = 0
        for i in range(len(self.renderer.leds)):
            # výpočet barvy na základě pozice a aktuálního posunu
            normalized_rgb = list(colorsys.hsv_to_rgb(mu.normalize(mu.wrap(self.coords[i][1] - self.current_y, 0, self.height), 0, self.height), 1, 1))
            # nastavení barvy LED diody
            self.renderer.leds[i] = tuple([int(channel * 255) for channel in normalized_rgb])
        self.renderer.show()
```

## 2. Zjistění led pozic v prostoru
Většina efektů a funkcionalit v této aplikaci závisí na znalosti pozic LED diod v prostoru. Tyto pozice jsou využívány pro výpočty vzdáleností, směrů a dalších prostorových vlastností, které umožňují vytvářet efekty reagující na 3D uspořádání světelné instalace, proto je jejich přesné zjištění kritické pro správné fungování aplikace. 2D rozložení lze kalibrovat pouze s použitím telefonu. Tento proces vyžaduje kameru, která vytváří fotografie každé samostatné rozsvícené LED diody v instalaci pomocí modulu `CalibrationEngine`. Před tím, než začneme fotit se však musíme ujistit, že je v prostoru dostatečná tma pro kontrast a že je kamera pevně zafixovaná kolmo k povrchu. Po pořízení obrázků je program projde a pokusí se detekovat pozici pomocí nejjasnějšího bodu na obrázku. Tento problém se dá řešit i jinými způsoby, například detekcí specifické barvy nebo detekcí kruhů pomocí Houghovy transformace. Pro tento projekt však byla zvolena detekce nejjasnějšího bodu kvůli její jednoduchosti i přes občasné nepřesnosti. Z tohoto důvodu jsou určené pozice v aplikaci prezentovány uživateli pro kontrolu a případnou manuální úpravu. Po kontrole a případných úpravách jsou pozice uloženy do souboru pro pozdější použití v aplikaci. [🎨🎨 Obrázek kalibrace] 

Získání pozic v 3D instalaci je komplikovanější, princip je ovšem stejný. Je potřeba pořídit fotografie ze aspoň dvou různých úhlů, ideálně kolmých na sebe. V tomto programu vyžaduji fotografie všech čtyř stran (přední, zadní, levá, pravá) pro lepší přesnost. Z důvodu nespolehlivosti automatické detekce není možné použít tento režim přímo v aplikaci [⚠️⚠️ doplnit instrukce pro 3D kalibraci]

## 3. Zobrazování barev na LED diodách
Funkcionalita pro zobrazování barev na LED diodách je oddělena do samostatné vrstvy `LEDRenderer`, která jako jediná komunikuje přímo s hardwarem. Tento přístup umožňuje snadný post-processing (filtry) jednom místě, či v budoucnu i podpora jiných LED architektur bez nutnosti měnit zbytek kódu. Třída `LEDRenderer` je instancována v hlavním souboru `server.py` a předávána do jednotlivých  modulů. Je to lehký wrapper (obal) nad voláním knihovny neopixel, který se snaží poskytnout stejný syntax jako přímé volání knihovny. Implementuje metody __getitem__ a __setitem__ pro přímé indexování objektu rendereru jako samotný seznam pixelů a funkce jako fill a clear pro často používané operace. Pro odeslání dat na LED diody je potřeba zavolat metodu `show()`, která přepíše aktuální barvy na LED diodách, protože činnost odesílání je výkonově náročná a často měníme více pixelů najednou, proto by automatické odesílání po každé změně pixelu bylo nežádoucí. Modul také obsahuje zkušební verzi třídy `DummyRenderer` používaná při validaci jednotlivých efektů (více v kapitole [⚠️⚠️ doplnit odkaz na kapitolu o vývoji efektů]), která obsahuje stejné funkce, ale neprovádí žádné operace s hardwarem.

### 3.1 Simulace LED diod na obrazovce
Pro usnadnění vývoje a testování efektů bez nutnosti fyzického hardwaru je součástí aplikace i simulátor LED diod na obrazovce. Tento simulátor zobrazuje LED diody jako barevné body na černém pozadí, jejichž pozice odpovídají kalibrovaným souřadnicím. Simulátor je implementován v souboru `led_simulator.py`, který po detekci operačního systému Windows automaticky spustí server, na který se připojí client `led_simulator.py` po spuštění a automaticky začne odesílat data barev. Tato implementace umožňuje nezávisle ukončovat simulátor a server, což je užitečné při vývoji.

[🎨🎨 Obrázek simulátoru]

#### 3.1.1. `DebugDraw`
Většina efektů využívá matematické vzorce a výpočty, které mohou být složité na pochopení a ladění. Pro usnadnění tohoto procesu je součástí simulátoru i nástroj `DebugDraw`, který umožňuje kreslit základní geometrické tvary (body, čáry, kruhy) přímo na simulátor. Funkce se používá pomocí volání `renderer.debug_draw.point / line / circle`, které vyžadují souřadnice jednoho či dvou bodů v typu tuple, barvu v RGB formátu a volitelně parametr, který určuje, zda se má čára zůstat vykreslená i po dalším volání `show()` (persistent).

### 3.2. Post-processing a filtry
Post-processing, neboli praktika úprav obrazu po jeho vygenerování, je velmi důležitá část vykreslovacího cyklu. Umožňuje aplikovat různé efekty a úpravy na výsledný obraz před jeho odesláním na LED diody, což může výrazně zlepšit vizuální kvalitu či přidá dodatečnou kontrolu nad výsledným výstupem. V této aplikaci implementuji filtry pro ovládání jasu, který vynásobí všechny kanály všech barev aktuálně nastaveným procentem jasu. Další je posun všech barev na spektru o zadanou vzdálenost (hue shift), který není běžný, ani praktický, ale poskytuje další způsob přispůsobení a osvěžení efektů, které mají pevně dané barvy. [⚠️⚠️ případně odstranit hue shift sekci] Poslední, ale nejdůležitější je gamma korekce, která upravuje jasnost středních tónů pro kompenzaci nelineárního vnímání jasu lidským okem. Tato korekce je kritická pro dosažení sytějších a příjemnějších barev. [⚠️⚠️ doplnit teorii do teoretické části] [🎨🎨 Obrázek srovnání s a bez gamma korekce, do teoretické části]

## 4. Modulární struktura (`Engine`)
Pro jednoduchou rozšiřitelnost, organizaci kódu a zajištění, že pouze jeden modul je aktivní a může ovládat LED diody, je celá funkcionalita rozdělena do modulů, které jsou spravovány třídou `EngineManager`. Každý modul dědí z třídy `BaseEngine`, která definuje základní rozhraní a chování pro všechny moduly. Přesněji řečeno se jedná o funkce `on_enable()`, `on_disable()`, které jsou volány při aktivaci a deaktivaci modulu, a dekorátor `@requires_active`, který zajišťuje, že funkce proběhne pouze, pokud je modul aktivní. Mimo tyhle komponenty je každý engine modul obyčejná třída, která může obsahovat libovolné funkce a data pro implementaci své funkcionality, které mohou být spuštěny i bez dekorátoru na pozadí. Je nutno podotknout, že tenhle aktivní stav modulu slouží spíše na označení a oznámení, jelikož špatně naprogramovaný modul může posílat požadavky do vykreslovače i když není aktivní.

### 4.1 `EngineManager`
Manažer engine modulů, `EngineManager`, je zodpovědný za správu všech modulů, včetně jejich aktivace, deaktivace a přepínání mezi nimi. Udržuje seznam všech dostupných modulů, který je vytvořen při postupném volání funkce `register_engine()` z každého modulu, který následně spouští funkce `on_enable()` a `on_disable()` a kontroluje aktivní stav modulu při volání funkcí dekorovaných `@requires_active`. Tento přístup umožňuje snadné přidávání nových modulů bez nutnosti měnit stávající kód, protože každý modul se stará pouze o svou vlastní funkcionalitu a manažer se stará o jejich správu a koordinaci. [🎨🎨 doplnit diagram engine správy]

## 5. Systém efektů
Jak bylo zmíněno dříve, efekty jsou implementovány jako samostatné Python skripty dědící z třídy `LightEffect`. Celý systém efektů je řízen modulem `EffectsEngine`, který slouží jako most mezi jednotlivými efekty a zbytkem aplikace.

### 5.1 Dynamické načítání scriptů
Efekty jsou načítány dynamicky při startu serveru, což znamená, že není nutné restartovat aplikaci při přidání nového efektu - stačí umístit Python soubor do složky `effects/` a restartovat server. Proces načítání využívá modul `importlib`, který umožňuje importovat Python moduly za běhu programu.

````python
def load_effects(self, folder="effects"):
    Log.info("EffectsEngine", "Loading and validating effects...")
    self.effects = {}
    for filename in os.listdir(folder):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            module = importlib.import_module(f"{folder}.{module_name}")
            for attr in dir(module):
                cls = getattr(module, attr)
                if hasattr(module, "LightEffect") and isinstance(cls, type) and \
                   issubclass(cls, module.LightEffect) and cls is not module.LightEffect:
                    thrown_exception = self.validate_effect(cls)
                    if thrown_exception is None:
                        self.effects[module_name] = cls
````

Důležitou součástí načítání je validace efektů. Každý efekt je před přidáním do seznamu dostupných efektů otestován spuštěním. Používá se `DummyRenderer` třída, která simuluje renderer bez skutečného ovládání LED diod. Tím se zajistí, že chybně napsaný efekt nezpůsobí pád celé aplikace.

Pro optimalizaci výkonu je implementován cachování systém. Každý efekt je hashován a pokud se jeho hash nachází v cache jako validní, přeskočí se jeho validace. To výrazně zrychluje start aplikace, protože validace může být časově náročná.

### 5.2 Nevýhody (bezpečnostní rizika)
Dynamické načítání a spouštění Python kódu přináší významná bezpečnostní rizika. Každý Python soubor umístěný do složky `effects/` je bez omezení spuštěn se všemi právy aplikace. Škodlivý efekt by mohl:

- Číst a modifikovat libovolné soubory na systému
- Spouštět externí příkazy a programy
- Navázat síťová spojení a odesílat data ven
- Manipulovat s hardware prostředky (GPIO piny, USB zařízení)

Tento přístup je akceptovatelný pouze v důvěryhodném prostředí, kde máte plnou kontrolu nad obsahem složky `effects/`. Pro produkční nasazení v nedůvěryhodném prostředí by bylo nutné implementovat sandboxing (například pomocí `RestrictedPython` knihovny) nebo přesunout spouštění efektů do izolovaného prostředí (Docker container s omezenými právy).

## 6. Webové rozhraní
Webové rozhraní je primární způsob interakce uživatele s aplikací. Pro backend se využívá knihovny Flask se značnou částí vykreslování na straně serveru (server-side rendering) a klasický HTML/CSS/JavaScript bez frameworků pro frontend. Pro komunikaci v reálném čase, jako je kalibrace nebo ovládání audio přehrávače (více v kapitole 7), se používají WebSockets implementované pomocí Socket.IO.

### 6.1 Flask API (HTTP requesty)
Backend je postaven na frameworku Flask, který poskytuje jednoduchý způsob vytváření webových API. Každý engine modul a část aplikace má své vlastní endpointy pro správu své funkcionality. Například:

**Správa efektů:**
- `GET /api/get_state` - Vrací aktuální stav (aktivní efekt a jeho parametry)
- `POST /api/set_effect` - Nastaví aktivní efekt
- `GET /api/get_parameters/<effect_name>` - Vrací seznam parametrů daného efektu
- `POST /api/set_parameter` - Nastaví hodnotu parametru aktuálního efektu

**Správa rozložení:**
- `POST /api/change_setup` - Přepne aktivní rozložení LED diod
- `POST /api/calibration/new_setup` - Vytvoří nové rozložení
- `POST /api/calibration/show_pixel` - Rozsvítí konkrétní LED při kalibraci

**Získání dat:**
- `GET /api/get_audio_files` - Seznam dostupných audio souborů
- `GET /api/get_image_files` - Seznam dostupných obrázků
- `GET /api/get_video_files` - Seznam dostupných video souborů

Všechny endpointy vrací data ve formátu JSON pro snadnou manipulaci v JavaScriptu. Pro operace vyžadující, aby byl konkrétní engine aktivní, se automaticky kontroluje stav pomocí dekorátoru `@EngineManager.requires_active`.

### 6.2 Nahrávání souborů (audio, video, lightshow)
Pro nahrávání souborů je implementován samostatný modul `upload_files.py`, který zpracovává multipart form data z prohlížeče. Nahrávání podporuje více souborů najednou a automaticky je třídí podle typu:

- **Audio soubory** (.mp3, .wav, .ogg) → `audio/`
- **Video soubory** (.mp4, .avi, .mov, .mkv) → `media/videos/`
- **Obrázky** (.png, .jpg, .jpeg) → `media/images/`
- **Lightshow soubory** (.json) → `lightshows/`
- **Python skripty** (.py) → `effects/`

Endpoint `/api/upload` přijímá POST request s přiloženými soubory a vrací JSON odpověď s výsledkem operace. Pro uživatelské pohodlí je možné přetáhnout soubory přímo do okna prohlížeče (drag & drop) na stránce `/upload`.

## 7. Efekty založené na zvuku
Audio funkcionality jsou implementovány prostřednictvím rozšíření základní třídy `Engine` - třídy `AudioEngine`. Ta přidává metody specifické pro práci se zvukem a synchronizaci s přehráváním.

### 7.1 Zpracování zvukového souboru `AudioEngine`
Třída `AudioEngine` poskytuje kostru pro moduly pracující se zvukem. Obsahuje vlákno s cyklem (`runner`) spouštějící hlavní funkci pro vykreslení efektu `on_frame` a hlavně definuje metody pro zpracování událostí životního cyklu (lifecycle) přehrávání:

- `on_audio_load(audio_path)` - Voláno při načtení audio souboru.
- `on_audio_play()` - Voláno při spuštění přehrávání. Spustí interní runner thread.
- `on_audio_pause()` - Voláno při pozastavení. Zastaví runner thread.
- `on_audio_stop()` - Voláno při zastavení. Vyčistí pixely a resetuje pozici.
- `on_audio_seek(position)` - Voláno při skoku na jinou pozici v souboru.
- `on_frame(current_time)` - Volá se každý snímek během přehrávání s aktuálním časem.

Samotné přehrávání audio probíhá v prohlížeči pomocí HTML5 `<audio>` prvku. Server pouze přijímá WebSocket zprávy o změnách stavu přehrávání (play, pause, seek) a reaguje na ně spuštěním příslušných metod v `AudioEngine`. Toto řešení má několik výhod:

- Není nutné řešit audio output na serveru (Raspberry Pi nemusí mít reproduktor)
- Uživatel může ovládat hlasitost přímo v prohlížeči
- Snížení zátěže na server (dekódování audio probíhá v prohlížeči)
- Nižší latence synchronizace (prohlížeč má přímou kontrolu nad přehráváním)

Narozdíl od standartního `EffectEngine` je `AudioEngine` navržen pro chod ve specifických snímkových intervalech (30, 60 nebo 120 FPS na základě nastavení výkonu), protože synchronizace s hudbou je důležitější než maximální plynulost, a zároveň je potřeba dát dostatek času pro zpracování dat a odeslání na LED diody.

### 7.2 Synchronizace světel se zvukem
Synchronizace je kritická pro dosažení efektu, kdy světla přesně odpovídají hudbě. Systém používá monotonický časovač (`time.monotonic()`) pro sledování času, což zajišťuje přesnost i při změnách systémového času.

````python
def _runner(self):
    while not self._stop_flag:
        elapsed = self._time.monotonic() - self.playback_start_time
        self.current_time = self.seek_time_at_start + elapsed

        if self.current_time >= self.audio_length:
            break

        self.on_frame(self.current_time)
        
        self._time.sleep(1 / self.FPS)
````

Runner běží v samostatném daemon threadu a volá metodu `on_frame()` s aktuálním časem přehrávání. Cílová snímkovací frekvence je nastavena na 30-60 FPS podle výkonu modu v nastavení. Toto je dostatečné pro plynulý vjem, protože lidské oko vnímá změny v osvětlení méně citlivě než video obsah.

#### 7.2.1 Ovládání přehrávače (play, pause, stop)
Komunikace mezi prohlížečem a serverem probíhá přes WebSocket zprávy:

**Z prohlížeče na server:**
- `audio_play` - Spustí přehrávání
- `audio_pause` - Pozastaví přehrávání
- `audio_stop` - Zastaví přehrávání a resetuje pozici
- `audio_seek` - Skočí na jinou pozici (s parametrem `time`)

**Ze serveru do prohlížeče:**
- `audio_ready` - Server je připraven na přehrávání (po dokončení `on_audio_load`)

Tento design umožňuje server připravit data předem, aby nebyl chod přehrávače zhoršen náročnými výpočetními operacemi a teprve poté signalizovat prohlížeči, že je možné začít přehrávat.

### 7.3 Příklad modulu: `VisualizerEngine`
`VisualiserEngine` je implementace automatické audio vizualizace. Využívá FFT (Fast Fourier Transform) analýzu pro rozklad zvuku na frekvenční spektrum a následné zobrazení jako barevné pruhy na LED diodách.

Proces zpracování:
1. **Načtení audio** - Audio soubor je načten pomocí knihovny pro zpracování zvuku
2. **FFT analýza** - Celý soubor je rozdělen na okna a pro každé okno se vypočítá frekvenční spektrum
3. **Předvýpočet snímků** - Pro každý časový snímek (60 FPS) se předpočítá, jaké barvy by měly LED mít
4. **Signalizace připraveného stavu** - Zavolá `ready_callback`, čímž prohlížeč dostane zprávu `audio_ready`
5. **Přehrávání** - Metoda `on_frame()` pouze čte předpočítaná data a odesílá je do vykreslovače

Tento přístup s předvýpočtem je výrazně efektivnější než real-time zpracování, protože výpočetně náročná FFT analýza proběhne pouze jednou, ne každý snímek.

## 8. `LightshowEngine`: Naaranžovaná světelná show
`LightshowEngine` umožňuje vytvářet komplexní, časově synchronizované světelné představení kombinací více efektů na timeline. Na rozdíl od `VisualizerEngine`, který automaticky reaguje na zvuk, lightshow poskytuje plnou manuální kontrolu nad tím, kdy a jak se efekty přehrávají.

### 8.1 Formát souboru
Lightshow je uložena jako JSON soubor s následující strukturou:

```json
{
  "song_name": "Název skladby",
  "song_artist": "Jméno interpreta",
  "song_path": "cesta\\k\\audio\\souboru.mp3",
  "bpm": 182,
  "timeline": [
    {
      "effect": "fade",
      "parameters": {
        "color_from": "#FFFFFF00",
        "color_to": "#FFFFFF77"
      },
      "start": 0,
      "end": 4,
      "layer": 0
    },
    {
      "effect": "sauce:sparkle",
      "parameters": {
        "percentage": 30,
        "color2": "#FFFFFF00"
      },
      "start": 4,
      "end": 5,
      "layer": 0
    }
  ]
}
```

Hlavní časti jsou metadata o skladbě (název, interpret, cesta k audio souboru, BPM) a pole `timeline`, které obsahuje jednotlivé efekty s jejich parametry, časem začátku a konce v taktech a vrstvou, na které se mají přehrávat. Implementován je také systém vrstev, který umožňuje efektům se překrývat a být zobrazeny současně. Efekty na vyšší vrstvě budou vykresleny nad efekty na nižších vrstvách, zárověň jsou všechny barvy definované v RGBA formátu (obsahující červenou, zelenou, modrou a alfa kanál pro průhlednost), což umožňuje efektům být částečně průhledné a umožnit vidět efekty pod nimi. Tento systém vrstvení odemyká prakticky neomezené možnosti pro kreativitu a komplexnost světelných show. Příklad použití by bylo například mít plně neprůhledný efekt, na něm vrstvu s efekty nezakrývající celý prostor, ale pouze část (například jiskry nebo pruh) a nad tím vrstvu s průhlednou bílou barvou pulzující v rytmu hudby pro zvýraznění efektů pod ní či plynulé přechody pomocí efektu přechodu z průhledné do černé a naopak na nejvyšší vrstvě. 

### 8.2 Definice lightshow efektů
Definice efektů pro lightshow je hodně odlišná od efektů pro `EffectEngine`. Každý soubor ve složce `lightshow_effects/` slouží jako balíček efektů s podobným zaměřením definován jako třída dědící z `LightshowEffects`. Každá tahle třída by měla obsahovat dekorátor @namespace("jmeno_jmenneho_prostoru"), který určuje jmenný prostor pro efekty v tomto souboru a je obsažen v referenci efektu v lightshow souborech. Tento přístup byl zvolen, aby se předešlo kolizím názvů efektů mezi různými soubory a aby se daly efekty logicky organizovat do skupin. Inicializační funkce musí také přijímat parametr `coords` obsahující seznam souřadnic LED diod.

Každý efekt je následně definován jako metoda v této třídě s dekorátorem @l_effect(EffectType(Universal/2D/3D)), který určuje, pro jaký typ rozložení světel je efekt určen. Tato metoda musí přijímat parametr `steps`, který určuje počet snímků, který efekt zabírá mezi svým startem a koncem. Dále může přijímat libovolné další parametry pro nastavení efektu, které ale musí obsahovat nápovědu typu (type hint) pro správné zobrazení v editoru lightshow souborů. Metoda musí vracet seznam obsahující seznamy barev pro každou LED diodu pro každý snímek, tedy formátu `List[List[Tuple[int, int, int, int]]]`
Příklad: 

```python
from effects.lightshow_effects import CustomParamType # python neobsahuje vestavěný typ pro reprezentaci barev, proto je vytvořen vlastní CustomParamType.Color, který pracuje jako RGBA tuple pro efekty a jako HEX string v souboru
@namespace("")
class DefaultUniversal(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)

    @l_effect(EffectType.UNIVERSAL)
    def fade(self, steps: int, color_from: CustomParamType.Color = Color.white, color_to: CustomParamType.Color = Color.white):
        # lineární interpolace: výpočet posunu mezi každým krokem pro každý kanál
        step_r = (color_to[0] - color_from[0]) / steps
        step_g = (color_to[1] - color_from[1]) / steps
        step_b = (color_to[2] - color_from[2]) / steps
        step_a = (color_to[3] - color_from[3]) / steps

        frames = []
        for step in range(steps):
            # výpočet mezilehlé barvy pro aktuální krok
            intermediate_color = (
                int(color_from[0] + step * step_r),
                int(color_from[1] + step * step_g),
                int(color_from[2] + step * step_b),
                int(color_from[3] + step * step_a),
            )
            frame = [intermediate_color] * len(self.coords) # kopírování stejné barvy pro všechny LED diody
            frames.append(frame)
        return frames
```

Při načítání lightshow se pro každý snímek (podle nastaveného FPS) a pro každou LED vypočítají všechny efekty v dané vrstvě, jdoucí zespoda nahoru, slučující tuto vrstvu do vrstev níže umístěných. Tyto předpočítané snímky jsou uloženy v paměti jako seznam, takže přehrávání je pak jen čtení z tohoto seznamu - extrémně rychlé.

````python
self.frames = process_lightshow(self.registry, data, LightshowSettings(self.FPS))
self.audio_length = len(self.frames) / self.FPS if self.frames else 0
````

Tento přístup umožňuje přehrávat i velmi složité lightshow s desítkami vrstev a efektů bez záseků, protože veškerá výpočetní náročnost je přesunuta do fáze načítání.

## 9. Další příklady engine modulů
Kromě již zmíněných modulů (`EffectsEngine`, `VisualizerEngine`, `LightshowEngine`) obsahuje aplikace ještě několik dalších užitečných engine modulů.

### 9.1 `CanvasEngine`
`CanvasEngine` transformuje LED instalaci na interaktivní kreslicí plátno. Uživatel může pomocí webového rozhraní klikat na jednotlivé LED pozice a nastavovat jim barvy, čímž vytváří statické obrazce nebo nápisy.

Implementace je velmi jednoduchá - engine pouze udržuje pole barev pro každou LED a poskytuje metody pro jejich čtení a zápis:

````python
def get_pixels(self):
    return self.state

def set_pixels(self, pixel_list):
    if len(pixel_list) != len(self.renderer):
        return
    self.state = pixel_list
    for pix in range(len(self.renderer)):
        self.renderer[pix] = self.state[pix]
    self.renderer.show()
````

Frontend pak poskytuje implementuje <div>, ve kterém jsou LED pozice vykresleny jako klikatelné body. Při kliknutí na bod se odešle požadavek přes HTTP API pro aktualizaci barvy dané LED diody. 

### 9.2 `VideoEngine`
`VideoEngine` umožňuje přehrávat video soubory na LED instalaci. Video je rozloženo do prostoru podle pozic LED diod - každá LED zobrazuje barvu pixelu, který se nachází na její pozici ve videu.

Nejdříve je třeba implementovat systém pro zobrazení obrázku na LED instalaci. Tento projekt obsahuje modul `display_utils.py`, který poskytuje funkci `map_image_to_leds(image, coords)`, která vezme 2D obraz formátu knihovny Pillow se seznamem souřadnic LED diod a vrátí seznam barev pro každou LED diodu podle barvy pixelu na pozici LED v obrázku. Funkce hledá nejbližší pixel v obrazu pro každou LED diodu a použije jednoduché vzorkování pomocí box filtru (průměr barev pixelů v okolí LED diody) pro hladší a výstižnější zobrazení. Tato funkcionalita umožňuje zobrazit libovolný obrázek na LED instalaci, i když rozlišení LED diod je mnohem nižší než rozlišení videa. Pro přehrávání videa se tento proces opakuje pro každý snímek videa, čímž se vytvoří animace, společně s audio stopou pro synchronizaci. Posun ve videu se dá ovládat pomocí <audio> prvku poskytnutý modulem AudioEngine.

`VideoEngine` tudíž dědí z `AudioEngine`. Vzhledem k výpočetní náročnosti práce s video soubory, audio část je extrahována předem již při nahrávání videa pomocí podstránky pro nahrávání souborů, která využívá FFmpeg pro extrakci audio stopy z videa a uložení jako samostatný MP3 soubor. Video soubor je při načítání zpracován pomocí knihovny ImageIO, která je lehčí a efektivnější oproti jiným knihovnám, a pro každý snímek se zavolá funkce ze zmiňovaného `display_utils.py` pro získání barev pro LED diody. Tyto barvy jsou uloženy v paměti jako seznam snímků, které se pak během přehrávání pouze čtou a odesílají na LED diody.

Nevýhodou je vysoká spotřeba paměti při delších videích, protože každý snímek musí být uložen v paměti. Pro video v délce 3 minuty při 30 FPS a 200 LED to představuje cca 10 MB RAM (3×60×30×200×3 bajtů).

## 10. Config, logování, cache
### 10.1 Config
Konfigurace celého projektu leží v souboru config/server_config.json, který obsahuje nastavení pro různé části aplikace, jako je poslední zapnutý efekt, všechny hodnoty z nastavení, aktuální rozložení LED diod a zvolené hodnoty pro všechny parametry efektů. Tento soubor je načítán při startu serveru a spravován modulem `config_manager.py`, který poskytuje funkce pro získání a aktualizaci jednotlivých nastavení. Data ze souboru jsou uchovány v instanci třídě Config, která je implementována jako singleton, což zajišťuje, že všechny části aplikace pracují se stejnou jedinou instancí konfigurace. Modul je velmi jednoduchý, umožňuje interakci s daty přímo ve slovníku `Config().config[]` a vyžaduje explicitní volání `Config().save()` pro uložení změn do souboru. Na ukládání a načítání používá modul vestavěnou knihovnu `json` pro práci s JSON formátem. 

### 10.2 Logování
Pro sledování chodu aplikace a usnadnění ladění je implementován vlastní systém logování v modulu `log_manager.py`. Modul je staticky implementován, proto umožňuje volat funkce pro logování z libovolné části kódu bez nutnosti předávání instance loggeru. Logovací funkce (info, warn - varování, error - chyba, debug - zpráva pro ladění) přijímají název zdroje (například název modulu nebo funkce) a zprávu, kterou chtějí zalogovat. Logy jsou ukládány do složky logs s názvem souboru odpovídajícím datu a času spuštění serveru. Každý log obsahuje časovou značku, úroveň logu, název zdroje a samotnou zprávu. Frontend také poskytuje zobrazení logů, barevně označené a filtrovatelné podle zdroje. Vše je samozdřejmě viditelné v konzoli pro snadný přístup během vývoje.

### 10.3 Cache
Jeden z nejdůležitějších optimalizačních mechanismů je bez pochyby cache. Vzhledem k tomu, že některé operace, jako je validace efektů nebo načítání lightshow, mohou být velmi náročné na výkon, implementoval jsem systém cache pro ukládání výsledků těchto operací. Modul `caching.py` umožňuje ukládání a čtení souborů podle jména, které jsou modulem ukládány do složky `.cache/`. Soubory mají stanovenou příponu .cache, ale jsou to jednoduché textové soubory a data jsou do nich ukládána ve formátu JSON pro snadnou manipulaci. Nejvýznamnější využití cache je při načítání efektů, kde se ukládá seznam hashů ověřených efektů.

## 11. Závěr a budoucí rozvoj

### 11.1 Shrnutí dosažených cílů
Projekt Spectraforge úspěšně implementuje komplexní systém pro řízení adresovatelných LED diod s následujícími klíčovými funkcemi:

**✅ Realizováno:**
- Plně funkční webové rozhraní pro ovládání z mobilních zařízení i desktopu
- Systém pro automatickou kalibraci pozic LED v 2D i 3D prostoru
- Dynamické načítání efektů umožňující snadné přidávání nových animací
- Audio vizualizér s real-time FFT analýzou
- Lightshow editor pro tvorbu časově synchronizovaných představení
- Podpora pro přehrávání video obsahu na LED instalaci
- LED simulátor pro vývoj bez fyzického hardwaru
- Modulární architektura založená na engine systému
- Post-processing filtry (jas, gamma korekce)

Aplikace byla úspěšně nasazena na Raspberry Pi Zero 2W a testována s 200 LED diodami ve 3D instalaci (vánoční stromek). Dosahuje stabilní snímkovací frekvence 30-60 FPS i u složitějších efektů, což je dostatečné pro plynulý vizuální vjem.

### 11.2 Možnosti rozšíření (nové hardwarové platformy, ESP32)
Ačkoliv je současná implementace plně funkční, existuje prostor pro budoucí vylepšení:

**Hardwarové rozšíření:**
- **ESP32 podpora** - Portace na mikrokontrolér ESP32 by umožnila levnější a kompaktnější řešení. ESP32 má vestavěné WiFi, podporuje až 8 paralelních RMT kanálů pro řízení LED a spotřebovává řádově méně energie. Implementace by vyžadovala přepsání do C++ (Arduino framework) a zjednodušení webového rozhraní.
- **Více LED pásků paralelně** - Současná implementace podporuje pouze jeden datový pin. Rozšíření o více výstupů by umožnilo řídit tisíce LED současně s rozdělením zátěže.
- **DMX512 protokol** - Přidání podpory pro DMX512 by umožnilo ovládat profesionální stage lighting hardware.

**Softwarové vylepšení:**
- **Cloud synchronizace** - Možnost sdílet efekty a lightshow mezi více zařízeními.
- **MIDI vstup** - Řízení efektů pomocí MIDI kontrolérů pro live performance.
- **Generativní efekty** - Integrace AI modelů pro automatické generování efektů na základě hudby.
- **Hardwarové tlačítka** - Podpora pro GPIO tlačítka na Raspberry Pi pro ovládání bez nutnosti webového rozhraní.

**Optimalizace:**
- **Rust/C++ core** - Přepsání výkonově kritických částí (renderer, FFT analýza) do rychlejšího jazyka s Python bindings.
- **GPU akcelerace** - Využití GPU pro matematické výpočty (pokud je dostupné).
- **Streaming lightshow** - Místo předvýpočtu celé lightshow v paměti postupné generování snímků na vyžádání.

Projekt prokázal, že i s omezeným hardwarem je možné vytvořit pokročilý systém pro řízení LED světel s bohatými možnostmi přizpůsobení a rozšíření. Modulární architektura zajišťuje, že jakékoliv budoucí rozšíření lze přidat bez zásahu do stávajícího kódu, což činí Spectraforge vhodnou platformou pro dlouhodobý vývoj a experimentování.