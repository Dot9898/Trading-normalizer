

import pandas as pd
import streamlit as st
import MetaTrader5 as mt5
from constants import DATA_PATH, TRADE_DATA_COLUMNS_TO_TYPES, SYMBOL_DATA, OUT_DEAL_REASONS
from backend import scale_point
from get_live_data import get_current_server_time, get_actual_timestamp, get_last_update_server_time, register_update_time


def load_trades_data():
    trades_data_path = DATA_PATH / 'trades_data.csv'

    if not trades_data_path.exists():
        trades_data = pd.DataFrame(columns = TRADE_DATA_COLUMNS_TO_TYPES.keys())
        for column, datatype in TRADE_DATA_COLUMNS_TO_TYPES.items():
            trades_data[column] = trades_data[column].astype(datatype)
    else:
        trades_data = pd.read_csv(trades_data_path, dtype = TRADE_DATA_COLUMNS_TO_TYPES)
    trades_data = trades_data.set_index('ticket')
    
    st.session_state['trades_data'] = trades_data
    update_all_trades_data()

def save_trades_data_to_file():
    trades_data_path = DATA_PATH / 'trades_data.csv'
    tmp_path = DATA_PATH / 'trades_data.csv.tmp'

    st.session_state['trades_data'].to_csv(tmp_path, index = True)
    tmp_path.replace(trades_data_path)

def edit_trade_data(ticket, data_to_edit: dict | None = None, delete = False):

    trades_data = st.session_state['trades_data']

    if delete:
        trades_data.drop(ticket, inplace = True)
    
    else:
        if data_to_edit is None:
            return

        if ticket not in trades_data.index:
            trades_data.loc[ticket] = pd.NA
            trades_data.at[ticket, 'is_shown'] = True

        for column, new_value in data_to_edit.items():
            trades_data.at[ticket, column] = new_value

    save_trades_data_to_file()

def get_update_categories(from_server_time):
    
    """
    When a ticket is changed server side, the local data must be edited to reflect it.
    The possible edit categories are the following, each implies a different edit to the data:
    
    Modified: a pending order known by the client had its parameters modified by the server\n
    Opened: a pending order known by the client was opened by the server\n
    Opened and closed: a pending order known by the client was opened by the server, and was closed afterwards by the server\n
    Deleted: a pending order known by the client was deleted by the server
    
    Edited: an open position known by the client had its parameters modified by the server\n
    Closed: an open position known by the client was closed by the server
    
    Market opened: a new position was opened by the server via a market order\n
    Market opened and closed: a new position was opened by the server via a market order, and was closed afterwards by the server
    
    Set: a new pending order was set by the server and is still pending\n
    Set and opened: a new pending order was set by the server, and was opened afterwards by the server\n
    Set opened and closed: a new pending order was set by the server, was opened afterwards by the server, and was finally closed by the server.
    """
    
    trades_data = st.session_state['trades_data']
    current_server_time = get_current_server_time()
    current_orders = mt5.orders_get()
    current_positions = mt5.positions_get()
    orders_history = mt5.history_orders_get(from_server_time, current_server_time)
    deals_history = mt5.history_deals_get(from_server_time, current_server_time)

    pending_tickets = [ticket for ticket in trades_data.index 
                       if trades_data.at[ticket, 'status'] == 'pending']
    open_tickets = [ticket for ticket in trades_data.index 
                    if trades_data.at[ticket, 'status'] == 'open']
    current_orders_tickets = [order.ticket for order in current_orders]
    current_positions_tickets = [position.ticket for position in current_positions]
    deal_history_tickets = [deal.position_id for deal in deals_history]
    history_pending_order_tickets = [order.position_id for order in orders_history 
                                     if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, 
                                                       mt5.ORDER_TYPE_SELL_LIMIT,
                                                       mt5.ORDER_TYPE_BUY_STOP, 
                                                       mt5.ORDER_TYPE_SELL_STOP]]
    
    category = {}

    for ticket in pending_tickets:
        if ticket in current_orders_tickets:
            category[ticket] = 'modified'
        elif ticket in current_positions_tickets:
            category[ticket] = 'opened'
        else:
            if ticket in deal_history_tickets:
                category[ticket] = 'opened_and_closed'
            else:
                category[ticket] = 'deleted'
        
    for ticket in open_tickets:
        if ticket in current_positions_tickets:
            category[ticket] = 'edited'
        else:
            category[ticket] = 'closed'

    for ticket in current_orders_tickets:
        if ticket not in (pending_tickets + open_tickets): #open tickets kept for clarity
            category[ticket] = 'set'

    for ticket in current_positions_tickets:
        if ticket not in (pending_tickets + open_tickets):
            if ticket in history_pending_order_tickets:
                category[ticket] = 'set_and_opened'
            else:
                category[ticket] = 'market_opened'
    
    for deal in deals_history:
        ticket = deal.position_id
        if ticket not in (pending_tickets + open_tickets):
            if deal.entry == mt5.DEAL_ENTRY_OUT:
                if ticket in history_pending_order_tickets:
                    category[ticket] = 'set_opened_and_closed'
                else:
                    category[ticket] = 'market_opened_and_closed'
    
    return(category)

