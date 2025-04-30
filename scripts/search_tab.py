import streamlit as st
import pandas as pd
import json
import logging
from pathlib import Path
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import search integration
try:
    from scripts.search_integration import SearchIntegration
    search_available = True
except ImportError:
    search_available = False
    logger.warning("Search integration module not available. Search features will be limited.")

def display_search_results(results, engine="solr"):
    """Display search results in a nice format"""
    if not results:
        st.warning(f"No search results from {engine}")
        return
    
    # Check if results are simulated
    if 'simulated' in results and results['simulated']:
        st.info(f"Simulated {engine} search (not connected to actual service)")
    
    # Check for error
    if 'error' in results:
        st.error(f"Error in {engine} search: {results['error']}")
        return
    
    # Format and display results based on engine
    if engine.lower() == "solr":
        if 'docs' in results:
            docs = results['docs']
            st.subheader(f"Found {results.get('numFound', len(docs))} results")
            
            if docs:
                # Convert to DataFrame for display
                df = pd.DataFrame(docs)
                st.dataframe(df)
            else:
                st.info("No matching documents found")
    
    elif engine.lower() == "elasticsearch":
        if 'hits' in results and 'hits' in results['hits']:
            hits = results['hits']['hits']
            st.subheader(f"Found {results['hits'].get('total', {}).get('value', len(hits))} results")
            
            if hits:
                # Extract source from each hit
                docs = [hit['_source'] for hit in hits]
                
                # Convert to DataFrame for display
                df = pd.DataFrame(docs)
                st.dataframe(df)
            else:
                st.info("No matching documents found")
    
    else:
        # Generic display for other result formats
        st.json(results)

def add_search_tab():
    """Add Search tab to Streamlit"""
    st.header("Search Interface")
    
    # Check if search integration is available
    if not search_available:
        st.error("Search integration module not available. Please install required dependencies.")
        
        with st.expander("Installation Instructions"):
            st.markdown("""
            To enable full search functionality, please install the required dependencies:
            
            ```bash
            pip install pysolr elasticsearch
            ```
            
            Then start Solr and ElasticSearch using Docker:
            
            ```bash
            docker-compose up -d
            ```
            
            Then restart the application.
            """)
        return
    
    # Initialize search integration
    search = SearchIntegration()
    
    # Create tabs for different search engines
    tab1, tab2, tab3 = st.tabs(["Solr Search", "ElasticSearch Search", "Index Data"])
    
    with tab1:
        st.subheader("Solr Search")
        
        # Search form
        with st.form("solr_search_form"):
            query = st.text_input("Search Query", placeholder="Enter search terms...")
            
            # Advanced options
            with st.expander("Advanced Options"):
                fields = st.text_input("Fields to Return", placeholder="comma-separated fields, e.g., location,state,evidence")
                filter_query = st.text_input("Filter Query", placeholder="e.g., state:California")
                rows = st.slider("Maximum Results", min_value=10, max_value=100, value=20)
                
            # Submit button
            search_submitted = st.form_submit_button("Search")
        
        if search_submitted and query:
            with st.spinner("Searching..."):
                # Prepare search parameters
                search_params = {
                    'rows': rows
                }
                
                if fields:
                    search_params['fl'] = fields
                
                if filter_query:
                    search_params['fq'] = filter_query
                
                # Perform search
                results = search.search_solr(query, **search_params)
                
                # Display results
                display_search_results(results, "solr")
    
    with tab2:
        st.subheader("ElasticSearch Search")
        
        # Search form
        with st.form("es_search_form"):
            query_text = st.text_input("Search Query", placeholder="Enter search terms...", key="es_query")
            
            # Advanced options
            with st.expander("Advanced Options"):
                field_name = st.text_input("Field Name", "description")
                size = st.slider("Maximum Results", min_value=10, max_value=100, value=20, key="es_size")
                
            # Submit button
            es_search_submitted = st.form_submit_button("Search")
        
        if es_search_submitted and query_text:
            with st.spinner("Searching..."):
                # Prepare query
                query = {
                    "query": {
                        "match": {
                            field_name: query_text
                        }
                    },
                    "size": size
                }
                
                # Perform search
                results = search.search_elasticsearch(query)
                
                # Display results
                display_search_results(results, "elasticsearch")
    
    with tab3:
        st.subheader("Index Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # File upload option
            st.markdown("### Upload File to Index")
            
            uploaded_file = st.file_uploader("Upload TSV, CSV, or JSON file", type=['tsv', 'csv', 'json'])
            
            if uploaded_file is not None:
                # Save the uploaded file temporarily
                file_extension = Path(uploaded_file.name).suffix
                temp_path = Path(f"temp_search_upload{file_extension}")
                
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                # Index options
                index_solr = st.checkbox("Index in Solr", value=True)
                index_es = st.checkbox("Index in ElasticSearch", value=True)
                
                if st.button("Index Uploaded File"):
                    with st.spinner("Processing and indexing data..."):
                        # Prepare data
                        data = search.prepare_data(temp_path)
                        
                        if data:
                            # Index in selected engines
                            results = []
                            
                            if index_solr:
                                solr_result = search.index_in_solr(data)
                                results.append(f"Solr: {'Success' if solr_result else 'Failed'}")
                            
                            if index_es:
                                es_result = search.index_in_elasticsearch(data)
                                results.append(f"ElasticSearch: {'Success' if es_result else 'Failed'}")
                            
                            # Display results
                            st.success(f"Indexed {len(data)} documents - " + ", ".join(results))
                        else:
                            st.error("Error preparing data for indexing")
        
        with col2:
            # Process all files option
            st.markdown("### Process All Files")
            
            st.info("This will find and index all haunted places data files in the data directory")
            
            if st.button("Process All Files"):
                with st.spinner("Processing all files..."):
                    result = search.process_all_files()
                    
                    if result:
                        st.success("All files processed and indexed successfully")
                    else:
                        st.error("Error processing files")
                        st.info("Make sure you have haunted places data files in the 'data' directory")

# For testing only
if __name__ == "__main__":
    st.set_page_config(page_title="Search Interface", layout="wide")
    add_search_tab() 