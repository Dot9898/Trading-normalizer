

from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5


#Parameters
POLLING_INTERVAL = 1.0
TRADES_UPDATE_INTERVAL = 5.0
WINDOW_WHEN_DATA_IS_CONSIDERED_LOCAL = 30


#To remove

GRAPH_EMPTY_SPACE_FRACTION = 0.15 #also setting to add space when going back
TOTAL_WIDTH = 16
MIN_GRAPH_WIDTH = 4  #poner min y max normales desde 4 hasta 12 o similar en el slider y eliminar estas constantes y las de abajo
#Add green and red theme (or just different themes)
MIN_LEFT_WIDTH = MIN_GRAPH_WIDTH - 1
MIN_RIGHT_WIDTH = TOTAL_WIDTH - (MIN_GRAPH_WIDTH - 1)

SHOW_ORDER_TYPES = True #make it a setting

DEFAULTS = {'ideal_ppb': None, #move this to symbol data
            'display': 'basis', 
            'digits': 1, 
            'power': 4}




#Dynamic defaults
SHOWN_SYMBOLS = ['US500', 'BTCUSD', 'ETHUSD']
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
RR = [(1, 1), (2, 3), (1, 2), (1, 3), 'custom']
SHOWN_TIMEZONES = ['Chile', 'New York', 'server', 'France']
SESSION_STATE_DEFAULTS = {'data_table': None, 
                          'update_data_table': True, 
                          'alerts_pending_notification': [], 
                          'orders_to_delete': set(), 
                          'dialog_open': False, 
                          'bars_data': None, 
                          'reload_Bars': True, 
                          'reload_table': True, 
                          'update_maxes': True, 
                          'selected_timezone': 'New York', 
                          'selected_symbol': 'US500', 
                          'selected_scale': 'normalized', 
                          'maxloss': -10.0, 
                          'RR': (1, 2), 
                          'custom_y_range': False, 
                          'risk': 0, 
                          'reward': 0, 
                          'dialog_data': None, 
                          'update_SLTP': False, 
                          'update_graph_lines': True}

#Fixed defaults
TIMEZONES = {'server': None, 
             'local': datetime.now().astimezone().tzinfo, 
             'UTC': timezone.utc, 
             'New York': ZoneInfo('America/New_York'), 
             'Chile': ZoneInfo('America/Santiago'), 
             'France': ZoneInfo('Europe/Paris')}
SCALES = ['absolute', 'normalized', 'logarithmic']
NORMALIZATION_BASES = ['first_bar', 'market_open', 'week_market_open', 'server_1:00', 'now']
INTERESTING_TIMES = ['now', 
                     'market_open', 
                     'market_close', 
                     'week_market_open', 
                     'New_York_day_start', 
                     'New_York_week_start', 
                     'server_1:00', 
                     'server_week_1:00']
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

#Trades data and table defaults
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
SHOWN_TRADES_DATA_COLUMNS = ['Time', 
                             'Status', 
                             'Operation', 
                             'Progress', 
                             'P/L', 
                             'Close reason', 
                             'action_button_1', 
                             'action_button_2']
SHOWN_ALERTS_DATA_COLUMNS = {'manual': ['Time', 'Status', 'Operation', 'Progress'], 
                             'conditional_trade': ['Time', 'Status', 'Operation'], 
                             'open': ['Time', 'Status', 'Operation', 'Progress', 'P/L'], 
                             'close': ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Close reason']}
SHOWN_ACTIONS_DATA_COLUMNS = {'modify': ['Status', 'Operation', 'Current entry', 'Current SL', 'Current TP'], 
                              'edit': ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Current SL', 'Current TP'], 
                              'erase': ['Time', 'Status', 'Operation', 'Progress', 'P/L', 'Close reason']}
DATA_TABLE_HEIGHT = 452

#Colors #make this a single constant
BLACK = '#1f1f1f'
WHITE = '#E6E6E6'
RED = '#FF4D4D'
BLUE = '#3B82F6'
GREEN = '#4CAF50'

#Chart ##
CHART_PARAMETERS = {'?'} #
MAX_BARS_IN_GRAPH = 1000

CHART_COLORS = {'candlesticks': {'fill_positive': WHITE, 
                                 'fill_negative': BLACK, 
                                 'stroke_positive': WHITE, 
                                 'stroke_negative': WHITE}, 

                'lines': {'bid': BLUE, 
                          'ask': RED, 
                          'SL': RED, 
                          'TP': GREEN, 
                          'entry': GREEN, 
                          'alert_price': GREEN, 
                          'open_SL': RED, 
                          'open_TP': GREEN, 
                          'pending_entry': GREEN, 
                          'pending_SL': GREEN, 
                          'pending_TP': GREEN, 
                          'placed_alert': GREEN, 
                          'conditonal_trade_trigger': GREEN}}
CHART_OPACITY = {'lines': {'bid': 1.0, 
                           'ask': 1.0, 
                           'SL': 1.0, 
                           'TP': 1.0, 
                           'entry': 0.8, 
                           'alert_price': 1.0, #?
                           'open_SL': 0.8, 
                           'open_TP': 0.8, 
                           'pending_entry': 0.6, 
                           'pending_SL': 0.6,  
                           'pending_TP': 0.6, 
                           'placed_alert': 1.0, 
                           'conditonal_trade_trigger': 0.4}}
CHART_PIXELS = {'height': 550, 
                'line_labels_font_size_big': 15, 
                'line_labels_font_size': 13, 
                'line_labels_dx': -4, 
                'line_labels_dy': -3, 
                'title_offset': 5}
CHART_OTHER_VALUES = {'candlesticks_inner_padding': 0.35, 
                      'candlesticks_outer_padding': 0.5, 
                      'x_labels_angle': 0}
CHART_STYLE = {'colors': CHART_COLORS, 
               'opacity': CHART_OPACITY, 
               'pixels': CHART_PIXELS, 
               'others': CHART_OTHER_VALUES}

#Formatted labels
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

#MT5 codes
OUT_DEAL_REASONS = {mt5.DEAL_REASON_CLIENT: 'manual', 
                    mt5.DEAL_REASON_MOBILE: 'manual', 
                    mt5.DEAL_REASON_WEB: 'manual', 
                    mt5.DEAL_REASON_EXPERT: 'manual', 
                    mt5.DEAL_REASON_SL: 'SL', 
                    mt5.DEAL_REASON_TP: 'TP', 
                    mt5.DEAL_REASON_SO: 'stop_out'}
ERROR_CODE_TO_DETAILS = {None: {'name': 'UNKNOWN', 
                                'description': 'Unknown error'}, 
                        10004: {'name': 'TRADE_RETCODE_REQUOTE',
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
SECONDS = {mt5.TIMEFRAME_M1: 60, 
           mt5.TIMEFRAME_M5: 300, 
           mt5.TIMEFRAME_M15: 900, 
           mt5.TIMEFRAME_H1: 3600, 
           mt5.TIMEFRAME_H4: 3600 * 4, 
           mt5.TIMEFRAME_D1: 3600 * 24, 
           mt5.TIMEFRAME_W1: 3600 * 24 * 7, 
           mt5.TIMEFRAME_MN1: 3600 * 24 * 30}
SHIFT_UNITS = ['bars', 'hours', 'days', 'weeks', 'months']
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

#Graphic constants
LABEL_SPACING = 28
WHITE_SPACE = ' '
LARGER_WHITE_SPACE = ' '
EMPTY_SPACE = '\u200b'
EMPTY_SPACE_2 = '\u200c'
EMPTY_SPACE_3 = '\u200d'

#Paths
ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_PATH / 'data'



