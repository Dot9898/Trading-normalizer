

from datetime import datetime
import streamlit as st
import MetaTrader5 as mt5
import constants
import risk_calculation
from backend import normalize_point_wrt_current_price, unscale_point_wrt_current_values
from alerts import Alert, update_all_trades_data, update_open_and_close_alerts
from data_table import update_data_table


def reload_graph():
    st.session_state['reload_Bars'] = True

def reload_table():
    update_all_trades_data()
    update_open_and_close_alerts()
    update_data_table(full_update = True)

def is_0930_to_1800():
    ny_time = datetime.now(tz = constants.TIMEZONES['New York'])
    if (10 <= ny_time.hour <= 18) or ny_time.hour == 9 and ny_time.minute > 30:
        return(True)
    return(False)


def goto(when):
    for key, setting in constants.ZOOM_FIXED_SETTINGS.items():
        st.session_state[key] = setting
    for key, settings_dict in constants.ZOOM_VARIABLE_SETTINGS.items():
        st.session_state[key] = settings_dict[when]
    if when in ['now', 'hour']:
        st.session_state['selected_normalization_base_name'] = 'market_open' if is_0930_to_1800() else 'server_1:00'
    reload_graph()

def reset_X_shifts():
    st.session_state['right_shift'] = 0
    st.session_state['left_shift'] = 0
    st.session_state['extra_shift'] = 0
    reload_graph()

def X_shift(quantity):
    st.session_state['extra_shift'] += quantity
    reload_graph()

def Y_shift(quantity):
    
    st.session_state['custom_y_range'] = True
    
    if 'y_min' not in st.session_state:
        st.session_state['y_min'] = (0 if st.session_state['bars_data'].min_price is None 
                                     else st.session_state['bars_data'].min_price)
    
    if 'y_max' not in st.session_state:
        st.session_state['y_max'] = (100 if st.session_state['bars_data'].max_price is None 
                                     else st.session_state['bars_data'].max_price)
    
    st.session_state['y_min'] += quantity
    st.session_state['y_max'] += quantity


def update_entry():
    tp = st.session_state['TP']
    sl = st.session_state['SL']
    risk = st.session_state['risk']
    reward = st.session_state['reward']
    entry = risk_calculation.get_entry(tp, sl, risk, reward)
    st.session_state['entry'] = entry

def update_ppb():
    displayed_tp, displayed_sl = st.session_state['TP'], st.session_state['SL']
    tp, sl = normalize_point_wrt_current_price(displayed_tp), normalize_point_wrt_current_price(displayed_sl)
    max_loss = st.session_state['maxloss']
    risk, reward = st.session_state['risk'], st.session_state['reward']
    if tp is None or sl is None or risk == 0 or reward == 0:
        ppb = 0
    else:
        rr = risk/reward
        ppb = risk_calculation.get_ppb_from_trade_risk(max_loss, tp, sl, rr)

    st.session_state['ppb'] = ppb

def update_pppt(): #Always used right after update_ppb
    ppb = st.session_state['ppb']
    current_price = st.session_state['bars_data'].current_bid
    if ppb == 0 or current_price in [0, None]:
        pppt = 0
    else:
        pppt = (10000 / current_price) * ppb
    st.session_state['pppt'] = pppt

def update_max_ppb():
    symbol = st.session_state['selected_symbol']
    margin_req = constants.SYMBOL_DATA[symbol]['margin_req'] if symbol in constants.SYMBOL_DATA else None
    if margin_req in [0, None]:
        max_ppb = 0
    else:
        max_ppb = risk_calculation.get_max_ppb(margin_req)
    st.session_state['max_ppb'] = max_ppb

def update_lotsize(): #Always used right after update_ppb
    current_price = st.session_state['bars_data'].current_bid
    equity = mt5.account_info().equity
    ppb = st.session_state['ppb']
    if ppb == 0 or current_price in [0, None]:
        lotsize = 0
    else:
        lotsize = risk_calculation.get_lotsize_from_ppb_or_pppt(current_price, current_price, equity = equity, ppb = ppb)
    st.session_state['lotsize'] = lotsize

def update_max_lotsize():
    update_max_ppb()
    current_price = st.session_state['bars_data'].current_bid
    equity = mt5.account_info().equity
    max_ppb = st.session_state['max_ppb']
    if max_ppb == 0 or current_price in [0, None]:
        max_lotsize = 0
    else:
        max_lotsize = risk_calculation.get_lotsize_from_ppb_or_pppt(current_price, current_price, equity = equity, ppb = max_ppb)
    st.session_state['max_lotsize'] = max_lotsize

def set_rr():
    if st.session_state['RR'] != 'custom':
        st.session_state['risk'] = st.session_state['RR'][0]
        st.session_state['reward'] = st.session_state['RR'][1]

def update_risk():
    set_rr()
    update_entry()
    update_ppb()
    update_pppt()
    update_lotsize()
    update_max_lotsize()
    update_max_ppb()

def full_update(): #when checking all callbacks UPDATE THIS FUNCTION TO INCLUDE ALERTS, DATA TABLE
    update_risk()
    reload_graph()


def set_alert():
    symbol = st.session_state['selected_symbol']
    price = st.session_state['alert_price']
    bid = st.session_state['bars_data'].current_bid
    more_or_less = 'more' if bid <= price else 'less'
    absolute_price = unscale_point_wrt_current_values(price)
    alert = Alert('manual', symbol = symbol, absolute_price = absolute_price, more_or_less = more_or_less)
    st.session_state['alerts'].add(alert)
    reload_table()

def set_conditional_trade(direction):
    symbol = st.session_state['selected_symbol']
    trigger_price = st.session_state['alert_price']
    bid = st.session_state['bars_data'].current_bid
    more_or_less = 'more' if bid <= trigger_price else 'less'
    trigger_price_abs = unscale_point_wrt_current_values(trigger_price)
    lots = 0.1   ################################################################################
    
    execution_price = st.session_state['entry']
    execution_price_abs = unscale_point_wrt_current_values(execution_price)
    SL = st.session_state['SL']
    SL_abs =  unscale_point_wrt_current_values(SL)
    TP = st.session_state['TP']
    TP_abs = unscale_point_wrt_current_values(TP)

    if direction == 'buy':
        order_type = 'stop' if execution_price_abs > trigger_price_abs else 'limit'
    if direction == 'sell':
        order_type = 'stop' if execution_price_abs < trigger_price_abs else 'limit'

    trade_data = {'symbol': symbol, 
                  'lots': lots, 
                  'direction': direction, 
                  'execution_price': execution_price_abs, 
                  'SL': SL_abs, 
                  'TP': TP_abs, 
                  'order_type': order_type}

    trade_alert = Alert('conditional_trade', symbol = symbol, absolute_price = trigger_price_abs, more_or_less = more_or_less, conditional_trade_data = trade_data)
    st.session_state['alerts'].add(trade_alert)
    reload_table()



















