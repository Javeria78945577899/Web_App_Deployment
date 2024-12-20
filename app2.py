import streamlit as st
import pandas as pd
import plotly.express as px
import os
import subprocess
import sys
from st_aggrid import AgGrid
import seaborn as sns
import matplotlib.pyplot as plt

# Cache the data loading to improve performance
@st.cache
def load_data():
    return pd.read_csv("combined_data_final_with_images.csv")

data = load_data()

# Handle missing or invalid data
numeric_columns = ["Caliber", "Barrel Length", "Weight", "Length", "Height"]
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce")
    data[col].fillna(-1, inplace=True)

categorical_columns = ["Weapon Category", "Origin", "Status"]
for col in categorical_columns:
    data[col] = data[col].fillna("Unknown")

# Sidebar filters
st.sidebar.header("Filter Options")
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
valid_caliber_data = data[data["Caliber"] > 0]
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

# Main title
st.title("Weapon Insights Dashboard")
st.write("Explore weapon specifications, search, and visualize data interactively.")

# Dataset Summary
st.write("### Dataset Summary")
st.write(f"**Total Weapons:** {len(data)}")
st.write(f"**Unique Categories:** {data['Weapon Category'].nunique()}")
st.write(f"**Unique Origins:** {data['Origin'].nunique()}")
st.dataframe(data.describe())

# Paginated Table (using st-aggrid)
st.write("### Filtered Data Table")
if not filtered_data.empty:
    AgGrid(filtered_data, enable_enterprise_modules=True)
else:
    st.warning("No data available after applying filters.")

# Threat Distribution Visualization
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

# Correlation Heatmap
st.write("### Correlation Heatmap")
if not filtered_data[numeric_columns].empty:
    corr = filtered_data[numeric_columns].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
else:
    st.warning("Not enough numeric data for correlation heatmap.")

# Categorized Images
st.write("### Weapon Images by Category")
categories = data["Weapon Category"].unique()
selected_category = st.selectbox("Select Category", categories)
if selected_category:
    images_filtered = data[data["Weapon Category"] == selected_category]
    for index, row in images_filtered.iterrows():
        if pd.notnull(row["Downloaded_Image_Name"]):
            image_path = os.path.join("weapon_images_final1", row["Downloaded_Image_Name"])
            if os.path.exists(image_path):
                st.image(image_path, caption=row["Weapon Name"], use_container_width=True)

# Additional Visualization: Line Chart
st.write("### Caliber Trends by Origin")
if not filtered_data.empty:
    line_fig = px.line(
        filtered_data,
        x="Origin",
        y="Caliber",
        color="Weapon Category",
        markers=True,
        title="Caliber Trends by Origin",
    )
    st.plotly_chart(line_fig)
else:
    st.warning("No data available for line chart.")

# Export Filtered Data
st.write("### Export Filtered Data")
if not filtered_data.empty:
    st.download_button(
        label="Download CSV",
        data=filtered_data.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download Excel",
        data=filtered_data.to_excel(index=False, engine="openpyxl"),
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.warning("No data available for download.")
