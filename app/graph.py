

import pandas as pd
import altair as alt
from constants import CHART_COLORS, CHART_AXIS_TIME_FORMAT



def generate_graph(bars, colors, timeframe, current_prices):

    candlestick_color = (
        alt.when('datum.is_positive')
        .then(alt.value(CHART_COLORS['fill'][colors]['positive']))
        .otherwise(alt.value(CHART_COLORS['fill'][colors]['negative'])))
    stroke_color = (
        alt.when('datum.is_positive')
        .then(alt.value(CHART_COLORS['stroke'][colors]['positive']))
        .otherwise(alt.value(CHART_COLORS['stroke'][colors]['negative'])))
    prices_color = alt.Color('line_color:N', scale=None)

    base = alt.Chart(bars).encode(
        alt.X('datetime:T', 
            axis = alt.Axis(format = CHART_AXIS_TIME_FORMAT[timeframe], labelAngle = 0, title = None)),
            color = candlestick_color, 
            stroke = stroke_color
        ).transform_calculate(
            is_positive = 'datum.open <= datum.close')
    
    candles = base.mark_bar().encode(
        alt.Y('open:Q', axis = alt.Axis(title = None), scale = alt.Scale(zero = False)),
        alt.Y2('close:Q'))

    sticks = base.mark_rule().encode(
        alt.Y('high:Q'),
        alt.Y2('low:Q'))
    
    prices_data = pd.DataFrame({'price': list(current_prices), 'line_color': [CHART_COLORS['price_lines']['bid'], CHART_COLORS['price_lines']['ask']]})

    price_lines = alt.Chart(prices_data).mark_rule().encode(y = 'price:Q', color = alt.Color('line_color:N', scale = None))

    chart = sticks + candles + price_lines

    return(chart)








