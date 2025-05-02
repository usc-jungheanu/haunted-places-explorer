import os
import shutil
import logging
import json
import zipfile
from pathlib import Path
from datetime import datetime
from elasticsearch import Elasticsearch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndexExporter:
    """Export indices for HW3 submission"""
    
    def __init__(self, output_dir="submission"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create timestamp for filenames
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Initialized index exporter. Output directory: {self.output_dir}")
    
    def export_elasticsearch_index(self):
        """Export Elasticsearch index"""
        try:
            # Connect to Elasticsearch
            es = Elasticsearch(['http://localhost:9200'])
            
            # Check if connected
            if not es.ping():
                logger.error("Could not connect to Elasticsearch")
                return False
            
            logger.info("Connected to Elasticsearch")
            
            # Get index information
            indices = es.indices.get(index="haunted_places")
            
            if not indices:
                logger.error("Haunted places index not found")
                return False
            
            # Create repository for snapshot
            repo_settings = {
                "type": "fs",
                "settings": {
                    "location": "haunted_places_backup"
                }
            }
            
            try:
                es.snapshot.create_repository(repository="haunted_repo", body=repo_settings)
                logger.info("Created snapshot repository")
            except Exception as e:
                logger.error(f"Error creating repository: {e}")
                
                # Alternative approach - get index data directly
                logger.info("Using alternative approach - direct data export")
                
                # Get all documents from the index
                query = {"query": {"match_all": {}}, "size": 10000}
                result = es.search(index="haunted_places", body=query)
                
                # Extract documents
                docs = [hit["_source"] for hit in result["hits"]["hits"]]
                
                # Save to file
                es_export_file = self.output_dir / f"elasticsearch_export_{self.timestamp}.json"
                with open(es_export_file, 'w') as f:
                    json.dump(docs, f, indent=2)
                
                logger.info(f"Exported {len(docs)} documents to {es_export_file}")
                
                # Create zip file
                zip_file = self.output_dir / f"elasticsearch_index_{self.timestamp}.zip"
                with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(es_export_file, es_export_file.name)
                
                logger.info(f"Created Elasticsearch index archive: {zip_file}")
                return True
            
            # Create a snapshot
            snapshot_name = f"haunted_snapshot_{self.timestamp}"
            es.snapshot.create(repository="haunted_repo", snapshot=snapshot_name, body={"indices": "haunted_places"})
            
            logger.info(f"Created snapshot: {snapshot_name}")
            
            # Export the snapshot data
            # Note: In a real-world scenario, you would need to copy from the Elasticsearch
            # container. For this example, we'll create a JSON export instead.
            
            # Get all documents from the index
            query = {"query": {"match_all": {}}, "size": 10000}
            result = es.search(index="haunted_places", body=query)
            
            # Extract documents
            docs = [hit["_source"] for hit in result["hits"]["hits"]]
            
            # Save to file
            es_export_file = self.output_dir / f"elasticsearch_export_{self.timestamp}.json"
            with open(es_export_file, 'w') as f:
                json.dump(docs, f, indent=2)
            
            logger.info(f"Exported {len(docs)} documents to {es_export_file}")
            
            # Create zip file
            zip_file = self.output_dir / f"elasticsearch_index_{self.timestamp}.zip"
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(es_export_file, es_export_file.name)
            
            logger.info(f"Created Elasticsearch index archive: {zip_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting Elasticsearch index: {e}")
            return False
    
    def export_solr_index(self):
        """Export Solr index (if available)"""
        try:
            import pysolr
            
            # Try to connect to Solr
            try:
                solr = pysolr.Solr('http://localhost:8983/solr/haunted_places')
                solr.ping()
                logger.info("Connected to Solr")
            except Exception as e:
                logger.error(f"Could not connect to Solr: {e}")
                return False
            
            # Get all documents
            results = solr.search('*:*', rows=10000)
            
            if not results:
                logger.error("No documents found in Solr index")
                return False
            
            # Save to file
            solr_export_file = self.output_dir / f"solr_export_{self.timestamp}.json"
            with open(solr_export_file, 'w') as f:
                json.dump(list(results), f, indent=2)
            
            logger.info(f"Exported {len(results)} documents to {solr_export_file}")
            
            # Create zip file
            zip_file = self.output_dir / f"solr_index_{self.timestamp}.zip"
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(solr_export_file, solr_export_file.name)
            
            logger.info(f"Created Solr index archive: {zip_file}")
            return True
        
        except ImportError:
            logger.warning("pysolr not installed. Skipping Solr export.")
            return False
        except Exception as e:
            logger.error(f"Error exporting Solr index: {e}")
            return False
    
    def export_imagecat_indices(self):
        """Export ImageCat indices"""
        try:
            # Look for image features directory
            image_features_dir = Path("output") / "image_features"
            
            if not image_features_dir.exists():
                logger.error(f"Image features directory not found: {image_features_dir}")
                return False
            
            # Check if all_features.json exists
            features_file = image_features_dir / "all_features.json"
            
            if not features_file.exists():
                logger.error(f"Image features file not found: {features_file}")
                return False
            
            # Create zip file
            zip_file = self.output_dir / f"imagecat_indices_{self.timestamp}.zip"
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all_features.json
                zipf.write(features_file, features_file.name)
                
                # Add any other files in the directory
                for file in image_features_dir.glob("*"):
                    if file != features_file:
                        zipf.write(file, file.name)
            
            logger.info(f"Created ImageCat indices archive: {zip_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting ImageCat indices: {e}")
            return False
    
    def export_all(self):
        """Export all indices"""
        # Create README file
        readme_file = self.output_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(f"""# Haunted Places Indices

Exported indices for DSCI 550 HW3 submission.

## Contents

This archive contains the following indices:

1. Elasticsearch index: Contains haunted places data indexed for search
2. ImageCat indices: Contains image features for similarity search

## How to Use

### Elasticsearch Index

To import the Elasticsearch index:

```bash
# Extract the archive
unzip elasticsearch_index_*.zip

# Use the REST API to import
curl -X POST "localhost:9200/haunted_places/_bulk" -H "Content-Type: application/json" --data-binary @elasticsearch_export_*.json
```

### ImageCat Indices

To use the ImageCat indices:

1. Extract the archive to the `output/image_features` directory
2. Run the Streamlit application to explore the images

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")
        
        # Export all indices
        es_result = self.export_elasticsearch_index()
        solr_result = self.export_solr_index()
        imagecat_result = self.export_imagecat_indices()
        
        # Create final zip file
        final_zip = self.output_dir / f"haunted_places_indices_{self.timestamp}.zip"
        with zipfile.ZipFile(final_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add README
            zipf.write(readme_file, readme_file.name)
            
            # Add Elasticsearch index
            if es_result:
                es_zip = self.output_dir / f"elasticsearch_index_{self.timestamp}.zip"
                if es_zip.exists():
                    zipf.write(es_zip, es_zip.name)
            
            # Add Solr index
            if solr_result:
                solr_zip = self.output_dir / f"solr_index_{self.timestamp}.zip"
                if solr_zip.exists():
                    zipf.write(solr_zip, solr_zip.name)
            
            # Add ImageCat indices
            if imagecat_result:
                imagecat_zip = self.output_dir / f"imagecat_indices_{self.timestamp}.zip"
                if imagecat_zip.exists():
                    zipf.write(imagecat_zip, imagecat_zip.name)
        
        logger.info(f"Created final archive: {final_zip}")
        logger.info(f"Export complete! Submission file: {final_zip}")
        
        return {
            "elasticsearch": es_result,
            "solr": solr_result,
            "imagecat": imagecat_result,
            "final_zip": str(final_zip)
        }

# Main execution
if __name__ == "__main__":
    print("\n========================================")
    print(" Haunted Places Index Exporter")
    print("========================================\n")
    
    # Create exporter
    exporter = IndexExporter()
    
    # Export all indices
    print("Exporting indices for submission...\n")
    results = exporter.export_all()
    
    # Print summary
    print("\n========================================")
    print(" Export Summary")
    print("========================================")
    print(f"Elasticsearch Index: {'Success' if results['elasticsearch'] else 'Failed or Skipped'}")
    print(f"Solr Index: {'Success' if results['solr'] else 'Failed or Skipped'}")
    print(f"ImageCat Indices: {'Success' if results['imagecat'] else 'Failed or Skipped'}")
    print(f"\nFinal Submission File: {results['final_zip']}")
    print("========================================\n")