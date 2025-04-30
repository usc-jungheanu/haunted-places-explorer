import os
import sys
import json
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Since ETLlib might not be installed yet, we'll use pandas for the conversion
def convert_tsv_to_json(input_file, output_file):
    """
    Convert TSV file to JSON using pandas instead of ETLlib
    """
    try:
        logger.info(f"Reading TSV file: {input_file}")
        df = pd.read_csv(input_file, sep='\t', encoding='utf-8')
        
        # Convert DataFrame to JSON
        logger.info(f"Converting to JSON and writing to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(df.to_json(orient='records'))
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error converting TSV to JSON: {e}")
        return None

def process_for_visualizations(data, output_dir):
    """
    Process the data for different D3 visualizations
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Process for map visualization
        logger.info("Processing data for map visualization")
        map_data = []
        for item in data:
            if 'latitude' in item and 'longitude' in item:
                map_data.append({
                    'location': item.get('location', 'Unknown'),
                    'state': item.get('state', 'Unknown'),
                    'country': item.get('country', 'Unknown'),
                    'latitude': float(item.get('latitude', 0)),
                    'longitude': float(item.get('longitude', 0)),
                    'description': item.get('description', ''),
                })
        
        with open(os.path.join(output_dir, 'map_visualization.json'), 'w', encoding='utf-8') as f:
            json.dump(map_data, f)
        
        # Process for time analysis
        logger.info("Processing data for time analysis")
        df = pd.DataFrame(data)
        if 'year' in df.columns:
            year_counts = df['year'].value_counts().reset_index()
            year_counts.columns = ['year', 'count']
            year_counts = year_counts.sort_values('year')
            
            with open(os.path.join(output_dir, 'time_analysis.json'), 'w', encoding='utf-8') as f:
                json.dump(year_counts.to_dict(orient='records'), f)
        
        # Process for evidence analysis
        logger.info("Processing data for evidence analysis")
        if 'evidence' in df.columns:
            evidence_counts = df['evidence'].value_counts().reset_index()
            evidence_counts.columns = ['evidence_type', 'count']
            
            with open(os.path.join(output_dir, 'evidence_analysis.json'), 'w', encoding='utf-8') as f:
                json.dump(evidence_counts.to_dict(orient='records'), f)
        
        # Process for location analysis
        logger.info("Processing data for location analysis")
        if 'state' in df.columns:
            state_counts = df['state'].value_counts().reset_index()
            state_counts.columns = ['state', 'count']
            
            with open(os.path.join(output_dir, 'location_analysis.json'), 'w', encoding='utf-8') as f:
                json.dump(state_counts.to_dict(orient='records'), f)
        
        logger.info("All data processing complete")
    except Exception as e:
        logger.error(f"Error processing data for visualizations: {e}")

def main():
    # Define paths
    data_dir = os.path.join(os.getcwd(), "data")
    output_dir = os.path.join(os.getcwd(), "output", "json")
    
    # Create directories if they don't exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define input and output files
    input_file = os.path.join(data_dir, "haunted_places_v2.tsv")
    output_file = os.path.join(output_dir, "haunted_places.json")
    
    # Convert TSV to JSON
    data = convert_tsv_to_json(input_file, output_file)
    
    # Process data for various visualizations
    if data:
        process_for_visualizations(data, output_dir)
        logger.info("Conversion and processing complete")
    else:
        logger.error("Conversion failed, no data to process")

if __name__ == "__main__":
    main() 