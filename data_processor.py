import pandas as pd
import json
import os
from typing import Dict, List, Any
import logging
from datetime import datetime
import numpy as np
try:
    from tika import parser
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Tika module not found. Image processing will be disabled.")
    parser = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, tsv_path: str, output_dir: str = "output"):
        """Initialize data processor with TSV file path"""
        self.tsv_path = tsv_path
        self.output_dir = output_dir
        self.data = None
        
        # Try to connect to Elasticsearch, but don't fail if it's not available
        try:
            from elasticsearch import Elasticsearch
            self.es = Elasticsearch(["http://localhost:9200"])
            self.es_available = True
        except (ImportError, Exception) as e:
            logger.warning(f"Elasticsearch not available: {e}. Data will not be indexed.")
            self.es_available = False
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def load_data(self) -> None:
        """Load and clean TSV data"""
        try:
            logger.info(f"Loading data from {self.tsv_path}")
            self.data = pd.read_csv(self.tsv_path, sep='\t', encoding='utf-8', on_bad_lines='skip')
            
            # Check and create required columns if they don't exist
            required_columns = ['latitude', 'longitude', 'location', 'state', 'country', 'description', 'date']
            
            for col in required_columns:
                if col not in self.data.columns:
                    logger.warning(f"Column '{col}' not found in data. Creating empty column.")
                    self.data[col] = np.nan
            
            # Basic data cleaning
            self.data = self.data.replace('', np.nan)
            
            # Drop rows with missing lat/long
            orig_count = len(self.data)
            self.data = self.data.dropna(subset=['latitude', 'longitude'])
            logger.info(f"Dropped {orig_count - len(self.data)} rows with missing lat/long")
            
            # Convert numeric columns
            numeric_columns = ['latitude', 'longitude']
            for col in numeric_columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            # Add other columns if they don't exist
            if 'evidence' not in self.data.columns:
                self.data['evidence'] = 'Unknown'
                
            if 'time' not in self.data.columns:
                self.data['time'] = 'Unknown'
                
            if 'apparition_type' not in self.data.columns:
                self.data['apparition_type'] = 'Unknown'
                
            if 'daylight_hours' not in self.data.columns:
                self.data['daylight_hours'] = 12  # Default value
            
            logger.info(f"Successfully loaded {len(self.data)} records")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def prepare_map_data(self) -> Dict[str, Any]:
        """Prepare data for map visualization"""
        try:
            logger.info("Preparing map data")
            map_data = []
            
            # Define common evidence types to look for - same as in prepare_evidence_analysis
            evidence_keywords = {
                "Sound": ["sound", "noise", "voice", "whisper", "footstep", "scream", "crying", "laugh", "music"],
                "Visual": ["appear", "figure", "shadow", "apparition", "image", "manifestation", "vision", "ghost"],
                "Temperature": ["cold", "chill", "temperature", "freezing", "icy", "hot", "warm", "heat"],
                "Touch": ["touch", "grab", "push", "pull", "physical", "sensation", "feel"],
                "EMF": ["emf", "electromagnetic", "electricity", "electronic", "battery", "device"],
                "Smell": ["smell", "odor", "scent", "perfume", "burning"],
                "Movement": ["move", "movement", "floating", "flying", "throw", "slam", "door", "window"],
                "Poltergeist": ["poltergeist", "thrown", "move", "thrown", "breaking"],
                "Orbs": ["orb", "ball of light", "glowing ball"],
                "EVP": ["evp", "electronic voice", "recording", "audio"]
            }
            
            # Helper function to extract evidence types from description
            def extract_evidence_from_description(description):
                if pd.isna(description) or not isinstance(description, str):
                    return "Unknown"
                
                description = description.lower()
                found_evidence = []
                
                for evidence_type, keywords in evidence_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in description:
                            found_evidence.append(evidence_type)
                            break
                
                if found_evidence:
                    return ", ".join(found_evidence)
                else:
                    return "Unknown"
            
            for _, row in self.data.iterrows():
                evidence = extract_evidence_from_description(row.get('description', ''))
                location = {
                    'location': str(row.get('location', '')),
                    'state': str(row.get('state', '')),
                    'country': str(row.get('country', '')),
                    'latitude': float(row.get('latitude', 0)),
                    'longitude': float(row.get('longitude', 0)),
                    'description': str(row.get('description', '')),
                    'date': str(row.get('evidence_date', '')),
                    'evidence': str(evidence)
                }
                map_data.append(location)
            
            return {'map_data': map_data}
            
        except Exception as e:
            logger.error(f"Error preparing map data: {e}")
            return {'map_data': []}
    
    def prepare_time_analysis(self) -> Dict[str, Any]:
        """Prepare data for time-based analysis"""
        try:
            logger.info("Preparing time analysis data")
            
            # Use the 'year' column directly if it exists
            if 'year' in self.data.columns:
                # Filter out invalid years
                valid_years = self.data['year'].dropna()
                valid_years = valid_years[valid_years != 0]
                
                # Year counts
                year_counts = valid_years.astype(int).value_counts().sort_index().reset_index()
                year_counts.columns = ['year', 'count']
                logger.info(f"Found {len(year_counts)} years with data")
            else:
                # Fallback to date column
                # Extract year from date
                self.data['year'] = pd.to_datetime(self.data['date'], errors='coerce').dt.year
                
                # Year counts
                year_counts = self.data['year'].dropna().astype(int).value_counts().sort_index().reset_index()
                year_counts.columns = ['year', 'count']
            
            # Time of day analysis
            # Check for time_of_day column first, then fall back to time column
            if 'time_of_day' in self.data.columns:
                time_column = 'time_of_day'
            else:
                time_column = 'time'
            
            # Create a more meaningful categorization if all values are "Unknown"
            time_data = self.data[time_column].copy()
            
            # If all/most values are "Unknown", try to categorize based on other columns
            if time_data.value_counts().get("Unknown", 0) > 0.9 * len(time_data):
                logger.info("Most time values are Unknown, creating categories from additional data")
                
                # Look for Morning_Event_Count_Description and Evening_Event_Count_Description columns
                if 'Morning_Event_Count_Description' in self.data.columns and 'Evening_Event_Count_Description' in self.data.columns:
                    # Create categories based on these columns
                    def categorize_time(row):
                        morning = row.get('Morning_Event_Count_Description', '')
                        evening = row.get('Evening_Event_Count_Description', '')
                        dusk = row.get('Dusk_Event_Count_Description', '')
                        
                        if isinstance(morning, str) and 'high' in morning.lower():
                            return 'Morning'
                        elif isinstance(evening, str) and 'high' in evening.lower():
                            return 'Evening'
                        elif isinstance(dusk, str) and 'high' in dusk.lower():
                            return 'Dusk'
                        
                        # Try to infer from description
                        desc = str(row.get('description', '')).lower()
                        if 'night' in desc or 'evening' in desc or 'midnight' in desc:
                            return 'Night'
                        elif 'morning' in desc or 'dawn' in desc:
                            return 'Morning'
                        elif 'afternoon' in desc or 'noon' in desc:
                            return 'Afternoon'
                        elif 'dusk' in desc or 'sunset' in desc or 'twilight' in desc:
                            return 'Dusk'
                        else:
                            return 'Unknown'
                    
                    time_data = self.data.apply(categorize_time, axis=1)
                
            time_of_day = time_data.value_counts().reset_index()
            time_of_day.columns = ['time_of_day', 'count']
            
            # Daylight hours analysis
            if 'average_daylight_hours' in self.data.columns:
                column_name = 'average_daylight_hours'
            elif 'Avg_Daylight_Hours_In_Year_Description' in self.data.columns:
                column_name = 'Avg_Daylight_Hours_In_Year_Description'
            elif 'daylight_hours' in self.data.columns:
                column_name = 'daylight_hours'
            else:
                column_name = None
                
            if column_name:
                # Extract numeric values from daylight hours descriptions if needed
                if 'Description' in column_name:
                    logger.info(f"Extracting numeric values from {column_name}")
                    # Extract numeric values from text descriptions
                    def extract_hours(value):
                        if pd.isna(value) or not isinstance(value, str):
                            return 12.0  # Default value
                        
                        value = value.lower()
                        if 'very high' in value:
                            return 14.0
                        elif 'high' in value:
                            return 13.0
                        elif 'moderate' in value:
                            return 12.0
                        elif 'low' in value:
                            return 11.0
                        elif 'very low' in value:
                            return 10.0
                        else:
                            return 12.0
                    
                    self.data['extracted_daylight_hours'] = self.data[column_name].apply(extract_hours)
                    column_name = 'extracted_daylight_hours'
                
                # Group by state and calculate mean
                daylight_by_state = self.data.groupby('state')[column_name].mean().reset_index()
                daylight_by_state.columns = ['state', 'average_daylight_hours']
                
                # We're keeping all states now, even those with default values
                # This ensures all states appear in the visualization
                
                # Check if we need to generate variation (all or most values are the same)
                if daylight_by_state['average_daylight_hours'].nunique() <= 3:
                    # Generate some variation if all values are the same
                    logger.info("All states have the same daylight hours, generating variation")
                    all_states = self.data['state'].unique()
                    
                    # Use latitude as a proxy for daylight hours (higher latitude = more variation)
                    state_lat = {}
                    for state in all_states:
                        state_rows = self.data[self.data['state'] == state]
                        state_lat[state] = state_rows['latitude'].mean()
                    
                    # Specific fixes for states with missing latitude data
                    problem_states = ['colorado', 'connecticut', 'delaware', 'minnesota', 
                                     'mississippi', 'missouri', 'rhode island', 
                                     'south carolina', 'south dakota']
                    
                    # Default latitudes for the problem states
                    default_latitudes = {
                        'colorado': 39.0, 
                        'connecticut': 41.6, 
                        'delaware': 39.0,
                        'minnesota': 46.0,
                        'mississippi': 32.7,
                        'missouri': 38.6,
                        'rhode island': 41.7,
                        'south carolina': 33.8,
                        'south dakota': 44.5
                    }
                    
                    state_daylight = []
                    for state, lat in state_lat.items():
                        # Apply special handling for problem states
                        if state.lower() in problem_states:
                            default_lat = default_latitudes[state.lower()]
                            logger.info(f"Using default latitude for {state}: {default_lat}")
                            avg_daylight = 12.0 + (default_lat - 40) * 0.1
                            state_daylight.append({'state': state, 'average_daylight_hours': float(avg_daylight)})
                        elif pd.notna(lat):
                            # For other states with valid latitude
                            avg_daylight = 12.0 + (lat - 40) * 0.1
                            state_daylight.append({'state': state, 'average_daylight_hours': float(avg_daylight)})
                        else:
                            # For any other states with NaN latitude
                            logger.warning(f"State {state} has no latitude data, using default value")
                            state_daylight.append({'state': state, 'average_daylight_hours': 12.0})
                    
                    daylight_by_state = pd.DataFrame(state_daylight)
            else:
                daylight_by_state = pd.DataFrame(columns=['state', 'average_daylight_hours'])
            
            return {
                'year_counts': year_counts.to_dict('records'),
                'time_of_day_counts': time_of_day.to_dict('records'),
                'daylight_by_state': daylight_by_state.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error preparing time analysis: {e}")
            # Return empty data structure
            return {
                'year_counts': [],
                'time_of_day_counts': [],
                'daylight_by_state': []
            }
    
    def prepare_evidence_analysis(self) -> Dict[str, Any]:
        """Prepare data for evidence analysis"""
        try:
            logger.info("Preparing evidence analysis data")
            
            # Extract evidence types from descriptions if the 'evidence' column only contains "Unknown"
            if self.data['evidence'].nunique() == 1 and 'Unknown' in self.data['evidence'].unique():
                logger.info("All evidence values are 'Unknown', extracting from descriptions")
                
                # Define common evidence types to look for
                evidence_keywords = {
                    "Sound": ["sound", "noise", "voice", "whisper", "footstep", "scream", "crying", "laugh", "music"],
                    "Visual": ["appear", "figure", "shadow", "apparition", "image", "manifestation", "vision", "ghost"],
                    "Temperature": ["cold", "chill", "temperature", "freezing", "icy", "hot", "warm", "heat"],
                    "Touch": ["touch", "grab", "push", "pull", "physical", "sensation", "feel"],
                    "EMF": ["emf", "electromagnetic", "electricity", "electronic", "battery", "device"],
                    "Smell": ["smell", "odor", "scent", "perfume", "burning"],
                    "Movement": ["move", "movement", "floating", "flying", "throw", "slam", "door", "window"],
                    "Poltergeist": ["poltergeist", "thrown", "move", "thrown", "breaking"],
                    "Orbs": ["orb", "ball of light", "glowing ball"],
                    "EVP": ["evp", "electronic voice", "recording", "audio"]
                }
                
                # Extract evidence types from descriptions
                evidence_counts = {key: 0 for key in evidence_keywords}
                
                for _, row in self.data.iterrows():
                    description = str(row.get('description', '')).lower()
                    if pd.isna(description) or description == '':
                        continue
                    
                    evidence_found = False
                    for evidence_type, keywords in evidence_keywords.items():
                        for keyword in keywords:
                            if keyword in description:
                                evidence_counts[evidence_type] += 1
                                evidence_found = True
                                break
                        
                        if evidence_found:
                            break
                            
                    if not evidence_found:
                        evidence_counts["Unknown"] = evidence_counts.get("Unknown", 0) + 1
            else:
                # Use existing evidence column
                evidence_counts = self.data['evidence'].value_counts().to_dict()
            
            # Apparition type analysis
            if 'apparition_type' in self.data.columns:
                apparition_counts = self.data['apparition_type'].value_counts().reset_index()
                apparition_counts.columns = ['apparition_type', 'count']
            else:
                apparition_counts = pd.DataFrame({'apparition_type': ['Unknown'], 'count': [len(self.data)]})
            
            return {
                'evidence_counts': evidence_counts,
                'apparition_counts': apparition_counts.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error preparing evidence analysis: {e}")
            return {
                'evidence_counts': {'Unknown': 0},
                'apparition_counts': []
            }
    
    def prepare_location_analysis(self) -> Dict[str, Any]:
        """Prepare data for location analysis"""
        try:
            logger.info("Preparing location analysis data")
            
            # State counts
            state_counts = self.data['state'].value_counts().reset_index()
            state_counts.columns = ['state', 'count']
            
            # Country counts - typically all USA
            country_counts = self.data['country'].value_counts().reset_index()
            country_counts.columns = ['country', 'count']
            
            # Create top states by apparition type
            if 'apparition_type' in self.data.columns:
                # Group data by state and apparition type
                state_apparition = self.data.groupby(['state', 'apparition_type']).size().reset_index(name='count')
                # Get the top apparition type for each state
                top_apparition_by_state = state_apparition.sort_values('count', ascending=False).drop_duplicates('state')
                # Sort by count and get top 15
                top_apparition_by_state = top_apparition_by_state.sort_values('count', ascending=False).head(15)
            else:
                top_apparition_by_state = pd.DataFrame({
                    'state': state_counts.head(15)['state'],
                    'apparition_type': 'Unknown',
                    'count': state_counts.head(15)['count']
                })
            
            # Create state location categories
            region_mapping = {
                'Northeast': ['maine', 'new hampshire', 'vermont', 'massachusetts', 'rhode island', 'connecticut', 
                              'new york', 'new jersey', 'pennsylvania'],
                'Midwest': ['ohio', 'michigan', 'indiana', 'illinois', 'wisconsin', 'minnesota', 'iowa', 
                            'missouri', 'north dakota', 'south dakota', 'nebraska', 'kansas'],
                'South': ['delaware', 'maryland', 'virginia', 'west virginia', 'kentucky', 'north carolina', 
                         'south carolina', 'tennessee', 'georgia', 'florida', 'alabama', 'mississippi', 
                         'arkansas', 'louisiana', 'texas', 'oklahoma', 'washington dc'],
                'West': ['montana', 'idaho', 'wyoming', 'colorado', 'new mexico', 'arizona', 'utah', 
                        'nevada', 'california', 'oregon', 'washington', 'alaska', 'hawaii']
            }
            
            # Map states to regions
            self.data['region'] = self.data['state'].str.lower().map(
                {state: region for region, states in region_mapping.items() for state in states}
            )
            
            # Count by region
            region_counts = self.data['region'].value_counts().reset_index()
            region_counts.columns = ['region', 'count']
            
            return {
                'state_counts': state_counts.to_dict('records'),
                'country_counts': country_counts.to_dict('records'),
                'top_apparition_by_state': top_apparition_by_state.to_dict('records'),
                'region_counts': region_counts.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error preparing location analysis: {e}")
            return {
                'state_counts': [],
                'country_counts': [],
                'top_apparition_by_state': [],
                'region_counts': []
            }
    
    def prepare_correlation_data(self) -> Dict[str, Any]:
        """Prepare data for correlation analysis"""
        try:
            logger.info("Preparing correlation data")
            
            # Create dummy variables for categorical columns first
            categorical_columns = ['state', 'evidence_type', 'apparition_type']
            for col in categorical_columns:
                if col in self.data.columns:
                    dummies = pd.get_dummies(self.data[col], prefix=col)
                    self.data = pd.concat([self.data, dummies], axis=1)
            
            # Group variables by category
            geographic_vars = ['latitude', 'longitude', 'daylight_hours', 'elevation']
            temporal_vars = ['year', 'month', 'day']
            
            # Get state variables (from dummy variables)
            state_vars = [col for col in self.data.columns if col.startswith('state_')]
            
            # Get apparition type variables (from dummy variables)
            apparition_vars = [col for col in self.data.columns if col.startswith('apparition_type_')]
            
            # Get evidence type variables (from dummy variables)
            evidence_vars = [col for col in self.data.columns if col.startswith('evidence_type_')]
            
            # Combine all variables in desired order
            all_vars = (
                geographic_vars +
                temporal_vars +
                state_vars +
                apparition_vars +
                evidence_vars
            )
            
            # Filter to only include columns that exist in the data
            numeric_columns = [col for col in all_vars if col in self.data.columns]
            
            correlation_data = []
            for i, col1 in enumerate(numeric_columns):
                for j, col2 in enumerate(numeric_columns):
                    if i <= j:  # Include diagonal and upper triangle
                        # Convert columns to numeric if needed
                        series1 = pd.to_numeric(self.data[col1], errors='coerce')
                        series2 = pd.to_numeric(self.data[col2], errors='coerce')
                        correlation = series1.corr(series2)
                        correlation_data.append({
                            'x': col1,
                            'y': col2,
                            'value': correlation if not pd.isna(correlation) else 0
                        })
            
            return {'correlation_matrix': correlation_data}
            
        except Exception as e:
            logger.error(f"Error preparing correlation data: {e}")
            return {'correlation_matrix': []}
    
    def prepare_air_pollution_analysis(self) -> Dict[str, Any]:
        """Prepare air pollution analysis data"""
        try:
            logger.info("Preparing air pollution analysis data")
            
            # Print initial data info
            print(f"Initial data shape: {self.data.shape}")
            print("\nColumns in data:", self.data.columns.tolist())
            print("\nSample of visual_evidence values:", self.data['visual_evidence'].value_counts())
            
            # Filter rows
            filtered_data = self.data[
                (self.data['CO_ppb_Description'].notna()) & 
                (self.data['CO_ppb_Description'] != "") &
                (self.data['apparition_type'].notna()) &
                (self.data['apparition_type'] != "") &
                (self.data['apparition_type'] != "Unknown")
            ].copy()
            
            # Print filtered data info
            print(f"\nFiltered data shape: {filtered_data.shape}")
            print("\nUnique CO_ppb_Description values:", filtered_data['CO_ppb_Description'].unique())
            print("\nUnique visual_evidence values:", filtered_data['visual_evidence'].unique())
            
            # Initialize results structure
            valid_categories = ['Good Air Quality', 'Moderate Air Pollution', 'Poor Air Quality']
            results = {category: {
                'total_count': 0,
                'total_percentage': 0,
                'breakdown': {
                    'FALSE': {'count': 0, 'percentage': 0},
                    'TRUE': {'count': 0, 'percentage': 0}
                }
            } for category in valid_categories}
            
            # Calculate total rows
            total_rows = len(filtered_data)
            print(f"\nTotal rows after filtering: {total_rows}")
            
            # Process each category
            for category in valid_categories:
                # Get data for this category
                category_data = filtered_data[filtered_data['CO_ppb_Description'] == category]
                category_count = len(category_data)
                
                print(f"\nProcessing {category}:")
                print(f"Category count: {category_count}")
                
                if category_count == 0:
                    continue
                
                # Calculate total percentage for this category
                results[category]['total_count'] = category_count
                results[category]['total_percentage'] = round((category_count / total_rows * 100), 2)
                
                # Count TRUE and FALSE values
                true_count = len(category_data[category_data['visual_evidence'] == True])
                false_count = len(category_data[category_data['visual_evidence'] == False])
                
                print(f"TRUE count: {true_count}")
                print(f"FALSE count: {false_count}")
                
                # Calculate percentages
                results[category]['breakdown']['TRUE'] = {
                    'count': true_count,
                    'percentage': round((true_count / category_count * 100), 2) if category_count > 0 else 0
                }
                results[category]['breakdown']['FALSE'] = {
                    'count': false_count,
                    'percentage': round((false_count / category_count * 100), 2) if category_count > 0 else 0
                }
            
            return {
                'categories': results,
                'metadata': {
                    'total_rows_analyzed': total_rows
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparing air pollution analysis: {e}")
            print(f"Error: {str(e)}")
            return {
                'categories': {},
                'metadata': {
                    'error': str(e)
                }
            }
    
    def ingest_to_elasticsearch(self) -> None:
        """Ingest data into Elasticsearch"""
        if not self.es_available:
            logger.warning("Elasticsearch not available. Skipping ingestion.")
            return
            
        try:
            logger.info("Ingesting data into Elasticsearch")
            
            # Create index if it doesn't exist
            if not self.es.indices.exists(index='haunted_places'):
                self.es.indices.create(index='haunted_places')
            
            # Ingest each record
            for _, row in self.data.iterrows():
                doc = row.to_dict()
                # Convert NaN values to None for JSON serialization
                for k, v in doc.items():
                    if isinstance(v, float) and pd.isna(v):
                        doc[k] = None
                self.es.index(index='haunted_places', body=doc)
            
            logger.info("Successfully ingested data into Elasticsearch")
            
        except Exception as e:
            logger.error(f"Error ingesting data into Elasticsearch: {e}")
    
    def process_images(self, image_dir: str) -> None:
        """Process images using Tika and prepare for ImageSpace"""
        if parser is None:
            logger.warning("Tika module not available. Skipping image processing.")
            return
            
        try:
            logger.info(f"Processing images from {image_dir}")
            
            if not os.path.exists(image_dir):
                logger.warning(f"Image directory {image_dir} does not exist. Skipping image processing.")
                return
                
            image_data = []
            for filename in os.listdir(image_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(image_dir, filename)
                    
                    # Extract metadata using Tika
                    parsed = parser.from_file(file_path)
                    
                    image_data.append({
                        'file_path': file_path,
                        'metadata': parsed.get('metadata', {}),
                        'content': parsed.get('content', '')
                    })
            
            # Save image data
            with open(os.path.join(self.output_dir, 'image_data.json'), 'w') as f:
                json.dump(image_data, f, indent=4)
            
            logger.info(f"Processed {len(image_data)} images")
            
        except Exception as e:
            logger.error(f"Error processing images: {e}")
    
    def process_all(self) -> None:
        """Process all data and save results"""
        try:
            self.load_data()
            
            # Prepare visualization data
            map_data = self.prepare_map_data()
            time_data = self.prepare_time_analysis()
            evidence_data = self.prepare_evidence_analysis()
            location_data = self.prepare_location_analysis()
            correlation_data = self.prepare_correlation_data()
            air_pollution_data = self.prepare_air_pollution_analysis()
            
            # Save all data
            data_files = {
                'map_data.json': map_data,
                'time_analysis.json': time_data,
                'evidence_analysis.json': evidence_data,
                'location_analysis.json': location_data,
                'correlation_data.json': correlation_data,
                'air_pollution.json': air_pollution_data
            }
            
            for filename, data in data_files.items():
                with open(os.path.join(self.output_dir, filename), 'w') as f:
                    json.dump(data, f, indent=4)
            
            # Try to ingest into Elasticsearch but don't fail if not available
            try:
                self.ingest_to_elasticsearch()
            except Exception as e:
                logger.warning(f"Elasticsearch ingestion failed: {e}")
            
            logger.info("All data processing complete")
            
        except Exception as e:
            logger.error(f"Error in data processing: {e}")

def main():
    """Main function to process data"""
    processor = DataProcessor('data/haunted_places_v2.tsv')
    processor.process_all()

if __name__ == "__main__":
    main() 
