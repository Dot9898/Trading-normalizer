

from datetime import datetime
import streamlit as st
import MetaTrader5 as mt5
import constants
import risk_calculation
import order_execution
from backend import scale_point_wrt_current_values, normalize_point_wrt_current_price, unscale_point_wrt_current_values, get_usable_price_level, get_usable_lotsize, get_used_ppb_and_margin_req
from trades_data import edit_trade_data
from alerts import Alert
from graph import update_lines_data


def reload_graph():
    st.session_state['reload_Bars'] = True

def reload_table():
    st.session_state['update_data_table'] = True

def update_trades_and_alerts_lines():
    st.session_state['update_graph_lines'] = True

def reload_graph_and_table():
    reload_graph()
    reload_table()

def is_0930_to_1800():
    ny_time = datetime.now(tz = constants.TIMEZONES['New York'])
    if (10 <= ny_time.hour <= 17) or ny_time.hour == 9 and ny_time.minute > 30:
        return(True)
    return(False)

def set_normalization_base():
    st.session_state['selected_normalization_base_name'] = 'market_open' if is_0930_to_1800() else 'server_1:00'


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

def update_SLTP():
    st.session_state['SL'] = scale_point_wrt_current_values(st.session_state['old_SL_abs'], rounded = True)
    st.session_state['TP'] = scale_point_wrt_current_values(st.session_state['old_TP_abs'], rounded = True)
    update_risk()
    st.session_state['update_SLTP'] = False

def save_old_SLTP_then_update(reset):
    if reset:
        bid = mt5.symbol_info_tick(st.session_state['selected_symbol']).bid
        SL_abs = bid
        TP_abs = bid
    else:
        SL_abs = unscale_point_wrt_current_values(st.session_state['SL'])
        TP_abs = unscale_point_wrt_current_values(st.session_state['TP'])
    st.session_state['old_SL_abs'] = SL_abs
    st.session_state['old_TP_abs'] = TP_abs
    st.session_state['update_SLTP'] = True

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
    pending_and_open_data = get_used_ppb_and_margin_req(include_pending = True)
    symbol = st.session_state['selected_symbol']
    margin_req = constants.SYMBOL_DATA[symbol]['margin_req'] if symbol in constants.SYMBOL_DATA else None
    if margin_req in [0, None]:
        max_ppb = 0
    else:
        max_ppb = risk_calculation.get_max_usable_ppb(pending_and_open_data, margin_req)
    st.session_state['max_ppb'] = round(max_ppb, 5)
    
    available = risk_calculation.get_available_fraction_of_account(pending_and_open_data)
    st.session_state['available_fraction_of_account'] = available

def update_lotsize(): #Always used right after update_ppb
    entry = st.session_state['entry']
    st.session_state['lotsize'] = get_usable_lotsize(execution_price_abs = entry)

def update_max_lotsize(): #Always used right after update_max_ppb
    current_price = st.session_state['bars_data'].current_bid
    equity = st.session_state['bars_data'].current_account_info.equity
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
    update_lines_data('current_levels')

def update_max_ppb_and_lotsize():
    update_max_ppb()
    update_max_lotsize()
    st.session_state['update_maxes'] = False

def full_update(reset_SLTP, update_maxes, force_set_normalization_base):
    if force_set_normalization_base:
        set_normalization_base()
    reload_graph()
    reload_table()
    save_old_SLTP_then_update(reset_SLTP) #Includes risk
    if update_maxes:
        update_max_ppb_and_lotsize()
    update_trades_and_alerts_lines()


def uncheck_checkbox(key):
    st.session_state[key] = False

def alerts_checkbox_callback():
    uncheck_checkbox('account_data_checkbox')
    update_lines_data('current_levels')

def set_alert():
    update_risk()
    symbol = st.session_state['selected_symbol']
    price = st.session_state['alert_price']
    bid = st.session_state['bars_data'].current_bid
    more_or_less = 'more' if bid <= price else 'less'
    absolute_price = unscale_point_wrt_current_values(price)
    alert = Alert('manual', symbol = symbol, absolute_price = absolute_price, more_or_less = more_or_less)
    st.session_state['alerts'].add(alert)
    reload_table()

def set_conditional_trade(direction):
    update_risk()
    symbol = st.session_state['selected_symbol']
    trigger_price = st.session_state['alert_price']
    bid = st.session_state['bars_data'].current_bid
    more_or_less = 'more' if bid <= trigger_price else 'less'
    trigger_price_abs = unscale_point_wrt_current_values(trigger_price)
    lots = get_usable_lotsize(trigger_price_abs)
    
    execution_price = st.session_state['entry']
    execution_price_abs = get_usable_price_level(execution_price)
    SL = st.session_state['SL']
    SL_abs =  get_usable_price_level(SL)
    TP = st.session_state['TP']
    TP_abs = get_usable_price_level(TP)

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

