# Haunted Places Explorer

An interactive Streamlit dashboard for exploring and analyzing haunted places data across the United States.

## Features

- **Interactive Map Visualization**: Explore haunted locations on an interactive map
- **Temporal Analysis**: Discover patterns in haunted sightings across different time periods
- **Evidence Analysis**: Analyze types of paranormal evidence and apparitions
- **Location-based Analysis**: Visualize geographical distribution of haunted places by state and region
- **Correlation Analysis**: Explore relationships between different variables
- **MEMEX Tools Integration**: Use simplified versions of MEMEX tools (ImageSpace and GeoParser)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/haunted-places-explorer.git
   cd haunted-places-explorer
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Data

The application uses the `haunted_places_v2.tsv` dataset, which contains information about haunted locations across the United States, including:

- Location details (name, state, coordinates)
- Description of hauntings
- Apparition types
- Evidence types

## Project Structure

- `app.py`: Main Streamlit application
- `data_processor.py`: Functions for loading and processing the haunted places data
- `data_storage.py`: In-memory data storage for the application
- `simplified_memex.py`: Simplified implementation of MEMEX tools

## DSCI 550 Assignment

This project was created as part of the DSCI 550 course assignment. 