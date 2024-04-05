import numpy as np
import pandas as pd
import scipy.stats
import random as random
from datetime import datetime, timedelta
from collections import OrderedDict
import logging

import app.constants as constants


def get_data_to_post(client):
    df = pd.read_csv(f"app/payloads/{client.indeks}.csv",
                     sep='\t', encoding='utf-8', engine='python', index_col=[0])
    values = df.to_numpy()

    keys = df.index.tolist()

    payload = dict(zip(keys, values))
    payload_items = list(payload.items())
    random.shuffle(payload_items)

    return OrderedDict(payload_items)


def get_ts_data(client):
    #np.random.seed(2022)
    end_date = get_end_date(constants.DAY_SHIFT)
    range = pd.date_range(start=constants.START_DATE,
                          end=end_date, freq=constants.REFRESH_INTERVAL)

    df = pd.DataFrame(np.random.rand(
        len(range), len(constants.DATA_TYPES)).round(5)*20, columns=constants.DATA_TYPES, index=range)
    df = df.round(0)
    #print(df)
    df_aggregates = df.groupby(df.index.date).agg(
        HUM_COUNT=('HUM', 'count'),
        HUM_MODE=('HUM', lambda x: scipy.stats.mode(x)[0]),
        HUM_AVG=('HUM', 'mean'),

        TEMP_COUNT=('TEMP', 'count'),
        TEMP_MODE=('TEMP', lambda x: scipy.stats.mode(x)[0]),
        TEMP_AVG=('TEMP', 'mean'),

        LIGHT_COUNT=('LIGHT', 'count'),
        LIGHT_MODE=('LIGHT', lambda x: scipy.stats.mode(x)[0]),
        LIGHT_AVG=('LIGHT', 'mean'),

        PRESS_COUNT=('PRESS', 'count'),
        PRESS_MODE=('PRESS', lambda x: scipy.stats.mode(x)[0]),
        PRESS_AVG=('PRESS', 'mean'),

        PREC_COUNT=('PREC', 'count'),
        PREC_MODE=('PREC', lambda x: scipy.stats.mode(x)[0]),
        PREC_AVG=('PREC', 'mean'),

    )

    df_aggregates['days_diff'] = [get_days_diff(
        day) for day in list(df_aggregates.index)]

    df.to_csv(f"app/payloads/{client.indeks}.csv",
              sep='\t', encoding='utf-8')
    df_aggregates.to_csv(
        f"app/payloads/{client.indeks}_aggregates.csv", sep='\t', encoding='utf-8')

    logging.info(
        f"Successfully generated {len(range)} data points for {client}")


def compare_results(client_time, result):
    file_name = f"{result.indeks}"
    last_sent_time = get_last_sent_time(file_name)

    f = open(f"app/results/{file_name}.txt", "w")

    diff = client_time - float(last_sent_time)

    df = pd.read_csv(f"app/payloads/{result.indeks}_aggregates.csv",
                     sep='\t', encoding='utf-8', engine='python', index_col=[0])

    f.write(
        f"Last data point was sent at {last_sent_time}, got client response at {client_time}, diff: {diff}s")
    f.write("\n")
    f.write(f"# days for which data aggregates were generated: {len(df)}")
    f.write("\n")
    f.write(f"# days received from client: {len(result.aggregates)}")
    f.write("\n\nComparing aggregates:\n")

    ile = 0
    all = 0

    for day in result.aggregates:
        day_server = df.iloc[day.day]
        for aggregate in constants.AGGREGATES:
            client_value = getattr(day, aggregate)
            server_value = getattr(day_server, aggregate)
            if abs(client_value - server_value) < 0.01:
                ile += 1
            all += 1
            f.write(
                f'{aggregate}: {client_value} == {server_value} ({abs(client_value - server_value) < 0.01})')
            f.write("\n")
    f.write(f'Summary : {ile}/{all}')
    f.close()
    return file_name


def save_last_sent_time(file_name, results):
    f = open(f"app/results/{file_name}.txt", "w")
    f.write(str(results))
    f.close()


def get_last_sent_time(file_name):
    f = open(f"app/results/{file_name}.txt", "r")
    res = f.read()
    f.close()
    return res


def get_end_date(day_shift):
    return datetime.strftime(datetime.strptime(constants.START_DATE, '%Y-%m-%d') + timedelta(days=day_shift), '%Y-%m-%d')


def get_days_diff(timestamp):
    if (isinstance(timestamp, str)):
        return (datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S') - datetime.strptime(constants.START_DATE, '%Y-%m-%d')).days
    return (timestamp - datetime.strptime(constants.START_DATE, '%Y-%m-%d').date()).days
