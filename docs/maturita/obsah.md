# Teoretická část

## 1. Moderní světelné systémy
### 1.1 Historie a vývoj LED technologie
### 1.2 LED mapping vs. projekce

## 2. Technologie adresovatelných LED
### 2.1 Princip fungování (čipy WS281x, SK6812)
### 2.2 Komunikační protokoly a časování
### 2.3 Problematika napájení a distribuce signálu
### 2.4 Teorie barev v digitálním světě (Barevné modely RGB, HSV a aditivní míchání barev)
### 2.5 Lidské vnímání jasu a barev (Proč lidské oko vnímá jas nelineárně a proč musíme matematicky upravovat výstup pro LED (rozdíl mezi lineárním zvýšením proudu a subjektivním pocitem jasu).)

## 3. Hardwarová platforma
### 3.1 Architektura Raspberry Pi (proč jsem si ho vybral)
### 3.2 Způsoby nasazení softwaru
### 3.3 Konfigurace bezhlavého (headless) systému a AP

## 4. Softwarové řešení (Backend)
### 4.1 Jazyk Python v embedded systémech
### 4.2 Knihovna NeoPixel a přímý přístup k DMA
### 4.3 Zpracování multimédií (FFmpeg, PyDub)
### 4.4 3D vizualizace dat pomocí PyVista
### 4.5 Dynamické načítání modulů a bezpečnostní rizika

## 5. Řídicí rozhraní (Frontend)
### 5.1 Architektura klient-server (Flask)
### 5.2 Real-time komunikace pomocí WebSockets (Socket.IO)
### 5.3 Uživatelské rozhraní (HTML/CSS/JS)
### 5.4 Formáty pro výměnu dat (Json, atd.)

---

# Praktická část

## 0. Úvod

## 1. Instalace
### 1.1 Prerekvizice
### 1.2 Instalace

## 2. Způsoby LED pozic v prostoru
### 2.1 2D Režim
### 2.2 3D Režim

## 3. Zobrazování barev na LED diodách
### 3.1 Oddělení barevné logiky od hardwarové vrstvy (`LEDRenderer`)
### 3.2 Simulace LED diod na obrazovce

## 4. Modulární struktura (`Engine`)
### 4.1 `EngineManager`

## 5. Systém efektů
### 5.1 Dynamické načítání scriptů
### 5.2 Nevýhody (bezpečnostní rizika)

## 6. Webové rozhraní
### 6.1 Flask API (HTTP requesty)
### 6.2 Nahrávání souborů (audio, video, lightshow)

## 7. Efekty založené na zvuku
### 7.1 Zpracování zvukového souboru `AudioEngine`
### 7.2 Synchronizace světel se zvukem
#### 7.2.1 Ovládání přehrávače (play, pause, stop)
### 7.3 Příklad modulu: `VisualizerEngine`

## 8. `LightshowEngine`: Naaranžovaná světelná show
- zmínit historii formátu
### 8.1 Formát souboru
- zmínit vrstvy, RGBA
### 8.2 Definice lightshow efektů

## 9. Další příklady engine modulů
### 9.1 `CanvasEngine`
### 9.2 `VideoEngine`

## 10. Optimalizace a výkonnostní testy
### 10.1 Limitace hardwaru (Raspberry Pi Zero 2W)
### 10.2 Měření snímkovací frekvence (FPS)
### 10.3 Profilování kódu a úzká hrdla (Bottlenecks)
### 10.4 Latence sítě při ovládání v reálném čase

## 11. Závěr a budoucí rozvoj
### 11.1 Shrnutí dosažených cílů
### 11.2 Možnosti rozšíření (nové hardwarové platformy, ESP32)


#