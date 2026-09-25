

import streamlit as st
from callbacks import reload_graph, save_old_SLTP_then_update, reload_table




#Save them in a file and load them from there
def load_settings():
    if 'settings' not in st.session_state:
        st.session_state['settings'] = {'empty_graph_percent': 15, 
                                        'SL_deviation': -0.15, 
                                        'TP_deviation': 0.3, 
                                        'default_y_range': 0.5, 
                                        'force_default_y_range': False, 
                                        'show_hidden_trades': False, 
                                        'show_account_balance': False, 
                                        'graph_width': 50}

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

def default_SL_TP_deviation():
    SL_col, TP_col = st.columns(2)

    with SL_col:
        key = 'SL_deviation'
        st.number_input('Default SL deviation (%)', 
                        key = key, 
                        value = st.session_state['settings'][key], 
                        step = 0.05, 
                        min_value = -100.0, 
                        max_value = 100.0, 
                        on_change = update_setting, 
                        args = [key, save_old_SLTP_then_update, [True]])

    with TP_col:
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
                args = [key])

def default_y_range_input():
    key = 'default_y_range'
    st.number_input('Default Y range (%)', 
                    key = key, 
                    value = st.session_state['settings'][key], 
                    step = 0.05, 
                    min_value = float(0), 
                    max_value = 100.0, 
                    on_change = update_setting, 
                    args = [key])

def show_hidden_trades_checkbox():
    key = 'show_hidden_trades'
    st.checkbox('Show hidden trades', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key, reload_table])

def show_account_balance_checkbox():
    key = 'show_account_balance'
    st.checkbox('Show account balance', 
                key = key, 
                value = st.session_state['settings'][key], 
                on_change = update_setting, 
                args = [key])

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




@st.dialog(' ', width = 'medium', dismissible = True, on_dismiss = 'rerun')
def open_settings():
    st.header('Settings', text_alignment = 'center')
    with st.columns(2)[0]:
        graph_empty_space_input()
        default_SL_TP_deviation()
        force_default_y_range_checkbox()
        if st.session_state['force_default_y_range']:
            default_y_range_input()
        show_hidden_trades_checkbox()
        show_account_balance_checkbox()
        graph_width_input()

    
