# 🧠 RiotGamesAPIs_TFT

Projekt, którego celem jest wizualizacja danych na temat gry TFT od Riot Games. 

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
RIOT_API_KEY=tu_wstaw_swoj_klucz
DB_HOST=tu_wstaw_host
DB_PORT=5432
DB_NAME=tu_wstaw_nazwe_bazy
DB_USER=twoja_nazwa_uzytkownika
DB_PASSWORD=twoje_haslo
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
W celu zmiany sposobu pobierania danych lub ich uruchamiania zaleca się modyfikację klasy DataUploader lub bezpośrednie jej uruchomienie.



