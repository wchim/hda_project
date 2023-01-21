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

# visualize daily home fitness progress
def measure_home_fitness(tab, home_fitness, profile, user_id):

        user_temp = home_fitness[home_fitness.user_id == user_id]
        user_df = pd.merge(user_temp, profile, on=['user_id','user_id'])
        home_exercises = user_df.home_exercises.iloc[0]
        current_time = datetime.now() - timedelta(hours=5)
        current_date = str(current_time.date())
                
        fitness_targets = pd.DataFrame()
        fitness_targets['exercise'] = [exer for exer in home_exercises]
        fitness_targets['target'] = [home_exercises[exer] for exer in home_exercises]

        daily_exer = user_df[user_df.date == current_date].groupby(['exercise'], as_index=False).reps.sum()
        #daily_exer = user_df.groupby(['exercise'], as_index=False).reps.sum()
        daily_exer['target'] = [home_exercises[record[0]] for record in daily_exer.values]
        daily_exer['progress'] = daily_exer.reps/daily_exer.target
        daily_exer['progress_adjust'] = [1 if n >= 1 else n for n in daily_exer.progress]
        daily_exer['marker_color'] = ['palegoldenrod' if n == 1 else 'mediumpurple' for n in daily_exer.progress_adjust]
        daily_exer['textfont_color'] = ['black' if n == 1 else 'white' for n in daily_exer.progress_adjust]
        daily_exer.sort_values(by=['progress_adjust'], inplace=True)

        overall_exer = user_df.groupby(['date','exercise'], as_index=False).reps.sum()
        overall_exer.sort_values(by=['date','reps'], inplace=True)
        
        fig1 = go.Figure()
        fig1.update_layout(
                title=f'Daily Home Fitness Status Update',
                xaxis_title='Repetition Progress',
                yaxis_title='Home Exercises',
                xaxis_range=[0,1],
                barmode='overlay',
                legend={'font':{'size':12}},
                showlegend=False
        )

        if len(daily_exer) == 0:
                y = fitness_targets.exercise
                text = fitness_targets.target
        else:
                for n in fitness_targets.exercise.values.tolist():
                        if n not in daily_exer.exercise.values:
                                s = {'exercise':n,
                                'reps':0,
                                'target':home_exercises[n],
                                'progress':None,
                                'progress_adjust':None,
                                'marker_color':'mediumpurple',
                                'textfont_color':'black'}
                                daily_exer = daily_exer.append(s, ignore_index=True)
                y = daily_exer.exercise
                text = daily_exer.target

        fig1.add_trace(go.Bar(
                x=[1]*len(y),
                y=y,
                name='Target',
                text=text,
                orientation='h',
                marker_color='seashell',
                marker_line_color='gray',
                opacity=0.4,
                marker_line_width=1,
                textfont_color='black'
        ))

        marker_color=daily_exer.marker_color.values.tolist()
        textfont_color=daily_exer.textfont_color.values.tolist()
        
        fig1.add_trace(go.Bar(
                x=daily_exer.progress_adjust,
                y=daily_exer.exercise,
                name='Repetitions In',
                text=daily_exer.reps,
                orientation='h',
                marker_color=marker_color,
                textfont_color=textfont_color
        ))
        
        fig2 = go.Figure()
        fig2.update_layout(
                title=f'Overall Home Fitness Summary',
                xaxis_title='Timeline',
                yaxis_title='Repetitions In ',
                yaxis_range=[overall_exer.reps.min()*0.5,overall_exer.reps.max()+2],
                legend={'font':{'size':11}},
                showlegend=True
        )
        color_palette = ['peachpuff','palegreen','mistyrose','lightcoral','cornflowerblue']
        idx = 0
        for exer in home_exercises:
                fig2.add_trace(go.Scatter(
                        x=overall_exer[overall_exer.exercise == exer]['date'],
                        y=overall_exer[overall_exer.exercise == exer]['reps'],
                        name=exer,
                        marker={'color':color_palette[idx],'size':9,
                        'line':{'color':'dimgray','width':1},
                        'symbol':'hexagon'},
                        line={'dash':'dot'}
                ))
                idx += 1

        tab.plotly_chart(fig1)
        tab.plotly_chart(fig2)
        #tab.table(user_df.tail(2))
        tab.table(daily_exer)
                        # home fitness notes
                        #
                        # ADJUST COLORS AND SCALE PROGRESS TO GOAL AS 100%
                        # EXERCISES DEPEND ON USER LIST
                        # GRAPH TRACKS DAILY PROGRESS TO GOAL, RESETS EVERY DAY
                        # UPDATE LEGEND
                        # ADD GRAPH FOR OVERALL PROGRESS FOR EACH EXERCISE (COMBINED LINE GRAPH TIMELINE)
                        #
        '''except:
                tab.warning('Not Available')'''

# visualize personalized running performance
def running_performance(tab, running, profile, user_id):
        try:
                user_temp = running[running.user_id == user_id]
                user_run_df = pd.merge(user_temp, profile, on=['user_id','user_id'])
        except:
                tab.warning('Not Available')

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
                        if lift_wt > 0 and reps > 0:
                                utils.get_breakdown(lift_wt, reps)

# print home fitness entry form
def print_homefit_form(tab, profile, user_id):
        home_exercises = profile[profile.user_id == user_id].home_exercises.iloc[0]
        with tab:
                with st.form('homefit_form', clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        reps = col1.number_input(label='Repetitions In',
                                                min_value=0,
                                                step=1)
                        exercise = st.radio('Home Exercise',
                        home_exercises)
                        
                        form_submit_btn = st.form_submit_button('Submit Data')
                        form_submit_msg = st.empty()
                        if form_submit_btn:
                                if reps <= 0:
                                        form_submit_msg.error('Repetitions cannot be 0')
                                        return

                                current_time = datetime.now() - timedelta(hours=5)
                                timestamp = current_time
                                current_date = str(current_time.date())
                                date = current_date

                                entry = {'timestamp': timestamp,
                                        'user_id': user_id,
                                        'exercise': exercise,
                                        'reps': reps,
                                        'date': date}
                                connect.submit_data(entry, 'home_fitness')
                                st.json(entry)
                                form_submit_msg.success('Data Submitted')

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