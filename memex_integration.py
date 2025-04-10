import streamlit as st
import requests
import json
import os
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px

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
    """Add MEMEX tools tab to the Streamlit app"""
    st.header("MEMEX Tools Integration")
    
    # Create tabs for different MEMEX tools
    tab1, tab2 = st.tabs(["ImageSpace", "GeoParser"])
    
    with tab1:
        st.subheader("ImageSpace Analysis")
        st.markdown("""
        ImageSpace allows you to analyze and visualize images from haunted locations.
        Upload an image or enter an image URL to analyze it.
        """)
        
        # Image input options
        image_input = st.radio(
            "Choose input method:",
            ["Upload Image", "Image URL"]
        )
        
        if image_input == "Upload Image":
            uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                # Save the uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Send to ImageSpace API
                try:
                    with open(temp_path, "rb") as f:
                        files = {"file": f}
                        response = requests.post(f"{IMAGESPACE_API}/analyze", files=files)
                        if response.status_code == 200:
                            results = response.json()
                            display_imagespace_results(results)
                        else:
                            st.error("Error analyzing image")
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        else:
            image_url = st.text_input("Enter image URL")
            if image_url:
                try:
                    response = requests.post(f"{IMAGESPACE_API}/analyze", json={"url": image_url})
                    if response.status_code == 200:
                        results = response.json()
                        display_imagespace_results(results)
                    else:
                        st.error("Error analyzing image")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("GeoParser Analysis")
        st.markdown("""
        GeoParser allows you to analyze geographical data from haunted locations.
        Enter a location or coordinates to analyze.
        """)
        
        # Location input options
        location_input = st.radio(
            "Choose input method:",
            ["Location Name", "Coordinates"]
        )
        
        if location_input == "Location Name":
            location_name = st.text_input("Enter location name")
            if location_name:
                try:
                    response = requests.post(f"{GEOPARSER_API}/analyze", json={"location": location_name})
                    if response.status_code == 200:
                        results = response.json()
                        display_geoparser_results(results)
                    else:
                        st.error("Error analyzing location")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        else:
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0)
            with col2:
                longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0)
            
            if latitude and longitude:
                try:
                    response = requests.post(
                        f"{GEOPARSER_API}/analyze",
                        json={"coordinates": {"latitude": latitude, "longitude": longitude}}
                    )
                    if response.status_code == 200:
                        results = response.json()
                        display_geoparser_results(results)
                    else:
                        st.error("Error analyzing coordinates")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

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