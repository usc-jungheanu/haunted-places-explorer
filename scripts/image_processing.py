import os
import logging
import json
import numpy as np
from pathlib import Path
from PIL import Image
try:
    import imagehash
except ImportError:
    logging.warning("imagehash not installed. Some features will be limited.")
try:
    from tika import parser
except ImportError:
    logging.warning("tika not installed. Metadata extraction will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Class to handle image processing for Image Space integration
    """
    def __init__(self, image_dir="images", output_dir="output"):
        self.image_dir = Path(image_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.features_cache = {}
        
        # Create output directories
        self.image_features_dir = self.output_dir / "image_features"
        self.image_features_dir.mkdir(exist_ok=True)
    
    def _get_image_files(self):
        """Get all image files in the image directory, sorted consistently"""
        extensions = ['.jpg', '.jpeg', '.png', '.gif']
        image_files = []
        
        for ext in extensions:
            image_files.extend(list(self.image_dir.glob(f"**/*{ext}")))
        
        # Sort files by path to ensure consistent ordering
        image_files.sort(key=lambda x: str(x).lower())
        
        return image_files
    
    def extract_features(self, image_path):
        """Extract features from an image"""
        image_path = Path(image_path)
        
        try:
            # Check if features already computed
            if str(image_path) in self.features_cache:
                return self.features_cache[str(image_path)]
            
            logger.info(f"Extracting features from {image_path}")
            features = {}
            
            # Basic image information
            features['path'] = str(image_path)
            features['filename'] = image_path.name
            
            # Read the image
            img = Image.open(image_path)
            features['width'] = img.width
            features['height'] = img.height
            features['format'] = img.format
            features['mode'] = img.mode
            
            # Generate image hash for similarity comparison
            try:
                if 'imagehash' in globals():
                    features['average_hash'] = str(imagehash.average_hash(img))
                    features['phash'] = str(imagehash.phash(img))
                    features['dhash'] = str(imagehash.dhash(img))
            except Exception as e:
                logger.error(f"Error computing image hash: {e}")
            
            # Extract metadata using Tika
            try:
                if 'parser' in globals():
                    metadata = parser.from_file(str(image_path))
                    if metadata and 'metadata' in metadata:
                        features['metadata'] = metadata['metadata']
                    if metadata and 'content' in metadata:
                        features['content'] = metadata['content']
            except Exception as e:
                logger.error(f"Error extracting metadata: {e}")
            
            # Cache the features
            self.features_cache[str(image_path)] = features
            
            return features
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None
    
    def process_all_images(self, start_index=0, batch_size=None, progress_callback=None):
        """
        Process images in the image directory
        
        Args:
            start_index (int): Index to start processing from
            batch_size (int): Number of images to process in this batch
            progress_callback (callable): Function to call with progress updates (0-1)
        
        Returns:
            list: List of processed image features
        """
        # Get all image files
        image_files = self._get_image_files()
        total_images = len(image_files)
        
        # Log info about total images found
        logger.info(f"Found {total_images} images to process")
        
        # Apply start_index
        if start_index >= total_images:
            logger.warning(f"Start index {start_index} exceeds total images {total_images}")
            return []
        
        # Apply batch size if specified
        if batch_size is not None:
            end_index = min(start_index + batch_size, total_images)
            logger.info(f"Processing batch from {start_index} to {end_index-1}")
            image_files = image_files[start_index:end_index]
        else:
            logger.info(f"Processing all images from index {start_index}")
            image_files = image_files[start_index:]
        
        # Get the actual number of images to process in this batch
        batch_count = len(image_files)
        logger.info(f"Batch contains {batch_count} images")
        
        results = []
        for i, image_file in enumerate(image_files):
            # Update progress if callback provided
            if progress_callback and batch_count > 0:
                progress = i / batch_count
                try:
                    progress_callback(progress)
                except Exception as e:
                    logger.error(f"Error calling progress callback: {e}")
            
            # Process the image
            features = self.extract_features(image_file)
            if features:
                results.append(features)
        
        # Final progress update
        if progress_callback:
            try:
                progress_callback(1.0)
            except Exception as e:
                logger.error(f"Error calling progress callback: {e}")
        
        # Load existing features if available
        existing_features = []
        output_file = self.image_features_dir / "all_features.json"
        if output_file.exists():
            try:
                with open(output_file, 'r') as f:
                    existing_features = json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing features: {e}")
        
        # Merge new results with existing features
        # Create a dictionary for quick lookup by path
        existing_dict = {f['path']: f for f in existing_features if 'path' in f}
        
        # Add/update features
        for feature in results:
            if 'path' in feature:
                existing_dict[feature['path']] = feature
        
        # Convert back to list
        merged_features = list(existing_dict.values())
        
        # Save all features to a json file
        with open(output_file, 'w') as f:
            json.dump(merged_features, f, indent=2)
        
        logger.info(f"Processed {len(results)} images. Total features: {len(merged_features)}. Features saved to {output_file}")
        return results
    
    def find_similar(self, query_image_path, method='phash', top_n=5):
        """Find similar images to the query image"""
        query_image_path = Path(query_image_path)
        
        # Add debug logging
        logger.info(f"Finding similar images to {query_image_path} using {method}")
        
        # Extract features for the query image
        query_features = self.extract_features(query_image_path)
        if not query_features or method not in query_features:
            logger.error(f"Could not extract {method} from query image")
            return []
        
        # Load all features if cache is empty
        if len(self.features_cache) <= 1:  # If only the query image is in cache or none at all
            try:
                features_file = self.image_features_dir / "all_features.json"
                logger.info(f"Loading features from {features_file}")
                if features_file.exists():
                    with open(features_file, 'r') as f:
                        all_features = json.load(f)
                        logger.info(f"Loaded {len(all_features)} features from file")
                        for features in all_features:
                            if 'path' in features:
                                self.features_cache[features['path']] = features
                else:
                    logger.warning("No features file found. Processing all images.")
                    self.process_all_images()
            except Exception as e:
                logger.error(f"Error loading image features: {e}")
                return []
        
        # Log cache status
        logger.info(f"Features cache contains {len(self.features_cache)} images")
        
        # Compare the query image with all other images
        similarities = []
        query_hash = query_features[method]
        query_path_str = str(query_image_path).lower()  # Normalize the path for comparison
        
        # Keep track of matching attempts for debugging
        match_attempts = 0
        hash_mismatches = 0
        
        for path, features in self.features_cache.items():
            # Normalize path for comparison
            path_str = str(path).lower()
            
            # Skip comparing the image with itself, but use normalized paths
            if path_str != query_path_str and method in features:
                match_attempts += 1
                try:
                    # Simple string difference for hash comparison
                    # In a real implementation, we'd use a proper distance metric
                    feature_hash = features[method]
                    
                    # Make sure hashes are of the same length
                    if len(query_hash) != len(feature_hash):
                        hash_mismatches += 1
                        continue
                    
                    distance = sum(c1 != c2 for c1, c2 in zip(query_hash, feature_hash))
                    max_distance = len(query_hash)  # Maximum possible distance
                    normalized_distance = (distance / max_distance) * 100  # Convert to percentage
                    
                    # Only include if reasonably similar (less than 80% different)
                    if normalized_distance < 80:
                        similarities.append((path, normalized_distance, features))
                except Exception as e:
                    logger.warning(f"Error comparing hashes: {e}")
            
        # Log matching statistics
        logger.info(f"Compared with {match_attempts} images, found {len(similarities)} similar images, had {hash_mismatches} hash mismatches")
        
        # Sort by similarity (lower distance = more similar)
        similarities.sort(key=lambda x: x[1])
        
        # Add more logging for debugging
        if not similarities:
            logger.warning("No similar images found")
        else:
            logger.info(f"Found {len(similarities)} similar images, top similarity: {100-similarities[0][1]:.1f}%")
        
        # Return top N most similar
        return similarities[:top_n]

def main():
    # Create an instance of the ImageProcessor
    processor = ImageProcessor()
    
    # Process all images
    processor.process_all_images()
    
    logger.info("Image processing complete")

if __name__ == "__main__":
    main() 