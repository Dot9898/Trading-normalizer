

import streamlit as st
import MetaTrader5 as mt5
from get_live_data import Graph_range
from graph import generate_graph_in_fragment
from constants import TIMEZONE_LABEL, TIMEFRAMES, TIMEFRAME_LABEL, POLLING_INTERVAL


def reload_graph(): #Callback
    st.session_state['reload_Bars'] = True

@st.fragment(run_every = POLLING_INTERVAL)
def print_prices_test():
    bars = st.session_state['bars_data']
    bid, ask = bars.current_bid, bars.current_ask
    bcol, acol = st.columns([1, 1])
    with bcol:
        st.header(bid, text_alignment = 'center')
    with acol:
        st.header(ask, text_alignment = 'center')

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

def generate_range_widgets(what_widgets):

    if what_widgets == 'first_bar':
        st.selectbox('from', 
                    ['now', 'market_open', 'market_close', 'server_1:00'], 
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
                        ['hours', 'days', 'bars'], 
                        key = 'left_shift_unit', 
                        on_change = reload_graph)
    
    if what_widgets == 'last_bar':
        st.selectbox('to', 
                    ['now', 'market_open', 'market_close', 'server_1:00'], 
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
                        ['hours', 'days', 'bars'], 
                        key = 'right_shift_unit', 
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
                        ['hours', 'days', 'bars'], 
                        key = 'extra_shift_unit', 
                        on_change = reload_graph)



st.set_page_config(layout = 'wide')

if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True



#---
symbol = 'US500'
graph_colors = 'black_and_white'
data_scale = 'normalized'
normalization_base_name = 'now'
#---

graph_column, widgets_column = st.columns([1, 1])

with widgets_column:
    left_widgets_column, right_widgets_column = st.columns([1, 1])

    with left_widgets_column:
        generate_timezone_dropdown()
        generate_range_widgets('first_bar')
    with right_widgets_column:
        generate_timeframe_dropdown()
        generate_range_widgets('last_bar')
        generate_range_widgets('shift')

    
with graph_column:

    graph_range = Graph_range(first_bar = st.session_state['first_bar'], 
                              left_shift = st.session_state['left_shift'], 
                              left_shift_unit = st.session_state['left_shift_unit'], 
                              last_bar = st.session_state['last_bar'], 
                              right_shift = st.session_state['right_shift'], 
                              right_shift_unit = st.session_state['right_shift_unit'], 
                              extra_shift = st.session_state['extra_shift'], 
                              extra_shift_unit = st.session_state['extra_shift_unit'])
    
    generate_graph_in_fragment(symbol = symbol, 
                               timeframe = st.session_state['selected_timeframe'], 
                               graph_range = graph_range, 
                               timezone = st.session_state['selected_timezone'], 
                               data_scale = data_scale, 
                               graph_colors = graph_colors, 
                               normalization_base_name = normalization_base_name)

with left_widgets_column:
    print_prices_test()
    


















