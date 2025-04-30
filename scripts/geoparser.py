import os
import json
import logging
import pandas as pd
import re
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationAnalyzer:
    """
    Class to handle location analysis and GeoParser integration
    Note: This is a simulated implementation since we might not have Mordecai installed
    """
    def __init__(self, data_dir="data", output_dir="output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create output directory for location analysis
        self.location_output_dir = self.output_dir / "location_analysis"
        self.location_output_dir.mkdir(exist_ok=True)
        
        # Try to import mordecai if available
        try:
            import mordecai
            self.geoparser_available = True
            # Create a new instance of the geoparser
            # This is commented out because it requires a running Elasticsearch instance
            # self.geoparser = mordecai.Geoparser()
        except ImportError:
            logger.warning("Mordecai not installed. Will use simulated geoparsing.")
            self.geoparser_available = False
    
    def _simulated_geoparse(self, text):
        """
        Simple simulated geoparsing function
        In a real implementation, we would use Mordecai's geoparser
        """
        # Simple regex to find locations (state names, cities)
        us_states = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
            "New Hampshire", "New Jersey", "New Mexico", "New York", 
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
            "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
            "West Virginia", "Wisconsin", "Wyoming"
        ]
        
        found_locations = []
        
        for state in us_states:
            if re.search(r'\b' + re.escape(state) + r'\b', text, re.IGNORECASE):
                found_locations.append({
                    'location': state,
                    'confidence': 0.9,
                    'type': 'state',
                    'country_code': 'US',
                    'lat': 0.0,  # In a real implementation, we would use actual coordinates
                    'lon': 0.0
                })
        
        # Look for cities (this is very simplified)
        city_patterns = [
            r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b',  # City, State
            r'\bin\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b'  # "in CityName"
        ]
        
        for pattern in city_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                city = match.group(1) if len(match.groups()) > 0 else match.group(0)
                found_locations.append({
                    'location': city,
                    'confidence': 0.7,
                    'type': 'city',
                    'country_code': 'US',
                    'lat': 0.0,
                    'lon': 0.0
                })
        
        return found_locations
    
    def process_locations(self, text):
        """
        Process text to extract location information
        """
        if not text or not isinstance(text, str):
            return []
        
        if self.geoparser_available:
            try:
                # Use mordecai's geoparser (commented out because it requires Elasticsearch)
                # return self.geoparser.geoparse(text)
                return self._simulated_geoparse(text)
            except Exception as e:
                logger.error(f"Error using mordecai geoparser: {e}")
                return self._simulated_geoparse(text)
        else:
            return self._simulated_geoparse(text)
    
    def analyze_data(self, data_file):
        """
        Analyze location data from a given file
        """
        try:
            logger.info(f"Analyzing location data from {data_file}")
            
            # Read the input file
            if data_file.suffix.lower() == '.tsv':
                df = pd.read_csv(data_file, sep='\t')
            elif data_file.suffix.lower() == '.csv':
                df = pd.read_csv(data_file)
            elif data_file.suffix.lower() == '.json':
                df = pd.read_json(data_file)
            else:
                logger.error(f"Unsupported file format: {data_file.suffix}")
                return None
            
            # Process locations
            location_results = []
            
            if 'description' in df.columns:
                for idx, row in df.iterrows():
                    if isinstance(row['description'], str):
                        locations = self.process_locations(row['description'])
                        if locations:
                            for loc in locations:
                                location_results.append({
                                    'source_idx': idx,
                                    'location': loc['location'],
                                    'type': loc['type'],
                                    'confidence': loc['confidence'],
                                    'lat': loc['lat'],
                                    'lon': loc['lon']
                                })
            
            # Aggregate results
            results = {
                'total_locations': len(location_results),
                'locations': location_results,
                'location_types': {}
            }
            
            # Count location types
            for loc in location_results:
                loc_type = loc['type']
                if loc_type in results['location_types']:
                    results['location_types'][loc_type] += 1
                else:
                    results['location_types'][loc_type] = 1
            
            # Save results
            output_file = self.location_output_dir / "location_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Location analysis complete. Results saved to {output_file}")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing location data: {e}")
            return None
    
    def analyze_historical_data(self):
        """
        Process location data from previous assignments
        """
        try:
            # Look for historical data files
            historical_files = []
            for file_pattern in ['*haunted*.tsv', '*haunted*.csv', '*haunted*.json']:
                historical_files.extend(list(self.data_dir.glob(file_pattern)))
            
            if not historical_files:
                logger.warning("No historical data files found")
                return None
            
            # Process each file
            all_results = []
            for file in historical_files:
                result = self.analyze_data(file)
                if result:
                    all_results.append({
                        'file': str(file),
                        'results': result
                    })
            
            # Aggregate results across files
            aggregated_results = {
                'total_files': len(all_results),
                'total_locations': sum(r['results']['total_locations'] for r in all_results if r['results']),
                'file_results': all_results,
                'location_types': {}
            }
            
            # Aggregate location types
            for result in all_results:
                if result['results'] and 'location_types' in result['results']:
                    for loc_type, count in result['results']['location_types'].items():
                        if loc_type in aggregated_results['location_types']:
                            aggregated_results['location_types'][loc_type] += count
                        else:
                            aggregated_results['location_types'][loc_type] = count
            
            # Save aggregated results
            output_file = self.location_output_dir / "historical_location_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(aggregated_results, f, indent=2)
            
            logger.info(f"Historical location analysis complete. Results saved to {output_file}")
            return aggregated_results
            
        except Exception as e:
            logger.error(f"Error analyzing historical location data: {e}")
            return None

def main():
    # Create an instance of the LocationAnalyzer
    analyzer = LocationAnalyzer()
    
    # Analyze data from data directory
    analyzer.analyze_historical_data()
    
    logger.info("Location analysis complete")

if __name__ == "__main__":
    main() 