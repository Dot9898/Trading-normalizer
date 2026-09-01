

import streamlit as st
import pandas as pd
import MetaTrader5 as mt5
from constants import OUT_DEAL_REASONS, ALERT_REASON_TEXT, SHOWN_ALERTS_DATA_COLUMNS
from order_execution import limit_or_stop_order
from backend import include_symbol, scale_point
from get_live_data import get_current_server_time
from format_functions import format_timestamp


def set_dialog_closed():
    st.session_state['dialog_open'] = False

class Alert:

    def __init__(self, reason, symbol = None, absolute_price = None, ticket = None, more_or_less = None, conditional_trade_data = None):
        self.reason = reason
        self.symbol = symbol
        self.absolute_price = absolute_price
        self.ticket = ticket
        self.more_or_less = more_or_less
        self.conditional_trade_data = conditional_trade_data
        self.order_type = None

        include_symbol(symbol)

    def check(self):

        if self.reason in ['manual', 'conditional_trade']:
            current_price = mt5.symbol_info_tick(self.symbol).bid
            if self.more_or_less == 'more':
                return(current_price >= self.absolute_price)
            elif self.more_or_less == 'less':
                return(current_price <= self.absolute_price)
        
        if self.reason == 'open':
            return(len(mt5.positions_get(ticket = self.ticket)) == 1)

        if self.reason == 'close':
            for deal in mt5.history_deals_get(position = self.ticket):
                if deal.entry == mt5.DEAL_ENTRY_OUT:
                    return(True)
            return(False)
    
    def execute(self):

        if self.reason == 'manual':
            pass #MAKE SOUND
        
        if self.reason == 'open':
            pass #MAKE SOUND
        
        if self.reason == 'close':
            for deal in mt5.history_deals_get(position = self.ticket):
                if deal.entry == mt5.DEAL_ENTRY_OUT:
                    reason = OUT_DEAL_REASONS
                    if reason == 'SL':
                        #MAKE SOUND
                        pass
                    if reason == 'TP':
                        #MAKE SOUND
                        pass
                    if reason == 'SO':
                        #MAKE SOUND
                        pass
        
        if self.reason == 'conditional_trade':
            trade_data = self.conditional_trade_data
            ordd = limit_or_stop_order(trade_data['symbol'], 
                                trade_data['lots'], 
                                trade_data['direction'], 
                                trade_data['execution_price'], 
                                trade_data['SL'], 
                                trade_data['TP'])
            st.session_state['order_return'] = ordd
    
    def notify_execution(self, data):

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

def get_execution_data(alert):
    if alert.ticket in st.session_state['data_table'].index:
        data = st.session_state['data_table'].loc[alert.ticket].copy()
    else:                     #The alert was instantly executed and didn't make it to the table
        data = pd.Series()    #That should only be possible with manual and conditional trade alerts

    bars = st.session_state['bars_data']

    if alert.reason == 'manual':
        data['Time'] = format_timestamp(get_current_server_time(), st.session_state['selected_timezone'])
        data['Status'] = 'Executed'
        data['Progress'] = bars.current_bid
        data['Operation'] = f'Alert {alert.symbol}'

    if alert.reason == 'conditional_trade':
        data['Time'] = format_timestamp(get_current_server_time(), st.session_state['selected_timezone'])
        data['Status'] = 'Set'
        direction = alert.conditional_trade_data['direction'].capitalize()
        order_type = alert.conditional_trade_data['order_type']
        operation = f'{direction} {order_type} {alert.symbol}'
        if bars.data_scale == 'normalized' and bars.symbol == alert.symbol:
            execution_price_abs = alert.conditional_trade_data['execution_price']
            execution_price_bp = scale_point(execution_price_abs, 'normalized', bars.normalization_base, alert.symbol, rounded = True)
            operation = f'{operation} at {execution_price_bp}'
        data['Operation'] = operation
        
    return(data)

def load_alerts():
    alerts = set()
    trades_data = st.session_state['trades_data']
    for ticket, trade_data in trades_data.iterrows():
        if trade_data['status'] == 'pending':
            alerts.add(Alert('open', ticket = ticket))
        if trade_data['status'] == 'open':
            alerts.add(Alert('close', ticket = ticket))
    st.session_state['alerts'] = alerts

def update_open_and_close_alerts():   #Used after updating trades_data
    alerts_tickets = [alert.ticket for alert in st.session_state['alerts']]
    trades_data = st.session_state['trades_data']
    for ticket, trade_data in trades_data.iterrows():
        if ticket not in alerts_tickets and trade_data['status'] == 'pending':
            st.session_state['alerts'].add(Alert('open', ticket = ticket))
        if ticket not in alerts_tickets and trade_data['status'] == 'open':
            st.session_state['alerts'].add(Alert('close', ticket = ticket))
    for alert in st.session_state['alerts']:
        if alert.reason in ['open', 'close'] and alert.ticket not in trades_data.index:
            st.session_state['orders_to_delete'].add(alert)

def notify_executions_in_serie():   #Used inside a fragment
    if st.session_state['dialog_open']:
        return
    data_table = st.session_state['data_table']
    alert, backup_data = st.session_state['alerts_pending_notification'][0]

    if alert.reason in ['open', 'close'] and alert.ticket in data_table.index:
        data = data_table.loc[alert.ticket].copy()
    else:
        data = backup_data
    
    alert.notify_execution(data)
    del st.session_state['alerts_pending_notification'][0]

#@st.fragment(run_every = POLLING_INTERVAL)
def alert_check():
    to_remove = []
    for alert in st.session_state['alerts']:
        if alert.check():
            alert.execute()
            to_remove.append(alert)
    for alert in to_remove:
        data = get_execution_data(alert)
        st.session_state['alerts_pending_notification'].append((alert, data))
        st.session_state['alerts'].discard(alert)
    for alert in st.session_state['orders_to_delete']:
        st.session_state['alerts'].discard(alert)
    if to_remove:
        st.session_state['update_data_table'] = True
        #ADD TO JUST EXECUTED, TO SEE THE ALERT









