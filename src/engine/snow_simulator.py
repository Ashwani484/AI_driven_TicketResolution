import streamlit as st
import requests
import datetime

API_BASE = "http://127.0.0.1:8080/snow/incident"

st.set_page_config(page_title="ServiceNow Incident Simulator", layout="wide")
st.title("🛠️ ServiceNow Incident Simulator (DB-backed)")

# Sidebar navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Create Incident", "Manage Incident", "Resolved Incidents"]
)

# ---------------- Home ----------------
if menu == "Home":
    st.markdown("""
    Welcome to the **Incident Simulator**.  
    Use the sidebar to navigate:
    - ➕ Create New Incident
    - 🔍 Manage Incident
    - 📊 View Resolved Incidents
    """)

# ---------------- Create Incident ----------------
elif menu == "Create Incident":
    st.header("➕ Create New Incident")
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

# ---------------- Manage Incident ----------------
elif menu == "Manage Incident":
    st.header("🔍 Manage Incident")
    inc_number = st.text_input("Enter Incident Number (e.g., INC00001)")

    col1, col2, col3 = st.columns(3)

    if col1.button("Get Incident"):
        response = requests.get(f"{API_BASE}/{inc_number}")
        if response.status_code == 200:
            incident = response.json()
            st.subheader(f"Incident {incident['inc_number']}")
            inc = incident["incident"]
            for k, v in inc.items():
                st.markdown(f"**{k}:** {v}")
        else:
            st.error("Incident not found")

    if col2.button("Update Incident (PATCH)"):
        updates = {"state": "In Progress", "assigned_to": "NetworkTeam"}
        response = requests.patch(f"{API_BASE}/{inc_number}", json=updates)
        if response.status_code == 200:
            st.success("Incident Updated")
            inc = response.json()["incident"]
            st.markdown(f"**State:** {inc.get('state','')}")
            st.markdown(f"**Assigned To:** {inc.get('assigned_to','')}")
        else:
            st.error("Update failed")

    if col3.button("Delete Incident"):
        response = requests.delete(f"{API_BASE}/{inc_number}")
        if response.status_code == 200:
            st.success("Incident Deleted")
        else:
            st.error("Delete failed")

# ---------------- Resolved Incidents ----------------
elif menu == "Resolved Incidents":
    st.header("📊 Incident Dashboard")
    response = requests.get("http://127.0.0.1:8080/snow/incidents")

    if response.status_code == 200:
        incidents = response.json()
        new_incidents = [i for i in incidents if i["state"] == "New"]
        resolved_incidents = [i for i in incidents if i["state"] == "Resolved"]

        st.subheader("🟢 New Incidents")
        st.table(new_incidents)

        st.subheader("🔵 Resolved Incidents")
        st.table(resolved_incidents)

        st.subheader("📋 All Incidents")
        st.table(incidents)
    else:
        st.error("Failed to fetch incidents")
