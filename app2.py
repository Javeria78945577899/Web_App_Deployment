import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Cache the data loading to improve performance
@st.cache_data
def load_data():
    return pd.read_csv("combined_data_final_with_images.csv")

# Load the data
data = load_data()

# Handle missing or invalid data
numeric_columns = ["Caliber"]
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce").fillna(-1)  # Convert invalid values to NaN and replace with -1

categorical_columns = ["Weapon Category", "Origin"]
for col in categorical_columns:
    data[col] = data[col].fillna("Unknown")  # Replace missing categorical values with 'Unknown'

# Ensure Year columns are numeric and handle missing values
if "Development" in data.columns:
    data["Development"] = pd.to_numeric(data["Development"], errors="coerce").fillna(-1).astype(int)

# Sidebar filters
st.sidebar.header("Filter Options")

# Weapon Category Filter
if not data["Weapon Category"].dropna().empty:
    weapon_category = st.sidebar.multiselect("Weapon Category", options=data["Weapon Category"].unique())
else:
    weapon_category = None

# Origin Filter
if not data["Origin"].dropna().empty:
    origin = st.sidebar.multiselect("Origin", options=data["Origin"].unique())
else:
    origin = None

# Caliber Slider
valid_caliber_data = data[data["Caliber"] > 0]  # Filter out invalid values
if not valid_caliber_data.empty:
    min_caliber = int(valid_caliber_data["Caliber"].min())
    max_caliber = int(valid_caliber_data["Caliber"].max())
    caliber = st.sidebar.slider("Caliber (mm)", min_value=min_caliber, max_value=max_caliber, step=1)
else:
    caliber = None

# Year Dropdown Filter (for Development Year)
if "Development" in data.columns and not data["Development"].dropna().empty:
    valid_years = sorted(data["Development"].unique())
    year = st.sidebar.selectbox("Select Development Year", options=valid_years)
else:
    year = None

# Filter data based on selected options
filtered_data = data.copy()

if weapon_category:
    filtered_data = filtered_data[filtered_data["Weapon Category"].isin(weapon_category)]

if origin:
    filtered_data = filtered_data[filtered_data["Origin"].isin(origin)]

if caliber:
    filtered_data = filtered_data[filtered_data["Caliber"] == caliber]

if year:
    filtered_data = filtered_data[filtered_data["Development"] == year]

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

# Display images
st.write("### Weapon Images")
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
    st.warning("No images available for the filtered data.")

# Export filtered data
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
