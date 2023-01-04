import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

import connect
import utils

# loads mongodb into dataframe
bodyweight, profile = connect.unload_data()

# visualize comparison across all users
def overall_weight_progression():
        pass

# write welcome message based on data availability
def write_welcome_msg(element, user):
        bwt_ct = len(bodyweight)
        if bwt_ct == 0:
                element.subheader("Welcome to a fresh start! Let's start tracking data..")
        else:
                element.subheader(f'Welcome back, {user}')

# build tabs as per selected user profile
def build_tabs(element, user):
        lift_opt = profile[profile.user == user].lift_opt.iloc[0]
        run_opt = profile[profile.user == user].run_opt.iloc[0]
        tab_ls = ['Profile Summary','Weight Journey','Data Entry']
        # check for lifting performance tracking opt-in
        if lift_opt:
                tab_ls.insert(len(tab_ls)-1, 'Lifting Performance')
        # check for running performance tracking opt-in
        if run_opt:
                tab_ls.insert(len(tab_ls)-1, 'Running Performance')
        user_tabs = element.tabs(tab_ls)
        return user_tabs

# print profile summary
def print_profile(tab, user):
        user_id = profile[profile.user == user].user_id.iloc[0]
        user_temp = bodyweight[bodyweight.user_id == user_id]
        groupby_day = user_temp.groupby(['date']).wt_lb.mean()

        try:
                user_df = pd.merge(user_temp, profile, on=['user_id','user_id'])
                bwt_goal = user_df.bw_goal.mean()
                with tab:
                        metr1, metr2, metr3 = st.columns(3)
                        # most recent bodyweight
                        recent_bwt = user_df.wt_lb.iloc[-1]
                        last_updated = str(user_df.date.iloc[-1])
                        metr1.metric('Current Bodyweight', recent_bwt)
                        metr1.caption(f'Last updated on {last_updated}')
                        # bodyweight goal set by user
                        progress = round(recent_bwt - bwt_goal, 2)
                        metr2.metric('Bodyweight Goal', bwt_goal, progress, 'inverse')
                        metr2.caption(np.random.randint(2, size=5))
                        # weekly change in weight
                        if len(groupby_day) >= 7:
                                wk_diff = groupby_day.wt_lb.iloc[-1] - groupby_day.wt_lb.iloc[-7]
                                metr3.metric('Weekly Change',wk_diff)
                        else:
                                metr3.metric('Weekly Change','N/A')
                                metr3.caption('Need at least 7 days of data')
                        st.table(user_df.tail())
                return user_df
        except:
                tab.subheader("Looks like you're new around here, submit your first bodyweight entry to get started!")

# print data entry form
def print_form(tab, user):
        user_id = profile[profile.user == user].user_id.iloc[0]
        
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
                                        bwt_entry = {'timestamp': timestamp,
                                                        'user_id': user_id,
                                                        'wt_lb': wt_lb,
                                                        'wt_kg': wt_kg,
                                                        'date': date,
                                                        'time_of_day': time_of_day}
                                        connect.submit_data(bwt_entry,'bodyweight')
                                        st.json(bwt_entry)
                                        form_submit_msg.success('Data Submitted')
                                        return
                                else:
                                        date = current_date
                                        bwt_entry = {'timestamp': timestamp,
                                                        'user_id': user_id,
                                                        'wt_lb': wt_lb,
                                                        'wt_kg': wt_kg,
                                                        'date': date,
                                                        'time_of_day': time_of_day}
                                        connect.submit_data(bwt_entry,'bodyweight')
                                        st.json(bwt_entry)
                                        form_submit_msg.success('Data Submitted')
                                        return
                                                        
# visualize personalized weight journey
def weight_journey(tab, user_df):
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

# visualize personalized lifting performance
def lift_performance(tab, lift_df):
        #
        pass

# visualize personalized running performance
def run_performance(tab, run_df):
        #
        pass