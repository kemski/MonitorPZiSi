# Instrukcja Uruchomienia Aplikacji

## Krok 1: Utworzenie środowiska wirtualnego

Otwórz terminal w katalogu projektu i wykonaj:

```bash
python3 -m venv venv
```

## Krok 2: Aktywacja środowiska wirtualnego

```bash
source venv/bin/activate
```

Na Windows:
```bash
venv\Scripts\activate
```

## Krok 3: Instalacja zależności

```bash
pip install -r requirements.txt
```

## Krok 4: Uruchomienie aplikacji

```bash
python app.py
```

Lub użyj skryptu:
```bash
./run.sh
```

## Krok 5: Otwarcie w przeglądarce

Po uruchomieniu aplikacji, otwórz przeglądarkę i przejdź do:

```
http://localhost:5001
```

**Uwaga:** Port został ustawiony na 5001, ponieważ port 5000 jest często zajęty przez AirPlay Receiver na macOS.

## Jak korzystać z aplikacji

### 1. Monitorowanie czasu pracy
- Kliknij przycisk "Rozpocznij Pracę" aby zacząć sesję
- Aplikacja będzie śledzić czas pracy i przypomni o przerwie po 50 minutach
- Kliknij "Zakończ Pracę" aby zakończyć sesję

### 2. Ćwiczenia fizyczne
- Przejrzyj dostępne ćwiczenia w sekcji "Ćwiczenia Fizyczne"
- Kliknij na karcie ćwiczenia, aby zobaczyć szczegółowe instrukcje
- Wykonuj ćwiczenia podczas przerw

### 3. Analiza postawy
- Kliknij "Wybierz Zdjęcie" i wybierz zdjęcie swojego stanowiska z boku
- Po wyświetleniu podglądu kliknij "Przeanalizuj Postawę"
- Aplikacja wyświetli sugestie dotyczące poprawy ergonomii

### 4. Sugestie ergonomiczne
- Przejrzyj ogólne wytyczne w sekcji "Sugestie Ergonomiczne"
- Zastosuj sugestie dotyczące ustawienia krzesła, monitora i klawiatury

## Rozwiązywanie problemów

### Błąd: "ModuleNotFoundError"
Upewnij się, że wszystkie zależności są zainstalowane:
```bash
pip install -r requirements.txt
```

### Port 5001 jest zajęty
Możesz zmienić port w pliku `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5002)  # Zmień na inny port
```

### Zdjęcia nie są przesyłane
Upewnij się, że folder `static/uploads/` istnieje i ma odpowiednie uprawnienia.

## Uwagi

- Aplikacja działa lokalnie na Twoim komputerze
- Statystyki pracy są zapisywane w pliku `work_stats.json`
- Przesłane zdjęcia są przechowywane w folderze `static/uploads/`

