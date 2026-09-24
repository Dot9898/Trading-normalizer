

import streamlit as st
import MetaTrader5 as mt5
import constants
import format_functions
import callbacks
from numpy import log10
from format_functions import no_tag_text, as_percent, round_balance, small_linebreak_caption
from alerts import alert_check, notify_executions_in_serie
from data_table import update_data_table
import dialog_boxes
from get_live_data import Graph_range
from graph import generate_graph_in_fragment, update_lines_data


def graph_width_slider(): ##
    st.slider('Graph width', 
              key = 'graph_width_slider', 
              min_value = 1, 
              max_value = 9, 
              step = 1, 
              value = 5) #delete and add to defaults


def timezone_dropdown():
    st.selectbox('Time zone', 
                constants.SHOWN_TIMEZONES, 
                key = 'selected_timezone', 
                format_func = format_functions.timezone_format, 
                on_change = callbacks.reload_graph_and_table)

def timeframe_dropdown():
    st.selectbox('Time frame', 
                constants.TIMEFRAME_LABEL.keys(), 
                key = 'selected_timeframe', 
                format_func = lambda timeframe: constants.TIMEFRAME_LABEL[timeframe], 
                on_change = callbacks.reload_graph)

def scale_dropdown():
    st.selectbox('Scale', 
                constants.SCALES,  
                key = 'selected_scale', 
                format_func = str.title, 
                on_change = callbacks.full_update, 
                args = [False, True, True])

def normalization_base_name_dropdown():
    st.selectbox('Zero', 
                constants.NORMALIZATION_BASES, 
                key = 'selected_normalization_base_name', 
                format_func = lambda name: name.capitalize().replace('_', ' '), 
                on_change = callbacks.full_update, 
                args = [False, False, False])


def generate_graph():

    graph_range = Graph_range(first_bar = st.session_state['first_bar'], 
                              left_shift = st.session_state['left_shift'], 
                              left_shift_unit = st.session_state['left_shift_unit'], 
                              last_bar = st.session_state['last_bar'], 
                              right_shift = st.session_state['right_shift'], 
                              right_shift_unit = st.session_state['right_shift_unit'], 
                              extra_shift = st.session_state['extra_shift'], 
                              extra_shift_unit = st.session_state['extra_shift_unit'])
    
    if st.session_state['custom_y_range']:
        price_range = [st.session_state['y_min'], st.session_state['y_max']]
    else:
        price_range = 'auto'

    generate_graph_in_fragment(symbol = st.session_state['selected_symbol'], 
                               timeframe = st.session_state['selected_timeframe'], 
                               graph_range = graph_range, 
                               timezone = st.session_state['selected_timezone'], 
                               data_scale = st.session_state['selected_scale'], 
                               normalization_base_name = st.session_state['selected_normalization_base_name'], 
                               price_range = price_range, 
                               lines_data = st.session_state['lines_data'])


def X_range_widgets(what_widgets):

    if what_widgets == 'first_bar':
        st.selectbox('From', 
                    constants.INTERESTING_TIMES, 
                    key = 'first_bar', 
                    format_func = lambda name: name.capitalize().replace('_', ' '), 
                    on_change = callbacks.reset_X_shifts)
        
        shift_column, unit_column = st.columns([1, 2])
        with shift_column:
            st.number_input('Shift', 
                            key = 'left_shift', 
                            step = 1, 
                            label_visibility = 'collapsed', 
                            on_change = callbacks.reload_graph)
        with unit_column:
            st.selectbox('Unit', 
                        constants.SHIFT_UNITS, 
                        key = 'left_shift_unit', 
                        label_visibility = 'collapsed', 
                        format_func = str.capitalize, 
                        on_change = callbacks.reload_graph)
    
    if what_widgets == 'last_bar':
        st.selectbox('To', 
                    constants.INTERESTING_TIMES, 
                    key = 'last_bar', 
                    format_func = lambda name: name.capitalize().replace('_', ' '), 
                    on_change = callbacks.reset_X_shifts)
        
        shift_column, unit_column = st.columns([1, 2])
        with shift_column:
            st.number_input('Shift', 
                            key = 'right_shift', 
                            step = 1, 
                            label_visibility = 'collapsed', 
                            on_change = callbacks.reload_graph)
        with unit_column:
            st.selectbox('Unit', 
                        constants.SHIFT_UNITS, 
                        key = 'right_shift_unit', 
                        label_visibility = 'collapsed', 
                        format_func = str.capitalize, 
                        on_change = callbacks.reload_graph)
    
    if what_widgets == 'shift':
        shift_column, unit_column = st.columns([1, 2])
        with shift_column:
            st.number_input('Shift', 
                            key = 'extra_shift', 
                            step = 1, 
                            label_visibility = 'collapsed', 
                            on_change = callbacks.reload_graph)
        with unit_column:
            st.selectbox('Unit', 
                        constants.SHIFT_UNITS, 
                        key = 'extra_shift_unit', 
                        label_visibility = 'collapsed', 
                        format_func = str.capitalize, 
                        on_change = callbacks.reload_graph)

