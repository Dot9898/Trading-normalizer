

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5


POLLING_INTERVAL = 0.5

HOUR = 3600
DAY = 86400

SHIFT = {'shift_hours': HOUR, 
         'shift_days': DAY}

TIMEZONES = {'server': None, 
             'local': datetime.now().astimezone().tzinfo, 
             'UTC': timezone.utc, 
             'NY': ZoneInfo('America/New_York'), 
             'Chile': ZoneInfo('America/Santiago'), 
             'France': ZoneInfo('Europe/Paris')}

TIMEZONE_LABEL = {'server': 'MT5 server', 
                  'local': 'local', 
                  'UTC': 'UTC', 
                  'NY': 'New York', 
                  'Chile': 'Chile', 
                  'France': 'France'}

BLACK = '#1f1f1f'
WHITE = '#E6E6E6'
RED = '#FF4D4D'
BLUE = '#3B82F6'
GREEN = '#4CAF50'

CHART_COLORS = {'fill': {'green_and_red': {'positive': GREEN, 'negative': RED}, 
                        'black_and_white': {'positive': WHITE, 'negative': BLACK}}, 
                'stroke': {'green_and_red': {'positive': GREEN, 'negative': RED}, 
                        'black_and_white': {'positive': WHITE, 'negative': WHITE}}, 
                'price_lines': {'bid': BLUE, 'ask': RED}}

CHART_AXIS_TIME_FORMAT = {mt5.TIMEFRAME_M1: '%H:%M', 
                          mt5.TIMEFRAME_M5: '%H:%M', 
                          mt5.TIMEFRAME_M15: '%H:%M', 
                          mt5.TIMEFRAME_H1: '%e %b %H:%M', 
                          mt5.TIMEFRAME_H4: '%e %b %H:%M', 
                          mt5.TIMEFRAME_D1: '%e %b', 
                          mt5.TIMEFRAME_W1: '%b %Y', 
                          mt5.TIMEFRAME_MN1: '%b %Y'}

BARS_PER_HOUR = {mt5.TIMEFRAME_M1: 60, 
                 mt5.TIMEFRAME_M5: 12, 
                 mt5.TIMEFRAME_M15: 4, 
                 mt5.TIMEFRAME_H1: 1, 
                 mt5.TIMEFRAME_H4: 1.0/4, 
                 mt5.TIMEFRAME_D1: 1.0/24, 
                 mt5.TIMEFRAME_W1: 1.0/(24 * 7), 
                 mt5.TIMEFRAME_MN1: 1.0/(24 * 30)}

SECONDS = {mt5.TIMEFRAME_M1: 60, 
           mt5.TIMEFRAME_M5: 300, 
           mt5.TIMEFRAME_M15: 900, 
           mt5.TIMEFRAME_H1: 3600, 
           mt5.TIMEFRAME_H4: 3600 * 4, 
           mt5.TIMEFRAME_D1: 3600 * 24, 
           mt5.TIMEFRAME_W1: 3600 * 24 * 7, 
           mt5.TIMEFRAME_MN1: 3600 * 24 * 30}











