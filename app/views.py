import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

import connect
import graphs
import utils

# construct web application home page
def build_userview():

    #st.write(len(bodyweight))
    st.title('Health Data App')
    # select a user through a dropdown
    user = st.selectbox('Profile',
                        ['Wayne Chim',
                         'Joyce Chan',
                         'Vincent Lee',
                         'Suk Chim',
                         'Hing Chim',
                         'Ernest Chim'])
                        
    bodyweight, profile = connect.unload_data()

    user_id = profile[profile.user == user].user_id.iloc[0]

    if len(bodyweight) == 0:
        new_tab, form_tab = st.tabs(['Welcome','Data Entry'])
        with new_tab:
            st.subheader("Looks like you're new around here, submit your first bodyweight entry to get started!")
    else:
        complete = pd.merge(bodyweight, profile, on=['user_id','user_id'])

        if user_id in (bodyweight.user_id.unique()):
            user_df = complete[complete.user_id == user_id]
            bodyweight_goal = user_df.bw_goal.mean()
            user_df['date'] = [t.date() for t in user_df.timestamp]
            # page tabs
            data_tab, graph_tab, form_tab = st.tabs(['Profile Summary','Weight Journey','Data Entry'])
            with data_tab:
                metr1, metr2, metr3 = st.columns(3)
                # First metric: Most Recent Bodyweight
                recent_wt = user_df['wt_lb'].iloc[-1]
                last_update = str(user_df['date'].iloc[-1])
                metr1.metric('Current Bodyweight', recent_wt)
                metr1.caption(f'Last updated on {last_update}')

                progress = round(recent_wt - bodyweight_goal, 2)
                metr2.metric('Bodyweight Goal', bodyweight_goal, progress, 'inverse')
                
                week_trend = utils.find_n_day_trend(7, user_df['wt_lb'])
                metr3.metric('7-Day Trend', week_trend)

                st.table(user_df)

            with graph_tab:
            # dummy slider
            #st.select_slider('Timeline Range', df.date, (df.date.min(), df.date.max()))
                graphs.weight_journey(user_df)
        else:
            new_tab, form_tab = st.tabs(['Welcome','Data Entry'])
            with new_tab:
                st.subheader("Looks like you're new around here, submit your first bodyweight entry to get started!")
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
                    timestamp = current_time
                    date = str(current_time.date())
                    time_of_day = current_time.strftime('%p')
                    
                    data_entry = {'timestamp': timestamp,
                                'user_id': user_id,
                                'wt_lb': wt_lb,
                                'wt_kg': wt_kg,
                                'date': date,
                                'time_of_day': time_of_day}
                    connect.submit_data(data_entry, 'bodyweight')
                    st.json(data_entry)
                    button_msg.success('Data successfully submitted')
                else:
                    button_msg = st.empty()
                    button_msg.error('Bodyweight must be at least 0')
    
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
