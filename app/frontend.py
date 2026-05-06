

import streamlit as st
import MetaTrader5 as mt5
from get_live_data import Graph_range
from graph import generate_graph_in_fragment
from constants import TIMEZONE_LABEL, POLLING_INTERVAL


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



st.set_page_config(layout = 'wide')

if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True


#---
update_delay = 0.5
symbol = 'US500'
timeframe = mt5.TIMEFRAME_M5
left_shift_hours = 0
range_type = 'date'
range = 'server_open'
graph_colors = 'black_and_white'
data_scale = None
#---
first_bar_type = 'absolute'
first_bar = 'market_open'
last_bar_type = 'absolute'
last_bar = 'now'
shift_type = 'shift_hours'
shift = 0
fixed = False


columns = st.columns([1, 1])
with columns[1]:
    st.selectbox('Time zone', 
                ['Chile', 'NY', 'server', 'France'], 
                key = 'selected_timezone', 
                index = 0, 
                format_func = lambda timezone: TIMEZONE_LABEL[timezone], 
                on_change = reload_graph)
    
    coltest = st.columns([2, 1, 1])
    with coltest[1]:
        st.selectbox('from', 
                    ['now', 'market_open', 'market_close', 'server_open', 'shift_hours', 'shift_days'], 
                    key = 'first_bar_type', 
                    index = 1, 
                    on_change = reload_graph)
        st.number_input('first bar shift', 
                        key = 'first_bar_shift', 
                        step = 1, 
                        on_change = reload_graph)
    with coltest[2]:
        st.selectbox('to', 
                    ['now', 'market_open', 'market_close', 'server_open', 'shift_hours', 'shift_days'], 
                    key = 'last_bar_type', 
                    on_change = reload_graph)
        st.number_input('last bar shift', 
                        key = 'last_bar_shift', 
                        step = 1, 
                        on_change = reload_graph)
    with coltest[1]:
        st.selectbox('extra shift', 
                    ['shift_hours', 'shift_days'], 
                    key = 'shift_type', 
                    on_change = reload_graph)
        st.number_input('qty', 
                        key = 'shift', 
                        step = 1, 
                        on_change = reload_graph)
    
    with coltest[2]:
        st.checkbox('fixed absolutes', 
                    key = 'fixed', 
                    on_change = reload_graph)


BAR_TYPES = {'now': 'absolute', 
             'market_open': 'absolute', 
             'market_close': 'absolute', 
             'server_open': 'absolute', 
             'shift_hours': 'shift_hours', 
             'shift_days': 'shift_days'}

with columns[0]:
    fb_type = BAR_TYPES[st.session_state['first_bar_type']]
    fb = st.session_state['first_bar_type'] if fb_type == 'absolute' else st.session_state['first_bar_shift']
    lb_type = BAR_TYPES[st.session_state['last_bar_type']]
    lb = st.session_state['last_bar_type'] if lb_type == 'absolute' else st.session_state['last_bar_shift']
    shift_type = st.session_state['shift_type']
    shift = st.session_state['shift']
    fixed = st.session_state['fixed']

    graph_range = Graph_range(first_bar_type = fb_type, 
                              first_bar = fb, 
                              last_bar_type = lb_type, 
                              last_bar = lb, 
                              shift_type = shift_type, 
                              shift = shift, 
                              fixed = fixed)
    
    generate_graph_in_fragment(symbol = symbol, 
                               timeframe = timeframe, 
                               graph_range = graph_range, 
                               timezone = st.session_state['selected_timezone'], 
                               data_scale = data_scale, 
                               graph_colors = graph_colors)

with coltest[0]:
    print_prices_test()
    
    


















