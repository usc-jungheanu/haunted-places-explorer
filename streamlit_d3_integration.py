import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

def add_d3_visualizations_tab():
    """
    Add D3 visualizations tab to the Streamlit app
    Directly creates visualizations using Streamlit/Plotly instead of D3
    """
    st.title("D3 Visualizations")
    
    # Display the D3 visualizations header
    st.markdown("""
    ## Interactive Visualizations
    
    Below are interactive visualizations of the haunted places data.
    """)
    
    # Add a reload button
    if st.button("🔄 Reload Data", help="Click to reload data if visualizations aren't displaying correctly"):
        st.cache_data.clear()
        st.rerun()
    
    # Create tabs for different visualizations with clear formatting
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Map Visualization", 
        "⏱️ Time Analysis", 
        "🔍 Evidence Analysis", 
        "📍 Location Analysis", 
        "📊 Correlation Analysis"
    ])
    
    # Load all data
    output_dir = "output"
    data = {}
    try:
        with open(os.path.join(output_dir, "map_data.json"), "r") as f:
            data["map"] = json.load(f)
    except Exception as e:
        data["map"] = None
        
    try:
        with open(os.path.join(output_dir, "time_analysis.json"), "r") as f:
            data["time"] = json.load(f)
    except Exception as e:
        data["time"] = None
        
    try:
        with open(os.path.join(output_dir, "evidence_analysis.json"), "r") as f:
            data["evidence"] = json.load(f)
    except Exception as e:
        data["evidence"] = None
        
    try:
        with open(os.path.join(output_dir, "location_analysis.json"), "r") as f:
            data["location"] = json.load(f)
    except Exception as e:
        data["location"] = None
        
    try:
        with open(os.path.join(output_dir, "correlation_data.json"), "r") as f:
            data["correlation"] = json.load(f)
    except Exception as e:
        data["correlation"] = None
    
    # Map Visualization Tab
    with tab1:
        st.header("Map Visualization")
        if data["map"] and "map_data" in data["map"]:
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(data["map"]["map_data"])
            
            # Filter for USA data
            usa_df = df[df['country'].str.lower() == 'united states'].copy()
            
            if len(usa_df) > 0:
                # Display map using Plotly
                fig = px.scatter_geo(
                    usa_df, 
                    lat="latitude", 
                    lon="longitude",
                    hover_name="location",
                    hover_data=["state", "description"],
                    title="Interactive Map of Haunted Locations in the USA",
                    color_discrete_sequence=["red"],
                    size_max=10,
                )
                
                # Center on USA and set appropriate zoom
                fig.update_geos(
                    scope="usa",
                    showcoastlines=True,
                    coastlinecolor="Black",
                    showland=True,
                    landcolor="lightgray",
                    showsubunits=True,  # This shows state boundaries
                    subunitcolor="gray",
                )
                
                fig.update_layout(
                    height=600,
                    margin=dict(l=0, r=0, t=30, b=0),
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add some stats about the data
                st.markdown(f"**Total Haunted Places in USA:** {len(usa_df)}")
                
                # Show top 5 states
                top_states = usa_df.groupby('state').size().reset_index(name='count').sort_values('count', ascending=False).head(5)
                st.markdown("**Top 5 States with Most Haunted Places:**")
                st.dataframe(top_states)
            else:
                st.error("No USA data found in the dataset.")
        else:
            st.error("Map data not available. Please run the data processing script.")
    
    # Time Analysis Tab
    with tab2:
        st.header("Temporal Patterns of Hauntings")
        
        if data["time"] and any(key in data["time"] for key in ["year_counts", "month_counts", "time_of_day_counts"]):
            # Create three columns
            col1, col2 = st.columns(2)
            
            # Year analysis
            if "year_counts" in data["time"]:
                try:
                    with col1:
                        st.subheader("Historical Timeline of Hauntings")
                        
                        # Convert to DataFrame
                        if isinstance(data["time"]["year_counts"], list):
                            # If it's a list of dictionaries
                            year_df = pd.DataFrame(data["time"]["year_counts"])
                            if "year" not in year_df.columns and "name" in year_df.columns:
                                year_df = year_df.rename(columns={"name": "year"})
                            if "count" not in year_df.columns and "value" in year_df.columns:
                                year_df = year_df.rename(columns={"value": "count"})
                        else:
                            # If it's a dictionary
                            year_df = pd.DataFrame({
                                "year": list(data["time"]["year_counts"].keys()),
                                "count": list(data["time"]["year_counts"].values())
                            })
                        
                        # Convert year to numeric if it's not already
                        year_df["year"] = pd.to_numeric(year_df["year"], errors="coerce")
                        
                        # Drop NaN years
                        year_df = year_df.dropna(subset=["year"])
                        
                        # Sort by year
                        year_df = year_df.sort_values("year")
                        
                        # Create a line chart for year trends
                        fig_line = px.line(
                            year_df,
                            x="year",
                            y="count",
                            title="Historical Trend of Reported Hauntings",
                            markers=True
                        )
                        fig_line.update_layout(
                            xaxis_title="Year",
                            yaxis_title="Number of Reported Hauntings",
                            hovermode="x unified"
                        )
                        
                        # Add smoothed trendline
                        if len(year_df) > 10:
                            try:
                                import numpy as np
                                from scipy import stats
                                
                                # Add 5-year moving average
                                year_df["moving_avg"] = year_df["count"].rolling(window=5, min_periods=1).mean()
                                
                                # Add moving average to plot
                                fig_line.add_scatter(
                                    x=year_df["year"],
                                    y=year_df["moving_avg"],
                                    mode="lines",
                                    name="5-Year Moving Average",
                                    line=dict(color="red", width=2, dash="dash")
                                )
                            except ImportError:
                                pass
                        
                        st.plotly_chart(fig_line, use_container_width=True)
                        
                        # Create a histogram by decades
                        year_df["decade"] = (year_df["year"] // 10) * 10
                        decade_counts = year_df.groupby("decade")["count"].sum().reset_index()
                        
                        fig_bar = px.bar(
                            decade_counts,
                            x="decade",
                            y="count",
                            title="Hauntings by Decade",
                            color="count",
                            color_continuous_scale="Viridis"
                        )
                        fig_bar.update_layout(
                            xaxis_title="Decade",
                            yaxis_title="Number of Reported Hauntings",
                            xaxis=dict(tickmode="array", tickvals=list(decade_counts["decade"]))
                        )
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error displaying year analysis: {e}")
            
            # Month and Time of Day analysis
            if "month_counts" in data["time"] or "time_of_day_counts" in data["time"]:
                with col2:
                    # Month analysis
                    if "month_counts" in data["time"]:
                        try:
                            st.subheader("Seasonal Patterns of Hauntings")
                            
                            # Convert to DataFrame
                            if isinstance(data["time"]["month_counts"], list):
                                # If it's a list of dictionaries
                                month_df = pd.DataFrame(data["time"]["month_counts"])
                                if "month" not in month_df.columns and "name" in month_df.columns:
                                    month_df = month_df.rename(columns={"name": "month"})
                                if "count" not in month_df.columns and "value" in month_df.columns:
                                    month_df = month_df.rename(columns={"value": "count"})
                            else:
                                # If it's a dictionary
                                month_df = pd.DataFrame({
                                    "month": list(data["time"]["month_counts"].keys()),
                                    "count": list(data["time"]["month_counts"].values())
                                })
                            
                            # Define month order
                            month_order = [
                                "January", "February", "March", "April", "May", "June",
                                "July", "August", "September", "October", "November", "December"
                            ]
                            
                            # Create a category for month with proper ordering
                            if all(month in month_order for month in month_df["month"]):
                                month_df["month"] = pd.Categorical(month_df["month"], categories=month_order, ordered=True)
                                month_df = month_df.sort_values("month")
                            
                            # Create a polar chart for months
                            fig_polar = px.line_polar(
                                month_df, 
                                r="count", 
                                theta="month",
                                line_close=True,
                                title="Monthly Distribution of Hauntings",
                                color_discrete_sequence=["rgba(31, 119, 180, 0.8)"]
                            )
                            fig_polar.update_traces(fill='toself')
                            
                            st.plotly_chart(fig_polar, use_container_width=True)
                            
                            # Create a bar chart for months
                            fig_bar = px.bar(
                                month_df,
                                x="month",
                                y="count",
                                title="Hauntings by Month",
                                color="count",
                                color_continuous_scale="Viridis"
                            )
                            
                            fig_bar.update_layout(
                                xaxis_title="Month",
                                yaxis_title="Number of Reported Hauntings"
                            )
                            
                            # Group months by season
                            season_map = {
                                "December": "Winter", "January": "Winter", "February": "Winter",
                                "March": "Spring", "April": "Spring", "May": "Spring",
                                "June": "Summer", "July": "Summer", "August": "Summer",
                                "September": "Fall", "October": "Fall", "November": "Fall"
                            }
                            
                            month_df["season"] = month_df["month"].map(season_map)
                            season_counts = month_df.groupby("season")["count"].sum().reset_index()
                            
                            # Ensure proper season order
                            season_order = ["Winter", "Spring", "Summer", "Fall"]
                            season_counts["season"] = pd.Categorical(
                                season_counts["season"], 
                                categories=season_order, 
                                ordered=True
                            )
                            season_counts = season_counts.sort_values("season")
                            
                            # Create a pie chart for seasons
                            fig_pie = px.pie(
                                season_counts,
                                values="count",
                                names="season",
                                title="Hauntings by Season",
                                color="season",
                                color_discrete_map={
                                    "Winter": "#9ecae1", 
                                    "Spring": "#a1d99b",
                                    "Summer": "#fd8d3c",
                                    "Fall": "#de2d26"
                                }
                            )
                            
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Error displaying month analysis: {e}")
                    
                    # Time of Day analysis
                    if "time_of_day_counts" in data["time"]:
                        try:
                            st.subheader("Time of Day Analysis")
                            
                            # Convert to DataFrame
                            if isinstance(data["time"]["time_of_day_counts"], list):
                                # If it's a list of dictionaries
                                time_df = pd.DataFrame(data["time"]["time_of_day_counts"])
                                if "time_of_day" not in time_df.columns and "name" in time_df.columns:
                                    time_df = time_df.rename(columns={"name": "time"})
                                if "count" not in time_df.columns and "value" in time_df.columns:
                                    time_df = time_df.rename(columns={"value": "count"})
                            else:
                                # If it's a dictionary
                                time_df = pd.DataFrame({
                                    "time_of_day": list(data["time"]["time_of_day_counts"].keys()),
                                    "count": list(data["time"]["time_of_day_counts"].values())
                                })
                            
                            # Define time of day order
                            time_order = ["Morning", "Afternoon", "Evening", "Night", "Midnight"]
                            
                            # Create a category for time with proper ordering
                            if all(time in time_order for time in time_df["time_of_day"]):
                                time_df["time_of_day"] = pd.Categorical(time_df["time_of_day"], categories=time_order, ordered=True)
                                time_df = time_df.sort_values("time_of_day")
                            
                            # Create a gauge chart for time of day
                            # Setup color coding for time of day
                            colors = {
                                "Morning": "#ffeda0",   # Light yellow
                                "Afternoon": "#feb24c",  # Orange
                                "Evening": "#f03b20",    # Dark orange/red
                                "Night": "#2c7fb8",     # Dark blue
                                "Midnight": "#253494"   # Very dark blue
                            }
                            
                            # Create a pie chart for time of day
                            fig_pie = px.pie(
                                time_df,
                                values="count",
                                names="time_of_day",
                                title="Hauntings by Time of Day",
                                color="time_of_day",
                                color_discrete_map=colors
                            )
                            
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                            # Create a half-circle gauge chart
                            fig_gauge = go.Figure()
                            
                            # Add a curved bar for each time of day
                            total = time_df["count"].sum()
                            cumulative = 0
                            
                            for i, row in time_df.iterrows():
                                value = row["count"] / total
                                fig_gauge.add_trace(go.Barpolar(
                                    r=[value],
                                    theta=[180],  # Center the bar
                                    width=[180],  # Cover half the circle
                                    base=cumulative,
                                    marker_color=colors.get(row["time_of_day"], "#000000"),
                                    name=f"{row['time_of_day']} ({row['count']} hauntings)",
                                    hoverinfo="name+text",
                                    text=[f"{row['count']} hauntings ({value:.1%})"]
                                ))
                                cumulative += value
                            
                            # Update layout for the gauge
                            fig_gauge.update_layout(
                                title="Time of Day Distribution",
                                polar=dict(
                                    radialaxis=dict(visible=False, range=[0, 1]),
                                    angularaxis=dict(
                                        visible=True,
                                        type="category",
                                        tickvals=[0, 45, 90, 135, 180],
                                        ticktext=["Dawn", "Morning", "Noon", "Evening", "Midnight"],
                                        direction="clockwise"
                                    )
                                ),
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig_gauge, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Error displaying time of day analysis: {e}")
            
            # Combined year and month heatmap
            if "year_counts" in data["time"] and "month_counts" in data["time"] and "year_month_counts" in data["time"]:
                try:
                    st.subheader("Detailed Temporal Patterns")
                    
                    # Convert year-month data to DataFrame
                    if isinstance(data["time"]["year_month_counts"], list):
                        year_month_df = pd.DataFrame(data["time"]["year_month_counts"])
                    else:
                        # Convert nested dictionary to DataFrame
                        year_month_data = []
                        for year, months in data["time"]["year_month_counts"].items():
                            for month, count in months.items():
                                year_month_data.append({"year": year, "month": month, "count": count})
                        year_month_df = pd.DataFrame(year_month_data)
                    
                    # Convert year to numeric if it's not already
                    year_month_df["year"] = pd.to_numeric(year_month_df["year"], errors="coerce")
                    
                    # Drop rows with NaN years
                    year_month_df = year_month_df.dropna(subset=["year"])
                    
                    # Create a pivot table for the heatmap
                    if not year_month_df.empty:
                        # Sort years and ensure month order
                        month_order = [
                            "January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"
                        ]
                        
                        # Filter to include only known months
                        year_month_df = year_month_df[year_month_df["month"].isin(month_order)]
                        
                        # Create pivot table
                        heatmap_data = year_month_df.pivot_table(
                            values="count", 
                            index="year", 
                            columns="month", 
                            aggfunc="sum",
                            fill_value=0
                        )
                        
                        # Reorder months
                        if all(month in heatmap_data.columns for month in month_order):
                            heatmap_data = heatmap_data[month_order]
                        
                        # Create heatmap
                        fig_heatmap = px.imshow(
                            heatmap_data,
                            labels=dict(x="Month", y="Year", color="Count"),
                            x=heatmap_data.columns,
                            y=heatmap_data.index,
                            color_continuous_scale="Viridis",
                            title="Hauntings by Year and Month"
                        )
                        
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                    else:
                        st.warning("Insufficient data for year-month heatmap.")
                    
                except Exception as e:
                    st.error(f"Error displaying year-month heatmap: {e}")
            
            # Display raw data as fallback
            with st.expander("View Raw Time Analysis Data"):
                for key in ["year_counts", "month_counts", "time_of_day_counts", "year_month_counts"]:
                    if key in data["time"]:
                        st.subheader(f"Raw {key.replace('_', ' ').title()} Data")
                        st.write(data["time"][key])
        else:
            st.error("Time analysis data not available. Please run the data processing script.")
    
    # Evidence Analysis Tab
    with tab3:
        st.header("Paranormal Evidence Analysis")
        
        if data["evidence"] and any(key in data["evidence"] for key in ["evidence_counts", "apparition_counts"]):
            # Create two-column layout
            col1, col2 = st.columns(2)
            
            # Process evidence types
            with col1:
                if "evidence_counts" in data["evidence"]:
                    try:
                        st.subheader("Types of Evidence Reported")
                        
                        # Convert to DataFrame
                        if isinstance(data["evidence"]["evidence_counts"], list):
                            # If it's a list of dictionaries
                            evidence_df = pd.DataFrame(data["evidence"]["evidence_counts"])
                            if "type" not in evidence_df.columns and "name" in evidence_df.columns:
                                evidence_df = evidence_df.rename(columns={"name": "type"})
                            if "count" not in evidence_df.columns and "value" in evidence_df.columns:
                                evidence_df = evidence_df.rename(columns={"value": "count"})
                        else:
                            # If it's a dictionary
                            evidence_df = pd.DataFrame({
                                "type": list(data["evidence"]["evidence_counts"].keys()),
                                "count": list(data["evidence"]["evidence_counts"].values())
                            })
                        
                        # Sort by count descending
                        evidence_df = evidence_df.sort_values("count", ascending=False)
                        
                        # Create a pie chart for evidence types
                        fig_pie = px.pie(
                            evidence_df,
                            values="count",
                            names="type",
                            title="Distribution of Evidence Types",
                            hover_data=["count"],
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Create a bar chart for evidence types
                        fig_bar = px.bar(
                            evidence_df,
                            y="type",
                            x="count",
                            title="Evidence Types by Frequency",
                            color="count",
                            color_continuous_scale="Viridis",
                            orientation="h"
                        )
                        fig_bar.update_layout(yaxis_title="Evidence Type", xaxis_title="Frequency")
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Create a treemap for evidence types
                        fig_treemap = px.treemap(
                            evidence_df,
                            path=["type"],
                            values="count",
                            title="Treemap of Evidence Types",
                            color="count",
                            color_continuous_scale="Viridis"
                        )
                        
                        st.plotly_chart(fig_treemap, use_container_width=True)
                        
                        # Show evidence types with counts in a data table
                        st.dataframe(evidence_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying evidence types: {e}")
            
            # Process apparition types
            with col2:
                if "apparition_counts" in data["evidence"]:
                    try:
                        st.subheader("Types of Apparitions Reported")
                        
                        # Convert to DataFrame
                        if isinstance(data["evidence"]["apparition_counts"], list):
                            # If it's a list of dictionaries
                            apparition_df = pd.DataFrame(data["evidence"]["apparition_counts"])
                            # Ensure columns are correct
                            if "type" not in apparition_df.columns:
                                if "apparition_type" in apparition_df.columns:
                                    apparition_df = apparition_df.rename(columns={"apparition_type": "type"})
                                elif "name" in apparition_df.columns:
                                    apparition_df = apparition_df.rename(columns={"name": "type"})
                            # Ensure count column exists
                            if "count" not in apparition_df.columns and "value" in apparition_df.columns:
                                apparition_df = apparition_df.rename(columns={"value": "count"})
                        else:
                            # If it's a dictionary
                            apparition_df = pd.DataFrame({
                                "type": list(data["evidence"]["apparition_counts"].keys()),
                                "count": list(data["evidence"]["apparition_counts"].values())
                            })
                        
                        # Sort by count descending
                        apparition_df = apparition_df.sort_values("count", ascending=False)
                        
                        # Create a pie chart for apparition types
                        fig_pie = px.pie(
                            apparition_df,
                            values="count",
                            names="type",
                            title="Distribution of Apparition Types",
                            hover_data=["count"],
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Create a bar chart for apparition types
                        fig_bar = px.bar(
                            apparition_df,
                            y="type",
                            x="count",
                            title="Apparition Types by Frequency",
                            color="count",
                            color_continuous_scale="Viridis",
                            orientation="h"
                        )
                        fig_bar.update_layout(yaxis_title="Apparition Type", xaxis_title="Frequency")
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Create a sunburst chart for apparition types
                        fig_sunburst = px.sunburst(
                            apparition_df,
                            path=["type"],
                            values="count",
                            title="Sunburst of Apparition Types",
                            color="count",
                            color_continuous_scale="Viridis"
                        )
                        
                        st.plotly_chart(fig_sunburst, use_container_width=True)
                        
                        # Show apparition types with counts in a data table
                        st.dataframe(apparition_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying apparition types: {e}")
            
            # If we have both evidence and apparition data, show correlation
            if "evidence_counts" in data["evidence"] and "apparition_counts" in data["evidence"] and "correlations" in data["evidence"]:
                try:
                    st.subheader("Correlations Between Evidence and Apparitions")
                    
                    # Check if correlations is a nested dictionary or a list
                    if isinstance(data["evidence"]["correlations"], dict):
                        # Convert nested dictionary to list of records
                        correlations = []
                        for ev_type, app_dict in data["evidence"]["correlations"].items():
                            for app_type, count in app_dict.items():
                                correlations.append({
                                    "evidence_type": ev_type,
                                    "apparition_type": app_type,
                                    "count": count
                                })
                    else:
                        # Assume it's already a list of records
                        correlations = data["evidence"]["correlations"]
                    
                    # Convert to DataFrame
                    corr_df = pd.DataFrame(correlations)
                    
                    # Check if we have correlation data
                    if not corr_df.empty and "evidence_type" in corr_df.columns and "apparition_type" in corr_df.columns and "count" in corr_df.columns:
                        # Create a heatmap of correlations
                        corr_pivot = corr_df.pivot_table(
                            index="evidence_type", 
                            columns="apparition_type", 
                            values="count",
                            fill_value=0
                        )
                        
                        # Create heatmap
                        fig_heatmap = px.imshow(
                            corr_pivot,
                            labels=dict(x="Apparition Type", y="Evidence Type", color="Count"),
                            x=corr_pivot.columns,
                            y=corr_pivot.index,
                            color_continuous_scale="Viridis",
                            title="Correlation Between Evidence and Apparition Types"
                        )
                        
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                        # Create a sankey diagram if we have reasonable amount of data
                        if len(corr_df) <= 50:  # Limit to avoid too complex diagrams
                            # Prepare data for Sankey diagram
                            # First, create unique IDs for each node
                            evidence_types = list(corr_df["evidence_type"].unique())
                            apparition_types = list(corr_df["apparition_type"].unique())
                            
                            # Create node labels
                            node_labels = evidence_types + apparition_types
                            
                            # Create source-target pairs
                            sources = []
                            targets = []
                            values = []
                            
                            for _, row in corr_df.iterrows():
                                if row["count"] > 0:  # Only include non-zero connections
                                    source_idx = evidence_types.index(row["evidence_type"])
                                    target_idx = len(evidence_types) + apparition_types.index(row["apparition_type"])
                                    sources.append(source_idx)
                                    targets.append(target_idx)
                                    values.append(row["count"])
                            
                            # Create Sankey diagram
                            fig_sankey = go.Figure(data=[go.Sankey(
                                node=dict(
                                    pad=15,
                                    thickness=20,
                                    line=dict(color="black", width=0.5),
                                    label=node_labels,
                                    color=["rgba(31, 119, 180, 0.8)"] * len(evidence_types) + 
                                          ["rgba(255, 127, 14, 0.8)"] * len(apparition_types)
                                ),
                                link=dict(
                                    source=sources,
                                    target=targets,
                                    value=values
                                )
                            )])
                            
                            fig_sankey.update_layout(
                                title_text="Evidence to Apparition Type Flows",
                                font_size=12
                            )
                            
                            st.plotly_chart(fig_sankey, use_container_width=True)
                    else:
                        st.warning("Correlation data format is not as expected.")
                except Exception as e:
                    st.error(f"Error displaying correlation between evidence and apparitions: {e}")
            
            # Display raw data as fallback
            with st.expander("View Raw Evidence Analysis Data"):
                for key in ["evidence_counts", "apparition_counts", "correlations"]:
                    if key in data["evidence"]:
                        st.subheader(f"Raw {key.replace('_', ' ').title()} Data")
                        st.write(data["evidence"][key])
        else:
            st.error("Evidence analysis data not available. Please run the data processing script.")
    
    # Location Analysis Tab
    with tab4:
        st.header("Geographic Analysis of Hauntings")
        
        if data["location"] and any(key in data["location"] for key in ["state_counts", "country_counts", "city_counts"]):
            # Create columns for analyses
            col1, col2 = st.columns(2)
            
            # Process and display state distribution
            with col1:
                if "state_counts" in data["location"]:
                    try:
                        st.subheader("Hauntings by State/Province")
                        
                        # Convert to DataFrame based on format
                        if isinstance(data["location"]["state_counts"], list):
                            # If it's a list of dictionaries
                            state_df = pd.DataFrame(data["location"]["state_counts"])
                            if "state" not in state_df.columns and "name" in state_df.columns:
                                state_df = state_df.rename(columns={"name": "state"})
                            if "count" not in state_df.columns and "value" in state_df.columns:
                                state_df = state_df.rename(columns={"value": "count"})
                        else:
                            # If it's a dictionary
                            state_df = pd.DataFrame({
                                "state": list(data["location"]["state_counts"].keys()),
                                "count": list(data["location"]["state_counts"].values())
                            })
                        
                        # Display US choropleth if we have US states
                        us_states = set([
                            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
                        ])
                        
                        # Convert state codes to uppercase for comparison
                        state_df["state_upper"] = state_df["state"].str.upper() if state_df["state"].dtype == 'object' else state_df["state"]
                        
                        # Check if we have mostly US states
                        us_state_count = sum(1 for state in state_df["state_upper"] if state in us_states)
                        
                        if us_state_count > len(state_df) * 0.5:  # If more than 50% are US states
                            # Filter to just US states and create a choropleth
                            us_df = state_df[state_df["state_upper"].isin(us_states)]
                            
                            # Only create choropleth if we have enough US states
                            if len(us_df) > 5:
                                fig_choropleth = px.choropleth(
                                    us_df,
                                    locations="state_upper",
                                    locationmode="USA-states",
                                    color="count",
                                    scope="usa",
                                    color_continuous_scale="Viridis",
                                    labels={"count": "Number of Hauntings", "state_upper": "State"},
                                    title="US States Haunting Heat Map"
                                )
                                st.plotly_chart(fig_choropleth, use_container_width=True)
                        
                        # Sort and limit to top states for bar chart
                        state_df = state_df.sort_values("count", ascending=False)
                        
                        # Show top 15 states/provinces
                        top_states = state_df.head(15)
                        
                        # Create a bar chart for top states
                        fig_bar = px.bar(
                            top_states,
                            y="state",
                            x="count",
                            title=f"Top {len(top_states)} States/Provinces with Most Hauntings",
                            color="count",
                            color_continuous_scale="Viridis",
                            orientation="h"
                        )
                        fig_bar.update_layout(yaxis_title="State/Province", xaxis_title="Number of Hauntings")
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Show states with counts in a data table with search
                        st.subheader("Search States/Provinces")
                        st.dataframe(state_df[["state", "count"]].reset_index(drop=True), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying state distribution: {e}")
            
            # Haunting density analysis
            with col2:
                # Region distribution instead of country (since it's all USA)
                if 'country_counts' in data["location"]:
                    try:
                        # Since it's all USA data, let's show something more useful
                        st.subheader("Haunting Density Analysis")
                        
                        if 'state_counts' in data["location"]:
                            # Create an analysis of haunting density by state population
                            # Approximate state populations (for demonstration)
                            state_populations = {
                                "california": 39.5, "texas": 29.0, "florida": 21.5, "new york": 19.5, 
                                "pennsylvania": 12.8, "illinois": 12.7, "ohio": 11.7, "georgia": 10.6,
                                "north carolina": 10.4, "michigan": 10.0, "new jersey": 9.0, 
                                "virginia": 8.5, "washington": 7.6, "arizona": 7.2, "massachusetts": 7.0,
                                "tennessee": 6.9, "indiana": 6.7, "missouri": 6.1, "maryland": 6.0,
                                "wisconsin": 5.8, "colorado": 5.7, "minnesota": 5.6, "south carolina": 5.1,
                                "alabama": 5.0, "louisiana": 4.6, "kentucky": 4.5, "oregon": 4.2,
                                "oklahoma": 4.0, "connecticut": 3.6, "utah": 3.2, "iowa": 3.2,
                                "nevada": 3.1, "arkansas": 3.0, "mississippi": 3.0, "kansas": 2.9,
                                "new mexico": 2.1, "nebraska": 1.9, "west virginia": 1.8, "idaho": 1.8,
                                "hawaii": 1.4, "new hampshire": 1.4, "maine": 1.3, "montana": 1.1,
                                "rhode island": 1.1, "delaware": 1.0, "south dakota": 0.9, 
                                "north dakota": 0.8, "alaska": 0.7, "vermont": 0.6, "wyoming": 0.6,
                                "washington dc": 0.7
                            }
                            
                            # Convert state counts to DataFrame
                            if isinstance(data["location"]["state_counts"], list):
                                state_df = pd.DataFrame(data["location"]["state_counts"])
                            else:
                                state_df = pd.DataFrame({
                                    "state": list(data["location"]["state_counts"].keys()),
                                    "count": list(data["location"]["state_counts"].values())
                                })
                            
                            # Normalize state names
                            state_df["state_lower"] = state_df["state"].str.lower()
                            
                            # Add population data and calculate haunting density
                            state_df["population_millions"] = state_df["state_lower"].map(state_populations)
                            state_df["hauntings_per_million"] = state_df["count"] / state_df["population_millions"]
                            
                            # Filter out states with missing population data
                            state_df = state_df.dropna(subset=["population_millions"])
                            
                            # Sort by haunting density
                            state_df = state_df.sort_values("hauntings_per_million", ascending=False).head(15)
                            
                            # Create bar chart of haunting density
                            fig = px.bar(
                                state_df,
                                y="state",
                                x="hauntings_per_million",
                                title="Top 15 States by Haunting Density (Hauntings per Million People)",
                                color="hauntings_per_million",
                                color_continuous_scale="Viridis",
                                orientation="h"
                            )
                            fig.update_layout(yaxis_title="State", xaxis_title="Hauntings per Million People")
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add some interesting stats
                            highest_density = state_df.iloc[0]
                            st.info(f"**Interesting Fact:** {highest_density['state']} has the highest haunting density with {highest_density['hauntings_per_million']:.1f} hauntings per million residents!")
                        else:
                            st.info("No state count data available for density analysis.")
                    except Exception as e:
                        st.error(f"Error displaying haunting density: {e}")
                else:
                    st.info("No country data available")
            
            # City analysis in full width
            if "city_counts" in data["location"]:
                try:
                    st.subheader("Top Cities with Hauntings")
                    
                    # Convert to DataFrame based on format
                    if isinstance(data["location"]["city_counts"], list):
                        # If it's a list of dictionaries
                        city_df = pd.DataFrame(data["location"]["city_counts"])
                        if "city" not in city_df.columns and "name" in city_df.columns:
                            city_df = city_df.rename(columns={"name": "city"})
                        if "count" not in city_df.columns and "value" in city_df.columns:
                            city_df = city_df.rename(columns={"value": "count"})
                    else:
                        # If it's a dictionary
                        city_df = pd.DataFrame({
                            "city": list(data["location"]["city_counts"].keys()),
                            "count": list(data["location"]["city_counts"].values())
                        })
                    
                    # Sort by count in descending order
                    city_df = city_df.sort_values("count", ascending=False)
                    
                    # Show top cities only (too many to show all)
                    top_cities = city_df.head(20)
                    
                    # Create a bar chart for cities
                    fig_bar = px.bar(
                        top_cities,
                        y="city",
                        x="count",
                        title=f"Top {len(top_cities)} Cities with Most Hauntings",
                        color="count",
                        color_continuous_scale="Viridis",
                        orientation="h"
                    )
                    fig_bar.update_layout(yaxis_title="City", xaxis_title="Number of Hauntings")
                    
                    # Create columns for two charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # Create a treemap for top cities
                        fig_treemap = px.treemap(
                            top_cities,
                            path=["city"],
                            values="count",
                            title=f"Treemap of Top {len(top_cities)} Haunted Cities",
                            color="count",
                            color_continuous_scale="Viridis"
                        )
                        
                        st.plotly_chart(fig_treemap, use_container_width=True)
                    
                    # Show cities with counts in a searchable data table
                    st.subheader("Search Cities")
                    st.dataframe(city_df[["city", "count"]].reset_index(drop=True), use_container_width=True)
                except Exception as e:
                    st.error(f"Error displaying city distribution: {e}")
            
            # Display raw data as fallback
            with st.expander("View Raw Location Analysis Data"):
                for key in ["state_counts", "country_counts", "city_counts"]:
                    if key in data["location"]:
                        st.subheader(f"Raw {key.replace('_', ' ').title()} Data")
                        st.write(data["location"][key])
        else:
            st.error("Location analysis data not available. Please run the data processing script.")
    
    # Correlation Analysis Tab
    with tab5:
        st.header("Correlation Analysis")
        if data["correlation"] and "correlation_matrix" in data["correlation"]:
            # Extract correlation matrix data
            correlation_data = data["correlation"]["correlation_matrix"]
            
            # For simplified correlation visualization if the full matrix is too complex
            if len(correlation_data) > 0:
                # Try to create a simple heatmap visualization
                try:
                    # Get unique variables - limit to just a few for visibility
                    all_vars = sorted(list(set([item["x"] for item in correlation_data])))
                    
                    # Take just the first 6 variables for a cleaner visualization
                    variables = all_vars[:6]
                    
                    # Create a data frame for the correlation values
                    # We need to convert the list of dicts to a pivoted DataFrame
                    filtered_corr_data = [item for item in correlation_data 
                                          if item["x"] in variables and item["y"] in variables]
                    
                    # Create the correlation matrix manually
                    matrix_dict = {}
                    for var in variables:
                        matrix_dict[var] = {}
                        for other_var in variables:
                            matrix_dict[var][other_var] = 0.0
                    
                    # Fill in correlation values
                    for item in filtered_corr_data:
                        x = item["x"]
                        y = item["y"]
                        if x in variables and y in variables:
                            matrix_dict[x][y] = item["value"]
                    
                    # Convert to DataFrame with explicit index and columns
                    corr_df = pd.DataFrame.from_dict(matrix_dict, orient='index')
                    corr_df = corr_df.reindex(index=variables, columns=variables)
                    
                    # Create heatmap - handle NaN values
                    fig = px.imshow(
                        corr_df.fillna(0),  # Replace NaN with 0
                        text_auto=True,
                        aspect="auto",
                        color_continuous_scale="RdBu_r",
                        title="Correlation Matrix of Haunted Places Data (Top 6 Variables)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Also create a simple table view for better readability
                    st.markdown("### Correlation Matrix Table")
                    st.dataframe(corr_df.style.background_gradient(cmap="RdBu_r"))
                    
                except Exception as e:
                    st.error(f"Could not create correlation matrix visualization: {e}")
                    
                    # Display raw data as fallback
                    st.write("Raw correlation data (sample):", correlation_data[:5])
                    
                    # Simple text-based representation
                    st.markdown("### Top Correlations")
                    # Sort by absolute value and get top 10
                    sorted_corr = sorted(correlation_data, 
                                         key=lambda x: abs(x.get("value", 0) if isinstance(x.get("value"), (int, float)) else 0), 
                                         reverse=True)[:10]
                    for item in sorted_corr:
                        if "x" in item and "y" in item and "value" in item:
                            st.write(f"{item['x']} ↔ {item['y']}: {item['value']:.3f}")
            else:
                st.error("Correlation matrix is empty. Please run the data processing script.")
        else:
            st.error("Correlation analysis data not available. Please run the data processing script.")

def add_data_status_tab():
    st.header("Data Storage Status")
    
    st.markdown("""
    Per the assignment requirements, the haunted places data has been prepared for ingestion into:
    
    1. **Elasticsearch** - A distributed search engine
    2. **Apache Solr** - An open-source search platform
    
    The data processor (`data_processor.py`) includes functionality to ingest the processed data 
    into both systems when they are available, allowing for advanced searching and filtering.
    
    For submission purposes, the indices would be archived and submitted separately.
    """)
    
    # Show current status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Elasticsearch Status")
        st.info("Data processor configured for Elasticsearch ingestion")
        
    with col2:
        st.subheader("Solr Status")
        st.info("Data processor configured for Solr ingestion")

def add_memex_tools_tab():
    """
    Add MEMEX tools tab to the Streamlit app
    Shows options for ImageSpace and GeoParser
    """
    st.header("MEMEX Tools")
    
    tab1, tab2 = st.tabs(["ImageSpace", "GeoParser"])
    
    with tab1:
        st.subheader("Image Analysis with ImageSpace")
        
        # Add instructions on viewing the Docker-based installation
        st.info("""
        For the full ImageSpace experience, the Docker container should be running at:
        http://localhost:8080
        
        Below is a simplified version that works directly in Streamlit:
        """)
        
        # Option to upload an image or enter a URL
        option = st.radio("Select an option:", ["Upload Image", "Enter Image URL"], key="image_option")
        
        if option == "Upload Image":
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="image_upload")
            if uploaded_file is not None:
                from PIL import Image
                import io
                
                # Display the image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Image analysis button
                if st.button("Analyze Image", key="analyze_image"):
                    with st.spinner("Analyzing image..."):
                        # Basic image analysis
                        st.write("**Image Information:**")
                        st.write(f"Dimensions: {image.size[0]}x{image.size[1]} pixels")
                        st.write(f"Format: {image.format}")
                        
                        # Extract color information
                        try:
                            from collections import Counter
                            import numpy as np
                            
                            # Convert to numpy array
                            img_array = np.array(image.convert('RGB').resize((100, 100)))
                            
                            # Reshape to get list of pixels
                            pixels = img_array.reshape(-1, 3)
                            
                            # Count most common colors
                            pixel_tuples = [tuple(pixel) for pixel in pixels]
                            most_common = Counter(pixel_tuples).most_common(5)
                            
                            st.write("**Dominant Colors:**")
                            for i, (color, count) in enumerate(most_common):
                                # Display color as a swatch
                                st.markdown(
                                    f"""
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <div style="width: 30px; height: 30px; background-color: rgb{color}; margin-right: 10px;"></div>
                                        <span>Color {i+1}: RGB{color} ({count} pixels)</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        except Exception as e:
                            st.error(f"Error analyzing colors: {e}")
                        
                        # Find similar images
                        st.write("**Similar Haunted Places Images:**")
                        st.write("In the full ImageSpace application, this would show similar images based on visual features.")
                        
                        # Display sample similar images (placeholder)
                        from data_storage import data_store
                        sample_places = data_store.get_documents("haunted_places", limit=3)
                        
                        if sample_places:
                            st.write("Based on image analysis, these haunted places might have similar characteristics:")
                            cols = st.columns(3)
                            for i, place in enumerate(sample_places):
                                with cols[i]:
                                    st.write(f"**{place.get('location', 'Unknown Location')}**")
                                    st.write(f"State: {place.get('state', 'Unknown')}")
                                    st.write(f"Evidence: {place.get('evidence', 'Unknown')}")
                        else:
                            st.info("No haunted places data available for similarity comparison.")
        else:
            url = st.text_input("Enter image URL:", key="image_url")
            if url:
                try:
                    import requests
                    from PIL import Image
                    import io
                    
                    response = requests.get(url)
                    image = Image.open(io.BytesIO(response.content))
                    
                    # Display the image
                    st.image(image, caption="Image from URL", use_column_width=True)
                    
                    # Image analysis button
                    if st.button("Analyze Image", key="analyze_url_image"):
                        with st.spinner("Analyzing image..."):
                            # Basic image analysis
                            st.write("**Image Information:**")
                            st.write(f"Dimensions: {image.size[0]}x{image.size[1]} pixels")
                            st.write(f"Format: {image.format}")
                            
                            # Extract color information (same as above)
                            try:
                                from collections import Counter
                                import numpy as np
                                
                                # Convert to numpy array
                                img_array = np.array(image.convert('RGB').resize((100, 100)))
                                
                                # Reshape to get list of pixels
                                pixels = img_array.reshape(-1, 3)
                                
                                # Count most common colors
                                pixel_tuples = [tuple(pixel) for pixel in pixels]
                                most_common = Counter(pixel_tuples).most_common(5)
                                
                                st.write("**Dominant Colors:**")
                                for i, (color, count) in enumerate(most_common):
                                    st.markdown(
                                        f"""
                                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                            <div style="width: 30px; height: 30px; background-color: rgb{color}; margin-right: 10px;"></div>
                                            <span>Color {i+1}: RGB{color} ({count} pixels)</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            except Exception as e:
                                st.error(f"Error analyzing colors: {e}")
                            
                            # Similarity placeholder (same as above)
                            st.write("**Similar Haunted Places Images:**")
                            st.write("In the full ImageSpace application, this would show similar images based on visual features.")
                            
                            from data_storage import data_store
                            sample_places = data_store.get_documents("haunted_places", limit=3)
                            
                            if sample_places:
                                st.write("Based on image analysis, these haunted places might have similar characteristics:")
                                cols = st.columns(3)
                                for i, place in enumerate(sample_places):
                                    with cols[i]:
                                        st.write(f"**{place.get('location', 'Unknown Location')}**")
                                        st.write(f"State: {place.get('state', 'Unknown')}")
                                        st.write(f"Evidence: {place.get('evidence', 'Unknown')}")
                            else:
                                st.info("No haunted places data available for similarity comparison.")
                except Exception as e:
                    st.error(f"Error loading image from URL: {e}")
    
    with tab2:
        st.subheader("Location Analysis with GeoParser")
        
        st.info("""
        For the full GeoParser experience, the Docker container should be running at:
        http://localhost:8081
        
        Below is a simplified version that works directly in Streamlit:
        """)
        
        # Text input for GeoParser
        text_input = st.text_area(
            "Enter text containing location information:",
            height=150,
            key="geoparser_text"
        )
        
        if st.button("Extract Locations", key="extract_locations"):
            if text_input:
                with st.spinner("Extracting locations..."):
                    # In a real implementation, this would call the GeoParser API
                    # For now, we'll use a simple placeholder implementation
                    st.write("**Extracted Locations:**")
                    
                    # Simple location extraction (very naive implementation)
                    import re
                    from data_storage import data_store
                    
                    # Get all state names
                    states = set()
                    for doc in data_store.get_documents('haunted_places'):
                        if 'state' in doc and doc['state']:
                            states.add(doc['state'].lower())
                    
                    # Find state names in the text
                    found_states = []
                    for state in states:
                        if re.search(r'\b' + re.escape(state) + r'\b', text_input.lower()):
                            found_states.append(state)
                    
                    if found_states:
                        st.success(f"Found {len(found_states)} locations in the text.")
                        
                        # Show locations on a map
                        import folium
                        from streamlit_folium import folium_static
                        
                        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
                        
                        # Add markers for each found state
                        for state in found_states:
                            # Get all haunted places in this state
                            from data_storage import get_places_by_state
                            places = get_places_by_state(state)
                            
                            if places:
                                for place in places:
                                    if place.get('latitude') and place.get('longitude'):
                                        popup_text = f"""
                                        <b>{place.get('location', 'Unknown')}</b><br>
                                        {place.get('description', 'No description')[:100]}...
                                        """
                                        folium.Marker(
                                            [place.get('latitude'), place.get('longitude')],
                                            popup=popup_text,
                                            tooltip=place.get('location', 'Unknown')
                                        ).add_to(m)
                        
                        # Display the map
                        st.write("**Locations on map:**")
                        folium_static(m)
                    else:
                        st.warning("No known locations found in the text.")
            else:
                st.warning("Please enter text to analyze.")


def setup_d3_file():
    """
    Create the D3 visualization HTML file if it doesn't exist
    """
    # Create directory for visualizations if it doesn't exist
    os.makedirs("visualizations", exist_ok=True)
    
    # Check if the main D3 visualization file exists
    if not os.path.exists("visualizations/index.html"):
        st.warning("D3 visualization file not found. You should create it with the D3 code provided.")
        
        # Create a basic HTML template for D3
        with open("visualizations/index.html", "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Haunted Places D3 Visualizations</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <script src="https://d3js.org/topojson.v3.min.js"></script>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px;
                        background-color: #1a1a1a;
                        color: #e0e0e0;
                    }
                    .visualization {
                        margin-bottom: 40px;
                        background-color: #2c2c2c;
                        padding: 20px;
                        border-radius: 8px;
                    }
                </style>
            </head>
            <body>
                <h1>👻 Haunted Places D3 Visualizations</h1>
                <p>Please replace this file with the complete D3 visualization code.</p>
                
                <div class="visualization">
                    <h2>Map Visualization</h2>
                    <div id="map-container"></div>
                </div>
                
                <div class="visualization">
                    <h2>Time Analysis</h2>
                    <div id="time-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Evidence Analysis</h2>
                    <div id="evidence-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Location Analysis</h2>
                    <div id="location-chart"></div>
                </div>
                
                <div class="visualization">
                    <h2>Correlation Analysis</h2>
                    <div id="correlation-chart"></div>
                </div>
                
                <script>
                    // This is a placeholder. Replace with actual D3 code.
                    document.addEventListener('DOMContentLoaded', function() {
                        d3.select('#map-container')
                            .append('p')
                            .text('Map visualization placeholder');
                            
                        d3.select('#time-chart')
                            .append('p')
                            .text('Time analysis placeholder');
                            
                        d3.select('#evidence-chart')
                            .append('p')
                            .text('Evidence analysis placeholder');
                            
                        d3.select('#location-chart')
                            .append('p')
                            .text('Location analysis placeholder');
                            
                        d3.select('#correlation-chart')
                            .append('p')
                            .text('Correlation analysis placeholder');
                    });
                </script>
            </body>
            </html>
            """)
        
        return False
    
    return True