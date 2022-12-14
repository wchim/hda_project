import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title('Health Data App')
# Select a user through a dropdown
user = st.selectbox('Select A Profile',
                   ['Wayne Chim'])

df = pd.read_csv('app/main.csv')
#Processing data
df.timestamp = pd.to_datetime(df.timestamp, infer_datetime_format=True)
df.date = pd.to_datetime(df.date, infer_datetime_format=True)
df['time_of_day'] = [time.strftime('%p') for time in df.timestamp]
new_df = df[df.user == 'Wayne Chim']

fig = px.scatter(data_frame=new_df,
                 x='date',
                 y='wt_lb',
                 title="Wayne's Weight Journey",
                 labels={'date': 'Timeline',
                         'wt_lb': 'Bodyweight (lbs)'},
                 trendline='rolling',
                 trendline_options=dict(window=7),
                 trendline_color_override='lightgreen',
                 opacity=0.5,
                 color='user',
                 color_discrete_map={
                    'Wayne Chim':'grey'})
fig.update_layout(yaxis_range=[new_df.wt_lb.min()-2, new_df.wt_lb.max()+2])
fig.add_hline(y=160,line_dash='dash',line_color='purple',opacity=0.5)

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
    #Generate weight journey graph
    #build_wt_jrny()
    st.plotly_chart(fig)
with form_tab:
    with st.form('body_wt_form', clear_on_submit=True):
        body_wt = st.number_input(label='Body Weight',
                                  min_value=0,
                                  step=1)
        unit = st.radio('Unit of Measure',
                        ['Kilograms','Pounds'])
        
        form_submit = st.form_submit_button('Submit Data')
        if form_submit:
            current_time = str(datetime.now() - timedelta(hours=4))
            data_submit = {'timestamp': current_time,
                           'user': user}