# Finanční aplikace pro backtestování akcií - Alfint 

Alfint je aplikace pro zpětné testování akcií na základě uživatelsky definovaných parametrů. Umožňuje uživatelům zvolit si klíčové finanční ukazatele a strategie, které chtějí otestovat na historických datech, a poskytuje přehledné výsledky, které jim pomohou zhodnotit výkonnost vybraných akcií v minulosti. Cílem aplikace je zefektivnit analýzu investičních strategií a nabídnout uživatelům jednoduchý nástroj pro simulaci jejich obchodních rozhodnutí. Dále nabízí vešekeré finančí ukazatele, ať už dnešní, nebo ty z historie.

## Funkce:
- Zpětné testování akcií na základě historických dat podle výběrů ukazatelů
- Vizuální zobrazení výkonnosti strategie
- Možnost úpravy a optimalizace vstupních parametrů
- Generování reportů s výsledky zpětného testování
- Vytvoření porfolia
- Sdílení portfolia/strategie s ostatními uživateli
- Všechny ukazatelé dané společnosti
- Možnost přehrát na graf ceny taky graf ukazatele
- Vytvoření grafu z akcií v portfoliu


## Co se tím naučím:
- Práce s vekým množstvím finančních dat a jejich analýzou
- Základy algoritmického obchodování a tvorba obchodních strategií
- Použití knihoven pro práci s daty v Pythonu (např. pandas, matplotlib)
- Vytvoření uživatelsky přívětivého rozhraní pro aplikaci
- Jak provádět backtesting a interpretovat výsledky z pohledu investičních strategií

## Technologie:
- Django
- Python 
- yfinance knihovna
- simfin knihovna
- randál dalších 

### inspirace:
- Simfin

### ČASOVÝ HARMONOGRAM

#### Září:
- Vytvoření projektu na githubu
- Průzkum technologií 
- Vymyšlení konceptu aplikace
- Funkce pro získání dat a uložení do databáze
#### Říjen:
- Vypsání všech akcií na stránku
- Stránka detailu akcie 
- Základní uživatelské rozhraní 
- Vytvoření uživatele
#### Listopad:
- Login systém 
- Vytvoření portfolia a přidání akcií do něj
- Vytvoření stránky s filterem, která vyfiltruje akcie podle finančních ukazatelů
- Stránka s portfoliem ukazuje akcie, výkonnost i grafy
#### Prosinec:
- Rozšíření modelů o více dat
- Upravený způsob filtrování akcií - možnost odebirát a upravovat akcie
- Paging(stránkování), kvůli dlouhému načítání filteru
- Vylepšená grafika a celkově UI

##Možná vylepšení:
- Možnost stažení výsledků
- Určit období backtestu
- Kalendář událostí
- Komentovat strategie


### Instalace:
- Klonování repozitáře:
- git clone https://github.com/Vojtik1/Rocnik.git
- python -m venv .venv
- Vytvoření virtuálního prostředí do složky .venv
- python -m venv .venv
- Aktivace virtuálního prostředí
- .venv\Scripts\activate
- Pro Linux:
- . .venv\bin\Activate
- Instalace závislostí
- pip install -r requirements.txt
- Spuštění aplikace
- python manage.py runserver
- Přístupové údaje do administrace
- superuživatel: admin
- heslo: admin
