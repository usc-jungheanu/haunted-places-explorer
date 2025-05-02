import subprocess
import sys
import os
import shutil
import json
from pathlib import Path

# List of all required Python files for the application
REQUIRED_FILES = [
    # Main app files
    "app.py",
    "data_processor.py",
    "data_storage.py",
    "elasticsearch_indexer.py",
    "image_processor.py",
    "memex_integration.py",
    "simplified_memex.py",
    "streamlit_d3_direct.py",
    "setup_elasticsearch.py",
    "setup_memex.py",
    "setup_search_engines.py",
    
    # Script files
    "scripts/image_space_tab.py",
    "scripts/image_processing.py",
    "scripts/search_tab.py",
    "scripts/search_integration.py",
    "scripts/geoparser_tab.py",
    "scripts/geoparser.py",
    "scripts/convert_tsv.py",
]

# Required JSON data files in the output directory
REQUIRED_DATA_FILES = [
    "output/map_data.json",
    "output/time_analysis.json",
    "output/evidence_analysis.json",
    "output/location_analysis.json",
    "output/correlation_data.json"
]

def check_required_files():
    """Check if all required Python files are present"""
    print("Checking required files...")
    missing_files = []
    
    for file_path in REQUIRED_FILES:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("WARNING: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        
        if "app.py" in missing_files or "streamlit_d3_direct.py" in missing_files:
            print("ERROR: Critical files are missing. Setup cannot continue.")
            return False
        
        print("Some non-critical files are missing. Setup will continue, but some features may not work.")
    else:
        print("All required files are present.")
    
    return True

def check_data_files():
    """Check if all required data files are present"""
    print("Checking data files...")
    missing_files = []
    
    for file_path in REQUIRED_DATA_FILES:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("WARNING: The following data files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        
        print("D3 visualizations may not work properly without these files.")
        return False
    
    # Verify that the JSON files are valid
    invalid_files = []
    for file_path in REQUIRED_DATA_FILES:
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except Exception as e:
            invalid_files.append(f"{file_path}: {str(e)}")
    
    if invalid_files:
        print("WARNING: The following data files contain invalid JSON:")
        for file in invalid_files:
            print(f"  - {file}")
        
        print("D3 visualizations may not work properly with invalid JSON files.")
        return False
    
    print("All data files are present and valid.")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("You may need to install dependencies manually with: pip install -r requirements.txt")
        return False
    return True

def ensure_directories():
    """Ensure all required directories exist"""
    print("Creating necessary directories...")
    directories = ["output", "data", "images", "visualizations", "visualizations/output", "docs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Copy data files to visualizations/output directory
    output_dir = Path("output")
    vis_output_dir = Path("visualizations/output")
    
    if output_dir.exists():
        for json_file in output_dir.glob("*.json"):
            try:
                shutil.copy2(json_file, vis_output_dir / json_file.name)
            except Exception as e:
                print(f"Warning: Could not copy {json_file} to {vis_output_dir}: {e}")
    
    print("Directories created and data files copied.")
    return True

def process_data():
    """Process the haunted places data"""
    print("Checking if data processing is needed...")
    
    # If we already have the required data files, skip processing
    if all(os.path.exists(file_path) for file_path in REQUIRED_DATA_FILES):
        print("All required data files already exist. Skipping data processing.")
        return True
    
    print("Processing data...")
    try:
        # Run the data processor if available
        if os.path.exists("data_processor.py"):
            subprocess.check_call([sys.executable, "data_processor.py"])
            print("Data processing completed successfully.")
        else:
            print("WARNING: data_processor.py not found. Cannot process data.")
            return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing data: {e}")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    print("Starting Streamlit application...")
    try:
        subprocess.check_call(["streamlit", "run", "app.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        print("You may need to run Streamlit manually with: streamlit run app.py")
        return False
    return True

def main():
    """Main setup function"""
    try:
        print("Setting up Haunted Places Analysis Application...")
        
        # Step 1: Check required files
        if not check_required_files():
            print("Setup cannot continue due to missing critical files.")
            sys.exit(1)
        
        # Step 2: Ensure directories exist
        ensure_directories()
        
        # Step 3: Install dependencies
        if not install_dependencies():
            print("WARNING: Issues occurred during dependency installation.")
            # Continue despite issues
        
        # Step 4: Process data if needed
        if not process_data():
            print("WARNING: Issues occurred during data processing.")
            # Continue despite issues
        
        # Step 5: Check data files
        check_data_files()
        
        # Step 6: Run Streamlit app
        print("Setup completed successfully. Starting application...")
        run_streamlit()
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
