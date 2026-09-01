

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
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

def capitalize_first(string):
    return(string[0].upper() + string[1:])

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

