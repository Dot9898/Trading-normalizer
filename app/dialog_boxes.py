

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

def risk_display(show_percent):
    if show_percent:
        ppb_col, percent_col = st.columns(2)
    else:
        ppb_col = st.columns(1)[0]

    with ppb_col:
        if st.session_state['selected_scale'] == 'normalized':
            st.number_input('PPB', 
                            key = 'set_ppb', 
                            value = st.session_state['ppb'], 
                            step = 0.00001, 
                            format = '%0.2f', 
                            disabled = True)
        if st.session_state['selected_scale'] == 'absolute':
            st.number_input('PPPT', 
                key = 'set_pppt', 
                value = st.session_state['pppt'], 
                step = 0.00001, 
                format = '%0.2f', 
                disabled = True)

    if show_percent:
        with percent_col:
            st.number_input('Risk (%)', 
                            key = 'set_maxloss', 
                            value = st.session_state['maxloss'], 
                            step = 0.5, 
                            format = '%0.1f', 
                            disabled = True)

def SLTP_display(set_or_edit, with_entry):
    digits = st.session_state['bars_data'].shown_digits
    format = f'%0.{digits}f'

    if with_entry:
        left_col, mid_col, right_col = st.columns(3)
    else:
        left_col, right_col = st.columns(2)

    with left_col:
        st.number_input('SL' if set_or_edit == 'set' else 'New SL', 
                        key = 'set_SL', 
                        value = st.session_state['SL'], 
                        format = format, 
                        disabled = True)
    with right_col:
        st.number_input('TP' if set_or_edit == 'set' else 'New TP', 
                        key = 'set_TP', 
                        value = st.session_state['TP'], 
                        format = format, 
                        disabled = True)
    if with_entry:
        with mid_col:
            st.number_input('Open price' if set_or_edit == 'set' else 'New open price', 
                            key = 'set_entry', 
                            value = st.session_state['entry'], 
                            format = format, 
                            disabled = True)

def confirm_or_dismiss_buttons(confirm_button_label, reason, callback_kwargs):
    left_col, right_col = st.columns(2)

    with left_col:
        st.button(confirm_button_label, 
                key = 'confirm_button', 
                width = 'stretch', 
                on_click = execute_action_and_dismiss_dialog, 
                args = [reason],
                kwargs = callback_kwargs)
    with right_col:
        st.button('Cancel', 
                key = 'cancel_button', 
                width = 'stretch', 
                on_click = st.rerun)


@st.dialog(' ', width = 'medium', dismissible = False)
def place_order(reason, direction):
    if reason == 'open':
        title_text = f'Market {direction}'
        button_label = direction.capitalize()
        with_entry = False
        show_percent = False
    if reason == 'set':
        button_label = 'Set'
        title_text = f'Set {direction} order'
        with_entry = True
        show_percent = True

    st.header(title_text, text_alignment = 'center')
    st.subheader('')
    with st.columns([1, 4, 1])[1]:
        risk_display(show_percent = show_percent)
        SLTP_display(set_or_edit = 'set', with_entry = with_entry)
        st.write('')
        confirm_or_dismiss_buttons(confirm_button_label = button_label, 
                                   reason = reason, 
                                   callback_kwargs = {'direction': direction})
        st.subheader('')

@st.dialog(' ', width = 'medium', dismissible = False)
def modify_trade_data(reason, ticket):
    display_data = get_data_row(ticket)

    if display_data is None:   #Shouldn't ever happen for closed trades
        st.header('Unable to find this trade\'s data', text_alignment = 'center')
        st.subheader('')
        mid_column = st.columns(3)[1]
        with mid_column:
            st.button('Close', 
                      key = 'close_button', 
                      width = 'stretch', 
                      on_click = st.rerun)

    else:
        if reason in ['edit', 'modify']:
            trade_data = st.session_state['trades_data'].loc[ticket]
            current_SL_abs = trade_data['SL_abs']
            current_TP_abs = trade_data['TP_abs']
            current_SL = scale_point_wrt_current_values(current_SL_abs, rounded = True)
            current_TP = scale_point_wrt_current_values(current_TP_abs, rounded = True)
            display_data['Current SL'] = current_SL
            display_data['Current TP'] = current_TP
        if reason == 'modify':
            current_entry_abs = trade_data['set_price']
            current_entry = scale_point_wrt_current_values(current_entry_abs, rounded = True)
            display_data['Current entry'] = current_entry

        if reason == 'erase':
            title_text = 'This will permanently delete all the data of this trade'
            button_label = 'Erase data'
        if reason == 'edit':
            title_text = 'Editing position'
            button_label = 'Confirm'
        if reason == 'modify':
            title_text = 'Modifying order'
            button_label = 'Confirm'

        st.header(title_text, text_alignment = 'center')
        st.subheader('')

        st.dataframe(display_data, 
                    hide_index = True, 
                    column_order = SHOWN_ACTIONS_DATA_COLUMNS[reason], 
                    placeholder = '-')
        st.write('')

        with st.columns([1, 4, 1])[1]:
            if reason == 'edit':
                SLTP_display(set_or_edit = 'edit', with_entry = False)
            if reason == 'modify':
                SLTP_display(set_or_edit = 'edit', with_entry = True)
            st.write('')
            confirm_or_dismiss_buttons(confirm_button_label = button_label, 
                                       reason = reason, 
                                       callback_kwargs = {'ticket': ticket})
            st.subheader('')

@st.dialog(' ', width = 'medium', dismissible = True)
def bare_text(reason, error_code = None):
    if reason == 'success':
        st.header('Request executed', text_alignment = 'center')
    if reason == 'null_lotsize':
        st.header('The volume of the request is 0', text_alignment = 'center')
    if reason == 'not_found':
        st.header('This position or order couldn\'t be found in the server', text_alignment = 'center')
        st.subheader('The most likely reason is that its status has changed', text_alignment = 'center')
    if reason == 'error':
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


