

import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
from constants import BARS_PER_HOUR, SECONDS, TIMEZONES, CHART_AXIS_TIME_FORMAT, HOUR, DAY

class Bars:

    def __init__(self, symbol, timeframe, left_shift_hours, range_type, range, timezone, data_scale):
        self.symbol = symbol
        self.timeframe = timeframe
        self.shift = round(left_shift_hours * HOUR) #incluir shift en range type date
        self.range_type = range_type
        self.range = range   #An number represeting hours or days, or a str of the name of the first bar
        self.timezone = timezone

        self.is_connected = self.initialize_MetaTrader()
        self.name = mt5.symbol_info(self.symbol).description
        self.digits = mt5.symbol_info(self.symbol).digits
        self.spread = round(mt5.symbol_info(self.symbol).spread / (10 ** self.digits), self.digits)
        self.is_static = False if self.shift == 0 else True

        self.old_bar_server_time = self.get_current_bar()['time'][0]
        self.bars = self.get_bars()
        self.current_bid = round(mt5.symbol_info_tick(self.symbol).bid, self.digits)
        self.current_ask = round(self.current_bid + self.spread, self.digits)

    def initialize_MetaTrader(self):
        return(mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe'))
    
    def get_current_server_time(self):
        current_symbol_info = mt5.symbol_info_tick(self.symbol)
        current_server_time = current_symbol_info.time
        return(current_server_time)

    def get_bar_quantity(self):
        if self.range_type == 'hours':
            bar_quantity = round(self.range * BARS_PER_HOUR[self.timeframe])
            return(bar_quantity)
    
    def get_bars_range(self):
        if self.range_type == 'date':
            first_bar_time = self.get_server_times_of_interest()[self.range]
            last_bar_time = self.get_current_server_time()
            return(first_bar_time, last_bar_time)

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
    
    def get_server_times_of_interest(self, shift_in_days = 0): #This is so ugly why couldn't they provide a normal timestamp
        server_time_of = {}

        current_server_time = self.get_current_server_time()
        server_day_start = current_server_time - current_server_time % DAY
        NY_day_start = server_day_start + 7 * HOUR

        server_time_of['market_open'] = NY_day_start + int(9.5 * HOUR)
        server_time_of['market_close'] = NY_day_start + 16 * HOUR
        server_time_of['server_open'] = server_day_start + 1 * HOUR

        for key, time in server_time_of.items():
            if time > current_server_time:
                server_time_of[key] = time - DAY
        
        for key, time in server_time_of.items():
            server_time_of[key] = time - shift_in_days * DAY
        
        return(server_time_of)
    
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
        bars['axis_label'] = bars['datetime'].dt.strftime(CHART_AXIS_TIME_FORMAT[timeframe])

    def get_bars2(self):
        bars = pd.DataFrame(mt5.copy_rates_from(self.symbol, 
                                                self.timeframe, 
                                                self.get_current_server_time() - self.shift, 
                                                self.get_bar_quantity()))
        bars['timestamp'] = bars['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(bars, self.timezone)
        self.create_label_columns(bars, self.timeframe)
        return(bars)

    def get_bars(self):
        first_bar_time, last_bar_time = self.get_bars_range()
        bars = pd.DataFrame(mt5.copy_rates_range(self.symbol, 
                                                 self.timeframe, 
                                                 first_bar_time, 
                                                 last_bar_time))
        bars['timestamp'] = bars['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(bars, self.timezone)
        self.create_label_columns(bars, self.timeframe)
        return(bars)

    def get_current_bar(self):
        current_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, 
                                                       self.timeframe, 
                                                       self.get_current_server_time(), 
                                                       1))
        current_bar['timestamp'] = current_bar['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(current_bar, self.timezone)
        self.create_label_columns(current_bar, self.timeframe)
        return(current_bar)
    
    def full_update(self):
        self.bars = self.get_bars()
    
    def update(self): #Soft updates with only the last bar. If the candlestick just closed, updates all bars.
        current_bar = self.get_current_bar()

        if not self.is_static:
            self.bars.iloc[-1] = current_bar.iloc[0]
            current_bar_server_time = current_bar['time'][0]
            if current_bar_server_time >= self.old_bar_server_time + SECONDS[self.timeframe] - 1:
                self.full_update()
                self.old_bar_server_time = current_bar_server_time
        
        self.current_bid = round(current_bar['close'][0], self.digits)
        self.current_ask = round(self.current_bid + self.spread, self.digits)










