import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import os

app = dash.Dash(__name__)
app.title = "Network Quality Dashboard"

def load_data():
    if not os.path.exists("network_log.csv"):
        return pd.DataFrame(columns=["timestamp", "ping_ms", "download_mbps", "upload_mbps", "server_name", "server_location", "status"])
    
    df = pd.read_csv("network_log.csv")

    # แปลง timestamp อย่างยืดหยุ่น
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', infer_datetime_format=True)

    # ลบแถวที่ datetime แปลงไม่ผ่าน
    df = df.dropna(subset=['timestamp'])

    return df

app.layout = html.Div([
    html.H1("📡 Network Quality Dashboard", style={"textAlign": "center"}),

    dcc.Interval(id="interval-update", interval=60*1000, n_intervals=0),

    dcc.Graph(id="ping-graph"),
    dcc.Graph(id="speed-graph"),
    dcc.Graph(id="status-graph"),

    html.H3("📋 ข้อมูลย้อนหลัง"),
    dcc.Loading(
        dcc.Graph(id="data-table")
    )
])

@app.callback(
    [dash.Output("ping-graph", "figure"),
     dash.Output("speed-graph", "figure"),
     dash.Output("status-graph", "figure"),
     dash.Output("data-table", "figure")],
    [dash.Input("interval-update", "n_intervals")]
)
def update_graphs(n):
    df = load_data()
    if df.empty:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Line: Ping
    fig_ping = px.line(df, x="timestamp", y="ping_ms", title="📶 Ping (ms)", markers=True)

    # Line: Download / Upload
    fig_speed = px.line(df, x="timestamp", y=["download_mbps", "upload_mbps"], title="📥 Download / 📤 Upload (Mbps)", markers=True)

    # Bar: Status Count
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig_status = px.bar(status_counts, x="status", y="count", color="status", title="🔍 Network Status Summary")

    # Scatter with status as text
    fig_table = px.scatter(df, x="timestamp", y="download_mbps", text="status", title="📊 สรุปย้อนหลัง (สถานะ + Download Speed)")
    fig_table.update_traces(mode='markers+text', textposition='top center')

    return fig_ping, fig_speed, fig_status, fig_table

if __name__ == "__main__":
    app.run(debug=True)

