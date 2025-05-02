import pandas as pd
import numpy as np
import json
from elasticsearch import Elasticsearch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to Elasticsearch
try:
    es = Elasticsearch(['http://localhost:9200'])
    logger.info(f"Connected to Elasticsearch: {es.info()}")
except Exception as e:
    logger.error(f"Failed to connect to Elasticsearch: {e}")
    exit(1)

# Function to clean data for Elasticsearch
def clean_for_es(value):
    """Clean and convert values for Elasticsearch"""
    if pd.isna(value):
        return None
    
    if isinstance(value, (np.int64, np.float64)):
        return float(value)
    
    if isinstance(value, str):
        return value
    
    return str(value)

# Load data
try:
    logger.info("Loading data from TSV file")
    df = pd.read_csv('data/haunted_places_v2.tsv', sep='\t', low_memory=False)
    logger.info(f"Loaded {len(df)} records")
except Exception as e:
    logger.error(f"Error loading data: {e}")
    exit(1)

# Check if index exists and delete it
if es.indices.exists(index='haunted_places'):
    logger.info("Deleting existing index")
    es.indices.delete(index='haunted_places')

# Create index with explicit mapping
mapping = {
    "mappings": {
        "properties": {
            "location": {"type": "text"},
            "city": {"type": "keyword"},
            "state": {"type": "keyword"},
            "country": {"type": "keyword"},
            "description": {"type": "text"},
            "latitude": {"type": "float"},
            "longitude": {"type": "float"},
            "evidence": {"type": "text"},
            "apparition_type": {"type": "keyword"}
        }
    }
}

logger.info("Creating index with mapping")
es.indices.create(index='haunted_places', body=mapping)

# Process and index documents
success_count = 0
error_count = 0

for i, row in df.iterrows():
    try:
        # Create clean document
        doc = {}
        for col in df.columns:
            doc[col] = clean_for_es(row[col])
        
        # Add ID field if not present
        if 'id' not in doc:
            doc['id'] = str(i)
        
        # Index document
        es.index(index='haunted_places', id=doc['id'], document=doc)
        success_count += 1
        
        # Log progress every 100 documents
        if success_count % 100 == 0:
            logger.info(f"Indexed {success_count} documents")
            
    except Exception as e:
        logger.error(f"Error indexing document {i}: {e}")
        error_count += 1
        continue

logger.info(f"Indexing complete. Successfully indexed {success_count} documents. Failed: {error_count}")

# Refresh index to make changes visible
es.indices.refresh(index='haunted_places')

# Get document count
count = es.count(index='haunted_places')
logger.info(f"Total documents in index: {count['count']}")