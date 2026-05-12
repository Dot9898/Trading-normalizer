

def get_entry(TP, SL, risk, reward): #Scale independent
    entry = (SL * risk + TP * reward) / (risk + reward)
    return(entry)

def get_lotsize_from_ppb_or_pppt(current_price, equity, pppt = None, ppb = None):
    """
    pppt is (account) percent per point
    If the underlying moves 1 point, how much % does the account win or lose?
    It's a way to normalize risk with respect to account balance: a pppt of 1 represents the same
    on a $100 and a $1000000 account.

    ppb is (account) percent per basis (point). It's a rephrasing of leverage.
    If the underlying moves 1 basis point, how much % does the account win or lose?
    ppb is a way to normalize risk with respect to both account balance and underlying: a ppb of 1 represents
    the same on a $100 and a $1000000 account, and the same too on EURUSD and GOOG.
    However, ppb is not a fixed risk to use for all trades. It still depends on volatility or average daily range:
    EURUSD moves 50-100 basis points in the same time GOOG moves 200-300 basis points.
    """

    if pppt is None and ppb is None:
        lotsize == 0

    elif pppt is None:
        pppt = (10000 / current_price) * ppb
        lotsize = pppt * equity * 0.01

    elif ppb is None:
        lotsize = pppt * equity * 0.01

    else:
        lotsize = 0

    return(lotsize)

def get_ppb_from_trade_risk(max_loss, TP, SL, rr): #ppb = (maxwin - maxloss) / (TP - SL)
    ppb = -max_loss * (1 + 1/rr) / abs(TP - SL)
    return(ppb)

def get_lotsize_from_trade_risk(max_loss, TP, SL, rr, current_price, equity):
    ppb = get_ppb_from_trade_risk(max_loss, TP, SL, rr)
    lotsize = get_lotsize_from_ppb_or_pppt(current_price, equity, ppb = ppb)
    return(lotsize)

def get_current_ppb_from_lotsize(lotsize, current_price, equity):
    ppb = lotsize * current_price * 0.01 / equity
    return(ppb)

def get_available_fraction_of_account(open_trades_data):
    base = 1
    #to get used ppb use lotsize of open trades
    for used_ppb, margin_req in open_trades_data:
        base = base - used_ppb * margin_req
    return(base)

def get_max_ppb(margin_req):
    return(1/margin_req)

def get_max_usable_ppb(open_trades_data, margin_req):
    return(get_available_fraction_of_account(open_trades_data) * get_max_ppb(margin_req))





#frontend show:
#TP, SL widgets
#RR widget
#maxloss widget
#ppb of selected risk
#max ppb available for the given stock
#used fraction of account

#absolute equivalents? just show lotsize and max lotsize prob

























