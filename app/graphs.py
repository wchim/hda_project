import streamlit as st
import pandas as pd
import plotly.express as px

def weight_journey(df, user, bodyweight_goal):
        bodyweight_avg = df[df.user==user].wt_lb.mean()
        fig = px.scatter(data_frame=df,
                        x='date',
                        y='wt_lb',
                        title=f"{user}'s Weight Journey",
                        labels={'date': 'Timeline',
                                'wt_lb': 'Bodyweight (lbs)',
                                'user': 'User'},
                        trendline='rolling',
                        trendline_options=dict(window=30),
                        trendline_color_override='yellow',
                        opacity=0.5,
                        color='user',
                        color_discrete_map={
                        'Wayne Chim':'gray',
                        'Joyce Chan':'gray'})
        fig.update_layout(yaxis_range=[bodyweight_goal-1, df.wt_lb.max()+1])
        fig.add_hline(y=bodyweight_goal,line_dash='dash',line_color='purple',opacity=0.5)
        fig.add_hline(y=bodyweight_avg,line_dash='dash',line_color='red',opacity=0.5)
        st.plotly_chart(fig)