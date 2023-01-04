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

    #st.write(len(bodyweight))
    st.title('Health Data App')
    # select a user through a dropdown
    user = st.selectbox('Profile',
                        ['Select Profile',
                         'Wayne Chim',
                         'Joyce Chan',
                         'Vincent Lee',
                         'Suk Chim',
                         'Hing Chim',
                         'Ernest Chim'])

    #bodyweight, profile = connect.unload_data()

    #user_id = profile[profile.user == user].user_id.iloc[0]
    welcome_msg = st.empty()
    tab_header = st.empty()

    if user != 'Select Profile':
        components.write_welcome_msg(welcome_msg, user)
        user_tabs = components.build_tabs(tab_header, user)
        user_df = components.print_profile(user_tabs[0], user)
        components.weight_journey(user_tabs[1], user_df)
        components.print_form(user_tabs[-1], user)
    if st.button('Refresh View'):
        st.experimental_memo.clear()

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
