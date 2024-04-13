import multiprocessing
import threading
from multiprocessing import Queue, Process, Array, Value, Lock
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
    lock = Lock()

    # Określamy długość Array
    result_length = 500000
    day_readings_length = 500000
    day_mode_length = 21 * 500

    daysCount = Value('i', 0)

    result = Array('d', result_length)
    day_readings = Array('i', day_readings_length)
    day_mode = Array('i', day_mode_length)

    number_of_workers = 4

    # Tworzymy procesy
    workers = [Process(target=process, args=(queue, result, day_readings, day_mode, daysCount, lock)) for _ in
               range(number_of_workers)]

    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    wynik = []

    for dzien in range(0, daysCount.value):
        for type in DATA_TYPES:
            result[Help.get(type + '_AVG') + dzien * 15] /= (float(day_readings[dzien]) / 5.0)
            maksimal = 0
            wy = 0
            for i in range(21):
                if maksimal < day_mode[(Type.get(type) + dzien * 5) * 21 + i]:
                    maksimal = day_mode[(Type.get(type) + dzien * 5) * 21 + i]
                    wy = i
            result[Help.get(type + '_MODE') + dzien * 15] = wy

    # wypisanie wyniku w formie w której serwer jej oczekuje
    # process zapisuje dane w tabeli pod indeksami po 20 indeksów na dzień w kolejności jak poniżej
    for dd in range(0, daysCount.value):
        dzien = {'day': dd,
                 'HUM_COUNT': result[dd * 15 + 0],
                 'HUM_MODE': result[dd * 15 + 1],
                 'HUM_AVG': result[dd * 15 + 2],
                 'TEMP_COUNT': result[dd * 15 + 3],
                 'TEMP_MODE': result[dd * 15 + 4],
                 'TEMP_AVG': result[dd * 15 + 5],
                 'LIGHT_COUNT': result[dd * 15 + 6],
                 'LIGHT_MODE': result[dd * 15 + 7],
                 'LIGHT_AVG': result[dd * 15 + 8],
                 'PRESS_COUNT': result[dd * 15 + 9],
                 'PRESS_MODE': result[dd * 15 + 10],
                 'PRESS_AVG': result[dd * 15 + 11],
                 'PREC_COUNT': result[dd * 15 + 12],
                 'PREC_MODE': result[dd * 15 + 13],
                 'PREC_AVG': result[dd * 15 + 14]}
        wynik.append(dzien)

    # to zostaje bez zmian
    requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/results",
                  json={"ip_addr": CLIENT_IP, "port": CLIENT_PORT, "indeks": INDEKS, "aggregates": wynik})


def process(queue: Queue, result, day_readings, day_mode, daysCount, lock: Lock):
    while True:
        if queue.empty():
            # print("Kolejka jest pusta, kończenie pracy procesu...")
            break
        data = queue.get()
        # print(data)

        day = data.day
        value = data.val

        mode_index = (Type[data.data_type] + day * 5) * 21 + value
        count_index = Help[data.data_type + '_COUNT'] + day * 15
        avg_index = Help[data.data_type + '_AVG'] + day * 15

        with lock:
            day_readings[day] += 1
            day_mode[mode_index] += 1

            if day >= daysCount.value:
                daysCount.value = day + 1

            result[count_index] += 1
            result[avg_index] += value


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
