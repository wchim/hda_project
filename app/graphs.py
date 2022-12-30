import streamlit as st
import pandas as pd
import plotly.express as px

def weight_journey(user_df):
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
        st.plotly_chart(fig)