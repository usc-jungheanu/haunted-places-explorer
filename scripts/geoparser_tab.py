import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import folium_static
import logging
from pathlib import Path
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import location analyzer
try:
    from scripts.geoparser import LocationAnalyzer
    geoparser_available = True
except ImportError:
    geoparser_available = False
    logger.warning("GeoParser module not available. Location analysis features will be limited.")

def display_location_map(locations, title="Detected Locations"):
    """Display locations on a map"""
    if not locations:
        st.warning("No location data available to display on map")
        return
    
    # Create a map centered on the US
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    
    # Add markers for each location
    for loc in locations:
        if 'lat' in loc and 'lon' in loc and loc['lat'] != 0 and loc['lon'] != 0:
            popup_text = f"""
            <b>{loc['location']}</b><br>
            Type: {loc.get('type', 'Unknown')}<br>
            Confidence: {loc.get('confidence', 'N/A')}
            """
            folium.Marker(
                [loc['lat'], loc['lon']],
                popup=popup_text,
                tooltip=loc['location']
            ).add_to(m)
    
    # Display the map
    st.subheader(title)
    folium_static(m)

def display_location_stats(location_data):
    """Display statistics about the detected locations"""
    if not location_data:
        st.warning("No location statistics available")
        return
    
    st.subheader("Location Statistics")
    
    # Display total locations
    st.metric("Total Locations Detected", location_data.get('total_locations', 0))
    
    # Display location types
    if 'location_types' in location_data and location_data['location_types']:
        # Convert to DataFrame for easier display
        types_df = pd.DataFrame({
            'Type': list(location_data['location_types'].keys()),
            'Count': list(location_data['location_types'].values())
        }).sort_values('Count', ascending=False)
        
        # Display as a bar chart
        st.bar_chart(types_df.set_index('Type'))
    
    # Display locations table
    if 'locations' in location_data and location_data['locations']:
        st.subheader("Detected Locations")
        
        # Convert to DataFrame
        locations_df = pd.DataFrame(location_data['locations'])
        
        # Reorder and rename columns for better display
        display_columns = ['location', 'type', 'confidence']
        if all(col in locations_df.columns for col in display_columns):
            # Filter and rename
            display_df = locations_df[display_columns].copy()
            display_df.columns = ['Location', 'Type', 'Confidence']
            
            # Sort by confidence
            display_df = display_df.sort_values('Confidence', ascending=False)
            
            # Display
            st.dataframe(display_df)
        else:
            # Display raw data if columns don't match expected format
            st.dataframe(locations_df)

def add_geoparser_tab():
    """Add GeoParser tab to Streamlit"""
    st.header("GeoParser Analysis")
    
    # Check if GeoParser is available
    if not geoparser_available:
        st.error("GeoParser module not available. Please install required dependencies.")
        
        with st.expander("Installation Instructions"):
            st.markdown("""
            To enable full GeoParser functionality, please install the required dependencies:
            
            ```bash
            pip install mordecai
            ```
            
            Then restart the application.
            """)
        return
    
    # Initialize location analyzer
    analyzer = LocationAnalyzer()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Text Analysis", "File Analysis", "Historical Analysis"])
    
    with tab1:
        st.subheader("Analyze Text for Locations")
        
        # Text input
        text_input = st.text_area("Enter text to analyze", height=200)
        
        if st.button("Extract Locations") and text_input:
            with st.spinner("Analyzing text..."):
                locations = analyzer.process_locations(text_input)
                
                if locations:
                    st.success(f"Found {len(locations)} locations in the text")
                    
                    # Display locations
                    location_df = pd.DataFrame(locations)
                    st.dataframe(location_df)
                    
                    # Display on map (if coordinates available)
                    if any('lat' in loc and 'lon' in loc and loc['lat'] != 0 and loc['lon'] != 0 for loc in locations):
                        display_location_map(locations)
                    else:
                        st.info("No coordinates available for map display")
                else:
                    st.info("No locations detected in the text")
    
    with tab2:
        st.subheader("Analyze File for Locations")
        
        # File upload
        uploaded_file = st.file_uploader("Upload a TSV, CSV, or JSON file", type=['tsv', 'csv', 'json'])
        
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            file_extension = Path(uploaded_file.name).suffix
            temp_path = Path(f"temp_upload{file_extension}")
            
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            # Analyze the file
            if st.button("Analyze File"):
                with st.spinner("Analyzing file..."):
                    results = analyzer.analyze_data(temp_path)
                    
                    if results:
                        # Display statistics
                        display_location_stats(results)
                        
                        # Display on map
                        if 'locations' in results and results['locations']:
                            display_location_map(results['locations'])
                        
                        # Option to save results
                        if st.button("Save Results"):
                            output_dir = Path("output/location_analysis")
                            output_dir.mkdir(exist_ok=True, parents=True)
                            
                            output_file = output_dir / f"analysis_{uploaded_file.name}.json"
                            with open(output_file, 'w') as f:
                                json.dump(results, f, indent=2)
                            
                            st.success(f"Results saved to {output_file}")
                    else:
                        st.error("Error analyzing file")
    
    with tab3:
        st.subheader("Historical Data Analysis")
        
        # Check for historical analysis results
        historical_file = Path("output/location_analysis/historical_location_analysis.json")
        
        if historical_file.exists():
            with open(historical_file, 'r') as f:
                historical_data = json.load(f)
            
            # Display historical data stats
            st.metric("Total Files Analyzed", historical_data.get('total_files', 0))
            st.metric("Total Locations Detected", historical_data.get('total_locations', 0))
            
            # Display location types from historical data
            if 'location_types' in historical_data and historical_data['location_types']:
                st.subheader("Location Types in Historical Data")
                
                # Convert to DataFrame
                hist_types_df = pd.DataFrame({
                    'Type': list(historical_data['location_types'].keys()),
                    'Count': list(historical_data['location_types'].values())
                }).sort_values('Count', ascending=False)
                
                # Display as a bar chart
                st.bar_chart(hist_types_df.set_index('Type'))
            
            # Option to view details for each file
            if 'file_results' in historical_data and historical_data['file_results']:
                st.subheader("File-specific Results")
                
                file_names = [Path(result['file']).name for result in historical_data['file_results']]
                selected_file = st.selectbox("Select a file to view details", file_names)
                
                # Find the selected file results
                selected_result = next((r for r in historical_data['file_results'] 
                                      if Path(r['file']).name == selected_file), None)
                
                if selected_result and 'results' in selected_result:
                    # Display statistics for the selected file
                    display_location_stats(selected_result['results'])
        else:
            # Option to perform historical analysis
            if st.button("Analyze Historical Data"):
                with st.spinner("Analyzing historical data..."):
                    results = analyzer.analyze_historical_data()
                    
                    if results:
                        st.success("Historical data analysis complete")
                        st.rerun()  # Rerun to display the results
                    else:
                        st.error("Error analyzing historical data")
                        
                        # Provide more context
                        st.info("Make sure you have haunted places data files in the 'data' directory")

# For testing only
if __name__ == "__main__":
    st.set_page_config(page_title="GeoParser", layout="wide")
    add_geoparser_tab() 
