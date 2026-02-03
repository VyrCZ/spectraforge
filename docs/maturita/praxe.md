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
Pokud chcete přidat parametry, které lze měnit z aplikace, použijte metodu `add_parameter()`, která vrací objekt parametru, ze kterého můžete získat aktuální hodnotu pomocí metody `get()`. Hodnoty parametrů jsou perzistentní a jejich hodnoty se ukládají do souboru s nastavením. Při jejich inicializaci musíte zadat název, typ parametru (číselný posuvník, výběr barvy, přepínač ano/ne, tlačítko) a výchozí hodnotu. Posuvník taky vyžaduje hodnoty min, max a step typu float (nebo int) a tlačítka mohou obsahovat argument onClick typu funkce, která se zavolá při kliknutí na tlačítko, nebo případně argumenty onDown a onUp pro funkce, které se zavolají samostatně při stisknutí a uvolnění tlačítka.

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
