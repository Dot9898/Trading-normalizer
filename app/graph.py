

import pandas as pd
import streamlit as st
import altair as alt
from constants import CHART_COLORS, POLLING_INTERVAL, TIMEZONE_LABEL
from get_live_data import Bars

GRAPH_HEIGHT = 600
Y_AXE_TITLE = 'Price (absolute)'

def altair_candlestick_graph(bars_data, colors):

    bars = bars_data.bars
    name = bars_data.name
    timezone = bars_data.timezone
    digits = bars_data.digits
    price_range = [bars_data.min_price, bars_data.max_price]
    date_label = '' if bars_data.date_label is None else bars_data.date_label
    bid = bars_data.current_bid
    ask = bars_data.current_ask


    candlestick_color = (
        alt.when('datum.is_positive')
        .then(alt.value(CHART_COLORS['fill'][colors]['positive']))
        .otherwise(alt.value(CHART_COLORS['fill'][colors]['negative'])))
    
    stroke_color = (
        alt.when('datum.is_positive')
        .then(alt.value(CHART_COLORS['stroke'][colors]['positive']))
        .otherwise(alt.value(CHART_COLORS['stroke'][colors]['negative'])))
    
    price_line_color = alt.Color(
        'type:N',
        scale = alt.Scale(
            domain = ['bid', 'ask'],
            range = [CHART_COLORS['price_lines']['bid'], CHART_COLORS['price_lines']['ask']]), 
        legend = None)

    candlesticks_tooltips = [
        alt.Tooltip('date_label:N', title = 'Date'),
        alt.Tooltip('time_label:N', title = 'Time'),
        alt.Tooltip('open:Q', title = 'Open'),
        alt.Tooltip('high:Q', title = 'High'),
        alt.Tooltip('low:Q', title = 'Low'),
        alt.Tooltip('close:Q', title = 'Close')]
    
    price_lines_tooltips = [
        alt.Tooltip('ask:Q', format = f'.{digits}f', title = 'Ask'), 
        alt.Tooltip('bid:Q', format = f'.{digits}f', title = 'Bid')]


    base = alt.Chart(bars).encode(
        alt.X('axis_label:O', 
            axis = alt.Axis(labelAngle = 0, title = [date_label, f'{TIMEZONE_LABEL[timezone]} time']), 
            scale = alt.Scale(paddingInner = 0.35, paddingOuter = 0.5), 
            sort = alt.SortField('time', order = 'ascending')), 
        color = candlestick_color, 
        stroke = stroke_color
    ).transform_calculate(
        is_positive = 'datum.open <= datum.close')
    
    candles = base.mark_bar().encode(
        alt.Y('open:Q', 
            axis = alt.Axis(title = Y_AXE_TITLE), 
            scale = alt.Scale(domain = price_range, zero = False)), 
        alt.Y2('close:Q'), 
        tooltip = candlesticks_tooltips)

    sticks = base.mark_rule().encode(
        alt.Y('high:Q'),
        alt.Y2('low:Q'), 
        tooltip = candlesticks_tooltips)
    
    price_data = pd.DataFrame({
        'type': ['bid', 'ask'], 
        'price': [bid, ask],
        'bid': [bid, bid],
        'ask': [ask, ask]})

    price_lines = alt.Chart(price_data).mark_rule(clip = True).encode(
        y = 'price:Q',
        color = price_line_color, 
        tooltip = price_lines_tooltips)
    
    #TODO: BACKGROUND COLOR BASED ON MARKET HOURS OR CLOSED MARKET

    chart = (sticks + candles + price_lines).properties(title = alt.TitleParams(text = name, anchor = 'middle'))

    return(chart)

@st.fragment(run_every = POLLING_INTERVAL)
def generate_graph_in_fragment(symbol, timeframe, graph_range, timezone, data_scale, graph_colors, normalization_base_name = None):

    if st.session_state['reload_Bars']:
        st.session_state['bars_data'] = Bars(symbol, timeframe, graph_range, timezone, data_scale, normalization_base_name)
        st.session_state['reload_Bars'] = False

    bars_data = st.session_state['bars_data']
    bars_data.update()
    graph = altair_candlestick_graph(bars_data, graph_colors)
    st.altair_chart(graph, width = 'stretch', height = GRAPH_HEIGHT)#, key = 'graph')
    #st.write(bars_data.bars.iloc[::-1])










