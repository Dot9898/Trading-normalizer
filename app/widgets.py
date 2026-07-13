

import streamlit as st
import MetaTrader5 as mt5
import constants
import format_functions
import callbacks
from numpy import log10
from backend import no_tag_text

def timezone_dropdown():
    st.selectbox('Time zone', 
                constants.SHOWN_TIMEZONES, 
                key = 'selected_timezone', 
                index = 1, 
                format_func = format_functions.timezone_format, 
                on_change = callbacks.reload_graph)

def timeframe_dropdown():
    st.selectbox('Time frame', 
                constants.TIMEFRAME_LABEL.keys(), 
                key = 'selected_timeframe', 
                index = 1, 
                format_func = lambda timeframe: constants.TIMEFRAME_LABEL[timeframe], 
                on_change = callbacks.reload_graph)

def scale_dropdown():
    st.selectbox('Scale', 
                constants.SCALES,  
                key = 'selected_scale', 
                index = 1, 
                format_func = str.title, 
                on_change = callbacks.full_update)
    
def normalization_base_name_dropdown():
    st.selectbox('Zero', 
                constants.NORMALIZATION_BASES, 
                key = 'selected_normalization_base_name', 
                index = 1 if callbacks.is_0930_to_1800() else 3, 
                format_func = lambda name: name.capitalize().replace('_', ' '), 
                on_change = callbacks.reload_graph)


def X_range_widgets(what_widgets):

    if what_widgets == 'first_bar':
        st.selectbox('From', 
                    constants.INTERESTING_TIMES, 
                    key = 'first_bar', 
                    index = 1, 
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
                        index = 1, 
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
                        index = 1, 
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
                        index = 1, 
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
                constants.SYMBOL_DATA.keys(),  
                key = 'selected_symbol', 
                index = 0, 
                on_change = callbacks.full_update)

def market_order_buttons():
    sell_column, buy_column = st.columns(2)
    with sell_column:
        st.button('Sell', 
                  key = 'sell_button', 
                  #on_click = pass, 
                  width = 'stretch')
    with buy_column:
        st.button('Buy', 
                  key = 'buy_button', 
                  #on_click = pass, 
                  width = 'stretch')

def limit_order_buttons():
    sell_limit_column, buy_limit_column = st.columns(2)
    with sell_limit_column:
        st.button('Sell limit\n\nSell stop', 
                  key = 'limit_sell_button', 
                  #on_click = pass,
                  width = 'stretch')
    with buy_limit_column:
        st.button('Buy limit\n\nBuy stop', 
                  key = 'limit_buy_button', 
                  #on_click = pass,
                  width = 'stretch')

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
    bid = st.session_state['bars_data'].current_bid
    step = get_SLTP_step()
    digits = st.session_state['bars_data'].shown_digits
    format = f'%0.{digits}f'
    SL_column, TP_column = st.columns(2)

    with SL_column:
        st.number_input('SL', 
                        key = 'SL', 
                        value = float(bid), 
                        step = step, 
                        format = format, 
                        on_change = callbacks.update_risk)
    
    with TP_column:
        st.number_input('TP', 
                        key = 'TP', 
                        value = bid, 
                        step = step, 
                        format = format, 
                        on_change = callbacks.update_risk)

def entry_display():
    bid = 0.0 if st.session_state['bars_data'].current_bid is None else st.session_state['bars_data'].current_bid
    step = get_SLTP_step()
    st.number_input('Entry', 
                    key = 'entry', 
                    value = bid, 
                    step = step, 
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
                    value = 0.0, 
                    step = 0.00001, 
                    format = '%0.2f', 
                    disabled = True)

def max_ppb_display():
    st.number_input('Max PPB', 
                    key = 'max_ppb', 
                    value = 0.0, 
                    step = 0.00001, 
                    format = '%0.2f', 
                    disabled = True)

def pppt_display():
    st.number_input('PPPT', 
                    key = 'pppt', 
                    value = 0.0, 
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
                    value = 0.0, 
                    step = get_lotsize_step(), 
                    format = '%0.2f', 
                    disabled = True)

def max_lotsize_display():
    st.number_input('Max lotsize', 
                    key = 'max_lotsize', 
                    value = 0.0, 
                    step = get_lotsize_step(), 
                    format = '%0.2f', 
                    disabled = True)

def max_loss_input():
    st.number_input('Max loss (%)', 
                    key = 'maxloss', 
                    min_value = -100.0, 
                    max_value = float(0), 
                    value = -10.0, 
                    step = 0.5, 
                    on_change = callbacks.update_risk)

def RR_dropdown():
    st.selectbox('RR ratio', 
                constants.RR, 
                key = 'RR', 
                index = 2, 
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
                            on_change = callbacks.update_risk)
        with reward_column:
            st.number_input('Reward', 
                            key = 'reward', 
                            min_value = 0.0, 
                            value = 0.0, 
                            step = 0.1, 
                            on_change = callbacks.update_risk)


def alert_price_input():
    bid = st.session_state['bars_data'].current_bid
    step = get_SLTP_step()
    digits = st.session_state['bars_data'].shown_digits
    format = f'%0.{digits}f'

    st.number_input('Price', 
                    key = 'alert_price', 
                    value = bid, 
                    step = step, 
                    format = format, 
                    label_visibility = 'collapsed', 
                    on_change = callbacks.reload_graph)

def set_alert_button():
    st.button('Set alert', 
                key = 'alert_button', 
                on_click = callbacks.set_alert(), 
                width = 'stretch')

def set_conditional_trade_button(direction):
    if direction == 'buy':
        st.button('Set BL/BS', 
                    key = 'conditional_buy_button', 
                    on_click = callbacks.set_conditional_trade, 
                    args = ['buy'], 
                    width = 'stretch')
    if direction == 'sell':
        st.button('Set SL/SS', 
                    key = 'conditional_sell_button', 
                    on_click = callbacks.set_conditional_trade, 
                    args = ['sell'], 
                    width = 'stretch')

def conditionals_and_account_data_checkboxes():
    conditionals_column, account_data_column = st.columns(2)
    with conditionals_column:
        st.checkbox('Set alert', 
                    key = 'conditionals_checkbox')
    with account_data_column:
        st.checkbox('Show account data', 
                    key = 'account_data_checkbox')

def conditional_operations_widgets():
    if st.session_state['conditionals_checkbox']:

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
            st.write()
            set_conditional_trade_button('buy')
        with alert_column:
            set_alert_button()
        with sell_column:
            set_conditional_trade_button('sell')






@st.fragment(run_every = constants.POLLING_INTERVAL)
def print_prices_test():
    bars = st.session_state['bars_data']
    bid, ask = bars.current_bid, bars.current_ask
    bcol, acol = st.columns([1, 1])
    with bcol:
        st.header(0 if bid is None else bid, text_alignment = 'center')
    with acol:
        st.header(0 if ask is None else ask, text_alignment = 'center')







































