Projekt opis


Projekt opiera się na implementacji dwóch programów nazywanych Klientem i Serwerem. Rolą serwera jest zebranie danych o klientach oraz wygenerowanie danych do obliczeń i przesłanie ich do klientów a następnie zebranie od nich wyników obliczeń. Rolą klienta jest "podłączenie" do serwera i przeprowadzenie podanych obliczeń w sposób jak najbardziej efektywny.

Państwa zadaniem jest napisanie w aplikacji klienta sekcji przetwarzania przychodzących danych (ale można też zmieniać pozostały kod, jezeli komuś na tym bardzo zależy). W optymalnym scenariuszu naszym celem jest przeprocesowanie danych w sposób wielowątkowy i pokazanie, że jest to lepsze podejście niż przetwarzanie jednowątkowe.

Udostępniona implementacja Serwera będzie wykorzystywana do sprawdzenia projektów i ma służyć Państwu w celu możliwości testowania własnego rozwiązania. Nie powinniście Państwo w żaden sposób samodzielnie zmieniać implementacji Serwera.

Komunikacja między Klientem a Serwerem odbywa się po sieci za pomocą REST_API i danych zapisanych w formacie JSON. Uruchamianie akcji na serwerze i w kliencie odbywa się poprzez metody GET protokołu REST, które mogą być symulowane poprzez wejście przeglądarką internetową na określony adres sieciowy.


Aplikacja Klienta


Zadaniem aplikacji klienta jest połączenie z serwer, odbiór danych do obliczeń oraz przesłanie wyniku obliczeń na serwer.

Głowna klasa klienta to plik main.py :

W linijkach:


SERVER_IP = 'localhost'
SERVER_PORT = 5678

CLIENT_IP = 'localhost'
CLIENT_PORT = 6780

INDEKS = 11
Wpisujemy adres IP i port na którym uruchamiana jest aplikacja klienta jak i port i adres serwera. W przypadku uruchomienia obu programów lokalnie na własnym komputerze nie musimy zmieniać niczego w tych linijkach. W czasie uruchomienia na wydziale przy sprawdzaniu projektu jest to miejsce w którym będziemy musieli podać adres IP prowadzącego w miejscu serwera i swojego komputera w miejscu klienta.

W miejscu Indeks powinniśmy podać swój numer indeksu.

Uwaga! Podane wyżej dane są niezależne od tego co wpiszemy przy uruchomieniu programu (kiedy to naprawdę definiujemy port na którym dany program ma się uruchomić)! W związku z tym jeżeli w programie będziemy mieli zapisane inne dane a uruchomimy program z innymi numerami portów nasz program nie zadziała! Proszę więc pilnować spójności pomiędzy tymi elementami.

Po uruchomieniu programu (patrz instrukcje uruchomienia w sekcji poniżej) pierwsza operacja, którą chcemy wykonać to rejestracja klienta na serwerze (zauważmy więc, że na tym etapie serwer też musi być już uruchomiony).

Aby tego dokonać musimy wykonać zapytanie typu GET na adres adres_klienta:nr_portu/hello . Działanie to możemy wykonać wpisując odpowiedni adres w dowolnej przeglądarce internetowej. Dla uruchomienia na własnym komputerze bez zmian w kodzie oznacza to wejście w przeglądarce na adres http://localhost:6780/hello .

Nasz program klienta powinien połączyć się z serwerem i wysyłać mu własny adres IP i port do komunikacji. Serwer wysyła komunikat potwierdzenia połączenia który jest wyświetlany w logach programu. W przelądarce powinniśmy zobaczyć komunikat

Success
W przypadku powodzenia i

Error occurred {res.text}
W przypadku błędu.
Następnie aplikacja klienta oczekuje na przesłanie przez serwer danych do obliczeń.

Przesłane dane są przekanywane do funkcji function, w formie kolejki komunikatów, odczytów symulujących dane z odczytów sensorów na temat warunków pogodowych. W tej funkcji tworzone jest X wątków do przetwarzania danych za pomocą

multiprocessing.Process
Jak i typy danych potrzebne do procesowania tablica do przechowywania wyniku, zamek oraz licznik przeprocesowanych danych (potrzebne tylko ewentualnie do debuggowania) oraz zmienna zapamiętująca liczbę dni dla których generowane są dane. Uwaga! Liczba dni nie jest nigdzie podawana można ją odczytać tylko na podstawie przychodzących danych poprzed określenie maksymalnej wartości dnia w tych danych, co też robi obecnie klient.

W przypadku rozwiązania projektu możecie Państwo oczywiście w tym miejscu określać nowe współdzielone zmienne, czy blokady służące do przetwarzania.

Zmienna:

n_workers = 4 
Określa liczbę wątków uruchamianych na komputerze (zalecam empirycznie sprawdzić różne wartości, w celu określenia, która będzie optymalna na moim komputerze).

Każdy z wątków uruchamia funkcję process, w której to dokonywane jest przetwarzanie danych. Jest to miejsce na którym powinniśmy skupić swoją uwagę i zaimplementować w tym miejscu proces przetwarzania danych w sposób wielowątkowy,

