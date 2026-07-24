


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









