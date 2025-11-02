# Teoretický úvod maturitní práce z programování

### 1. Úvod do problematiky, tématu, projektu

- Stručné představení tématu a jeho významu (proč je daný program či oblast důležitá).
- Motivace k výběru tématu (osobní, profesní, společenský význam).
- Vymezení základních pojmů a terminologie, které budou v práci použity.
- Úvod by měl být výstižný, srozumitelný i pro neodborníka, obvykle do 250–300 slov.


### 2. Historie a kontext

- Přehled vývoje dané oblasti programování či technologie, zasadit do rámce.
- Zmínka o významných algoritmech, jazycích, nástrojích... ve vztahu k vaší práci.


### 3. Teoretická východiska

- Popis základních principů, na kterých je program založen (např. objektově orientované programování, algoritmy, datové struktury). Vždy v souvislosti se samotným programem.
- Vysvětlení používaných metod, technologií a jejich význam v rámci projektu. Myšleno obrazně - zda některé základní rysy nebo aspekty programování jste využívali i vy ve své práci, přístupy k programování, paradigmata atd.
- Porovnání možných přístupů a zdůvodnění výběru konkrétního řešení.


### 4. Použité technologie a nástroje (teoreticky)

- Obecný popis programovacího jazyka a nástrojů (frameworky, knihovny) využitých v projektu.
- Vysvětlení, proč jsou vhodné pro daný typ úlohy.
- Může obsahovat i stručný přehled alternativ a jejich porovnání.


### 5. Bezpečnostní a etické aspekty (pokud relevantní)

- Základní bezpečnostní rizika spojená s aplikací.
- Etické otázky vývoje a používání softwaru.


### 6. Shrnutí a přechod k praktické části

- Krátké shrnutí teoretických poznatků.
- Náznak, co bude následovat v praktické části (bez detailů implementace).


## Další tipy a rady pro teoretický úvod

- **Vyhněte se přílišnému rozepisování** — úvod má být stručný, jasný a výstižný.
- **Citujte relevantní odborné zdroje** (knihy, články, dokumentace) pro doložení teoretických faktů.
- **Používejte přehledné členění** s jasnými nadpisy a podnadpisy.
- **Terminologii vysvětlujte srozumitelně**, ale ne příliš zjednodušeně.
- **Nepopisujte detaily implementace programu** — to patří do praktické části.
- **Formátujte text podle předlohy** (viz HaKa).


## Doporučené způsoby citování v teoretické části

- Citace by měly být přesné, uvádějte autora, název, rok vydání a zdroj.
- Používejte citační styl např. ČSN ISO 690, APA, Harvard.
- Citace AI nástrojů (ChatGPT, Perplexity) dle dostupných konvencí (např. citace.com).
    - Uveďte autora (většinou společnost OpenAI pro ChatGPT, Perplexity Inc. pro Perplexity).
    - Uveďte rok vydání verze modelu (např. 2023, 2024).
    - Název nástroje a verzi (např. *ChatGPT-4* [Large language model]).
    - Typ zdroje (např. [AI program], [AI vyhledávač]).
    - URL odkazu na službu.
    - V textu práce popište, jak jste AI nástroj použili (např. generování textu, konzultace).
    - Pokud je možné, přiložte přepis konverzace nebo souslednost základních promptů.


## Přehledná tabulka – co může obsahovat teoretický úvod

| Kapitola / Sekce | Obsah / Náměty |
| :-- | :-- |
| Úvod do problematiky | Představení tématu, motivace, význam, základní pojmy |
| Historie a kontext | Vývoj oblasti, milníky, současný stav |
| Teoretická východiska | Principy programování, algoritmy, datové struktury, metody |
| Použité technologie | Programovací jazyk, knihovny, frameworky, jejich stručný popis a důvody výběru |
| Bezpečnost a etika | Základní bezpečnostní rizika, etické otázky |
| Shrnutí a přechod | Krátké shrnutí, uvedení praktické části |
| Citace | Odborná literatura, dokumentace, AI zdroje (ChatGPT, Perplexity) |









---