Wyniki z funkcji procesów są zapisywane w tablicy result i wracają do funkcji function, która tłumaczy je na wynik zrozumiały (oczekiwany) przez serwer. Znów nie powinniśmy raczej zmieniać elementów tego kodu. Wynik w tablicy result jest zapisywany w kolejnych indeksach tablicy posortwanych po dniach i w ramach każdego dnia podając kolejne parametry. Szczegółowy opis znajduje się poniżej w sekcji zadanie.



Aplikacja Serwera


Zadaniem serwera jest zebranie danych od klientów i wygenerowanie dla nich danych do obliczeń i przesłanie ich do klientów a następnie zebranie wyników i wypisanie podsumowania.

W celu kontroli procesu serwer zapisuje dane do logu oraz wygenerowane dane w katalogu payloads oraz porównanie wyniku w katalogu results.

Głównym plikiem programu jest plik main.py.

Serwer posiada endpointy na którym dokonuje się "handshake" (uzgodnienie połączenia) gdzie kliencie wysyłają swój adres IP i port a serwer odsyła potwierdzenie nawiązania połączenia. Przy każdym połączeniu serwer podaje łączną liczbę połączonych klientów w terminalu.

Po zarejestrowaniu klienta na serwerze jeżeli chemy uruchomić proces generowania danych i przesłania do klienta musimy wykonać odpowiednie zapytanie GET do serwera. Podobnie jak dla klienta możemy teo dokonać poprzez wejście w przeglądarce na adres na adres_serwera:port/start . W konsoli serwera powinien się pojawić komunikat o wysyłaniu danych. Dla uruchomienia lokalnego bez żadnych zmian oznaza to po prostu wejście przez przeglądarkę na adres http://localhost:5678/start .

W przeglądarce powinniśmy zobaczyć komunikat:

sending
Serwer generuje losowo zadaną w kodzie liczbę danych na podstawie parametrów, liczba dni, odstęp między danymi (przekładający się na liczbę danych) zapisanych w pliku constants.py

START_DATE = '2022-01-01'

# START_DATE + DAY_SHIFT = END_DATE
DAY_SHIFT = 5

# REFRESH INTERVAL BETWEEN DATA POINTS, E.G. "2022-01-01 12:00:00", "2022-01-01 12:03:00"
REFRESH_INTERVAL = '60min'
W tym wypadku wygenerujemy dane dla 5 dni w odstępach co 60 min. Co daje 120 danych, kazde z nich zawiera po 5 parametrów, czyli ostatecznie będzie to 600 odczytów.
Uwaga! Start date nie ma znaczenia, gdyż i tak dzień jest zamieniany na liczbę od 0 do DAY_SHIFT i jest potrzebny tylko dla procesu generowania danych. Klient widzi dni jako numeru od zera a nie jako prawdziwe daty!

Typy przesyłanych danych (które symulujemy), to wilgotność, temperatura, natężenie światła, ciśnienie i opad zapisane angielskimi skrótami:

DATA_TYPES = ['HUM', 'TEMP', 'LIGHT', 'PRESS', 'PREC']
Serwer za jednym razem przesyła do klientów całą kolejkę (listę) odczytów z danymi dotyczącymi symulowanych odczytów z sensorów.

Pojedynczy komunikat ma postać:

{Datatype, Dzien, Wartość}

np

{TEMP, 1, 12}
{HUM, 3, 888}

Przykładowa odpowiedź klienta, której oczekuje serwer to lista zagregowanych wartości odczytów, dla kazdego dnia dla którego były wysłane dane oczekujemy wartości COUNT, MODE, AVG(średniej) odczytów:

Przykład:
[{"day": 0,  "HUM_COUNT": 10, "HUM_MODE": 13, "HUM_AVG": 12, "TEMP_COUNT": 10, "TEMP_MODE": 13, "TEMP_AVG": 12, "LIGHT_COUNT": 10, "LIGHT_MODE": 13, "LIGHT_AVG": 12, "PRESS_COUNT": 10, "PRESS_MODE": 13, "PRESS_AVG": 12, "PREC_COUNT": 10, "PREC_MODE": 13, "PREC_AVG": 12, }]})

Uwaga! Klient posiada metodę generującą dla Państwa podany wyżej format danych wyjściowych.

Serwer zapamiętuje dla każdego parametru, każdego dnia i każdego klienta średnia, max, min wartości. Dodatkowo zapamiętuje czas wysyłania ostatniego zapytania i czas odpowiedzi od klienta odczytów. Po otrzymaniu odpowiedzi od klienta serwer zapisuje wynik porównania wyniku klienta i wlasnych obliczeń w katalogu results (opis w sekcji poniżej).

Uruchomienie

Instrukcje uruchomienia z konsoli są dostępne także w projekcie w plikach readme. Do uruchomienia serwera / klienta w PyCharm, możemy stosować konfigurację (zrzut ekranu konfiuracji także znajdziemy w katalogach z plikami projektów).

