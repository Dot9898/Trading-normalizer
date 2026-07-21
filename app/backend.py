

from numpy import log10
import streamlit as st
import MetaTrader5 as mt5
from constants import SYMBOL_DATA, DEFAULTS, DATA_PATH
from decimal import Decimal, ROUND_FLOOR
from risk_calculation import get_lotsize_from_ppb_or_pppt


def initialize_MetaTrader():
    mt5.initialize('D:/Dot/FX/Pepperstone MT5/terminal64.exe')

def include_symbol(symbol):
    mt5.symbol_select(symbol, True)


def get_rounding_digits(symbol, scale):
    if scale == 'absolute':
        return(mt5.symbol_info(symbol).digits)
    elif scale == 'normalized':
        return(SYMBOL_DATA[symbol]['digits'] if symbol in SYMBOL_DATA else DEFAULTS['digits'])
    elif scale == 'logarithmic':
        return(6)

def scale_point(value, data_scale, normalization_base = None, symbol = None, true_normalization = False, rounded = False):

    if data_scale == 'absolute':
        pass
    
    if data_scale == 'normalized':
        if normalization_base is None:
            return
        power = SYMBOL_DATA[symbol]['power'] if symbol in SYMBOL_DATA else DEFAULTS['power']
        normalization_factor = 10 ** power
        unit = 1
        if true_normalization:
            unit = 0
        value = ((value / normalization_base) - unit) * normalization_factor
    
    if data_scale == 'logarithmic':
        value = log10(value)

    if rounded:
        value = round(value, get_rounding_digits(symbol, data_scale))
    
    return(value)

def unscale_point(value, original_scale, original_normalization_base, original_normalization_factor):

    if original_scale == 'absolute':
        return(value)
    
    if original_scale == 'normalized':
        return((value/original_normalization_factor + 1) * original_normalization_base)

    if original_scale == 'logarithmic':
        if value > 9:
            return(None) #Prevents overflow
        return(10 ** value)

def unscale_point_wrt_current_values(value):
    bars = st.session_state['bars_data']

    original_scale = bars.data_scale
    base = bars.normalization_base
    factor = bars.normalization_factor
    return(unscale_point(value, original_scale, base, factor))

def normalize_point_wrt_current_price(value):
    bars = st.session_state['bars_data']

    original_scale = bars.data_scale
    base = bars.normalization_base
    factor = bars.normalization_factor
    current_scaled_price = bars.current_bid
    
    original_absolute_value = unscale_point(value, original_scale, base, factor)
    current_absolute_price = unscale_point(current_scaled_price, original_scale, base, factor)
    if original_absolute_value is None:
        return(None)
    
    new_normalized_value = ((original_absolute_value / current_absolute_price) - 1) * 10000 #In basis points from current price
    
    return(new_normalized_value)

def floor_with_step(value, step):
    value = Decimal(str(value))
    step = Decimal(str(step))
    return(float((value / step).quantize(0, rounding = ROUND_FLOOR) * step))

def get_usable_lotsize(execution_price = 'current'):
    bars = st.session_state['bars_data']
    symbol = bars.symbol
    symbol_info = mt5.symbol_info(symbol)

    equity = mt5.account_info().equity
    current_price = symbol_info.bid
    if execution_price == 'current':
        execution_price = current_price  
    scale = bars.selected_scale

    pppt = None
    ppb = None
    if scale == 'absolute':
        pppt = st.session_state['pppt']
    if scale == 'normalized':
        ppb = st.session_state['ppb']

    exact_lotsize = get_lotsize_from_ppb_or_pppt(current_price, execution_price, equity, pppt, ppb)
    
    if exact_lotsize < symbol_info.volume_min:
        lotsize = 0
    elif exact_lotsize >= symbol_info.volume_max:
        lotsize = symbol_info.volume_max
    else:
        lotsize = floor_with_step(exact_lotsize, symbol_info.volume_step)
    
    return(lotsize)

def no_tag_text(text, alignment, font_size, font_weight):
    st.html(f"""
    <h5 style="
        margin:0;
        font-size:{font_size};
        font-weight:{font_weight};
        text-align:{alignment};
    ">
        {text}
    </h5>
    """)











