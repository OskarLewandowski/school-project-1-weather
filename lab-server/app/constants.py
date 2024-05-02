DATA_TYPES = ['HUM', 'TEMP', 'LIGHT', 'PRESS', 'PREC']

AGGREGATES = ['HUM_COUNT',
              'HUM_MODE',
              'HUM_AVG',

              'TEMP_COUNT',
              'TEMP_MODE',
              'TEMP_AVG',

              'LIGHT_COUNT',
              'LIGHT_MODE',
              'LIGHT_AVG',

              'PRESS_COUNT',
              'PRESS_MODE',
              'PRESS_AVG',

              'PREC_COUNT',
              'PREC_MODE',
              'PREC_AVG']

START_DATE = '2022-01-01'

# START_DATE + DAY_SHIFT = END_DATE
DAY_SHIFT = 100

# REFRESH INTERVAL BETWEEN DATA POINTS, E.G. "2022-01-01 12:00:00", "2022-01-01 12:03:00"
REFRESH_INTERVAL = '5min'

