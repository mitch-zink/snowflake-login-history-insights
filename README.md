# Snowflake Login History Insights
[![Open with Streamlit](https://img.shields.io/badge/-Open%20with%20Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://snow-access-history-insights.streamlit.app)

[![Python](https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Snowflake](https://img.shields.io/badge/-Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://snowflake.com/)
[![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

This application 
1. Hits the snowflake.account_usage.login_history table to fetch the IPs, usernames, and login counts
2. Uses IP2LOCATION data to convert the IP to a location
3. Displays a map and table showing you the City, State, IP, username, and login counts

## Setup Instructions

### Create a virtual env, install dependencies, and then run the streamlit app

#### For Mac/Linux
```bash
python3 -m venv venv && source venv/bin/activate && pip3 install --upgrade pip && pip3 install -r requirements.txt && streamlit run app.py
```

#### For Windows
```powershell
py -m venv venv; .\venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install -r requirements.txt; streamlit run app.py
```
