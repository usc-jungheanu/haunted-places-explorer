import streamlit as st
from pathlib import Path
import os
import pandas as pd
import json
import logging
from PIL import Image
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import image processing module
try:
    from scripts.image_processing import ImageProcessor
    image_processor_available = True
except ImportError:
    image_processor_available = False
    logger.warning("Image processing module not available. ImageSpace features will be limited.")

def display_image_features(features):
    """Display image features in a nice format"""
    if not features:
        st.error("No features available for this image")
        return
    
    st.subheader("Image Information")
    
    # Display basic image information
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Width", features.get('width', 'Unknown'))
        st.metric("Height", features.get('height', 'Unknown'))
    
    with col2:
        st.metric("Format", features.get('format', 'Unknown'))
        st.metric("Mode", features.get('mode', 'Unknown'))
    
    # Display image hashes if available
    if 'average_hash' in features or 'phash' in features or 'dhash' in features:
        st.subheader("Image Hashes")
        
        hash_col1, hash_col2, hash_col3 = st.columns(3)
        
        with hash_col1:
            if 'average_hash' in features:
                st.text_input("Average Hash", features['average_hash'], disabled=True)
        
        with hash_col2:
            if 'phash' in features:
                st.text_input("Perceptual Hash", features['phash'], disabled=True)
        
        with hash_col3:
            if 'dhash' in features:
                st.text_input("Difference Hash", features['dhash'], disabled=True)
    
    # Display metadata if available
    if 'metadata' in features:
        st.subheader("Image Metadata")
        
        # Format metadata as a table
        if isinstance(features['metadata'], dict):
            # Convert any list values to strings to avoid pyarrow conversion errors
            formatted_metadata = {}
            for k, v in features['metadata'].items():
                if isinstance(v, list):
                    formatted_metadata[k] = str(v)
                else:
                    formatted_metadata[k] = v
            
            metadata_df = pd.DataFrame(list(formatted_metadata.items()), columns=['Property', 'Value'])
            st.dataframe(metadata_df)
        else:
            st.json(features['metadata'])
    
    # Display extracted content if available
    if 'content' in features and features['content']:
        st.subheader("Extracted Text")
        st.text_area("Content", features['content'], height=200)

def display_similar_images(similar_images, similarity_method):
    """Display similar images with similarity scores"""
    if not similar_images:
        st.warning("No similar images found. Try processing more images or selecting a different similarity method.")
        return
    
    st.subheader(f"Similar Images ({similarity_method})")
    
    # Create summary info
    st.info(f"Found {len(similar_images)} similar images. Displaying the top matches.")
    
    # Create columns for displaying images
    cols = st.columns(min(len(similar_images), 3))
    
    for i, (path, distance, features) in enumerate(similar_images):
        with cols[i % 3]:
            try:
                # Display the image
                img = Image.open(path)
                
                # Calculate similarity percentage (distance is now 0-100 where lower is better)
                similarity_percent = 100 - distance
                
                st.image(img, caption=f"Similarity: {similarity_percent:.1f}%")
                
                # Display basic info in an expandable section
                with st.expander(f"Image Details: {Path(path).name}"):
                    st.text(f"File: {Path(path).name}")
                    st.text(f"Dimensions: {features.get('width', 'Unknown')}x{features.get('height', 'Unknown')}")
                    st.text(f"Format: {features.get('format', 'Unknown')}")
                    
                    # Add hash information if available
                    if similarity_method in features:
                        st.text_input(f"{similarity_method.capitalize()} Hash", 
                                     features[similarity_method], 
                                     disabled=True)
            except Exception as e:
                st.error(f"Error displaying image: {e}")

