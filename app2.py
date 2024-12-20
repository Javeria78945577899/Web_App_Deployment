import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Required packages (this part installs missing packages)
import subprocess
import sys

required_packages = ["pandas", "streamlit", "plotly"]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Load the data
data = pd.read_csv("combined_data_final_with_images.csv")

# Handle missing or invalid data
numeric_columns = ["Caliber"]
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce")  # Convert invalid values to NaN
    data[col].fillna(-1, inplace=True)  # Replace NaN with a default value (-1)

categorical_columns = ["Weapon Category", "Origin"]
for col in categorical_columns:
    data[col] = data[col].fillna("Unknown")  # Replace missing categorical values with 'Unknown'

# Sidebar filters
st.sidebar.header("Filter Options")

# Filter options initialization
filters = {}

# Add Weapon Category filter if valid values exist
if not data["Weapon Category"].dropna().empty:
    weapon_category = st.sidebar.multiselect("Weapon Category", options=data["Weapon Category"].unique())
    if weapon_category:
        filters["Weapon Category"] = weapon_category

# Add Origin filter if valid values exist
if not data["Origin"].dropna().empty:
    origin = st.sidebar.multiselect("Origin", options=data["Origin"].unique())
    if origin:
        filters["Origin"] = origin

# Add Caliber slider if valid numeric data exists
valid_caliber_data = data[data["Caliber"] > 0]  # Filter out invalid values
if not valid_caliber_data.empty:
    min_caliber = int(valid_caliber_data["Caliber"].min())
    max_caliber = int(valid_caliber_data["Caliber"].max())
    caliber = st.sidebar.slider("Caliber (mm)", min_value=min_caliber, max_value=max_caliber, step=1)
    filters["Caliber"] = caliber

# Filter the data based on selected filters
filtered_data = data.copy()

if "Weapon Category" in filters:
    filtered_data = filtered_data[filtered_data["Weapon Category"].isin(filters["Weapon Category"])]

if "Origin" in filters:
    filtered_data = filtered_data[filtered_data["Origin"].isin(filters["Origin"])]

if "Caliber" in filters:
    filtered_data = filtered_data[filtered_data["Caliber"] == filters["Caliber"]]

# Main content
st.title("Weapon Insights Dashboard")
st.write("Explore weapon specifications, search, and visualize data interactively.")

# Display filtered data
st.write("### Filtered Data Table")
st.dataframe(filtered_data)

# Plot visuals
st.write("### Threat Distribution by Origin")
if not filtered_data.empty:
    fig = px.bar(
        filtered_data,
        x="Origin",
        y="Weapon Name",
        color="Weapon Category",
        title="Threat Distribution by Origin",
    )
    st.plotly_chart(fig)
else:
    st.warning("No data available for visualization.")

# Interactive Map (if Latitude and Longitude columns exist)
if "Latitude" in filtered_data.columns and "Longitude" in filtered_data.columns:
    st.write("### Geospatial Threat Map")
    map_fig = px.scatter_geo(
        filtered_data,
        lat="Latitude",
        lon="Longitude",
        color="Weapon Category",
        hover_name="Weapon Name",
        title="Threat Locations",
    )
    st.plotly_chart(map_fig)
else:
    st.warning("Latitude and Longitude data are missing for geospatial visualization.")

# Display images
st.write("### Weapon Images")
image_base_dir = "weapon_images_final1"
if not filtered_data.empty:
    for index, row in filtered_data.iterrows():
        if pd.notnull(row["Downloaded_Image_Name"]):
            category = row["Weapon Category"]
            image_name = row["Downloaded_Image_Name"]
            image_path = os.path.join(image_base_dir, category, image_name)
            
            if os.path.exists(image_path):
                st.image(image_path, caption=row["Weapon Name"], use_container_width=True)
            else:
                st.warning(f"Image not found: {image_path}")
else:
    st.warning("No images available for the filtered data.")

# Export data
st.write("### Export Filtered Data")
if not filtered_data.empty:
    st.download_button(
        label="Download CSV",
        data=filtered_data.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv",
    )
else:
    st.warning("No filtered data available for download.")