def get_y_step():

    display = (constants.SYMBOL_DATA[st.session_state['selected_symbol']]['display'] if 
               st.session_state['selected_symbol'] in constants.SYMBOL_DATA else 
               constants.DEFAULTS['display'])
    
    if st.session_state['selected_scale'] == 'logarithmic':
        y_step = 0.2
    
    elif st.session_state['selected_scale'] == 'normalized':
        y_step = 10 if display == 'basis' else 1
    
    elif st.session_state['selected_scale'] == 'absolute':
        current_price = st.session_state['bars_data'].current_bid
        if current_price in [0, None]:
            y_step = 1
        else:
            digits = round(log10(abs(current_price))) - (3 if display == 'basis' else 2) #Display type depends on average movement
            y_step = 10 ** digits

    return(float(y_step))

def Y_range_widgets():
    
    if st.session_state['custom_y_range']:
        bottom = (0 if st.session_state['bars_data'].min_price is None 
                  else st.session_state['bars_data'].min_price)
        top = (100 if st.session_state['bars_data'].max_price is None 
               else st.session_state['bars_data'].max_price)
        step = get_y_step()
        bottom_column, top_column = st.columns(2)
        
        with bottom_column:
            st.number_input('Bottom', 
                            key = 'y_min', 
                            value = bottom, 
                            step = step, 
                            label_visibility = 'collapsed', 
                            on_change = callbacks.reload_graph)
        
        with top_column:
            st.number_input('Top', 
                            key = 'y_max', 
                            value = top, 
                            step = step, 
                            label_visibility = 'collapsed', 
                            on_change = callbacks.reload_graph)
    
    st.checkbox('Custom Y range', 
                key = 'custom_y_range', 
                on_change = callbacks.reload_graph)


def X_navigation_buttons():
    left_button_column, right_button_column = st.columns(2)
    with left_button_column:
        st.button('←', 
                  key = 'go_left', 
                  on_click = callbacks.X_shift, 
                  args = [-1], 
                  width = 'stretch')
    with right_button_column:
        st.button('→', 
                  key = 'go_right', 
                  on_click = callbacks.X_shift, 
                  args = [1], 
                  width = 'stretch')

def Y_navigation_buttons():
    down_button_column, up_button_column = st.columns(2)
    with down_button_column:
        st.button('↓', 
                key = 'go_down', 
                on_click = callbacks.Y_shift, 
                args = [-get_y_step()], 
                width = 'stretch')
    with up_button_column:
        st.button('↑', 
                key = 'go_up', 
                on_click = callbacks.Y_shift, 
                args = [get_y_step()], 
                width = 'stretch')