def place_order(order_type, direction):   #If successful, updates data table via order edit_trade_data call
    update_risk()
    if order_type == 'market':
        st.session_state['dialog_data'] = {'reason': 'open', 'direction': direction}
    if order_type == 'pending':
        st.session_state['dialog_data'] = {'reason': 'set', 'direction': direction}

def execute_table_action(button_number):
    """
    This function and the next are called from a inside fragment.
    They use a manual full-app rerun at the end to avoid input lag after being executed.
    """

    button_key = f'action_button_{button_number}_state'
    row_number = st.session_state[button_key].row
    label = st.session_state[button_key].label
    row = st.session_state['displayed_table'].iloc[row_number]
    ticket = int(row.name)
    status = row['Status']
    check_execution = False

    if label == 'Hide':
        assert status == 'Closed'
        data = {'is_shown': False}
        edit_trade_data(ticket, data)

    if label == 'Unhide':
        assert status == 'Closed'
        data = {'is_shown': True}
        edit_trade_data(ticket, data)

    if label == 'Delete' and status in ['Alert', 'Conditional trade']:
        alert = st.session_state['data_table'].loc[ticket, 'source_object']
        st.session_state['alerts'].discard(alert)

    if label == 'Close':
        assert status == 'Open'
        update_risk()
        result = order_execution.close_position(ticket = ticket)
        check_execution = True

    if label == 'Delete' and status == 'Pending':
        result = order_execution.delete_pending_order(ticket = ticket)
        check_execution = True

    if label == 'Erase':
        assert status == 'Closed'
        st.session_state['dialog_data'] = {'reason': 'erase', 'ticket': ticket}

    if label == 'Edit':
        assert status == 'Open'
        update_risk()
        st.session_state['dialog_data'] = {'reason': 'edit', 'ticket': ticket}

    if label == 'Modify':
        assert status == 'Pending'
        update_risk()
        st.session_state['dialog_data'] = {'reason': 'modify', 'ticket': ticket}

    if check_execution:
        if result is None:
            st.session_state['dialog_data'] = {'reason': 'not_found'}
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            if label in ['Close', 'Delete']:
                update_max_ppb_and_lotsize()
        else:
            st.session_state['dialog_data'] = {'reason': 'error', 'error_code': result.retcode}

    st.rerun()

def execute_action_and_dismiss_dialog(reason, direction = None, ticket = None):
    check_execution = True

    if reason == 'erase':
        edit_trade_data(ticket, delete = True)
        check_execution = False

    if reason == 'open':
        symbol = st.session_state['selected_symbol']
        lots = get_usable_lotsize(execution_price_abs = 'current')
        if lots == 0:
            result = 'null_lotsize'
        else:
            SL = get_usable_price_level(st.session_state['SL'])
            TP = get_usable_price_level(st.session_state['TP'])
            result = order_execution.market_order(symbol, lots, direction, SL, TP)

    if reason == 'set':
        symbol = st.session_state['selected_symbol']
        entry_abs = get_usable_price_level(st.session_state['entry'])
        lots = get_usable_lotsize(execution_price_abs = entry_abs)
        if lots == 0:
            result = 'null_lotsize'
        else:
            SL = get_usable_price_level(st.session_state['SL'])
            TP = get_usable_price_level(st.session_state['TP'])
            result = order_execution.limit_or_stop_order(symbol, lots, direction, entry_abs, SL, TP)

    if reason == 'edit':
        new_SL = get_usable_price_level(st.session_state['SL'])
        new_TP = get_usable_price_level(st.session_state['TP'])
        result = order_execution.change_SLTP_open(ticket, new_SL, new_TP)

    if reason == 'modify':
        new_SL = get_usable_price_level(st.session_state['SL'])
        new_TP = get_usable_price_level(st.session_state['TP'])
        new_entry = get_usable_price_level(st.session_state['entry'])
        result = order_execution.change_price_and_SLTP_pending(ticket, new_entry, new_SL, new_TP)

    if check_execution:
        if result == 'not_found':
            st.session_state['dialog_data'] = {'reason': 'not_found'}
        elif result == 'null_lotsize':
            st.session_state['dialog_data'] = {'reason': 'null_lotsize'}
        elif result is None:
            st.session_state['dialog_data'] = {'reason': 'error', 'error_code': None}
        elif result.retcode == mt5.TRADE_RETCODE_DONE:
            st.session_state['dialog_data'] = {'reason': 'success'}
            if reason in ['open', 'set']:
                update_max_ppb_and_lotsize()
        else:
            st.session_state['dialog_data'] = {'reason': 'error', 'error_code': result.retcode}

    st.rerun()













