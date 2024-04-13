import multiprocessing
import threading
from multiprocessing import Queue

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

INDEKS = 12

def function(queue : Queue):
    global result
    result = [0] * 500000 # w przypadku duzej liczby danych powinno być zwiększane!
    global day_readings
    day_readings = [0] * 500
    global day_mode
    day_mode = [0] * 21 * 500

    global days
    days = set()

    DATA_TYPES = ['HUM', 'TEMP', 'LIGHT', 'PRESS', 'PREC']

    number_of_wokers = 1

    workers = [threading.Thread(target=process, args=(queue, )) for i in range(0,number_of_wokers)] # w docelowym rozwiązaniu musisz zastosować multiprocessing.Process

    for w in workers:
        w.start()

    for w in workers:
        w.join()

    wynik = []
    
    for dzien in range(0, len(days)):
        for type in DATA_TYPES:
            result[Help.get(type + '_AVG') + dzien * len(Help)] /= (float(day_readings[dzien]) / float(len(DATA_TYPES)))
            maksimal = 0
            wy = 0
            for i in range(21):
                if maksimal <  day_mode[(Type.get(type) + dzien*len(Type))*21 +i]: 
                    maksimal = day_mode[(Type.get(type) + dzien*len(Type))*21 +i]
                    wy = i
            result[Help.get(type + '_MODE') + dzien*len(Help)] = wy

    # wypisanie wyniku w formie w której serwer jej oczekuje
    # process zapisuje dane w tabeli pod indeksami po 20 indeksów na dzień w kolejności jak poniżej
    # ponieważ tak jest najbardziej wydajnie
    for dd in range(0, len(days)):
        dzien = {'day': dd,
                 'HUM_COUNT': result[dd*len(Help) + Help.get('HUM_COUNT')],
                 'HUM_MODE': result[dd*len(Help) + Help.get('HUM_MODE')],
                 'HUM_AVG': result[dd*len(Help) + Help.get('HUM_AVG')],
                 'TEMP_COUNT': result[dd*len(Help) + Help.get('TEMP_COUNT')],
                 'TEMP_MODE': result[dd*len(Help) + Help.get('TEMP_MODE')],
                 'TEMP_AVG': result[dd*len(Help) + Help.get('TEMP_AVG')],
                 'LIGHT_COUNT': result[dd*len(Help) + Help.get('LIGHT_COUNT')],
                 'LIGHT_MODE': result[dd*len(Help) + Help.get('LIGHT_MODE')],
                 'LIGHT_AVG': result[dd*len(Help) + Help.get('LIGHT_AVG')],
                 'PRESS_COUNT': result[dd*len(Help) + Help.get('PRESS_COUNT')],
                 'PRESS_MODE': result[dd*len(Help) + Help.get('PRESS_MODE')],
                 'PRESS_AVG': result[dd*len(Help) + Help.get('PRESS_AVG')],
                 'PREC_COUNT': result[dd*len(Help) + Help.get('PREC_COUNT')],
                 'PREC_MODE': result[dd*len(Help) + Help.get('PREC_MODE')],
                 'PREC_AVG': result[dd*len(Help) + Help.get('PREC_AVG')]}
        wynik.append(dzien)

    requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/results",
                  json={"ip_addr": CLIENT_IP, "port": CLIENT_PORT, "indeks": INDEKS, "aggregates": wynik})


def process(queue: Queue):
    while True:
        global days
        global result
        global day_readings
        global day_mode

        #logging.info(f'{dataCounter.value} + {multiprocessing.current_process()}')
        # każdy wątek pobiera z kolejki aż skończą się dane
        if queue.empty():
            break
        data = queue.get()

        day_readings[data.day] = day_readings[data.day] + 1
        day_mode[(Type.get(data.data_type) + data.day*len(Type))*21 + data.val] +=1

        if data.day not in days:
            days.add(data.day)

        result[Help.get(data.data_type + '_COUNT') + data.day*len(Help)] += 1
        #print(data.data_type + ' ' + str(data.day) + ' '  + str(data.val))
        result[Help.get(data.data_type + '_AVG') + data.day * len(Help)] += data.val

    return result

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