## Teoretický úvod maturitní práce z programování

### Úvod do problematiky, tématu, projektu
Projekt se zaobírá platformou umožňující jednoduché řízení jednotlivě adresovatelných LED světel řízenou přes webové rozhraní. Obsahuje systém pro dynamické načítání světelných efektů, audio vizualizaci automatickou i ruční a nástroje pro kalibraci LED v 2D i 3D prostoru. Cílem je vytvořit flexibilní a rozšiřitelný framework, který umožní uživatelům snadno přidávat nové efekty či jiné funkčnosti a ovládat LED rozložení v reálném čase.

### Historie a kontext
Adresovatelná LED světla jsou celkem moderní technologií. Dříve bylo možné řídit LED světla pouze pomocí externích řadičů, jako je TLC5940 vytvořený v roce 2006, ale tenhle přístup byl omezený počtem kanálů v řadiči a složitostí zapojení. Okolo roku 2010 vznikly integrované řadiče, jako WS2801 a později pokročilejší WS2812, které jsou obsaženy u každé LED, umožňující individuální ovládání pomocí jediného datového vodiče. Tato technologie umožnila vznik lepších a levnějších LED zařízení, jako jsou LED pásky a matice, které umožňují jednoduché experimentování pro lidi se zájmem o mikrokontroléry a programování. 

### Základní pojmy
- Engine: jednotlivé moduly, části kódu implementující konkrétní funkcionalitu (efekty, kalibrace, audio vizualizace).
- Světelný efekt: programovatelný vzor nebo animace zobrazena pomocí Enginu na efekty.
- Parametr efektu: nastavitelná hodnota ovlivňující chování efektu (rychlost, barva, intenzita).
- Renderer: modul zodpovědný za vykreslování efektů na LED.
- Setup 2D/3D: fyzické uspořádání LED v prostoru, které je potřeba definovat pro správnou funčnost efektů.
- Kalibrace: proces mapování fyzických LED na virtuální souřadnice pro přesné vykreslování.
- Lightshow: předem naprogramovaná sekvence efektů a akcí synchronizovaných s časovou osou.
- Vizualizér: engine pro vizualizaci audio signálů a synchronizaci s LED efekty.

### Využité technologie
Jako hlavní programovací jazyk byl zvolen Python pro rychlý vývoj, rozsáhlý ekosystém knihoven a moji znalost. Alternativně by se mohl použít jazyk C++ kvůli jeho výkonu a efektivitě. Pro webové rozhraní jsou použity knihovny Flask, která umožňuje snadnou tvorbu HTTP serveru, jeho API a rozšíření Flask-SocketIO, která zjednodušuje komunikaci v reálném čase pomocí WebSocketů (Socket.IO). Pro frontend je využito HTML, CSS a čistý JavaScript bez frameworků.

### Architektura projektu
Projekt klade silný důraz na modularitu a hojně využívá objektově orientované programování (OOP). Hlavní třída je `Engine`, ze které všechny ostatní moduly dědí a získávají společné metody a dekorátor, který zajišťuje, že pouze jeden modul může upravovat světla v daném okamžiku. Poté existuje rozšíření třídy `AudioEngine`, obsahující funkce pro správné přehrávání k doprovodnému audio souboru. Další důležitá část je `EngineManager`, který spravuje všechny zaregistrované `Engine` třídy a zajišťuje, že pouze jeden je aktivní a může měnit světla. Poslední důležitá třída je `LEDRenderer`, která zajišťuje vykreslování efektů na LED hardwaru nebo simulátoru. Komunikace mezi klientem (webovým prohlížečem) a serverem probíhá přes REST API a WebSockety, což umožňuje rychlé reakce na uživatelské vstupy a real-time aktualizace efektů.

### Bezpečnost a nedostatky
Projekt je určený pro lokální použití v domácím prostředí, a proto bezpečnostní aspekty nejsou prioritou. Jednotlivé efekty jsou definovány jako Python skripty, což přináší riziko spuštění škodlivého kódu na zařízení serveru. Přístup do rozhraní taky není nijak omezen, kterékoli zařízení v síti může ovládat LED. Tyto nedostatky jsou akceptovány vzhledem k zamýšlenému použití projektu.


