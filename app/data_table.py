

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import MetaTrader5 as mt5
from constants import TIMEZONES, DATA_TABLE_DATE_FORMAT
from backend import scale_point, capitalize_first, unscale_point_wrt_current_values
from format_functions import add_sign

import warnings
warnings.filterwarnings('ignore', message = 'The behavior of DataFrame concatenation with empty or all-NA entries is deprecated')
##########


def get_RR_string(price, SL, TP):
    if pd.isna(price) or pd.isna(SL) or pd.isna(TP):
        return('')
    risk = price - SL
    reward = TP - price
    RR = (reward / risk).round(1)
    RR_string = f'1.0 : {RR}'
    return(RR_string)

def get_progress_string(row):   #Format leading zeroes here
    bars = st.session_state['bars_data']
    current_price = bars.current_bid

    if row.Status == 'Pending':
        order = row.source_object
        goal_price_bp = scale_point(order.set_price, 'normalized', bars.normalization_base, order.symbol, rounded = True)
        return(f'{current_price} / {goal_price_bp}')

    if row.Status == 'Open':
        position = row.source_object
        current_price_abs = unscale_point_wrt_current_values(current_price)
        current_bp = scale_point(current_price_abs, 'normalized', position.open_price, position.symbol, rounded = True)
        if pd.isna(position.SL_bp) and pd.isna(position.TP_bp):
            return(add_sign(current_bp))
        currently_winning = current_bp >= 0 if position.direction == 'buy' else current_bp <= 0
        goal_bp = (position.TP_bp if pd.isna(position.SL_bp) else 
                   position.SL_bp if pd.isna(position.TP_bp) else 
                   position.TP_bp if currently_winning else 
                   position.SL_bp)
        if position.direction == 'sell':
            current_bp = -current_bp
            goal_bp = - goal_bp
        return(f'{current_bp} / {goal_bp}')

    if row.Status == 'Alert':
        alert = row.source_object
        goal_price_bp = scale_point(alert.absolute_price, 'normalized', bars.normalization_base, alert.symbol, rounded = True)
        return(f'{current_price} / {goal_price_bp}')

    if row.Status == 'Conditional trade':
        conditional_trade = row.source_object
        trigger_price_bp = scale_point(conditional_trade.absolute_price, 'normalized', bars.normalization_base, conditional_trade.symbol, rounded = True)
        return(f'{current_price} / {trigger_price_bp}')

def generate_trades_data_table():
    trades_data = st.session_state['trades_data']
    PL_equity_column_number = trades_data.columns.get_loc('P/L_acc_percent_(equity)') + 1
    PL_estimate_column_number = trades_data.columns.get_loc('P/L_acc_percent_(estimate)') + 1
    table = pd.DataFrame(columns = ['Status', 'Time', 'Operation', 'Close reason', 'Progress', 'P/L', 'Show', 'server_timestamp', 'source_object'])
    table.index.name = 'ticket'

    for trade in trades_data.itertuples():

        status = trade.status

        server_timestamp = (trade.open_server_time if trade.status == 'open' 
                            else trade.close_server_time if trade.status == 'closed' 
                            else pd.NA)
        
        order_type = '' if trade.order_type == 'market' else trade.order_type
        price = trade.set_price if trade.status == 'pending' else trade.open_price
        RR = get_RR_string(price, trade.SL_abs, trade.TP_abs)

        time = datetime.fromtimestamp(server_timestamp).strftime(DATA_TABLE_DATE_FORMAT)
        operation = f'{trade.direction.capitalize()} {order_type} {trade.symbol} {RR}'
        close_reason = pd.NA if pd.isna(trade.close_reason) else capitalize_first(trade.close_reason)

        if trade.status == 'closed':
            points = trade.points_bp if trade.direction == 'buy' else -trade.points_bp
            progress = add_sign(points)
            PL_percent = (trade[PL_equity_column_number] if not pd.isna(trade[PL_equity_column_number]) 
                        else trade[PL_estimate_column_number])
            PL_percent = add_sign(PL_percent, percent = True)
        else:
            progress = pd.NA
            PL_percent = pd.NA

        table.loc[trade.Index] = [status.capitalize(), time, operation, close_reason, progress, PL_percent, trade.is_shown, server_timestamp, trade]

    table['Status'] = pd.Categorical(table['Status'], categories = ['Alert', 'Open', 'Pending', 'Conditional trade', 'Closed'], ordered = True)
    table.reset_index(inplace = True)
    table.sort_values(by = ['Status', 'server_timestamp', 'ticket'], ascending = [True, False, False], inplace = True)
    table.set_index('ticket', inplace = True)
    
    return(table)