def zoom_buttons():

    now_column, zoom_column = st.columns(2)
    with now_column:
        st.button('Now', 
                  key = 'go_now', 
                  on_click = callbacks.goto, 
                  args = ['now'], 
                  width = 'stretch')
    with zoom_column:
        st.button('Zoom', 
                  key = 'go_zoom', 
                  on_click = callbacks.goto, 
                  args = ['hour'], 
                  width = 'stretch')
        
    year_column, month_column, week_column, day_column = st.columns(4)
    with year_column:
        st.button('Year', 
                  key = 'go_year', 
                  on_click = callbacks.goto, 
                  args = ['year'], 
                  width = 'stretch')
    with month_column:
        st.button('Month', 
                  key = 'go_month', 
                  on_click = callbacks.goto, 
                  args = ['month'], 
                  width = 'stretch')
    with week_column:
        st.button('Week', 
                  key = 'go_week', 
                  on_click = callbacks.goto, 
                  args = ['week'], 
                  width = 'stretch')
    with day_column:
        st.button('Day', 
                  key = 'go_day', 
                  on_click = callbacks.goto, 
                  args = ['day'], 
                  width = 'stretch')


def symbol_dropdown():
    st.selectbox('Ticker', 
                constants.SHOWN_SYMBOLS,  
                key = 'selected_symbol', 
                on_change = callbacks.full_update, 
                args = [True, True, False])

def is_order_button_disabled(direction):
    if st.session_state['first_run']:
        return(True)
    if st.session_state['selected_scale'] == 'logarithmic':
        return(True)
    SL = st.session_state['SL']
    TP = st.session_state['TP']
    enabled = (SL < TP if direction == 'buy' 
               else SL > TP if direction == 'sell' 
               else False)
    return(not enabled)

def market_order_buttons():
    sell_column, buy_column = st.columns(2)
    with sell_column:
        st.button('Sell', 
                  key = 'sell_button', 
                  disabled = is_order_button_disabled('sell'), 
                  on_click = callbacks.place_order, 
                  args = ['market', 'sell'], 
                  width = 'stretch')
    with buy_column:
        st.button('Buy', 
                  key = 'buy_button', 
                  disabled = is_order_button_disabled('buy'), 
                  on_click = callbacks.place_order, 
                  args = ['market', 'buy'], 
                  width = 'stretch')

def limit_order_buttons():
    sell_limit_column, buy_limit_column = st.columns(2)
    with sell_limit_column:
        st.button('Sell limit\n\nSell stop', 
                  key = 'limit_sell_button', 
                  disabled = is_order_button_disabled('sell'), 
                  on_click = callbacks.place_order, 
                  args = ['pending', 'sell'], 
                  width = 'stretch', 
                  wrap = True)
    with buy_limit_column:
        st.button('Buy limit\n\nBuy stop', 
                  key = 'limit_buy_button', 
                  disabled = is_order_button_disabled('buy'), 
                  on_click = callbacks.place_order, 
                  args = ['pending', 'buy'], 
                  width = 'stretch', 
                  wrap = True)

def get_SLTP_step():
    if st.session_state['selected_scale'] == 'logarithmic':
        step = 0.00001
    
    elif st.session_state['selected_scale'] == 'normalized':
        display = (constants.SYMBOL_DATA[st.session_state['selected_symbol']]['display'] 
                   if st.session_state['selected_symbol'] in constants.SYMBOL_DATA 
                   else constants.DEFAULTS['display'])
        step = 0.1 if display == 'basis' else 0.01

    elif st.session_state['selected_scale'] == 'absolute':
        step = st.session_state['bars_data'].digits

    return(float(step))

def SL_and_TP_input():
    disabled = st.session_state['selected_scale'] == 'logarithmic'
    step = get_SLTP_step()
    digits = st.session_state['bars_data'].shown_digits
    format = f'%0.{digits}f'
    if st.session_state['update_SLTP']:
        callbacks.update_SLTP()
    SL_column, TP_column = st.columns(2)

    with SL_column:
        st.number_input('SL', 
                        key = 'SL', 
                        disabled = disabled, 
                        step = step, 
                        format = format, 
                        on_change = callbacks.update_risk)
    
    with TP_column:
        st.number_input('TP', 
                        key = 'TP', 
                        disabled = disabled, 
                        step = step, 
                        format = format, 
                        on_change = callbacks.update_risk)

def entry_display():
    digits = st.session_state['bars_data'].shown_digits
    format = f'%0.{digits}f'
    step = get_SLTP_step()
    st.number_input('Entry', 
                    key = 'entry', 
                    step = step, 
                    format = format, 
                    disabled = True)


