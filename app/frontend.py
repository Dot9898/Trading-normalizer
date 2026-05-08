

from numpy import log10
import streamlit as st
import MetaTrader5 as mt5
from get_live_data import Graph_range
from graph import generate_graph_in_fragment
from constants import TIMEZONE_LABEL, TIMEFRAMES, TIMEFRAME_LABEL, POLLING_INTERVAL, NORMALIZATION_DATA, DEFAULTS


def reload_graph(): #Callback
    st.session_state['reload_Bars'] = True

def get_y_step():
    if st.session_state['selected_scale'] == 'logarithmic':
        y_step = 0.2

    display = NORMALIZATION_DATA[st.session_state['selected_symbol']]['display'] if st.session_state['selected_symbol'] in NORMALIZATION_DATA else DEFAULTS['display']
    
    if st.session_state['selected_scale'] == 'normalized':
        y_step = 10 if display == 'basis' else 1
    
    if st.session_state['selected_scale'] == 'absolute':
        current_price = st.session_state['bars_data'].current_bid
        if current_price in [0, None]:
            y_step = 1
        else:
            digits = round(log10(abs(current_price))) - (3 if display == 'basis' else 2)
            y_step = 10 ** digits

    return(float(y_step))

def get_last_y_range():
    bottom = 0 if st.session_state['bars_data'].min_price is None else st.session_state['bars_data'].min_price
    top = 100 if st.session_state['bars_data'].max_price is None else st.session_state['bars_data'].max_price
    return(bottom, top)    

@st.fragment(run_every = POLLING_INTERVAL)
def print_prices_test():
    bars = st.session_state['bars_data']
    bid, ask = bars.current_bid, bars.current_ask
    bcol, acol = st.columns([1, 1])
    with bcol:
        st.header(0 if bid is None else bid, text_alignment = 'center')
    with acol:
        st.header(0 if ask is None else ask, text_alignment = 'center')

def generate_timezone_dropdown():
    st.selectbox('Time zone', 
                ['Chile', 'NY', 'server', 'France'], 
                key = 'selected_timezone', 
                format_func = lambda timezone: TIMEZONE_LABEL[timezone], 
                on_change = reload_graph)

def generate_timeframe_dropdown():
    st.selectbox('Time frame', 
                TIMEFRAMES, 
                key = 'selected_timeframe', 
                index = 1, 
                format_func = lambda timeframe: TIMEFRAME_LABEL[timeframe], 
                on_change = reload_graph)

def generate_scale_dropdown():
    st.selectbox('Scale', 
                ['absolute', 'normalized', 'logarithmic'], 
                key = 'selected_scale', 
                index = 1, 
                on_change = reload_graph)

def generate_normalization_base_name_dropdown():
    st.selectbox('Zero', 
                ['first_bar', 'market_open', 'market_close', 'server_1:00', 'now', 'last_bar'], 
                key = 'selected_normalization_base_name', 
                on_change = reload_graph)

def generate_X_range_widgets(what_widgets):

    if what_widgets == 'first_bar':
        st.selectbox('from', 
                    ['now', 'market_open', 'market_close', 'week_market_open', 'NY_day_start', 'NY_week_start', 'server_1:00', 'server_week_1:00'], 
                    key = 'first_bar', 
                    index = 1, 
                    on_change = reload_graph)
        
        shift_column, unit_column = st.columns([1, 1])
        with shift_column:
            st.number_input('first bar shift', 
                            key = 'left_shift', 
                            step = 1, 
                            on_change = reload_graph)
        with unit_column:
            st.selectbox('unit', 
                        ['bars', 'hours', 'days', 'weeks', 'months'], 
                        key = 'left_shift_unit', 
                        index = 1, 
                        on_change = reload_graph)
    
    if what_widgets == 'last_bar':
        st.selectbox('to', 
                    ['now', 'market_open', 'market_close', 'week_market_open', 'NY_day_start', 'NY_week_start', 'server_1:00', 'server_week_1:00'], 
                    key = 'last_bar', 
                    on_change = reload_graph)
        
        shift_column, unit_column = st.columns([1, 1])
        with shift_column:
            st.number_input('last bar shift', 
                            key = 'right_shift', 
                            step = 1, 
                            on_change = reload_graph)
        with unit_column:
            st.selectbox('unit', 
                        ['bars', 'hours', 'days', 'weeks', 'months'], 
                        key = 'right_shift_unit', 
                        index = 1, 
                        on_change = reload_graph)
    
    if what_widgets == 'shift':
        shift_column, unit_column = st.columns([1, 1])
        with shift_column:
            st.number_input('extra shift', 
                            key = 'extra_shift', 
                            step = 1, 
                            on_change = reload_graph)
        with unit_column:
            st.selectbox('unit', 
                        ['bars', 'hours', 'days', 'weeks', 'months'], 
                        key = 'extra_shift_unit', 
                        index = 1, 
                        on_change = reload_graph)

def generate_Y_range_widgets():
    st.checkbox('Custom Y range', 
                key = 'custom_y_range', 
                on_change = reload_graph)
    
    if st.session_state['custom_y_range']:
        bottom, top = get_last_y_range()
        
        left_column, right_column = st.columns([1, 1])
        with left_column:
            st.number_input('Bottom', 
                            key = 'y_min', 
                            value = bottom, 
                            step = get_y_step(), 
                            on_change = reload_graph)
        with right_column:
            st.number_input('Top', 
                            key = 'y_max', 
                            step = get_y_step(), 
                            value = top, 
                            on_change = reload_graph)



st.set_page_config(layout = 'wide')

if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True



#---
st.session_state['selected_symbol'] = 'US500'
graph_colors = 'black_and_white'
#---

graph_column, widgets_column = st.columns([1, 1])

with widgets_column:
    left_widgets_column, right_widgets_column = st.columns([1, 1])

    with left_widgets_column:
        leftmost_column, midleft_column = st.columns([1, 1])
    
        with leftmost_column:
            generate_timezone_dropdown()
        with midleft_column:
            generate_timeframe_dropdown()
        
        generate_X_range_widgets('first_bar')

    with right_widgets_column:
        midright_column, rightmost_column = st.columns([1, 1])

        with midright_column:
            generate_scale_dropdown()
        with rightmost_column:
            generate_normalization_base_name_dropdown()
        
        generate_X_range_widgets('last_bar')
        generate_X_range_widgets('shift')
        generate_Y_range_widgets()
        st.button('reload graph', 
                  width = 'stretch', 
                  on_click = reload_graph)
    

    
with graph_column:

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
                               graph_colors = graph_colors)

with left_widgets_column:
    print_prices_test()


    


















