import multiprocessing
import threading
from multiprocessing import Queue, Process, Array, Value
from queue import Empty
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

DATA_TYPES = {
    'HUM': 0,
    'TEMP': 1,
    'LIGHT': 2,
    'PRESS': 3,
    'PREC': 4
}

STATS = {
    '_COUNT': 0,
    '_MODE': 1,
    '_AVG': 2,
}

TYPES_NUM = len(DATA_TYPES)
STATS_NUM = len(STATS)
PARAMS_NUM = STATS_NUM + 21
PER_DAY_NUM = len(DATA_TYPES) * PARAMS_NUM

MAX_PROCESSED_DAYS = 200


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

INDEKS = 448700


def function(queue: Queue):
    result = Array('d', MAX_PROCESSED_DAYS * PER_DAY_NUM)
    days_num = Value('i', 0)

    number_of_wokers = 4
    workers = [Process(target=process, args=(queue, result, days_num)) for _ in range(0, number_of_wokers)]

    for w in workers:
        w.start()
    for w in workers:
        w.join()

    for day in range(0, days_num.value + 1):
        for type in DATA_TYPES:
            base_index = day * PER_DAY_NUM + DATA_TYPES[type] * PARAMS_NUM
            result[base_index + STATS['_AVG']] /= result[base_index + STATS['_COUNT']]
            max_count = 0
            max_value = 0
            for i in range(21):
                if max_count < result[base_index + STATS_NUM + i]:
                    max_count = result[base_index + STATS_NUM + i]
                    max_value = i
            result[base_index + STATS['_MODE']] = max_value

    final_result = []
    for dd in range(0, days_num.value + 1):
        day = {'day': dd,
               'HUM_COUNT': result[dd * PER_DAY_NUM + DATA_TYPES.get('HUM') * PARAMS_NUM + STATS.get('_COUNT')],
               'HUM_MODE': result[dd * PER_DAY_NUM + DATA_TYPES.get('HUM') * PARAMS_NUM + STATS.get('_MODE')],
               'HUM_AVG': result[dd * PER_DAY_NUM + DATA_TYPES.get('HUM') * PARAMS_NUM + STATS.get('_AVG')],
               'TEMP_COUNT': result[dd * PER_DAY_NUM + DATA_TYPES.get('TEMP') * PARAMS_NUM + STATS.get('_COUNT')],
               'TEMP_MODE': result[dd * PER_DAY_NUM + DATA_TYPES.get('TEMP') * PARAMS_NUM + STATS.get('_MODE')],
               'TEMP_AVG': result[dd * PER_DAY_NUM + DATA_TYPES.get('TEMP') * PARAMS_NUM + STATS.get('_AVG')],
               'LIGHT_COUNT': result[dd * PER_DAY_NUM + DATA_TYPES.get('LIGHT') * PARAMS_NUM + STATS.get('_COUNT')],
               'LIGHT_MODE': result[dd * PER_DAY_NUM + DATA_TYPES.get('LIGHT') * PARAMS_NUM + STATS.get('_MODE')],
               'LIGHT_AVG': result[dd * PER_DAY_NUM + DATA_TYPES.get('LIGHT') * PARAMS_NUM + STATS.get('_AVG')],
               'PRESS_COUNT': result[dd * PER_DAY_NUM + DATA_TYPES.get('PRESS') * PARAMS_NUM + STATS.get('_COUNT')],
               'PRESS_MODE': result[dd * PER_DAY_NUM + DATA_TYPES.get('PRESS') * PARAMS_NUM + STATS.get('_MODE')],
               'PRESS_AVG': result[dd * PER_DAY_NUM + DATA_TYPES.get('PRESS') * PARAMS_NUM + STATS.get('_AVG')],
               'PREC_COUNT': result[dd * PER_DAY_NUM + DATA_TYPES.get('PREC') * PARAMS_NUM + STATS.get('_COUNT')],
               'PREC_MODE': result[dd * PER_DAY_NUM + DATA_TYPES.get('PREC') * PARAMS_NUM + STATS.get('_MODE')],
               'PREC_AVG': result[dd * PER_DAY_NUM + DATA_TYPES.get('PREC') * PARAMS_NUM + STATS.get('_AVG')]}
        final_result.append(day)

    requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/results",
                  json={"ip_addr": CLIENT_IP, "port": CLIENT_PORT, "indeks": INDEKS, "aggregates": final_result})


def process(queue: Queue, result: Array, days_num: Value):
    while True:
        try:
            data = queue.get(timeout=0.0001)
        except Empty:
            break

        base_index = data.day * PER_DAY_NUM + DATA_TYPES[data.data_type] * PARAMS_NUM
        with result.get_lock():
            result[base_index + STATS['_COUNT']] += 1
        with result.get_lock():
            result[base_index + STATS['_AVG']] += data.val
        with result.get_lock():
            result[base_index + STATS_NUM + data.val] += 1

        with days_num.get_lock():
            if data.day > days_num.value:
                days_num.value = data.day

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
