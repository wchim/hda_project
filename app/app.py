import streamlit as st
import pandas as pd
from datetime import datetime
import pymongo
from pymongo.server_api import ServerApi

import views
import connect

# initialize mongodb connection
@st.experimental_singleton
def init_connection():
    client = pymongo.MongoClient(st.secrets['connection_url'],
                                 server_api=ServerApi('1'))
    db = client.pod_health
    #return pymongo.MongoClient("mongodb://wchim:aUkvGgAarVb8Gv3P@localhost:27017/sample_airbnb")
    #return pymongo.MongoClient(**st.secrets['mongo'])
    return db
    
db = init_connection()

#@st.experimental_memo(ttl=600)
def get_data():
    bw = db.bodyweight
    profile = db.profile
    bw_ls = pd.DataFrame(list(bw.find()))
    profiles = pd.DataFrame(list(profile.find()))
    return bw_ls, profiles
        
bw_ls, profiles = get_data()
uid = '001'
st.write(bw_ls[bw_ls.user_id == uid])
st.write(profiles)
#st.write(profiles[profiles.user_id == uid])

# writes new record to mongodb
'''client.pod_health.bodyweight.insert_one({"user_id":"001",
               "timestamp":datetime.now(),
               "wt_lb":170.5,
               "wt_kg":170.5/2.2})'''

#client.close()