def ppb_display():
    symbol = st.session_state['selected_symbol']
    warning_number = constants.SYMBOL_DATA[symbol]['ideal_ppb'] if symbol in constants.SYMBOL_DATA else None
    if warning_number is None:
        label = '(ideal is unknown)'
    else:
        label = f'({warning_number} is reasonable)'
    
    st.number_input(f'PPB {label}', 
                    key = 'ppb', 
                    step = 0.00001, 
                    format = '%0.2f', 
                    disabled = True)

@st.fragment(run_every = constants.TRADES_UPDATE_INTERVAL)
def max_ppb_display():
    if st.session_state['update_maxes']:
        callbacks.update_max_ppb_and_lotsize()
    st.number_input('Max PPB', 
                    key = 'max_ppb', 
                    step = 0.00001, 
                    format = '%0.2f', 
                    disabled = True)

def pppt_display():
    st.number_input('PPPT', 
                    key = 'pppt', 
                    step = 0.00001, 
                    format = '%0.2f', 
                    disabled = True)

def get_lotsize_step():
    symbol = st.session_state['selected_symbol']
    step = mt5.symbol_info(symbol).volume_step
    return(step)

def lotsize_display():
    st.number_input('Lotsize', 
                    key = 'lotsize', 
                    step = get_lotsize_step(), 
                    format = '%0.2f', 
                    disabled = True)

@st.fragment(run_every = constants.TRADES_UPDATE_INTERVAL)
def max_lotsize_display():
    if st.session_state['update_maxes']:
        callbacks.update_max_ppb_and_lotsize()
    st.number_input('Max lotsize', 
                    key = 'max_lotsize', 
                    step = get_lotsize_step(), 
                    format = '%0.2f', 
                    disabled = True)

def max_loss_input():
    st.number_input('Max loss (%)', 
                    key = 'maxloss', 
                    min_value = -100.0, 
                    max_value = float(0), 
                    step = 0.5, 
                    format = '%0.1f', 
                    on_change = callbacks.update_risk)

def RR_dropdown():
    st.selectbox('RR ratio', 
                constants.RR, 
                key = 'RR', 
                format_func = format_functions.RR_format, 
                on_change = callbacks.update_risk)

def RR_and_maxloss_widgets():
    risk_column, reward_column = st.columns(2)
    
    with risk_column:
        max_loss_input()
    with reward_column:
        RR_dropdown()
    
    if st.session_state['RR'] == 'custom':
        with risk_column:
            st.number_input('Risk', 
                            key = 'risk', 
                            min_value = 0.0, 
                            value = 0.0, 
                            step = 0.1, 
                            format = '%0.1f', 
                            on_change = callbacks.update_risk)
        with reward_column:
            st.number_input('Reward', 
                            key = 'reward', 
                            min_value = 0.0, 
                            value = 0.0, 
                            step = 0.1, 
                            format = '%0.1f', 
                            on_change = callbacks.update_risk)


def settings_checkboxes():
    conditionals_column, account_data_column = st.columns(2)
    with conditionals_column:
        st.checkbox('Set alert', 
                    key = 'alerts_checkbox', 
                    on_change = callbacks.alerts_checkbox_callback)
    with account_data_column:
        st.checkbox('Show account data', 
                    key = 'account_data_checkbox', 
                    on_change = callbacks.uncheck_checkbox, 
                    args = ['alerts_checkbox'])
        st.checkbox('Show hidden trades', 
                    key = 'show_hidden_checkbox')

def account_data_info():
    available_percent = as_percent(st.session_state['available_fraction_of_account'])
    account_info = st.session_state['bars_data'].current_account_info
    rounded_balance = round_balance(account_info.balance)

    margin_text = f'Margin available: {available_percent}'
    balance_text = f'Balance: ${rounded_balance}'
    small_linebreak_caption(margin_text, balance_text, alignment = 'right')

def alert_price_input():
    disabled = st.session_state['selected_scale'] == 'logarithmic'
    bid = st.session_state['bars_data'].current_bid
    step = get_SLTP_step()
    digits = st.session_state['bars_data'].shown_digits
    format = f'%0.{digits}f'

    st.number_input('Price', 
                    key = 'alert_price', 
                    disabled = disabled, 
                    value = bid, 
                    step = step, 
                    format = format, 
                    label_visibility = 'collapsed', 
                    on_change = update_lines_data, 
                    args = ['current_levels'])

