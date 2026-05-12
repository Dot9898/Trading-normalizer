

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5


#Parameters

POLLING_INTERVAL = 0.5
MAX_BARS_IN_GRAPH = 1000
GRAPH_HEIGHT = 450

NORMALIZATION_DATA = {'US500': {'display': 'basis', 'digits': 1, 'power': 4},    #The ideal values are dependent on average range
                      'BTCUSD': {'display': 'percent', 'digits': 2, 'power': 2}}


#Groups

TIMEZONES = {'server': None, 
             'local': datetime.now().astimezone().tzinfo, 
             'UTC': timezone.utc, 
             'New York': ZoneInfo('America/New_York'), 
             'Chile': ZoneInfo('America/Santiago'), 
             'France': ZoneInfo('Europe/Paris')}
SHOWN_TIMEZONES = ['Chile', 'New York', 'server', 'France', 'server']
SCALES = ['absolute', 'normalized', 'logarithmic']
NORMALIZATION_BASES = ['first_bar', 'market_open', 'week_market_open', 'now']

INTERESTING_TIMES = ['now', 
                     'market_open', 
                     'market_close', 
                     'week_market_open', 
                     'New_York_day_start', 
                     'New_York_week_start', 
                     'server_1:00', 
                     'server_week_1:00']
SHIFT_UNITS = ['bars', 'hours', 'days', 'weeks', 'months']

RR = [(1, 1), (2, 3), (1, 2), (1, 3), None]


#Labels

TIMEFRAME_LABEL = {mt5.TIMEFRAME_M1: '1 Minute', 
                   mt5.TIMEFRAME_M5: '5 Minutes', 
                   mt5.TIMEFRAME_M15: '15 Minutes', 
                   mt5.TIMEFRAME_H1: '1 Hour', 
                   mt5.TIMEFRAME_H4: '4 Hours', 
                   mt5.TIMEFRAME_D1: 'Daily', 
                   mt5.TIMEFRAME_W1: 'Weekly', 
                   mt5.TIMEFRAME_MN1: 'Monthly'}

CHART_AXIS_TIME_FORMAT = {mt5.TIMEFRAME_M1: '%H:%M', 
                          mt5.TIMEFRAME_M5: '%H:%M', 
                          mt5.TIMEFRAME_M15: '%H:%M', 
                          mt5.TIMEFRAME_H1: '%e %b %H:%M', 
                          mt5.TIMEFRAME_H4: '%e %b %H:%M', 
                          mt5.TIMEFRAME_D1: '%e %b', 
                          mt5.TIMEFRAME_W1: '%b %Y', 
                          mt5.TIMEFRAME_MN1: '%b %Y'}

REMAINING_CANDLE_TIME_FORMAT = {mt5.TIMEFRAME_M1: '%M:%S', 
                                mt5.TIMEFRAME_M5: '%M:%S', 
                                mt5.TIMEFRAME_M15: '%M:%S', 
                                mt5.TIMEFRAME_H1: '%M:%S', 
                                mt5.TIMEFRAME_H4: '%H:%M:%S', 
                                mt5.TIMEFRAME_D1: '%H:%M:%S', 
                                mt5.TIMEFRAME_W1: '%ed, %Hh', 
                                mt5.TIMEFRAME_MN1: '%ed, %Hh'}


#Colors

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


#Time

HOUR = 3600
DAY = 3600 * 24
WEEK = 3600 * 24 * 7
MONTH = 3600 * 24 * 30

OFFSET_SECONDS = {'hours': HOUR, 
                  'days': DAY, 
                  'weeks': WEEK, 
                  'months': MONTH}

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


#Zoom settings

ZOOM_FIXED_SETTINGS = {'first_bar': 'now', 
                       'last_bar': 'now', 
                       'right_shift': 0, 
                       'extra_shift': 0, 
                       'custom_y_range': False, 
                       'selected_normalization_base_name': 'first_bar'}

ZOOM_VARIABLE_SETTINGS = {'selected_timeframe': {'hour': mt5.TIMEFRAME_M1, 
                                                'now': mt5.TIMEFRAME_M5, 
                                                'day': mt5.TIMEFRAME_M5, 
                                                'week': mt5.TIMEFRAME_H1, 
                                                'month': mt5.TIMEFRAME_H1, 
                                                'year': mt5.TIMEFRAME_D1}, 

                        'left_shift': {'hour': -1.5, 
                                    'now': -8, 
                                    'day': -1, 
                                    'week': -1, 
                                    'month': -1, 
                                    'year': -12}, 

                        'left_shift_unit': {'hour': 'hours', 
                                            'now': 'hours', 
                                            'day': 'days', 
                                            'week': 'weeks', 
                                            'month': 'months', 
                                            'year': 'months'}, 

                        'right_shift_unit': {'hour': 'hours', 
                                            'now': 'hours', 
                                            'day': 'days', 
                                            'week': 'weeks', 
                                            'month': 'months', 
                                            'year': 'months'}, 
                        
                        'extra_shift_unit': {'hour': 'bars', 
                                            'now': 'hours', 
                                            'day': 'hours', 
                                            'week': 'days', 
                                            'month': 'weeks', 
                                            'year': 'months'}}


#Others

NORMALIZATION_PRECISION = 5
DEFAULTS = {'display': 'percent', 'digits': 2, 'power': 2}

EMPTY_SPACE = '\u200b'
EMPTY_SPACE_2 = '\u200c'
LABEL_SPACING = 28









