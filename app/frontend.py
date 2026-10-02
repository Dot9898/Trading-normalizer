

import streamlit as st

import widgets
from alerts import load_alerts
from backend import init_session_state, init_session_state_functions, initialize_MetaTrader
from callbacks import (set_normalization_base, set_session_first_bar, save_old_SLTP_then_update, 
                       set_closed_trades_history_visibility, is_friday)
from constants import SESSION_STATE_DEFAULTS, LABEL_SPACING_FOR_BUTTON, LABEL_SPACING_FOR_CHECKBOX
from format_functions import add_vertical_spacing
from graph import Layers
from settings import load_settings
from style import set_style
from trades_data import load_trades_data, get_last_backup_time

SESSION_STATE_DEFAULT_FUNCTIONS = {'mt5_initialized': {'function': initialize_MetaTrader, 
                                                       'assign': True, 
                                                       'value': 'return_value'}, 
                                   'settings': {'function': load_settings, 
                                                'assign': False}, 
                                   'last_backup_timestamp': {'function': get_last_backup_time, 
                                                             'assign': True, 
                                                             'value': 'return_value'}, 
                                   'trades_data': {'function': load_trades_data, 
                                                   'assign': False}, 
                                   'alerts': {'function': load_alerts, 
                                              'assign': False}, 
                                   'graph_layers': {'function': Layers, 
                                                    'assign': True, 
                                                    'value': 'return_value'}, 
                                   'selected_normalization_base_name': {'function': set_normalization_base, 
                                                                        'assign': False}, 
                                   'first_bar': {'function': set_session_first_bar, 
                                                 'assign': False}, 
                                   'custom_y_range': {'function': lambda: st.session_state['settings']['force_default_y_range'], 
                                                      'assign': True, 
                                                      'value': 'return_value'}}


st.set_page_config(layout = 'wide')
set_style()

init_session_state_functions(SESSION_STATE_DEFAULT_FUNCTIONS)
init_session_state(SESSION_STATE_DEFAULTS)

graph_width = st.session_state['settings']['graph_width']
graph_column, trade_column = st.columns([graph_width, 100 - graph_width])

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
        add_vertical_spacing(LABEL_SPACING_FOR_BUTTON)
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
        widgets.SL_TP_inputs_and_button()
        widgets.entry_display()
        widgets.market_order_buttons()
        widgets.limit_order_buttons()

    with risk_column:
        
        if st.session_state['selected_scale'] == 'absolute':
            risk_subcolumns = st.columns(4, vertical_alignment = 'bottom')
            with risk_subcolumns[0]:
                widgets.pppt_display()
            with risk_subcolumns[1]:
                widgets.lotsize_display()
            with risk_subcolumns[2]:
                widgets.max_lotsize_display()
            with risk_subcolumns[3]:
                widgets.settings_button()

        if st.session_state['selected_scale'] == 'normalized':
            risk_subcolumns = st.columns([2, 1, 1], vertical_alignment = 'bottom')
            with risk_subcolumns[0]:
                widgets.ppb_display()
            with risk_subcolumns[1]:
                widgets.max_ppb_display()
            with risk_subcolumns[2]:
                widgets.settings_button()
        
        if st.session_state['selected_scale'] == 'logarithmic':
            risk_subcolumns = st.columns(2, vertical_alignment = 'bottom')
            with risk_subcolumns[0]:
                widgets.lotsize_display()
            with risk_subcolumns[1]:
                widgets.settings_button()

        widgets.RR_and_maxloss_widgets()
        if st.session_state['alerts_checkbox']:
            widgets.alerts_and_conditional_trades_widgets()
        else:
            add_vertical_spacing(LABEL_SPACING_FOR_CHECKBOX)
        widgets.alert_and_account_checkboxes()
        if st.session_state['account_data_checkbox']:
            widgets.account_data_info()

    widgets.data_table()

widgets.update_trades_data()
if st.session_state['dialog_data'] is not None:
    widgets.open_dialog()

if st.session_state['first_run']:
    save_old_SLTP_then_update(reset = True)
    set_closed_trades_history_visibility()
    if is_friday():
        st.session_state['dialog_data'] = {'reason': 'backup'}
    st.session_state['first_run'] = False
    st.rerun()