def generate_alerts_data_table():
    alerts = st.session_state['alerts']
    table = pd.DataFrame(columns = ['Status', 'Time', 'Operation', 'Close reason', 'Progress', 'P/L', 'Show', 'server_timestamp', 'source_object'])
    table.index.name = 'ticket'

    index = 0
    for alert in alerts:

        if alert.reason == 'manual':
            operation = f'Alert {alert.symbol}'
            table.loc[index] = ['Alert', pd.NA, operation, pd.NA, pd.NA, pd.NA, True, pd.NA, alert]
            alert.ticket = index
            index = index + 1

        if alert.reason == 'conditional_trade':
            direction = alert.conditional_trade_data['direction']
            order_type = alert.conditional_trade_data['order_type']
            operation = f'Set {direction} {order_type} {alert.symbol}'
            table.loc[index] = ['Conditional trade', pd.NA, operation, pd.NA, pd.NA, pd.NA, True, pd.NA, alert]
            alert.ticket = index
            index = index + 1
    
    table['Status'] = pd.Categorical(table['Status'], categories = ['Alert', 'Open', 'Pending', 'Conditional trade', 'Closed'], ordered = True)

    return(table)

def update_trades_data_table(table):
    bars = st.session_state['bars_data']
    if (table['Status'] == 'Open').any():
        equity = mt5.account_info().equity
    #['Status', 'Time', 'Operation', 'Close reason', +'Progress', +'P/L', 'Show', 'server_timestamp', 'source_object']

    for row in table.itertuples():
        if row.Status == 'Closed':
            continue
        if bars.data_scale == 'normalized' and bars.symbol == row.source_object.symbol:
            table.at[row.Index, 'Progress'] = get_progress_string(row)
        else:
            table.at[row.Index, 'Progress'] = pd.NA

        if row.Status == 'Open':
            position = mt5.positions_get(ticket = row.Index)[0]
            PL = position.profit
            PL_percent = round(PL/(equity - PL) * 100, 1)
            table.at[row.Index, 'P/L'] = add_sign(PL_percent, percent = True)






def update_alerts_data_table(table):
    bars = st.session_state['bars_data']

    for row in table.itertuples():

        if row.Status == 'Alert':
            if bars.data_scale == 'normalized' and bars.symbol == row.source_object.symbol:
                table.at[row.Index, 'Progress'] = get_progress_string(row)
            else:
                table.at[row.Index, 'Progress'] = pd.NA
        
        if row.Status == 'Conditional trade':
            conditional_trade = row.source_object
            direction = conditional_trade.conditional_trade_data['direction']
            order_type = conditional_trade.conditional_trade_data['order_type']
            operation = f'Set {direction} {order_type} {conditional_trade.symbol}'
            
            if bars.data_scale == 'normalized' and bars.symbol == conditional_trade.symbol:
                execution_price_abs = conditional_trade.conditional_trade_data['execution_price']
                execution_price_bp = scale_point(execution_price_abs, 'normalized', bars.normalization_base, conditional_trade.symbol, rounded = True)
                operation = f'{operation} at {execution_price_bp}'
                table.at[row.Index, 'Progress'] = get_progress_string(row)
                table.at[row.Index, 'Operation'] = operation
            else:
                table.at[row.Index, 'Progress'] = pd.NA
                table.at[row.Index, 'Operation'] = operation


def update_data_table(full_update = False):

    if full_update:
        st.session_state['trades_data_table'] = generate_trades_data_table()
        st.session_state['alerts_data_table'] = generate_alerts_data_table()

    update_trades_data_table(st.session_state['trades_data_table'])
    update_alerts_data_table(st.session_state['alerts_data_table'])

    data_table = pd.concat([st.session_state['trades_data_table'], st.session_state['alerts_data_table']])
    data_table.sort_values(by = ['Status'], inplace = True)
    st.session_state['data_table'] = data_table

























