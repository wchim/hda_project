import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import connect
import utils

# loads mongodb into dataframe
#bodyweight, profile = connect.unload_data()

# visualize comparison across all users
def overall_weight_progression():
        pass

# retrieve user and user id based on profile selected
def get_user(profile):
        user = st.selectbox('Profile',
                        ['Select Profile',
                        'Wayne Chim',
                        'Joyce Chan',
                        'Vincent Lee',
                        'Suk Chim',
                        'Hing Chim',
                        'Ernest Chim',
                        'Haoxiang Chen'])
        if user == 'Select Profile':
                user_id = '000'
        else:
                user_id = profile[profile.user == user].user_id.iloc[0]
        return user, user_id

# write welcome message based on data availability
def write_welcome_msg(element, bodyweight, user):
        bwt_ct = len(bodyweight)
        if bwt_ct == 0:
                element.subheader("Welcome to a fresh start! Let's start tracking data..")
        else:
                element.subheader(f'Welcome back, {user}')

# build tabs as per selected user profile
def build_tabs(element, profile, user):
        homefit_opt = profile[profile.user == user].homefit_opt.iloc[0]
        lift_opt = profile[profile.user == user].lift_opt.iloc[0]
        run_opt = profile[profile.user == user].run_opt.iloc[0]
        tab_ls = ['Profile Summary','Weight Journey','Data Entry']
        # check for lifting performance tracking opt-in
        if homefit_opt:
                tab_ls.insert(len(tab_ls)-1, 'Home Fitness')
        if lift_opt:
                tab_ls.insert(len(tab_ls)-1, 'Lifting Performance')
        # check for running performance tracking opt-in
        if run_opt:
                tab_ls.insert(len(tab_ls)-1, 'Running Performance')
        user_tabs = element.tabs(tab_ls)
        return user_tabs

# print profile summary
def print_profile(tab, bodyweight, profile, user):
        current_time = datetime.now() - timedelta(hours=5)
        today = str(current_time.date())
        user_id = profile[profile.user == user].user_id.iloc[0]
        user_temp = bodyweight[bodyweight.user_id == user_id]
        avg_by_day = user_temp.groupby(['date'], as_index=False).wt_lb.mean()
        records_today = user_temp[user_temp.date == today]

        try:
                user_df = pd.merge(user_temp, profile, on=['user_id','user_id'])
                bwt_goal = user_df.bw_goal.mean()
                with tab:
                        col1, col2, col3 = st.columns(3)
                        # most recent bodyweight
                        recent_bwt = user_df.wt_lb.iloc[-1]
                        last_updated = str(user_df.date.iloc[-1])
                        col1.metric('Current Bodyweight (lbs)', recent_bwt)
                        col1.caption(f'Last updated on {last_updated}')
                        if len(records_today) > 1:
                                day_diff = round(records_today.wt_lb.iloc[-1] - records_today.wt_lb.iloc[0],2)
                                col1.metric('Daily Fluctuation (lbs)', day_diff, len(records_today), 'off')
                                col1.caption('')
                        else:
                                col1.metric('Daily Fluctuation (lbs)', 'N/A', len(records_today), 'off')
                                col1.caption('Need 2 records for the day')
                        # bodyweight goal set by user
                        progress = round(recent_bwt - bwt_goal, 2)
                        col2.metric('Bodyweight Goal (lbs)', bwt_goal, progress, 'inverse')
                        col2.caption('')
                        col2.metric('Days Recorded', len(avg_by_day))
                        # weekly change in weight
                        if len(avg_by_day) >= 7:
                                wk_diff = round(avg_by_day.wt_lb.iloc[-1] - avg_by_day.wt_lb.iloc[-7],2)
                                col3.metric('Weekly Change (lbs)', wk_diff)
                        else:
                                col3.metric('Weekly Change','N/A')
                                col3.caption('Need at least 7 days of data')
                        st.table(user_df.tail())
                return user_df

        except:
                tab.subheader("Looks like you're new around here, submit your first bodyweight entry to get started!")

