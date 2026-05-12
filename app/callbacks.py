

import streamlit as st
import constants

def reload_graph():
    st.session_state['reload_Bars'] = True

def goto(when):
    for key, setting in constants.ZOOM_FIXED_SETTINGS.items():
        st.session_state[key] = setting
    for key, settings_dict in constants.ZOOM_VARIABLE_SETTINGS.items():
        st.session_state[key] = settings_dict[when]
    reload_graph()

def X_shift(quantity):
    st.session_state['extra_shift'] += quantity
    reload_graph()

def Y_shift(quantity):
    
    st.session_state['custom_y_range'] = True
    
    if 'y_min' not in st.session_state:
        st.session_state['y_min'] = (0 if st.session_state['bars_data'].min_price is None 
                                     else st.session_state['bars_data'].min_price)
    
    if 'y_max' not in st.session_state:
        st.session_state['y_max'] = (100 if st.session_state['bars_data'].max_price is None 
                                     else st.session_state['bars_data'].max_price)
    
    st.session_state['y_min'] += quantity
    st.session_state['y_max'] += quantity

