def set_alert_button():
    disabled = st.session_state['selected_scale'] == 'logarithmic'
    st.button('Set alert', 
                key = 'alert_button', 
                disabled = disabled, 
                on_click = callbacks.set_alert, 
                width = 'stretch')

def set_conditional_trade_button(direction):
    if direction == 'sell':
        st.button('Set SL/SS', 
                    key = 'conditional_sell_button', 
                    disabled = is_order_button_disabled('sell'), 
                    on_click = callbacks.set_conditional_trade, 
                    args = ['sell'], 
                    width = 'stretch')
    if direction == 'buy':
        st.button('Set BL/BS', 
                    key = 'conditional_buy_button', 
                    disabled = is_order_button_disabled('buy'), 
                    on_click = callbacks.set_conditional_trade, 
                    args = ['buy'], 
                    width = 'stretch')

def alerts_and_conditional_trades_widgets():
    text_column, price_column = st.columns(2)

    with price_column:
        alert_price_input()

    price = st.session_state['alert_price']
    bid = st.session_state['bars_data'].current_bid
    sign = '≥' if bid <= price else '≤'

    with text_column:
        no_tag_text(f'If price {sign}', font_size = '1.5rem', font_weight = '600', alignment = 'center')

    buy_column, alert_column, sell_column = st.columns(3)
    with buy_column:
        set_conditional_trade_button('sell')
    with alert_column:
        set_alert_button()
    with sell_column:
        set_conditional_trade_button('buy')


@st.fragment(run_every = constants.TRADES_UPDATE_INTERVAL)
def reload_table_and_lines_and_maxes():
    st.session_state['update_maxes'] = True
    st.session_state['update_data_table'] = True
    st.session_state['update_graph_lines'] = True

@st.fragment(run_every = constants.POLLING_INTERVAL)
def data_table():
    if st.session_state['first_run']:
        return
    alert_check()
    update_data_table()
    if st.session_state['alerts_pending_notification']:
        notify_executions_in_serie()

    display_table = st.session_state['data_table'].drop(columns = ['source_object']) #Object can't be converted by st.dataframe
    if not st.session_state['show_hidden_checkbox']:
        display_table = display_table[display_table['is_shown'] == True]
    st.session_state['displayed_table'] = display_table

    column_config = {'action_button_1': st.column_config.ButtonColumn('', 
                                                                      key = 'action_button_1_state', 
                                                                      on_click = callbacks.execute_table_action, 
                                                                      args = [1]), 
                     'action_button_2': st.column_config.ButtonColumn('', 
                                                                      key = 'action_button_2_state', 
                                                                      on_click = callbacks.execute_table_action, 
                                                                      args = [2])}
    
    st.dataframe(display_table, 
                 hide_index = True, 
                 column_order = constants.SHOWN_TRADES_DATA_COLUMNS, 
                 column_config = column_config, 
                 placeholder = '-', 
                 height = constants.DATA_TABLE_HEIGHT)

@st.fragment(key = 'dialog_fragment')
def open_dialog():
    data = st.session_state['dialog_data']
    st.session_state['dialog_data'] = None
    reason = data['reason']
    
    if reason in ['open', 'set']:
        dialog_boxes.place_order(reason, data['direction'])
    
    if reason in ['edit', 'modify', 'erase']:
        dialog_boxes.modify_trade_data(reason, data['ticket'])
    
    if reason in ['success', 'not_found', 'null_lotsize']:
        dialog_boxes.bare_text(reason)
    
    if reason == 'error':
        dialog_boxes.bare_text(reason, data['error_code'])









@st.fragment(run_every = constants.POLLING_INTERVAL)
def print_prices_test():
    bars = st.session_state['bars_data']
    bid, ask = bars.current_bid, bars.current_ask
    bcol, acol = st.columns([1, 1])
    with bcol:
        st.header(0 if bid is None else bid, text_alignment = 'center')
    with acol:
        st.header(0 if ask is None else ask, text_alignment = 'center')


































