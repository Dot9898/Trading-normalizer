

import streamlit as st
from graph import generate_graph_in_fragment
import MetaTrader5 as mt5


st.set_page_config(layout = 'wide')

if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True


update_delay = 0.5
symbol = 'US500'
timeframe = mt5.TIMEFRAME_M5
left_shift_hours = 0
range_in_hours = 4 #13.5
graph_colors = 'black_and_white'


columns = st.columns([1, 1])
with columns[0]:
    generate_graph_in_fragment(symbol, timeframe, left_shift_hours, range_in_hours, graph_colors)
with columns[1]:
    st.text_input('test')




