## Praktická část

### Obsah

1. Potřebný hardware, příklad a zapojení

2. Geometrické uspořádání LED světel
2.1. Způsoby získání LED pozic
2.1.1. 2D uspořádání
2.1.2. 3D uspořádání

3. Vykreslování dat na LED světla

4. Architektura modulů (`Engine`) a jejich správa
4.1. Definice a role modulů v systému (Modulární architektura a její výhody)
4.2. Správa modulů a jejich interakce
4.3. Jednoduchý příklad implementace vlastního modulu (`CanvasEngine`)
4.4. `AudioEngine` a synchronizace s audio soubory

5. EffectEngine a tvorba světelných efektů
5.1. Dynamické načítání python scriptů
5.1.1. Struktura efektů a jejich implementace
5.2. Parametrizace efektů
5.3. Design efektů a uživatelská přizpůsobitelnost
5.4. Příklady efektů

6. Rozhraní pro ovládání: Server a webové UI

7. Vizualizace audio signálu
7.1. Teoretické základy audio vizualizace
7.2. Algoritmy pro analýzu audio signálů
7.3. Příklady aplikací audio vizualizace v praxi

### 1. Potřebný hardware, příklad a zapojení
Pro provoz systému jsou potřeba jednotlivě adresovatelná LED světla a řídící zařízení. V mém případě jsem použil 4x adresovatelné 50 LED WS2811B řetězce a Raspberry Pi Zero 2W pro řízení světel a běh serveru. Raspberry Pi je napájeno nabíječkou na telefon vydávající 5V 2A. LED řetězce jsou zapojeny do GPIO 18 pinu na Raspberry Pi, které je standardně používáno pro LED světla. Jako zdroj používám 5V 6A nabíječku na telefon, která připojena k prvnímu a třetímu řetězci. Druhý a čtvrtý řetězec jsou napájeny z řetězce předchozího.

[Schéma zapojení LED světel s Raspberry Pi](docs/wiring.png)

Komunikace mezi Raspberry Pi a řídícím telefonem probíhá přes Wi-Fi síť, kde Raspberry Pi vytváří schovaný přístupový bod. Telefon se připojí k této síti a otevře webové rozhraní pro ovládání LED světel.


### 2. Způsoby získání LED pozic v prostoru
Nyní máme LED světla zapojená a připravená k použití, ale pro komplexnější efekty je nejdříve potřeba definovat jejich pozice v prostoru. 

#### 2.1 2D uspořádání
Na 2D ploše je mnohem jednodušší definovat pozice LED světel. Světla po jednom rozsvítíme a pořídíme fotografii povrchu. Je důležité, aby kamera byla fixována a byla umístěna co nejvíce kolmo k povrchu. Díky tomu můžeme zanedbat perspektivní zkreslení a výstup z detekčního algoritmu můžeme přímo použít jako souřadnice LED světel. Hledat LED na obrázku můžeme hledat několika způsoby, záleží na prostředí, ve kterém jsou LED světla umístěna. Nejjednodušší způsob je detekce jasných pixelů na tmavém pozadí.
```python
  image_path = os.path.join(self.image_dir, file_name)
  image = Image.open(image_path).convert("L")
  renderer = image.load()
  width, height = image.size

  # najde nejvyšší hodnotu jasu v obrázku
  brightest_value = 0
  for x in range(width):
      for y in range(height):
          if renderer[x, y] > brightest_value:
              brightest_value = renderer[x, y]

  # sebere souřadnice všech pixelů s maximálním jasem
  brightest_renderer = []
  for x in range(width):
      for y in range(height):
          if renderer[x, y] == brightest_value:
              brightest_renderer.append((x, y))

  # pokud nejsou nalezeny žádné jasné pixely, vrátí střed obrázku jako bezpečné záložní řešení
  if not brightest_renderer:
      return width // 2, height // 2

  # vypočítá středový bod jasných pixelů
  sum_x = sum(p[0] for p in brightest_renderer)
  sum_y = sum(p[1] for p in brightest_renderer)
  center_x = int(sum_x / len(brightest_renderer))
  center_y = int(sum_y / len(brightest_renderer))

  # odfiltruje izolované jasné pixely, které jsou daleko od středového bodu (pravděpodobně šum)
  DISTANCE_THRESHOLD = 30
  filtered_renderer = []
  for x, y in brightest_renderer:
      distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
      if distance <= DISTANCE_THRESHOLD:
          filtered_renderer.append((x, y))

  # pokud filtrování odstranilo odlehlé body, znovu spočítá středový bod ze zbylých bodů
  if filtered_renderer:
      sum_x = sum(p[0] for p in filtered_renderer)
      sum_y = sum(p[1] for p in filtered_renderer)
      center_x = int(sum_x / len(filtered_renderer))
      center_y = int(sum_y / len(filtered_renderer))

  return center_x, center_y
```

