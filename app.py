import streamlit as st
import pandas as pd
import os
import plotly.express as px
from sqlalchemy import create_engine
import importlib.util

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

# Load data from weapon_data1
@st.cache_data
def load_data():
    query = """
    SELECT wd.* 
    FROM weapon_data1 wd 
    LEFT JOIN dbo_images di 
    ON wd.Weapon_Name = SUBSTRING_INDEX(di.image_name, '_aug', 1);
    """
    data = pd.read_sql(query, engine)
    return data

# Load data
data = load_data()

# Base image directory
IMAGE_FOLDER = "weapon_images_final1"
placeholder_image_path = os.path.join(IMAGE_FOLDER, "placeholder.jpeg")

# Handle Page Navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Navigation Function
def navigate_to(page):
    st.session_state.current_page = page

# Main Navigation Bar
st.sidebar.markdown("### Navigation")
if st.sidebar.button("Back to Dashboard"):
    navigate_to("Home")

# Dynamically detect pages from the Pages folder
pages_dir = "Pages"
if os.path.exists(pages_dir):
    for file in os.listdir(pages_dir):
        if file.endswith(".py") and file != "__init__.py":
            page_name = file.replace(".py", "").replace("_", " ").title()
            if st.sidebar.button(f"Go to {page_name}", key=file):
                navigate_to(page_name)

# Main Content
if st.session_state.current_page == "Home":
    st.title("Weapon Insights Dashboard")
    st.write("Explore weapon specifications, search, and visualize data interactively.")

    # Display filtered data
    st.write("### Filtered Data Table")
    st.dataframe(data)

    # Threat Distribution by Origin
    st.write("### Threat Distribution by Origin")
    if not data.empty:
        fig = px.bar(
            data,
            x="Origin",
            y="Weapon_Name",
            color="Weapon_Category",
            title="Threat Distribution by Origin",
            labels={"Weapon_Name": "Weapon Name", "Origin": "Country of Origin"},
        )
        st.plotly_chart(fig)
    else:
        st.warning("No data available for visualization.")

    # Load Top 5 Countries Data
    @st.cache_data
    def load_top_countries():
        query = """
    SELECT Origin, COUNT(*) as Weapon_Count
    FROM weapon_data1
    GROUP BY Origin
    ORDER BY Weapon_Count DESC
    LIMIT 5;
    """
        return pd.read_sql(query, engine)

    # Display Top 5 Countries Map
    top_countries_data = load_top_countries()
    st.title("Top 5 Countries by Weapon Production")
    st.write("This map shows the top 5 countries that produce the highest number of weapons.")

    if not top_countries_data.empty:
        # Display the map
        st.write("### Top 5 Countries Map")
        fig = px.choropleth(
            top_countries_data,
            locations="Origin",
            locationmode="country names",
            color="Weapon_Count",
            hover_name="Origin",
            title="Top 5 Countries by Weapon Production",
            color_continuous_scale=px.colors.sequential.Plasma,
        )
        fig.update_layout(geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"))
        st.plotly_chart(fig)

        # Display the data in a table
        st.write("### Top 5 Countries Data")
        st.dataframe(top_countries_data)
    else:
        st.warning("No data available to display.")

    # Display Categories with Representative Images
    st.write("### Weapon Categories")
    cols_per_row = 3
    rows = [categories[i:i + cols_per_row] for i in range(0, len(categories), cols_per_row)]
    for row in rows:
        cols = st.columns(len(row))
        for col, category in zip(cols, row):
            category_dir = os.path.join(IMAGE_FOLDER, category.replace(" ", "_"))

            category_image = None
            if os.path.exists(category_dir) and os.path.isdir(category_dir):
                for file_name in os.listdir(category_dir):
                    if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                        category_image = os.path.join(category_dir, file_name)
                        break

            if category_image and os.path.exists(category_image):
                col.image(category_image, caption=category, use_container_width=True)
            elif os.path.exists(placeholder_image_path):
                col.image(placeholder_image_path, caption=f"{category} (Placeholder)", use_container_width=True)
            else:
                col.error(f"No image available for {category}")

            if col.button(f"Visit {category}", key=f"visit-{category}"):
                navigate_to(category)

# Category Page
else:
    category = st.session_state.current_page
    st.title(f"Category: {category}")
    st.write(f"Here are the details for the category: {category}")

    category_dir = os.path.join(IMAGE_FOLDER, category.replace(" ", "_"))
    if os.path.exists(category_dir) and os.path.isdir(category_dir):
        images = [
            os.path.join(category_dir, f)
            for f in os.listdir(category_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        for img in images:
            st.image(img, use_container_width=True)
    else:
        st.warning(f"No images available for the category: {category}")

    if st.button("Back to Dashboard"):
        navigate_to("Home")

# News Section
st.write("### News Section")

# Prepare the data for the news
news_data = data[["Weapon_Name", "Development", "Weight", "Status", "Downloaded_Image_Name"]].dropna().reset_index(
    drop=True
)
total_news_items = len(news_data)

# State to keep track of the current news index
if "news_index" not in st.session_state:
    st.session_state.news_index = 0


# Function to move to the next news item
def next_news():
    st.session_state.news_index = (st.session_state.news_index + 1) % total_news_items


# Function to move to the previous news item
def prev_news():
    st.session_state.news_index = (st.session_state.news_index - 1) % total_news_items


# Display the current news item
current_news = news_data.iloc[st.session_state.news_index]

# Get the image for the current news item
image_path = None
if pd.notnull(current_news["Downloaded_Image_Name"]):
    image_name = current_news["Downloaded_Image_Name"]
    weapon_category = current_news["Weapon_Name"].replace(" ", "_")
    category_folder = os.path.join(IMAGE_FOLDER, weapon_category)

    if os.path.exists(category_folder) and os.path.isdir(category_folder):
        image_path = os.path.join(category_folder, image_name)

if not image_path or not os.path.exists(image_path):  # Use placeholder if image not found
    image_path = placeholder_image_path

# Display the news image
st.image(
    image_path,
    caption=f"Image for {current_news['Weapon_Name']}",
    use_container_width=True,
)

# Display the news description
st.write(
    f"**Here is {current_news['Weapon_Name']}**, developed in **{current_news['Development']}**, "
    f"having a weight of **{current_news['Weight']}**. Its current status is **{current_news['Status']}**."
)

# Navigation buttons for the news
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("⬅️ Previous"):
        prev_news()
with col3:
    if st.button("➡️ Next"):
        next_news()


# Handle other pages dynamically
else:
    page_name = st.session_state.current_page
    page_file = f"{page_name.replace(' ', '_').lower()}.py"
    page_path = os.path.join(pages_dir, page_file)
    if os.path.exists(page_path):
        spec = importlib.util.spec_from_file_location(page_name, page_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[page_name] = module
        spec.loader.exec_module(module)
    else:
        st.error(f"Page '{page_name}' not found.")

