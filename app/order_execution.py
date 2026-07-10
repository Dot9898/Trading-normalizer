

import MetaTrader5 as mt5
from constants import SYMBOL_DATA, DEFAULTS
from math import floor
from trades_data import get_trade_data_to_edit, edit_trade_data


def get_deviation(symbol):
    display = (SYMBOL_DATA[symbol]['display'] if symbol in SYMBOL_DATA else DEFAULTS['display'])
    max_deviation_percentage = 0.05 if display == 'basis' else 0.5
    current_price = mt5.symbol_info_tick(symbol).bid
    absolute_deviation = current_price * max_deviation_percentage * 0.01
    point = mt5.symbol_info(symbol).point
    deviation_in_points = int(floor(absolute_deviation / point))
    return(deviation_in_points)

def market_order(symbol, lots, direction, SL = None, TP = None):
    if direction == 'buy':
        order_type = mt5.ORDER_TYPE_BUY
    elif direction == 'sell':
        order_type = mt5.ORDER_TYPE_SELL
    
    request = {'action': mt5.TRADE_ACTION_DEAL, 
               'symbol': symbol, 
               'volume': lots, 
               'type': order_type, 
               'type_filling': mt5.ORDER_FILLING_IOC}
    
    if SL is not None:
        request['sl'] = float(SL)
    if TP is not None:
        request['tp'] = float(TP)

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        ticket = result.order
        data = get_trade_data_to_edit(ticket, 'local', 'market_opened')
        edit_trade_data(ticket, data)

    return(result)

def limit_or_stop_order(symbol, lots, direction, execution_price, SL = None, TP = None):
    execution_price = float(execution_price)
    current_price = mt5.symbol_info_tick(symbol).ask
    
    if direction == 'buy':
        if execution_price > current_price:
            order_type = mt5.ORDER_TYPE_BUY_STOP
        else:
            order_type = mt5.ORDER_TYPE_BUY_LIMIT
   
    elif direction == 'sell':
        if execution_price > current_price:
            order_type = mt5.ORDER_TYPE_SELL_LIMIT
        else:
            order_type = mt5.ORDER_TYPE_SELL_STOP

    request = {'action': mt5.TRADE_ACTION_PENDING, 
               'symbol': symbol, 
               'volume': lots, 
               'price': execution_price, 
               'deviation': get_deviation(symbol),
               'type': order_type, 
               'type_filling': mt5.ORDER_FILLING_IOC}
    
    if SL is not None:
        request['sl'] = float(SL)
    if TP is not None:
        request['tp'] = float(TP)

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        ticket = result.order
        data = get_trade_data_to_edit(ticket, 'local', 'set')
        edit_trade_data(ticket, data)

    return(result)

def change_SLTP_open(ticket, symbol, SL = None, TP = None):
    request = {'action': mt5.TRADE_ACTION_SLTP, 
               'position': ticket, 
               'symbol': symbol}
    
    if SL is not None:
        request['sl'] = float(SL)
    if TP is not None:
        request['tp'] = float(TP)

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        data = get_trade_data_to_edit(ticket, 'local', 'edited')
        edit_trade_data(ticket, data)

    return(result)

def change_price_and_SLTP_pending(ticket, symbol, execution_price = None, SL = None, TP = None):
    
    request = {'action': mt5.TRADE_ACTION_MODIFY, 
               'order': ticket, 
               'symbol': symbol}
    
    if execution_price is not None:
        request['price'] = float(execution_price)
    if SL is not None:
        request['sl'] = float(SL)
    if TP is not None:
        request['tp'] = float(TP)

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        data = get_trade_data_to_edit(ticket, 'local', 'modified')
        edit_trade_data(ticket, data)

    return(result)

def delete_pending_order(ticket):

    request = {'action': mt5.TRADE_ACTION_REMOVE, 
               'order': ticket}

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        edit_trade_data(ticket, delete = True)
    
    return(result)

def close_position(ticket, symbol, lots, original_direction): ####
    if original_direction == 'buy':
        order_type = mt5.ORDER_TYPE_SELL
    elif original_direction == 'sell':
        order_type = mt5.ORDER_TYPE_BUY

    request = {'action': mt5.TRADE_ACTION_DEAL, 
               'position': ticket, 
               'symbol': symbol, 
               'volume': lots, 
               'type': order_type, 
               'type_filling': mt5.ORDER_FILLING_IOC}
    
    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        data = get_trade_data_to_edit(ticket, 'local', 'closed') #, ORDERTYPE?)
        edit_trade_data(ticket, data)

    return(result)


#lotsize symbol.volume_min

"""

"price": price,
order
Order ticket. Required for modifying pending orders
position
Position ticket. Fill it when changing and closing a position for its clear identification. Usually, it is the same as the ticket of the order that opened the position.


TRADE_ACTION_SLTP                   = 6      # Modify Stop Loss and Take Profit values of an opened position
TRADE_ACTION_MODIFY                 = 7      # Modify the parameters of the order placed previously
TRADE_ACTION_REMOVE                 = 8      # Delete the pending order placed previously

"""














