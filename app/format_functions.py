


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


