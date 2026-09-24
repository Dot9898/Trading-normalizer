

import streamlit as st
from callbacks import reload_graph
#from constants import SHOWN_ACTIONS_DATA_COLUMNS, ERROR_CODE_TO_DETAILS
#from backend import scale_point_wrt_current_values



#Save them in a file and load them from there
def load_settings():
    if 'settings' not in st.session_state:
        st.session_state['settings'] = {'empty_graph_percent': 15}

def update_setting(key, callback):
    new_value = st.session_state[f'setting_{key}']
    st.session_state['settings'][key] = new_value
    callback()

def graph_empty_space_input():
    value = st.session_state['settings']['empty_graph_percent']
    st.number_input('Empty graph space (%)', 
                    key = 'setting_empty_graph_percent', 
                    value = value, 
                    step = 5, 
                    min_value = 0, 
                    max_value = 100, 
                    on_change = update_setting, 
                    args = ['empty_graph_percent', reload_graph])


@st.dialog(' ', width = 'medium', dismissible = True, on_dismiss = 'rerun')
def open_settings():
    st.header('Settings', text_alignment = 'center')
    with st.columns(4)[0]:
        graph_empty_space_input()


    #two columns?
    
