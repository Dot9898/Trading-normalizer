

import altair as alt
import pandas as pd
import streamlit as st

from backend import scale_point_wrt_current_values
from constants import CHART_STYLE, POLLING_INTERVAL, SECONDS
from format_functions import timezone_format
from get_live_data import Bars, get_remaining_candle_time


class Layers:   #Can be made better. It's enough for this use case.

    def __init__(self):

        self.empty_layer = alt.layer()
        self.base = alt.layer()
        self.candlesticks = alt.layer()
        self.bid_line = alt.layer()
        self.ask_line = alt.layer()
        self.SL_TP_entry_alert_lines = alt.layer()
        self.alert_line = alt.layer()
        self.trades_and_alerts_lines = alt.layer()
        self.closed_trades_segments = alt.layer()

        self.x_categories = None
        self.lines_data = {}
        self.update_pending = {}
        self.redundant_update = False

        self.show_SL_TP_lines = True
        self.show_closed_trades = False #Overwritten in first_run

        self.load_lines_data()
        self.set_updates_to_false()
        

    def load_lines_data(self):
        columns = ['line_type', 'price', 'label']
        bid = pd.DataFrame(index = ['bid'], columns = columns)
        ask = pd.DataFrame(index = ['ask'], columns = columns)
        SL_TP_entry = pd.DataFrame(index = ['SL', 'TP', 'entry'], columns = columns)
        alert = pd.DataFrame(index = ['alert_price'], columns = columns)
        trades_and_alerts_levels = pd.DataFrame(columns = columns)
        closed_trades = pd.DataFrame(columns = columns + ['open_axis_label', 'close_axis_label', 'label'])

        lines_data = {'bid': bid, 
                      'ask': ask, 
                      'SL_TP_entry': SL_TP_entry, 
                      'alert': alert, 
                      'trades_and_alerts_levels': trades_and_alerts_levels, 
                      'closed_trades': closed_trades}

        self.lines_data = lines_data

    def set_updates_to_false(self):
        self.update_pending = {'candlesticks': False, 
                               'bid_and_ask_lines': False, 
                               'SL_TP_lines': False, 
                               'alert_line': False, 
                               'trades_and_alerts_lines': False, 
                               'closed_trades_lines': False}