Uwaga! Kod wymaga zainstalowanej języka Python w wersji co najmniej 3.10.

Aby uruchomić kod wykonaj następujące kroki:

Wypakuj kod

Uruchom dla klienta :

pip install -r requirements.txt
python -m uvicorn main:app --port 6780


Uruchom serwer:

pip install -r requirements.txt
python -m uvicorn main:app --port 5678

Wejdź na przeglądarkę na adres http://localhost:6780/hello

Wejdź na przeglądarkę na adres http://localhost:5678/start

W katalogu payloads serwera znajdziesz dane wygenerowane przez program

W katalogu results po przesłaniu odpowiedzi przez klienta znajdziesz wynik działania

Edytuj plik constants.py w celu definicji różnej liczby danych do obliczeń dla klienta

Uwaga! W przypadku uruchomienia programu z adresem IP należy zmienić odpowiednie zapisy w kliencie, ale ponadto należy zmienić sposób uruchamiania programu na poniższy:

python -m uvicorn main:app --host 192.168.50.239 --port 5678

python -m uvicorn main:app --host 192.168.50.239 --port 6780



Zadanie projektowe

Naszym celem jest napisanie programu poprawnie zliczającego zagregowane wzlędem dni wartości takie jak liczba odczytów (COUNT), najczęstsza wartość (MODE) - uwaga w przypadku remisów należy wypisać najmniejszą z najliczniejszych wartości, średnia wartości odczytów (AVG) dla symulowanych odczytów parametrów warunków pogodowych. Odczyty przychodzą w losowej kolejności możemy więc otrzymać temperaturę z dnia 5 potem ciśnienie z dnia 2, temperature z dnia 0 itd.

Generowane dane są losowe z zakresu wartości od 0 do 20 .

Chcemy porównać wynik działania z poprawnym wynikiem jaki powinniśmy otrzymać oraz z czasem działania podobnego programu działającego jednowątkowo. Implementacja jednowątkowego programu będzie dostarczona przez prowadzącego. 

Nie powinniście Państwo zmieniać nic w implementacji serwera, ma on na celu pomóc państwu testować własne rozwiązanie i odpowiadać temu jak ostatecznie będzie testowany program.

Głównym przedmiotem państwa zainteresowania jest funkcja

def process(queue: Queue):
która po przepisaniu na multiprocessing będzie zapewne wyglądać mniej więcej tak:
def process(queue: Queue, result : multiprocessing.Array, lock: multiprocessing.Lock...
która przyjmuje kolejkę komunikatów (odczytów) i oblicza wartości wynikowe zapisując je w tablicy pod indeksami

Help.get(data.data_type + '_COUNT') + data.day*20
Słownik Help definiuje indeksy parametrów takich jak TEMP_COUNT, HUM_AVG itp w kolejności w jakiej oczekuje ich funkcja function zapisująca ostateczny wynik w formie akceptowanej przez serwer. Serwer oczekuje wyników jako obiekty zapisujące dzień oraz wartości parametrów. Kod klienta pokazuje przykład jak poradzić sobie z tą sytuacją z pomocą słownika Help, ale można zaimplementować własne rozwiązanie w tym zakresie.

Dlaczego stosujemy Array zamiast Słownika, który byłby wygodniejszym rozwiązaniem? Ponieważ słownik współdzielony przez procesy działa wielokrotnie wolniej i nie jesteśmy w stanie wydajnie przetwarzać przez to danych

https://stackoverflow.com/questions/35353934/python-manager-dict-is-very-slow-compared-to-regular-dict

Można ograniczyć się do zmian tylko w metodach function i process klienta, ale jak ktoś się czuje na siłach może dokonywać DOWOLNYCH zmian w aplikacji klienta, byle na koniec był w stanie realizować wymaganą funkcjonalność, czyli obliczać zagregowane wartości zmiennych.

Opis pliku results:

Plik results_nr_indeksu.txt opisuje

Last data point was sent at 1680435618.5010126, got client response at 1680435618.5705042, diff: 0.06949162483215332s
# days for which data aggregates were generated: 6
# days received from client: 6
W pierwszej linii podawany jest czas wysłania danych do klienta i czas odpowiedzi klienta, oraz różnice która odpowiada ile czasu potrzebował klient żeby przetworzyć dane.

Niżej podana jest liczba dni dla których wygenerowano dane oraz liczba dni odpowiedzi otrzymanych od klienta (gdyby okazało się że np klient liczy tylko 1 dzień podsumowań zamiast dla wszystkich dni).

Pod nimi wypisana jest lista szczegółowych odpowiedzi w postaci ODP_KLIENTA == ODP_SERWERA oraz true albo false mówiące czy te dwie wartości się zgadzają. W ostatniej linijce wypisane jest także podsumowanie mówiące ile wartości na ile jest prawidłowych. Naszym celem jest oczywiście to by wszystkie wartości były prawidłowe.

PREC_MODE: 13 == 13 (True)
PREC_AVG: 0.0 == 16.1308 (False)
Summary : 30/120
