

import streamlit as st
import MetaTrader5 as mt5
from get_live_data import get_last_update_server_time, register_update_time, get_current_server_time
from trades_data import update_all_data, edit_trade_data
from constants import OUT_DEAL_REASONS
from order_execution import limit_or_stop_order
from backend import scale_point




class Alert:

    def __init__(self, reason, symbol, price = None, ticket = None, more_or_less = None, conditional_trade_data = {}, new_conditional_trade = False):
        self.reason = reason
        self.symbol = symbol
        self.price = price
        self.ticket = ticket
        self.more_or_less = more_or_less
        self.conditional_trade_data = conditional_trade_data
        if new_conditional_trade:
            self.save_conditional_trade_data()
    
    def save_conditional_trade_data(self):
        trade_data = self.conditional_trade_data
        SL = trade_data['SL']
        TP = trade_data['TP']
        set_price = trade_data['set_price']
        symbol = trade_data['symbol']
        lots = trade_data['lots']
        direction = trade_data['direction']

        data = {'status': 'conditional', 
                
                'symbol': symbol, 
                'volume': lots, 
                'set_price': set_price, 
                'direction': direction, 
                'SL_abs': SL, 
                'SL_bp': round(scale_point(SL, 'normalized', set_price, symbol), 1), 
                'TP_abs': TP, 
                'TP_bp': round(scale_point(TP, 'normalized', set_price, symbol), 1)}
        
        ticket = get_current_server_time()

        edit_trade_data(ticket, data)

    def check(self):

        if self.reason == 'manual':
            current_price = mt5.symbol_info_tick.bid
            if self.more_or_less == 'more':
                return(current_price >= self.price)
            elif self.more_or_less == 'less':
                return(current_price <= self.price)
        
        if self.reason == 'conditional_trade':
            order_type = self.conditional_trade_data['order_type']
            bid_or_ask = 'ask' if order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP] else 'bid'
            current_price = getattr(mt5.symbol_info_tick(self.symbol), bid_or_ask)
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
            
            edit_trade_data(self.ticket, delete = True)
        
        update_all_data(get_last_update_server_time())
        register_update_time()

        #alerts.remove

def load_alerts():
    trades_data = st.session_state['trades_data']
    for ticket, trade_data in trades_data.iterrows():

        if trade_data['status'] == 'conditional':
            conditional_trade_data = {'symbol': trade_data['symbol'], 
                                      'lots': trade_data['volume'], 
                                      'set_price': trade_data['set_price'], 
                                      'direction': trade_data['direction'], 
                                      'SL': trade_data['SL_abs'], 
                                      'TP': trade_data['TP_abs']}
            alert = Alert('conditional', trade_data['symbol'], )

st.fragment()
def alert_check():

    for alert in st.session_state['alerts']:

        if alert.type == 'conditional_trade':
            pass

        #if alert.type == ''










