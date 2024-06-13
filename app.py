# Author: Mitch Zink
# Last Updated: 6/13/2024

import streamlit as st
import snowflake.connector
import pandas as pd
from IP2Location import IP2Location
import os
from datetime import datetime, timedelta
from iso3166 import countries_by_alpha2


def set_env_variables(account, user, password):
    """Set environment variables for Snowflake connection"""
    os.environ["SNOWFLAKE_ACCOUNT"] = account
    os.environ["SNOWFLAKE_USER"] = user
    if password:
        os.environ["SNOWFLAKE_PASSWORD"] = password


def create_snowflake_connection(
    user, account, password=None, authenticator="externalbrowser"
):
    """Create and return a Snowflake connection"""
    try:
        if authenticator == "externalbrowser":
            snowflake_conn = snowflake.connector.connect(
                user=user, account=account, authenticator=authenticator
            )
        else:
            snowflake_conn = snowflake.connector.connect(
                user=user, account=account, password=password
            )
        return snowflake_conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")
        return None


def get_full_country_name(country_code):
    """Convert country code to full country name"""
    try:
        return countries_by_alpha2[country_code].name
    except KeyError:
        return country_code


def get_geo_info(ip, ip2location_db):
    """Get geolocation information for a given IP address"""
    try:
        rec = ip2location_db.get_all(ip)
        if rec.ip == "0.0.0.0":
            st.warning(f"IP2Location returned 0.0.0.0 for IP: {ip}")
        return {
            "client_ip": ip,
            "country": rec.country_short,
            "country_name": get_full_country_name(rec.country_short),
            "city": rec.city,
            "state": rec.region,
            "latitude": float(rec.latitude),
            "longitude": float(rec.longitude),
        }
    except Exception as e:
        st.error(f"Error retrieving geolocation for IP {ip}: {e}")
        return {
            "client_ip": ip,
            "country": "Unknown",
            "country_name": "Unknown",
            "city": "Unknown",
            "state": "Unknown",
            "latitude": None,
            "longitude": None,
        }


def fetch_login_history(connection, start_date, end_date, user_name=None):
    """Fetch login history from Snowflake within a date range, optionally filtered by user name"""
    user_filter = f"AND user_name = '{user_name}'" if user_name else ""
    query = f"""
    SELECT client_ip, user_name, count(*) as login_count
    FROM snowflake.account_usage.login_history
    WHERE event_timestamp BETWEEN '{start_date}' AND '{end_date}' {user_filter}
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


def main():
    # Set Streamlit page configuration
    st.set_page_config(layout="wide")
    st.title("Snowflake Login History")
    st.sidebar.header("Configuration")

    # Sidebar inputs for Snowflake account and authentication
    ACCOUNT = st.sidebar.text_input("Snowflake Account", placeholder="abc12345")
    USER = st.sidebar.text_input("User", placeholder="admin@snowflake.com")
    use_external_auth = st.sidebar.checkbox("Use External Browser Authentication")

    # Conditional input for password
    PASSWORD = ""
    if not use_external_auth:
        PASSWORD = st.sidebar.text_input("Password", type="password")
        authenticator = "snowflake"
    else:
        authenticator = "externalbrowser"

    # Sidebar inputs for date range
    START_DATE = st.sidebar.date_input(
        "Start Date", datetime.now().date() - timedelta(days=1)
    )
    END_DATE = st.sidebar.date_input("End Date", datetime.now().date())

    # Optional input for user name filter
    USER_NAME_FILTER = st.sidebar.text_input(
        "User Name Filter", placeholder="Enter user name to filter (optional)"
    )

    # Path to IP2Location database
    IP2LOCATION_DB_PATH = (
        "IP2LOCATION/IP2LOCATION-LITE-DB5.BIN/IP2LOCATION-LITE-DB5.BIN"
    )

    # Fetch and map data when button is clicked
    if st.sidebar.button("Fetch and Map Data"):
        if not ACCOUNT or not USER or (not use_external_auth and not PASSWORD):
            st.error("Please fill in all the configuration fields.")
        else:
            set_env_variables(ACCOUNT, USER, PASSWORD)

            with st.spinner("Connecting to Snowflake..."):
                snowflake_conn = create_snowflake_connection(
                    USER, ACCOUNT, PASSWORD, authenticator
                )

            if snowflake_conn:
                login_history_data = fetch_login_history(
                    snowflake_conn, START_DATE, END_DATE, USER_NAME_FILTER
                )
                snowflake_conn.close()

                if login_history_data:
                    ip2location_db = IP2Location(IP2LOCATION_DB_PATH)
                    geo_info_list = []
                    for row in login_history_data:
                        if row[0] != "0.0.0.0":  # Skip invalid IPs
                            geo_info = get_geo_info(row[0], ip2location_db)
                            geo_info["user_name"] = row[1]
                            geo_info["login_count"] = row[2]
                            geo_info_list.append(geo_info)

                    # Ensure latitude and longitude columns are present
                    for geo_info in geo_info_list:
                        geo_info.setdefault("latitude", None)
                        geo_info.setdefault("longitude", None)

                    geo_df = pd.DataFrame(geo_info_list).dropna(
                        subset=["latitude", "longitude"]
                    )
                    geo_df["latitude"] = geo_df["latitude"].astype(float)
                    geo_df["longitude"] = geo_df["longitude"].astype(float)

                    # Display summary tiles
                    num_countries = geo_df["country_name"].nunique()
                    num_users = geo_df["user_name"].nunique()
                    num_logins = geo_df["login_count"].sum()

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Countries", num_countries)
                    col2.metric("Users", num_users)
                    col3.metric("Logins", num_logins)

                    st.subheader("Login History")
                    st.map(geo_df)  # Display map for login data

                    # Calculate and display login counts by country
                    country_counts = (
                        geo_df.groupby("country_name")["login_count"]
                        .sum()
                        .reset_index()
                    )
                    country_counts = country_counts[country_counts["login_count"] > 0]
                    country_counts = country_counts.sort_values(
                        by="login_count", ascending=False
                    )

                    st.subheader("# of Logins by Country")
                    st.bar_chart(
                        country_counts.set_index("country_name")["login_count"]
                    )  # Display bar chart
                    st.dataframe(
                        country_counts, width=1600
                    )  # Display country login counts in table

                    st.subheader("Detailed List of Logins by IP")
                    st.dataframe(
                        geo_df.sort_values(by="login_count", ascending=False),
                        width=1600,
                    )  # Display geolocation data in table


if __name__ == "__main__":
    main()
