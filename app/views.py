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

    #bodyweight, profile = connect.unload_data()

    #user_id = profile[profile.user == user].user_id.iloc[0]
    welcome_msg = st.empty()
    tab_header = st.empty()
    refresh_ele = st.empty()

    if user != 'Select Profile':
        components.write_welcome_msg(welcome_msg, bodyweight, user)
        user_tabs = components.build_tabs(tab_header, profile, user)
        user_df = components.print_profile(user_tabs[0], bodyweight, profile, user)
        components.weight_journey(user_tabs[1], user_df)
        components.print_form(user_tabs[-1], bodyweight, profile, user)
        connect.refresh_view(refresh_ele)
        
    ''' if ~fitness_opt:
        data_tab, graph_tab, form_tab = st.tabs(['Profile Summary','Weight Journey','Data Entry'])
    else:
        data_tab, graph_tab, form_tab, exercise_tab= st.tabs(['Profile Summary','Weight Journey','Data Entry','General Exercise Breakdown'])

        with exercise_tab:
            col1, col2 = st.columns(2)
            lifted_wt = col1.number_input(label='Weight Lifted',
                                        min_value=0,
                                        step=1)
            reps = col2.number_input(label='Set Repetitions',
                                   min_value=0,
                                   step=1)
            utils.get_breakdown(lifted_wt, reps)'''
