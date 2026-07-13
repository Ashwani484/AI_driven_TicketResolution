import streamlit as st
import requests
import datetime
import pandas as pd

API_BASE = "http://127.0.0.1:8080/snow/incident"

st.set_page_config(page_title="ServiceNow Incident Simulator", layout="wide")

st.markdown(
    """
    <style>
        :root {
            --hcl-blue: #005f9e;
            --hcl-blue-dark: #0b3f66;
            --hcl-blue-light: #eaf5ff;
            --hcl-slate: #223242;
            --hcl-border: #d7e6f3;
            --hcl-green: #147d3b;
            --hcl-amber: #b36b00;
        }
        .stApp {
            background: linear-gradient(135deg, #f7fbff 0%, #eef6fc 100%);
        }
        .hero-card {
            background: linear-gradient(135deg, var(--hcl-blue-dark) 0%, var(--hcl-blue) 100%);
            padding: 24px 28px;
            border-radius: 18px;
            color: white;
            box-shadow: 0 8px 24px rgba(11, 63, 102, 0.15);
            margin-bottom: 18px;
        }
        .hero-card h1 {
            margin: 0 0 8px 0;
            font-size: 2rem;
            font-weight: 700;
        }
        .hero-card p {
            margin: 0;
            font-size: 1rem;
            color: #dcefff;
        }
        .top-nav {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 14px;
        }
        .top-nav span {
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 999px;
            padding: 7px 12px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .section-card {
            background: white;
            border: 1px solid var(--hcl-border);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 4px 14px rgba(34, 50, 66, 0.05);
            margin-bottom: 16px;
        }
        .section-card h3 {
            color: var(--hcl-blue-dark);
            margin-top: 0;
        }
        .metric-pill {
            background: var(--hcl-blue-light);
            border: 1px solid var(--hcl-border);
            border-radius: 999px;
            padding: 8px 12px;
            color: var(--hcl-blue-dark);
            font-weight: 600;
            display: inline-block;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f4f9ff 100%);
            border: 1px solid var(--hcl-border);
            border-radius: 14px;
            padding: 14px;
            min-height: 88px;
            box-shadow: 0 4px 12px rgba(34, 50, 66, 0.05);
        }
        .metric-title {
            display: block;
            color: var(--hcl-slate);
            font-size: 0.9rem;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--hcl-blue-dark);
        }
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .status-new { background: #e8f4ff; color: var(--hcl-blue); }
        .status-resolved { background: #eaf8ee; color: var(--hcl-green); }
        .status-inprogress { background: #fff4e8; color: var(--hcl-amber); }
        .incident-card {
            background: white;
            border: 1px solid var(--hcl-border);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(34, 50, 66, 0.03);
        }
        .incident-heading {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
            color: var(--hcl-blue-dark);
            font-weight: 700;
        }
        .incident-meta {
            color: var(--hcl-slate);
            font-size: 0.9rem;
            margin-top: 4px;
        }
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, var(--hcl-blue) 0%, #2b88c8 100%);
            color: white;
            border: none;
            border-radius: 999px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }
        div.stButton > button {
            border-radius: 999px;
            border: 1px solid var(--hcl-border);
            color: var(--hcl-blue-dark);
            background: white;
            padding: 0.5rem 0.9rem;
        }
        div.stButton > button:hover {
            border-color: var(--hcl-blue);
            color: var(--hcl-blue);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Operations Console")
    st.caption("HCL Tech-inspired incident workspace")
    st.markdown("**Quick actions**")
    st.markdown("- Create new incident")
    st.markdown("- Review incident details")
    st.markdown("- Update and resolve")
    st.divider()
    st.markdown("**Workspace status**")
    st.info("All actions below preserve the existing workflow and backend behavior.")

st.markdown(
    """
    <div class="hero-card">
        <div class="metric-pill">HCL Tech-inspired operations experience</div>
        <h1>ServiceNow Incident Resolution Workspace</h1>
        <p>Create, review, update, and monitor incidents through a polished and focused operations console.</p>
        <div class="top-nav">
            <span>Incident Intake</span>
            <span>Change Tracking</span>
            <span>Resolution Workflow</span>
            <span>Service Monitoring</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='section-card'><h3>Incident Intake</h3></div>", unsafe_allow_html=True)
with st.form("incident_form"):
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ['network','server', 'cache', 'optimize'])
        creation_date = st.date_input("Creation Date", datetime.date.today())
        state = st.selectbox("State", ["New", "In Progress", "Resolved", "Closed"])

    with col2:
        urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
        assigned_to = st.text_input("Assigned To", "Ashwani")
        open_by = st.text_input("Opened By", "User123")
    short_description = st.text_input("Short Description", "VPN not working")
    full_description = st.text_area("Full Description", "User unable to connect to VPN from Lucknow office.")

    submitted = st.form_submit_button("Create Incident")

    if submitted:
        payload = {
            "category": category,
            "creation_date": str(creation_date),
            "state": state,
            "urgency": urgency,
            "assigned_to": assigned_to,
            "open_by": open_by,
            "short_description": short_description,
            "full_description": full_description,
            "solution": "",
            "resolution_time": None,
            "escalated_to": "",
            "work_notes": "",
            "resolved_by": ""
        }
        response = requests.post(API_BASE, json=payload)
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ Incident Created! Number: {data['inc_number']}")
        else:
            st.error(f"❌ Error: {response.text}")

