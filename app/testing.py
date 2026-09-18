

import pandas as pd
import streamlit as st
from backend import floor_with_step


def round_balance(number):
    if number < 1:
        return(0)
    if number < 50:
        return(round(number))
    
    rounded_balance = str(round(number))
    digits_qty = len(rounded_balance)
    power = digits_qty - 2
    first_digit = int(rounded_balance[0])
    
    if first_digit == 1:
        step = 5
        power = power - 1
    elif first_digit in [2, 3, 4]:
        step = 1
    else:
        step = 2

    step = step * 10 ** power
    return(int(floor_with_step(number, step)))


test_values = [5, 27, 97, 107, 378, 450, 893, 1181, 1513, 2270, 2370]

for value in test_values:
    print(value, 'rounded:', round_balance(value))


