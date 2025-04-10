import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
import io
from PIL import Image
import json
import os
from typing import Dict, List, Any, Optional
import base64
from data_storage import data_store, search_places, get_places_by_state

def add_simplified_memex_tab():
    """Add simplified MEMEX tools tab that works without Docker"""
    
    st.header("MEMEX Tools (Simplified Version)")
    
    st.info("""
    This is a simplified version of the MEMEX tools that works directly in Streamlit Cloud
    without requiring Docker containers. It includes basic image analysis and geolocation
    capabilities to demonstrate the concepts.
    """)
    
    tab1, tab2 = st.tabs(["ImageSpace (Simplified)", "GeoParser (Simplified)"])
    
    with tab1:
        image_space_simplified()
    
    with tab2:
        geoparser_simplified()

def image_space_simplified():
    """Simplified version of ImageSpace using Streamlit's native image capabilities"""
    
    st.subheader("Image Analysis")
    st.write("Upload an image to analyze or enter a URL to an image.")
    
    # Option to upload an image or enter a URL
    option = st.radio("Select an option:", ["Upload Image", "Enter Image URL"])
    
    image = None
    
    if option == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
    else:
        url = st.text_input("Enter image URL:")
        if url:
            try:
                response = requests.get(url)
                image = Image.open(io.BytesIO(response.content))
            except Exception as e:
                st.error(f"Error loading image from URL: {e}")
    
    if image:
        # Display the image
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Image analysis
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                # Get image information
                width, height = image.size
                mode = image.mode
                format = image.format
                
                # Basic color analysis
                image_rgb = image.convert('RGB')
                pixels = list(image_rgb.getdata())
                r_avg = sum(pixel[0] for pixel in pixels) / len(pixels)
                g_avg = sum(pixel[1] for pixel in pixels) / len(pixels)
                b_avg = sum(pixel[2] for pixel in pixels) / len(pixels)
                
                # Display image info
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Image Information:**")
                    st.write(f"Dimensions: {width}x{height} pixels")
                    st.write(f"Mode: {mode}")
                    st.write(f"Format: {format}")
                
                with col2:
                    st.write("**Color Analysis:**")
                    st.write(f"Average RGB: ({r_avg:.1f}, {g_avg:.1f}, {b_avg:.1f})")
                    # Visual representation of dominant color
                    st.markdown(
                        f"""
                        <div style="width:100%;height:50px;background-color:rgb({int(r_avg)},{int(g_avg)},{int(b_avg)})"></div>
                        """,
                        unsafe_allow_html=True
                    )
                
                st.write("**Similar Haunted Places:**")
                st.write("Finding haunted places with similar characteristics...")
                
                # This is a mock similarity function - in a real app, this would use machine learning
                # Instead, we'll just return some haunted places as an example
                similar_places = data_store.get_documents("haunted_places", limit=3)
                if similar_places:
                    for place in similar_places:
                        with st.expander(f"{place.get('location', 'Unknown Location')}"):
                            st.write(f"**State:** {place.get('state', 'Unknown')}")
                            st.write(f"**Country:** {place.get('country', 'Unknown')}")
                            st.write(f"**Description:** {place.get('description', 'No description available')}")
                else:
                    st.write("No similar places found in the database.")

def geoparser_simplified():
    """Simplified version of GeoParser using Streamlit's map capabilities"""
    
    st.subheader("Location Analysis")
    st.write("Search for haunted places by location or explore the map.")
    
    # Search for locations
    search_query = st.text_input("Search for a location:")
    
    if search_query:
        results = search_places(search_query)
        
        if results:
            st.success(f"Found {len(results)} haunted places matching '{search_query}'")
            
            # Create a map with the results
            m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
            
            for place in results:
                if place.get('latitude') and place.get('longitude'):
                    popup_text = f"""
                    <b>{place.get('location', 'Unknown')}</b><br>
                    State: {place.get('state', 'Unknown')}<br>
                    Country: {place.get('country', 'Unknown')}<br>
                    Description: {place.get('description', 'No description')[:100]}...
                    """
                    folium.Marker(
                        [place.get('latitude'), place.get('longitude')],
                        popup=popup_text,
                        tooltip=place.get('location', 'Unknown')
                    ).add_to(m)
            
            # Display the map
            st.write("**Locations on map:**")
            folium_static(m)
            
            # Show results table
            st.write("**Detailed results:**")
            df = pd.DataFrame(results)
            if 'latitude' in df.columns and 'longitude' in df.columns:
                st.dataframe(df[['location', 'state', 'country', 'latitude', 'longitude']])
            else:
                st.dataframe(df[['location', 'state', 'country']])
        else:
            st.warning(f"No haunted places found matching '{search_query}'")
    
    # Display a state selector and show results
    st.write("**Or select a state to see haunted places:**")
    states = sorted(list(set([doc.get('state') for doc in data_store.get_documents('haunted_places') if doc.get('state')])))
    
    if states:
        selected_state = st.selectbox("Select a state:", states)
        
        if selected_state:
            state_places = get_places_by_state(selected_state)
            
            if state_places:
                st.success(f"Found {len(state_places)} haunted places in {selected_state}")
                
                # Create a map for the state
                m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
                
                for place in state_places:
                    if place.get('latitude') and place.get('longitude'):
                        popup_text = f"""
                        <b>{place.get('location', 'Unknown')}</b><br>
                        Description: {place.get('description', 'No description')[:100]}...
                        """
                        folium.Marker(
                            [place.get('latitude'), place.get('longitude')],
                            popup=popup_text,
                            tooltip=place.get('location', 'Unknown')
                        ).add_to(m)
                
                # Display the map
                st.write(f"**Haunted places in {selected_state}:**")
                folium_static(m)
    else:
        st.warning("No state data available.") 