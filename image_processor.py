import os
import logging
import json
import hashlib
from pathlib import Path
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Process images for ImageSpace/ImageCat integration"""
    
    def __init__(self, image_dir="images", output_dir="output"):
        self.image_dir = Path(image_dir)
        self.output_dir = Path(output_dir) / "image_features"
        
        # Create directories if they don't exist
        self.image_dir.mkdir(exist_ok=True, parents=True)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Initialized image processor: {self.image_dir} -> {self.output_dir}")
        
        # Keep track of processed images
        self.processed_images = []
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing processed data if available"""
        index_file = self.output_dir / "all_features.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self.processed_images = json.load(f)
                logger.info(f"Loaded {len(self.processed_images)} previously processed images")
            except Exception as e:
                logger.error(f"Error loading existing data: {e}")
    
    def save_data(self):
        """Save processed image data"""
        index_file = self.output_dir / "all_features.json"
        
        try:
            with open(index_file, 'w') as f:
                json.dump(self.processed_images, f, indent=2)
            logger.info(f"Saved {len(self.processed_images)} processed images to {index_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def get_image_hash(self, image_path):
        """Generate a hash for the image file"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating hash for {image_path}: {e}")
            return None
    
    def extract_features(self, image_path):
        """Extract features from an image"""
        try:
            image_path = Path(image_path)
            
            # Skip if already processed
            image_hash = self.get_image_hash(image_path)
            for img in self.processed_images:
                if img.get('hash') == image_hash:
                    logger.debug(f"Skipping already processed image: {image_path}")
                    return img
            
            logger.info(f"Processing image: {image_path}")
            
            # Open and analyze image
            img = Image.open(image_path)
            
            # Basic image features
            features = {
                'filename': image_path.name,
                'path': str(image_path),
                'hash': image_hash,
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
            }
            
            # Generate image histogram (for similarity matching)
            if img.mode in ('RGB', 'RGBA'):
                histogram = img.histogram()
                features['histogram'] = histogram[:768]  # Keep RGB channels only
            
            # Calculate average color
            if img.mode == 'RGB':
                rgb_img = img
            else:
                rgb_img = img.convert('RGB')
                
            pixels = list(rgb_img.getdata())
            avg_r = sum(pixel[0] for pixel in pixels) / len(pixels)
            avg_g = sum(pixel[1] for pixel in pixels) / len(pixels)
            avg_b = sum(pixel[2] for pixel in pixels) / len(pixels)
            
            features['avg_color'] = {
                'r': avg_r,
                'g': avg_g,
                'b': avg_b
            }
            
            # Add to processed images
            self.processed_images.append(features)
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features from {image_path}: {e}")
            return None
    
    def process_all_images(self, start_idx=0, batch_size=None):
        """Process all images in the directory"""
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(list(self.image_dir.glob(f"**/*{ext}")))
            image_files.extend(list(self.image_dir.glob(f"**/*{ext.upper()}")))
        
        # Sort files for consistent ordering
        image_files.sort()
        
        # Apply start index and batch size
        if start_idx >= len(image_files):
            logger.warning(f"Start index {start_idx} exceeds number of images {len(image_files)}")
            return []
        
        if batch_size:
            end_idx = min(start_idx + batch_size, len(image_files))
            image_files = image_files[start_idx:end_idx]
        
        logger.info(f"Processing {len(image_files)} images")
        
        # Process each image
        processed = []
        for i, image_file in enumerate(image_files):
            try:
                features = self.extract_features(image_file)
                if features:
                    processed.append(features)
                
                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(image_files)} images")
            except Exception as e:
                logger.error(f"Error processing {image_file}: {e}")
                continue
        
        # Save results
        self.save_data()
        
        return processed
    
    def find_similar(self, query_image_path, top_n=5):
        """Find similar images to the query image"""
        try:
            # Extract features for the query image
            query_features = self.extract_features(query_image_path)
            
            if not query_features or 'histogram' not in query_features:
                logger.error(f"Failed to extract features from query image: {query_image_path}")
                return []
            
            # Calculate similarity scores
            similarities = []
            for img in self.processed_images:
                if 'histogram' not in img:
                    continue
                
                # Skip comparing with itself
                if img['hash'] == query_features['hash']:
                    continue
                
                # Calculate histogram similarity
                score = 0
                for i in range(min(len(query_features['histogram']), len(img['histogram']))):
                    score += (query_features['histogram'][i] - img['histogram'][i]) ** 2
                
                # Lower score = more similar
                similarities.append((img, score))
            
            # Sort by similarity (lowest score first)
            similarities.sort(key=lambda x: x[1])
            
            # Return top N similar images
            return [img for img, _ in similarities[:top_n]]
        except Exception as e:
            logger.error(f"Error finding similar images: {e}")
            return []

# Main execution
if __name__ == "__main__":
    # Create processor
    processor = ImageProcessor()
    
    # Check if images directory is empty
    if not list(processor.image_dir.glob('**/*')):
        logger.warning(f"No images found in {processor.image_dir}. Creating sample directories.")
        
        # Create sample directories for user to add images
        sample_dirs = ['haunted_houses', 'ghostly_figures', 'paranormal_evidence']
        for dir_name in sample_dirs:
            (processor.image_dir / dir_name).mkdir(exist_ok=True)
        
        print(f"\nIMPORTANT: Please add images to the '{processor.image_dir}' directory before running this script again.")
        print(f"             You can organize them in the sample subdirectories that were created.")
        exit(0)
    
    # Process images
    print(f"\nProcessing images from '{processor.image_dir}'...")
    processor.process_all_images()
    
    print(f"\nImage processing complete!")
    print(f"Processed {len(processor.processed_images)} images.")
    print(f"Features saved to: {processor.output_dir / 'all_features.json'}")
    print("\nYou can now use the Streamlit app to explore the images and find similar images.")