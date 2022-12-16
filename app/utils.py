import streamlit as st

def convert_weight(unit, body_wt):
    if unit == 'Pounds':
        wt_lb = round(body_wt, 2)
        wt_kg = round(body_wt/2.2, 2)
    elif unit == 'Kilograms':
        wt_lb = round(body_wt*2.2, 2)
        wt_kg = round(body_wt, 2)
    return wt_lb, wt_kg