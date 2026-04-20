import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Store Intelligence Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
import os
API_URL = os.getenv("API_URL", "http://localhost:9001") 

# Sidebar
st.sidebar.title("🏪 Store Intelligence")
st.sidebar.markdown("---")

# Discover Stores
st.sidebar.subheader("📍 Active Stores")
try:
    # Quick health check / stores list
    health = requests.get(f"{API_URL}/health").json()
    active_stores = health.get("active_stores", ["STORE_BLR_002"])
    for s in active_stores:
        st.sidebar.code(s)
except:
    st.sidebar.code("STORE_BLR_002")

st.sidebar.markdown("---")
store_id = st.sidebar.text_input("Enter Store ID", value="STORE_BLR_002")
refresh = st.sidebar.button("🔄 Refresh Data")

# Main Header
st.title("📊 Real-Time Store Analytics")
st.markdown(f"Currently monitoring: **{store_id}**")

def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# --- Top Metrics ---
metrics = fetch_data(f"/stores/{store_id}/metrics")

col1, col2, col3, col4 = st.columns(4)

if metrics:
    col1.metric("Total Visitors", metrics.get("total_unique_visitors", 0))
    col2.metric("Converted", metrics.get("converted_visitors", 0))
    col3.metric("Conversion Rate", f"{round(metrics.get('conversion_rate', 0)*100, 1)}%")
    col4.metric("Store Status", "Online", delta="Healthy")
else:
    st.warning("⚠️ Could not connect to API. Please check if the backend is running.")

st.markdown("---")

# --- Layout: Funnel and Anomalies ---
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🛒 Customer Funnel Analysis")
    funnel_data = fetch_data(f"/stores/{store_id}/funnel")
    
    if funnel_data:
        stages = ["Entry", "Zone Visit", "Billing Queue", "Purchase"]
        counts = [
            funnel_data.get("entry", 0), 
            funnel_data.get("zone_visit", 0), 
            funnel_data.get("billing_queue", 0),
            funnel_data.get("purchase", 0)
        ]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=counts,
            textinfo="value+percent initial",
            marker={"color": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]}
        ))
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for funnel visualization.")

with right_col:
    st.subheader("🚨 Behavioral Anomalies")
    anomaly_data = fetch_data(f"/stores/{store_id}/anomalies")
    
    if anomaly_data and anomaly_data["anomalies"]:
        for anomaly in anomaly_data["anomalies"]:
            severity = anomaly["severity"]
            color = "red" if severity == "CRITICAL" else "orange"
            st.markdown(f"""
                <div style="padding:10px; border-radius:5px; border-left:5px solid {color}; background-color:#f0f2f6; margin-bottom:10px">
                    <strong>{anomaly['type']}</strong> ({severity})<br/>
                    <p style="margin-bottom:5px">{anomaly['message']}</p>
                    <div style="font-size:0.85em; color:#444; border-top:1px solid #ddd; padding-top:5px">
                        💡 <b>Action:</b> {anomaly.get('suggested_action', 'Monitor situation')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No anomalies detected in the last hour.")

# --- Footer ---
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
