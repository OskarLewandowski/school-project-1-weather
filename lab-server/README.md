# serwer produkujacy dane

Aplikacja serwerowa odpowiedzialna za dostarczanie klientom danych szeregów czasowych, 
porównujących wartości zagregowane do przeslanych przez klienta

Kroki: 

* Klient laczy sie z serwerem podajac swoj adres ip, port oraz nr indeksu
* Serwer zbiera polaczenia i generuje w katalogu payloads dane
* Serwer po wykonaniu /start uruchamia generowanie danych do klientów
* Klient odsyła wynik 
* Serwer waliduje wynik i podaje w folderze /results wynik porównania

## Funkcjonalności

- `/clients/handshake`, endpoint który umożliwia "uzgadnianie" połączenia

- `/clients`, endpoint aby mieć przegląd dostępnych klientów

- `/results` endpoint do porównywania zagregowanych wartości
- 
- `/start` endpoint do rozpoczynania przesyłania wartości

## Jak uruchomić

- zapoznaj się z treścią /app/constants.py. W razie potrzeby edytuj `DAY_SHIFT`, `REFRESH_INTERVAL`.

Zainstaluj wszystkie potrzebne pakiety i uruchom serwer lokalnie:

```
pip install -r requirements.txt

uvicorn main:app --port 5670
```

## Dodatkowe informacje

Odwiedź `http://localhost:5670/redoc`, aby zobaczyć dokumentacje API 
