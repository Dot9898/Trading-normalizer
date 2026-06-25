

from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd



print()
#print('Initialization:', mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe'))

#symbol = 'BTCUSD' #weekend test
#bar_shift_hours = 3
#bar_quantity_hours = 6



#current_symbol_info = mt5.symbol_info_tick(symbol)
#current_server_time = current_symbol_info.time
#bar_shift_seconds = round(bar_shift_hours * 3600)

#last_bar = current_server_time - bar_shift_seconds
#bar_quantity_m5 = round(bar_quantity_hours * 12)



#bars = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, last_bar, bar_quantity_m5)

#print(type(bars))
#print('lastbar', datetime.fromtimestamp(last_bar))
#for bar in bars:
#    print(datetime.fromtimestamp(bar[0]), bar)

#BARS = pd.DataFrame(bars)

#BARS['datetime'] = pd.to_datetime(BARS['time'], unit = 's')



#print(BARS)







