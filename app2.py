import streamlit as st
import pandas as pd
import os

# Cache the data loading to improve performance
@st.cache_data
def load_data():
    return pd.read_csv("combined_data_final_with_images.csv")

# Load the data
data = load_data()

# Handle missing or invalid data
data["Caliber"] = pd.to_numeric(data["Caliber"], errors="coerce").fillna(-1)  # Numeric cleaning
data.fillna({"Weapon Category": "Unknown", "Origin": "Unknown"}, inplace=True)  # Categorical cleaning

# Ensure the Year columns contain valid numeric data
if "Development" in data.columns:
    data["Development"] = pd.to_numeric(data["Development"], errors="coerce")
if "Production" in data.columns:
    data["Production"] = pd.to_numeric(data["Production"], errors="coerce")

# Sidebar filters
st.sidebar.header("Filter Options")

# Weapon Category Filter
category_filter = st.sidebar.selectbox(
    "Select a Weapon Category", options=data["Weapon Category"].unique(), index=0
)

# Year Filter
if "Development" in data.columns and not data["Development"].dropna().empty:
    min_year = int(data["Development"].dropna().min())
    max_year = int(data["Development"].dropna().max())
    year_range = st.sidebar.slider(
        "Filter by Development Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
    )
    data = data[(data["Development"] >= year_range[0]) & (data["Development"] <= year_range[1])]

# Origin Filter
origin_filter = st.sidebar.multiselect(
    "Select Origin", options=data["Origin"].unique()
)

# Filter data by category and origin
filtered_data = data[data["Weapon Category"] == category_filter]
if origin_filter:
    filtered_data = filtered_data[filtered_data["Origin"].isin(origin_filter)]

# Main content
st.title("Weapon Insights Dashboard")
st.write(f"Showing images for category: **{category_filter}**")

# Display Images
image_base_dir = "weapon_images_final1"
if not filtered_data.empty:
    for _, row in filtered_data.iterrows():
        if pd.notnull(row["Downloaded_Image_Name"]):
            category = row["Weapon Category"]
            image_name = row["Downloaded_Image_Name"]
            image_path = os.path.join(image_base_dir, category, image_name)
            if os.path.exists(image_path):
                st.image(image_path, caption=row["Weapon Name"], use_column_width=True)
else:
    st.warning("No images available for the selected category or filters.")

# Export filtered data
st.write("### Export Filtered Data")
if not filtered_data.empty:
    csv_data = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"{category_filter}_filtered_data.csv",
        mime="text/csv"
    )
else:
    st.warning("No data available for download.")
