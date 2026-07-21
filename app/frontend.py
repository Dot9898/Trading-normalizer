

import streamlit as st
from backend import initialize_MetaTrader
from constants import LABEL_SPACING
import widgets
from get_live_data import Graph_range
from graph import generate_graph_in_fragment
from callbacks import is_0930_to_1800, reload_table
from trades_data import load_trades_data
from alerts import load_alerts, alert_check
from data_table import update_data_table



from get_live_data import get_remaining_candle_time
from constants import POLLING_INTERVAL
@st.fragment(run_every = POLLING_INTERVAL)
def print_remaining_time_test():
    st.subheader(get_remaining_candle_time(st.session_state['bars_data'].timeframe), text_alignment = 'center')




def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)



#---
graph_colors = 'black_and_white'
#---



st.set_page_config(layout = 'wide')

if 'mt5_initialized' not in st.session_state:
    st.session_state['mt5_initialized'] = initialize_MetaTrader()
if 'trades_data' not in st.session_state:
    load_trades_data()
if 'alerts' not in st.session_state:
    load_alerts()
if 'data_table' not in st.session_state:
    st.session_state['data_table'] = None
if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True
if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True
if 'reload_table' not in st.session_state:
    st.session_state['reload_table'] = True
if 'selected_scale' not in st.session_state:
    st.session_state['selected_scale'] = 'normalized'
if 'selected_normalization_base_name' not in st.session_state:
    st.session_state['selected_normalization_base_name'] = 'market_open' if is_0930_to_1800() else 'server_1:00'
if 'extra_shift' not in st.session_state:
    st.session_state['extra_shift'] = 0
if 'extra_shift_unit' not in st.session_state:
    st.session_state['extra_shift_unit'] = 'hours'
if 'custom_y_range' not in st.session_state:
    st.session_state['custom_y_range'] = False
if 'risk' not in st.session_state:
    st.session_state['risk'] = 0
if 'reward' not in st.session_state:
    st.session_state['reward'] = 0





graph_column, trade_column = st.columns(2)

with trade_column:

    orders_column, info_column = st.columns(2)

    with orders_column:
        widgets.symbol_dropdown()

with graph_column:
    
    timezone_column, timeframe_column, scale_column, zero_column = st.columns(4)
    with timezone_column:
        widgets.timezone_dropdown()
    with timeframe_column:
        widgets.timeframe_dropdown()
    with scale_column:
        widgets.scale_dropdown()
    if st.session_state['selected_scale'] == 'normalized':
        with zero_column:
            widgets.normalization_base_name_dropdown()

    graph_spot = st.container()

    precise_range_control_column, basic_range_control_column = st.columns(2)

    with precise_range_control_column:
        from_column, to_column = st.columns(2)
        with from_column:
            widgets.X_range_widgets('first_bar')
        with to_column:
            widgets.X_range_widgets('last_bar')
        widgets.Y_range_widgets()
    
    with basic_range_control_column:
        add_vertical_spacing(LABEL_SPACING)
        X_navigation_column, Y_navigation_column = st.columns(2)
        with X_navigation_column:
            widgets.X_navigation_buttons()
        with Y_navigation_column:
            widgets.Y_navigation_buttons()
        widgets.zoom_buttons()


with info_column:
    risk_spot = st.container()
    widgets.RR_and_maxloss_widgets()




##########Frontend done until here


with graph_spot:

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

#############


    
with orders_column:
    prices_container = st.container()
    with prices_container:
        widgets.print_prices_test()
    widgets.market_order_buttons()
    widgets.SL_and_TP_input()
    widgets.limit_order_buttons()
    widgets.entry_display()

with risk_spot:
    
    if st.session_state['selected_scale'] == 'absolute':
        pppt_column, lotsize_column, max_lotsize_column = st.columns(3)
        with pppt_column:
            widgets.pppt_display()
        with lotsize_column:
            widgets.lotsize_display()
        with max_lotsize_column:
            widgets.max_lotsize_display()

    if st.session_state['selected_scale'] == 'normalized':
        ppb_column, max_ppb_column = st.columns(2)
        with ppb_column:
            widgets.ppb_display()
        with max_ppb_column:
            widgets.max_ppb_display()
    
    if st.session_state['selected_scale'] == 'logarithmic':
        lotsize_column, max_lotsize_column = st.columns(2)
        with lotsize_column:
            widgets.lotsize_display()
        with max_lotsize_column:
            widgets.max_lotsize_display()

with info_column:
    widgets.conditionals_and_account_data_checkboxes()
    widgets.conditional_operations_widgets()
    

with info_column:
    st.header('')
    print_remaining_time_test()
    

with trade_column:
    widgets.basic_data_table()
    st.write(st.session_state['alerts'])




if st.session_state['first_run']:
    update_data_table(full_update = True)
    st.session_state['first_run'] = False
    st.rerun()








import MetaTrader5 as mt5
from order_execution import change_SLTP_open, market_order, close_position, delete_pending_order, change_price_and_SLTP_pending, limit_or_stop_order
from get_live_data import get_current_server_time
from trades_data import update_all_trades_data
def lmocallback():
    #st.session_state['order_return'] = market_order('BTCUSD', 0.01, 'buy', TP = 79000)
    #st.session_state['order_return'] = change_SLTP_open(304969852, TP = 80000)
    #st.session_state['order_return'] = limit_or_stop_order('BTCUSD', 0.01, 'buy', 5000, TP = 200000)
    #st.session_state['order_return'] = change_price_and_SLTP_pending(304970240, execution_price = 4000, TP = 30000)
    #st.session_state['order_return'] = delete_pending_order(304969813)
    #st.session_state['order_return'] = close_position(304969852)
    pass

st.button('reload table', 
          on_click = reload_table)

st.button('LIMIT ORDER TEST', 
          on_click = lmocallback)

if 'order_return' in st.session_state:
    st.write(st.session_state['order_return'])

current_time = get_current_server_time()
ord = mt5.orders_get()
pos = mt5.positions_get()
hord = mt5.history_orders_get(current_time - 300, current_time)
hdls = mt5.history_deals_get(current_time - 300, current_time)
st.write('orders')
for i in ord:
    st.write(i)
st.write('positions')
for i in pos:
    st.write(i)
st.write('orders history')
for i in hord:
    st.write(i)
st.write('deals history')
for i in hdls:
    st.write(i)

st.button('UPDATE DATA TEST', 
          on_click = update_all_trades_data, 
          args = [get_current_server_time() - 600])



