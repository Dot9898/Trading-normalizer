

import streamlit as st
import MetaTrader5 as mt5
from trades_data import update_all_trades_data
from constants import OUT_DEAL_REASONS, ALERT_REASON_TEXT
from order_execution import limit_or_stop_order
from backend import include_symbol
from data_table import update_data_table


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
            limit_or_stop_order(trade_data['symbol'], 
                                trade_data['lots'], 
                                trade_data['direction'], 
                                trade_data['execution_price'], 
                                trade_data['SL'], 
                                trade_data['TP'])
    
    def notify_execution(self, data):

        @st.dialog(ALERT_REASON_TEXT[self.reason], width = 'medium', on_dismiss = set_dialog_closed)
        def notification_dialog():
            st.session_state['dialog_open'] = True
            display_data = data.drop('alert_object') ###silences warning, check again when using st.data_editor
            st.write(display_data)

        notification_dialog()



def load_alerts():
    alerts = set()
    trades_data = st.session_state['trades_data']
    for ticket, trade_data in trades_data.iterrows():
        if trade_data['status'] in ['pending', 'open']:
            alerts.add(Alert(trade_data['status'], ticket = ticket))
    st.session_state['alerts'] = alerts

def notify_executions_in_serie():   #Used inside a fragment
    if st.session_state['dialog_open']:
        return
    alert, data = st.session_state['alerts_pending_notification'][0]
    alert.notify_execution(data)
    del st.session_state['alerts_pending_notification'][0]

def alert_check():
    to_remove = []
    for alert in st.session_state['alerts']:
        if alert.check():
            alert.execute()
            to_remove.append(alert)
    for alert in to_remove:
        st.session_state['alerts_pending_notification'].append((alert, st.session_state['data_table'].loc[alert.ticket]))
        st.session_state['alerts'].discard(alert)
    if st.session_state['alerts_pending_notification']:
        notify_executions_in_serie()
    if to_remove:
        update_all_trades_data()
        update_data_table(full_update = True)
        #ADD TO JUST EXECUTED, TO SEE THE ALERT









