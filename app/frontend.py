

import streamlit as st
from constants import LABEL_SPACING
import widgets
from get_live_data import Graph_range, is_dst
from graph import generate_graph_in_fragment



from get_live_data import get_remaining_candle_time
from constants import POLLING_INTERVAL
@st.fragment(run_every = POLLING_INTERVAL)
def print_remaining_time_test():
    st.subheader(get_remaining_candle_time(st.session_state['bars_data'].timeframe, st.session_state['is_dst']), text_alignment = 'center')




def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)



#---
st.session_state['selected_symbol'] = 'US500'
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
    st.session_state['selected_normalization_base_name'] = 'first_bar'
if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True
if 'extra_shift' not in st.session_state:
    st.session_state['extra_shift'] = 0
if 'extra_shift_unit' not in st.session_state:
    st.session_state['extra_shift_unit'] = 'hours'
if 'custom_y_range' not in st.session_state:
    st.session_state['custom_y_range'] = False




graph_column, trade_column = st.columns(2)

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

    graph_spot = st.columns(1)[0]

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



with trade_column:

    orders_column, info_column = st.columns(2)
    
    with orders_column:
        widgets.RR_and_maxloss_widgets()
        prices_container = st.container()
        with prices_container:
            widgets.print_prices_test()
        widgets.market_order_buttons()
        widgets.SL_and_TP_input()
        widgets.limit_order_buttons()
        widgets.entry_display()

    with info_column:
        ppb_column, max_ppb_column = st.columns(2)
        with ppb_column:
            widgets.ppb_display()

        print_remaining_time_test()
    









if st.session_state['first_run']:
    st.session_state['first_run'] = False
    st.rerun()



#with graph_column:
    #from callbacks import reload_graph
    #st.button('reload graph', 
    #            width = 'stretch', 
    #            on_click = reload_graph)

###########












