

import streamlit as st
from constants import LABEL_SPACING
import widgets
from get_live_data import Graph_range, is_dst
from graph import generate_graph_in_fragment
from callbacks import is_0930_to_1800



from get_live_data import get_remaining_candle_time
from constants import POLLING_INTERVAL
@st.fragment(run_every = POLLING_INTERVAL)
def print_remaining_time_test():
    st.subheader(get_remaining_candle_time(st.session_state['bars_data'].timeframe, st.session_state['is_dst']), text_alignment = 'center')




def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)



#---
graph_colors = 'black_and_white'
#---



st.set_page_config(layout = 'wide')

if 'bars_data' not in st.session_state:
    st.session_state['bars_data'] = None
if 'reload_Bars' not in st.session_state:
    st.session_state['reload_Bars'] = True
if 'is_dst' not in st.session_state:
    st.session_state['is_dst'] = is_dst()
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
    st.header('')
    print_remaining_time_test()
    


from order_execution import limit_or_stop_order
def lmocallback():
    st.session_state['order_return'] = limit_or_stop_order('US500', 0.1, 'buy', execution_price = 7900.0, TP = 8000)

st.button('LIMIT ORDER TEST', 
          on_click = lmocallback)
if 'order_return' in st.session_state:
    st.write(st.session_state['order_return'])