def update_SL_TP(data, data_source, update_type, SL, TP, base_price, lots, symbol, current_account_info):

    if SL is None:
        data['SL_abs'] = None
        data['SL_bp'] = None

    else:
        data['SL_abs'] = SL
        data['SL_bp'] = round(scale_point(SL, 'normalized', base_price, symbol), 1)

        if update_type == 'set':
            data['SL_acc_percent_at_set_(equity)'] = round(100 * (SL - base_price) * lots / current_account_info.equity, 1)
        if update_type == 'open' and data_source == 'local':
            data['SL_acc_percent_at_open_(equity)'] = round(100 * (SL - base_price) * lots / current_account_info.equity, 1)

    if TP is None:
        data['TP_abs'] = None
        data['TP_bp'] = None

    else:
        data['TP_abs'] = TP
        data['TP_bp'] = round(scale_point(TP, 'normalized', base_price, symbol), 1)

        if update_type == 'set':
            data['TP_acc_percent_at_set_(equity)'] = round(100 * (TP - base_price) * lots / current_account_info.equity, 1)
        if update_type == 'open' and data_source == 'local':
            data['TP_acc_percent_at_open_(equity)'] = round(100 * (TP - base_price) * lots / current_account_info.equity, 1)

    return(data)

def update_closing_PL(data, data_source, PL, ticket, trades_data, current_account_info):

    if data_source == 'local':
        data['balance_at_close'] = current_account_info.balance
        data['equity_at_close'] = current_account_info.equity
        data['P/L_acc_percent_(equity)'] = round(PL/(current_account_info.equity - PL) * 100, 1)
        data['P/L_acc_percent_(balance)'] = round(PL/(current_account_info.balance - PL) * 100, 1)
    
    if data_source == 'server':
        last_known_account_value = None
        if ticket in trades_data.index:
            for key in ['equity_at_open', 'balance_at_open', 'equity_at_set', 'balance_at_set']:
                if not pd.isna(trades_data.at[ticket, key]): #includes None
                    last_known_account_value = trades_data.at[ticket, key]
                    break
        if last_known_account_value is None:
            last_known_account_value = current_account_info.balance
        data['P/L_acc_percent_(estimate)'] = round(PL/(last_known_account_value - PL) * 100, 1)
    
    return(data)

