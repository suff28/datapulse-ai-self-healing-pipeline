import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8010")

st.set_page_config(page_title="DataPulse", layout="wide")
st.title("DataPulse: AI Self-Healing Data Pipeline")


def api_get(path: str):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str):
    response = requests.post(f"{API_BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


col_a, col_b, col_c = st.columns([1, 1, 3])
with col_a:
    if st.button("Generate Messy Data", use_container_width=True):
        st.session_state["last_action"] = api_post("/generate-sample?rows=250")
with col_b:
    if st.button("Run Pipeline", use_container_width=True):
        st.session_state["last_action"] = api_post("/run")
with col_c:
    if "last_action" in st.session_state:
        st.caption(st.session_state["last_action"])

metrics = api_get("/metrics")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Runs", metrics["total_runs"])
m2.metric("Rows", metrics["total_rows"])
m3.metric("Clean Rows", metrics["clean_rows"])
m4.metric("Quarantined", metrics["quarantined_rows"])
m5.metric("Avg Quality", float(metrics["avg_quality_score"]))

runs = pd.DataFrame(api_get("/runs?limit=30"))
if not runs.empty:
    st.subheader("Pipeline Runs")
    st.dataframe(runs, use_container_width=True, hide_index=True)

    chart_df = runs.sort_values("started_at")
    fig = px.line(chart_df, x="started_at", y="quality_score", markers=True, title="Quality Score by Run")
    st.plotly_chart(fig, use_container_width=True)

quality = pd.DataFrame(api_get("/quality?limit=100"))
if not quality.empty:
    st.subheader("Data Quality Checks")
    st.dataframe(quality, use_container_width=True, hide_index=True)

suggestions = pd.DataFrame(api_get("/repair-suggestions?limit=100"))
if not suggestions.empty:
    st.subheader("AI-Assisted Repair Suggestions")
    st.dataframe(suggestions, use_container_width=True, hide_index=True)

quarantine = pd.DataFrame(api_get("/quarantine?limit=50"))
if not quarantine.empty:
    st.subheader("Quarantined Records")
    st.dataframe(quarantine, use_container_width=True, hide_index=True)
