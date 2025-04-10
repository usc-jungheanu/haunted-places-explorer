import subprocess
import sys
import os
import time
import json
from typing import Optional, Dict
import requests

def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_imagespace() -> Optional[Dict[str, str]]:
    """Set up MEMEX ImageSpace using Docker"""
    try:
        print("Setting up MEMEX ImageSpace...")
        
        # Create necessary directories
        os.makedirs("imagespace/data", exist_ok=True)
        os.makedirs("imagespace/config", exist_ok=True)
        
        # Pull ImageSpace image
        subprocess.run([
            "docker", "pull",
            "nasa-jpl-memex/image_space:latest"
        ], check=True)
        
        # Create ImageSpace container
        subprocess.run([
            "docker", "run", "-d",
            "-p", "8080:8080",
            "-v", f"{os.path.abspath('imagespace/data')}:/data",
            "-v", f"{os.path.abspath('imagespace/config')}:/config",
            "--name", "haunted_imagespace",
            "nasa-jpl-memex/image_space:latest"
        ], check=True)
        
        # Wait for ImageSpace to start
        time.sleep(60)
        
        # Check if ImageSpace is running
        try:
            response = requests.get("http://localhost:8080")
            if response.status_code == 200:
                print("MEMEX ImageSpace setup complete!")
                return {
                    "url": "http://localhost:8080",
                    "data_dir": os.path.abspath("imagespace/data"),
                    "config_dir": os.path.abspath("imagespace/config")
                }
        except requests.RequestException:
            print("ImageSpace is not responding")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error setting up ImageSpace: {e}")
        return None

def setup_geoparser() -> Optional[Dict[str, str]]:
    """Set up MEMEX GeoParser using Docker"""
    try:
        print("Setting up MEMEX GeoParser...")
        
        # Create necessary directories
        os.makedirs("geoparser/data", exist_ok=True)
        os.makedirs("geoparser/config", exist_ok=True)
        
        # Pull GeoParser image
        subprocess.run([
            "docker", "pull",
            "nasa-jpl-memex/geoparser:latest"
        ], check=True)
        
        # Create GeoParser container
        subprocess.run([
            "docker", "run", "-d",
            "-p", "8081:8081",
            "-v", f"{os.path.abspath('geoparser/data')}:/data",
            "-v", f"{os.path.abspath('geoparser/config')}:/config",
            "--name", "haunted_geoparser",
            "nasa-jpl-memex/geoparser:latest"
        ], check=True)
        
        # Wait for GeoParser to start
        time.sleep(60)
        
        # Check if GeoParser is running
        try:
            response = requests.get("http://localhost:8081")
            if response.status_code == 200:
                print("MEMEX GeoParser setup complete!")
                return {
                    "url": "http://localhost:8081",
                    "data_dir": os.path.abspath("geoparser/data"),
                    "config_dir": os.path.abspath("geoparser/config")
                }
        except requests.RequestException:
            print("GeoParser is not responding")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error setting up GeoParser: {e}")
        return None

def setup_imagecat() -> Optional[Dict[str, str]]:
    """Set up ImageCat for image processing"""
    try:
        print("Setting up ImageCat...")
        
        # Create necessary directories
        os.makedirs("imagecat/data", exist_ok=True)
        os.makedirs("imagecat/config", exist_ok=True)
        
        # Pull ImageCat image
        subprocess.run([
            "docker", "pull",
            "nasa-jpl-memex/imagecat:latest"
        ], check=True)
        
        # Create ImageCat container
        subprocess.run([
            "docker", "run", "-d",
            "-p", "8082:8082",
            "-v", f"{os.path.abspath('imagecat/data')}:/data",
            "-v", f"{os.path.abspath('imagecat/config')}:/config",
            "--name", "haunted_imagecat",
            "nasa-jpl-memex/imagecat:latest"
        ], check=True)
        
        # Wait for ImageCat to start
        time.sleep(60)
        
        # Check if ImageCat is running
        try:
            response = requests.get("http://localhost:8082")
            if response.status_code == 200:
                print("ImageCat setup complete!")
                return {
                    "url": "http://localhost:8082",
                    "data_dir": os.path.abspath("imagecat/data"),
                    "config_dir": os.path.abspath("imagecat/config")
                }
        except requests.RequestException:
            print("ImageCat is not responding")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error setting up ImageCat: {e}")
        return None

def main():
    """Main setup function for MEMEX tools"""
    if not check_docker_installed():
        print("Docker is not installed or not running. Please install Docker first.")
        sys.exit(1)
    
    # Set up ImageSpace
    imagespace_config = setup_imagespace()
    if not imagespace_config:
        print("Failed to set up ImageSpace")
        sys.exit(1)
    
    # Set up GeoParser
    geoparser_config = setup_geoparser()
    if not geoparser_config:
        print("Failed to set up GeoParser")
        sys.exit(1)
    
    # Set up ImageCat
    imagecat_config = setup_imagecat()
    if not imagecat_config:
        print("Failed to set up ImageCat")
        sys.exit(1)
    
    # Save configuration
    config = {
        "imagespace": imagespace_config,
        "geoparser": geoparser_config,
        "imagecat": imagecat_config
    }
    
    with open("memex_config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("\nMEMEX tools setup complete!")
    print(f"ImageSpace URL: {imagespace_config['url']}")
    print(f"GeoParser URL: {geoparser_config['url']}")
    print(f"ImageCat URL: {imagecat_config['url']}")
    print("\nConfiguration saved to memex_config.json")
    
    # Create a script to ingest data into ImageCat
    with open("ingest_images.py", "w") as f:
        f.write("""import os
import requests
import json
from tika import parser

def load_config():
    with open('memex_config.json', 'r') as f:
        return json.load(f)

def process_image(image_path: str, config: dict):
    # Extract metadata using Tika
    parsed = parser.from_file(image_path)
    
    # Prepare data for ImageCat
    data = {
        'file_path': image_path,
        'metadata': parsed['metadata'],
        'content': parsed['content']
    }
    
    # Send to ImageCat
    response = requests.post(
        f"{config['imagecat']['url']}/ingest",
        json=data
    )
    
    if response.status_code == 200:
        print(f"Successfully processed {image_path}")
    else:
        print(f"Failed to process {image_path}: {response.text}")

def main():
    config = load_config()
    
    # Process all images in the data directory
    for root, _, files in os.walk('data'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(root, file)
                process_image(image_path, config)

if __name__ == "__main__":
    main()
""")

if __name__ == "__main__":
    main() 