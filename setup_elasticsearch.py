import subprocess
import sys
import os
import time
import json
from typing import Optional, Dict
import requests
from elasticsearch import Elasticsearch

def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_elasticsearch() -> Optional[Dict[str, str]]:
    """Set up Elasticsearch using Docker"""
    try:
        print("Setting up Elasticsearch...")
        
        # Create necessary directories
        os.makedirs("elasticsearch/data", exist_ok=True)
        os.makedirs("elasticsearch/config", exist_ok=True)
        
        # Pull Elasticsearch image
        subprocess.run([
            "docker", "pull",
            "docker.elastic.co/elasticsearch/elasticsearch:7.17.0"
        ], check=True)
        
        # Create Elasticsearch container
        subprocess.run([
            "docker", "run", "-d",
            "-p", "9200:9200",
            "-p", "9300:9300",
            "-e", "discovery.type=single-node",
            "-e", "xpack.security.enabled=false",
            "-v", f"{os.path.abspath('elasticsearch/data')}:/usr/share/elasticsearch/data",
            "-v", f"{os.path.abspath('elasticsearch/config')}:/usr/share/elasticsearch/config",
            "--name", "haunted_elasticsearch",
            "docker.elastic.co/elasticsearch/elasticsearch:7.17.0"
        ], check=True)
        
        # Wait for Elasticsearch to start
        time.sleep(60)
        
        # Check if Elasticsearch is running
        try:
            response = requests.get("http://localhost:9200")
            if response.status_code == 200:
                print("Elasticsearch setup complete!")
                return {
                    "url": "http://localhost:9200",
                    "data_dir": os.path.abspath("elasticsearch/data"),
                    "config_dir": os.path.abspath("elasticsearch/config")
                }
        except requests.RequestException:
            print("Elasticsearch is not responding")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Elasticsearch: {e}")
        return None

def ingest_data(es: Elasticsearch, data_dir: str) -> None:
    """Ingest data into Elasticsearch"""
    try:
        print("Ingesting data into Elasticsearch...")
        
        # Create index if it doesn't exist
        if not es.indices.exists(index='haunted_places'):
            es.indices.create(index='haunted_places')
        
        # Load and process data files
        data_files = [
            'map_data.json',
            'time_analysis.json',
            'location_analysis.json',
            'evidence_analysis.json',
            'correlation_data.json'
        ]
        
        for filename in data_files:
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Ingest data based on file type
                    if filename == 'map_data.json':
                        for doc in data['map_data']:
                            es.index(index='haunted_places', body=doc)
                    elif filename == 'time_analysis.json':
                        es.index(index='haunted_places', body={
                            'type': 'time_analysis',
                            'data': data
                        })
                    elif filename == 'location_analysis.json':
                        es.index(index='haunted_places', body={
                            'type': 'location_analysis',
                            'data': data
                        })
                    elif filename == 'evidence_analysis.json':
                        es.index(index='haunted_places', body={
                            'type': 'evidence_analysis',
                            'data': data
                        })
                    elif filename == 'correlation_data.json':
                        es.index(index='haunted_places', body={
                            'type': 'correlation_analysis',
                            'data': data
                        })
        
        print("Data ingestion complete!")
        
    except Exception as e:
        print(f"Error ingesting data: {e}")
        raise

def main():
    """Main setup function for Elasticsearch"""
    if not check_docker_installed():
        print("Docker is not installed or not running. Please install Docker first.")
        sys.exit(1)
    
    # Set up Elasticsearch
    es_config = setup_elasticsearch()
    if not es_config:
        print("Failed to set up Elasticsearch")
        sys.exit(1)
    
    # Connect to Elasticsearch
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    
    # Ingest data
    ingest_data(es, 'output')
    
    print("\nElasticsearch setup complete!")
    print(f"Elasticsearch URL: {es_config['url']}")
    print("\nYou can now use the D3 visualizations with the Elasticsearch backend.")

if __name__ == "__main__":
    main() 