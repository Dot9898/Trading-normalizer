

import streamlit as st
from backend import init_session_state, init_session_state_functions, initialize_MetaTrader
from constants import SESSION_STATE_DEFAULTS, LABEL_SPACING, MIN_LEFT_WIDTH, MIN_RIGHT_WIDTH
import widgets
from callbacks import reload_table, set_normalization_base, goto, save_old_SLTP_then_update
from format_functions import add_vertical_spacing
from trades_data import load_trades_data
from alerts import load_alerts
from graph import load_lines_data

SESSION_STATE_DEFAULT_FUNCTIONS = {'mt5_initialized': {'function': initialize_MetaTrader, 
                                                       'args': [], 
                                                       'assign': True, 
                                                       'value': 'return_value'}, 
                                   'first_run': {'function': goto, 
                                                 'args': ['now'], 
                                                 'assign': True, 
                                                 'value': True}, 
                                   'trades_data': {'function': load_trades_data, 
                                                   'args': [], 
                                                   'assign': False}, 
                                   'alerts': {'function': load_alerts, 
                                              'args': [], 
                                              'assign': False}, 
                                   'lines_data': {'function': load_lines_data, 
                                                  'args': [], 
                                                  'assign': False}, 
                                   'selected_normalization_base_name': {'function': set_normalization_base, 
                                                                        'args': [], 
                                                                        'assign': False}}



#---------------------------------------------------------------------------------------------------------
from get_live_data import get_remaining_candle_time
from constants import POLLING_INTERVAL
@st.fragment(run_every = POLLING_INTERVAL)
def print_remaining_time_test():
    st.subheader(get_remaining_candle_time(st.session_state['bars_data'].timeframe), text_alignment = 'center')

graph_width = 5
#---------------------------------------------------------------------------------------------------------



st.set_page_config(layout = 'wide')

init_session_state_functions(SESSION_STATE_DEFAULT_FUNCTIONS)
init_session_state(SESSION_STATE_DEFAULTS)


graph_column, trade_column = st.columns([MIN_LEFT_WIDTH + graph_width, MIN_RIGHT_WIDTH - graph_width])

with graph_column:

    upper_graph_subcolumns = st.columns(4)
    with upper_graph_subcolumns[0]:
        widgets.timezone_dropdown()
    with upper_graph_subcolumns[1]:
        widgets.timeframe_dropdown()
    with upper_graph_subcolumns[2]:
        widgets.scale_dropdown()
    if st.session_state['selected_scale'] == 'normalized':
        with upper_graph_subcolumns[3]:
            widgets.normalization_base_name_dropdown()

    graph_spot = st.container()

    range_control_column, range_buttons_column = st.columns(2)
    with range_control_column:
        range_subcolumns = st.columns(2)
        with range_subcolumns[0]:
            widgets.X_range_widgets('first_bar')
        with range_subcolumns[1]:
            widgets.X_range_widgets('last_bar')
        widgets.Y_range_widgets()
    with range_buttons_column:
        add_vertical_spacing(LABEL_SPACING)
        range_buttons_subcolumns = st.columns(2)
        with range_buttons_subcolumns[0]:
            widgets.X_navigation_buttons()
        with range_buttons_subcolumns[1]:
            widgets.Y_navigation_buttons()
        widgets.zoom_buttons()

    with graph_spot:
        widgets.generate_graph()

with trade_column:
    orders_column, risk_column = st.columns(2)

    with orders_column:
        widgets.symbol_dropdown()
        with st.container():
            widgets.print_prices_test()
        widgets.market_order_buttons() #add container if needed
        widgets.SL_and_TP_input()
        widgets.limit_order_buttons()
        widgets.entry_display()

    with risk_column:
        
        if st.session_state['selected_scale'] == 'absolute':
            risk_subcolumns = st.columns(3)
            with risk_subcolumns[0]:
                widgets.pppt_display()
            with risk_subcolumns[1]:
                widgets.lotsize_display()
            with risk_subcolumns[2]:
                widgets.max_lotsize_display()

        if st.session_state['selected_scale'] == 'normalized':
            risk_subcolumns = st.columns(2)
            with risk_subcolumns[0]:
                widgets.ppb_display()
            with risk_subcolumns[1]:
                widgets.max_ppb_display()
        
        if st.session_state['selected_scale'] == 'logarithmic':
            risk_subcolumns = st.columns(2)
            with risk_subcolumns[0]:
                widgets.lotsize_display()
            with risk_subcolumns[1]:
                widgets.max_lotsize_display()

        widgets.RR_and_maxloss_widgets()
        widgets.settings_checkboxes()
        if st.session_state['alerts_checkbox']:
            widgets.alerts_and_conditional_trades_widgets()
        if st.session_state['account_data_checkbox']:
            widgets.account_data_info()

        #else: ####delete after moving remaining time
        #    st.header('')
        print_remaining_time_test()

    widgets.data_table()

widgets.reload_table_and_lines_and_maxes()
if st.session_state['dialog_data'] is not None:
    widgets.open_dialog()

if st.session_state['first_run']:
    save_old_SLTP_then_update(reset = True)
    st.session_state['first_run'] = False
    st.rerun()





#---------------------------------------------------------------------------------------------






st.write('')
st.write('')
st.write('test')
st.write(f'dialog open {st.session_state['dialog_open']}')

st.write(f"Streamlit version: {st.__version__}")
st.write(st.session_state['alerts'])

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
    #st.session_state['order_return'] = close_position(325121823)
    pass
#mt5.positions_get(ticket = ticket)

st.button('reload table', 
          on_click = reload_table)

from callbacks import update_max_ppb_and_lotsize
st.button('update max ppb and lotsize', 
          on_click = update_max_ppb_and_lotsize)

if 'order_return' in st.session_state:
    st.write(st.session_state['order_return'])

current_time = get_current_server_time()
ord = mt5.orders_get()
pos = mt5.positions_get()
hord = mt5.history_orders_get(current_time - 120, current_time)
hdls = mt5.history_deals_get(current_time - 120, current_time)
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