def update_lines_data(category):
    """Order matters for layering"""

    layers = st.session_state['graph_layers']
    bars = st.session_state['bars_data']
    lines_data = layers.lines_data

    if category == 'bid_and_ask':
        ask_data = lines_data['ask']
        bid_data = lines_data['bid']

        ask = bars.current_ask
        bid = bars.current_bid
        extra_label = get_remaining_candle_time(bars.timeframe) if bars.is_market_open else 'Market closed'
        ask_data.loc['ask'] = ['ask', ask, f'{ask}']
        bid_data.loc['bid'] = ['bid', bid, f'{bid}\n{extra_label}']

        layers.update_pending['bid_and_ask_lines'] = True

    if category == 'SL_TP_entry':
        levels_data = lines_data['SL_TP_entry']

        SL = round(st.session_state['SL'], bars.shown_digits)
        TP = round(st.session_state['TP'], bars.shown_digits)
        entry = round(st.session_state['entry'], bars.shown_digits)
        direction = 'buy' if TP >= SL else 'sell'

        levels_data.loc['SL'] = ['SL', SL, f'SL {SL}']
        levels_data.loc['TP'] = ['TP', TP, f'TP {TP}']
        levels_data.loc['entry'] = [f'entry_{direction}', entry, f'Entry {entry}']

        layers.update_pending['SL_TP_lines'] = True

    if category == 'alert':
        alert_data = lines_data['alert']

        if st.session_state['alerts_checkbox']:
            if 'alert_price' in st.session_state:
                alert_price = round(st.session_state['alert_price'], bars.shown_digits)
            else:
                alert_price = bars.current_bid
            alert_data.loc['alert_price'] = ['alert_price', alert_price, f'Set alert at {alert_price}']
        else:
            alert_data.loc['alert_price'] = ['alert_price', None, '']

        layers.update_pending['alert_line'] = True

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
                table_levels_data[f'{ticket}'] = ['placed_alert', alert_price, f'Alert {alert_price}']

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
                table_levels_data[f'{ticket}_entry'] = [f'pending_entry_{trade.direction}', entry, f'{direction} {order_type} {entry}']

            if status == 'Conditional trade':
                alert = source
                ticket = alert.ticket
                direction = alert.conditional_trade_data['direction']
                order_type = alert.conditional_trade_data['order_type']

                trigger_price = scale_point_wrt_current_values(source.absolute_price, rounded = True)
                table_levels_data[f'{ticket}'] = ['conditional_trade_trigger', trigger_price, 
                                                  f'Set {direction} {order_type} {trigger_price}']
        
        lines_data['trades_and_alerts_levels'] = pd.DataFrame.from_dict(table_levels_data,
                                                                        columns = ['line_type', 'price', 'label'], 
                                                                        orient = 'index')

        layers.update_pending['trades_and_alerts_lines'] = True

    if category == 'closed_trades':
        data_table = st.session_state['data_table']
        PL_column_number = data_table.columns.get_loc('P/L') + 1
        time_to_category = bars.time_to_axis_label
        closed_trades_data = {}

        for row in data_table.itertuples():
            status = row.Status
            if status != 'Closed':
                continue
            trade = row.source_object
            if trade.symbol != st.session_state['selected_symbol']:
                continue

            open_time = trade.open_server_time
            close_time = trade.close_server_time
            rounded_open_time = open_time - open_time % SECONDS[bars.timeframe]
            rounded_close_time = close_time - close_time % SECONDS[bars.timeframe]
            if rounded_open_time in time_to_category and rounded_close_time in time_to_category:
                open_axis_label = time_to_category[rounded_open_time]
                close_axis_label = time_to_category[rounded_close_time]
            else:
                continue

            ticket = trade.Index
            PL_percent_string = row[PL_column_number]
            PL_percent = float(PL_percent_string[:-1])
            line_type = ('positive_trade' if PL_percent > 0 
                         else 'negative_trade' if PL_percent < 0 
                         else 'neutral_trade')
            open_price = scale_point_wrt_current_values(trade.open_price, rounded = True)
            close_price = scale_point_wrt_current_values(trade.close_price, rounded = True)

            closed_trades_data[f'{ticket}'] = [line_type, open_price, close_price, 
                                               open_axis_label, close_axis_label, PL_percent_string]

        lines_data['closed_trades'] = pd.DataFrame.from_dict(closed_trades_data,
                                                             columns = ['line_type', 'open_price', 'close_price', 
                                                                        'open_axis_label', 'close_axis_label', 'label'], 
                                                             orient = 'index')

        layers.update_pending['closed_trades_lines'] = True


