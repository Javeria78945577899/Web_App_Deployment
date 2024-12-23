import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
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

# Function to normalize category names for matching folder names
def normalize_name(name):
    """Normalize a name to handle underscores, spaces, and case insensitivity."""
    return name.lower().replace(" ", "_").replace("-", "_")

# Function to find image files matching the category
def find_images_for_category(base_folder, category_name):
    """Find all images in a folder matching the normalized category name."""
    normalized_category = normalize_name(category_name)
    images = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if normalized_category in normalize_name(root):
                images.append((os.path.join(root, file), file))  # Return full path and file name
    return images

# Function to load details for the images from the database
def load_image_details(file_name):
    """Load additional details for a given image from the database table."""
    query = f"""
    SELECT Weapon_Name AS 'Weapon Name', Development AS 'Development era', Production as "Production era", Origin, 
           Weapon_Category AS 'Weapon Type', Status, Designations AS 'Designation', Caliber
    FROM weapon_data1
    WHERE Downloaded_Image_Name = '{file_name}'
    """
    result = pd.read_sql(query, engine)
    if not result.empty:
        return result.iloc[0].dropna().to_dict()  # Drop any columns with NaN values
    return {}

# Function to create a PDF
def create_pdf(images_with_details, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for image_path, details in images_with_details:
        pdf.add_page()

        # Add the image
        if os.path.exists(image_path):
            pdf.image(image_path, x=10, y=10, w=100)

        # Add the details
        pdf.set_font("Arial", size=12)
        pdf.ln(110)  # Move below the image
        for key, value in details.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)

    pdf.output(output_file)

# Base image directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "..", "weapon_images_final1")
placeholder_image_path = os.path.join(IMAGE_FOLDER, "placeholder.jpeg")

# Get the category from the page name
category_name = os.path.splitext(os.path.basename(__file__))[0].replace("_", " ")

# Find images for the category
images = find_images_for_category(IMAGE_FOLDER, category_name)

# Main content
st.title(f"Category: {category_name.replace('_', ' ').title()}")
st.write(f"Explore all the weapons under the category: {category_name.replace('_', ' ').title()}")

# Filters
st.write("### Filter Options")
col1, col2 = st.columns(2)
with col1:
    year_query = f"SELECT DISTINCT Development FROM weapon_data1 WHERE Weapon_Category = '{category_name}' AND Development IS NOT NULL"
    available_years = ["All"] + sorted(pd.read_sql(year_query, engine)["Development"].unique())
    selected_year = st.selectbox("Filter by Year", options=available_years)
with col2:
    origin_query = f"SELECT DISTINCT Origin FROM weapon_data1 WHERE Weapon_Category = '{category_name}' AND Origin IS NOT NULL"
    available_origins = ["All"] + sorted(pd.read_sql(origin_query, engine)["Origin"].unique())
    selected_origin = st.selectbox("Filter by Origin", options=available_origins)

# Apply filters to the images
filtered_images = []
for image_path, file_name in images:
    details = load_image_details(file_name)
    if details and (selected_year == "All" or details.get("Year") == selected_year) and \
       (selected_origin == "All" or details.get("Origin") == selected_origin):
        filtered_images.append((image_path, file_name, details))

