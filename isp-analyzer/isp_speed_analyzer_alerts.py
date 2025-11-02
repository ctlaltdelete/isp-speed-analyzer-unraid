#!/usr/bin/env python3
"""
ISP Speed Analyzer with Alerts & Daily Graphs
---------------------------------------------
• Streamlit dashboard (port 8501)
• Automated Ookla speed tests
• Email/Webhook alert when download < threshold
• Daily average graph auto-saved to plots/
"""

import os, json, time, re, threading, subprocess, shutil, smtplib, requests, schedule
from datetime import datetime, timedelta
from email.message import EmailMessage
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

DATA_DIR = "/root/speedtest_logs"
os.makedirs(DATA_DIR, exist_ok=True)
PLOTS_DIR = os.path.join(DATA_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "speedtest_data.json")

THRESHOLD = float(os.getenv("ALERT_THRESHOLD", 800))
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# -------------------------------------------------------------
# Helpers
# -------------------------------------------------------------
def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(float(str(value).replace("−", "-")))
    except Exception:
        return default

def load_results():
    rows=[]
    if not os.path.exists(DATA_FILE): return pd.DataFrame()
    with open(DATA_FILE,"r") as f:
        for line in f:
            try:
                o=json.loads(line)
                rows.append(o)
            except Exception: pass
    df=pd.DataFrame(rows)
    if not df.empty:
        df["recorded_at"]=pd.to_datetime(df["recorded_at"])
        df["download"]=df["download"]/1e6
        df["upload"]=df["upload"]/1e6
    return df

# -------------------------------------------------------------
# Ookla speed test
# -------------------------------------------------------------
def run_speedtest():
    cli = shutil.which("speedtest") or shutil.which("speedtest-cli")
    if not cli:
        raise RuntimeError("No speedtest CLI found")
    args=[cli,"--json"]
    try:
        result=subprocess.check_output(args,text=True)
        data=json.loads(result)
        data["recorded_at"]=datetime.utcnow().isoformat()
        with open(DATA_FILE,"a") as f:
            f.write(json.dumps(data)+"\n")
        return data
    except Exception as e:
        return {"error":str(e)}

# -------------------------------------------------------------
# Alert functions
# -------------------------------------------------------------
def send_email_alert(download_mbps):
    if not ALERT_EMAIL: return
    msg=EmailMessage()
    msg["Subject"]="⚠️ ISP Speed Alert"
    msg["From"]=ALERT_EMAIL
    msg["To"]=ALERT_EMAIL
    msg.set_content(f"Download speed dropped to {download_mbps:.1f} Mbps (below {THRESHOLD} Mbps)")
    try:
        with smtplib.SMTP("localhost") as s:
            s.send_message(msg)
    except Exception as e:
        print("Email alert failed:", e)

def send_webhook_alert(download_mbps):
    if not WEBHOOK_URL: return
    payload={"text": f"⚠️ ISP Speed Alert: {download_mbps:.1f} Mbps (<{THRESHOLD})"}
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print("Webhook alert failed:", e)

def check_alert(result):
    if "download" in result:
        download_mbps=result["download"]/1e6
        if download_mbps < THRESHOLD:
            print(f"ALERT: {download_mbps:.1f} Mbps < {THRESHOLD}")
            send_email_alert(download_mbps)
            send_webhook_alert(download_mbps)

# -------------------------------------------------------------
# Daily average plot
# -------------------------------------------------------------
def generate_daily_graph():
    df=load_results()
    if df.empty: return
    df["date"]=df["recorded_at"].dt.date
    daily=df.groupby("date")[["download","upload"]].mean()
    plt.figure()
    daily["download"].plot(label="Download (Mbps)")
    daily["upload"].plot(label="Upload (Mbps)")
    plt.axhline(THRESHOLD,color="r",linestyle="--",label=f"Threshold {THRESHOLD} Mbps")
    plt.title("Daily Average Speeds")
    plt.ylabel("Mbps")
    plt.legend()
    plt.tight_layout()
    filename=os.path.join(PLOTS_DIR,f"daily_avg_{datetime.utcnow().date()}.png")
    plt.savefig(filename)
    plt.close()
    print("Saved daily graph:", filename)

# -------------------------------------------------------------
# Scheduler thread (runs 3×/day + daily graph)
# -------------------------------------------------------------
def scheduler_loop(stop_event):
    schedule.every(8).hours.do(lambda: check_alert(run_speedtest()))
    schedule.every().day.at("23:59").do(generate_daily_graph)
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(30)

# -------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------
st.set_page_config(page_title="ISP Speed Analyzer with Alerts", layout="wide")
st.title("🌐 ISP Speed Analyzer with Alerts & Daily Graphs")

col1,col2=st.columns(2)
if "thread" not in st.session_state:
    st.session_state["stop"]=threading.Event()
    st.session_state["thread"]=None

if col1.button("⚡ Run Single Test"):
    with st.spinner("Running speed test (~30 s)..."):
        result=run_speedtest()
        check_alert(result)
    if "error" in result: st.error(result["error"])
    else: st.success("✅ Test complete"); st.json(result)

if col2.button("🕒 Start Automated Testing (3/day)"):
    if st.session_state["thread"] and st.session_state["thread"].is_alive():
        st.warning("Already running.")
    else:
        st.session_state["stop"].clear()
        t=threading.Thread(target=scheduler_loop,args=(st.session_state["stop"],),daemon=True)
        t.start(); st.session_state["thread"]=t; st.success("Automation started!")

if st.session_state["thread"] and st.session_state["thread"].is_alive():
    if st.button("🛑 Stop Automation"):
        st.session_state["stop"].set(); st.success("Automation stopped.")

df=load_results()
if not df.empty:
    st.subheader("📊 Results")
    st.dataframe(df[["recorded_at","download","upload","ping"]].sort_values("recorded_at",ascending=False))
    st.metric("Avg Download (Mbps)",round(df["download"].mean(),2))
    st.metric("Avg Upload (Mbps)",round(df["upload"].mean(),2))
    st.line_chart(df.set_index("recorded_at")[["download","upload"]])

st.subheader("⚙️ Current Settings")
st.write(f"Alert Threshold: {THRESHOLD} Mbps")
if ALERT_EMAIL: st.write(f"Email Alerts → {ALERT_EMAIL}")
if WEBHOOK_URL: st.write("Webhook Alerts → Enabled")
st.write(f"Logs stored at: {DATA_FILE}")