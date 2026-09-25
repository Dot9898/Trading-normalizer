

import pandas as pd
import streamlit as st
import altair as alt
from constants import CHART_STYLE, POLLING_INTERVAL
from backend import scale_point_wrt_current_values
from get_live_data import Bars, get_remaining_candle_time
from format_functions import timezone_format


def get_base_chart(bars_data):

    colors = CHART_STYLE['colors']['candlesticks']
    chart_values = CHART_STYLE['others']
    bars = bars_data.bars
    dummy_bars = bars_data.dummy_bars
    date_label = bars_data.date_label
    timezone = bars_data.timezone
    all_bars = pd.concat([bars[['axis_label', 'time']], dummy_bars[['axis_label', 'time']]])
    sorted_labels = all_bars.sort_values('time')['axis_label']

    candlestick_color = (
        alt.when('datum.is_positive')
        .then(alt.value(colors['fill_positive']))
        .otherwise(alt.value(colors['fill_negative'])))   

    stroke_color = (
        alt.when('datum.is_positive')
        .then(alt.value(colors['stroke_positive']))
        .otherwise(alt.value(colors['stroke_negative'])))

    x_axis = alt.X(
        'axis_label:O', 
        axis = alt.Axis(labelAngle = chart_values['x_labels_angle'], 
                        title = [date_label, f'{timezone_format(timezone)} time']), 
        scale = alt.Scale(domain = sorted_labels, 
                            paddingInner = chart_values['candlesticks_inner_padding'], 
                            paddingOuter = chart_values['candlesticks_outer_padding']), 
        sort = alt.SortField('time', order = 'ascending'))
    
    base = alt.Chart(bars).encode(
        x_axis, 
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

def lines_layer(lines_data):

    pixels = CHART_STYLE['pixels']
    colors = CHART_STYLE['colors']['lines']
    opacity = CHART_STYLE['opacity']['lines']

    font_size = (pixels['line_labels_font_size_big'] if ('bid' in lines_data.index or 'ask' in lines_data.index) 
                 else pixels['line_labels_font_size'])
    baseline = 'top' if 'bid' in lines_data.index else 'bottom'
    lines_label_dy = -pixels['line_labels_dy'] if 'bid' in lines_data.index else pixels['line_labels_dy']

    lines_color = alt.Color(
        'line_type:N', 
        scale = alt.Scale(
            domain = list(colors.keys()), 
            range = list(colors.values())), 
        legend = None)

    lines_opacity = alt.Opacity(
        'line_type:N', 
        scale = alt.Scale(
            domain = list(opacity.keys()), 
            range = list(opacity.values())))

    lines = alt.Chart(lines_data).mark_rule(clip = True, tooltip = None).encode(
        y = 'price:Q',
        color = lines_color, 
        opacity = lines_opacity)

    labels = alt.Chart(lines_data).mark_text(
        clip = True, 
        lineBreak = '\n',
        align = 'right', 
        fontSize = font_size, 
        baseline = baseline, 
        dx = pixels['line_labels_dx'], 
        dy = lines_label_dy, 
        tooltip = None)

    labels = labels.encode(
        x = alt.X(value = 'width'), 
        y = 'price:Q', 
        color = lines_color, 
        opacity = lines_opacity, 
        text = 'label:N')

    return(lines + labels)

def altair_candlestick_graph(bars_data: Bars, price_range, lines_data):

    if price_range == 'auto':
        price_range = [bars_data.min_price, bars_data.max_price]

    base = get_base_chart(bars_data)
    candlesticks = candlesticks_layer(base, price_range, bars_data.data_scale)

    bid_line = lines_layer(lines_data['bid'])
    ask_line = lines_layer(lines_data['ask'])
    SLTP_lines = lines_layer(lines_data['current_levels'])
    trades_and_alert_lines = lines_layer(lines_data['trades_and_alerts_levels'])

    chart = (candlesticks + SLTP_lines + trades_and_alert_lines + ask_line + bid_line).properties(
             title = alt.TitleParams(text = bars_data.name, 
                                     anchor = 'middle', 
                                     offset = CHART_STYLE['pixels']['title_offset']))

    return(chart)


@st.fragment(run_every = POLLING_INTERVAL)
def generate_graph_in_fragment(symbol, 
                               timeframe, 
                               graph_range, 
                               timezone, 
                               data_scale, 
                               normalization_base_name, 
                               price_range, 
                               lines_data):

    if st.session_state['reload_Bars']:
        st.session_state['bars_data'] = Bars(symbol, timeframe, graph_range, timezone, data_scale, normalization_base_name)
        st.session_state['reload_Bars'] = False

    bars_data = st.session_state['bars_data']
    bars_data.update()
    update_lines_data('current_prices')

    if bars_data.too_many_bars:
        st.subheader('')
        st.subheader('')
        st.subheader('Candlestick count is too big to load', text_alignment = 'center')
        st.subheader('Please select a smaller window or a larger timeframe', text_alignment = 'center')
    else:
        graph = altair_candlestick_graph(bars_data, price_range, lines_data)
        st.altair_chart(graph, width = 'stretch', height = CHART_STYLE['pixels']['height'], key = 'graph')


def load_lines_data():
    bid = pd.DataFrame(index = ['bid'], columns = ['line_type', 'price', 'label'])
    ask = pd.DataFrame(index = ['ask'], columns = ['line_type', 'price', 'label'])
    current_levels = pd.DataFrame(index = ['SL', 'TP', 'entry', 'alert_price'], 
                                  columns = ['line_type', 'price', 'label'])
    trades_and_alerts_levels = pd.DataFrame(columns = ['line_type', 'price', 'label'])

    lines_data = {'bid': bid, 
                  'ask': ask, 
                  'current_levels': current_levels, 
                  'trades_and_alerts_levels': trades_and_alerts_levels}

    st.session_state['lines_data'] = lines_data

def update_lines_data(category):
    """Order matters for layering"""

    lines_data = st.session_state['lines_data']
    bars = st.session_state['bars_data']

    if category == 'current_prices':
        ask_data = lines_data['ask']
        bid_data = lines_data['bid']

        ask = bars.current_ask
        bid = bars.current_bid
        ask_data.loc['ask'] = ['ask', ask, f'{ask}']
        bid_data.loc['bid'] = ['bid', bid, f'{bid}\n{get_remaining_candle_time(bars.timeframe)}']

    if category == 'current_levels':
        if not st.session_state['show_SLTP_lines']:
            lines_data['current_levels'] = pd.DataFrame(index = ['SL', 'TP', 'entry', 'alert_price'], 
                                                        columns = ['line_type', 'price', 'label'])
            return
        
        levels_data = lines_data['current_levels']

        SL = round(st.session_state['SL'], bars.shown_digits)
        TP = round(st.session_state['TP'], bars.shown_digits)
        entry = round(st.session_state['entry'], bars.shown_digits)

        levels_data.loc['SL'] = ['SL', SL, f'SL {SL}']
        levels_data.loc['TP'] = ['TP', TP, f'TP {TP}']
        levels_data.loc['entry'] = ['entry', entry, f'Entry {entry}']
        
        if st.session_state['alerts_checkbox']:
            if 'alert_price' in st.session_state:
                alert_price = round(st.session_state['alert_price'], bars.shown_digits)
            else:
                alert_price = bars.current_bid
            levels_data.loc['alert_price'] = ['alert_price', alert_price, f'Set alert at {alert_price}']
        else:
            levels_data.loc['alert_price'] = ['alert_price', None, '']

    if category == 'trades_and_alerts_levels':
        data_table = st.session_state['data_table']
        table_levels_data = {}

        for row in data_table.itertuples():
            status = row.Status
            if status == 'Closed':
                continue
            source = row.source_object
            if source.symbol != st.session_state['selected_symbol']:
                continue
            
            if status == 'Open':
                trade = source
                ticket = trade.Index
                direction = trade.direction.capitalize()

                SL = scale_point_wrt_current_values(trade.SL_abs, rounded = True)
                TP = scale_point_wrt_current_values(trade.TP_abs, rounded = True)
                table_levels_data[f'{ticket}_SL'] = ['open_SL', SL, f'{direction} SL {SL}']
                table_levels_data[f'{ticket}_TP'] = ['open_TP', TP, f'{direction} TP {TP}']

            if status == 'Alert':
                alert = source
                ticket = alert.ticket

                alert_price = scale_point_wrt_current_values(source.absolute_price, rounded = True)
                table_levels_data[ticket] = ['placed_alert', alert_price, f'Alert {alert_price}']

            if status == 'Pending':
                trade = source
                ticket = trade.Index
                direction = trade.direction.capitalize()
                order_type = trade.order_type

                SL = scale_point_wrt_current_values(trade.SL_abs, rounded = True)
                TP = scale_point_wrt_current_values(trade.TP_abs, rounded = True)
                entry = scale_point_wrt_current_values(trade.set_price, rounded = True)
                table_levels_data[f'{ticket}_SL'] = ['pending_SL', SL, f'{direction} {order_type} SL {SL}']
                table_levels_data[f'{ticket}_TP'] = ['pending_TP', TP, f'{direction} {order_type} TP {TP}']
                table_levels_data[f'{ticket}_entry'] = ['pending_entry', entry, f'{direction} {order_type} {entry}']

            if status == 'Conditional trade':
                alert = source
                ticket = alert.ticket
                direction = alert.conditional_trade_data['direction']
                order_type = alert.order_type

                trigger_price = scale_point_wrt_current_values(source.absolute_price, rounded = True)
                table_levels_data[ticket] = ['placed_alert', trigger_price, f'Set {direction} {order_type} {trigger_price}']

        lines_data['trades_and_alerts_levels'] = pd.DataFrame.from_dict(table_levels_data,
                                                                        columns = ['line_type', 'price', 'label'], 
                                                                        orient = 'index')








