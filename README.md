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
