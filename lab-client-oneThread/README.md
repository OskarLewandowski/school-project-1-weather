# aplikacja kliencka

Aplikacja do rejestrowania się na serwerze i odbierania danych

Kroki: 

* Klient laczy sie z serwerem podajac swoj adres ip, port oraz nr indeksu
* Serwer zbiera polaczenia i generuje w katalogu payloads dane
* Serwer po wykonaniu /start uruchamia generowanie danych do klientów
* Klient odsyła wynik
* Serwer waliduje wynik i podaje w folderze /results wynik porównania

## Funkcjonalności

- `/hello` endpoint do rejestracji na serwerze

- `/sensor-data` endpoint do odbioru danych

### Jak uruchomić

- in /app/main.py ustaw poprawnie wartości :

```
   SERVER_IP = 'localhost'
   SERVER_PORT = 5678

   CLIENT_IP = 'localhost'
   CLIENT_PORT = 6780
```
Zainstaluj wszystkie potrzebne pakiety i uruchom serwer lokalnie:

```
pip install -r requirements.txt

uvicorn main:app --port 6780
```

## Additional information

Dokumentacja API  `http://localhost:6780/redoc` 


