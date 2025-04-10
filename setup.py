import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def process_data():
    """Process the haunted places data"""
    print("Processing data...")
    subprocess.check_call([sys.executable, "data_processor.py"])

def run_streamlit():
    """Run the Streamlit application"""
    print("Starting Streamlit application...")
    subprocess.check_call(["streamlit", "run", "app.py"])

def main():
    """Main setup function"""
    try:
        # Install dependencies
        install_dependencies()
        
        # Process data
        process_data()
        
        # Run Streamlit app
        run_streamlit()
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 