# Display images and their names
if filtered_images:
    st.write("### Weapon Images")
    cols_per_row = 4  # Adjust number of images per row
    rows = [filtered_images[i:i + cols_per_row] for i in range(0, len(filtered_images), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (image_path, file_name, details) in zip(cols, row):
            if os.path.exists(image_path):
                col.image(image_path, caption=file_name, use_container_width=True)
            else:
                col.image(placeholder_image_path, caption="Image Not Available", use_container_width=True)

            # Add a button for details
            if col.button(f"Details: {file_name}", key=f"details_button_{file_name}"):
                with st.expander(f"Details of {file_name}", expanded=True):
                    for key, value in details.items():
                        st.write(f"**{key}:** {value}")

    # Add a download button for the PDF
    pdf_file = os.path.join(BASE_DIR, "weapon_images_details.pdf")
    create_pdf([(img[0], img[2]) for img in filtered_images], pdf_file)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name="weapon_images_details.pdf",
            mime="application/pdf",
        )
else:
    st.warning(f"No images found for the selected filters.")
import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
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

# Function to normalize category names for matching folder names
def normalize_name(name):
    """Normalize a name to handle underscores, spaces, and case insensitivity."""
    return name.lower().replace(" ", "_").replace("-", "_")

# Function to find image files matching the category
def find_images_for_category(base_folder, category_name):
    """Find all images in a folder matching the normalized category name."""
    normalized_category = normalize_name(category_name)
    images = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if normalized_category in normalize_name(root):
                images.append((os.path.join(root, file), file))  # Return full path and file name
    return images

# Function to load details for the images from the database
def load_image_details(file_name):
    """Load additional details for a given image from the database table."""
    query = f"""
    SELECT Weapon_Name AS 'Weapon Name', Development AS 'Development era', Production AS 'Production era', Origin, 
           Weapon_Category AS 'Weapon Type', Status, Designations AS 'Designation', Caliber
    FROM weapon_data1
    WHERE Downloaded_Image_Name = '{file_name}'
    """
    result = pd.read_sql(query, engine)
    if not result.empty:
        details = result.iloc[0].dropna().to_dict()  # Drop any columns with NaN values
        # Filter out features with "Unknown" values for display
        return {key: value for key, value in details.items() if value != "Unknown"}
    return {}

# Function to create a PDF
# Function to create a PDF with safe encoding
def create_pdf(images_with_details, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for image_path, details in images_with_details:
        pdf.add_page()

        # Add the image
        if os.path.exists(image_path):
            pdf.image(image_path, x=10, y=10, w=100)

        # Add the details
        pdf.set_font("Arial", size=12)
        pdf.ln(110)  # Move below the image
        for key, value in details.items():
            # Safely encode the value to replace unsupported characters
            safe_value = str(value).encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(0, 10, f"{key}: {safe_value}", ln=True)

    pdf.output(output_file)


# Base image directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "..", "weapon_images_final1")
placeholder_image_path = os.path.join(IMAGE_FOLDER, "placeholder.jpeg")

# Get the category from the page name
category_name = os.path.splitext(os.path.basename(__file__))[0].replace("_", " ")

# Find images for the category
images = find_images_for_category(IMAGE_FOLDER, category_name)

# Query normalized category name
year_query = f"""
SELECT DISTINCT Development AS Year 
FROM weapon_data1 
WHERE LOWER(REPLACE(REPLACE(Weapon_Category, ' ', '_'), '-', '_')) = '{category_name}' AND Development IS NOT NULL
"""
available_years = ["All"] + sorted(pd.read_sql(year_query, engine)["Year"].unique())

origin_query = f"""
SELECT DISTINCT Origin 
FROM weapon_data1 
WHERE LOWER(REPLACE(REPLACE(Weapon_Category, ' ', '_'), '-', '_')) = '{category_name}' AND Origin IS NOT NULL
"""
available_origins = ["All"] + sorted(pd.read_sql(origin_query, engine)["Origin"].unique())

# Filters
st.write("### Filter Options")
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Filter by Year", options=available_years)
with col2:
    selected_origin = st.selectbox("Filter by Origin", options=available_origins)

# Main content
st.title(f"Category: {category_name.replace('_', ' ').title()}")
st.write(f"Explore all the weapons under the category: {category_name.replace('_', ' ').title()}")


# Apply filters to the images
filtered_images = []
for image_path, file_name in images:
    details = load_image_details(file_name)
    if details and (selected_year == "All" or details.get("Development era") == selected_year) and \
       (selected_origin == "All" or details.get("Origin") == selected_origin):
        filtered_images.append((image_path, file_name, details))

# Display images and their names
if filtered_images:
    st.write("### Weapon Images")
    cols_per_row = 4  # Adjust number of images per row
    rows = [filtered_images[i:i + cols_per_row] for i in range(0, len(filtered_images), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (image_path, file_name, details) in zip(cols, row):
            if os.path.exists(image_path):
                col.image(image_path, caption=file_name, use_container_width=True)
            else:
                col.image(placeholder_image_path, caption="Image Not Available", use_container_width=True)

            # Add a button for details
            if col.button(f"Details: {file_name}", key=f"details_button_{file_name}"):
                with st.expander(f"Details of {file_name}", expanded=True):
                    for key, value in details.items():
                        st.write(f"**{key}:** {value}")

    # Add a download button for the PDF
    pdf_file = os.path.join(BASE_DIR, "weapon_images_details.pdf")
    create_pdf([(img[0], img[2]) for img in filtered_images], pdf_file)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name="weapon_images_details.pdf",
            mime="application/pdf",
        )
else:
    st.warning(f"No images found for the selected filters.")
