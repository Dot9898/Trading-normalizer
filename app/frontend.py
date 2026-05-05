

import streamlit as st
import MetaTrader5 as mt5
from graph import generate_graph_in_fragment
from constants import TIMEZONE_LABEL


def reload_graph(): #Callback
    st.session_state['reload_Bars'] = True


st.set_page_config(layout = 'wide')

if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True


update_delay = 0.5
symbol = 'US500'
timeframe = mt5.TIMEFRAME_M5
left_shift_hours = 9
range_in_hours = 4
graph_colors = 'black_and_white'
data_scale = None

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
                               range_in_hours = range_in_hours, 
                               timezone = st.session_state['selected_timezone'], 
                               data_scale = data_scale, 
                               graph_colors = graph_colors)





