def get_base_chart(bars_data, x_categories):

    colors = CHART_STYLE['colors']
    chart_values = CHART_STYLE['others']
    bars = bars_data.bars
    date_label = bars_data.date_label if bars_data.date_label is not None else ''
    timezone = bars_data.timezone

    candlestick_color = (
        alt.when('datum.is_positive')
        .then(alt.value(colors['candlesticks']['fill_positive']))
        .otherwise(alt.value(colors['candlesticks']['fill_negative'])))   

    stroke_color = (
        alt.when('datum.is_positive')
        .then(alt.value(colors['candlesticks']['stroke_positive']))
        .otherwise(alt.value(colors['candlesticks']['stroke_negative'])))

    x_axis = alt.X(
        'axis_label:O', 
        axis = alt.Axis(labelAngle = chart_values['x_labels_angle'], 
                        labelColor = colors['labels']['x_axis'], 
                        title = [date_label, f'{timezone_format(timezone)} time'], 
                        titleColor = colors['labels']['x_axis']), 
        scale = alt.Scale(domain = x_categories, 
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

    colors = CHART_STYLE['colors']

    candlesticks_tooltips = [
        alt.Tooltip('date_label:N', title = 'Date'),
        alt.Tooltip('time_label:N', title = 'Time'),
        alt.Tooltip('open:Q', title = 'Open'),
        alt.Tooltip('high:Q', title = 'High'),
        alt.Tooltip('low:Q', title = 'Low'),
        alt.Tooltip('close:Q', title = 'Close')]
    
    candles = base.mark_bar(clip = True).encode(
        alt.Y('open:Q', 
            axis = alt.Axis(title = f'Price ({data_scale})', 
                            titleColor = colors['labels']['y_axis'], 
                            labelColor = colors['labels']['y_axis']), 
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
    labels_colors = colors.copy()

    labels_colors['bid'] = CHART_STYLE['colors']['labels']['bid']
    labels_colors['ask'] = CHART_STYLE['colors']['labels']['ask']
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

    labels_color = alt.Color(
        'line_type:N', 
        scale = alt.Scale(
            domain = list(labels_colors.keys()), 
            range = list(labels_colors.values())), 
        legend = None)

    lines_opacity = alt.Opacity(
        'line_type:N', 
        scale = alt.Scale(
            domain = list(opacity.keys()), 
            range = list(opacity.values()), 
            type = 'ordinal'), 
        legend = None)

    lines = alt.Chart(lines_data).mark_rule(clip = True, tooltip = None).encode(
        y = 'price:Q',
        color = lines_color, 
        opacity = lines_opacity)

    labels = alt.Chart(lines_data).mark_text(
        clip = True, 
        tooltip = None, 
        lineBreak = '\n', 
        align = 'right', 
        fontSize = font_size, 
        baseline = baseline, 
        dx = pixels['line_labels_dx'], 
        dy = lines_label_dy).encode(
        
        x = alt.X(value = 'width'), 
        y = 'price:Q', 
        color = labels_color, 
        opacity = lines_opacity, 
        text = 'label:N')

    lines_and_labels = (lines + labels).resolve_scale(color = 'independent')
    return(lines_and_labels)

def segments_layer(segments_data, x_categories):

    pixels = CHART_STYLE['pixels']
    colors = CHART_STYLE['colors']['lines']
    opacity = CHART_STYLE['opacity']['lines']

    segments_color = alt.Color(
        'line_type:N',
        scale = alt.Scale(
            domain = list(colors.keys()),
            range = list(colors.values())),
        legend = None)

    segments_opacity = alt.Opacity(
        'line_type:N',
        scale = alt.Scale(
            domain = list(opacity.keys()),
            range = list(opacity.values()), 
            type = 'ordinal'), 
        legend = None)

    segments = alt.Chart(segments_data).mark_rule(clip = True, tooltip = None).encode(
        x = alt.X('open_axis_label:O', scale = alt.Scale(domain = x_categories)), 
        x2 = 'close_axis_label:O', 
        y = 'open_price:Q', 
        y2 = 'close_price:Q', 
        color = segments_color, 
        opacity = segments_opacity, 
        strokeWidth = alt.value(pixels['diagonal_lines_width']))

    start_circles = alt.Chart(segments_data).mark_point(
        clip = True, 
        tooltip = None, 
        shape = 'circle', 
        filled = True, 
        size = pixels['line_endpoints_radius']).encode(
        
        x = 'open_axis_label:O', 
        y = 'open_price:Q', 
        color = segments_color, 
        opacity = segments_opacity).transform_filter(
        'datum.open_axis_label != datum.close_axis_label')
    
    end_circles = alt.Chart(segments_data).mark_point(
        clip = True, 
        tooltip = None, 
        shape = 'circle', 
        filled = True, 
        size = pixels['line_endpoints_radius']).encode(
        
        x = 'close_axis_label:O', 
        y = 'close_price:Q', 
        color = segments_color, 
        opacity = segments_opacity)

    labels = alt.Chart(segments_data).mark_text(
        clip = True, 
        tooltip = None, 
        align = 'left', 
        fontSize = pixels['line_labels_font_size_big'], 
        baseline = 'middle', 
        dx = pixels['diagonal_lines_labels_dx'], 
        dy = 0).encode(
        
        x = 'close_axis_label:O', 
        y = 'close_price:Q', 
        color = segments_color, 
        opacity = segments_opacity, 
        text = 'label:N')

    return(segments + start_circles + end_circles + labels)


def altair_candlestick_graph(bars_data: Bars, layers: Layers, price_range):

    if layers.update_pending['candlesticks'] or layers.redundant_update: #This block has to run twice when
        layers.redundant_update = not layers.redundant_update            #the candlesticks layer is updated.
                                                                         #It fixes an extremely weird bug.
        
        x_categories = pd.concat([bars_data.bars[['axis_label', 'time']], 
                                  bars_data.dummy_bars[['axis_label', 'time']]])
        layers.x_categories = x_categories.sort_values('time')['axis_label']

        base = get_base_chart(bars_data, layers.x_categories)
        if price_range == 'auto':
            price_range = [bars_data.min_price, bars_data.max_price]
        layers.candlesticks = candlesticks_layer(base, price_range, bars_data.data_scale)

    if layers.update_pending['bid_and_ask_lines']:
        layers.bid_line = lines_layer(layers.lines_data['bid'])
        layers.ask_line = lines_layer(layers.lines_data['ask'])

    if layers.update_pending['SL_TP_lines']:
        layers.SL_TP_entry_alert_lines = lines_layer(layers.lines_data['SL_TP_entry'])

    if layers.update_pending['alert_line']:
        layers.alert_line = lines_layer(layers.lines_data['alert'])

    if layers.update_pending['trades_and_alerts_lines']:
        layers.trades_and_alerts_lines = lines_layer(layers.lines_data['trades_and_alerts_levels'])

    if layers.update_pending['closed_trades_lines']:
        layers.closed_trades_segments = segments_layer(layers.lines_data['closed_trades'], layers.x_categories)

    layers.set_updates_to_false()

    SL_TP_entry_alert_layer = layers.SL_TP_entry_alert_lines if layers.show_SL_TP_lines else layers.empty_layer
    closed_trades_layer = layers.closed_trades_segments if layers.show_closed_trades else layers.empty_layer

    chart = (layers.candlesticks 
             + closed_trades_layer 
             + SL_TP_entry_alert_layer 
             + layers.trades_and_alerts_lines 
             + layers.alert_line 
             + layers.bid_line 
             + layers.ask_line).properties(title = alt.TitleParams(text = bars_data.name, 
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
                               layers):

    if st.session_state['reload_Bars']:
        st.session_state['bars_data'] = Bars(symbol, timeframe, graph_range, timezone, data_scale, normalization_base_name)
        st.session_state['reload_Bars'] = False

    bars_data = st.session_state['bars_data']
    bars_data.update()
    if bars_data.just_full_updated:
        bars_data.just_full_updated = False
        layers.update_pending['candlesticks'] = True
        if not st.session_state['first_run']:
            update_lines_data('closed_trades')
    update_lines_data('bid_and_ask')

    if bars_data.too_many_bars:
        st.subheader('')
        st.subheader('')
        st.subheader('Candlestick count is too big to load', text_alignment = 'center')
        st.subheader('Please select a smaller window or a larger timeframe', text_alignment = 'center')
        st.subheader('')
        st.subheader('')
    else:
        graph = altair_candlestick_graph(bars_data, layers, price_range)
        st.altair_chart(graph, width = 'stretch', height = CHART_STYLE['pixels']['height'], key = 'graph')








