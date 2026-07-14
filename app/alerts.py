

import streamlit as st
import MetaTrader5 as mt5
from trades_data import update_all_trades_data
from constants import OUT_DEAL_REASONS, POLLING_INTERVAL
from order_execution import limit_or_stop_order
from backend import include_symbol


class Alert:

    def __init__(self, reason, symbol = None, price = None, ticket = None, more_or_less = None, conditional_trade_data = None):
        self.reason = reason
        self.symbol = symbol
        self.price = price
        self.ticket = ticket
        self.more_or_less = more_or_less
        self.conditional_trade_data = conditional_trade_data
        self.order_type = None

        if self.reason == 'conditional_trade':
            self.set_order_type()

        include_symbol(symbol)
        
    def set_order_type(self):
        if self.conditional_trade_data['direction'] == 'buy':
            if self.conditional_trade_data['execution_price'] > self.price:
                self.order_type = 'stop'
            else:
                self.order_type = 'limit'
        if self.conditional_trade_data['direction'] == 'sell':
            if self.conditional_trade_data['execution_price'] > self.price:
                self.order_type = 'limit'
            else:
                self.order_type = 'stop'

    def check(self):

        if self.reason in ['manual', 'conditional_trade']:
            current_price = mt5.symbol_info_tick(self.symbol).bid
            if self.more_or_less == 'more':
                return(current_price >= self.price)
            elif self.more_or_less == 'less':
                return(current_price <= self.price)
        
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
        
        update_all_trades_data()


def load_alerts():
    alerts = set()
    trades_data = st.session_state['trades_data']
    for ticket, trade_data in trades_data.iterrows():
        if trade_data['status'] in ['pending', 'open']:
            alerts.add(Alert(trade_data['status'], ticket = ticket))
    return(alerts)

st.fragment(run_every = POLLING_INTERVAL)
def alert_check():
    to_remove = []
    for alert in st.session_state['alerts']:
        if alert.check():
            alert.execute()
            to_remove.append(alert)
    for alert in to_remove:
        st.session_state['alerts'].discard(alert)