def add_image_space_tab(customize_batch=False):
    """Add Image Space tab to Streamlit
    
    Args:
        customize_batch (bool): Whether to enable customized batch processing options
    """
    # Initialize session state for batch processing if it doesn't exist
    if 'last_processed_index' not in st.session_state:
        st.session_state.last_processed_index = 0
    
    if 'last_batch_size' not in st.session_state:
        st.session_state.last_batch_size = 100
    
    st.header("Image Space Analysis")
    
    # Check if image processor is available
    if not image_processor_available:
        st.error("Image processing module not available. Please install required dependencies.")
        
        with st.expander("Installation Instructions"):
            st.markdown("""
            To enable full Image Space functionality, please install the required dependencies:
            
            ```bash
            pip install pillow imagehash tika
            ```
            
            Then restart the application.
            """)
        return
    
    # Initialize image processor
    processor = ImageProcessor()
    
    # Create tabs for different functionalities - reordering to put Batch Processing before Image Explorer
    tab1, tab3, tab2 = st.tabs(["Image Upload", "Batch Processing", "Image Explorer"])
    
    with tab1:
        st.subheader("Upload an Image for Analysis")
        
        uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif'])
        
        if uploaded_file is not None:
            # Display the uploaded image
            image_bytes = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(image, caption='Uploaded Image', use_container_width=True)
            
            with col2:
                # Save the image temporarily to extract features
                temp_path = Path("temp_upload.jpg")
                image.save(temp_path)
                
                # Extract features
                features = processor.extract_features(temp_path)
                
                # Display features
                display_image_features(features)
                
                # Find similar images
                if st.button("Find Similar Images"):
                    similarity_method = st.radio(
                        "Similarity Method",
                        options=["phash", "average_hash", "dhash"],
                        horizontal=True
                    )
                    
                    similar = processor.find_similar(temp_path, method=similarity_method)
                    display_similar_images(similar, similarity_method)
    
    # Batch Processing tab (now tab3 in UI but second in code)
    with tab3:
        st.subheader("Batch Image Processing")
        
        # Add a note about batch processing
        st.markdown("""
        **This tool allows you to process multiple images at once. For large collections (10,000+ images),
        it's recommended to process in smaller batches to avoid system resource issues.**
        """)
        
        # Get total count of images for informational purposes
        total_images = len(processor._get_image_files())
        
        if total_images == 0:
            st.error("""
            ### No images found in the 'images' directory!
            
            To use the Image Space features, you need to:
            1. Make sure the 'images' directory exists in the project root
            2. Add your image files to this directory (supported formats: jpg, jpeg, png, gif)
            
            **Note**: This folder is not included in the Git repository. When you clone this repository, you need to add your own images.
            """)
            
            # Create images directory button
            if st.button("Create 'images' directory", key="create_images_dir"):
                import os
                try:
                    os.makedirs("images", exist_ok=True)
                    st.success("'images' directory created successfully! Please add your images to this folder.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating directory: {e}")
            
            return
            
        st.info(f"📊 **Detected {total_images} images** in the images folder that can be processed. **Note:** For storage limitations within GitHub, only showing a random sample of 500 images from the full dataset of 10,000+ haunted place images.")
        
        # Check if we have batch processing customization enabled
        if customize_batch:
            # Create a section for batch size selection
            st.subheader("Batch Processing Options")
            
            # Option to select batch size, using the last batch size as default
            batch_size = st.slider(
                "Number of images to process in one batch", 
                min_value=50, 
                max_value=1000, 
                value=st.session_state.last_batch_size, 
                step=50,
                help="Selecting a smaller batch size reduces memory usage but requires more batches"
            )
            
            # Calculate how many batches would be needed
            if total_images > 0:
                total_batches = (total_images + batch_size - 1) // batch_size  # Ceiling division
                st.write(f"With this batch size, you would need **{total_batches} batches** to process all images.")
            
            # Option to select starting index - default to the last processed index
            col1, col2 = st.columns(2)
            with col1:
                st.info("""
                **Batch Processing Order:**
                - Images are processed in order by filename
                - Start from index 0 for the first batch
                - For next batch, use start index = previous start index + batch size
                """)
                
                # Calculate suggested next index based on the last processed batch
                suggested_index = st.session_state.last_processed_index
                if suggested_index >= total_images:
                    suggested_index = 0  # Reset if we've processed all images
                
                starting_index = st.number_input(
                    "Start processing from image #", 
                    min_value=0, 
                    max_value=max(0, total_images-1),
                    value=suggested_index, 
                    help="Start from a specific image index (0 = beginning)"
                )
                
                # Show which batch this would be
                if total_images > 0 and batch_size > 0:
                    current_batch = (starting_index // batch_size) + 1
                    st.write(f"This will process batch #{current_batch} of {total_batches}")
            
            with col2:
                st.write("Configure batch size and starting point, then process")
                process_col, _ = st.columns([1, 1])
                with process_col:
                    if st.button("Process Batch", key="process_custom_batch", use_container_width=True):
                        try:
                            # Calculate end index for more informative messages
                            end_index = min(starting_index + batch_size, total_images)
                            with st.spinner(f"Processing images {starting_index+1} to {end_index} (batch of {batch_size})..."):
                                # Add a progress bar
                                progress_bar = st.progress(0)
                                
                                # Implement batch processing with progress updates
                                result = processor.process_all_images(
                                    start_index=starting_index,
                                    batch_size=batch_size,
                                    progress_callback=lambda x: progress_bar.progress(x)
                                )
                                
                                if result:
                                    st.success(f"Successfully processed {len(result)} images (batch {current_batch} of {total_batches})")
                                    
                                    # Show a summary of processed images
                                    file_types = {}
                                    for features in result:
                                        if 'format' in features:
                                            format_type = features['format']
                                            if format_type in file_types:
                                                file_types[format_type] += 1
                                            else:
                                                file_types[format_type] = 1
                                    
                                    # Display summary
                                    st.subheader("Processing Summary")
                                    for format_type, count in file_types.items():
                                        st.metric(f"{format_type} Files", count)
                                    
                                    # Suggest next batch if not the last batch
                                    if end_index < total_images:
                                        next_batch_start = end_index
                                        st.info(f"""
                                        **Next Batch:**
                                        The starting index has been automatically updated to **{next_batch_start}** for the next batch.
                                        """)
                                        
                                        # Update session state for next time
                                        st.session_state.last_processed_index = next_batch_start
                                        st.session_state.last_batch_size = batch_size
                                        
                                        # Force a rerun to update the number input field
                                        st.rerun()
                                    else:
                                        # If we've processed all images, reset to 0
                                        st.session_state.last_processed_index = 0
                                        st.success("All images have been processed! Index has been reset to 0.")
                                        
                                        # Force a rerun to update the number input field
                                        st.rerun()
                                else:
                                    st.error("Error processing images")
                        except Exception as e:
                            st.error(f"Error processing images: {e}")
        
        # Add a separator before the standard "Process All" button
        st.markdown("---")
        
        # Option to process all images (keep the original functionality)
        st.subheader("Process All Images at Once")
        
        # Add a warning for large collections
        if total_images > 500:
            st.warning(f"""
            ⚠️ **Warning**: Processing all {total_images} images at once may use significant system resources. 
            Consider using the batch processing options above for better performance.
            """)
        
        col_process, col_clear = st.columns([1, 1])
        
        with col_process:
            if st.button(f"Process All {total_images} Images", key="batch_process", use_container_width=True):
                with st.spinner(f"Processing all {total_images} images..."):
                    try:
                        # Add a progress bar
                        progress_bar = st.progress(0)
                        
                        # Try to use the progress callback if available
                        try:
                            result = processor.process_all_images(
                                progress_callback=lambda x: progress_bar.progress(x)
                            )
                        except TypeError:
                            # If progress_callback is not supported, fall back to standard call
                            result = processor.process_all_images()
                        
                        if result:
                            st.success(f"Successfully processed {len(result)} images")
                            
                            # Show a summary of processed images
                            file_types = {}
                            for features in result:
                                if 'format' in features:
                                    format_type = features['format']
                                    if format_type in file_types:
                                        file_types[format_type] += 1
                                    else:
                                        file_types[format_type] = 1
                            
                            # Display summary
                            st.subheader("Processing Summary")
                            for format_type, count in file_types.items():
                                st.metric(f"{format_type} Files", count)
                        else:
                            st.error("Error processing images")
                    except Exception as e:
                        st.error(f"Error processing images: {e}")
        
        with col_clear:
            # Add a button to clear existing processed images
            if st.button("Clear Processed Images", key="clear_processed", type="secondary", use_container_width=True):
                try:
                    features_file = Path("output/image_features/all_features.json")
                    if features_file.exists():
                        # Backup the file just in case
                        backup_file = Path("output/image_features/all_features_backup.json")
                        try:
                            import shutil
                            shutil.copy2(features_file, backup_file)
                            st.info("Created backup of existing features")
                        except Exception as e:
                            st.warning(f"Could not create backup: {e}")
                        
                        # Clear the file by writing an empty list
                        with open(features_file, 'w') as f:
                            json.dump([], f)
                        
                        # Also clear the cache
                        processor.features_cache = {}
                        
                        st.success("Successfully cleared all processed image data")
                    else:
                        st.info("No processed image data found to clear")
                except Exception as e:
                    st.error(f"Error clearing processed images: {e}")
    
    # Image Explorer tab (now tab2 in UI but third in code)
    with tab2:
        st.subheader("Explore Image Collection")
        
        # Get all processed images
        try:
            features_file = Path("output/image_features/all_features.json")
            
            if not features_file.exists():
                st.info("No processed images found. Please process images using the 'Batch Processing' tab first.")
                return
            
            # Load feature data
            with open(features_file, 'r') as f:
                all_features = json.load(f)
            
            # Create a selection for images
            image_names = [f["filename"] for f in all_features]
            
            if not image_names:
                st.warning("No images have been processed yet. Please process images using the 'Batch Processing' tab.")
                return
            
            # Sort image names alphabetically for easier navigation
            image_names.sort()
            
            # Add a filter/search option for large collections
            filter_col, count_col = st.columns([3, 1])
            with filter_col:
                name_filter = st.text_input("🔍 Filter images by name", 
                                          help="Type part of an image name to filter the dropdown")
            with count_col:
                st.metric("Total Images", len(image_names))
            
            # Filter the image names if a filter is provided
            if name_filter:
                filtered_images = [name for name in image_names if name_filter.lower() in name.lower()]
                if not filtered_images:
                    st.warning(f"No images match the filter '{name_filter}'")
                    # Provide option to clear the filter
                    if st.button("Clear Filter"):
                        name_filter = ""
                        st.rerun()
                    return
                st.info(f"Found {len(filtered_images)} images matching '{name_filter}'")
                display_images = filtered_images
            else:
                display_images = image_names
                
            selected_image = st.selectbox("Select an image to explore", display_images)
            
            # Find the selected image features
            selected_features = next((f for f in all_features if f["filename"] == selected_image), None)
            
            if selected_features:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    try:
                        img = Image.open(selected_features["path"])
                        st.image(img, caption=selected_features["filename"], use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
                
                with col2:
                    display_image_features(selected_features)
                
                # Find similar images
                if st.button("Find Similar Images", key="explorer_find_similar"):
                    similarity_method = st.radio(
                        "Similarity Method",
                        options=["phash", "average_hash", "dhash"],
                        horizontal=True,
                        key="explorer_similarity_method"
                    )
                    
                    similar = processor.find_similar(selected_features["path"], method=similarity_method)
                    display_similar_images(similar, similarity_method)
        
        except Exception as e:
            st.error(f"Error exploring images: {e}")

# For testing only
if __name__ == "__main__":
    st.set_page_config(page_title="Image Space", layout="wide")
    add_image_space_tab(customize_batch=True) 