st.markdown("<div class='section-card'><h3>Incident Management</h3></div>", unsafe_allow_html=True)
inc_number = st.text_input("Enter Incident Number (e.g., INC00001)")

col1, col2, col3 = st.columns(3)
if col1.button("Get Incident"):
    response = requests.get(f"{API_BASE}/{inc_number}")
    if response.status_code == 200:
        incident = response.json()
        st.subheader(f"Incident {incident['inc_number']}")

        inc = incident["incident"]
        st.markdown(
            f"""
            <div class="section-card">
                <p><strong>Category:</strong> {inc.get('category','')}</p>
                <p><strong>Creation Date:</strong> {inc.get('creation_date','')}</p>
                <p><strong>State:</strong> {inc.get('state','')}</p>
                <p><strong>Urgency:</strong> {inc.get('urgency','')}</p>
                <p><strong>Assigned To:</strong> {inc.get('assigned_to','')}</p>
                <p><strong>Opened By:</strong> {inc.get('open_by','')}</p>
                <p><strong>Short Description:</strong> {inc.get('short_description','')}</p>
                <p><strong>Full Description:</strong> {inc.get('full_description','')}</p>
                <p><strong>Solution:</strong> {inc.get('solution','')}</p>
                <p><strong>Resolution Time:</strong> {inc.get('resolution_time','')}</p>
                <p><strong>Escalated To:</strong> {inc.get('escalated_to','')}</p>
                <p><strong>Resolution Notes:</strong> {inc.get('work_notes','')}</p>
                <p><strong>Resolved By:</strong> {inc.get('resolved_by','')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Incident not found")

if col2.button("Update Incident (PATCH)"):
    updates = {"state": "In Progress", "assigned_to": "NetworkTeam"}
    response = requests.patch(f"{API_BASE}/{inc_number}", json=updates)
    if response.status_code == 200:
        st.success("Incident Updated")
        inc = response.json()["incident"]
        st.markdown(
            f"""
            <div class="section-card">
                <p><strong>State:</strong> {inc.get('state','')}</p>
                <p><strong>Assigned To:</strong> {inc.get('assigned_to','')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Update failed")

if col3.button("Delete Incident"):
    response = requests.delete(f"{API_BASE}/{inc_number}")
    if response.status_code == 200:
        st.success("Incident Deleted")
    else:
        st.error("Delete failed")

st.markdown("<div class='section-card'><h3>Incident Dashboard</h3></div>", unsafe_allow_html=True)
response = requests.get("http://127.0.0.1:8080/snow/incidents")
if response.status_code == 200:
    incidents = response.json()

    new_incidents = [i for i in incidents if i["state"] == "New"]
    resolved_incidents = [i for i in incidents if i["state"] == "Resolved"]
    in_progress_incidents = [i for i in incidents if i["state"] == "In Progress"]

    metric_cols = st.columns(4)
    metric_values = [
        ("Total", len(incidents), "#005f9e"),
        ("New", len(new_incidents), "#0b3f66"),
        ("In Progress", len(in_progress_incidents), "#b36b00"),
        ("Resolved", len(resolved_incidents), "#147d3b"),
    ]
    for col, (label, value, color) in zip(metric_cols, metric_values):
        col.markdown(
            f"""
            <div class="metric-card">
                <span class="metric-title">{label}</span>
                <div class="metric-value" style="color:{color};">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("New Incidents")
    if new_incidents:
        for incident in new_incidents:
            st.markdown(
                f"""
                <div class="incident-card">
                    <div class="incident-heading">
                        <span>{incident.get('inc_number', 'N/A')}</span>
                        <span class="status-badge status-new">New</span>
                    </div>
                    <div><strong>{incident.get('short_description', '')}</strong></div>
                    <div class="incident-meta">Category: {incident.get('category', '')} • Urgency: {incident.get('urgency', '')} • Assigned to: {incident.get('assigned_to', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No new incidents at the moment.")

    st.subheader("Resolved Incidents")
    if resolved_incidents:
        for incident in resolved_incidents:
            st.markdown(
                f"""
                <div class="incident-card">
                    <div class="incident-heading">
                        <span>{incident.get('inc_number', 'N/A')}</span>
                        <span class="status-badge status-resolved">Resolved</span>
                    </div>
                    <div><strong>{incident.get('short_description', '')}</strong></div>
                    <div class="incident-meta">Category: {incident.get('category', '')} • Urgency: {incident.get('urgency', '')} • Resolved by: {incident.get('resolved_by', '') or 'Pending'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No resolved incidents yet.")

    st.subheader("All Incidents")
    st.dataframe(pd.DataFrame(incidents), use_container_width=True, hide_index=True)
