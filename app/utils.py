import streamlit as st
import numpy as np

def convert_weight(unit, body_wt):
    if unit == 'Pounds':
        wt_lb = round(body_wt, 2)
        wt_kg = round(body_wt/2.2, 2)
    elif unit == 'Kilograms':
        wt_lb = round(body_wt*2.2, 2)
        wt_kg = round(body_wt, 2)
    return wt_lb, wt_kg

def find_n_day_trend(n, body_wts):
    n_day_trend = body_wts.rolling(n).apply(lambda x: np.polyfit(range(n), x, 1)[0], raw=True).values[-1]
    n_day_trend = round(n_day_trend, 3)
    return n_day_trend