import json
import os
import logging
from typing import Dict, List, Any, Optional, Set

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataStorage:
    """
    Simple in-memory data storage class for the application.
    Provides basic collection, document, and query functionality.
    """
    
    def __init__(self):
        """Initialize empty data storage"""
        self.collections: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("Initialized new data storage instance")
    
    def create_collection(self, collection_name: str) -> bool:
        """
        Create a new collection if it doesn't exist
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            True if collection was created, False if it already exists
        """
        if collection_name in self.collections:
            logger.warning(f"Collection '{collection_name}' already exists")
            return False
        
        self.collections[collection_name] = []
        logger.info(f"Created collection '{collection_name}'")
        return True
    
    def add_document(self, collection_name: str, document: Dict[str, Any]) -> bool:
        """
        Add a document to a collection
        
        Args:
            collection_name: Name of the collection
            document: Document to add
            
        Returns:
            True if document was added, False if collection doesn't exist
        """
        if collection_name not in self.collections:
            logger.error(f"Collection '{collection_name}' doesn't exist")
            return False
        
        self.collections[collection_name].append(document)
        logger.debug(f"Added document to '{collection_name}'")
        return True
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> int:
        """
        Add multiple documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to add
            
        Returns:
            Number of documents added, 0 if collection doesn't exist
        """
        if collection_name not in self.collections:
            logger.error(f"Collection '{collection_name}' doesn't exist")
            return 0
        
        self.collections[collection_name].extend(documents)
        logger.info(f"Added {len(documents)} documents to '{collection_name}'")
        return len(documents)
    
    def get_documents(self, collection_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get documents from a collection
        
        Args:
            collection_name: Name of the collection
            limit: Optional limit on number of documents to return
            
        Returns:
            List of documents, empty list if collection doesn't exist
        """
        if collection_name not in self.collections:
            logger.warning(f"Collection '{collection_name}' doesn't exist")
            return []
        
        documents = self.collections[collection_name]
        if limit is not None:
            documents = documents[:limit]
        
        return documents
    
    def save_collection(self, collection_name: str, file_path: str) -> bool:
        """
        Save a collection to a JSON file
        
        Args:
            collection_name: Name of the collection to save
            file_path: Path to save the collection to
            
        Returns:
            True if saved successfully, False otherwise
        """
        if collection_name not in self.collections:
            logger.error(f"Collection '{collection_name}' doesn't exist")
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.collections[collection_name], f)
            logger.info(f"Saved collection '{collection_name}' to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save collection '{collection_name}': {e}")
            return False
    
    def load_collection(self, collection_name: str, file_path: str) -> bool:
        """
        Load a collection from a JSON file
        
        Args:
            collection_name: Name to give the loaded collection
            file_path: Path to load the collection from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist")
            return False
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.collections[collection_name] = data
            logger.info(f"Loaded collection '{collection_name}' from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load collection '{collection_name}': {e}")
            return False

# Create a global instance
data_store = DataStorage()

def load_processed_data(data_dir: str = "output") -> None:
    """
    Load pre-processed data files into the data store
    
    Args:
        data_dir: Directory containing processed data files
    """
    try:
        # Create haunted_places collection if it doesn't exist
        if "haunted_places" not in data_store.collections:
            data_store.create_collection("haunted_places")
        
        # Map data
        map_data_path = os.path.join(data_dir, "map_data.json")
        if os.path.exists(map_data_path):
            with open(map_data_path, 'r') as f:
                map_data = json.load(f)
                if 'map_data' in map_data:
                    data_store.add_documents('haunted_places', map_data['map_data'])
                    logger.info(f"Loaded {len(map_data['map_data'])} places into data store")
        
        # Other data files can be loaded as needed
                
        logger.info("All data loaded into data store")
    except Exception as e:
        logger.error(f"Error loading data: {e}")

def search_places(query: str) -> List[Dict[str, Any]]:
    """
    Search for haunted places matching the query
    
    Args:
        query: Search query string
        
    Returns:
        List of matching haunted places
    """
    query = query.lower()
    results = []
    
    for place in data_store.get_documents('haunted_places'):
        # Search in location, state, country, and description
        location = str(place.get('location', '')).lower()
        state = str(place.get('state', '')).lower()
        country = str(place.get('country', '')).lower() 
        description = str(place.get('description', '')).lower()
        
        if (query in location or query in state or query in country or query in description):
            results.append(place)
    
    return results

def get_places_by_state(state: str) -> List[Dict[str, Any]]:
    """
    Get haunted places for a specific state
    
    Args:
        state: State name
        
    Returns:
        List of haunted places in the state
    """
    results = []
    
    for place in data_store.get_documents('haunted_places'):
        if place.get('state', '').lower() == state.lower():
            results.append(place)
    
    return results

def get_places_by_country(country: str) -> List[Dict[str, Any]]:
    """
    Get haunted places for a specific country
    
    Args:
        country: Country name
        
    Returns:
        List of haunted places in the country
    """
    results = []
    
    for place in data_store.get_documents('haunted_places'):
        if place.get('country', '').lower() == country.lower():
            results.append(place)
    
    return results 