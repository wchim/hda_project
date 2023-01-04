import streamlit as st
import pandas as pd
import pymongo
from pymongo.server_api import ServerApi

# initialize mongodb connection
# connection_url = "mongodb+srv://wchim:aUkvGgAarVb8Gv3P@hda-cluster.qtfcgsu.mongodb.net/bodyweight"
@st.experimental_singleton
def init_connection():
    MONGO_USER = st.secrets['mongo'].username
    MONGO_AUTH = st.secrets['mongo'].password
    MONGO_CLUSTER = st.secrets['mongo'].cluster
    #MONGO_DB = st.secrets['mongo'].database
    MONGO_URL = f'mongodb+srv://{MONGO_USER}:{MONGO_AUTH}@{MONGO_CLUSTER}.qtfcgsu.mongodb.net/'
    
    client = pymongo.MongoClient(MONGO_URL,
                                 server_api=ServerApi('1'))
    db = client.pod_health
    return db

db = init_connection()

# unload all data from mongodb for user view and analytics
@st.experimental_memo(ttl=600)
def unload_data():
    bodyweight = pd.DataFrame(list(db.bodyweight.find()))
    #bodyweight = pd.DataFrame(list(db.test.find()))
    profile = pd.DataFrame(list(db.profile.find()))
    return bodyweight, profile
    
# refreshes mongodb connection for updated query
def refresh_view(element):
        refresh_btn = element.button('Refresh View')
        if refresh_btn:
                st.experimental_memo.clear()

# writes new record to mongodb
def submit_data(data_entry, collection):
    db[collection].insert_one(data_entry)
