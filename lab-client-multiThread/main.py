import multiprocessing
import threading
from multiprocessing import Queue
from multiprocessing import Process, Array, Manager, Lock

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import logging

app = FastAPI()

logging.basicConfig(handlers=[
    logging.StreamHandler()
],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

global Help
Help = {
    'HUM_COUNT': 0,
    'HUM_MODE': 1,
    'HUM_AVG': 2,
    'TEMP_COUNT': 3,
    'TEMP_MODE': 4,
    'TEMP_AVG': 5,
    'LIGHT_COUNT': 6,
    'LIGHT_MODE': 7,
    'LIGHT_AVG': 8,
    'PRESS_COUNT': 9,
    'PRESS_MODE': 10,
    'PRESS_AVG': 11,
    'PREC_COUNT': 12,
    'PREC_MODE': 13,
    'PREC_AVG': 14,
}

global Type
Type = {
    'HUM': 0,
    'TEMP': 1,
    'LIGHT': 2,
    'PRESS': 3,
    'PREC': 4
}


class SensorDataEntry(BaseModel):
    data_type: str
    day: int
    val: int


class Handshake(BaseModel):
    ip_addr: str
    port: int


SERVER_IP = 'localhost'
SERVER_PORT = 5678

CLIENT_IP = 'localhost'
CLIENT_PORT = 6780

INDEKS = 11111

DATA_TYPES = ['HUM', 'TEMP', 'LIGHT', 'PRESS', 'PREC']


def function(queue: Queue):
    manager = Manager()
    days = manager.list()
    lock = Lock()

    # Określamy długość Array
    result_length = 500000
    day_readings_length = 500000
    day_mode_length = 21 * 500

    result = Array('d', result_length)
    day_readings = Array('i', day_readings_length)
    day_mode = Array('i', day_mode_length)

    number_of_workers = 4

    # Tworzymy procesy
    workers = [Process(target=process, args=(queue, result, day_readings, day_mode, days, lock)) for _ in
               range(number_of_workers)]

    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    wynik = []

    for dzien in range(0, len(days)):
        for type in DATA_TYPES:
            result[Help.get(type + '_AVG') + dzien * len(Help)] /= (float(day_readings[dzien]) / float(len(DATA_TYPES)))
            maksimal = 0
            wy = 0
            for i in range(21):
                if maksimal < day_mode[(Type.get(type) + dzien * len(Type)) * 21 + i]:
                    maksimal = day_mode[(Type.get(type) + dzien * len(Type)) * 21 + i]
                    wy = i
            result[Help.get(type + '_MODE') + dzien * len(Help)] = wy

    # to zostaje bez zmian
    # wypisanie wyniku w formie w której serwer jej oczekuje
    # process zapisuje dane w tabeli pod indeksami po 20 indeksów na dzień w kolejności jak poniżej
    # ponieważ tak jest najbardziej wydajnie
    for dd in range(0, len(days)):
        dzien = {'day': dd,
                 'HUM_COUNT': result[dd * len(Help) + Help.get('HUM_COUNT')],
                 'HUM_MODE': result[dd * len(Help) + Help.get('HUM_MODE')],
                 'HUM_AVG': result[dd * len(Help) + Help.get('HUM_AVG')],
                 'TEMP_COUNT': result[dd * len(Help) + Help.get('TEMP_COUNT')],
                 'TEMP_MODE': result[dd * len(Help) + Help.get('TEMP_MODE')],
                 'TEMP_AVG': result[dd * len(Help) + Help.get('TEMP_AVG')],
                 'LIGHT_COUNT': result[dd * len(Help) + Help.get('LIGHT_COUNT')],
                 'LIGHT_MODE': result[dd * len(Help) + Help.get('LIGHT_MODE')],
                 'LIGHT_AVG': result[dd * len(Help) + Help.get('LIGHT_AVG')],
                 'PRESS_COUNT': result[dd * len(Help) + Help.get('PRESS_COUNT')],
                 'PRESS_MODE': result[dd * len(Help) + Help.get('PRESS_MODE')],
                 'PRESS_AVG': result[dd * len(Help) + Help.get('PRESS_AVG')],
                 'PREC_COUNT': result[dd * len(Help) + Help.get('PREC_COUNT')],
                 'PREC_MODE': result[dd * len(Help) + Help.get('PREC_MODE')],
                 'PREC_AVG': result[dd * len(Help) + Help.get('PREC_AVG')]}
        wynik.append(dzien)

    # to zostaje bez zmian
    requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/results",
                  json={"ip_addr": CLIENT_IP, "port": CLIENT_PORT, "indeks": INDEKS, "aggregates": wynik})


def process(queue: Queue, result, day_readings, day_mode, days, lock: Lock):
    local_day_readings = {}  # Dla optymalizacji, przechowujemy dane lokalnie
    local_day_mode = {}
    local_result_count = {}
    local_result_sum = {}  # Dla obliczenia średniej, potrzebujemy sumy i liczby odczytów

    while True:
        if queue.empty():
            print("Kolejka jest pusta, kończenie pracy procesu...")
            break
        data = queue.get()

        # Przetwarzanie danych bez blokady
        day_readings_index = data.day
        day_mode_index = (Type[data.data_type] + data.day * len(Type)) * 21 + data.val

        # Aktualizacja lokalnych zmiennych
        local_day_readings[day_readings_index] = local_day_readings.get(day_readings_index, 0) + 1
        local_day_mode[day_mode_index] = local_day_mode.get(day_mode_index, 0) + 1

        result_count_index = Help[data.data_type + '_COUNT'] + data.day * len(Help)
        result_avg_index = Help[data.data_type + '_AVG'] + data.day * len(Help)

        local_result_count[result_count_index] = local_result_count.get(result_count_index, 0) + 1
        local_result_sum[result_avg_index] = local_result_sum.get(result_avg_index, 0) + data.val

        # Aktualizacja globalnych zmiennych w sekcji krytycznej
        with lock:
            if data.day not in days:
                days.append(data.day)  # Optymalizacja: unika blokady dla każdego odczytu

    # Kolejna sekcja krytyczna do zapisu wyników
    with lock:
        for day, count in local_day_readings.items():
            day_readings[day] += count

        for index, count in local_day_mode.items():
            day_mode[index] += count

        for index, count in local_result_count.items():
            result[index] += count

        for index, val_sum in local_result_sum.items():
            # Tu aktualizujemy tylko sumę, średnią obliczymy po zakończeniu wszystkich operacji
            result[index] += val_sum

    # Logika do obliczenia MODE i AVG pozostaje poza tą funkcją, może być zaimplementowana
    # na końcu, gdy wszystkie dane zostaną przetworzone.


# nie zmieniać
@app.post("/sensor-data", status_code=201)
async def create_sensor_data(sensor_data_entry: List[SensorDataEntry]):
    queue = multiprocessing.Queue()
    for el in sensor_data_entry:
        queue.put(el)
    logging.info('Processing')
    res = threading.Thread(target=function, args=(queue,), daemon=True)
    res.start()


@app.get("/hello")
async def say_hello():
    res = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/clients/handshake",
                        json={"ip_addr": CLIENT_IP, "port": CLIENT_PORT, "indeks": INDEKS})
    if (res.status_code == 201):
        return "Success"
    else:
        return f"Error occurred {res.text}"