Tento problém se dá řešit i jinými způsoby, například detekcí specifické barvy nebo detekcí kruhů pomocí Houghovy transformace.

#### 2.2 3D uspořádání
Pro 3D uspořádání je situace složitější. Je potřeba získat prostorové souřadnice LED světel, což vyžaduje použití více kamer nebo pohledů a následná rekonstrukce 3D pozic z 2D obrázků. Tento proces je náročnější na automatizaci a vyžaduje pokročilejší algoritmy, jako je triangulace nebo použití struktur z pohybu (Structure from Motion) nebo dodatečné senzory či hardware, jako jsou LiDAR kamery. V tomto projektu se využívá metoda asistované kalibrace, kde se pořídí fotografie každé individuální diody ze všech čtyř stran a uživatel manuálně přepíná mezi pohledy a označuje LED diody. 3D souřadnice jsou následně vypočítány pomocí os ze dvou na sebe kolmých pohledů.

### 4. Architektura modulů (`Engine`) a jejich správa
#### 4.1 Definice a role modulů v systému (Modulární architektura a její výhody)
Projekt obsahuje mnoho způsobů, jak interagovat se světly, každý podle svých pravidel. Abych tento systém udržel přehledný a rozšiřitelný, je každá funkce implementována jako samostatný modul, nazývaný `Engine`. Všechny moduly dědí ze základní třídy `Engine`, která poskytuje společné metody na bezpečné zapnutí a vypnutí a dekorátor pro zajištění, že pouze jeden modul může upravovat světla v daném okamžiku.

#### 4.2 Správa modulů a jejich interakce
Pro správu modulů je vytvořena třída `EngineManager`, která uchovává seznam všech zaregistrovaných `Engine` tříd a zajišťuje, že pouze jeden je aktivní a může měnit světla. Když je nový modul aktivován, `EngineManager` deaktivuje předchozí modul a umožní novému modulu převzít kontrolu nad LED světly. Tento přístup zajišťuje, že nedojde ke konfliktům mezi moduly a umožňuje snadné přepínání mezi různými funkcionalitami. Jednotlivé moduly mohou komunikovat mezi sebou prostřednictvím svých metod, ty však nesmí být označeny dekorátorem pro úpravu světel, aby nedocházelo k nečekanému přepínání aktivního modulu.

