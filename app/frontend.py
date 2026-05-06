

import streamlit as st
import MetaTrader5 as mt5
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
timeframe = mt5.TIMEFRAME_M1
left_shift_hours = 0
range_type = 'date'
range = 'server_open'
graph_colors = 'black_and_white'
data_scale = None
#---


columns = st.columns([1, 1])
with columns[1]:
    st.selectbox('Time zone', 
                 ['Chile', 'NY', 'server', 'France'], 
                 key = 'selected_timezone', 
                 index = 0, 
                 format_func = lambda timezone: TIMEZONE_LABEL[timezone], 
                 on_change = reload_graph)
with columns[0]:
    generate_graph_in_fragment(symbol = symbol, 
                               timeframe = timeframe, 
                               left_shift_hours = left_shift_hours, 
                               range_type = range_type, 
                               range = range, 
                               timezone = st.session_state['selected_timezone'], 
                               data_scale = data_scale, 
                               graph_colors = graph_colors)

with columns[1]:
    with st.columns([1, 1])[0]:
        print_prices_test()
    
    from get_live_data import Bars
    bars: Bars = st.session_state['bars_data']
    bells = bars.get_server_times_of_interest(0)
    ts_op = bars.get_actual_timestamp(bells['market_open'])
    ts_cl = bars.get_actual_timestamp(bells['market_close'])
    ts_sv = bars.get_actual_timestamp(bells['server_open'])
    from datetime import datetime
    from constants import TIMEZONES
    op = datetime.fromtimestamp(ts_op, tz = TIMEZONES['NY'])
    cl = datetime.fromtimestamp(ts_cl, tz = TIMEZONES['NY'])
    sv = datetime.fromtimestamp(ts_sv, tz = TIMEZONES['NY'])
    st.write(op)
    st.write(cl)
    st.write(sv)


















