import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

import connect
import components
import utils

# construct web application home page
def build_userview():
    bodyweight, home_fitness, lifting, running, profile = connect.unload_data()
    st.title('Health Tracking App')
    # select a user through a dropdown
    user, user_id = components.get_user(profile)
    welcome_msg = st.empty()
    tab_header = st.empty()
    refresh_ele = st.empty()

    if user != 'Select Profile':
        # load profile opt-ins
        homefit_opt = profile[profile.user == user].homefit_opt.iloc[0]
        lift_opt = profile[profile.user == user].lift_opt.iloc[0]
        run_opt = profile[profile.user == user].run_opt.iloc[0]

        # construct user view
        components.write_welcome_msg(welcome_msg, bodyweight, user)
        user_tabs = components.build_tabs(tab_header, profile, user)
        user_bwt_df = components.print_profile(user_tabs[0], bodyweight, profile, user)
        components.weight_journey(user_tabs[1], user_bwt_df)
        components.print_bwt_form(user_tabs[-1], bodyweight, user_id)
        connect.refresh_view(refresh_ele)
        # always 2
        if homefit_opt and lift_opt:
            components.measure_home_fitness(user_tabs[2], home_fitness, profile, user_id)
            components.print_homefit_form(user_tabs[-1], home_fitness, profile, user_id)
            components.build_rbt(user_tabs[3])
        elif not homefit_opt and lift_opt:
            components.build_rbt(user_tabs[2])

        if lift_opt:
            components.print_lift_form(user_tabs[-1], user_id)  
        # always -2
        if run_opt:
            components.running_performance(user_tabs[-2], running, profile, user_id)
            components.print_run_form(user_tabs[-1], user_id)
            
