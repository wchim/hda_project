import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import timedelta
import time

import connect
import graphs
import utils

st.title('Health Data App')
# Select a user through a dropdown
user = st.selectbox('Select A Profile',
                   ['Wayne Chim'])

#df = pd.read_csv('main.csv')
df = connect.load_gsheet()

#df['date'] = [i.date() for i in df.timestamp]
#df.date = pd.to_datetime(df.date, infer_datetime_format=True)
#df['time_of_day'] = [i.strftime('%p') for i in df.timestamp]
new_df = df[df.user == user]

# Page tabs
data_tab, graph_tab, form_tab = st.tabs(['Summary Statistics','Weight Journey','Data Entry'])
with data_tab:
    current_wt, week_ma, to_goal = st.columns(3)
    current_wt.metric('Current Body Weight', 163)
    week_ma.metric('7-Day Moving Average', 165, 163-165)
    to_goal.metric('Progress from Goal', 163-160)
with graph_tab:
    #Dummy slider
    st.select_slider('Timeline Range', df.date, (df.date.min(), df.date.max()))
    graphs.weight_journey(new_df)
with form_tab:
    with st.form('body_wt_form', clear_on_submit=True):
        body_wt = st.number_input(label='Body Weight',
                                  min_value=0,
                                  step=1)
        unit = st.radio('Unit of Measure',
                        ['Pounds','Kilograms'])
    
        form_submit = st.form_submit_button('Submit Data')
        if form_submit:
            if body_wt > 0:
                wt_lb, wt_kg = utils.convert_weight(unit, body_wt)
                #current_time = datetime.now() - timedelta(hours=4)
                current_time = datetime.now()
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
            else:
                blank = st.empty()
                blank.error('Bodyweight must be at least 0')
                time.sleep(3)
                blank.empty()
                    
            