# print data entry form
def print_bwt_form(tab, bodyweight, user_id):
        with tab:
                with st.form('bwt_form', clear_on_submit=True):
                        # input bodyweight
                        body_wt = st.number_input(label='Bodyweight',min_value=0.0,step=0.1)
                        # set unit of measure
                        unit = st.radio('Unit of Measure',['Pounds','Kilograms'])
                        # form submit button for bodyweight entry
                        form_submit_btn = st.form_submit_button('Submit Data')
                        form_submit_msg = st.empty()
                        # bodyweight data submission
                        # 
                        # 1. WEIGHT > 0
                        # 2. WEIGHT WITHIN n% OF LAST SUBMISSION
                        # 3. ONE SUBMISSION FOR AM/PM EACH
                        #
                        if form_submit_btn:
                                if body_wt <= 0:
                                        form_submit_msg.error('Bodyweight cannot be 0')
                                        return

                                current_time = datetime.now() - timedelta(hours=5)
                                #current_time = datetime.now()
                                timestamp = current_time
                                current_date = str(current_time.date())
                                time_of_day = current_time.strftime('%p')

                                wt_lb, wt_kg = utils.convert_weight(unit, body_wt)
                                user_temp = bodyweight[bodyweight.user_id == user_id]
                                data_exists = False

                                if len(user_temp) > 0:
                                        data_exists = True
                                        recent_bwt = user_temp.wt_lb.iloc[0]
                                        recent_entries = user_temp[user_temp.date == current_date]
                                        am_count = (len(recent_entries[recent_entries.time_of_day == 'AM']))
                                        pm_count = (len(recent_entries[recent_entries.time_of_day == 'PM']))
                                        
                                        bwt_lower = 0.9*recent_bwt
                                        bwt_upper = 1.1*recent_bwt

                                if data_exists:
                                        if (time_of_day == 'AM' and am_count == 1) or (time_of_day == 'PM' and pm_count == 1):
                                                form_submit_msg.error('You have already submitted an entry for the time of day, please try again later')
                                                return

                                        if wt_lb < bwt_lower or wt_lb > bwt_upper:
                                                form_submit_msg.error('Bodyweight is not within reasonable bounds')
                                                return
                                        
                                        date = current_date
                                        entry = {'timestamp': timestamp,
                                                'user_id': user_id,
                                                'wt_lb': wt_lb,
                                                'wt_kg': wt_kg,
                                                'date': date,
                                                'time_of_day': time_of_day}
                                        connect.submit_data(entry,'bodyweight')
                                        st.json(entry)
                                        form_submit_msg.success('Data Submitted')
                                        return
                                else:
                                        date = current_date
                                        entry = {'timestamp': timestamp,
                                                'user_id': user_id,
                                                'wt_lb': wt_lb,
                                                'wt_kg': wt_kg,
                                                'date': date,
                                                'time_of_day': time_of_day}
                                        connect.submit_data(entry,'bodyweight')
                                        st.json(entry)
                                        form_submit_msg.success('Data Submitted')
                                        return
                                                        
# visualize personalized weight journey
def weight_journey(tab, user_df):
        try:
                user_df.date = pd.to_datetime(user_df.date, infer_datetime_format=True)
                user = user_df.user.iloc[0]
                bwt_goal = user_df.bw_goal.mean()
                bwt_avg = user_df.wt_lb.mean()
                bwt_max = user_df.wt_lb.max()
                bwt_min = user_df.wt_lb.min()
                avg_by_day = user_df.groupby(['date'], as_index=False).wt_lb.mean()
                fig = go.Figure()
                fig.update_layout(
                        title=f"{user}'s Weight Journey",
                        xaxis_title='Timeline',
                        yaxis_title='Bodyweight (lbs)'
                )
                fig.add_trace(go.Scatter(
                        mode='markers',
                        x=user_df[user_df.time_of_day == 'AM']['date'],
                        y=user_df[user_df.time_of_day == 'AM']['wt_lb'],
                        marker={'color':'orangered','size':9,
                        'line':{'color':'orange','width':1},
                        'symbol':'hexagon'},
                        name ='AM',
                        opacity=0.7,
                        legendgroup='group1',
                        legendgrouptitle_text='Time of Day'
                ))
                fig.add_trace(go.Scatter(
                        mode='markers',
                        x=user_df[user_df.time_of_day == 'PM']['date'],
                        y=user_df[user_df.time_of_day == 'PM']['wt_lb'],
                        marker={'color':'royalblue','size':9,
                        'line':{'color':'lightblue','width':1},
                        'symbol':'hexagon'},
                        name ='PM',
                        opacity=0.7,
                        legendgroup='group1'
                ))
                fig.add_trace(go.Scatter(
                        mode='lines',
                        x=avg_by_day.date,
                        y=avg_by_day.wt_lb,
                        line={'color':'mediumpurple','dash':'dot'},
                        name='Bodyweight Average',
                        opacity=0.5,
                        legendgroup='group2',
                        legendgrouptitle_text='Profile Metrics'
                ))
                fig.add_trace(go.Scatter(
                        mode='lines',
                        x=user_df['date'],
                        y=user_df['bw_goal'],
                        line_color='goldenrod',
                        name='Bodyweight Goal',
                        opacity=0.8,
                        legendgroup='group2'
                ))
                
                if bwt_min >= bwt_goal:
                        fig.update_layout(
                                yaxis_range=[bwt_goal-1, bwt_max+1]
                        )
                else:
                        fig.update_layout(
                                yaxis_range=[bwt_min-1, bwt_max+1]
                        )

                tab.plotly_chart(fig)
        except:
                tab.warning('Not Available')

