

from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5


#Parameters

POLLING_INTERVAL = 0.5
DATA_TABLE_UPDATE_INTERVAL = 5.0 ###########
MAX_BARS_IN_GRAPH = 1000
GRAPH_HEIGHT = 450
SHOW_ORDER_TYPES = True
WINDOW_WHEN_DATA_IS_CONSIDERED_LOCAL = 30

SHOWN_SYMBOLS = ['US500', 'BTCUSD']
SYMBOL_DATA = {'US500': {'ideal_ppb': 0.75, 
                         'margin_req': 0.005, 
                         'display': 'basis', 
                         'digits': 1, 
                         'power': 4},
                         
               'BTCUSD': {'ideal_ppb': None,
                          'margin_req': 0.05, 
                          'display': 'percent', 
                          'digits': 2, 
                          'power': 2}, 

               'ETHUSD': {'ideal_ppb': None,
                          'margin_req': 0.05, 
                          'display': 'percent', 
                          'digits': 2, 
                          'power': 2}}


#Groups

TIMEZONES = {'server': None, 
             'local': datetime.now().astimezone().tzinfo, 
             'UTC': timezone.utc, 
             'New York': ZoneInfo('America/New_York'), 
             'Chile': ZoneInfo('America/Santiago'), 
             'France': ZoneInfo('Europe/Paris')}
