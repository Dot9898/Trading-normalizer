

import pandas as pd
import MetaTrader5 as mt5
from constants import BARS_PER_HOUR, SECONDS


class Bars:

    def __init__(self, symbol, timeframe, range_in_hours, left_shift_hours):
        self.symbol = symbol
        self.timeframe = timeframe
        self.bar_quantity = self.get_bar_quantity(range_in_hours)
        self.shift = round(left_shift_hours * 3600)
        self.is_connected = self.initialize_MetaTrader()
        self.spread = self.get_spread()
        self.is_static = False if self.shift == 0 else True
        self.old_bar_timestamp = self.get_current_bar()['time'][0]
        self.bars = self.get_bars()
        self.current_bid = mt5.symbol_info_tick(self.symbol).bid
        self.current_ask = self.current_bid + self.spread


    def initialize_MetaTrader(self):
        return(mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe'))
    
    def get_spread(self):
        digits = mt5.symbol_info(self.symbol).digits
        spread = round(mt5.symbol_info(self.symbol).spread / (10 ** digits), digits)
        return(spread)

    def get_bar_quantity(self, range_in_hours):
        bar_quantity = round(range_in_hours * BARS_PER_HOUR[self.timeframe])
        return(bar_quantity)
    
    def get_current_server_time(self):
        current_symbol_info = mt5.symbol_info_tick(self.symbol)
        current_server_time = current_symbol_info.time
        return(current_server_time)
    
    def get_bars(self):
        bars = pd.DataFrame(mt5.copy_rates_from(self.symbol, self.timeframe, self.get_current_server_time() - self.shift, self.bar_quantity)) #For some reason get_last_bar_timestamp doesn't work.
        bars['datetime'] = pd.to_datetime(bars['time'], unit = 's')
        return(bars)

    def get_current_bar(self):
        current_bar = pd.DataFrame(mt5.copy_rates_from(self.symbol, self.timeframe, self.get_current_server_time(), 1))
        current_bar['datetime'] = pd.to_datetime(current_bar['time'], unit = 's')
        return(current_bar)
    
    def full_update(self):
        self.bars = self.get_bars()
    
    def update(self): #Soft updates with only the last bar. If the candlestick just closed, updates all bars.
        current_bar = self.get_current_bar()

        if not self.is_static:
            self.bars.iloc[-1] = current_bar.iloc[0]
            current_bar_timestamp = current_bar['time'][0]
            if current_bar_timestamp >= self.old_bar_timestamp + SECONDS[self.timeframe] - 1:
                self.full_update()
                self.old_bar_timestamp = current_bar_timestamp
        
        self.current_bid = current_bar['close'][0]
        self.current_ask = self.current_bid + self.spread






















