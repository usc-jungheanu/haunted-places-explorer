# 👻 Haunted Places Explorer

A comprehensive data visualization and analysis tool for haunted places data, built for DSCI 550 HW3.

## Features

- **Interactive Map Visualization**: Explore haunted locations across the US with marker clustering
- **Temporal Analysis**: Examine historical patterns and time of day distributions
- **Evidence Analysis**: Analyze types of paranormal evidence and apparition types
- **Location Analysis**: Explore geographical patterns of hauntings
- **Correlation Analysis**: Discover relationships between different variables
- **D3 Visualizations**: Interactive visualizations built with D3.js
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

3. Process the data:
   ```bash
   python scripts/convert_tsv.py
   python scripts/image_processing.py
   python scripts/geoparser.py
   python scripts/search_integration.py
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
   - **Map View**: Explore haunted locations geographically
   - **Time Analysis**: Examine temporal patterns
   - **Evidence Analysis**: Analyze types of paranormal evidence
   - **Location Analysis**: Explore geographical distributions
   - **Correlation Analysis**: Discover relationships between variables
   - **D3 Visualizations**: Interact with custom D3.js visualizations
   - **MEMEX Tools**: Use advanced image and location analysis tools
   - **Image Space**: Analyze images with similarity search
   - **GeoParser**: Extract and analyze location information
   - **Search Tools**: Search the data using Solr and ElasticSearch

## Components

### ETLlib Integration

- Conversion of TSV data to JSON for D3 visualizations
- Data processing and transformation

### Search Integration

- Solr and ElasticSearch for advanced search capabilities
- Data indexing and querying

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

For a complete list, see `requirements.txt`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: Haunted Places dataset
- MEMEX tools integration
- ETLlib for data processing 