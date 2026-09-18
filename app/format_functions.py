

import streamlit as st
from datetime import datetime, timezone
from backend import floor_with_step
from constants import TIMEZONES, DATA_TABLE_DATE_FORMAT
from get_live_data import get_actual_timestamp


def timezone_format(timezone):
    if timezone == 'server':
        return('MT5 server')
    else:
        return(timezone.title())

def RR_format(rr):
    if rr == 'custom':
        return('Custom')
    else:
        risk, reward = rr
        return(f'{risk}:{reward}') #({round(risk / (risk + reward), 2)})')

def add_sign(number, percent = False):
    if number > 0:
        formatted = f'+{number}'
    else:
        formatted = f'{number}'
    if percent:
        formatted = f'{formatted}%'
    return(formatted)

def as_percent(number, digits = 1):
    return(f'{round(number * 100, digits)}%')

def round_balance(number):
    if number < 1:
        return(0)
    if number < 50:
        return(round(number))
    
    rounded_balance = str(round(number))
    digits_qty = len(rounded_balance)
    power = digits_qty - 2
    first_digit = int(rounded_balance[0])
    
    if first_digit == 1:
        step = 5
        power = power - 1
    elif first_digit in [2, 3, 4]:
        step = 1
    else:
        step = 2

    step = step * 10 ** power
    return(int(floor_with_step(number, step)))

def capitalize_first(string):
    return(string[0].upper() + string[1:])

def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)

def small_linebreak_caption(first_line, second_line, alignment = 'left'):
    st.caption(f'{first_line}<br>{second_line}', 
               unsafe_allow_html = True, 
               text_alignment = alignment)

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

def format_timestamp(server_time, selected_timezone):
    if selected_timezone == 'server':
        dt = datetime.fromtimestamp(server_time, tz = timezone.utc)
    else:
        timestamp = get_actual_timestamp(server_time)
        dt = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        dt = dt.astimezone((TIMEZONES[selected_timezone]))
    formatted = dt.strftime(DATA_TABLE_DATE_FORMAT)
    return(formatted)

