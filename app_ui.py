import streamlit as st
import requests

# Backend API URL
API_URL = "https://afc-fencing-app-1.onrender.com"

st.title("AFC Fencing Job Estimator")

# === Submit Job Details ===
st.header("Submit Job Details")

client_name = st.text_input("Client Name")
contact_info = st.text_input("Contact Info")
job_address = st.text_input("Job Address")
job_scope = st.text_area("Job Scope")
notes = st.text_area("Notes (Optional)")

if st.button("Submit Job"):
    payload = {
        "client_name": client_name,
        "contact_info": contact_info,
        "job_address": job_address,
        "job_scope": job_scope,
        "notes": notes
    }
    response = requests.post(f"{API_URL}/new_bid/job_details", json=payload)
    if response.status_code == 200:
        st.success(f"Job Created! ID: {response.json()['job_id']}")
    else:
        st.error(f"Error: {response.json()}")

# === Submit Fence Details ===
st.header("Submit Fence Details")

job_id = st.text_input("Enter Job ID")
fence_type = st.selectbox("Fence Type", ["Chain Link", "SP Wrought Iron", "Vinyl", "Wood"])
linear_feet = st.number_input("Linear Feet", min_value=1)
corner_posts = st.number_input("Corner Posts", min_value=0, step=1)
end_posts = st.number_input("End Posts", min_value=0, step=1)
height = st.number_input("Height (ft)", min_value=1, step=1)
option_d = st.selectbox("Option D", ["No", "Yes"])

if st.button("Submit Fence Details"):
    payload = {
        "job_id": job_id,
        "fence_type": fence_type,
        "linear_feet": linear_feet,
        "corner_posts": corner_posts,
        "end_posts": end_posts,
        "height": height,
        "option_d": option_d
    }
    response = requests.post(f"{API_URL}/new_bid/fence_details", json=payload)
    if response.status_code == 200:
        st.success("Fence details submitted successfully!")
    else:
        st.error(f"Error: {response.json()}")

# === Cost Estimation ===
st.header("Calculate Cost Estimation")

price_per_sq_ft = st.number_input("Price per Square Foot", min_value=0.01, step=0.01)

if st.button("Estimate Cost"):
    payload = {
        "job_id": job_id,
        "price_per_square_foot": price_per_sq_ft,
        "material_prices": {}
    }
    response = requests.post(f"{API_URL}/new_bid/cost_estimation", json=payload)
    if response.status_code == 200:
        cost_data = response.json()["costs"]
        st.write("### Estimated Costs")
        st.json(cost_data)
    else:
        st.error(f"Error: {response.json()}")