# visualize personalized home fitness measure
def measure_home_fitness(tab, home_fitness, profile, user_id):
        try:
                user_temp = home_fitness[home_fitness.user_id == user_id]
                user_df = pd.merge(user_temp, profile, on=['user_id','user_id'])
                current_time = datetime.now() - timedelta(hours=5)
                current_date = str(current_time.date())
                curr_exer = user_df[user_df.date == current_date].groupby(['exercise'], as_index=False).reps.sum()
                exer_by_day = user_df.groupby(['date','exercise'], as_index=False).reps.sum()
                user = user_df.user.iloc[0]
                pushup_goal = user_df.pushup_goal.iloc[0]
                pullup_goal = user_df.pullup_goal.iloc[0]
                lraise_goal = user_df.lraise_goal.iloc[0]
                kraise_goal = user_df.kraise_goal.iloc[0]
                fig = go.Figure()
                fig.update_layout(
                        title=f"{user}'s {current_date} Home Fitness Status Report",
                        xaxis_title='Home Exercises',
                        yaxis_title='Repetitions In'
                )
                fig.add_trace(go.Bar(
                        x=curr_exer.exercise,
                        y=curr_exer.reps
                ))
                fig.add_trace(go.Scatter(
                        x=['Push Ups'],
                        y=user_df.pushup_goal
                ))
                fig.add_trace(go.Scatter(
                        x=['Pull Ups'],
                        y=user_df.pullup_goal
                ))
                fig.add_trace(go.Scatter(
                        x=['Straight Leg Raises'],
                        y=user_df.lraise_goal
                ))
                fig.add_trace(go.Scatter(
                        x=['Vertical Knee Raises'],
                        y=user_df.kraise_goal
                ))
                tab.plotly_chart(fig)
                tab.table(user_df)
                tab.table(curr_exer)
                tab.table(exer_by_day)
                # home fitness notes
                #
                # EXERCISES DEPEND ON USER LIST
                # GRAPH TRACKS DAILY PROGRESS TO GOAL, RESETS EVERY DAY
                # UPDATE LEGEND
                # ADD GRAPH FOR OVERALL PROGRESS FOR EACH EXERCISE (COMBINED LINE GRAPH TIMELINE)
                #
        except:
                tab.warning('Not Available')

# visualize personalized running performance
def running_performance(tab, running, profile, user_id):
        try:
                user_temp = running[running.user_id == user_id]
                user_run_df = pd.merge(user_temp, profile, on=['user_id','user_id'])
        except:
                tab.warning('Not Available')

def weight_journey_old(tab, user_df):
        try:
                user_df.date = pd.to_datetime(user_df.date, infer_datetime_format=True)
                user = user_df.user.iloc[0]
                bodyweight_goal = user_df.bw_goal.mean()
                bodyweight_avg = user_df.wt_lb.mean()
                fig = px.scatter(data_frame=user_df,
                                x='date',
                                y='wt_lb',
                                title= f"{user}'s Weight Journey",
                                labels={
                                'date': 'Timeline',
                                'wt_lb': 'Bodyweight (lbs)',
                                'time_of_day': 'Time of Day'},
                                trendline='rolling',
                                trendline_options=dict(window=7),
                                trendline_color_override='gray',
                                opacity=0.7,
                                color='time_of_day',
                                color_discrete_map={
                                'AM':'orangered',
                                'PM':'royalblue'})
                fig.update_layout(yaxis_range=[bodyweight_goal-1, user_df.wt_lb.max()+1])
                fig.add_hline(y=bodyweight_goal,line_color='goldenrod',opacity=0.8)
                fig.add_hline(y=bodyweight_avg,line_dash='dot',line_color='rebeccapurple',opacity=0.5)
                tab.plotly_chart(fig)
        except:
                tab.error('Not Available')

