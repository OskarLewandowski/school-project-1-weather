import multiprocessing
import threading

from fastapi import FastAPI, HTTPException
import logging
import requests
import concurrent.futures
import time

from app import utils as utils, constants as constants
from app.data_models import client_handshake, result

logging.basicConfig(handlers=[
    logging.FileHandler("app/logs/app.log"),
    logging.StreamHandler()
],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

client_whitelist = []

app = FastAPI()


@app.post("/clients/handshake", status_code=201)
async def handshake(client: client_handshake.ClientHandshake):
    if client in client_whitelist:
        raise HTTPException(
            status_code=409, detail="IP address is already registered")
    else:
        client_whitelist.append(client)

        utils.get_ts_data(client)
        logging.info(
            f"Registered {client.ip_addr} client successfully! # available clients: {len(client_whitelist)}")


@app.get("/clients")
async def get_clients():
    logging.debug(
        f"Found {len(client_whitelist)} clients. Available clients: {client_whitelist}")
    return {"clients": client_whitelist}


@app.get("/start")
def get_clients():
    a = threading.Thread(target=send_data)
    a.start()
    return {"sending"}


@app.post("/results")
def submit_result(result: result.Result):
    res = threading.Thread(target=function, args=(result,))
    res.start()


def function(result):
    current_time = time.time()
    res = utils.compare_results(current_time, result)
    logging.info(f"Successfully saved the result into {res}.txt file")

def send_data():
    if (len(client_whitelist) > 0):
        logging.info("Starting sending data")
        post_to_multiple_urls()
        logging.info("Finished sending data")
    else:
        logging.info("No clients registered")


def post_to_multiple_urls():
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for client in client_whitelist:
            payload_items = utils.get_data_to_post(client)
            future = executor.submit(
                post_to_url, f"http://{client.ip_addr}:{client.port}/sensor-data", client, payload_items)
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error: {e}")


def post_to_url(url, client, data):
    print(url)
    response = []
    for timestamp in data:
        days_diff = utils.get_days_diff(timestamp)
        for idx, data_point in enumerate(data[timestamp]):
            response.append({"val": data_point, "data_type": constants.DATA_TYPES[idx], "day": days_diff})

    tmp = time.time()
    utils.save_last_sent_time(f"{client.indeks}", tmp)
    send = requests.post(url, json=response, headers={'host': 'example.com'})
    time.sleep(0.05)



