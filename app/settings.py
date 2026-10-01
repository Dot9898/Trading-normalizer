

import pandas as pd
import streamlit as st

from callbacks import (reload_graph, save_old_SLTP_then_update, reload_table, 
                       set_closed_trades_history_visibility, update_y_range_checkbox)
from constants import DATA_PATH, DEFAULT_SETTINGS


def load_settings():
    settings_path = DATA_PATH / 'settings.csv'
    if not settings_path.exists():
        settings = DEFAULT_SETTINGS.copy()
    else:
        settings = pd.read_csv(settings_path).iloc[0].to_dict()
    st.session_state['settings'] = settings

def save_settings_to_file():
    settings_path = DATA_PATH / 'settings.csv'
    settings = st.session_state['settings']
    pd.DataFrame([settings]).to_csv(settings_path, index = False)
    st.rerun()

def update_setting(key, callback = None, args = []):
    new_value = st.session_state[key]
    st.session_state['settings'][key] = new_value
    if callback is not None:
        callback(*args)


def graph_empty_space_input():
    key = 'empty_graph_percent'
    st.number_input('Empty graph space (%)', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 5, 
                    min_value = 0, 
                    max_value = 100, 
                    on_change = update_setting, 
                    args = [key, reload_graph])

def default_SL_deviation():
    key = 'SL_deviation'
    st.number_input('Default SL deviation (%)', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 0.05, 
                    min_value = -100.0, 
                    max_value = 100.0, 
                    on_change = update_setting, 
                    args = [key, save_old_SLTP_then_update, [True]])

def default_TP_deviation():
    key = 'TP_deviation'
    st.number_input('Default TP deviation (%)', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 0.05, 
                    min_value = -100.0, 
                    max_value = 100.0, 
                    on_change = update_setting, 
                    args = [key, save_old_SLTP_then_update, [True]])

def force_default_y_range_checkbox():
    key = 'force_default_y_range'
    st.checkbox('Force default Y range', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key, update_y_range_checkbox], 
                wrap = True)

def default_y_range_input():
    key = 'default_y_range'
    disabled = not st.session_state['settings']['force_default_y_range']
    st.number_input('Default Y range (%)', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 0.05, 
                    min_value = float(0), 
                    max_value = 100.0, 
                    disabled = disabled, 
                    on_change = update_setting, 
                    args = [key])

def show_hidden_trades_checkbox():
    key = 'show_hidden_trades'
    st.checkbox('Show hidden trades', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key, reload_table], 
                wrap = True)

def show_account_balance_checkbox():
    key = 'show_account_balance'
    st.checkbox('Show account balance', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key], 
                wrap = True)

def graph_width_input():
    key = 'graph_width'
    st.number_input('Graph portion of the screen (%)', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 5, 
                    min_value = 25, 
                    max_value = 65, 
                    on_change = update_setting, 
                    args = [key])

def max_closed_trades_input():
    key = 'max_closed_trades_shown'
    st.number_input('Max number of closed trades shown', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 1, 
                    min_value = 0, 
                    max_value = 300, 
                    on_change = update_setting, 
                    args = [key, reload_table])

def show_order_types_checkbox():
    key = 'show_order_types'
    st.checkbox('Show order type of closed trades', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key, reload_table], 
                wrap = True)

def show_trade_history_checkbox():
    key = 'show_trade_history'
    st.checkbox('Show closed trades on the chart', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key, set_closed_trades_history_visibility], 
                wrap = True)


@st.dialog(' ', width = 'medium', dismissible = True, on_dismiss = save_settings_to_file)
def open_settings():
    st.header('Settings', text_alignment = 'center')
    st.subheader('')
    settings_columns = st.columns(3)
    with settings_columns[0]:
        graph_width_input()
        default_SL_deviation()
        show_hidden_trades_checkbox()
        show_account_balance_checkbox()
    with settings_columns[1]:
        graph_empty_space_input()
        default_TP_deviation()
        show_trade_history_checkbox()
        show_order_types_checkbox()
    with settings_columns[2]:
        max_closed_trades_input()
        default_y_range_input()
        force_default_y_range_checkbox()
    st.subheader('')



