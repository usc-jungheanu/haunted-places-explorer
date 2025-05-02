import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium import plugins
from streamlit_folium import folium_static
from typing import Dict, List, Any
import numpy as np
import matplotlib.pyplot as plt
import re
import logging
from simplified_memex import add_simplified_memex_tab
from data_storage import load_processed_data
from data_processor import DataProcessor
from memex_integration import add_memex_tab
from streamlit_d3_direct import add_d3_visualizations_tab

# Import new modules - handle gracefully if not available
try:
    from scripts.image_space_tab import add_image_space_tab
    image_space_available = True
except ImportError:
    image_space_available = False

try:
    from scripts.geoparser_tab import add_geoparser_tab
    geoparser_available = True
except ImportError:
    geoparser_available = False

try:
    from scripts.search_tab import add_search_tab
    search_available = True
except ImportError:
    search_available = False

# Define the enhanced MEMEX tab function to integrate Image Space and GeoParser
def add_enhanced_memex_tab():
    """Add enhanced MEMEX tab with integration of Image Space and GeoParser functionalities"""
    st.header("MEMEX Tools Dashboard")
    
    # Add a general summary of the MEMEX tools
    st.markdown("""
    **MEMEX Tools** provide advanced analysis capabilities for haunted places investigation. 
    Below are specialized modules for image analysis and geographic data processing.
    """)
    
    # Create tabs for MEMEX components - removed Basic Tools
    memex_tabs = st.tabs(["Image Space", "GeoParser"])
    
    # Tab 1: Image Space
    with memex_tabs[0]:
        # Add summary description for Image Space
        st.markdown("""
        ### Image Space
        
        This module allows you to analyze images for paranormal evidence through:
        - **Image Upload**: Process individual images for spectral analysis
        - **Batch Processing**: Process multiple images at once for pattern recognition
        - **Image Explorer**: Explore uploaded images and their extracted features
        
        **Important Notes:**
        - Images must be processed through Image Upload or Batch Processing before they appear in Image Explorer
        - For large image collections (like 10,000+ images), use Batch Processing with smaller batches (100-500 images)
        - Processing all images at once may strain system resources
        
        *Note: Requires Docker with Tika running for full functionality*
        """)
        
        # Line separator
        st.markdown("---")
        
        if image_space_available:
            # Check if the add_image_space_tab function accepts a customize_batch parameter
            import inspect
            try:
                params = inspect.signature(add_image_space_tab).parameters
                if 'customize_batch' in params:
                    # If the function supports customization, pass the parameter
                    add_image_space_tab(customize_batch=True)
                else:
                    # Otherwise, call it normally and add our own batch processing suggestions
                    add_image_space_tab()
                    # Add additional UI guidance for batch processing
                    st.info("""
                    **💡 Processing Large Image Collections:**
                    
                    If you have thousands of images, consider:
                    1. Processing in smaller batches of 100-500 images
                    2. Starting with a representative sample of images
                    3. Monitoring system resources during processing
                    """)
            except Exception as e:
                # In case of any errors, fallback to standard call
                add_image_space_tab()
                st.warning(f"Encountered an issue customizing batch processing: {str(e)}")
        else:
            st.warning("Image Space module is not available. Please check if scripts/image_space_tab.py exists and dependencies are installed.")
            st.info("The Image Space feature would allow you to upload, analyze, and process images for paranormal evidence.")
    
    # Tab 2: GeoParser
    with memex_tabs[1]:
        # Add summary description for GeoParser
        st.markdown("""
        ### GeoParser
        
        This module helps analyze text for location data and geographic patterns:
        - **Text Analysis**: Extract location entities from haunted place descriptions
        - **Location Mapping**: Visualize extracted locations on interactive maps
        - **Historical Correlation**: Connect locations to historical events
        
        *Note: Requires the Mordecai geoparsing library for full functionality*
        """)
        
        # Line separator
        st.markdown("---")
        
        if geoparser_available:
            add_geoparser_tab()
        else:
            st.warning("GeoParser module is not available. Please check if scripts/geoparser_tab.py exists and dependencies are installed.")
            st.info("The GeoParser feature would allow you to analyze location data and extract geographic information from text.")

