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
    bodyweight, profile = connect.unload_data()
    #st.write(len(bodyweight))
    
    st.title('Health Tracking App')
    # select a user through a dropdown
    user = st.selectbox('Profile',
                        ['Select Profile',
                         'Wayne Chim',
                         'Joyce Chan',
                         'Vincent Lee',
                         'Suk Chim',
                         'Hing Chim',
                         'Ernest Chim',
                         'Haoxiang Chen'])

    #user_id = profile[profile.user == user].user_id.iloc[0]
    welcome_msg = st.empty()
    tab_header = st.empty()
    refresh_ele = st.empty()

    if user != 'Select Profile':
        # load profile opt-ins
        lift_opt = profile[profile.user == user].lift_opt.iloc[0]
        run_opt = profile[profile.user == user].run_opt.iloc[0]

        # construct user view
        components.write_welcome_msg(welcome_msg, bodyweight, user)
        user_tabs = components.build_tabs(tab_header, profile, user)
        user_df = components.print_profile(user_tabs[0], bodyweight, profile, user)
        components.weight_journey(user_tabs[1], user_df)
        components.print_form(user_tabs[-1], bodyweight, profile, user)
        connect.refresh_view(refresh_ele)
        if lift_opt:
            components.build_rbt(user_tabs[2])
            components.print_lift_form(user_tabs[-1], profile, user)
        if run_opt:
            components.print_run_form(user_tabs[-1], profile, user)
            
