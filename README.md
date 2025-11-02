# isp-speed-analyzer-unraid
Streamlit-based ISP Speed Analyzer for Unraid with alerts and daily graphs.

<Container>
ISP Speed Analyzer

Support - https://github.com/CTLALTDELETE/isp-speed-analyzer-unraid
Project - https://github.com/CTLALTDELETE/isp-speed-analyzer-unraid
  
Overview
Streamlit dashboard that logs Ookla Speedtests, creates daily graphs, and sends alerts if speeds drop below a threshold.
  
Category - Network:Monitoring

<img width="256" height="256" alt="isp-speed-analyzer-icon-github" src="https://github.com/user-attachments/assets/f7e18f0b-275a-4765-b211-a86729c4e357" />

 
WebUI - http://[IP]:[PORT:8501]

  <Config Name="AppData" Target="/root/speedtest_logs"
          Default="/mnt/user/appdata/isp_analyzer_logs" Mode="rw"
          Description="Persistent logs" Type="Path"/>

  <Config Name="Port 8501" Target="8501" Default="8501" Mode="tcp"
          Description="Web UI Port" Type="Port"/>

  <Config Name="Alert Threshold" Target="ALERT_THRESHOLD" Default="800" Mode="env"
          Description="Mbps threshold" Type="Variable"/>

  <Config Name="Alert Email" Target="ALERT_EMAIL" Default="" Mode="env"
          Description="Email alert recipient" Type="Variable"/>

  <Config Name="Webhook URL" Target="WEBHOOK_URL" Default="" Mode="env"
          Description="Optional webhook" Type="Variable"/>
</Container>
