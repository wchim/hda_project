import streamlit as st
import pandas as pd
import plotly.express as px

def weight_journey(df, user, bodyweight_goal):
        
        fig = px.scatter(data_frame=df,
                        x='date',
                        y='wt_lb',
                        title=f"{user}'s Weight Journey",
                        labels={'date': 'Timeline',
                                'wt_lb': 'Bodyweight (lbs)',
                                'user': 'User'},
                        trendline='rolling',
                        trendline_options=dict(window=7),
                        trendline_color_override='lightgreen',
                        opacity=0.5,
                        color='user',
                        color_discrete_map={
                        'Wayne Chim':'grey',
                        'Joyce Chan':'pink'})
        fig.update_layout(yaxis_range=[df.wt_lb.min()-2, df.wt_lb.max()+2])
        fig.add_hline(y=bodyweight_goal,line_dash='dash',line_color='purple',opacity=0.5)
        st.plotly_chart(fig)