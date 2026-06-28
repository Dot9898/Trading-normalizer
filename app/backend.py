

from numpy import log10
import streamlit as st
from constants import SYMBOL_DATA, DEFAULTS
from get_live_data import Bars



def scale_point(value, data_scale, normalization_base = None, symbol = None):

    if data_scale == 'absolute':
        return(value)
    
    if data_scale == 'normalized':
        if normalization_base is None:
            return
        power = SYMBOL_DATA[symbol]['power'] if symbol in SYMBOL_DATA else DEFAULTS['power']
        normalization_factor = 10 ** power
        return(((value / normalization_base) - 1) * normalization_factor)
    
    if data_scale == 'logarithmic':
        return(log10(value))

def unscale_point(value, original_scale, original_normalization_base, original_normalization_factor):

    if original_scale == 'absolute':
        return(value)
    
    if original_scale == 'normalized':
        return((value/original_normalization_factor + 1) * original_normalization_base)

    if original_scale == 'logarithmic':
        if value > 9:
            return(None) #Prevents overflow
        return(10 ** value)

def normalize_point_wrt_current_price(value):
    bars: Bars = st.session_state['bars_data']

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






















