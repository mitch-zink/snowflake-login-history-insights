# Snowflake Login History Insights
[![Open with Streamlit](https://img.shields.io/badge/-Open%20with%20Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)]([https://snow-table-to-csv-exporter.streamlit.app/](https://snow-table-to-csv-exporter.streamlit.app/)) 
[![Python](https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Snowflake](https://img.shields.io/badge/-Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://snowflake.com/)
[![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

Snowflake login history gets locally computed using ip to geo location data

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
