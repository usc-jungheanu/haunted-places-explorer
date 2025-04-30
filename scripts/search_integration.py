import os
import json
import logging
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchIntegration:
    """
    Class to handle integration with Solr and ElasticSearch
    """
    def __init__(self, data_dir="data", output_dir="output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Check if Solr and ElasticSearch clients are available
        self.solr_available = False
        self.es_available = False
        
        try:
            import pysolr
            self.solr_available = True
            self.solr = pysolr.Solr('http://localhost:8983/solr/haunted_places')
            logger.info("Solr client initialized")
        except ImportError:
            logger.warning("pysolr not installed. Solr integration will be simulated.")
        except Exception as e:
            logger.error(f"Error initializing Solr client: {e}")
        
        try:
            from elasticsearch import Elasticsearch
            self.es_available = True
            self.es = Elasticsearch(['http://localhost:9200'])
            logger.info("ElasticSearch client initialized")
        except ImportError:
            logger.warning("elasticsearch not installed. ElasticSearch integration will be simulated.")
        except Exception as e:
            logger.error(f"Error initializing ElasticSearch client: {e}")
    
    def prepare_data(self, input_file):
        """
        Prepare data for indexing
        """
        try:
            logger.info(f"Preparing data from {input_file}")
            
            # Read the input file
            if input_file.suffix.lower() == '.tsv':
                df = pd.read_csv(input_file, sep='\t')
            elif input_file.suffix.lower() == '.csv':
                df = pd.read_csv(input_file)
            elif input_file.suffix.lower() == '.json':
                if isinstance(input_file, str):
                    with open(input_file, 'r') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame([data])
                else:
                    df = pd.read_json(input_file)
            else:
                logger.error(f"Unsupported file format: {input_file.suffix}")
                return None
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict(orient='records')
            
            # Clean and prepare data for indexing
            prepared_data = []
            for item in data:
                # Clean up None values and convert to strings for Solr
                cleaned_item = {}
                for key, value in item.items():
                    if value is not None:
                        if isinstance(value, (int, float)):
                            cleaned_item[key] = value
                        else:
                            cleaned_item[key] = str(value)
                
                # Add an ID field if not present
                if 'id' not in cleaned_item:
                    cleaned_item['id'] = str(len(prepared_data))
                
                prepared_data.append(cleaned_item)
            
            return prepared_data
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            return None
    
    def index_in_solr(self, data):
        """
        Index data in Solr
        """
        if not self.solr_available:
            logger.warning("Solr integration not available. Indexing simulated.")
            return False
        
        try:
            logger.info(f"Indexing {len(data)} documents in Solr")
            self.solr.add(data)
            self.solr.commit()
            logger.info("Solr indexing complete")
            return True
        except Exception as e:
            logger.error(f"Error indexing in Solr: {e}")
            return False
    
    def index_in_elasticsearch(self, data):
        """
        Index data in ElasticSearch
        """
        if not self.es_available:
            logger.warning("ElasticSearch integration not available. Indexing simulated.")
            return False
        
        try:
            logger.info(f"Indexing {len(data)} documents in ElasticSearch")
            
            # Check if index exists and create it if needed
            if not self.es.indices.exists(index='haunted_places'):
                self.es.indices.create(index='haunted_places')
            
            # Index documents
            for item in data:
                self.es.index(index='haunted_places', id=item['id'], body=item)
            
            logger.info("ElasticSearch indexing complete")
            return True
        except Exception as e:
            logger.error(f"Error indexing in ElasticSearch: {e}")
            return False
    
    def search_solr(self, query, **kwargs):
        """
        Search in Solr
        """
        if not self.solr_available:
            logger.warning("Solr integration not available. Search simulated.")
            return {'simulated': True, 'query': query, 'results': []}
        
        try:
            logger.info(f"Searching Solr with query: {query}")
            results = self.solr.search(query, **kwargs)
            return {'docs': list(results), 'numFound': len(results)}
        except Exception as e:
            logger.error(f"Error searching Solr: {e}")
            return {'error': str(e)}
    
    def search_elasticsearch(self, query, **kwargs):
        """
        Search in ElasticSearch
        """
        if not self.es_available:
            logger.warning("ElasticSearch integration not available. Search simulated.")
            return {'simulated': True, 'query': query, 'results': []}
        
        try:
            logger.info(f"Searching ElasticSearch with query: {query}")
            results = self.es.search(index='haunted_places', body=query, **kwargs)
            return results
        except Exception as e:
            logger.error(f"Error searching ElasticSearch: {e}")
            return {'error': str(e)}
    
    def process_all_files(self):
        """
        Process all data files and index them
        """
        try:
            # Look for data files
            data_files = []
            for file_pattern in ['*haunted*.tsv', '*haunted*.csv', '*haunted*.json']:
                data_files.extend(list(self.data_dir.glob(file_pattern)))
            
            if not data_files:
                logger.warning("No data files found")
                return False
            
            # Process each file
            for file in data_files:
                logger.info(f"Processing file: {file}")
                data = self.prepare_data(file)
                
                if data:
                    # Save processed data
                    processed_file = self.output_dir / f"processed_{file.name}.json"
                    with open(processed_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    # Index data
                    if self.solr_available:
                        self.index_in_solr(data)
                    
                    if self.es_available:
                        self.index_in_elasticsearch(data)
            
            return True
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            return False

def main():
    # Create an instance of the SearchIntegration
    search = SearchIntegration()
    
    # Process all files
    search.process_all_files()
    
    logger.info("Search integration complete")

if __name__ == "__main__":
    main() 