#### 4.3 Jednoduchý příklad implementace vlastního modulu (`CanvasEngine`)
Jako příklad jednoduchého modulu je `CanvasEngine`, který umožňuje uživateli kreslit přímo na LED světla pomocí webového rozhraní. Tento modul implementuje metody pro zpracování uživatelských vstupů a vykreslování na LED podle zadaných souřadnic a barev. Moduly slouží pouze pro backendovou logiku, uživatelské rozhraní je implementováno samostatně ve webovém klientovi. Z tohoto důvodu je `CanvasEngine` velmi jednoduchý a obsahuje pouze základní metody pro správu stavu LED světel.
```python
class CanvasEngine(Engine):
    def __init__(self, renderer):
        self.renderer = renderer
        self.state = [(0, 0, 0)] * len(renderer)

    def on_enable(self):
        # vyčištění plátna při zapnutí a obnovení stavu při opětovném zapnutí
        for pix in range(len(self.renderer)):
            self.renderer[pix] = self.state[pix]
        self.renderer.show()
        Log.info("CanvasEngine", "CanvasEngine enabled.")

    def on_disable(self):
        # není třeba nic dělat, protože stav je již uložen v self.state
        Log.info("CanvasEngine", "CanvasEngine disabled.")

    # funkce potřebná pro webové rozhraní
    @EngineManager.requires_active
    def get_pixels(self):
        return self.state
    
    @EngineManager.requires_active
    def set_pixels(self, pixel_list):
        """
        Nastaví barvy všech pixelů na plátně.
        (Musíte nastavit celý seznam pixelů, ne jen jeho část.)
        """
        if len(pixel_list) != len(self.renderer):
            Log.warn("CanvasEngine", "Pixel list length does not match the canvas size, not updating.")
            return
        Log.debug("CanvasEngine", pixel_list)
        self.state = pixel_list
        # aktualizace rendereru
        for pix in range(len(self.renderer)):
            self.renderer[pix] = self.state[pix]
        self.renderer.show()
        Log.debug("CanvasEngine", "renderer updated.")
```

#### 4.4 `AudioEngine` a synchronizace s audio soubory
V projektu se nachází více modulů, které používají doprovodnou audio stopu pro synchronizaci světelných efektů s hudbou. Tyto moduly dědí z třídy `AudioEngine`, která rozšiřuje základní `Engine` o funkce pro správné přehrávání audio souboru. Frontend jednotně řeší přehrávání audio souborů a odesílá na server aktuální pozici přehrávání, kterou moduly využívají pro synchronizaci efektů s hudbou. `AudioEngine` poskytuje metody pro získání aktuální pozice přehrávání, získání samotného audio souboru a funkce pro reakci na změny v přehrávání (pauza, skok, zastavení).

### 5. EffectEngine a tvorba světelných efektů
Každý světelný efekt je implementován jako samostatný Python skript v adresáři `effects/`. Všechny musí dědit z třídy `LightEffect`. Správce efektů (`EffectEngine`) má vždy zvolený jeden aktivní efekt, který inicializuje s referencí na renderer a souřadnice LED světel. Správce efektů poté volá metodu `update()` aktivního efektu v nekonečné smyčce. 

```python
from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time

class Breathing(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Breathing", EffectType.UNIVERSAL)
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 50, min=1, max=500, step=1)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.off_time = 0.5
        self.t = 0
        self.dir = 1

    def update(self):
        self.t += self.dir * self.fade_speed.get() / 10000
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            time.sleep(self.off_time)
        for i in range(len(self.renderer)):
            self.renderer[i] = [mu.clamp(int(channel * self.t), 0, 255) for channel in self.color.get()]
        self.renderer.show()
```

#### 5.1 Dynamické načítání python scriptů
Efekty jsou načítány dynamicky při spuštění serveru, pomocí modulu `importlib`.

```python
  def load_effects(self, folder="effects"):
    """Načte všechny efekty ze zadaného adresáře."""
    Log.info("EffectsEngine", "Loading and validating effects...")
    self.effects = {}
    for filename in os.listdir(folder):
      # vyfiltrování pouze .py souborů, které nejsou speciálními soubory jako __init__.py
      if filename.endswith(".py") and not filename.startswith("__"):
        # získání názvu modulu bez přípony
        module_name = filename[:-3]
        module = importlib.import_module(f"{folder}.{module_name}")
        for attr in dir(module):
          cls = getattr(module, attr)
          # kontrola, zda je třída podtřídou LightEffect
          if hasattr(module, "LightEffect") and isinstance(cls, type) and issubclass(cls, module.LightEffect) and cls is not module.LightEffect:
            # uložení do seznamu efektů
            self.effects[module_name] = cls
```

