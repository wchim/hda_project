import streamlit as st
import numpy as np
from datetime import datetime
from datetime import timedelta
import time

import connect
import graphs
import utils


def load_page():

    df = connect.load_gsheet()
    profiles = connect.load_profiles()
    st.title('Health Data App')
    # Select a user through a dropdown
    user = st.selectbox('Select A Profile',
                        ['Wayne Chim','Joyce Chan'])
    new_df = df[df.user == user]

    # Page tabs
    data_tab, graph_tab, form_tab = st.tabs(['Profile Summary','Weight Journey','Data Entry'])
    with data_tab:
        metr1, metr2, metr3 = st.columns(3)
        # First metric: Most Recent Bodyweight
        recent_wt = new_df['wt_lb'].iloc[-1]
        last_update = str(new_df['date'].iloc[-1].date())
        metr1.metric('Current Bodyweight', recent_wt)
        metr1.caption(f'Last updated on {last_update}')

        bodyweight_goal = profiles[profiles.user == user].bodyweight_goal.iloc[0]
        progress = round(recent_wt - bodyweight_goal, 2)
        metr2.metric('Bodyweight Goal', bodyweight_goal, progress, 'inverse')
        
        week_trend = utils.find_n_day_trend(7, new_df['wt_lb'])
        metr3.metric('7-Day Trend', week_trend)

    with graph_tab:
        #Dummy slider
        st.select_slider('Timeline Range', df.date, (df.date.min(), df.date.max()))
        graphs.weight_journey(new_df, user)

    with form_tab:
        with st.form('body_wt_form', clear_on_submit=True):
            body_wt = st.number_input(label='Body Weight',
                                      min_value=0.0,
                                      step=0.1)
            unit = st.radio('Unit of Measure',
                            ['Pounds','Kilograms'])
        
            form_submit = st.form_submit_button('Submit Data')
            button_msg = st.empty()
            if form_submit:
                if body_wt > 0:
                    wt_lb, wt_kg = utils.convert_weight(unit, body_wt)
                    current_time = datetime.now() - timedelta(hours=4)
                    #current_time = datetime.now()
                    timestamp = str(current_time)
                    date = current_time.date()
                    time_of_day = current_time.strftime('%p')
                    
                    data_entry = {'timestamp': timestamp,
                                  'user': user,
                                  'wt_lb': wt_lb,
                                  'wt_kg': wt_kg,
                                  'date': date,
                                  'time_of_day': time_of_day}
                    #st.json(data_entry)
                    #connect.submit_data(data_entry, df)
                    st.json(data_entry)
                    button_msg.success('Data successfully submitted')
                    time.sleep(3)
                    button_msg.empty()
                else:
                    button_msg = st.empty()
                    button_msg.error('Bodyweight must be at least 0')
                    time.sleep(3)
                    button_msg.empty()
