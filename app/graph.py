

import pandas as pd
import streamlit as st
import altair as alt
from constants import CHART_CANDLESTICK_COLORS, CHART_LINES_COLORS, CHART_LINES_OPACITY, POLLING_INTERVAL, GRAPH_HEIGHT, GRAPH_TITLE_SEPARATION, WHITE_SPACE
from get_live_data import Bars
from format_functions import timezone_format



#add constants of padding etc
#check subfunctions parameters order etc and clean main function



def get_base_chart(bars, colors, date_label, timezone):

    candlestick_color = (
        alt.when('datum.is_positive')
        .then(alt.value(CHART_CANDLESTICK_COLORS['fill'][colors]['positive']))
        .otherwise(alt.value(CHART_CANDLESTICK_COLORS['fill'][colors]['negative'])))   

    stroke_color = (
        alt.when('datum.is_positive')
        .then(alt.value(CHART_CANDLESTICK_COLORS['stroke'][colors]['positive']))
        .otherwise(alt.value(CHART_CANDLESTICK_COLORS['stroke'][colors]['negative'])))
    
    base = alt.Chart(bars).encode(
        alt.X('axis_label:O', 
            axis = alt.Axis(labelAngle = 0, title = [date_label, f'{timezone_format(timezone)} time']), 
            scale = alt.Scale(paddingInner = 0.35, paddingOuter = 0.5), 
            sort = alt.SortField('time', order = 'ascending')), 
        color = candlestick_color, 
        stroke = stroke_color
    ).transform_calculate(
        is_positive = 'datum.open <= datum.close')

    return(base)

def candlesticks_layer(base: alt.Chart, price_range, data_scale):

    candlesticks_tooltips = [
        alt.Tooltip('date_label:N', title = 'Date'),
        alt.Tooltip('time_label:N', title = 'Time'),
        alt.Tooltip('open:Q', title = 'Open'),
        alt.Tooltip('high:Q', title = 'High'),
        alt.Tooltip('low:Q', title = 'Low'),
        alt.Tooltip('close:Q', title = 'Close')]
    
    candles = base.mark_bar(clip = True).encode(
        alt.Y('open:Q', 
            axis = alt.Axis(title = f'Price ({data_scale})'), 
            scale = alt.Scale(domain = price_range, zero = False)), 
        alt.Y2('close:Q'), 
        tooltip = candlesticks_tooltips)

    sticks = base.mark_rule(clip = True).encode(
        alt.Y('high:Q'),
        alt.Y2('low:Q'), 
        tooltip = candlesticks_tooltips)

    return(sticks + candles)



def price_lines_layer(bid, ask, shown_digits):

    price_lines_color = alt.Color(
        'type:N',
        scale = alt.Scale(
            domain = ['bid', 'ask'],
            range = [CHART_LINES_COLORS['bid'], CHART_LINES_COLORS['ask']]), 
        legend = None)

    price_lines_tooltips = [
        alt.Tooltip('ask:Q', format = f'.{shown_digits}f', title = 'Ask'), 
        alt.Tooltip('bid:Q', format = f'.{shown_digits}f', title = 'Bid')]
    
    price_data = pd.DataFrame({
        'type': ['bid', 'ask'], 
        'price': [bid, ask],
        'bid': [bid, bid],
        'ask': [ask, ask]})

    price_lines = alt.Chart(price_data).mark_rule(clip = True).encode(
        y = 'price:Q',
        color = price_lines_color, 
        tooltip = price_lines_tooltips)

    return(price_lines)




#add constants for everything
#formato: df line_type price label
def lines_layer(lines_data): #change line data on data table full update #key = 'graph_lines_data'

    lines_color = alt.Color(
        'line_type:N', 
        scale = alt.Scale(
            domain = list(CHART_LINES_COLORS.keys()), 
            range = list(CHART_LINES_COLORS.values())), 
        legend = None)

    lines_opacity = alt.Opacity(
        'line_type:N', 
        scale = alt.Scale(
            domain = list(CHART_LINES_OPACITY.keys()), 
            range = list(CHART_LINES_OPACITY.values())))

    lines = alt.Chart(lines_data).mark_rule(clip = True, tooltip = None).encode(
        y = 'price:Q',
        color = lines_color, 
        opacity = lines_opacity)

    labels = alt.Chart(lines_data).mark_text(
        clip = True, 
        align = 'right', 
        baseline = 'bottom', 
        dx = -2, 
        dy = -3, 
        fontSize = 13, 
        tooltip = None)

    labels = labels.encode(
        x = alt.X(value = 'width'), 
        y = 'price:Q', 
        color = lines_color, 
        opacity = lines_opacity, 
        text = 'label:N')

    return(lines + labels)




def altair_candlestick_graph(bars_data: Bars, price_range, colors):

    bars = bars_data.bars
    name = bars_data.name
    timezone = bars_data.timezone
    data_scale = bars_data.data_scale
    if price_range == 'auto':
        price_range = [bars_data.min_price, bars_data.max_price]
    date_label = '' if bars_data.date_label is None else bars_data.date_label
    bid = bars_data.current_bid
    ask = bars_data.current_ask

    price_data = pd.DataFrame({
        'line_type': ['bid', 'ask'], 
        'price': [bid, ask], 
        'label': ['bidd', 'ask']})

    if 'SL' in st.session_state and 'TP' in st.session_state:
        SL = st.session_state['SL']
        TP = st.session_state['TP']
    else:
        SL = 0
        TP = 0
    SLTP_data = pd.DataFrame({
        'line_type': ['SL', 'TP'], 
        'price': [SL, TP], 
        'label': [f'SL{WHITE_SPACE}{SL}', f'TP{WHITE_SPACE}{TP}']})
    



    #TODO: BACKGROUND COLOR BASED ON MARKET HOURS OR CLOSED MARKET

    base = get_base_chart(bars, colors, date_label, timezone)
    candlesticks = candlesticks_layer(base, price_range, data_scale)
    price_lines = lines_layer(price_data)
    SLTP_lines = lines_layer(SLTP_data)


    chart = (candlesticks + SLTP_lines + price_lines).properties(title = alt.TitleParams(text = name, anchor = 'middle', offset = GRAPH_TITLE_SEPARATION))

    return(chart)

@st.fragment(run_every = POLLING_INTERVAL)
def generate_graph_in_fragment(symbol, timeframe, graph_range, timezone, data_scale, normalization_base_name, price_range, graph_colors):

    if st.session_state['reload_Bars']:
        st.session_state['bars_data'] = Bars(symbol, timeframe, graph_range, timezone, data_scale, normalization_base_name)
        st.session_state['reload_Bars'] = False

    bars_data = st.session_state['bars_data']
    bars_data.update()
    if bars_data.too_many_bars:
        st.subheader('')
        st.subheader('')
        st.subheader('Candlestick count is too big to load', text_alignment = 'center')
        st.subheader('Please select a smaller window or a larger timeframe', text_alignment = 'center')
    else:
        graph = altair_candlestick_graph(bars_data, price_range, graph_colors)
        st.altair_chart(graph, width = 'stretch', height = GRAPH_HEIGHT)#, key = 'graph')









