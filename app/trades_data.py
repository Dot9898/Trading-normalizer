

import pandas as pd
import streamlit as st
import MetaTrader5 as mt5
from constants import DATA_PATH, TRADE_DATA_COLUMNS_TO_TYPES, SYMBOL_DATA
from backend import scale_point
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

def edit_trade_data(ticket, data_to_edit: dict | None = None, delete = False):

    trades_data = st.session_state['trades_data']

    if delete:
        trades_data.drop(ticket, inplace = True)
    
    else:
        if data_to_edit is None:
            return

        if ticket not in trades_data.index:
            trades_data.loc[ticket] = pd.NA
            trades_data.at[ticket, 'is_shown'] = True

        for column, new_value in data_to_edit.items():
            trades_data.at[ticket, column] = new_value

    save_trades_data_to_file()

def get_trade_data_to_edit(ticket, 
                           operation_type, 
                           symbol = None, 
                           lots = None, 
                           direction = None, 
                           SL = None, 
                           TP = None, 
                           order_type = None, 
                           set_price = None):
    
    account_info = mt5.account_info()
    trades_data = st.session_state['trades_data']
    current_server_time = get_current_server_time()
    current_timestamp = int(time())
    
    data = {}

    if operation_type == 'market':
        
        open_positions = mt5.positions_get()
        for position in open_positions:
            if position.ticket == ticket:
                current_position = position

        open_price = current_position.price_open

        data = {'status': 'open', 
                'symbol': symbol, 
                'volume': lots, 
                'set_price': open_price, 
                'direction': direction, 
                'order_type': 'market', 
                'balance_at_set': round(account_info.balance), 
                'equity_at_set': round(account_info.equity), 

                'open_server_time': current_server_time, 
                'open_timestamp': current_timestamp, 
                'open_price': open_price, 
                'balance_at_open': round(account_info.balance), 
                'equity_at_open': round(account_info.equity)}

        if SL is not None:
            data['SL_abs'] = SL
            data['SL_bp'] = round(scale_point(SL, 'normalized', open_price, symbol), 1)
            data['SL_acc_percent_at_set_(equity)'] = round(100 * (SL - set_price) * lots / account_info.equity, 1)
            data['SL_acc_percent_at_open_(equity)'] = round(100 * (SL - open_price) * lots / account_info.equity, 1)

        if TP is not None:
            data['TP_abs'] = TP
            data['TP_bp'] = round(scale_point(TP, 'normalized', open_price, symbol), 1)
            data['TP_acc_percent_at_set_(equity)'] = round(100 * (TP - set_price) * lots / account_info.equity, 1)
            data['TP_acc_percent_at_open_(equity)'] = round(100 * (TP - open_price) * lots / account_info.equity, 1) 


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

        if SL is not None:
            data['SL_abs'] = SL
            data['SL_bp'] = round(scale_point(SL, 'normalized', set_price, symbol), 1)
            data['SL_acc_percent_at_set_(equity)'] = round(100 * (SL - set_price) * lots / account_info.equity, 1)

        if TP is not None:
            data['TP_abs'] = TP
            data['TP_bp'] = round(scale_point(TP, 'normalized', set_price, symbol), 1)
            data['TP_acc_percent_at_set_(equity)'] = round(100 * (TP - set_price) * lots / account_info.equity, 1)


    if operation_type == 'sltp_open':

        open_price = trades_data.at[ticket, 'open_price']

        if SL is None:
            data['SL'] = None
            data['SL_bp'] = None
            data['SL_acc_percent_at_open_(equity)'] = None
        else:
            data['SL_abs'] = SL
            data['SL_bp'] = round(scale_point(SL, 'normalized', open_price, symbol), 1)
            data['SL_acc_percent_at_open_(equity)'] = round(100 * (SL - open_price) * lots / account_info.equity, 1)

        if TP is None:
            data['TP'] = None
            data['TP_bp'] = None
            data['TP_acc_percent_at_open_(equity)'] = None
        else:
            data['TP_abs'] = TP
            data['TP_bp'] = round(scale_point(TP, 'normalized', open_price, symbol), 1)
            data['TP_acc_percent_at_open_(equity)'] = round(100 * (TP - open_price) * lots / account_info.equity, 1)


    if operation_type == 'price_sltp_pending':
        lots = trades_data.at[ticket, 'volume']

        if SL is None:
            data['SL'] = None
            data['SL_bp'] = None
            data['SL_acc_percent_at_set_(equity)'] = None
        else:
            data['SL_abs'] = SL
            data['SL_bp'] = round(scale_point(SL, 'normalized', set_price, symbol), 1)
            data['SL_acc_percent_at_set_(equity)'] = round(100 * (SL - set_price) * lots / account_info.equity, 1)

        if TP is None:
            data['TP'] = None
            data['TP_bp'] = None
            data['TP_acc_percent_at_set_(equity)'] = None
        else:
            data['TP_abs'] = TP
            data['TP_bp'] = round(scale_point(TP, 'normalized', set_price, symbol), 1)
            data['TP_acc_percent_at_set_(equity)'] = round(100 * (TP - set_price) * lots / account_info.equity, 1)


    if operation_type == 'close' :
        open_price = trades_data.at[ticket, 'open_price']

        last_deals = mt5.history_deals_get(current_server_time - 30, current_server_time)
        for deal in last_deals:
            if deal.position_id == ticket and deal.entry == mt5.DEAL_ENTRY_OUT:
                out_deal = deal

        close_price = out_deal.price
        PL = out_deal.profit


        reason = out_deal.reason
        if reason in [mt5.DEAL_REASON_CLIENT, mt5.DEAL_REASON_MOBILE, mt5.DEAL_REASON_WEB, mt5.DEAL_REASON_EXPERT]:
            close_reason = 'manual'
        elif reason == mt5.DEAL_REASON_SL:
            close_reason = 'SL'
        elif reason == mt5.DEAL_REASON_SL:
            close_reason = 'TP'
        elif reason == mt5.DEAL_REASON_SO:
            close_reason = 'stop_out'
        else:
            close_reason = None

        data = {'status': 'closed', 
                
                'close_server_time': current_server_time, 
                'close_timestamp': current_timestamp, 
                'close_reason': close_reason, 
                'close_price': close_price, 
                'points_abs': round(close_price - open_price, 1), 
                'points_bp': round(scale_point(close_price - open_price, 'normalized', open_price, symbol), 1), 
                'balance_at_close': account_info.balance, 
                'equity_at_close': account_info.equity, 
                'P/L_abs': PL, 
                'P/L_acc_percent_(equity)': round(PL/(account_info.equity - PL) * 100, 1), 
                'P/L_acc_percent_(balance)': round(PL/(account_info.balance - PL) * 100, 1)}


    if symbol is not None:
        data['display'] = SYMBOL_DATA[symbol]['display']

    return(data)





#Pensar cuándo quiero updatear la data polleando del server:
#Cuando el server abre una orden pendiente, por precio
#Cuando el server cierra una posición abierta, por precio
#Al iniciar el programa
#Cada cierto tiempo, para revisar acciones remotas del usuario al server (desktop client, mobile), revisar cada acción? o actualizar las abiertas, pendientes, history





