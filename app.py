import streamlit as st
import snowflake.connector
import pandas as pd
from IP2Location import IP2Location  # Correct import statement
import os
from datetime import datetime, timedelta

# Streamlit page setup
st.set_page_config(layout="wide")
st.title("Snowflake Login History")
st.sidebar.header("Configuration")

ACCOUNT = st.sidebar.text_input("Snowflake Account", placeholder="abc12345")
USER = st.sidebar.text_input("User", placeholder="admin@snowflake.com")
use_external_auth = st.sidebar.checkbox("Use External Browser Authentication")

PASSWORD = ""
if not use_external_auth:
    PASSWORD = st.sidebar.text_input("Password", type="password")
    authenticator = "snowflake"
else:
    authenticator = "externalbrowser"

START_DATE = st.sidebar.date_input("Start Date", datetime.now().date() - timedelta(days=1))
END_DATE = st.sidebar.date_input("End Date", datetime.now().date())

# Path to the IP2Location database file
IP2LOCATION_DB_PATH = "IP2LOCATION/IP2LOCATION-LITE-DB5.BIN/IP2LOCATION-LITE-DB5.BIN"

# Function to set environment variables
def set_env_variables(account, user, password):
    os.environ["SNOWFLAKE_ACCOUNT"] = account
    os.environ["SNOWFLAKE_USER"] = user
    if password:
        os.environ["SNOWFLAKE_PASSWORD"] = password

def create_snowflake_connection(user, account, password=None, authenticator="externalbrowser"):
    try:
        if authenticator == "externalbrowser":
            snowflake_conn = snowflake.connector.connect(
                user=user,
                account=account,
                authenticator=authenticator,
            )
        else:
            snowflake_conn = snowflake.connector.connect(
                user=user,
                account=account,
                password=password,
            )
        return snowflake_conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")
        return None

def fetch_login_history(connection, start_date, end_date):
    query = f"""
    SELECT client_ip,
           user_name,
           count(*) as login_count
    FROM snowflake.account_usage.login_history
    WHERE event_timestamp BETWEEN '{start_date}' AND '{end_date}'
      --AND USER_NAME = 'MITCH'
    GROUP BY client_ip, user_name
    """
    try:
        with connection.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return rows
    except Exception as e:
        st.error(f"Error fetching login history: {e}")
        return []

def get_geo_info(ip, ip2location_db):
    try:
        rec = ip2location_db.get_all(ip)
        if rec.ip == "0.0.0.0":
            st.warning(f"IP2Location returned 0.0.0.0 for IP: {ip}")
        return {
            'client_ip': ip,
            'country': rec.country_short,
            'city': rec.city,
            'state': rec.region,
            'latitude': float(rec.latitude),
            'longitude': float(rec.longitude)
        }
    except Exception as e:
        st.error(f"Error retrieving geolocation for IP {ip}: {e}")
        return {
            'client_ip': ip,
            'country': 'Unknown',
            'city': 'Unknown',
            'state': 'Unknown',
            'latitude': None,
            'longitude': None
        }

if st.sidebar.button("Fetch and Map Data"):
    if not ACCOUNT or not USER or (not use_external_auth and not PASSWORD):
        st.error("Please fill in all the configuration fields.")
    else:
        set_env_variables(ACCOUNT, USER, PASSWORD)
        
        with st.spinner("Connecting to Snowflake..."):
            snowflake_conn = create_snowflake_connection(USER, ACCOUNT, PASSWORD, authenticator)
        
        if snowflake_conn:
            login_history_data = fetch_login_history(snowflake_conn, START_DATE, END_DATE)
            snowflake_conn.close()
            
            if login_history_data:
                ip2location_db = IP2Location(IP2LOCATION_DB_PATH)
                geo_info_list = []
                for row in login_history_data:
                    if row[0] != '0.0.0.0':  # Skip invalid IPs
                        geo_info = get_geo_info(row[0], ip2location_db)
                        geo_info['user_name'] = row[1]
                        geo_info['login_count'] = row[2]
                        geo_info_list.append(geo_info)

                geo_df = pd.DataFrame(geo_info_list).dropna(subset=['latitude', 'longitude'])
                geo_df['latitude'] = geo_df['latitude'].astype(float)
                geo_df['longitude'] = geo_df['longitude'].astype(float)
                
                st.map(geo_df)
                st.dataframe(geo_df)
