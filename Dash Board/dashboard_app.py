import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("network_log.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

st.title("📡 Dashboard ตรวจสอบคุณภาพอินเทอร์เน็ต")

st.line_chart(df.set_index("Timestamp")[["Ping (ms)", "Download (Mbps)", "Upload (Mbps)"]])
