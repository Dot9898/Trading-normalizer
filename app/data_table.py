

import streamlit as st
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from constants import TIMEZONES
from backend import scale_point, capitalize_first

import warnings
warnings.filterwarnings('ignore', message = 'The behavior of DataFrame concatenation with empty or all-NA entries is deprecated')


def create_datetime_label(ts_column, timezone):

    if timezone == 'server':
        datetime_column = pd.to_datetime(ts_column, unit = 's')
    else:
        datetime_column = pd.to_datetime(ts_column, unit = 's', utc = True)
        datetime_column = datetime_column.dt.tz_convert(TIMEZONES[timezone])

    label_column = datetime_column.dt.strftime('%e %b %Y, %H:%M')
    return(label_column)

def get_RR_column(price, SL, TP):   #Columns
    price = price.astype('Float64')
    SL = SL.astype('Float64')
    TP = TP.astype('Float64')
    risk = price - SL
    reward = TP - price
    RR = (reward / risk).round(1)
    RR_string = ('1.0 : ' + RR.astype('string')).where(SL.notna() & TP.notna(), '')
    return(RR_string)

def get_current_prices():
    trades_data = st.session_state['trades_data']
    alerts = st.session_state['alerts']
    all_symbols = set(trades_data['symbol']) | set(alert.symbol for alert in alerts)
    current_prices = {symbol: mt5.symbol_info_tick(symbol).bid for symbol in all_symbols}
    return(current_prices)

def get_current_prices_column(current_prices):
    trades_data = st.session_state['trades_data']

    current_prices_bp = pd.Series(pd.NA, index = trades_data.index)
    for ticket in trades_data.index:
        if trades_data.at[ticket, 'status'] == 'open':
            symbol = trades_data.at[ticket, 'symbol']
            open_price = trades_data.at[ticket, 'open_price']
            current_prices_bp.at[ticket] = scale_point(current_prices[symbol], 'normalized', normalization_base = open_price, symbol = symbol)

    return(current_prices_bp)

def generate_trades_data_table(current_prices):

    trades_data = st.session_state['trades_data']

    table = pd.DataFrame(index = trades_data.index)

    table['server_timestamp'] = np.select([trades_data['status'] == 'pending', 
                                           trades_data['status'] == 'open', 
                                           trades_data['status'] == 'closed'], 

                                          [pd.NA, 
                                           trades_data['open_server_time'], 
                                           trades_data['close_server_time']])
    table['price'] = np.select([trades_data['status'] == 'pending', 
                                trades_data['status'] == 'open', 
                                trades_data['status'] == 'closed'], 

                               [trades_data['set_price'], 
                                trades_data['open_price'], 
                                trades_data['open_price']])
    table['RR'] = get_RR_column(table['price'], trades_data['SL_abs'], trades_data['TP_abs'])
    #current_prices_column = get_current_prices_column(current_prices)
    table['current_bp'] = np.select([trades_data['status'] == 'pending', 
                                     trades_data['status'] == 'open', 
                                     (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'SL'), 
                                     (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'TP'), 
                                     (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'manual'), 
                                     (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'SO')], 

                                    [0, 
                                     0, #current_prices_column, 
                                     trades_data['SL_bp'], 
                                     trades_data['TP_bp'], 
                                     trades_data['points_bp'], 
                                     trades_data['points_bp']])
    table['goal_bp'] = np.select([trades_data['status'] == 'pending', 
                                  (trades_data['status'] == 'open'),  #& (current_prices_column >= 0), 
                                  (trades_data['status'] == 'open'),  #& (current_prices_column < 0), 
                                  (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'SL'), 
                                  (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'TP'), 
                                  (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'manual'), 
                                  (trades_data['status'] == 'closed') & (trades_data['close_reason'] == 'SO')], 

                                 [trades_data['TP_bp'], 
                                  trades_data['TP_bp'], 
                                  trades_data['SL_bp'], 
                                  trades_data['SL_bp'], 
                                  trades_data['TP_bp'], 
                                  trades_data['TP_bp'], 
                                  trades_data['TP_bp']])

    #table['order_type'] = limit or stop orders in operation

    table['Status'] = trades_data['status'].str.capitalize()
    table['Time'] = create_datetime_label(table['server_timestamp'], st.session_state['selected_timezone'])
    table['Operation'] = trades_data['direction'].str.capitalize() + ' ' + trades_data['symbol'] + ' ' + table['RR']
    table['Close reason'] = trades_data['close_reason'].apply(capitalize_first)
    table['Progress'] = table['current_bp'].astype('string') + '/' + table['goal_bp'].astype('string')
    table['Show'] = trades_data['is_shown']

    table['Status'] = pd.Categorical(table['Status'], categories = ['Alert', 'Open', 'Pending', 'Conditional trade', 'Closed'], ordered = True)
    table.reset_index(inplace = True)
    table.sort_values(by = ['Status', 'server_timestamp', 'ticket'], inplace = True)
    table.set_index('ticket', inplace = True)
    
    return(table)

