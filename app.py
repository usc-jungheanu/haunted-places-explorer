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
from streamlit_d3_integration import add_d3_visualizations_tab

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
    section[data-testid="stSidebar"] > div > div:first-child {
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
    # Create data directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Check if we have the processed data files
    required_files = [
        os.path.join(OUTPUT_DIR, "map_data.json"),
        os.path.join(OUTPUT_DIR, "time_analysis.json"),
        os.path.join(OUTPUT_DIR, "evidence_analysis.json"),
        os.path.join(OUTPUT_DIR, "location_analysis.json"),
        os.path.join(OUTPUT_DIR, "correlation_data.json")
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

# Load map data
@st.cache_data
def load_map_data():
    try:
        with open(os.path.join(OUTPUT_DIR, "map_data.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading map data: {e}")
        return None

# Load time analysis data
@st.cache_data
def load_time_analysis():
    try:
        with open(os.path.join(OUTPUT_DIR, "time_analysis.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading time analysis data: {e}")
        return None

# Load evidence analysis data
@st.cache_data
def load_evidence_analysis():
    try:
        with open(os.path.join(OUTPUT_DIR, "evidence_analysis.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading evidence analysis data: {e}")
        return None

# Load location analysis data
@st.cache_data
def load_location_analysis():
    try:
        with open(os.path.join(OUTPUT_DIR, "location_analysis.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading location analysis data: {e}")
        return None

# Load correlation data
@st.cache_data
def load_correlation_data():
    try:
        with open(os.path.join(OUTPUT_DIR, "correlation_data.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading correlation data: {e}")
        return None

# Process data and ensure files exist
data_loaded = load_data()

# Load data
data = {
    'map': load_map_data(),
    'time': load_time_analysis(),
    'location': load_location_analysis(),
    'evidence': load_evidence_analysis(),
    'correlation': load_correlation_data()
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
        "🗺️ Map View": "Map Visualization",
        "⏱️ Time Analysis": "Time Analysis",
        "🔍 Evidence Analysis": "Evidence Analysis",
        "📍 Location Analysis": "Location Analysis",
        "📊 Correlation Analysis": "Correlation Analysis",
        "📈 D3 Visualizations": "D3 Visualizations",
        "🔬 MEMEX Tools": "MEMEX Tools"
    }
    
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
    
    - **Map Visualization**: View haunted locations on an interactive map
    - **Time Analysis**: Explore temporal patterns in haunted sightings
    - **Evidence Analysis**: Analyze types of evidence and apparitions
    - **Location Analysis**: Explore geographical patterns
    - **Correlation Analysis**: Discover relationships between different variables
    - **D3 Visualizations**: Explore interactive D3.js visualizations
    - **MEMEX Tools**: Use advanced image and location analysis tools
    
    Use the sidebar to navigate between different visualizations.
    """)

elif page == "Map Visualization":
    st.header("Haunted Places Map")
    
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
            st.info(f"⚡ For performance reasons, showing a random sample of {max_markers} locations out of {filtered_locations} valid locations.")
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
    
    if 'map' in data and data['map'] and 'map_data' in data['map']:
        # Create a map centered on the US
        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        
        # Add markers for each haunted location
        for location in data['map']['map_data']:
            if location['latitude'] != 0 and location['longitude'] != 0:
                popup_text = f"""
                <b>{location['location']}</b><br>
                State: {location['state']}<br>
                Country: {location['country']}<br>
                Description: {location['description'][:100]}...
                """
                folium.Marker(
                    [location['latitude'], location['longitude']],
                    popup=popup_text,
                    tooltip=location['location']
                ).add_to(m)
        
        # Display the map
        folium_static(m)
    else:
        st.warning("No map data available")

elif page == "Time Analysis":
    st.header("Temporal Analysis")
    
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
                fig = px.bar(df_daylight.head(20), x='state', y='average_daylight_hours',
                            title='Average Daylight Hours by State (Top 20)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daylight hours data available")
        else:
            st.info("No daylight hours data available")
    else:
        st.warning("No time analysis data available")

elif page == "Evidence Analysis":
    st.header("Evidence Analysis")
    
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

# New D3 Visualizations page
elif page == "D3 Visualizations":
    # We don't need a duplicate header here since the page title will show
    # Try to import and use the D3 visualization code
    try:
        from streamlit_d3_integration import add_d3_visualizations_tab
        add_d3_visualizations_tab()
    except ImportError:
        st.error("D3 integration module not found. Please create streamlit_d3_integration.py first.")
        
        # Provide instructions
        st.info("""
        To set up D3 visualizations:
        
        1. Create a file named `streamlit_d3_integration.py` with the code provided
        2. Create a directory named `visualizations`
        3. Create HTML files for each D3 visualization in the `visualizations` directory
        """)

# MEMEX Tools page
elif page == "MEMEX Tools":
    st.header("MEMEX Tools")
    add_simplified_memex_tab()
