# ztw-cinema-project - Absolute Cinema
Projekt zaliczeniowy na Zaawansowane Technologie Webowe - Aplikacja kinowa
Aplikacja do zarządzania rezerwacjami i filmami w kinie "Absolute Cinema". Umożliwia adminowi oraz pracownikowi zarządzanie rezerwacjami, filmami, klientami oraz sesjami kinowymi.

// Dokumentacja - o czym jest projekt, instrukcja krok po kroku jak uruchomić kod, najważniejsze pliki naszego kodu zaznaczyć, jakies przykłądy użycia kodu

## Opis projektu
Aplikacja Absolute Cinema to aplikacja webowa umożliwiająca użytkownikom przeglądanie repertuaru kinowego, wybór seansu oraz rezerwację miejsc na wybrane filmy. Oferuje interaktywną mapę sali kinowej do wyboru miejsc. Dodatkowo administrator ma dostęp do specjalnego panelu, który pozwala na zarządzanie filmami, seansami oraz rezerwacjami. Projekt posiada także API, które umożliwia rezerwację biletów poprzez URL.

## Use Case Diagram

![image](https://github.com/user-attachments/assets/978b4ca9-ce66-4934-bfdc-65f00aebf5d2)



## Uruchamianie aplikacji

## Wymagania wstępne

Aby uruchomić aplikację, musisz mieć zainstalowane poniższe narzędzia:

1. **Python 3.x** (zalecana wersja: 3.8 lub wyższa)  
2. **pip** - menedżer pakietów Pythona, aby zainstalować zależności.
3. **Virtualenv** (opcjonalnie, ale zalecane) - do utworzenia wirtualnego środowiska.
4. **Flask** - mikroframework do tworzenia aplikacji webowych w Pythonie.
5. **SQLAlchemy** - biblioteka do obsługi baz danych w aplikacjach Flask.
6. **Werkzeug** - pomocne narzędzie do zarządzania hasłami w aplikacjach Flask.

Wszystkie zależności są zapisane w pliku `requirements.txt`, aby łatwiej je zainstalować.

## Instalacja i uruchomienie

### 1. Klonowanie repozytorium

Zacznij od sklonowania repozytorium:

```bash
git clone https://github.com/wgadzinaAGH/ztw-cinema-project.git
```

### 2. Utworzenie wirtualnego środowiska (opcjonalnie)

Zaleca się utworzenie wirtualnego środowiska, aby unikać konfliktów z innymi projektami. Aby stworzyć wirtualne środowisko:

#### Na systemie Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Na systemie Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalacja zależności

Zainstaluj wszystkie wymagane biblioteki za pomocą `pip`:

```bash
pip install -r requirements.txt
```

### 4. Konfiguracja aplikacji

Aplikacja wykorzystuje bazę danych do przechowywania rezerwacji, klientów i sesji. Przed jej uruchomieniem upewnij się, że masz odpowiednio skonfigurowaną bazę danych.

Jeśli używasz SQLite (domyślnie w aplikacji), nie musisz niczego dodatkowo konfigurować. W przeciwnym razie skonfiguruj odpowiednią bazę danych w pliku `config.py`.

### 5. Uruchomienie aplikacji

Aby uruchomić aplikację, użyj polecenia:

```bash
python app.py run
```

Aplikacja powinna uruchomić się na domyślnym porcie `http://127.0.0.1:5000`.


## Struktura bazy danych
Aplikacja korzysta z bazy danych SQLite, w której zaimplementowano pięć głównych tabel:

### 1. Tabela `filmy`
Przechowuje informacje o filmach dostępnych w repertuarze kina.

| Kolumna        | Typ             | Opis                                      |
|---------------|----------------|-------------------------------------------|
| `id`         | `Integer` (PK)  | Unikalny identyfikator filmu.            |
| `tytul`      | `String(150)`   | Tytuł filmu.                              |
| `opis`       | `Text`          | Opis filmu.                               |
| `gatunek`    | `String(50)`    | Gatunek filmu.                            |
| `dlugosc`    | `Integer`       | Długość filmu w minutach.                 |
| `data_premiery` | `Date`       | Data premiery filmu.                      |
| `plakat_url` | `String(1000)`  | URL do plakatu filmu.                     |

### 2. Tabela `seanse`
Zawiera informacje o seansach filmowych.

| Kolumna    | Typ              | Opis                                       |
|-----------|-----------------|------------------------------------------|
| `id`      | `Integer` (PK)   | Unikalny identyfikator seansu.         |
| `film_id` | `Integer`        | Id filmu, do którego odnosi się seans. |
| `data`    | `Date`           | Data seansu.                            |
| `godzina` | `Time`           | Godzina rozpoczęcia seansu.             |
| `sala`    | `String(10)`     | Numer sali kinowej.                     |
| `cena`    | `Float`          | Cena biletu na seans.                   |

### 3. Tabela `klienci`
Przechowuje informacje o użytkownikach rezerwujących bilety.

| Kolumna    | Typ              | Opis                                        |
|-----------|-----------------|-------------------------------------------|
| `id`      | `Integer` (PK)   | Unikalny identyfikator klienta.          |
| `imie`    | `String(100)`    | Imię klienta.                            |
| `nazwisko` | `String(100)`   | Nazwisko klienta.                        |
| `email`   | `String(150)`    | Unikalny adres e-mail klienta.           |

### 4. Tabela `rezerwacje`
Przechowuje informacje o rezerwacjach miejsc na seanse.

| Kolumna     | Typ              | Opis                                           |
|------------|-----------------|----------------------------------------------|
| `id`       | `Integer` (PK)   | Unikalny identyfikator rezerwacji.          |
| `klient_id` | `Integer`       | Id klienta dokonującego rezerwacji.         |
| `seans_id`  | `Integer`       | Id seansu, na który dokonano rezerwacji.    |
| `miejsca`   | `Text`          | Lista zarezerwowanych miejsc.                |
| `status`    | `String(50)`    | Status rezerwacji (np. "potwierdzona").     |
| `unikalny_kod` | `String(100)` | Unikalny kod rezerwacji.                    |

### 5. Tabela `administratorzy`
Zawiera dane administratorów zarządzających aplikacją.

| Kolumna    | Typ              | Opis                                       |
|-----------|-----------------|------------------------------------------|
| `id`      | `Integer` (PK)   | Unikalny identyfikator administratora.  |
| `imie`    | `String(100)`    | Imię administratora.                     |
| `nazwisko` | `String(100)`   | Nazwisko administratora.                 |
| `email`   | `String(150)`    | Unikalny adres e-mail administratora.    |
| `haslo`   | `String(200)`    | Hasło (powinno być zaszyfrowane).        |
| `rola`    | `String(50)`     | Rola administratora (np. "zarządca").   |


## API – Przykłady użycia

### 1. Pobranie listy filmów
Endpoint:
/api/filmy/

Opis:
Zwraca listę wszystkich dostępnych filmów.

[
  {
    "id": 1,
    "tytul": "Incepcja",
    "opis": "Film science-fiction o podróżach w głąb snów.",
    "gatunek": "Sci-Fi",
    "dlugosc": 148,
    "data_premiery": "2010-07-16",
    "plakat_url": "https://example.com/inception.jpg"
  },
  {
    "id": 2,
    "tytul": "Gladiator",
    "opis": "Historia rzymskiego generała zdradzonego przez cesarza.",
    "gatunek": "Dramat",
    "dlugosc": 155,
    "data_premiery": "2000-05-05",
    "plakat_url": "https://example.com/gladiator.jpg"
  }
]


### 2. Rezerwacja miejsc na seans
Endpoint: 
/api/rezerwacje/

Opis:
Tworzy nową rezerwację na wybrany seans.

Przykładowe żądanie:
{
  "klient_id": 5,
  "seans_id": 1,
  "miejsca": ["A1"],
  "status": "potwierdzona"
}

Przykładowa odpowiedź:
{
  "id": 12,
  "klient_id": 5,
  "seans_id": 1,
  "miejsca": ["A1"],
  "status": "potwierdzona",
  "unikalny_kod": "ABC123XYZ"
}