# Set page config
st.set_page_config(
    page_title="Haunted Places Analysis",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force the theme settings from config.toml (must come AFTER set_page_config)
st.markdown("""
<style>
    /* Force light theme with custom text color */
    :root {
        --background-color: white;
        --secondary-background-color: #e7e9ec;
        --text-color: #717198;
    }
    
    /* Make ALL tab labels white throughout the application */
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2c2c2c;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* Make expander headers white - multiple selectors for better coverage */
    button[kind="expandable"] div[data-testid="StyledFullScreenFrame"] > div {
        color: white !important;
    }
    .streamlit-expanderHeader {
        color: white !important;
        font-weight: bold !important;
    }
    [data-testid="stExpander"] details summary p {
        color: white !important;
    }
    [data-testid="stExpander"] summary {
        color: white !important;
    }
    [data-testid="stExpander"] summary p {
        color: white !important;
    }
    
    /* Override native Streamlit theme selector */
    section[data-testid="stSidebarUserContent"] div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Ensure sidebar text is properly visible */
    [data-testid="stSidebar"] {
        background-color: #2c2c2c !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown strong,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white !important;
    }
    
    /* Remove the sidebar collapse button completely */
    button[kind="expanderIcon"] {
        display: none !important;
    }
    
    /* Ensure the sidebar remains at a fixed width */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }
    
    /* Add a subtle border on the right side of the sidebar */
    [data-testid="stSidebar"] > div {
        border-right: 1px solid #4a4a4a;
    }
</style>
""", unsafe_allow_html=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize data directories
DATA_DIR = "data"
OUTPUT_DIR = "output"
PROCESSED_DATA = False

# Adding custom CSS for a more modern look
st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
        color: white;
    }
    /* Tab styles already defined in the first CSS block */
    .stTabs [aria-selected="true"] {
        background-color: #5a5ae2;
    }
    h1, h2, h3 {
        color: white;
    }
    .stSidebar {
        background-color: #2c2c2c;
    }
    .stButton button {
        background-color: #5a5ae2;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #5250b4;
        transform: translateY(-2px);
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    }
    /* Card-like containers for content */
    .stExpander {
        background-color: #2c2c2c;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    /* Make dataframes more readable */
    .dataframe {
        background-color: #2c2c2c !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .dataframe th {
        background-color: #4a4a4a !important;
        color: white !important;
    }
    /* Navigation button styling */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div[data-testid="column"] div button {
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        background-color: #2c2c2c;
        color: white;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border: none;
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div[data-testid="column"] div button:hover {
        background-color: #4a4a4a;
        transform: translateX(5px);
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div[data-testid="column"] div button[data-active="true"] {
        background-color: #5a5ae2;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Load and process data if needed
@st.cache_data
def load_data():
    """Load and process data for analysis"""
    try:
        # Create data directories if they don't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Check if we have the processed data files
        required_files = [
            os.path.join(OUTPUT_DIR, "map_data.json"),
            os.path.join(OUTPUT_DIR, "time_analysis.json"),
            os.path.join(OUTPUT_DIR, "evidence_analysis.json"),
            os.path.join(OUTPUT_DIR, "location_analysis.json"),
            os.path.join(OUTPUT_DIR, "correlation_data.json"),
            os.path.join(OUTPUT_DIR, "air_pollution.json")
        ]
        
        all_files_exist = all(os.path.exists(f) for f in required_files)
        
        if not all_files_exist:
            with st.spinner("Processing data... This may take a moment."):
                try:
                    # Process the data
                    data_processor = DataProcessor(
                        os.path.join(DATA_DIR, "haunted_places_v2.tsv"),
                        OUTPUT_DIR
                    )
                    data_processor.process_all()
                    global PROCESSED_DATA
                    PROCESSED_DATA = True
                    st.success("Data processed successfully!")
                except Exception as e:
                    st.error(f"Error processing data: {e}")
                    logger.error(f"Error processing data: {e}")
                    return False
        
        # Load the processed data into the data storage for MEMEX tools
        load_processed_data(OUTPUT_DIR)
        
        return True
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return False

# Load map data
@st.cache_data
def load_map_data():
    """Load map data for D3 visualization"""
    try:
        with open(os.path.join(OUTPUT_DIR, "map_data.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading map data: {e}")
        return None

# Load time analysis data
@st.cache_data
def load_time_analysis():
    """Load time analysis data for D3 visualization"""
    try:
        with open(os.path.join(OUTPUT_DIR, "time_analysis.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading time analysis data: {e}")
        return None

# Load evidence analysis data
@st.cache_data
def load_evidence_analysis():
    """Load evidence analysis data for D3 visualization"""
    try:
        with open(os.path.join(OUTPUT_DIR, "evidence_analysis.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading evidence analysis data: {e}")
        return None

# Load location analysis data
@st.cache_data
def load_location_analysis():
    """Load location analysis data for D3 visualization"""
    try:
        with open(os.path.join(OUTPUT_DIR, "location_analysis.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading location analysis data: {e}")
        return None

# Load correlation data
@st.cache_data
def load_correlation_data():
    """Load correlation data for D3 visualization"""
    try:
        with open(os.path.join(OUTPUT_DIR, "correlation_data.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading correlation data: {e}")
        return None
    

# Load air pollution data
@st.cache_data
def load_air_pollution_data():
    """Load air pollution data for visualization"""
    try:
        with open(os.path.join(OUTPUT_DIR, "air_pollution.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading air pollution data: {e}")
        return None

# Process data and ensure files exist
data_loaded = load_data()

# Load data
data = {
    'map': load_map_data(),
    'time': load_time_analysis(),
    'location': load_location_analysis(),
    'evidence': load_evidence_analysis(),
    'correlation': load_correlation_data(),
    'air_pollution': load_air_pollution_data()
}

# Title and description (we'll put this in the main content area instead of sidebar)
st.title("👻 Haunted Places Analysis")
# Improved sidebar with modern navigation
with st.sidebar:
    st.markdown("<h1 style='color: #5E6592;'>DSCI 550 HW3 Assignment</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Modern-looking menu with buttons
    st.markdown("<h3 style='color: #5E6592;'>👻 Navigation</h3>", unsafe_allow_html=True)
    
    # Initialize session state for current page if it doesn't exist
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Create column layout for buttons
    menu_options = {
        "🏠 Home": "Home",
        "☁️ Air Pollution Analysis": "Air Pollution Analysis",
        "🗺️ Map View": "Map Visualization",
        "⏱️ Time Analysis": "Time Analysis",
        "🔍 Evidence Analysis": "Evidence Analysis",
        "📍 Location Analysis": "Location Analysis",
        "📊 Correlation Analysis": "Correlation Analysis",
        "📈 D3 Visualizations": "D3 Visualizations",
        "🔬 MEMEX Tools": "MEMEX Tools"
    }
    
    # Add Search Tools option
    if search_available:
        menu_options["🔎 Search Tools"] = "Search"
    
    # Create buttons for each menu option
    for emoji_label, page_name in menu_options.items():
        button_style = "primary" if st.session_state.current_page == page_name else "secondary"
        if st.button(emoji_label, key=f"nav_{page_name}", use_container_width=True, type=button_style):
            st.session_state.current_page = page_name
            # Force a rerun to update the page content
            st.rerun()
    

# Get current page from session state
page = st.session_state.current_page

# Main content based on selected page
if page == "Home":
    st.header("Welcome to the Haunted Places Explorer")
    st.markdown("""
    This dashboard provides various ways to explore and analyze haunted places data:
    
    - **Air Pollution Visualization**: Visualize key insights derived from air pollution feature set appended in homework 1
    - **Map Visualization**: View haunted locations on an interactive map
    - **Time Analysis**: Explore temporal patterns in haunted sightings
    - **Evidence Analysis**: Analyze types of evidence and apparitions
    - **Location Analysis**: Explore geographical patterns
    - **Correlation Analysis**: Discover relationships between different variables
    - **D3 Visualizations**: Explore interactive D3.js visualizations
    - **MEMEX Tools**: Use advanced image and location analysis tools
    - **Search Tools**: Search and discover haunted places using Solr and ElasticSearch
    
    Use the sidebar to navigate between different visualizations.
    """)

    # Add authors section
    st.markdown("---")
    st.markdown("""
    ### Authors:
    James Temme, Jason Ungheanu, Jesse Fulcher, Ryan Ho, and Tyler Wong
    """)

elif page == "Air Pollution Analysis":
    st.header("Air Pollution Analysis")
    
    # Add summary description for HW1 Visualization
    st.markdown("""
    This section visualizes insights derived from the features appended to the dataset in Homework 1:
    - **Air Quality Analysis**: Explore the relationship between air quality and haunted places
    - **Visual Evidence**: Analyze the distribution of visual evidence across air quality categories
    - **Pattern Discovery**: Identify patterns between air quality and paranormal activity
    """)
    
    # Line separator
    st.markdown("---")
    
    if 'air_pollution' in data and data['air_pollution']:
        # Create two columns for the visualizations
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Haunted Reports by Air Quality (CO PPB)")
            # Prepare data for overall distribution donut chart
            overall_labels = []
            overall_values = []
            overall_colors = []
            
            for category, category_data in data['air_pollution']['categories'].items():
                 overall_labels.append(category)
                 overall_values.append(category_data['total_percentage'])
            #     overall_colors.append(color_map[category])
            
            # Create overall distribution donut chart
            fig1 = go.Figure(data=[go.Pie(
                labels=overall_labels,
                values=overall_values,
                hole=.4,
                # marker_colors=overall_colors,
                textinfo='label+percent',
                textposition='outside'
            )])
            
            # Update layout for dark theme
            fig1.update_layout(
                title={
                    'text': "Overall Air Quality Distribution",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    #'font': {'size': 16, 'color': '#FFFFFF'}
                },
                height=400,
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Visual Evidence Breakdown by Air Quality (CO PPB)")
            # Prepare data for breakdown visualization
            evidence_mapping = {
                'TRUE': 'Visual Evidence',
                'FALSE': 'No Visual Evidence'
            }
            
            # Create figure for evidence breakdown
            fig2 = go.Figure()
            
            # Calculate y-positions for each category's pie chart
            x_positions = [0.25, 0.5, 0.75]  # Left, middle, right positions
            
            for i, (category, category_data) in enumerate(data['air_pollution']['categories'].items()):
                # Get evidence breakdown
                evidence_labels = []
                evidence_values = []
                evidence_colors = []
                
                for evidence_type, evidence_data in category_data['breakdown'].items():
                    friendly_name = evidence_mapping[evidence_type]
                    evidence_labels.append(friendly_name)
                    evidence_values.append(evidence_data['percentage'])
                    #evidence_colors.append(color_map[friendly_name])
                
                # Add pie chart for this category
                fig2.add_trace(go.Pie(
                    labels=evidence_labels,
                    values=evidence_values,
                    name=category,
                    #marker_colors=evidence_colors,
                    domain=dict(x=[x_positions[i]-0.15, x_positions[i]+0.15], y=[0.2, 0.8]),
                    textinfo='percent',
                    textposition='inside',
                    showlegend=True,
                    title=f"{category}<br>({category_data['total_percentage']:.1f}% of total)",
                    titleposition="top right",
                    #titlefont=dict(size=12, color='#FFFFFF')
                ))
            
            # Update layout for dark theme
            fig2.update_layout(
                title={
                    'text': "Visual Evidence Breakdown by Air Quality",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    #'font': {'size': 16, 'color': '#FFFFFF'}
                },
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5,
                    #font=dict(color='#FFFFFF')
                ),
                #plot_bgcolor='rgba(0,0,0,0)',
                #paper_bgcolor='rgba(0,0,0,0)',
                #font=dict(color='#FFFFFF'),
                height=400,
                margin=dict(t=20, b=60, l=10, r=10)  # Adjust margins to account for legend
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # Add explanation with custom styling
        st.markdown("""
        <div>
        <h3>Insights:</h3>
        <ul>
            <li>Carbon monoxide can typically cause hallucinations that are oftentimes attributed as the cause of "hauntings". Areas with poor CO air quality had higher percentages of reports with no visual evidence. </li>
            <li>90.91% of reports in areas with good air quality as defined by concentration in parts-per-billion (ppb) of carbon monoxide (CO) had visual evidence.</li>
            <li>The number of reports with no visual evidence increased as the concentration of CO increased(and air quality as a measure of this concentration decreased). With each level of decreased air quality, the portion of reports with no visual evidence increased significantly. </li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Add data note with custom styling
        st.markdown(
            f"""
            <div style='background-color: rgba(49, 51, 63, 0.7); padding: 20px; border-radius: 5px; margin: 10px 0;'>
                <p style='color: #FFFFFF; margin: 0;'>
                    ℹ️ Analysis based on {data['air_pollution']['metadata']['total_rows_analyzed']} haunted locations with recorded air quality data.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("No air pollution data available")

elif page == "Map Visualization":
    st.header("Haunted Places Map")
    
    # Add summary description for Map Visualization
    st.markdown("""
    This visualization displays the geographic distribution of haunted places across the United States:
    - **Interactive Map**: Explore locations with reported paranormal activity
    - **Clustered Markers**: Click on clusters to see detailed information about haunted sites
    - **Data Table**: View and download the complete dataset below the map
    """)
    
    # Line separator
    st.markdown("---")
    
    if 'map' in data and data['map'] and 'map_data' in data['map']:
        # Create a map centered on the US
        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='CartoDB dark_matter')
        
        # Add marker clustering for better performance
        marker_cluster = plugins.MarkerCluster(
            name="Haunted Places",
            overlay=True,
            control=False,
            icon_create_function=None
        )
        
        # Limit the number of markers for better performance
        locations = data['map']['map_data']
        max_markers = 500  # Adjust this number based on performance needs
        
        # Information about the total dataset
        total_locations = len(locations)
        filtered_locations = len([loc for loc in locations if loc['latitude'] != 0 and loc['longitude'] != 0])
        
        # Create a sampling notice if we're limiting markers
        if filtered_locations > max_markers:
            st.markdown(
                f"""
                <div style='background-color: rgba(49, 51, 63, 0.7); padding: 20px; border-radius: 5px; margin: 10px 0;'>
                    <p style='color: #FFFFFF; margin: 0;'>
                        For performance reasons, showing a random sample of {max_markers} locations out of {filtered_locations} valid locations.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Random sample for better distribution
            import random
            valid_locations = [loc for loc in locations if loc['latitude'] != 0 and loc['longitude'] != 0]
            locations_to_display = random.sample(valid_locations, max_markers)
        else:
            locations_to_display = [loc for loc in locations if loc['latitude'] != 0 and loc['longitude'] != 0]
        
        # Add markers to the cluster
        for location in locations_to_display:
            # Simplified popup with less text for better performance
            popup_text = f"""
            <b>{location['location']}</b><br>
            {location['state']}
            """
            folium.Marker(
                [location['latitude'], location['longitude']],
                popup=popup_text,
                tooltip=location['location']
            ).add_to(marker_cluster)
        
        # Add the marker cluster to the map
        marker_cluster.add_to(m)
        
        # Add layer control to toggle marker cluster
        folium.LayerControl().add_to(m)
        
        # Display the map
        folium_static(m)
        
        # Display additional stats below the map
        st.markdown(f"**Total Locations in Dataset:** {total_locations}")
        st.markdown(f"**Locations with Valid Coordinates:** {filtered_locations}")
        
        # Add a button to show full data table with improved display
        if st.button("Show Data Table"):
            # Create a copy of the data to avoid modifying the original
            locations_df = pd.DataFrame(locations)
            
            # Select only the most relevant columns for display
            display_columns = ['location', 'state', 'country', 'latitude', 'longitude']
            
            # Add description if it exists and isn't mostly empty
            if 'description' in locations_df.columns and locations_df['description'].notna().sum() > len(locations_df) * 0.1:
                # Truncate description to make it more readable
                locations_df['description'] = locations_df['description'].apply(
                    lambda x: str(x)[:100] + '...' if isinstance(x, str) and len(str(x)) > 100 else x
                )
                display_columns.append('description')
            
            # Add date if it exists and isn't mostly empty/NaN
            if 'date' in locations_df.columns and locations_df['date'].notna().sum() > len(locations_df) * 0.1:
                display_columns.append('date')

            if 'evidence' in locations_df.columns:
                display_columns.append('evidence')
                
                def format_evidence(evidence_str):
                    if evidence_str == "Unknown" or pd.isna(evidence_str):
                        return "Unknown"
                    return evidence_str
                
                # Apply formatting if not in an environment where it would cause issues
                try:
                    locations_df['evidence_formatted'] = locations_df['evidence'].apply(format_evidence)
                    locations_df['evidence'] = locations_df['evidence_formatted']
                    locations_df = locations_df.drop(columns=['evidence_formatted'])
                except Exception as e:
                    logger.warning(f"Could not format evidence column: {e}")
            
            # Add apparition_type if it exists
            if 'apparition_type' in locations_df.columns and locations_df['apparition_type'].notna().sum() > len(locations_df) * 0.1:
                display_columns.append('apparition_type')
            
            # Filter the DataFrame to only include the selected columns if they exist
            display_df = locations_df[[col for col in display_columns if col in locations_df.columns]].copy()
            
            # Replace NaN values with more user-friendly text
            display_df = display_df.fillna({
                'date': 'Date unknown',
                'evidence': 'No evidence recorded',
                'description': 'No description available',
                'apparition_type': 'Type unknown'
            })
            
            # Create nicer column headers for display
            column_map = {
                'location': 'Location',
                'state': 'State',
                'country': 'Country',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
                'description': 'Description',
                'date': 'Date',
                'evidence': 'Evidence',
                'apparition_type': 'Apparition Type'
            }
            display_df = display_df.rename(columns=column_map)
            
            # Display the data table with pagination for better performance
            st.dataframe(display_df)
            
            # Add a download button for the full dataset
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="haunted_places_data.csv",
                mime="text/csv",
            )
    else:
        st.warning("No map data available")

elif page == "Time Analysis":
    st.header("Temporal Analysis")
    
    # Add summary description for Time Analysis
    st.markdown("""
    This analysis explores the temporal patterns of haunted place reports:
    - **Yearly Trends**: Visualize how haunting reports have changed over time
    - **Time of Day**: Discover when paranormal activity is most frequently reported
    - **Daylight Analysis**: Examine correlations between daylight hours and reported hauntings by state
    """)
    
    # Line separator
    st.markdown("---")
    
    if 'time' in data and data['time']:
        col1, col2 = st.columns(2)
        
        with col1:
            # Year-based analysis
            if 'year_counts' in data['time'] and data['time']['year_counts']:
                st.subheader("Haunted Sightings by Year")
                df_years = pd.DataFrame(data['time']['year_counts'])
                if not df_years.empty and 'year' in df_years.columns and 'count' in df_years.columns:
                    # Filter out future years (> 2023)
                    current_year = 2023  # Set a reasonable cutoff year
                    df_years = df_years[df_years['year'] <= current_year]
                    
                    fig = px.line(df_years, x='year', y='count', 
                                title='Number of Haunted Sightings Over Time')
                    
                    # Set default x-axis range from 1900 to current year, but allow zooming
                    fig.update_layout(
                        xaxis=dict(
                            range=[1900, current_year],
                            autorange=False
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add a note about panning to see older data
                    st.info("💡 **Tips:** Use the 'Pan' tool in the chart toolbar to drag and see historical data before 1900. Double-click anywhere on the chart to reset the view.")
                else:
                    st.info("No year data available")
            else:
                st.info("No year data available")
        
        with col2:
            # Time of day analysis
            if 'time_of_day_counts' in data['time'] and data['time']['time_of_day_counts']:
                st.subheader("Sightings by Time of Day")
                
                # Fix: Check if time_of_day_counts is a dictionary and convert properly
                try:
                    if isinstance(data['time']['time_of_day_counts'], dict):
                        # Create explicit DataFrame with named columns from dictionary
                        df_times = pd.DataFrame({
                            'time_of_day': list(data['time']['time_of_day_counts'].keys()),
                            'count': list(data['time']['time_of_day_counts'].values())
                        })
                    else:
                        # If it's already a list of dictionaries
                        df_times = pd.DataFrame(data['time']['time_of_day_counts'])
                    
                    # Now check if we have the needed columns and proceed with visualization
                    if not df_times.empty and 'time_of_day' in df_times.columns and 'count' in df_times.columns:
                        fig = px.pie(df_times, values='count', names='time_of_day',
                                    title='Distribution of Sightings by Time of Day')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No time of day data available")
                except Exception as e:
                    st.error(f"Error displaying time of day data: {str(e)}")
                    st.info("Time of day data format may need adjustment")
            else:
                st.info("No time of day data available")
        
        # Daylight hours analysis
        if 'daylight_by_state' in data['time'] and data['time']['daylight_by_state']:
            st.subheader("Average Daylight Hours by State")
            df_daylight = pd.DataFrame(data['time']['daylight_by_state'])
            if not df_daylight.empty and 'state' in df_daylight.columns and 'average_daylight_hours' in df_daylight.columns:
                # Filter out any NaN values to prevent visualization issues
                df_daylight = df_daylight.dropna(subset=['average_daylight_hours'])
                
                # Sort by daylight hours for better visualization
                df_daylight = df_daylight.sort_values('average_daylight_hours', ascending=False)
                
                # Add a checkbox to toggle between showing all states or just the top ones
                show_all_states = st.checkbox("Show all states", value=True)
                
                if show_all_states:
                    # Show all states
                    fig = px.bar(df_daylight, x='state', y='average_daylight_hours',
                               title='Average Daylight Hours by State (All States)')
                    # Adjust layout for better readability with many states
                    fig.update_layout(
                        xaxis={'categoryorder':'total descending'},
                        height=600  # Make the chart taller to accommodate all states
                    )
                else:
                    # Show only top 20 states
                    fig = px.bar(df_daylight.head(20), x='state', y='average_daylight_hours',
                               title='Average Daylight Hours by State (Top 20)')
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daylight hours data available")
        else:
            st.info("No daylight hours data available")
    else:
        st.warning("No time analysis data available")

    #insights section
    st.markdown("""
    <div style='background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 5px; margin: 10px 0;'>
    <h3 style='color: #FFFFFF;'>Insights:</h3>
    <ul style='color: #FFFFFF;'>
        <li>We see spikes in haunted places reports in 1990 and 2008. Possible explanations for these spikes is that the increased volume of reports could have been due in part to the rise of the internet and social media as well as increasing popularity of paranormal content in entertainment.</li>
        <li>2008 saw widespread adoption of digital and social media platforms such as Reddit and Youtube which may have helped sensationalize paranormal content and helped facilitate the spread of paranormal reports.</li>
        <li>In 1990, there was a resurgence in paranormal and ghost related content in popular culture, with the release of "Ghost" and with shows like "Unsolved Mysteries" and "The X-Files" which may have helped popularize the idea of haunted places.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

elif page == "Evidence Analysis":
    st.header("Evidence Analysis")
    
    # Add summary description for Evidence Analysis
    st.markdown("""
    This section examines the types of paranormal evidence reported across haunted locations:
    - **Evidence Types**: Compare frequencies of different evidence categories (visual, auditory, etc.)
    - **Apparition Types**: Explore the distribution of reported apparition categories
    - **Understanding Evidence**: Learn about common forms of paranormal evidence
    """)
    
    # Line separator
    st.markdown("---")
    
    if 'evidence' in data and data['evidence']:
        col1, col2 = st.columns(2)
        
        with col1:
            # Evidence type distribution
            if 'evidence_counts' in data['evidence'] and data['evidence']['evidence_counts']:
                st.subheader("Types of Evidence")
                evidence_data = data['evidence']['evidence_counts']
                df_evidence = pd.DataFrame({
                    'Type': list(evidence_data.keys()),
                    'Count': list(evidence_data.values())
                })
                if not df_evidence.empty:
                    # Sort by count
                    df_evidence = df_evidence.sort_values('Count', ascending=False)
                    fig = px.bar(df_evidence, x='Type', y='Count',
                                title='Distribution of Evidence Types',
                                color='Type')
                    fig.update_layout(xaxis_title="Evidence Type", 
                                     yaxis_title="Number of Occurrences")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No evidence type data available")
            else:
                st.info("No evidence type data available")
        
        with col2:
            # Apparition type distribution
            if 'apparition_counts' in data['evidence'] and data['evidence']['apparition_counts']:
                st.subheader("Types of Apparitions")
                df_apparitions = pd.DataFrame(data['evidence']['apparition_counts'])
                if not df_apparitions.empty and 'apparition_type' in df_apparitions.columns and 'count' in df_apparitions.columns:
                    # Sort by count
                    df_apparitions = df_apparitions.sort_values('count', ascending=False)
                    fig = px.pie(df_apparitions, values='count', names='apparition_type',
                                title='Distribution of Apparition Types',
                                color_discrete_sequence=px.colors.sequential.Plasma_r)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No apparition type data available")
            else:
                st.info("No apparition type data available")
                
        # Add description of common evidence types
        st.subheader("Understanding Evidence Types")
        st.markdown("""
        Evidence of paranormal activity comes in various forms:
        
        - **Visual**: Apparitions, shadow figures, mists, or unexplained movements
        - **Auditory**: Unexplained sounds, voices, footsteps, or music
        - **Temperature**: Sudden cold spots or temperature fluctuations
        - **Touch**: Physical sensations of being touched when no one is present
        - **EMF**: Electromagnetic field fluctuations detected by specialized equipment
        - **Movement**: Objects moving without explanation, doors opening/closing
        """)
    else:
        st.warning("No evidence analysis data available")

elif page == "Location Analysis":
    st.header("Location Analysis")
    
    # Add summary description for Location Analysis
    st.markdown("""
    This analysis investigates geographical patterns of haunted places:
    - **State Distribution**: Identify states with the highest concentration of reported hauntings
    - **Regional Patterns**: Compare haunting frequencies across different U.S. regions
    - **Apparition Geography**: Discover which types of apparitions are most common in different states
    """)
    
    # Line separator
    st.markdown("---")
    
    if 'location' in data and data['location']:
        col1, col2 = st.columns(2)
        
        with col1:
            # State distribution
            if 'state_counts' in data['location'] and data['location']['state_counts']:
                st.subheader("Haunted Sightings by State")
                df_states = pd.DataFrame(data['location']['state_counts'])
                if not df_states.empty and 'state' in df_states.columns and 'count' in df_states.columns:
                    fig = px.bar(df_states.head(20), x='state', y='count',
                                title='Top 20 States with Most Haunted Sightings',
                                color='count', color_continuous_scale='Viridis')
                    fig.update_layout(xaxis_title="State", 
                                     yaxis_title="Number of Haunted Places")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No state data available")
            else:
                st.info("No state data available")
        
        with col2:
            # Region distribution instead of country (since it's all USA)
            if 'region_counts' in data['location'] and data['location']['region_counts']:
                st.subheader("Haunted Sightings by Region")
                df_regions = pd.DataFrame(data['location']['region_counts'])
                if not df_regions.empty and 'region' in df_regions.columns and 'count' in df_regions.columns:
                    fig = px.pie(df_regions, values='count', names='region',
                                title='Distribution of Haunted Places by Region',
                                color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No region data available")
            else:
                st.info("No region data available")
        
        # Add top apparition types by state
        if 'top_apparition_by_state' in data['location'] and data['location']['top_apparition_by_state']:
            st.subheader("Top Apparition Types by State")
            df_top = pd.DataFrame(data['location']['top_apparition_by_state'])
            if not df_top.empty and 'state' in df_top.columns and 'apparition_type' in df_top.columns and 'count' in df_top.columns:
                fig = px.bar(df_top, x='state', y='count', color='apparition_type',
                           title='Most Common Apparition Type by State (Top 15)',
                           color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_layout(xaxis_title="State", 
                                 yaxis_title="Count",
                                 legend_title="Apparition Type")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No top apparition by state data available")
        else:
            st.info("No top apparition by state data available")
    else:
        st.warning("No location analysis data available")

elif page == "Correlation Analysis":
    st.header("Correlation Analysis")
    
    # Add summary description for Correlation Analysis
    st.markdown("""
    This visualization reveals relationships between different variables in haunted places data:
    - **Variable Correlations**: Examine how different factors correlate with each other
    - **Heatmap Visualization**: Stronger colors indicate stronger relationships
    - **Insight Discovery**: Identify patterns that may suggest causal relationships
    """)
    
    # Line separator
    st.markdown("---")
    
    if 'correlation' in data and data['correlation']:
        if 'correlation_matrix' in data['correlation'] and data['correlation']['correlation_matrix']:
            st.subheader("Variable Correlations")
            # Convert correlation data to matrix format
            corr_data = data['correlation']['correlation_matrix']
            if corr_data:
                variables = sorted(list(set([d['x'] for d in corr_data])))
                matrix = np.zeros((len(variables), len(variables)))
                
                for d in corr_data:
                    i = variables.index(d['x'])
                    j = variables.index(d['y'])
                    matrix[i, j] = d['value']
                
                # Create heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=matrix,
                    x=variables,
                    y=variables,
                    colorscale='RdBu',
                    zmin=-1,
                    zmax=1
                ))
                
                fig.update_layout(
                    title='Correlation Matrix of Variables',
                    xaxis_title="Variables",
                    yaxis_title="Variables",
                    height=800
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No correlation data available")
        else:
            st.info("No correlation data available")
    else:
        st.warning("No correlation data available")

    #insights section
    st.markdown("""
    <div style='background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 5px; margin: 10px 0;'>
    <h3 style='color: #FFFFFF;'>Insights:</h3>
    <ul style='color: #FFFFFF;'>
        <li>The strongest negative correlation (-0.340) is between apparition_type_Ghost and apparition_type_Ghost Light, suggesting these types tend to be mutually exclusive.</li>
        <li>Looking at the larger correlation matrix, there are some weak correlations between latitude and certain states, which is expected due to their geographic positions. The state correlations show mostly negative values with each other (visible in the blue squares), which is logical since a haunting can't occur in multiple states simultaneously.</li>
        <li>Full-Bodied Apparitions show very weak negative correlations with all other types, suggesting they occur relatively independently. Shadow Figures and Partial Apparitions have the weakest correlations with other types, indicating they might occur randomly across locations.</li>
        <li>The generally weak correlations between different apparition types suggest that haunted places don't typically experience multiple types of apparitions simultaneously. The strongest relationships are between traditional ghost sightings and other manifestation types, possibly indicating that these categories might overlap in witness descriptions. The geographic correlations (visible in the larger matrix) suggest some regional patterns in haunting reports, though these correlations are relatively weak. </li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# New D3 Visualizations page
elif page == "D3 Visualizations":
    # We don't need a duplicate header here since the page title will show
    
    # Add summary description for D3 Visualizations
    st.markdown("""
    This section features interactive D3.js visualizations for advanced data exploration:
    - **Interactive Maps**: Explore geographic patterns with dynamic filtering
    - **Time Series Analysis**: Investigate temporal trends with adjustable parameters
    - **Advanced Correlations**: Discover relationships with interactive data points
    - **Network Analysis**: Visualize connections between locations and evidence types
    
    *Note: These visualizations utilize D3's powerful capabilities for more advanced interactivity and customization*
    """)
    
    # Line separator
    st.markdown("---")
    
    # Try to import and use the D3 visualization code
    try:
        add_d3_visualizations_tab()
    except Exception as e:
        st.error(f"D3 visualization module error: {str(e)}")
        
        # Provide instructions
        st.info("""
        To set up D3 visualizations:
        
        1. Create a file named `streamlit_d3_direct.py` with the code provided
        2. Create a directory named `visualizations`
        3. Create HTML files for each D3 visualization in the `visualizations` directory
        """)

# MEMEX Tools enhanced page
elif page == "MEMEX Tools":
    add_enhanced_memex_tab()

# Search page
elif page == "Search" and search_available:
    st.header("Search Tools")
    
    # Add summary description for Search Tools
    st.markdown("""
    ### Advanced Search Capabilities

    This module provides powerful search tools for exploring the haunted places dataset:
    
    - **Full-Text Search**: Search across all text fields in the haunted places data
    - **Solr Integration**: Utilize Apache Solr's high-performance search capabilities
    - **ElasticSearch**: Leverage complex query capabilities and relevance scoring
    - **Faceted Navigation**: Filter results by state, evidence type, or time period
    - **Geographic Search**: Find haunted places within specific regions or distances
    
    *Note: Full functionality requires Docker with Solr and/or ElasticSearch containers running*
    """)
    
    # Line separator
    st.markdown("---")
    
    add_search_tab()

# If a page is selected but the module is not available, show an error
elif page == "Search":
    st.error(f"The Search module is not available. Please check the console for error messages.")
    st.info("To enable Search functionality, make sure scripts/search_tab.py exists and required dependencies are installed.")