def get_trade_data_to_edit(ticket, data_source, operation_type): #Need to fix this flow, break it down in more functions
    
    current_account_info = mt5.account_info()
    trades_data = st.session_state['trades_data']

    data = {}

    if operation_type == 'market_opened':

        position = mt5.positions_get(ticket = ticket)[0]

        SL = None if position.sl == 0 else position.sl
        TP = None if position.tp == 0 else position.tp
        open_price = position.price_open
        symbol = position.symbol
        lots = position.volume

        data = {'status': 'open', 
                
                'symbol': symbol, 
                'volume': lots, 
                'set_price': open_price, 
                'direction': 'buy' if position.type == mt5.ORDER_TYPE_BUY else 'sell', 
                'order_type': 'market', 

                'open_server_time': position.time, 
                'open_timestamp': get_actual_timestamp(position.time), 
                'open_price': open_price, 
                
                'display': SYMBOL_DATA[symbol]['display']}
        
        if data_source == 'local':
            data['balance_at_set'] = round(current_account_info.balance)
            data['equity_at_set'] = round(current_account_info.equity)
            data['balance_at_open'] = round(current_account_info.balance)
            data['equity_at_open'] = round(current_account_info.equity)

        data = update_SL_TP(data, data_source, 'set', SL, TP, open_price, lots, symbol, current_account_info)
        data = update_SL_TP(data, data_source, 'open', SL, TP, open_price, lots, symbol, current_account_info)

    if operation_type in ['market_opened_and_closed', 'opened_and_closed']:

        deals_of_this_ticket = mt5.history_deals_get(position = ticket)
        for potential_deal in deals_of_this_ticket:
            if potential_deal.entry == mt5.DEAL_ENTRY_IN:
                entry_deal = potential_deal
            if potential_deal.entry == mt5.DEAL_ENTRY_OUT:
                exit_deal = potential_deal
        
        entry_order = mt5.history_orders_get(position = ticket)[0] #Deals have no TP or SL, we assume the first order is the entry market order

        SL = None if entry_order.sl == 0 else entry_order.sl
        TP = None if entry_order.tp == 0 else entry_order.tp
        open_price = entry_deal.price
        close_price = exit_deal.price
        symbol = entry_deal.symbol
        lots = entry_deal.volume
        PL = exit_deal.profit
        close_reason = OUT_DEAL_REASONS.get(exit_deal.reason)

        data = {'status': 'closed', 
                
                'symbol': symbol, 
                'volume': lots, 
                'direction': 'buy' if entry_deal.type == mt5.ORDER_TYPE_BUY else 'sell', 

                'open_server_time': entry_deal.time, 
                'open_timestamp': get_actual_timestamp(entry_deal.time), 
                'open_price': open_price, 

                'close_server_time': exit_deal.time, 
                'close_timestamp': get_actual_timestamp(exit_deal.time), 
                'close_reason': close_reason, 
                'close_price': close_price, 
                'points_abs': round(close_price - open_price, 1), 
                'points_bp': round(scale_point(close_price - open_price, 'normalized', open_price, symbol, true_normalization = True), 1), 
                'P/L_abs': PL, 

                'display': SYMBOL_DATA[symbol]['display']}
    
        if operation_type == 'market_opened_and_closed':
            data['order_type'] = 'market'
            data['set_price'] = open_price
            data = update_SL_TP(data, data_source, 'set', SL, TP, open_price, lots, symbol, current_account_info)

        data = update_SL_TP(data, data_source, 'open', SL, TP, open_price, lots, symbol, current_account_info)
        data = update_closing_PL(data, data_source, PL, ticket, trades_data, current_account_info)

    if operation_type == 'set':

        order = mt5.orders_get(ticket = ticket)[0]

        SL = None if order.sl == 0 else order.sl
        TP = None if order.tp == 0 else order.tp
        set_price = order.price_open
        symbol = order.symbol
        lots = order.volume_initial

        data = {'status': 'pending', 
                
                'symbol': symbol, 
                'volume': lots, 
                'set_price': set_price, 
                'direction': 'buy' if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP] else 'sell', 
                'order_type': 'limit' if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT] else 'stop', 
                'balance_at_set': round(current_account_info.balance), 
                'equity_at_set': round(current_account_info.equity), 
                
                'display': SYMBOL_DATA[symbol]['display']}

        data = update_SL_TP(data, data_source, 'set', SL, TP, set_price, lots, symbol, current_account_info)

    if operation_type == 'edited':

        position = mt5.positions_get(ticket = ticket)[0]

        SL = None if position.sl == 0 else position.sl
        TP = None if position.tp == 0 else position.tp
        open_price = position.price_open
        symbol = position.symbol
        lots = position.volume

        data = update_SL_TP(data, data_source, 'edited', SL, TP, open_price, lots, symbol, current_account_info)

    if operation_type == 'modified':

        order = mt5.orders_get(ticket = ticket)[0]

        SL = None if order.sl == 0 else order.sl
        TP = None if order.tp == 0 else order.tp
        set_price = order.price_open
        symbol = order.symbol
        lots = order.volume_initial

        data['set_price'] = set_price
        data['balance_at_set'] = round(current_account_info.balance)
        data['equity_at_set'] = round(current_account_info.equity)

        data = update_SL_TP(data, data_source, 'set', SL, TP, set_price, lots, symbol, current_account_info)

    if operation_type == 'closed':

        open_price = trades_data.at[ticket, 'open_price']
        deals_of_this_ticket = mt5.history_deals_get(position = ticket)
        for potential_deal in deals_of_this_ticket:
            if potential_deal.entry == mt5.DEAL_ENTRY_OUT:
                deal = potential_deal

        close_price = deal.price
        symbol = deal.symbol
        PL = deal.profit
        close_reason = OUT_DEAL_REASONS.get(deal.reason)

        data = {'status': 'closed', 
                
                'close_server_time': deal.time, 
                'close_timestamp': get_actual_timestamp(deal.time), 
                'close_reason': close_reason, 
                'close_price': close_price, 
                'points_abs': round(close_price - open_price, 1), 
                'points_bp': round(scale_point(close_price - open_price, 'normalized', open_price, symbol, true_normalization = True), 1), 
                'P/L_abs': PL}

        data = update_closing_PL(data, data_source, PL, ticket, trades_data, current_account_info)

    if operation_type == 'opened':

        set_price = trades_data.at[ticket, 'set_price']
        position = mt5.positions_get(ticket = ticket)[0]

        SL = None if position.sl == 0 else position.sl
        TP = None if position.tp == 0 else position.tp
        open_price = position.price_open
        symbol = position.symbol
        lots = position.volume

        data = {'status': 'open', 

                'open_server_time': position.time, 
                'open_timestamp': get_actual_timestamp(position.time), 
                'open_price': open_price}
        
        if data_source == 'local':
            data['balance_at_open'] = round(current_account_info.balance)
            data['equity_at_open'] = round(current_account_info.equity)

        data = update_SL_TP(data, data_source, 'open', SL, TP, open_price, lots, symbol, current_account_info)

    if operation_type == 'set_and_opened':
        
        orders_of_this_ticket = mt5.history_orders_get(position = ticket)
        for potential_order in orders_of_this_ticket:
            if potential_order.type in [mt5.ORDER_TYPE_BUY_LIMIT, 
                                        mt5.ORDER_TYPE_SELL_LIMIT,
                                        mt5.ORDER_TYPE_BUY_STOP, 
                                        mt5.ORDER_TYPE_SELL_STOP]:
                order = potential_order
        position = mt5.positions_get(ticket = ticket)[0]

        SL = None if position.sl == 0 else position.sl
        TP = None if position.tp == 0 else position.tp
        set_SL = None if order.sl == 0 else order.sl
        set_TP = None if order.tp == 0 else order.tp
        set_price = order.price_open
        open_price = position.price_open
        symbol = position.symbol
        lots = position.volume

        data = {'status': 'open', 
                
                'symbol': symbol, 
                'volume': lots, 
                'set_price': set_price, 
                'direction': 'buy' if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP] else 'sell', 
                'order_type': 'limit' if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT] else 'stop', 
                'open_server_time': position.time, 
                'open_timestamp': get_actual_timestamp(position.time), 
                'open_price': open_price, 
                
                'display': SYMBOL_DATA[symbol]['display']}
        
        data = update_SL_TP(data, data_source, 'set', set_SL, set_TP, set_price, lots, symbol, current_account_info)
        data = update_SL_TP(data, data_source, 'open', SL, TP, open_price, lots, symbol, current_account_info)

    if operation_type == 'set_opened_and_closed':

        orders_of_this_ticket = mt5.history_orders_get(position = ticket)
        for potential_order in orders_of_this_ticket:
            if potential_order.type in [mt5.ORDER_TYPE_BUY_LIMIT, 
                                        mt5.ORDER_TYPE_SELL_LIMIT,
                                        mt5.ORDER_TYPE_BUY_STOP, 
                                        mt5.ORDER_TYPE_SELL_STOP]:
                order = potential_order

        deals_of_this_ticket = mt5.history_deals_get(position = ticket)
        for potential_deal in deals_of_this_ticket:
            if potential_deal.entry == mt5.DEAL_ENTRY_IN:
                entry_deal = potential_deal
            if potential_deal.entry == mt5.DEAL_ENTRY_OUT:
                exit_deal = potential_deal
        
        entry_order = mt5.history_orders_get(position = ticket)[0] #Deals have no TP or SL, we assume the first order is the entry market order

        SL = None if entry_order.sl == 0 else entry_order.sl
        TP = None if entry_order.tp == 0 else entry_order.tp
        set_SL = None if order.sl == 0 else order.sl
        set_TP = None if order.tp == 0 else order.tp
        set_price = order.price_open
        open_price = entry_deal.price
        symbol = entry_deal.symbol
        lots = entry_deal.volume

        data = {'status': 'open', 
                
                'symbol': symbol, 
                'volume': lots, 
                'set_price': set_price, 
                'direction': 'buy' if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP] else 'sell', 
                'order_type': 'limit' if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT] else 'stop', 
                'open_server_time': entry_deal.time, 
                'open_timestamp': get_actual_timestamp(entry_deal.time), 
                'open_price': open_price, 
                
                'display': SYMBOL_DATA[symbol]['display']}
        
        data = update_SL_TP(data, data_source, 'set', set_SL, set_TP, set_price, lots, symbol, current_account_info)
        data = update_SL_TP(data, data_source, 'open', SL, TP, open_price, lots, symbol, current_account_info)

        close_price = exit_deal.price
        PL = exit_deal.profit
        close_reason = OUT_DEAL_REASONS.get(exit_deal.reason)

        data['status'] = 'closed'
        data['close_server_time'] = exit_deal.time
        data['close_timestamp'] = get_actual_timestamp(exit_deal.time)
        data['close_reason'] = close_price
        data['close_price'] = close_price
                
        data['points_abs'] = round(close_price - open_price, 1)
        data['points_bp'] = round(scale_point(close_price - open_price, 'normalized', open_price, symbol, true_normalization = True), 1)
        data['P/L_abs'] = PL

        data = update_closing_PL(data, data_source, PL, ticket, trades_data, current_account_info)

    return(data)

def update_ticket_data(ticket, data_source, category):
    
    if category == 'deleted':
        edit_trade_data(ticket, delete = True)
    
    else:
        data = get_trade_data_to_edit(ticket, data_source, category)
        edit_trade_data(ticket, data)

def update_all_trades_data():#from_server_time = None):
    #if from_server_time is None:
    from_server_time = get_last_update_server_time()
    categories = get_update_categories(from_server_time)
    for ticket, category in categories.items():
        update_ticket_data(ticket, 'server', category)
    register_update_time()




#Pensar cuándo quiero updatear la data polleando del server:
#Cuando se ejecuta una alert (set conditional, open, close, alert)
#Al iniciar el programa
#Cada cierto tiempo, para revisar acciones remotas del usuario al server (desktop client, mobile), o actualizar las abiertas, pendientes, history





