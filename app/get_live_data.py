

import pandas as pd
from datetime import datetime, timedelta
from numpy import log10
from time import time
import MetaTrader5 as mt5
from constants import SECONDS, TIMEZONES, CHART_AXIS_TIME_FORMAT, HOUR, DAY, WEEK, OFFSET_SECONDS, EMPTY_SPACE, EMPTY_SPACE_2, MAX_BARS_IN_GRAPH, NORMALIZATION_PRECISION, NORMALIZATION_DATA, DEFAULTS, REMAINING_CANDLE_TIME_FORMAT


class Graph_range:
    
    def __init__(self, first_bar, left_shift, left_shift_unit, last_bar, right_shift, right_shift_unit, extra_shift, extra_shift_unit):
        self.first_bar = first_bar
        self.last_bar = last_bar
        self.left_shift = left_shift
        self.left_shift_unit = left_shift_unit
        self.right_shift = right_shift
        self.right_shift_unit = right_shift_unit
        self.extra_shift = extra_shift
        self.extra_shift_unit = extra_shift_unit

        self.first_bar_time = None
        self.last_bar_time = None
    
    @staticmethod
    def get_offset(shift, unit, timeframe):
        if unit == 'bars':
            offset = shift * SECONDS[timeframe]
        else:
            offset = shift * OFFSET_SECONDS[unit]
        offset = int(round(offset))
        return(offset)

    def set_first_and_last_bar_time(self, fixed_times, timeframe):

        first_base = fixed_times[self.first_bar]
        last_base = fixed_times[self.last_bar]
        first_offset = self.get_offset(self.left_shift, self.left_shift_unit, timeframe)
        last_offset = self.get_offset(self.right_shift, self.right_shift_unit, timeframe) 
        extra_offset = self.get_offset(self.extra_shift, self.extra_shift_unit, timeframe)

        first_time = first_base + first_offset + extra_offset
        last_time = last_base + last_offset + extra_offset

        if first_time < last_time:
            self.first_bar_time = first_time
            self.last_bar_time = last_time
        else:
            self.first_bar_time = None
            self.last_bar_time = None

