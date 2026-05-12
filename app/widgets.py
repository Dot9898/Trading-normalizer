

import streamlit as st
import constants
import format_functions
import callbacks
from numpy import log10
from get_live_data import get_remaining_candle_time


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
                on_change = callbacks.reload_graph)

def normalization_base_name_dropdown():
    st.selectbox('Zero', 
                constants.NORMALIZATION_BASES, 
                key = 'selected_normalization_base_name', 
                index = 0, 
                format_func = lambda name: name.capitalize().replace('_', ' '), 
                on_change = callbacks.reload_graph)


def X_range_widgets(what_widgets):

    if what_widgets == 'first_bar':
        st.selectbox('From', 
                    constants.INTERESTING_TIMES, 
                    key = 'first_bar', 
                    index = 1, 
                    format_func = lambda name: name.capitalize().replace('_', ' '), 
                    on_change = callbacks.reload_graph)
        
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
                    on_change = callbacks.reload_graph)
        
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

    display = (constants.NORMALIZATION_DATA[st.session_state['selected_symbol']]['display'] if 
               st.session_state['selected_symbol'] in constants.NORMALIZATION_DATA else 
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



def get_SLTP_step():
    if st.session_state['selected_scale'] == 'logarithmic':
        step = 0.00001
    
    elif st.session_state['selected_scale'] == 'normalized':
        display = (constants.NORMALIZATION_DATA[st.session_state['selected_symbol']]['display'] 
                   if st.session_state['selected_symbol'] in constants.NORMALIZATION_DATA 
                   else constants.DEFAULTS['display'])
        step = 0.1 if display == 'basis' else 0.01
    
    elif st.session_state['selected_scale'] == 'absolute':
        step = st.session_state['bars_data'].digits

    return(float(step))

def SL_and_TP_input():
    bid = 0 if st.session_state['bars_data'] is None else st.session_state['bars_data']
    step = get_SLTP_step()
    SL_column, TP_column = st.columns([1, 1])

    with SL_column:
        st.number_input('SL', 
                        key = 'chosen_SL', 
                        value = bid, 
                        step = step, 
                        on_change = callbacks.reload_graph)
    
    with TP_column:
        st.number_input('Top', 
                        key = 'chosen_TP', 
                        value = bid, 
                        step = step, 
                        on_change = callbacks.reload_graph)

def RR_widgets():
    st.selectbox('RR ratio', 
                constants.RR, 
                key = 'selected_rr', 
                index = 2, 
                format_func = format_functions.RR_format, 
                on_change = callbacks.reload_graph)
    
    if st.session_state['selected_rr'] is not None: #Make this a callback
        st.session_state['chosen_risk'] = st.session_state['selected_rr'][0]
        st.session_state['chosen_risk'] = st.session_state['selected_rr'][1]
    
    else:
        risk_column, reward_column = st.columns([1, 1])
        
        with risk_column:
            st.number_input('Risk', 
                            key = 'chosen_risk', 
                            value = 1, 
                            step = 0.1, 
                            on_change = reload_graph)
        
        with reward_column:
            st.number_input('Reward', 
                            key = 'chosen_reward', 
                            value = 1, 
                            step = 0.1, 
                            on_change = reload_graph)
    
def max_loss_input():
    st.number_input('Max loss', 
                    key = 'chosen_maxloss', 
                    value = 10, 
                    step = 0.5, 
                    on_change = callbacks.reload_graph)


@st.fragment(run_every = constants.POLLING_INTERVAL)
def print_prices_test():
    bars = st.session_state['bars_data']
    bid, ask = bars.current_bid, bars.current_ask
    bcol, acol = st.columns([1, 1])
    with bcol:
        st.header(0 if bid is None else bid, text_alignment = 'center')
    with acol:
        st.header(0 if ask is None else ask, text_alignment = 'center')
    
    st.subheader(get_remaining_candle_time(bars.timeframe, st.session_state['is_dst']), text_alignment = 'center')













































