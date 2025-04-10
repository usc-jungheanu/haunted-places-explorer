import subprocess
import sys
import os
import time
import json
from typing import Optional

def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_solr() -> Optional[str]:
    """Set up Apache Solr using Docker"""
    try:
        print("Setting up Apache Solr...")
        
        # Pull Solr image
        subprocess.run(["docker", "pull", "solr:8.11.1"], check=True)
        
        # Create Solr container
        subprocess.run([
            "docker", "run", "-d",
            "-p", "8983:8983",
            "--name", "haunted_solr",
            "solr:8.11.1"
        ], check=True)
        
        # Wait for Solr to start
        time.sleep(30)
        
        # Create core
        subprocess.run([
            "docker", "exec", "haunted_solr",
            "solr", "create_core", "-c", "haunted_places"
        ], check=True)
        
        print("Apache Solr setup complete!")
        return "http://localhost:8983/solr/haunted_places"
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Solr: {e}")
        return None

def setup_elasticsearch() -> Optional[str]:
    """Set up ElasticSearch using Docker"""
    try:
        print("Setting up ElasticSearch...")
        
        # Pull ElasticSearch image
        subprocess.run(["docker", "pull", "elasticsearch:8.11.0"], check=True)
        
        # Create ElasticSearch container
        subprocess.run([
            "docker", "run", "-d",
            "-p", "9200:9200",
            "-p", "9300:9300",
            "-e", "discovery.type=single-node",
            "--name", "haunted_elastic",
            "elasticsearch:8.11.0"
        ], check=True)
        
        # Wait for ElasticSearch to start
        time.sleep(30)
        
        print("ElasticSearch setup complete!")
        return "http://localhost:9200"
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up ElasticSearch: {e}")
        return None

def main():
    """Main setup function for search engines"""
    if not check_docker_installed():
        print("Docker is not installed or not running. Please install Docker first.")
        sys.exit(1)
    
    # Set up Solr
    solr_url = setup_solr()
    if not solr_url:
        print("Failed to set up Solr")
        sys.exit(1)
    
    # Set up ElasticSearch
    es_url = setup_elasticsearch()
    if not es_url:
        print("Failed to set up ElasticSearch")
        sys.exit(1)
    
    # Save configuration
    config = {
        "solr_url": solr_url,
        "elasticsearch_url": es_url
    }
    
    with open("search_config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("\nSearch engines setup complete!")
    print(f"Solr URL: {solr_url}")
    print(f"ElasticSearch URL: {es_url}")
    print("\nConfiguration saved to search_config.json")

if __name__ == "__main__":
    main() 