import streamlit as st
import pandas as pd
import json
from datetime import datetime
from google.oauth2 import service_account
import gspread
import gspread_dataframe as gd

# set up gsheet connect
scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
google_key_file = 'hda-gsheet-connect-0e3f2b4e1012.josn'
credentials = service_account.Credentials.from_service_account_info(st.secrets['gcp_service_account'],
                                                                    scopes=scope)
g_auth = gspread.authorize(credentials)

spreadsheet_key = '1tuqOdo_xjfbIvZxhxAHfJTVrZatpu8XY-At3LfodWFc'
worksheet_name = 'bodyweight'
workbook = g_auth.open_by_key(spreadsheet_key)
sheet = workbook.worksheet(worksheet_name)

def load_gsheet():
    values = sheet.get_all_values()
    df = pd.DataFrame(values[1:], columns=values[0])
    df.timestamp = pd.to_datetime(df.timestamp, infer_datetime_format=True)
    df.wt_lb = df.wt_lb.astype(float)
    df.wt_kg = df.wt_kg.astype(float)
    df.date = pd.to_datetime(df.date, infer_datetime_format=True)
    #df['date'] = [i.date() for i in df.timestamp]
    #df['time_of_day'] = [i.strftime('%p') for i in df.timestamp]
    return df

def load_profiles():
    #profiles = pd.read_csv('app/profiles.csv')
    profiles = pd.read_csv('profiles.csv')
    return profiles

def submit_data(data_entry, df):
    updated_df = df.append(data_entry, ignore_index=True)
    gd.set_with_dataframe(sheet, updated_df)