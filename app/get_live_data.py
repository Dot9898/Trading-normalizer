

import pandas as pd
from datetime import datetime
from numpy import log10
import MetaTrader5 as mt5
from constants import SECONDS, TIMEZONES, CHART_AXIS_TIME_FORMAT, HOUR, DAY, EMPTY_SPACE, EMPTY_SPACE_2


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
        if unit == 'hours':
            offset = shift * HOUR
        if unit == 'days':
            offset = shift * DAY
        if unit == 'bars':
            offset = shift * SECONDS[timeframe]
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
        self.symbol = symbol
        self.timeframe = timeframe
        self.graph_range = graph_range
        self.timezone = timezone
        self.data_scale = data_scale
        self.normalization_base_name = normalization_base_name

        self.is_connected = self.initialize_MetaTrader()
        self.name = mt5.symbol_info(self.symbol).description
        self.digits = mt5.symbol_info(self.symbol).digits
        self.shown_digits = 3 if data_scale == 'normalized' else 6 if data_scale == 'logarithmic' else self.digits
        #self.spread = round(mt5.symbol_info(self.symbol).spread / (10 ** self.digits), self.digits) #absolute

        self.first_bar_time = None
        self.last_bar_time = None
        self.shows_current_bar = None
        self.normalization_base = None
        self.last_current_bar_open_time = self.get_current_bar()['time'][0]
        self.bars = None
        self.max_price = None
        self.min_price = None
        self.date_label = None
        self.current_bid = None
        self.current_ask = None
        self.full_update()

    def initialize_MetaTrader(self):
        return(mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe'))
    
    def get_current_server_time(self):
        current_symbol_info = mt5.symbol_info_tick(self.symbol)
        current_server_time = current_symbol_info.time
        return(current_server_time)
    
    def get_server_times_of_interest(self):
        server_time_of = {}
        current_server_time = self.get_current_server_time()

        server_day_start = current_server_time - current_server_time % DAY
        NY_day_start = server_day_start + 7 * HOUR

        server_time_of['market_open'] = NY_day_start + int(9.5 * HOUR)
        server_time_of['market_close'] = NY_day_start + 16 * HOUR
        server_time_of['server_1:00'] = server_day_start + 1 * HOUR

        for key, time in server_time_of.items():
            if time > current_server_time:
                server_time_of[key] = time - DAY
        
        server_time_of['now'] = current_server_time

        return(server_time_of)

    def set_normalization_base(self):
        if self.normalization_base_name is None:
            self.normalization_base = None
            return
        elif self.normalization_base_name == 'first_bar':
            normalization_base_time = self.first_bar_time
        elif self.normalization_base_name == 'last_bar':
            normalization_base_time = self.last_bar_time
        else:
            normalization_base_time = self.get_server_times_of_interest()[self.normalization_base_name]
        
        normalization_base_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, 
                                                                  self.timeframe, 
                                                                  normalization_base_time, 
                                                                  1))
        self.normalization_base = normalization_base_bar['open'][0]


    def update_range(self):
        fixed_times = self.get_server_times_of_interest()
        self.graph_range.set_first_and_last_bar_time(fixed_times, self.timeframe)
        self.first_bar_time = self.graph_range.first_bar_time
        self.last_bar_time = self.graph_range.last_bar_time

    def update_current_bar_visibility(self):
        if self.first_bar_time is None or self.last_bar_time is None:
            return
        
        if self.get_current_bar_open_time() <= self.last_bar_time:
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

        #Check if the server timestamp is UTC +3 (if NY is in DST)
        timestamp_if_DST = server_time - 3 * HOUR
        NY_datetime_if_DST = datetime.fromtimestamp(timestamp_if_DST, TIMEZONES['NY'])
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

    @staticmethod
    def scale_point(point, scale, digits, base = None):
        if scale == 'absolute':
            return(round(point, digits))
        if scale == 'normalized':
            if base is None:
                return
            return(round(point / base * 100, digits))
        if scale == 'logarithmic':
            return(round(log10(point), digits))
    
    @staticmethod
    def scale_data(bars: pd.DataFrame, scale, digits, base = None):
        for column in ['open', 'high', 'low', 'close']:
            if scale == 'absolute':
                bars[column] = round(bars[column], digits)
            if scale == 'normalized':
                if base is None:
                    return
                bars[column] = round(bars[column] / base * 100, digits)
            if scale == 'logarithmic':
                bars[column] = round(log10(bars[column]), digits)

    def get_bars(self):
        bars = pd.DataFrame(mt5.copy_rates_range(self.symbol, 
                                                 self.timeframe, 
                                                 self.first_bar_time, 
                                                 self.last_bar_time))
        if bars.empty:
            return(bars)
        bars['timestamp'] = bars['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(bars, self.timezone)
        self.create_label_columns(bars, self.timeframe)
        self.scale_data(bars, self.data_scale, self.shown_digits, self.normalization_base)
        self.max_price = bars['high'].max()
        self.min_price = bars['low'].min()
        self.date_label = f'{bars['date_label'].iloc[0]} - {bars['date_label'].iloc[-1]}'
        return(bars)

    def get_current_bar(self):
        current_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, 
                                                       self.timeframe, 
                                                       self.get_current_server_time(), 
                                                       1))
        current_bar['timestamp'] = current_bar['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(current_bar, self.timezone)
        self.create_label_columns(current_bar, self.timeframe)
        self.scale_data(current_bar, self.data_scale, self.shown_digits, self.normalization_base)
        return(current_bar)

    def get_current_bar_open_time(self):
        current_bar = self.get_current_bar()
        open_time = current_bar['time'][0]
        return(open_time)
    
    def update_current_prices(self):
        current_symbol_info = mt5.symbol_info_tick(self.symbol)
        self.current_bid = self.scale_point(current_symbol_info.bid, self.data_scale, self.shown_digits, self.normalization_base)
        self.current_ask = self.scale_point(current_symbol_info.ask, self.data_scale, self.shown_digits, self.normalization_base)

    def full_update(self):
        self.update_range()
        self.update_current_bar_visibility()
        self.set_normalization_base()
        self.bars = self.get_bars()
        self.update_current_prices()
    
    def update(self): #Soft updates with only the last bar. If the candlestick just closed, updates all bars.
        if self.bars.empty:
            return
        
        current_bar = self.get_current_bar()
        if self.shows_current_bar:
            self.bars.iloc[-1] = current_bar.iloc[0]

        current_bar_open_time = self.get_current_bar_open_time()
        if current_bar_open_time >= self.last_current_bar_open_time + SECONDS[self.timeframe] - 1:
            self.full_update()
            self.last_current_bar_open_time = current_bar_open_time
        
        self.update_current_prices()