def generate_alerts_data_table():
    
    alerts = st.session_state['alerts']

    table = pd.DataFrame(columns = ['Status', 'Time', 'Operation', 'Close reason', 'Progress', 'Show', 'alert_object'])

    index = 0
    for alert in alerts:

        if alert.reason == 'manual':
            operation = f'Alert {alert.symbol}'
            table.loc[index] = ['Alert', pd.NA, operation, pd.NA, pd.NA, True, alert]
            alert.ticket = index
            index = index + 1

        if alert.reason == 'conditional_trade':
            direction = alert.conditional_trade_data['direction']
            order_type = alert.conditional_trade_data['order_type']
            operation = f'Set {direction} {order_type} {alert.symbol}'
            table.loc[index] = ['Conditional trade', pd.NA, operation, pd.NA, pd.NA, True, alert]
            alert.ticket = index
            index = index + 1
    
    table['Status'] = pd.Categorical(table['Status'], categories = ['Alert', 'Open', 'Pending', 'Conditional trade', 'Closed'], ordered = True)

    return(table)

def update_alerts_data_table(table):
    bars = st.session_state['bars_data']
    current_price = bars.current_bid

    for entry in table.itertuples():

        if entry.Status == 'Alert':
            alert = entry.alert_object

            if bars.data_scale == 'normalized' and bars.symbol == alert.symbol:
                goal_price_bp = scale_point(alert.absolute_price, 'normalized', bars.normalization_base, alert.symbol, rounded = True)
                table.at[entry.Index, 'Progress'] = f'{current_price}/{goal_price_bp}'
            else:
                table.at[entry.Index, 'Progress'] = pd.NA
        
        if entry.Status == 'Conditional trade':
            conditional_trade = entry.alert_object
            direction = conditional_trade.conditional_trade_data['direction']
            order_type = conditional_trade.conditional_trade_data['order_type']
            operation = f'Set {direction} {order_type} {conditional_trade.symbol}'
            
            if bars.data_scale == 'normalized' and bars.symbol == conditional_trade.symbol:
                trigger_price_bp = scale_point(conditional_trade.absolute_price, 'normalized', bars.normalization_base, conditional_trade.symbol, rounded = True)
                execution_price_abs = conditional_trade.conditional_trade_data['execution_price']
                execution_price_bp = scale_point(execution_price_abs, 'normalized', bars.normalization_base, conditional_trade.symbol, rounded = True)
                operation = f'{operation} at {execution_price_bp}'
                table.at[entry.Index, 'Progress'] = f'{current_price}/{trigger_price_bp}'
                table.at[entry.Index, 'Operation'] = operation
            else:
                table.at[entry.Index, 'Progress'] = pd.NA
                table.at[entry.Index, 'Operation'] = operation



def update_data_table(full_update = False):

    if full_update:
        st.session_state['trades_data_table'] = generate_trades_data_table('placeholder')#get_current_prices())
        st.session_state['alerts_data_table'] = generate_alerts_data_table()

    #update_trades_data_table(trades_table)
    update_alerts_data_table(st.session_state['alerts_data_table'])

    data_table = pd.concat([st.session_state['trades_data_table'], st.session_state['alerts_data_table']])
    data_table.sort_values(by = ['Status'], inplace = True)
    st.session_state['data_table'] = data_table

























