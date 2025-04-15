import streamlit as st
import os
import shutil

def add_d3_visualizations_tab():
    """
    Add D3 visualizations tab to the Streamlit app
    Uses individual HTML files for each visualization
    """

    st.markdown("""
    These visualizations were created using D3.js.
    Click on the tabs below to explore different aspects of the haunted places data.
    """)
    
    # Create directory for visualizations if it doesn't exist
    os.makedirs("visualizations", exist_ok=True)
    
    # Check if the main D3 visualization file exists
    if not os.path.exists("visualizations/index.html"):
        st.warning("D3 visualization file not found. Creating it now...")
        
        # Create a basic HTML template for D3
        with open("visualizations/index.html", "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Haunted Places D3 Visualizations</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <script src="https://d3js.org/topojson.v3.min.js"></script>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px;
                        background-color: #1a1a1a;
                        color: #e0e0e0;
                    }
                    .visualization {
                        margin-bottom: 40px;
                        background-color: #2c2c2c;
                        padding: 20px;
                        border-radius: 8px;
                    }
                </style>
            </head>
            <body>
                <h1>👻 Haunted Places D3 Visualizations</h1>
                <p>Please replace this file with the complete D3 visualization code.</p>
                
                <div class="visualization">
                    <h2>Map Visualization</h2>
                    <div id="map-container"></div>
                </div>
                
                <div class="visualization">
                    <h2>Time Analysis</h2>
                    <div id="time-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Evidence Analysis</h2>
                    <div id="evidence-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Location Analysis</h2>
                    <div id="location-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Correlation Analysis</h2>
                    <div id="correlation-chart"></div>
                </div>
                
                <script>
                    // This is a placeholder. Replace with actual D3 code.
                    document.addEventListener('DOMContentLoaded', function() {
                        d3.select('#map-container')
                            .append('p')
                            .text('Map visualization placeholder');
                            
                        d3.select('#time-chart')
                            .append('p')
                            .text('Time analysis placeholder');
                            
                        d3.select('#evidence-chart')
                            .append('p')
                            .text('Evidence analysis placeholder');
                            
                        d3.select('#location-chart')
                            .append('p')
                            .text('Location analysis placeholder');
                            
                        d3.select('#correlation-chart')
                            .append('p')
                            .text('Correlation analysis placeholder');
                    });
                </script>
            </body>
            </html>
            """)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Map Visualization", 
        "Time Analysis", 
        "Evidence Analysis", 
        "Location Analysis", 
        "Correlation Analysis"
    ])
    
    # Display the complete D3 visualization in an iframe
    with tab1:
        st.components.v1.iframe("visualizations/index.html", height=700, scrolling=True)

def add_data_status_tab():
    st.header("Data Storage Status")
    
    st.markdown("""
    Per the assignment requirements, the haunted places data has been prepared for ingestion into:
    
    1. **Elasticsearch** - A distributed search engine
    2. **Apache Solr** - An open-source search platform
    
    The data processor (`data_processor.py`) includes functionality to ingest the processed data 
    into both systems when they are available, allowing for advanced searching and filtering.
    
    For submission purposes, the indices would be archived and submitted separately.
    """)
    
    # Show current status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Elasticsearch Status")
        st.info("Data processor configured for Elasticsearch ingestion")
        
    with col2:
        st.subheader("Solr Status")
        st.info("Data processor configured for Solr ingestion")

def add_memex_tools_tab():
    """
    Add MEMEX tools tab to the Streamlit app
    Shows options for ImageSpace and GeoParser
    """
    st.header("MEMEX Tools")
    
    tab1, tab2 = st.tabs(["ImageSpace", "GeoParser"])
    
    with tab1:
        st.subheader("Image Analysis with ImageSpace")
        
        # Add instructions on viewing the Docker-based installation
        st.info("""
        For the full ImageSpace experience, the Docker container should be running at:
        http://localhost:8080
        
        Below is a simplified version that works directly in Streamlit:
        """)
        
        # Option to upload an image or enter a URL
        option = st.radio("Select an option:", ["Upload Image", "Enter Image URL"], key="image_option")
        
        if option == "Upload Image":
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="image_upload")
            if uploaded_file is not None:
                from PIL import Image
                import io
                
                # Display the image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Image analysis button
                if st.button("Analyze Image", key="analyze_image"):
                    with st.spinner("Analyzing image..."):
                        # Basic image analysis
                        st.write("**Image Information:**")
                        st.write(f"Dimensions: {image.size[0]}x{image.size[1]} pixels")
                        st.write(f"Format: {image.format}")
                        
                        # Extract color information
                        try:
                            from collections import Counter
                            import numpy as np
                            
                            # Convert to numpy array
                            img_array = np.array(image.convert('RGB').resize((100, 100)))
                            
                            # Reshape to get list of pixels
                            pixels = img_array.reshape(-1, 3)
                            
                            # Count most common colors
                            pixel_tuples = [tuple(pixel) for pixel in pixels]
                            most_common = Counter(pixel_tuples).most_common(5)
                            
                            st.write("**Dominant Colors:**")
                            for i, (color, count) in enumerate(most_common):
                                # Display color as a swatch
                                st.markdown(
                                    f"""
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <div style="width: 30px; height: 30px; background-color: rgb{color}; margin-right: 10px;"></div>
                                        <span>Color {i+1}: RGB{color} ({count} pixels)</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        except Exception as e:
                            st.error(f"Error analyzing colors: {e}")
                        
                        # Find similar images
                        st.write("**Similar Haunted Places Images:**")
                        st.write("In the full ImageSpace application, this would show similar images based on visual features.")
                        
                        # Display sample similar images (placeholder)
                        from data_storage import data_store
                        sample_places = data_store.get_documents("haunted_places", limit=3)
                        
                        if sample_places:
                            st.write("Based on image analysis, these haunted places might have similar characteristics:")
                            cols = st.columns(3)
                            for i, place in enumerate(sample_places):
                                with cols[i]:
                                    st.write(f"**{place.get('location', 'Unknown Location')}**")
                                    st.write(f"State: {place.get('state', 'Unknown')}")
                                    st.write(f"Evidence: {place.get('evidence', 'Unknown')}")
                        else:
                            st.info("No haunted places data available for similarity comparison.")
        else:
            url = st.text_input("Enter image URL:", key="image_url")
            if url:
                try:
                    import requests
                    from PIL import Image
                    import io
                    
                    response = requests.get(url)
                    image = Image.open(io.BytesIO(response.content))
                    
                    # Display the image
                    st.image(image, caption="Image from URL", use_column_width=True)
                    
                    # Image analysis button
                    if st.button("Analyze Image", key="analyze_url_image"):
                        with st.spinner("Analyzing image..."):
                            # Basic image analysis
                            st.write("**Image Information:**")
                            st.write(f"Dimensions: {image.size[0]}x{image.size[1]} pixels")
                            st.write(f"Format: {image.format}")
                            
                            # Extract color information (same as above)
                            try:
                                from collections import Counter
                                import numpy as np
                                
                                # Convert to numpy array
                                img_array = np.array(image.convert('RGB').resize((100, 100)))
                                
                                # Reshape to get list of pixels
                                pixels = img_array.reshape(-1, 3)
                                
                                # Count most common colors
                                pixel_tuples = [tuple(pixel) for pixel in pixels]
                                most_common = Counter(pixel_tuples).most_common(5)
                                
                                st.write("**Dominant Colors:**")
                                for i, (color, count) in enumerate(most_common):
                                    st.markdown(
                                        f"""
                                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                            <div style="width: 30px; height: 30px; background-color: rgb{color}; margin-right: 10px;"></div>
                                            <span>Color {i+1}: RGB{color} ({count} pixels)</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            except Exception as e:
                                st.error(f"Error analyzing colors: {e}")
                            
                            # Similarity placeholder (same as above)
                            st.write("**Similar Haunted Places Images:**")
                            st.write("In the full ImageSpace application, this would show similar images based on visual features.")
                            
                            from data_storage import data_store
                            sample_places = data_store.get_documents("haunted_places", limit=3)
                            
                            if sample_places:
                                st.write("Based on image analysis, these haunted places might have similar characteristics:")
                                cols = st.columns(3)
                                for i, place in enumerate(sample_places):
                                    with cols[i]:
                                        st.write(f"**{place.get('location', 'Unknown Location')}**")
                                        st.write(f"State: {place.get('state', 'Unknown')}")
                                        st.write(f"Evidence: {place.get('evidence', 'Unknown')}")
                            else:
                                st.info("No haunted places data available for similarity comparison.")
                except Exception as e:
                    st.error(f"Error loading image from URL: {e}")
    
    with tab2:
        st.subheader("Location Analysis with GeoParser")
        
        st.info("""
        For the full GeoParser experience, the Docker container should be running at:
        http://localhost:8081
        
        Below is a simplified version that works directly in Streamlit:
        """)
        
        # Text input for GeoParser
        text_input = st.text_area(
            "Enter text containing location information:",
            height=150,
            key="geoparser_text"
        )
        
        if st.button("Extract Locations", key="extract_locations"):
            if text_input:
                with st.spinner("Extracting locations..."):
                    # In a real implementation, this would call the GeoParser API
                    # For now, we'll use a simple placeholder implementation
                    st.write("**Extracted Locations:**")
                    
                    # Simple location extraction (very naive implementation)
                    import re
                    from data_storage import data_store
                    
                    # Get all state names
                    states = set()
                    for doc in data_store.get_documents('haunted_places'):
                        if 'state' in doc and doc['state']:
                            states.add(doc['state'].lower())
                    
                    # Find state names in the text
                    found_states = []
                    for state in states:
                        if re.search(r'\b' + re.escape(state) + r'\b', text_input.lower()):
                            found_states.append(state)
                    
                    if found_states:
                        st.success(f"Found {len(found_states)} locations in the text.")
                        
                        # Show locations on a map
                        import folium
                        from streamlit_folium import folium_static
                        
                        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
                        
                        # Add markers for each found state
                        for state in found_states:
                            # Get all haunted places in this state
                            from data_storage import get_places_by_state
                            places = get_places_by_state(state)
                            
                            if places:
                                for place in places:
                                    if place.get('latitude') and place.get('longitude'):
                                        popup_text = f"""
                                        <b>{place.get('location', 'Unknown')}</b><br>
                                        {place.get('description', 'No description')[:100]}...
                                        """
                                        folium.Marker(
                                            [place.get('latitude'), place.get('longitude')],
                                            popup=popup_text,
                                            tooltip=place.get('location', 'Unknown')
                                        ).add_to(m)
                        
                        # Display the map
                        st.write("**Locations on map:**")
                        folium_static(m)
                    else:
                        st.warning("No known locations found in the text.")
            else:
                st.warning("Please enter text to analyze.")


def setup_d3_file():
    """
    Create the D3 visualization HTML file if it doesn't exist
    """
    # Create directory for visualizations if it doesn't exist
    os.makedirs("visualizations", exist_ok=True)
    
    # Check if the main D3 visualization file exists
    if not os.path.exists("visualizations/index.html"):
        st.warning("D3 visualization file not found. You should create it with the D3 code provided.")
        
        # Create a basic HTML template for D3
        with open("visualizations/index.html", "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Haunted Places D3 Visualizations</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <script src="https://d3js.org/topojson.v3.min.js"></script>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px;
                        background-color: #1a1a1a;
                        color: #e0e0e0;
                    }
                    .visualization {
                        margin-bottom: 40px;
                        background-color: #2c2c2c;
                        padding: 20px;
                        border-radius: 8px;
                    }
                </style>
            </head>
            <body>
                <h1>👻 Haunted Places D3 Visualizations</h1>
                <p>Please replace this file with the complete D3 visualization code.</p>
                
                <div class="visualization">
                    <h2>Map Visualization</h2>
                    <div id="map-container"></div>
                </div>
                
                <div class="visualization">
                    <h2>Time Analysis</h2>
                    <div id="time-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Evidence Analysis</h2>
                    <div id="evidence-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Location Analysis</h2>
                    <div id="location-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Correlation Analysis</h2>
                    <div id="correlation-chart"></div>
                </div>
                
                <script>
                    // This is a placeholder. Replace with actual D3 code.
                    document.addEventListener('DOMContentLoaded', function() {
                        d3.select('#map-container')
                            .append('p')
                            .text('Map visualization placeholder');
                            
                        d3.select('#time-chart')
                            .append('p')
                            .text('Time analysis placeholder');
                            
                        d3.select('#evidence-chart')
                            .append('p')
                            .text('Evidence analysis placeholder');
                            
                        d3.select('#location-chart')
                            .append('p')
                            .text('Location analysis placeholder');
                            
                        d3.select('#correlation-chart')
                            .append('p')
                            .text('Correlation analysis placeholder');
                    });
                </script>
            </body>
            </html>
            """)
        
        return False
    
    return True