# build repetition breakdown table
def build_rbt(tab):
        with tab:
                with st.expander('Repetition Breakdown Table', expanded=False):
                        col1, col2 = st.columns(2)
                        lift_wt = col1.number_input(label='Weight Lifted',
                                                        min_value=0,
                                                        step=1)
                        reps = col2.number_input(label='Set Repetitions',
                                                     min_value=0,
                                                     step=1)
                        utils.get_breakdown(lift_wt, reps)

# print home fitness entry form
def print_homefit_form(tab, home_fitness, user_id):
        with tab:
                with st.form('homefit_form', clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        reps = col1.number_input(label='Repetitions In',
                                                min_value=0,
                                                step=1)
                        exercise = st.radio('Home Exercise',
                        ['Push Ups','Pull Ups','Vertical Knee Raises','Straight Leg Raises'])
                        if exercise == 'Push Ups':
                                exer_cat = 'BWT'
                        else:
                                exer_cat = 'TWR'
                        form_submit_btn = st.form_submit_button('Submit Data')
                        form_submit_msg = st.empty()
                        if form_submit_btn:
                                current_time = datetime.now() - timedelta(hours=5)
                                timestamp = current_time
                                current_date = str(current_time.date())
                                date = current_date
                                entry = {'timestamp': timestamp,
                                        'user_id': user_id,
                                        'exercise': exercise,
                                        'reps': reps,
                                        'exer_cat': exer_cat,
                                        'date': date}
                                #connect.submit_data(entry, 'home_fitness')
                                st.json(entry)
                                form_submit_msg.info('This button buttons')

# print weight lifting entry form
def print_lift_form(tab, user_id):
        with tab:
                with st.form('lift_form', clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        lift_wt = col1.number_input(label='Weight Lifted (lbs)',
                                                min_value=0,
                                                step=1)
                        reps = col2.number_input(label='Set Repetitions',
                                                min_value=0,
                                                step=1)
                        lift_type = st.radio('Lift Performed',
                        ['Bench Press','Back Squat','Deadlift','Military Press'])
                        form_submit_btn = st.form_submit_button('Submit Data')
                        form_submit_msg = st.empty()
                        if form_submit_btn:
                                current_time = datetime.now() - timedelta(hours=5)
                                timestamp = current_time
                                current_date = str(current_time.date())
                                date = current_date
                                orm = utils.find_orm(lift_wt, reps)
                                entry = {'timestamp': timestamp,
                                        'user_id': user_id,
                                        'lift_type': lift_type,
                                        'lift_wt': lift_wt,
                                        'reps': reps,
                                        'orm': orm,
                                        'date': date}
                                #connect.submit_data(entry, 'test')
                                st.json(entry)
                                form_submit_msg.info('This button buttons')

# print running entry form
def print_run_form(tab, user_id):
        with tab:
                with st.form('run_form', clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        distance = col1.number_input(label='Distance Ran (Mi.)',
                                                min_value=0,
                                                step=1)
                        run_time = col2.text_input('Run Time (MM:SS)')
                        form_submit_btn = st.form_submit_button('Submit Data')
                        form_submit_msg = st.empty()
                        if form_submit_btn:
                                current_time = datetime.now() - timedelta(hours=5)
                                timestamp = current_time
                                current_date = str(current_time.date())
                                date = current_date
                                #pace = utils.find_pace(distance, run_time)
                                pace = 'Pacing'
                                entry = {'timestamp': timestamp,        
                                        'user_id': user_id,
                                        'distance': distance,
                                        'run_time': run_time,
                                        'pace': pace,
                                        'date': date}
                                st.json(entry)
                                form_submit_msg.info('This button buttons')

# visualize personalized lifting performance
def lift_performance(tab, lift_df):
        #
        pass

# visualize personalized running performance
def run_performance(tab, run_df):
        #
        pass