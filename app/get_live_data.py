

import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
from constants import BARS_PER_HOUR, SECONDS, TIMEZONES, CHART_AXIS_TIME_FORMAT

class Bars:

    def __init__(self, symbol, timeframe, range_in_hours, left_shift_hours, timezone, data_scale):
        self.symbol = symbol
        self.timeframe = timeframe
        self.bar_quantity = self.get_bar_quantity(range_in_hours)
        self.shift = round(left_shift_hours * 3600)
        self.timezone = timezone

        self.is_connected = self.initialize_MetaTrader()
        self.digits = mt5.symbol_info(self.symbol).digits
        self.spread = round(mt5.symbol_info(self.symbol).spread / (10 ** self.digits), self.digits)
        self.is_static = False if self.shift == 0 else True

        self.old_bar_server_time = self.get_current_bar()['time'][0]
        self.bars = self.get_bars()
        self.current_bid = mt5.symbol_info_tick(self.symbol).bid
        self.current_ask = self.current_bid + self.spread

    def initialize_MetaTrader(self):
        return(mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe'))

    def get_bar_quantity(self, range_in_hours):
        bar_quantity = round(range_in_hours * BARS_PER_HOUR[self.timeframe])
        return(bar_quantity)
    
    def get_current_server_time(self):
        current_symbol_info = mt5.symbol_info_tick(self.symbol)
        current_server_time = current_symbol_info.time
        return(current_server_time)

    def get_actual_timestamp(self, server_time): #This probably fails in the DST boundary. The server not providing an absolute timestamp cretes problems.
        #Check if the server timestamp is UTC +3 (if NY is in DST)
        timestamp_if_DST = server_time - 3600 * 3
        NY_datetime_if_DST = datetime.fromtimestamp(timestamp_if_DST, TIMEZONES['NY'])
        if NY_datetime_if_DST.dst():
            return(timestamp_if_DST)
        #Otherwise, it has to be UTC +2
        else:
            timestamp_if_not_DST = server_time - 3600 * 2
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
        bars['axis_label'] = bars['datetime'].dt.strftime(CHART_AXIS_TIME_FORMAT[timeframe])

    def get_bars(self):
        bars = pd.DataFrame(mt5.copy_rates_from(self.symbol, self.timeframe, self.get_current_server_time() - self.shift, self.bar_quantity))
        bars['timestamp'] = bars['time'].apply(self.get_actual_timestamp)
        self.create_datetime_column(bars, self.timezone)
        self.create_label_columns(bars, self.timeframe)
        return(bars)

    def get_current_bar(self):
        current_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, self.timeframe, self.get_current_server_time(), 1))
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
        
        self.current_bid = current_bar['close'][0]
        self.current_ask = self.current_bid + self.spread



#1777939200 00:00 of MT5 server

#86400

#server 16:30  23
#ny      9:30  16

#9.30 es en los time mod 86400 = 16.5 * 3600
#16:00 es en los time mod 86400 = 23 * 3600
#18:00 -> 1 * 3600

#domingo 17:00 -> es en los time mod 86400 * 7 = 3 * 86400   #empieza la semana del server el jueves a las 17:00
#lunes 9:30 es en los time mod 86400 * 7 = 3 * 86400 + 16.5 * 3600

#necesito la diferencia en s desde ese time (server) al actual, para usarla como shift en copy rates from

#ah pf lo tengo directo con la division euclideana de current server time para saber el dia, y un condicional pa saber si ya paso la hora requerida







