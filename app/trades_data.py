

import pandas as pd
import streamlit as st
import MetaTrader5 as mt5
from constants import DATA_PATH, TRADE_DATA_COLUMNS_TO_TYPES
from backend import normalize_point_wrt_current_price, scale_point
from get_live_data import get_current_server_time
from time import time


def load_trades_data():
    trades_data_path = DATA_PATH / 'trades_data.csv'

    if not trades_data_path.exists():
        trades_data = pd.DataFrame(columns = TRADE_DATA_COLUMNS_TO_TYPES.keys())
        for column, datatype in TRADE_DATA_COLUMNS_TO_TYPES.items():
            trades_data[column] = trades_data[column].astype(datatype)
    else:
        trades_data = pd.read_csv(trades_data_path, dtype = TRADE_DATA_COLUMNS_TO_TYPES)
    trades_data = trades_data.set_index('ticket')
    
    return(trades_data)

def save_trades_data_to_file():
    trades_data_path = DATA_PATH / 'trades_data.csv'
    tmp_path = DATA_PATH / 'trades_data.csv.tmp'

    st.session_state['trades_data'].to_csv(tmp_path, index = True)
    tmp_path.replace(trades_data_path)

def edit_trade_data(ticket, data_to_edit: dict | None = None):
    if data_to_edit is None:
        return()
    
    trades_data = st.session_state['trades_data']
    if ticket not in trades_data.index:
        trades_data.loc[ticket] = pd.NA
        trades_data.at[ticket, 'is_shown'] = True

    for column, new_value in data_to_edit.items():
        trades_data.at[ticket, column] = new_value
    
    save_trades_data_to_file()

def get_trade_data_to_edit(operation_type, 
                           result, 
                           symbol = None, 
                           lots = None, 
                           direction = None, 
                           SL = None, 
                           TP = None, 
                           order_type = None, 
                           set_price = None):
    
    account_info = mt5.account_info()
    
    if operation_type == 'market':

        data = {'status': 'open', 
                'symbol': symbol, 
                'volume': lots, 
                'set_price': result.price, 
                'direction': direction, 
                'order_type': 'market', 
                'balance_at_set': round(account_info.balance), 
                'equity_at_set': round(account_info.equity), 

                'open_server_time': get_current_server_time(), 
                'open_timestamp': int(time()), 
                'open_price_abs': result.price, 
                'balance_at_open': round(account_info.balance), 
                'equity_at_open': round(account_info.equity)}
        
        if set_price != 0:

            if SL is not None:
                data['SL_abs'] = SL
                data['SL_bp'] = round(normalize_point_wrt_current_price(SL), 1)
                #data['SL_acc_percent'] = round((SL/set_price - 1) * 100, 1)

            if TP is not None:
                data['TP_abs'] = TP
                data['TP_bp'] = round(normalize_point_wrt_current_price(TP), 1)
                #data['TP_acc_percent'] = round((TP/set_price - 1) * 100, 1)       

        return(data)

    if operation_type == 'pending':

        if order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT]:
            order_type = 'limit'
        if order_type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP]:
            order_type = 'stop'

        data = {'status': 'pending', 
                'symbol': symbol, 
                'volume': lots, 
                'set_price': set_price, 
                'direction': direction, 
                'order_type': order_type, 
                'balance_at_set': round(account_info.balance), 
                'equity_at_set': round(account_info.equity)}
        
        if set_price != 0:

            if SL is not None:
                data['SL_abs'] = SL
                data['SL_bp'] = round(scale_point(SL, 'normalized', set_price, symbol), 1)
                #data['SL_acc_percent'] = round((SL/set_price - 1) * 100, 1)

            if TP is not None:
                data['TP_abs'] = TP
                data['TP_bp'] = round(scale_point(TP, 'normalized', set_price, symbol), 1)
                #data['TP_acc_percent'] = round((TP/set_price - 1) * 100, 1)   

        return(data)











