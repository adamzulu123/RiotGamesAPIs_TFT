# RiotGamesAPIs_TFT

Projekt, którego celem jest wizualizacja danych na temat gry TFT od Riot Games. 
Gotowe notebooki z wizualizacją najważniejszych dla nas danych dostępne są w projekcie, w folderze 'Notebooks'.
---

## 🔧 Wymagania wstępne

### Konto Riot Games Developer
Aby móc korzystać z API, załóż konto i wygeneruj swój klucz:
- [https://developer.riotgames.com](https://developer.riotgames.com)

### Zdalna baza danych PostgreSQL
Potrzebna jest baza PostgreSQL, np. w chmurze:
- [https://aiven.io](https://aiven.io)

---

## 📁 Plik `.env`

W katalogu głównym projektu utwórz plik `.env` z następującymi danymi:

```env
RIOT_GAMES_KEY=twoj_klucz
PG_DB_PASSWORD=hasło_do_bazy
PG_DB_USER=nazwa_usera
PG_DB_DATABASE=nazwa_bazy
PG_DB_HOST=host
PG_DB_PORT=port
```

```bash
git clone https://github.com/twoj-login/nazwa-repozytorium.git
cd nazwa-repozytorium
```

2. Stwórz środowisko Conda z pliku environment.yml:
```bash
conda env create -f environment.yml
```

3. Aktywuj środowisko: 
```bash
conda activate pythonProject
```

4. Uruchom projekt w PyCharm
* Otwórz folder projektu w PyCharm
* Ustaw interpreter Conda: pythonProject

---

## Pobieranie danych i analiza

Możesz pobrać dane lub skorzystać z gotowych notebooków i na ich podstawie wyciągnać wnioski. 

### Utwórz schemat bazy danych:
Skorzystaj z gotowego pliku **init_db.sql**, aby zainicjować cały schemat bazy danych, która jest kluczowym elementem przechowywania danych oraz ich późniejszej analizy. 

### Pobieranie danych

Aby pobrać dane z API i zapisać je do bazy danych PostgreSQL:

1. Upewnij się, że masz poprawnie skonfigurowany plik `.env` oraz aktywne środowisko Conda.
2. Uruchom plik `DataUploader.py`, który odpowiada za (razem z DatabaseConnection.py oraz DataPipeline):
   - pobieranie danych z Riot API,
   - hurtowy zapis danych do bazy danych (tzw. bulk insert).
---

### Praca z notebookami
Po zapisaniu danych do bazy możesz analizować je za pomocą plików .ipynb (Jupyter Notebook).