SHOWN_TIMEZONES = ['Chile', 'New York', 'server', 'France']
SCALES = ['absolute', 'normalized', 'logarithmic']
NORMALIZATION_BASES = ['first_bar', 'market_open', 'week_market_open', 'server_1:00', 'now']
SHOWN_TRADES_DATA_COLUMNS = ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Close reason', 'action_button_1', 'action_button_2']
SHOWN_ALERTS_DATA_COLUMNS = {'manual': ['Time', 'Status', 'Operation', 'Progress'], 
                             'conditional_trade': ['Time', 'Status', 'Operation'], 
                             'open': ['Time', 'Status', 'Operation', 'Progress', 'P/L'], 
                             'close': ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Close reason']}
SHOWN_ACTIONS_DATA_COLUMNS = {'modify': ['Status', 'Operation', 'Current entry', 'Current SL', 'Current TP'], 
                              'edit': ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Current SL', 'Current TP'], 
                              'erase': ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Close reason']}

INTERESTING_TIMES = ['now', 
                     'market_open', 
                     'market_close', 
                     'week_market_open', 
                     'New_York_day_start', 
                     'New_York_week_start', 
                     'server_1:00', 
                     'server_week_1:00']
SHIFT_UNITS = ['bars', 'hours', 'days', 'weeks', 'months']

RR = [(1, 1), (2, 3), (1, 2), (1, 3), 'custom']

TRADE_DATA_COLUMNS_TO_TYPES = {'status': 'string', 
                                'ticket': int, 
                                'symbol': 'string', 
                                'volume': 'Float64', 
                                'set_price': 'Float64', 
                                'direction': 'string', 
                                'order_type': 'string', 
                                'volume': 'Float64', 
                                'SL_abs': 'Float64', 
                                'TP_abs': 'Float64', 
                                'SL_bp': 'Float64', 
                                'TP_bp': 'Float64', 
                                'balance_at_set': 'Float64', 
                                'equity_at_set': 'Float64', 
                                'SL_acc_percent_at_set_(equity)': 'Float64', 
                                'TP_acc_percent_at_set_(equity)': 'Float64', 
                                
                                'open_server_time': 'Int64', 
                                'open_timestamp': 'Int64', 
                                'open_price': 'Float64', 
                                'balance_at_open': 'Float64', 
                                'equity_at_open': 'Float64', 
                                'SL_acc_percent_at_open_(equity)': 'Float64', 
                                'TP_acc_percent_at_open_(equity)': 'Float64', 
                                
                                'close_server_time': 'Int64', 
                                'close_timestamp': 'Int64', 
                                'close_reason': 'string', 
                                'close_price': 'Float64', 
                                'points_abs': 'Float64', 
                                'points_bp': 'Float64', 
                                'balance_at_close': 'Float64', 
                                'equity_at_close': 'Float64', 
                                'P/L_abs': 'Float64', 
                                'P/L_acc_percent_(equity)': 'Float64', 
                                'P/L_acc_percent_(balance)': 'Float64', 
                                'P/L_acc_percent_(estimate)': 'Float64', 
                                
                                'display': 'string', 
                                'is_shown': 'boolean'}


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

DATA_TABLE_DATE_FORMAT = '%e %b, %H:%M'

ALERT_REASON_TEXT = {'manual': 'Alert', 
                     'open': 'Position opened', 
                     'close': 'Position closed', 
                     'conditional_trade': 'Order set'}


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


#MT5 Codes

OUT_DEAL_REASONS = {mt5.DEAL_REASON_CLIENT: 'manual', 
                    mt5.DEAL_REASON_MOBILE: 'manual', 
                    mt5.DEAL_REASON_WEB: 'manual', 
                    mt5.DEAL_REASON_EXPERT: 'manual', 
                    mt5.DEAL_REASON_SL: 'SL', 
                    mt5.DEAL_REASON_TP: 'TP', 
                    mt5.DEAL_REASON_SO: 'stop_out'}

ERROR_CODE_TO_DETAILS = {10004: {'name': 'TRADE_RETCODE_REQUOTE',
                                'description': 'Requote'},
                        10006: {'name': 'TRADE_RETCODE_REJECT',
                                'description': 'Request rejected'},
                        10007: {'name': 'TRADE_RETCODE_CANCEL',
                                'description': 'Request canceled by trader'},
                        10008: {'name': 'TRADE_RETCODE_PLACED',
                                'description': 'Order placed'},
                        10009: {'name': 'TRADE_RETCODE_DONE',
                                'description': 'Request completed'},
                        10010: {'name': 'TRADE_RETCODE_DONE_PARTIAL',
                                'description': 'Only part of the request was completed'},
                        10011: {'name': 'TRADE_RETCODE_ERROR',
                                'description': 'Request processing error'},
                        10012: {'name': 'TRADE_RETCODE_TIMEOUT',
                                'description': 'Request canceled by timeout'},
                        10013: {'name': 'TRADE_RETCODE_INVALID',
                                'description': 'Invalid request'},
                        10014: {'name': 'TRADE_RETCODE_INVALID_VOLUME',
                                'description': 'Invalid volume in the request'},
                        10015: {'name': 'TRADE_RETCODE_INVALID_PRICE',
                                'description': 'Invalid price in the request'},
                        10016: {'name': 'TRADE_RETCODE_INVALID_STOPS',
                                'description': 'Invalid stops in the request'},
                        10017: {'name': 'TRADE_RETCODE_TRADE_DISABLED',
                                'description': 'Trade is disabled'},
                        10018: {'name': 'TRADE_RETCODE_MARKET_CLOSED',
                                'description': 'Market is closed'},
                        10019: {'name': 'TRADE_RETCODE_NO_MONEY',
                                'description': 'There is not enough money to complete the request'},
                        10020: {'name': 'TRADE_RETCODE_PRICE_CHANGED',
                                'description': 'Prices changed'},
                        10021: {'name': 'TRADE_RETCODE_PRICE_OFF',
                                'description': 'There are no quotes to process the request'},
                        10022: {'name': 'TRADE_RETCODE_INVALID_EXPIRATION',
                                'description': 'Invalid order expiration date in the request'},
                        10023: {'name': 'TRADE_RETCODE_ORDER_CHANGED',
                                'description': 'Order state changed'},
                        10024: {'name': 'TRADE_RETCODE_TOO_MANY_REQUESTS',
                                'description': 'Too frequent requests'},
                        10025: {'name': 'TRADE_RETCODE_NO_CHANGES',
                                'description': 'No changes in request'},
                        10026: {'name': 'TRADE_RETCODE_SERVER_DISABLES_AT',
                                'description': 'Autotrading disabled by server'},
                        10027: {'name': 'TRADE_RETCODE_CLIENT_DISABLES_AT',
                                'description': 'Autotrading disabled by client terminal'},
                        10028: {'name': 'TRADE_RETCODE_LOCKED',
                                'description': 'Request locked for processing'},
                        10029: {'name': 'TRADE_RETCODE_FROZEN',
                                'description': 'Order or position frozen'},
                        10030: {'name': 'TRADE_RETCODE_INVALID_FILL',
                                'description': 'Invalid order filling type'},
                        10031: {'name': 'TRADE_RETCODE_CONNECTION',
                                'description': 'No connection with the trade server'},
                        10032: {'name': 'TRADE_RETCODE_ONLY_REAL',
                                'description': 'Operation is allowed only for live accounts'},
                        10033: {'name': 'TRADE_RETCODE_LIMIT_ORDERS',
                                'description': 'The number of pending orders has reached the limit'},
                        10034: {'name': 'TRADE_RETCODE_LIMIT_VOLUME',
                                'description': 'The volume of orders and positions for the symbol has reached the limit'},
                        10035: {'name': 'TRADE_RETCODE_INVALID_ORDER',
                                'description': 'Incorrect or prohibited order type'},
                        10036: {'name': 'TRADE_RETCODE_POSITION_CLOSED',
                                'description': 'Position with the specified POSITION_IDENTIFIER has already been closed'},
                        10038: {'name': 'TRADE_RETCODE_INVALID_CLOSE_VOLUME',
                                'description': 'A close volume exceeds the current position volume'},
                        10039: {'name': 'TRADE_RETCODE_CLOSE_ORDER_EXIST',
                                'description': 'A close order already exists for a specified position'},
                        10040: {'name': 'TRADE_RETCODE_LIMIT_POSITIONS',
                                'description': 'The number of open positions simultaneously present on an account has reached the limit'},
                        10041: {'name': 'TRADE_RETCODE_REJECT_CANCEL',
                                'description': 'The pending order activation request is rejected, the order is canceled'},
                        10042: {'name': 'TRADE_RETCODE_LONG_ONLY',
                                'description': 'The request is rejected because only long positions are allowed for the symbol'},
                        10043: {'name': 'TRADE_RETCODE_SHORT_ONLY',
                                'description': 'The request is rejected because only short positions are allowed for the symbol'},
                        10044: {'name': 'TRADE_RETCODE_CLOSE_ONLY',
                                'description': 'The request is rejected because only position closing is allowed for the symbol'},
                        10045: {'name': 'TRADE_RETCODE_FIFO_CLOSE',
                                'description': 'The request is rejected because position closing is allowed only by FIFO rule'},
                        10046: {'name': 'TRADE_RETCODE_HEDGE_PROHIBITED',
                                'description': 'The request is rejected because opposite positions on a single symbol are disabled'}
}


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
                       'custom_y_range': False}

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
                                            'year': 'months'}, 
                        
                        'selected_normalization_base_name': {'hour': 'market_open', #Overwritten in callback
                                                            'now': 'market_open', #Overwritten in callback
                                                            'day': 'market_open', 
                                                            'week': 'first_bar', 
                                                            'month': 'first_bar', 
                                                            'year': 'first_bar'}}


#Others

ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_PATH / 'data'

NORMALIZATION_PRECISION = 5
DEFAULTS = {'ideal_ppb': None, 
            'display': 'basis', 
            'digits': 1, 
            'power': 4}

EMPTY_SPACE = '\u200b'
EMPTY_SPACE_2 = '\u200c'
LABEL_SPACING = 28









