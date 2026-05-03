

import MetaTrader5 as mt5

CHART_COLORS = {'fill': {'green_and_red': {'positive': '#06982d', 'negative': '#ae1325'}, 
                        'black_and_white': {'positive': '#FFFFFF', 'negative': '#000000'}}, 
                'stroke': {'green_and_red': {'positive': '#06982d', 'negative': '#ae1325'}, 
                        'black_and_white': {'positive': '#000000', 'negative': '#000000'}}, 
                'price_lines': {'bid': '#0000ff', 'ask': '#ff0000'}}

CHART_AXIS_TIME_FORMAT = {mt5.TIMEFRAME_M1: '%H:%M', 
                          mt5.TIMEFRAME_M5: '%H:%M', 
                          mt5.TIMEFRAME_M15: '%H:%M', }
  #                        mt5.TIMEFRAME_H1: 1, 
   #                       mt5.TIMEFRAME_H4: 1.0/4, 
    #                      mt5.TIMEFRAME_D1: 1.0/24, 
     #                     mt5.TIMEFRAME_W1: 1.0/(24 * 7), 
      #                    mt5.TIMEFRAME_MN1: 1.0/(24 * 30)}
#'%m/%d'


BARS_PER_HOUR = {mt5.TIMEFRAME_M1: 60, 
                 mt5.TIMEFRAME_M5: 12, 
                 mt5.TIMEFRAME_M15: 4, 
                 mt5.TIMEFRAME_H1: 1, 
                 mt5.TIMEFRAME_H4: 1.0/4, 
                 mt5.TIMEFRAME_D1: 1.0/24, 
                 mt5.TIMEFRAME_W1: 1.0/(24 * 7), 
                 mt5.TIMEFRAME_MN1: 1.0/(24 * 30)}

SECONDS = {mt5.TIMEFRAME_M1: 60, 
           mt5.TIMEFRAME_M5: 300, 
           mt5.TIMEFRAME_M15: 900, 
           mt5.TIMEFRAME_H1: 3600, 
           mt5.TIMEFRAME_H4: 3600 * 4, 
           mt5.TIMEFRAME_D1: 3600 * 24, 
           mt5.TIMEFRAME_W1: 3600 * 24 * 7, 
           mt5.TIMEFRAME_MN1: 3600 * 24 * 30}