#### 5.2 Parametrizace efektů
Každý efekt může mít své vlastní parametry, které uživatel může měnit přes webové rozhraní. Cílem bylo vytvořit systém, který umožní snadné přidávání nových parametrů pouze ve skriptu efektu. Každý parametr je přidán pomocí metody `add_parameter()`, která požaduje název parametru, jeho typ (posuvník, barva, přepínač) a výchozí hodnotu. Parametry jsou poté automaticky zpracovány webovým rozhraním a jejich hodnoty jsou dostupné v efektu přes metody jako `get()`.

#### 5.3 Design efektů a uživatelská přizpůsobitelnost
Všechny efekty by měly být navrženy tak, aby byly funkční stejně na všech uspořádáních světel. Jelikož souřadnice LED světel mohou být libovolné čísla v libovolném rozsahu, efekty by měly používat poměry a relativní pozice místo pevných hodnot. Efekty by také měly být co nejvíce parametrizované, aby uživatel mohl přizpůsobit jejich chování podle svých potřeb.

#### 5.4 Příklady efektů
Jako příklad jednoduchého efektu je zde implementace efektu "Color Wave", který tvoří barevnou vlnu pohybující se vertikálně přes LED světla. Uživatel může nastavit rychlost vlny, aktivní a pozadí barvu, zda se vlna má odrážet na okrajích nebo obíhat, a šířku vlny.

```python
class ColorSweep(LightEffect):
    def __init__(self, renderer, coords):
      # Inicializace efektu s parametry
        super().__init__(renderer, coords, "Color Wave", EffectType.UNIVERSAL)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 100, min=30, max=200, step=1)
        self.active_color = self.add_parameter("Active Color", ParamType.COLOR, "#FF0000")
        self.background_color = self.add_parameter("Background Color", ParamType.COLOR, "#000000")
        self.bounce = self.add_parameter("Bounce", ParamType.CHECKBOX, True)
        self.width = self.add_parameter("Width", ParamType.SLIDER, 50, min=5, max=50, step=1) # Tloušťka vlny v % výšky
        self.current_y = 0
        self.current_dir = 1
        self.max_y = max(coord[1] for coord in coords)
        self.min_y = min(coord[1] for coord in coords)

    def update(self):
      # aktualizace pozice vlny
        self.current_y += 10 * self.current_dir * self.speed.get() / self.height
        total_height = self.max_y - self.min_y
        wave_width = self.width.get() / 100 * total_height

        if self.bounce.get():
            # Odraz: změna směru při dosažení okrajů
            if self.current_y > self.max_y + wave_width * 0.2:
                self.current_dir = -1
            if self.current_y < self.min_y - wave_width * 0.2:
                self.current_dir = 1
        else:
            # Obíhání: přemístění na opačný konec při dosažení okrajů
            if self.current_y > self.max_y + wave_width:
                self.current_y -= total_height
            elif self.current_y < self.min_y - wave_width:
                self.current_y += total_height

        # Aktualizace barev LED podle vzdálenosti od aktuální Y pozice vlny
        for i in range(len(self.renderer)):
            y = self.coords[i][1]
            
            # Vzdálenost od aktuální Y pozice vlny
            y_distance = abs(y - self.current_y)

            if not self.bounce.get():
                # ber obíhání v úvahu: vypočítej minimální vzdálenost od reálné nebo pomocné vlny
                wrapped_dist = min(abs(y - (self.current_y - total_height)), abs(y - (self.current_y + total_height)))
                y_distance = min(y_distance, wrapped_dist)

            if y_distance > wave_width:
                ratio = 1
            else:
                # vypočítej % vzdálenosti od aktuální Y pozice k výšce LED zdi
                ratio = y_distance / wave_width

            # Lineární interpolace mezi active_color a background_color
            new_color = mu.color_lerp(self.active_color.get(), self.background_color.get(), ratio)
            self.renderer[i] = new_color  # Aktualizace barvy konkrétního bodu

        self.renderer.show()
```

### 6. Rozhraní pro ovládání: Server a webové UI



# ZDROJE: 
chatgpt.com (vytvoř mi srhnutí historie jednotlivě adresovatelných led světel)
github copilot
https://en.wikipedia.org/wiki/Circle_Hough_Transform
https://www.ti.com/product/TLC5940-EP#params