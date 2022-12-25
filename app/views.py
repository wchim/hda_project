import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

import connect
import graphs
import utils

def load_page_test():
    #items = connect.get_data()
    connect.init_connection()
    #connect.get_data()
    #st.write(items)

def load_page():
    st.set_page_config(layout='centered')
    df = connect.load_gsheet()
    profiles = connect.load_profiles()
    st.title('Health Data App')
    # Select a user through a dropdown
    user = st.selectbox('Select A Profile',
                        ['Wayne Chim','Joyce Chan'])
    fitness_opt = profiles[profiles.user == user].fitness_opt.iloc[0]
    bodyweight_goal = profiles[profiles.user == user].bodyweight_goal.iloc[0]

    new_df = df[df.user == user]

    # Page tabs
    if ~fitness_opt:
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
            utils.get_breakdown(lifted_wt, reps)
    
    with data_tab:
        metr1, metr2, metr3 = st.columns(3)
        # First metric: Most Recent Bodyweight
        recent_wt = new_df['wt_lb'].iloc[-1]
        last_update = str(new_df['date'].iloc[-1].date())
        metr1.metric('Current Bodyweight', recent_wt)
        metr1.caption(f'Last updated on {last_update}')

        progress = round(recent_wt - bodyweight_goal, 2)
        metr2.metric('Bodyweight Goal', bodyweight_goal, progress, 'inverse')
        
        week_trend = utils.find_n_day_trend(7, new_df['wt_lb'])
        metr3.metric('7-Day Trend', week_trend)

    with graph_tab:
        #Dummy slider
        st.select_slider('Timeline Range', df.date, (df.date.min(), df.date.max()))
        graphs.weight_journey(new_df, user, bodyweight_goal)

    with form_tab:
        with st.form('body_wt_form', clear_on_submit=True):
            body_wt = st.number_input(label='Bodyweight',
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
                    connect.submit_data(data_entry, df)
                    st.json(data_entry)
                    button_msg.success('Data successfully submitted')
                    utils.display_fade(button_msg)
                else:
                    button_msg = st.empty()
                    button_msg.error('Bodyweight must be at least 0')
                    utils.display_fade(button_msg)
