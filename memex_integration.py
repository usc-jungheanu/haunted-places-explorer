import streamlit as st
import requests
import json
import os
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# MEMEX API endpoints
IMAGESPACE_API = "http://localhost:5000/api"
GEOPARSER_API = "http://localhost:5001/api"

class MEMEXIntegration:
    def __init__(self):
        """Initialize MEMEX integration with configuration"""
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load MEMEX configuration"""
        try:
            with open('memex_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("MEMEX configuration not found. Please run setup_memex.py first.")
            return {}
            
    def search_similar_images(self, image_path: str) -> Optional[List[Dict[str, Any]]]:
        """Search for similar images using ImageSpace"""
        if not self.config:
            return None
            
        try:
            # Upload image to ImageSpace
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.config['imagespace']['url']}/search",
                    files=files
                )
                
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error searching similar images: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error searching similar images: {e}")
            return None
            
    def analyze_locations(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Analyze locations in text using GeoParser"""
        if not self.config:
            return None
            
        try:
            response = requests.post(
                f"{self.config['geoparser']['url']}/analyze",
                json={'text': text}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error analyzing locations: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error analyzing locations: {e}")
            return None
            
    def visualize_similar_images(self, image_path: str):
        """Visualize similar images in Streamlit"""
        st.header("Similar Images Analysis")
        
        similar_images = self.search_similar_images(image_path)
        if similar_images:
            # Create a grid of similar images
            cols = st.columns(3)
            for i, img in enumerate(similar_images[:6]):  # Show top 6 similar images
                with cols[i % 3]:
                    st.image(img['url'], caption=f"Similarity: {img['similarity']:.2f}")
                    
            # Show similarity distribution
            df = pd.DataFrame(similar_images)
            fig = px.histogram(df, x='similarity', title='Similarity Distribution')
            st.plotly_chart(fig)
        else:
            st.warning("No similar images found")
            
    def visualize_location_analysis(self, text: str):
        """Visualize location analysis in Streamlit"""
        st.header("Location Analysis")
        
        locations = self.analyze_locations(text)
        if locations:
            # Create a map of locations
            df = pd.DataFrame(locations)
            fig = px.scatter_geo(
                df,
                lat='latitude',
                lon='longitude',
                hover_name='location',
                title='Geographic Distribution of Locations'
            )
            st.plotly_chart(fig)
            
            # Show location frequency
            fig = px.bar(
                df.groupby('location').size().reset_index(name='count'),
                x='location',
                y='count',
                title='Location Frequency'
            )
            st.plotly_chart(fig)
        else:
            st.warning("No locations found in text")

def add_memex_tab():
    """Add original simplified MEMEX functionalities"""
    st.subheader("Basic MEMEX Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Image Analysis")
        
        # Simplified image analysis tool
        st.write("Upload an image to analyze haunted places features:")
        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            # Simulated image analysis results
            st.write("### Analysis Results")
            st.write("- **Spectral Analysis**: Medium anomalies detected")
            st.write("- **Shadow Detection**: 2 potential shadow figures")
            st.write("- **Light Orb Detection**: 3 potential orbs identified")
            st.write("- **Color Temperature**: Significant cold spots detected")
            
            # Add a simulated similarity score
            st.metric("Haunting Probability", "76%")
    
    with col2:
        st.markdown("### Location Analysis")
        
        # Simple location input
        location_input = st.text_input("Enter a location to analyze")
        
        if location_input:
            # Create a map centered on the US
            m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
            
            # Add a sample marker
            folium.Marker(
                [39.8283, -98.5795],
                popup=f"Analyzing: {location_input}",
                tooltip=location_input
            ).add_to(m)
            
            # Display the map
            folium_static(m)
            
            # Display simulated analysis
            st.write("### Location Analysis Results")
            st.write(f"- **Historical Analysis**: 12 reported hauntings near {location_input}")
            st.write("- **Temporal Patterns**: Most activity reported between 2am-4am")
            st.write("- **Site Features**: Located near historical buildings")
            
            # Add a simulated correlation score
            st.metric("Location Correlation", "83%")
    
    # Additional MEMEX tools section
    st.markdown("### Additional MEMEX Tools")
    st.info("""
    The original MEMEX toolkit includes these basic analysis features. 
    For more advanced functionality, use the Image Space and GeoParser tabs above.
    """)

def display_imagespace_results(results: Dict[str, Any]):
    """Display ImageSpace analysis results"""
    st.subheader("Analysis Results")
    
    if "objects" in results:
        st.write("Detected Objects:")
        for obj in results["objects"]:
            st.write(f"- {obj['label']} (confidence: {obj['confidence']:.2f})")
    
    if "colors" in results:
        st.write("Dominant Colors:")
        for color in results["colors"]:
            st.write(f"- {color['name']} (RGB: {color['rgb']})")
    
    if "text" in results:
        st.write("Detected Text:")
        st.write(results["text"])

def display_geoparser_results(results: Dict[str, Any]):
    """Display GeoParser analysis results"""
    st.subheader("Analysis Results")
    
    if "location_info" in results:
        st.write("Location Information:")
        for key, value in results["location_info"].items():
            st.write(f"- {key}: {value}")
    
    if "nearby_places" in results:
        st.write("Nearby Places:")
        for place in results["nearby_places"]:
            st.write(f"- {place['name']} ({place['type']})")
    
    if "historical_data" in results:
        st.write("Historical Data:")
        for event in results["historical_data"]:
            st.write(f"- {event['year']}: {event['description']}")

# Example usage in Streamlit app
if __name__ == "__main__":
    st.title("MEMEX Integration Demo")
    add_memex_tab() 