class Bars:

    def __init__(self, symbol, timeframe, graph_range: Graph_range, timezone, data_scale, normalization_base_name = None):
        
        #Data set by the user
        self.symbol = symbol
        self.timeframe = timeframe
        self.graph_range = graph_range
        self.timezone = timezone
        self.data_scale = data_scale
        self.normalization_base_name = normalization_base_name

        self.is_connected = self.initialize_MetaTrader()

        #Fixed data
        self.name = mt5.symbol_info(self.symbol).description
        self.digits = mt5.symbol_info(self.symbol).digits
        self.shown_digits = self.get_shown_digits()
        self.normalization_factor = self.get_normalization_factor()
        #self.spread = round(mt5.symbol_info(self.symbol).spread / (10 ** self.digits), self.digits) #absolute

        #Data updated on full update, when a new bar appears
        self.first_bar_time = None
        self.last_bar_time = None
        self.shows_current_bar = None
        self.normalization_base = None
        self.server_times_of_interest = None
        self.last_current_bar_open_time = None
        self.bars = None
        self.max_price = None
        self.min_price = None
        self.date_label = None

        #Data updated on soft update, every tick
        self.current_server_time = None
        self.current_bar = None
        self.current_bar_open_time = None
        self.current_candle_time = None
        self.remaining_candle_time = None
        self.current_bid = None
        self.current_ask = None
        self.too_many_bars = False

        self.full_update()

    def initialize_MetaTrader(self):
        return(mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe'))

    def update_server_times_of_interest(self):
        server_time_of = {}
        current_server_time = self.current_server_time

        server_day_start = current_server_time - current_server_time % DAY
        NY_day_start = server_day_start + 7 * HOUR
        server_week_start = current_server_time - current_server_time % WEEK + 4 * DAY
        NY_week_start = server_week_start + 7 * HOUR

        server_time_of['market_open'] = NY_day_start + int(9.5 * HOUR)
        server_time_of['market_close'] = NY_day_start + 16 * HOUR
        server_time_of['server_1:00'] = server_day_start + 1 * HOUR
        server_time_of['New_York_day_start'] = NY_day_start

        for key in ['market_open', 'market_close', 'server_1:00', 'New_York_day_start']:
            if server_time_of[key] > current_server_time:
                server_time_of[key] = server_time_of[key] - DAY
        
        server_time_of['week_market_open'] = NY_week_start + int(9.5 * HOUR)
        server_time_of['server_week_1:00'] = server_week_start + 1 * HOUR
        server_time_of['New_York_week_start'] = NY_week_start

        for key in ['week_market_open', 'server_week_1:00', 'New_York_week_start']:
            if server_time_of[key] > current_server_time:
                server_time_of[key] = server_time_of[key] - WEEK
        
        server_time_of['now'] = current_server_time

        self.server_times_of_interest = server_time_of

    def set_normalization_base(self):
        if self.normalization_base_name is None:
            self.normalization_base = None
            return
        
        elif self.normalization_base_name == 'first_bar':
            normalization_base_time = self.first_bar_time
        elif self.normalization_base_name == 'last_bar':
            normalization_base_time = self.last_bar_time
            
        else:
            normalization_base_time = self.server_times_of_interest[self.normalization_base_name]
        
        normalization_base_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, 
                                                                  self.timeframe, 
                                                                  normalization_base_time, 
                                                                  1))
        if not normalization_base_bar.empty:
            self.normalization_base = normalization_base_bar['open'][0]

    def get_shown_digits(self):
        if self.data_scale == 'absolute':
            return(self.digits)
        elif self.data_scale == 'normalized':
            return(NORMALIZATION_DATA[self.symbol]['digits'] if self.symbol in NORMALIZATION_DATA else DEFAULTS['digits'])
        elif self.data_scale == 'logarithmic':
            return(6)

    def get_normalization_factor(self):
        if self.data_scale == 'normalized':
            power = NORMALIZATION_DATA[self.symbol]['power'] if self.symbol in NORMALIZATION_DATA else DEFAULTS['power']
            return(10 ** power)
        else:
            return(None)

    def update_range(self):
        fixed_times = self.server_times_of_interest
        self.graph_range.set_first_and_last_bar_time(fixed_times, self.timeframe)
        self.first_bar_time = self.graph_range.first_bar_time
        self.last_bar_time = self.graph_range.last_bar_time

    def update_current_bar_visibility(self):
        if self.first_bar_time is None or self.last_bar_time is None:
            return
        
        if self.current_bar_open_time <= self.last_bar_time:
            self.shows_current_bar = True
        else:
            self.shows_current_bar = False
    
    @staticmethod
    def get_actual_timestamp(server_time):

        """
        This possibly fails in the DST boundary.
        Pepperstone server time is defined as UTC+3 if there's DST in NY and UTC+2 otherwise.

        The 'time' column provided by mt5.copy_rates_from is NOT a timestamp but instead a shifted timestamp.
        
        To use the 'time' column we need to know the shift, 
        the shift depends on the current server time, 
        the server time depends on DST status, 
        to determine DST status we need to know the time, 
        and our only source of time is by using the 'time' column.
        That creates circularity.

        This function tries to infer the DST status at the time provided by the server
        and get the actual unix timestamp of the instant.
        """

        #Check if the server time is UTC +3 (if NY is in DST)
        timestamp_if_DST = server_time - 3 * HOUR
        NY_datetime_if_DST = datetime.fromtimestamp(timestamp_if_DST, TIMEZONES['New York'])
        if NY_datetime_if_DST.dst():
            return(timestamp_if_DST)
        #Otherwise, it has to be UTC +2
        else:
            timestamp_if_not_DST = server_time - 2 * HOUR
            return(timestamp_if_not_DST)

    @staticmethod
    def create_datetime_column(bars: pd.DataFrame, timezone):
        if timezone == 'server':
            bars['datetime'] = pd.to_datetime(bars['time'], unit = 's')
        else:
            bars['datetime'] = pd.to_datetime(bars['timestamp'], unit = 's', utc = True)
            bars['datetime'] = bars['datetime'].dt.tz_convert(TIMEZONES[timezone])
    
    @staticmethod
    def create_label_columns(bars: pd.DataFrame, timeframe):
        bars['date_label'] = bars['datetime'].dt.strftime('%e %b %Y')
        bars['time_label'] = bars['datetime'].dt.strftime('%H:%M')
        empty_spaces = [EMPTY_SPACE * index for index in range(len(bars))] #Needed to bypass Altair axis defaulting to local timezone
        if len(bars) == 1:
            empty_spaces = [EMPTY_SPACE_2] #Avoids current bar label colliding with the first bar label when they have the same HH:MM.
        bars['axis_label'] = bars['datetime'].dt.strftime(CHART_AXIS_TIME_FORMAT[timeframe]) + empty_spaces

    def scale_point(self, value):

        if self.data_scale == 'absolute':
            return(round(value, self.shown_digits))
        
        if self.data_scale == 'normalized':
            if self.normalization_base is None:
                return
            return(round(((value / self.normalization_base) - 1) * self.normalization_factor, self.shown_digits))
        
        if self.data_scale == 'logarithmic':
            return(round(log10(value), self.shown_digits))
    
    def scale_data(self, bars: pd.DataFrame):
        columns = ['open', 'high', 'low', 'close']

        if self.data_scale == 'absolute':
            bars[columns] = bars[columns].round(self.shown_digits)

        elif self.data_scale == 'normalized':
            if self.normalization_base is None:
                return
            #bars[f'true_{column}'] = round(bars[column] / self.normalization_base, NORMALIZATION_PRECISION)
            bars[columns] = ((bars[columns] / self.normalization_base - 1) * self.normalization_factor).round(self.shown_digits)

        elif self.data_scale == 'logarithmic':
            bars[columns] = (log10(bars[columns])).round(self.shown_digits)

    def get_bars(self):
        bars = pd.DataFrame(mt5.copy_rates_range(self.symbol, 
                                                 self.timeframe, 
                                                 self.first_bar_time, 
                                                 self.last_bar_time))
        if bars.empty:
            return(bars)
        if len(bars) > MAX_BARS_IN_GRAPH:
            self.too_many_bars = True
            return(pd.DataFrame())
        else:
            self.too_many_bars = False
        
        bars['timestamp'] = bars['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(bars, self.timezone)
        self.create_label_columns(bars, self.timeframe)
        self.scale_data(bars)
        return(bars)

    def get_current_bar(self):
        current_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, 
                                                       self.timeframe, 
                                                       self.current_server_time,
                                                       1))
        current_bar['timestamp'] = current_bar['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(current_bar, self.timezone)
        self.create_label_columns(current_bar, self.timeframe)
        self.scale_data(current_bar)
        return(current_bar)
    
    def update_current_data(self):
        current_symbol_info = mt5.symbol_info_tick(self.symbol)
        self.current_server_time = current_symbol_info.time
        self.current_candle_time = self.current_server_time % SECONDS[self.timeframe]
        self.remaining_candle_time = SECONDS[self.timeframe] - self.current_candle_time
        self.current_bid = self.scale_point(current_symbol_info.bid)
        self.current_ask = self.scale_point(current_symbol_info.ask)
        self.current_bar = self.get_current_bar()
        self.current_bar_open_time = self.current_bar['time'][0]

    def full_update(self):
        self.update_current_data()
        self.update_server_times_of_interest()
        self.update_range()
        self.set_normalization_base()
        self.update_current_bar_visibility()
        self.bars = self.get_bars()
        if not self.bars.empty:
            self.max_price = self.bars['high'].max()
            self.min_price = self.bars['low'].min()
            self.date_label = f'{self.bars['date_label'].iloc[0]} - {self.bars['date_label'].iloc[-1]}'
        self.last_current_bar_open_time = self.current_bar_open_time
    
    def update(self): #Soft updates with only the last bar. If the candlestick just closed, updates all bars.
        
        self.update_current_data()
        
        if self.bars.empty:
            return
        
        if self.shows_current_bar:
            self.bars.iloc[-1] = self.current_bar.iloc[0]

        if self.current_bar_open_time >= self.last_current_bar_open_time + SECONDS[self.timeframe] - 1:
            self.full_update()


def is_dst():
    current_NY_date = datetime.now(TIMEZONES['New York'])
    return(current_NY_date.dst())

def get_current_server_time(is_dst):
    current_timestamp = int(time())
    if is_dst:
        return(current_timestamp + 3 * HOUR)
    else:
        return(current_timestamp + 2 * HOUR)

def format_seconds(seconds, timeframe):
    dt = datetime.fromtimestamp(seconds, tz = TIMEZONES['UTC'])
    formatted = dt.strftime(REMAINING_CANDLE_TIME_FORMAT[timeframe])
    return(formatted)

def get_remaining_candle_time(timeframe, is_dst):
    current_server_time = get_current_server_time(is_dst)
    current_candle_time =  current_server_time % SECONDS[timeframe]
    remaining_candle_time = SECONDS[timeframe] - current_candle_time
    return(format_seconds(remaining_candle_time, timeframe))










