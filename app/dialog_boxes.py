

import streamlit as st
from callbacks import execute_action_and_dismiss_dialog
from constants import SHOWN_ACTIONS_DATA_COLUMNS, ERROR_CODE_TO_DETAILS
from backend import scale_point_wrt_current_values


def get_data_row(ticket):
    if ticket in st.session_state['data_table'].index:
        data = st.session_state['data_table'].loc[ticket].copy()
        display_data = data.drop('source_object', errors = 'ignore')
        display_data = display_data.to_frame().T
    else:
        display_data = None
    return(display_data)

def unable_to_find_data_widgets():
    st.header('Unable to find this trade\'s data', text_alignment = 'center')
    st.subheader('')
    mid_column = st.columns(3)[1]
    with mid_column:
        st.button('Close', 
                    key = 'close_button', 
                    width = 'stretch', 
                    on_click = st.rerun)

@st.dialog(' ', width = 'medium', dismissible = False)
def erase_closed_trade(ticket):
    display_data = get_data_row(ticket)

    if display_data is None:   #Shouldn't ever happen for closed trades
        unable_to_find_data_widgets()

    else:
        st.header('This will permanently delete all the data of this trade', text_alignment = 'center')
        st.subheader('')
        st.dataframe(display_data, 
                    hide_index = True, 
                    column_order = SHOWN_ACTIONS_DATA_COLUMNS['erase'], 
                    placeholder = '-')
        st.write('')

        mid_column = st.columns([1, 4, 1])[1]
        with mid_column:
            left_col, right_col = st.columns(2)

            with left_col:
                st.button('Erase data', 
                        key = 'erase_button', 
                        width = 'stretch', 
                        on_click = execute_action_and_dismiss_dialog, 
                        args = ['erase', ticket])
            with right_col:
                st.button('Cancel', 
                        key = 'cancel_button', 
                        width = 'stretch', 
                        on_click = st.rerun)

@st.dialog(' ', width = 'medium', dismissible = False)
def edit_open_trade(ticket):
    display_data = get_data_row(ticket)

    if display_data is None:
        unable_to_find_data_widgets()

    else:
        trade_data = st.session_state['trades_data'].loc[ticket]
        current_SL_abs = trade_data['SL_abs']
        current_TP_abs = trade_data['TP_abs']
        current_SL = scale_point_wrt_current_values(current_SL_abs, rounded = True)
        current_TP = scale_point_wrt_current_values(current_TP_abs, rounded = True)
        display_data['Current SL'] = current_SL
        display_data['Current TP'] = current_TP

        st.header('Editing position', text_alignment = 'center')
        st.subheader('')
        st.dataframe(display_data, 
                    hide_index = True, 
                    column_order = SHOWN_ACTIONS_DATA_COLUMNS['edit'], 
                    placeholder = '-')
        st.write('')

        mid_column = st.columns([1, 4, 1])[1]
        with mid_column:
            left_col, right_col = st.columns(2)
            
        digits = st.session_state['bars_data'].shown_digits
        format = f'%0.{digits}f'
        with left_col:
            st.number_input('New SL', 
                            key = 'new_SL', 
                            value = st.session_state['SL'], 
                            format = format, 
                            disabled = True)
        with right_col:
            st.number_input('New TP', 
                            key = 'new_TP', 
                            value = st.session_state['TP'], 
                            format = format, 
                            disabled = True)

        with left_col:
            st.button('Confirm', 
                    key = 'edit_button', 
                    width = 'stretch', 
                    on_click = execute_action_and_dismiss_dialog, 
                    args = ['edit', ticket])
        with right_col:
            st.button('Cancel', 
                    key = 'cancel_button', 
                    width = 'stretch', 
                    on_click = st.rerun)

@st.dialog(' ', width = 'medium', dismissible = False)
def modify_pending_order(ticket):
    display_data = get_data_row(ticket)

    if display_data is None:
        unable_to_find_data_widgets()

    else:
        trade_data = st.session_state['trades_data'].loc[ticket]
        current_SL_abs = trade_data['SL_abs']
        current_TP_abs = trade_data['TP_abs']
        current_entry_abs = trade_data['set_price']
        current_SL = scale_point_wrt_current_values(current_SL_abs, rounded = True)
        current_TP = scale_point_wrt_current_values(current_TP_abs, rounded = True)
        current_entry = scale_point_wrt_current_values(current_entry_abs, rounded = True)
        display_data['Current SL'] = current_SL
        display_data['Current TP'] = current_TP
        display_data['Current entry'] = current_entry

        st.header('Modifying order', text_alignment = 'center')
        st.subheader('')
        st.dataframe(display_data, 
                    hide_index = True, 
                    column_order = SHOWN_ACTIONS_DATA_COLUMNS['modify'], 
                    placeholder = '-')
        st.write('')

        mid_column = st.columns([1, 4, 1])[1]
        with mid_column:
            left_col, center_col, right_col = st.columns(3)
            
        digits = st.session_state['bars_data'].shown_digits
        format = f'%0.{digits}f'
        with left_col:
            st.number_input('New SL', 
                            key = 'new_SL', 
                            value = st.session_state['SL'], 
                            format = format, 
                            disabled = True)
        with center_col:
            st.number_input('New entry', 
                            key = 'new_entry', 
                            value = st.session_state['entry'], 
                            disabled = True)
        with right_col:
            st.number_input('New TP', 
                            key = 'new_TP', 
                            value = st.session_state['TP'], 
                            format = format, 
                            disabled = True)

        with mid_column:
            left_col, right_col = st.columns(2)
        with left_col:
            st.button('Confirm', 
                    key = 'edit_button', 
                    width = 'stretch', 
                    on_click = execute_action_and_dismiss_dialog, 
                    args = ['modify', ticket])
        with right_col:
            st.button('Cancel', 
                    key = 'cancel_button', 
                    width = 'stretch', 
                    on_click = st.rerun)

@st.dialog(' ', width = 'medium', dismissible = True)
def success():
    st.header('Request executed', text_alignment = 'center')
    st.subheader('')

@st.dialog(' ', width = 'medium', dismissible = True)
def not_found():
    st.header('This position or order can\'t be found in the server', text_alignment = 'center')
    st.subheader('The most likely reason is that its status has changed', text_alignment = 'center')
    st.subheader('')

@st.dialog(' ', width = 'medium', dismissible = True)
def error(error_code):
    st.header('The request has been sent to the server, but it hasn\'t been executed due to the following error:', text_alignment = 'center')
    st.subheader(ERROR_CODE_TO_DETAILS[error_code]['name'])
    st.write(ERROR_CODE_TO_DETAILS[error_code]['description'])
    st.subheader('')













def fake():
    if False:
        @st.dialog(ALERT_REASON_TEXT[self.reason], width = 'medium', on_dismiss = set_dialog_closed)
        def notification_dialog(reason):
            st.session_state['dialog_open'] = True
            display_data = data.drop('source_object', errors = 'ignore')   #Object can't be converted by st.dataframe
            display_data = display_data.to_frame().T   #Cast the series to single colum df, take its transpose
            
            st.dataframe(display_data, 
                         hide_index = True, 
                         column_order = SHOWN_ALERTS_DATA_COLUMNS[reason], 
                         placeholder = '-')

        notification_dialog(self.reason)


