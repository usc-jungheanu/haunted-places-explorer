# 👻 Haunted Places Explorer

A comprehensive data visualization and analysis tool for haunted places data, built for DSCI 550 HW3.

> **⚠️ IMPORTANT:** Please use **Light mode** when viewing the application. This ensures all text in visualizations is properly visible. Dark mode may cause some text elements to be difficult to read in certain charts and visualizations.

## Features

- **Air Pollution Visualization**: Visualize key insights derived from air pollution feature set appended in homework 1
- **Interactive Map Visualization**: Explore haunted locations across the US with marker clustering
- **Temporal Analysis**: Examine historical patterns and time of day distributions
- **Evidence Analysis**: Analyze types of paranormal evidence and apparition types
- **Location Analysis**: Explore geographical patterns of hauntings
- **Correlation Analysis**: Discover relationships between different variables
- **D3 Visualizations**: Interactive visualizations built directly with D3.js (no iframes)
- **MEMEX Tools**: Image analysis and location tools integration
- **Search Capabilities**: Solr and ElasticSearch integration
- **GeoParser**: Location extraction and analysis

## Installation

### Prerequisites

- Python 3.7+
- Docker (for Solr and ElasticSearch)

### Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/haunted-places-explorer.git
   cd haunted-places-explorer
   ```

2. Run the setup script:
   ```bash
   python setup.py
   ```

This will:
- Install all required dependencies
- Create necessary directories
- Process the data
- Start the Streamlit application

### Manual Installation

If you prefer to install manually:

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Solr and ElasticSearch (optional):
   ```bash
   docker-compose up -d
   ```

3. Ensure the output directory exists and has the necessary data files:
   ```bash
   mkdir -p output
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Data

The application uses the `haunted_places_v2.tsv` dataset, which should be placed in the `data` directory. This dataset contains information about haunted locations across the United States, including:

- Location details (name, state, coordinates)
- Description of paranormal activity
- Types of evidence and apparitions
- Historical information

### Required Data Files

The following JSON files should be present in the `output` directory for the visualizations to work properly:
- `map_data.json`: Contains geographical data for haunted locations
- `time_analysis.json`: Contains temporal data for hauntings
- `evidence_analysis.json`: Contains data about types of evidence
- `location_analysis.json`: Contains geographical distributions
- `correlation_data.json`: Contains relationship data between variables

### Image Data

For the Image Space features, you need to place your image files in the `images` directory:

1. Create an `images` folder in the project root if it doesn't exist:
   ```bash
   mkdir -p images
   ```

2. Add your image files to this directory (supported formats: jpg, jpeg, png, gif).

3. Process the images using the Image Space tab in the application:
   - Navigate to "MEMEX Tools" > "Image Space" > "Batch Processing"
   - Process images in batches (recommended 100-500 at a time for large collections)

**Note**: The images folder is excluded from Git due to size considerations. When cloning this repository, you'll need to create the folder and add your own images.

## Usage

1. Navigate using the sidebar menu to explore different visualizations
2. Each tab offers unique insights and interactive elements:
   - **Air Pollution Analysis**: Analyze key insights derived from air pollution feature set
   - **Map View**: Explore haunted locations geographically
   - **Time Analysis**: Examine temporal patterns
   - **Evidence Analysis**: Analyze types of paranormal evidence
   - **Location Analysis**: Explore geographical distributions
   - **Correlation Analysis**: Discover relationships between variables
   - **D3 Visualizations**: Interact with custom D3.js visualizations directly embedded in Streamlit
   - **MEMEX Tools**: Use advanced image and location analysis tools
   - **Image Space**: Analyze images with similarity search
   - **GeoParser**: Extract and analyze location information
   - **Search Tools**: Search the data using Solr and ElasticSearch

## Components

### D3.js Visualizations

- Direct embedding of D3.js visualizations within Streamlit components
- No iframes are used, ensuring better security and compatibility
- Interactive map, time series charts, bar charts, pie charts, and geographic heatmaps
- Custom styling and tooltips for enhanced user experience

### Search Integration

- Solr and ElasticSearch for advanced search capabilities
- Data indexing and querying
- Fallback to simplified search when Docker components are not available

### Image Space

- Image similarity search
- Feature extraction and comparison
- Metadata analysis
- Batch processing for large image collections

### GeoParser

- Location extraction from text
- Geographic analysis of haunted locations
- Coordinate mapping

## Troubleshooting

### D3 Visualization Issues

If you encounter issues with the D3 visualizations:

1. Make sure all required JSON files exist in the `output` directory
2. Check that the JSON files have the expected structure
3. The application logs will show detailed errors if there are issues loading the data

### Image Processing Issues

If you encounter errors during image processing:

1. Make sure the `images` directory exists and contains image files
2. For large collections, process images in smaller batches (100-500 at a time)
3. Ensure you have enough disk space and memory
4. Check that Tika is properly installed (`pip install tika`)

### Search Tool Errors

If search features show connection errors:

1. Make sure Docker is running
2. Start containers using `docker-compose up -d`
3. Verify container status with `docker ps`
4. The application will use fallback search mode when Docker is not available

## Project Structure

The project has been reorganized for better clarity and performance:

- **app.py**: Main Streamlit application
- **streamlit_d3_direct.py**: Direct D3.js visualizations integrated with Streamlit
- **data_processor.py**: Processes the haunted places data
- **data_storage.py**: Handles data storage and retrieval
- **simplified_memex.py**: Simplified MEMEX tools that work without Docker
- **elasticsearch_indexer.py**: Handles Elasticsearch indexing and queries
- **setup.py**: Script to set up the application

## Dependencies

The main dependencies are:
- Streamlit
- Pandas
- Plotly
- Folium
- ElasticSearch
- pysolr
- Pillow
- Tika
- Mordecai (for geoparsing capability)

For a complete list, see `requirements.txt`.

### Optional Dependencies

**Mordecai**: If Mordecai is not installed, the application will fall back to using simulated geoparsing. To install Mordecai:

```bash
pip install mordecai==2.1.0
```

Note that Mordecai installation may require additional system dependencies like SpaCy models. If you encounter issues installing Mordecai, the application will still work with reduced geoparsing capabilities.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: Haunted Places dataset
- MEMEX tools integration
- D3.js for advanced visualizations
- Streamlit for the interactive web application

## Authors

Tyler Wong

Ryan Ho

Jesse Fulcher

Jason Ungheanu

James Temme

