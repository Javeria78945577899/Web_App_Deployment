import streamlit as st
import pandas as pd
import os
import re
import plotly.express as px
from sqlalchemy import create_engine

# Database connection details
DB_HOST = "junction.proxy.rlwy.net"
DB_USER = "root"
DB_PASSWORD = "GKesHFOMJkurJYvpaVNuqRgTEGYOgFQN"
DB_NAME = "railway"
DB_PORT = "27554"

# Define the database connection
@st.cache_resource
def get_engine():
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    return engine

engine = get_engine()

# Clean Development Year Function
def clean_year(year_value):
    if pd.isnull(year_value):
        return None
    match = re.match(r"(\d{4})(?:\s*-\s*(\d{4}))?", str(year_value))
    if match:
        return match.group(0)
    return None

# Load data from weapon_data1
@st.cache_data
def load_data():
    query = """
    SELECT wd.*, di.preprocessed_path 
    FROM weapon_data1 wd
    LEFT JOIN dbo_images di 
    ON wd.Weapon_Name = SUBSTRING_INDEX(di.image_name, '_aug', 1);
    """
    data = pd.read_sql(query, engine)
    # Clean the Development column
    data["Development"] = data["Development"].apply(clean_year)
    return data

# Load data

data = load_data()

# Function to recursively search for an image in subfolders
def find_image_recursive(base_folder, image_name):
    for root, dirs, files in os.walk(base_folder):
        if image_name in files:
            return os.path.join(root, image_name)
    return None

# Sidebar filters with conditional options
st.sidebar.header("Filter Options")

# Weapon Category Filter
weapon_category_options = ["Choose an option"] + sorted(data["Weapon_Category"].dropna().unique().tolist())
weapon_category = st.sidebar.selectbox("Weapon Category", options=weapon_category_options, index=0)

# Origin Filter
if weapon_category != "Choose an option":
    origin_options = ["Choose an option"] + sorted(
        data[data["Weapon_Category"] == weapon_category]["Origin"].dropna().unique().tolist()
    )
else:
    origin_options = ["Choose an option"] + sorted(data["Origin"].dropna().unique().tolist())
origin = st.sidebar.selectbox("Origin", options=origin_options, index=0)

# Year Filter
if weapon_category != "Choose an option" and origin != "Choose an option":
    year_options = ["Choose an option"] + sorted(
        data[
            (data["Weapon_Category"] == weapon_category)
            & (data["Origin"] == origin)
        ]["Development"].dropna().unique().tolist()
    )
elif weapon_category != "Choose an option":
    year_options = ["Choose an option"] + sorted(
        data[data["Weapon_Category"] == weapon_category]["Development"].dropna().unique().tolist()
    )
elif origin != "Choose an option":
    year_options = ["Choose an option"] + sorted(
        data[data["Origin"] == origin]["Development"].dropna().unique().tolist()
    )
else:
    year_options = ["Choose an option"] + sorted(data["Development"].dropna().unique().tolist())
year = st.sidebar.selectbox("Select Development Year", options=year_options, index=0)

# Filter the data based on selections
filtered_data = data.copy()
if weapon_category != "Choose an option":
    filtered_data = filtered_data[filtered_data["Weapon_Category"] == weapon_category]
if origin != "Choose an option":
    filtered_data = filtered_data[filtered_data["Origin"] == origin]
if year != "Choose an option":
    filtered_data = filtered_data[filtered_data["Development"] == year]

# Main content
st.title("Weapon Insights Dashboard")
st.write("Explore weapon specifications, search, and visualize data interactively.")

# Display filtered data
st.write("### Filtered Data Table")
st.dataframe(filtered_data)

# Threat Distribution by Origin
st.write("### Threat Distribution by Origin")
if not filtered_data.empty:
    fig = px.bar(
        filtered_data,
        x="Origin",
        y="Weapon_Name",
        color="Weapon_Category",
        title="Threat Distribution by Origin",
        labels={"Weapon_Name": "Weapon Count", "Origin": "Country of Origin"},
    )
    st.plotly_chart(fig)
else:
    st.warning("No data available for visualization.")

# Display images in a grid layout
st.write("### Weapon Images")
IMAGE_FOLDER = "weapon_images_final1"
placeholder_image_path = "weapon_images_final1/placeholder.jpeg"  # Ensure this exists
if not filtered_data.empty:
    cols_per_row = 6  # Number of images per row
    rows = [filtered_data.iloc[i:i + cols_per_row] for i in range(0, len(filtered_data), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (idx, weapon) in zip(cols, row.iterrows()):
            image_name = weapon.get("Downloaded_Image_Name", weapon.get("Weapon_Name"))
            if pd.notnull(image_name):
                image_path = find_image_recursive(IMAGE_FOLDER, image_name)

                if image_path:  # If image is found
                    col.image(image_path, caption=weapon["Weapon_Name"], use_container_width=True)
                elif os.path.exists(placeholder_image_path):  # If placeholder exists
                    col.image(placeholder_image_path, caption="Image Not Available", use_container_width=True)
                else:  # If no image or placeholder is found
                    col.error("Image and placeholder not found.")

                if col.button(f"Details: {weapon['Weapon_Name']}", key=f"details_button_{idx}"):
                    with st.expander(f"Details of {weapon['Weapon_Name']}", expanded=True):
                        st.write("**Name:**", weapon["Weapon_Name"])
                        st.write("**Category:**", weapon["Weapon_Category"])
                        st.write("**Origin:**", weapon["Origin"])
                        st.write("**Development Year:**", weapon["Development"])
                        st.write("**Type:**", weapon["Type"])
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
