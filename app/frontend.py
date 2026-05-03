

from time import sleep
import streamlit as st
from graph import generate_graph
import MetaTrader5 as mt5
from get_live_data import Bars


st.set_page_config(layout = 'wide')

update_delay = 0.5
symbol = 'BTCUSD' #weekend test
timeframe = mt5.TIMEFRAME_M5
left_shift_hours = 0
range_in_hours = 12 #13.5
graph_colors = 'black_and_white'

if 'bars' not in st.session_state:
    st.session_state['bars'] = Bars(symbol, timeframe, range_in_hours, left_shift_hours)

st.session_state['bars'].update()
bars = st.session_state['bars'].bars
current_prices = (st.session_state['bars'].current_bid, st.session_state['bars'].current_ask)
graph = generate_graph(bars, colors = graph_colors, timeframe = timeframe, current_prices = current_prices)
st.altair_chart(graph, width = 'stretch')#, height = GRAPH_HEIGHT)#, key = 'Gráfico')
st.write(bars.iloc[::-1])
sleep(update_delay)

st.rerun()



















