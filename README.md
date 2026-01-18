# MonitorPZiSi

# Aplikacja Monitorująca Równowagę Pracy i Życia

## Opis projektu

Aplikacja desktopowa napisana w Pythonie z wykorzystaniem frameworka Flask, która pomaga informatykom utrzymać zdrową równowagę między życiem zawodowym a prywatnym poprzez:

- **Monitorowanie czasu pracy** przy komputerze
- **Sugerowanie przerw** w odpowiednich momentach
- **Proponowanie ćwiczeń fizycznych** podczas przerw
- **Weryfikację postawy siedzącej** na podstawie zdjęcia stanowiska
- **Sugestie ergonomiczne** dotyczące ustawienia krzesła i stanowiska pracy

## Wymagania

- Python 3.8+
- Zainstalowane zależności z pliku `requirements.txt`

## Instalacja

1. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

2. Uruchom aplikację:
```bash
python app.py
```

3. Otwórz przeglądarkę i przejdź do:
```
http://localhost:5001
```

**Uwaga:** Port został zmieniony na 5001, ponieważ port 5000 jest często zajęty przez AirPlay Receiver na macOS.

## Funkcjonalności

### Monitorowanie czasu pracy
Aplikacja śledzi czas spędzony przy komputerze i wyświetla statystyki dzienne.

### System przerw
Automatyczne przypomnienia o przerwach co określony czas pracy (domyślnie co 50 minut).

### Ćwiczenia fizyczne
Sugestie ćwiczeń dostosowanych do przerw w pracy, z instrukcjami wizualnymi.

### Analiza postawy
Możliwość przesłania zdjęcia stanowiska z boku, które zostanie przeanalizowane pod kątem ergonomii.

### Sugestie ergonomiczne
Rekomendacje dotyczące prawidłowego ustawienia krzesła, monitora i klawiatury.

## Struktura projektu

```
.
├── app.py                 # Główna aplikacja Flask
├── work_monitor.py        # Moduł monitorowania czasu pracy
├── posture_analyzer.py    # Moduł analizy postawy
├── exercises.py           # Moduł ćwiczeń fizycznych
├── templates/            # Szablony HTML
│   └── index.html
├── static/               # Pliki statyczne
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/         # Przesłane zdjęcia
├── requirements.txt      # Zależności projektu
├── README.md            # Dokumentacja projektu
└── .gitignore           # Pliki ignorowane przez Git
```

## Szczegółowy opis modułów

### app.py
Główny plik aplikacji Flask zawierający:
- Konfigurację aplikacji
- Endpointy API dla wszystkich funkcjonalności
- Routing i obsługę żądań HTTP
- Integrację wszystkich modułów

### work_monitor.py
Moduł odpowiedzialny za:
- Śledzenie czasu pracy przy komputerze
- Sugerowanie przerw co określony interwał (domyślnie 50 minut)
- Przechowywanie statystyk dziennych
- Zarządzanie sesjami pracy

### posture_analyzer.py
Moduł analizy postawy zawierający:
- Analizę przesłanych zdjęć stanowiska pracy
- Wykrywanie nieprawidłowej postawy (wersja demonstracyjna)
- Generowanie sugestii poprawy ergonomii
- Bazę wiedzy o prawidłowym ustawieniu stanowiska

### exercises.py
Moduł zarządzania ćwiczeniami:
- Bazę 8 różnych ćwiczeń fizycznych
- Instrukcje wykonania każdego ćwiczenia
- Kategoryzację ćwiczeń (szyja, ramiona, plecy, itp.)
- Informacje o korzyściach z każdego ćwiczenia

## Uwagi techniczne

### Analiza postawy
Obecna implementacja analizy postawy używa podstawowych heurystyk. W rzeczywistej aplikacji produkcyjnej zaleca się użycie:
- Modeli uczenia maszynowego (np. MediaPipe, OpenPose)
- Detekcji pozycji ciała z obrazu
- Zaawansowanej analizy komputerowej obrazu

### Bezpieczeństwo
- W produkcji należy zmienić `SECRET_KEY` na losowy ciąg znaków
- Dodać walidację przesłanych plików
- Zaimplementować autoryzację użytkowników
- Ograniczyć rozmiar przesyłanych plików

### Rozszerzenia
Możliwe rozszerzenia aplikacji:
- Integracja z kalendarzem
- Powiadomienia systemowe
- Eksport statystyk do plików
- Integracja z urządzeniami do monitorowania aktywności
- Wykorzystanie AI do dokładniejszej analizy postawy

## Autor
Przemysław Porębski
Projekt wykonany w ramach przedmiotu "Problemy społeczne i zawodowe informatyki"

