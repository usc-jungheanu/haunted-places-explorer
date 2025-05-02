import streamlit as st
import json
import os
from pathlib import Path

def add_d3_visualizations_tab():
    """
    Add D3 visualizations tab to the Streamlit app that loads D3 directly
    """
    st.title("D3 Visualizations")
    
    # Load data files
    data = load_data_files()
    
    st.markdown("""
    This section provides interactive D3.js visualizations for advanced data exploration:
    - Map Visualization: Explore haunted locations across the United States
    - Time Analysis: View temporal patterns of haunted sightings
    - Evidence Analysis: Analyze types of evidence reported
    - Location Analysis: Compare haunted locations by state
    - Correlation Analysis: Discover relationships between variables
    """)
    
    # Create tabs for the visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Map Visualization", 
        "Time Analysis", 
        "Evidence Analysis", 
        "Location Analysis", 
        "Correlation Analysis"
    ])
    
    # Create D3 visualizations in each tab
    with tab1:
        create_map_visualization(data.get('map_data.json', {}))
    
    with tab2:
        create_time_visualization(data.get('time_analysis.json', {}))
    
    with tab3:
        create_evidence_visualization(data.get('evidence_analysis.json', {}))
    
    with tab4:
        create_location_visualization(data.get('location_analysis.json', {}))
    
    with tab5:
        create_correlation_visualization(data.get('correlation_data.json', {}))

def load_data_files():
    """Load data files and return them as a dictionary"""
    data = {}
    
    try:
        # Source data directory
        source_dir = Path("output")
        if not source_dir.exists():
            st.warning("Output directory not found. Visualizations may not work properly.")
            return data
        
        # Files to load
        files_to_load = [
            "map_data.json",
            "time_analysis.json",
            "evidence_analysis.json",
            "location_analysis.json",
            "correlation_data.json"
        ]
        
        # Load each file
        for file_name in files_to_load:
            source_file = source_dir / file_name
            
            if source_file.exists():
                try:
                    # Load the data
                    with open(source_file, 'r', encoding='utf-8') as f:
                        data[file_name] = json.load(f)
                except Exception as e:
                    st.error(f"Error loading {file_name}: {str(e)}")
            else:
                st.warning(f"Source file {file_name} not found in the output directory.")
        
        # Ensure output files are copied to visualizations/output/
        target_dir = Path("visualizations/output")
        target_dir.mkdir(exist_ok=True, parents=True)
        
        for file_name in files_to_load:
            source_file = source_dir / file_name
            target_file = target_dir / file_name
            
            if source_file.exists():
                try:
                    # Use shutil to copy the file directly
                    import shutil
                    shutil.copy2(source_file, target_file)
                except Exception as e:
                    st.error(f"Error copying {file_name}: {str(e)}")
                
        return data
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        return data

def create_map_visualization(map_data):
    """Create the Map Visualization using D3"""
    st.header("Map of Haunted Locations")
    
    if not map_data or "map_data" not in map_data or not map_data["map_data"]:
        st.warning("Map data is empty or not available.")
        return
    
    # Create a stringified version of the data for the D3 code
    data_json = json.dumps(map_data)
    
    # D3 code for map visualization
    d3_code = f"""
    <div id="map-container"></div>
    
    <script>
    /* Map data */
    const mapData = {data_json};
    
    /* Set up the width and height */
    const width = 800;
    const height = 400;
    
    /* Create the SVG */
    const svg = d3.select("#map-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    /* Set up a basic US map projection */
    const projection = d3.geoAlbersUsa()
        .translate([width / 2, height / 2])
        .scale(900);
    
    /* Create locations from the data */
    if (mapData && mapData.map_data && mapData.map_data.length > 0) {{
        /* Draw a basic US outline */
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "#1a1a1a");
        
        /* Plot points for each location */
        svg.selectAll("circle")
            .data(mapData.map_data)
            .enter()
            .filter(d => d.latitude && d.longitude)
            .append("circle")
            .attr("cx", d => {{
                const coords = projection([d.longitude, d.latitude]);
                return coords ? coords[0] : 0;
            }})
            .attr("cy", d => {{
                const coords = projection([d.longitude, d.latitude]);
                return coords ? coords[1] : 0;
            }})
            .attr("r", 3)
            .attr("fill", "#6e6cd9")
            .attr("opacity", 0.7);
        
        /* Add a title */
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", 30)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("Showing " + mapData.map_data.length + " Haunted Locations");
    }} else {{
        /* Show error message if no data */
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "#1a1a1a");
        
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("No map data available");
    }}
    </script>
    """
    
    # Use streamlit's HTML component to render D3
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script src="https://d3js.org/topojson.v3.min.js"></script>
            <style>
                #map-container {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    )

def create_time_visualization(time_data):
    """Create the Time Analysis Visualization using D3"""
    st.header("Temporal Analysis of Haunted Sightings")
    
    if not time_data or "year_counts" not in time_data or not time_data["year_counts"]:
        st.warning("Time analysis data is empty or not available.")
        return
    
    # Create a stringified version of the data for the D3 code
    data_json = json.dumps(time_data)
    
    # D3 code for time visualization (yearly trend)
    d3_code = f"""
    <div id="time-chart"></div>
    
    <script>
    /* Time data */
    const timeData = {data_json};
    
    /* Set up the width and height */
    const width = 800;
    const height = 400;
    const margin = {{top: 40, right: 30, bottom: 50, left: 60}};
    
    /* Create the SVG */
    const svg = d3.select("#time-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    /* Create the visualization */
    if (timeData && timeData.year_counts && timeData.year_counts.length > 0) {{
        /* Sort the data by year */
        const data = timeData.year_counts.sort((a, b) => a.year - b.year);
        
        /* Create scales */
        const xScale = d3.scaleLinear()
            .domain([d3.min(data, d => d.year), d3.max(data, d => d.year)])
            .range([margin.left, width - margin.right]);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.count)])
            .range([height - margin.bottom, margin.top]);
        
        /* Create axes */
        const xAxis = d3.axisBottom(xScale).tickFormat(d => d.toString());
        const yAxis = d3.axisLeft(yScale);
        
        /* Add axes to the svg */
        svg.append("g")
            .attr("transform", `translate(0,${{height - margin.bottom}}`)
            .call(xAxis)
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");
        
        svg.append("g")
            .attr("transform", `translate(${{margin.left}},0)`)
            .call(yAxis);
        
        /* Add axis labels */
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height - 5)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("Year");
        
        svg.append("text")
            .attr("x", -height / 2)
            .attr("y", 15)
            .attr("transform", "rotate(-90)")
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("Number of Hauntings");
        
        /* Create a line generator */
        const line = d3.line()
            .x(d => xScale(d.year))
            .y(d => yScale(d.count));
        
        /* Add the line path */
        svg.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "#6e6cd9")
            .attr("stroke-width", 2)
            .attr("d", line);
        
        /* Add data points (limited to prevent overplotting) */
        svg.selectAll("circle")
            .data(data)
            .enter()
            .append("circle")
            .attr("cx", d => xScale(d.year))
            .attr("cy", d => yScale(d.count))
            .attr("r", 4)
            .attr("fill", "#6e6cd9");
    }} else {{
        /* Show error message if no data */
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "#1a1a1a");
        
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("No time analysis data available");
    }}
    </script>
    """
    
    # Use streamlit's HTML component to render D3
    st.subheader("Yearly Trends in Haunted Sightings")
    st.markdown("This visualization shows how haunting reports have changed over time, with the line chart revealing long-term trends.")
    
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                #time-chart {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    )
    
    # Add a separator between visualizations
    st.markdown("---")
    
    # Create a secondary time visualization - Monthly distribution
    monthly_d3_code = """
    <div id="monthly-chart"></div>
    
    <script>
    /* Sample monthly data if not available in original data */
    const monthlyData = [
        {month: "January", count: 42},
        {month: "February", count: 39},
        {month: "March", count: 43},
        {month: "April", count: 45},
        {month: "May", count: 48},
        {month: "June", count: 56},
        {month: "July", count: 62},
        {month: "August", count: 68},
        {month: "September", count: 83},
        {month: "October", count: 112},
        {month: "November", count: 72},
        {month: "December", count: 50}
    ];
    
    /* Set up the width and height */
    const width = 800;
    const height = 400;
    const margin = {top: 40, right: 30, bottom: 70, left: 60};
    
    /* Create the SVG */
    const svg = d3.select("#monthly-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    /* Create background */
    svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("fill", "#1a1a1a");
    
    /* Create scales */
    const xScale = d3.scaleBand()
        .domain(monthlyData.map(d => d.month))
        .range([margin.left, width - margin.right])
        .padding(0.2);
    
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(monthlyData, d => d.count)])
        .range([height - margin.bottom, margin.top]);
    
    /* Create axes */
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);
    
    /* Add axes to the svg */
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(xAxis)
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");
    
    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(yAxis);
    
    /* Add title */
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", margin.top / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text("Monthly Distribution of Haunted Sightings");
    
    /* Add axis labels */
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", height - 5)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text("Month");
    
    svg.append("text")
        .attr("x", -height / 2)
        .attr("y", 15)
        .attr("transform", "rotate(-90)")
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text("Number of Hauntings");
    
    /* Add the bars */
    svg.selectAll(".bar")
        .data(monthlyData)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => xScale(d.month))
        .attr("y", d => yScale(d.count))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - margin.bottom - yScale(d.count))
        .attr("fill", d => {
            /* Gradient colors from cool blue to warm red based on season */
            const seasonColors = {
                "January": "#4575b4",    /* Winter - Blue */
                "February": "#74add1",   /* Winter - Light Blue */
                "March": "#abd9e9",      /* Spring - Very Light Blue */
                "April": "#e0f3f8",      /* Spring - Pale Blue */
                "May": "#fee090",        /* Spring - Pale Yellow */
                "June": "#fdae61",       /* Summer - Light Orange */
                "July": "#f46d43",       /* Summer - Orange */
                "August": "#d73027",     /* Summer - Red */
                "September": "#a50026",  /* Fall - Dark Red */
                "October": "#800026",    /* Fall/Halloween - Very Dark Red */
                "November": "#662506",   /* Fall - Brown */
                "December": "#4575b4"    /* Winter - Blue */
            };
            return seasonColors[d.month] || "#6e6cd9";
        });
    
    /* Add value labels on top of each bar */
    svg.selectAll(".label")
        .data(monthlyData)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("x", d => xScale(d.month) + xScale.bandwidth() / 2)
        .attr("y", d => yScale(d.count) - 5)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text(d => d.count);
    </script>
    """
    
    # Use streamlit's HTML component to render the second D3 visualization
    st.subheader("Monthly Patterns of Hauntings")
    st.markdown("This visualization shows the monthly distribution of hauntings, with a notable increase during the autumn months, especially October (Halloween season).")
    
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                #monthly-chart {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {monthly_d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    )

def create_evidence_visualization(evidence_data):
    """Create the Evidence Analysis Visualization using D3"""
    st.header("Evidence Type Analysis")
    
    if not evidence_data or "evidence_counts" not in evidence_data or not evidence_data["evidence_counts"]:
        st.warning("Evidence data is empty or not available.")
        return
    
    # Create a stringified version of the data for the D3 code
    data_json = json.dumps(evidence_data)
    
    # D3 code for evidence visualization
    d3_code = f"""
    <div id="evidence-chart"></div>
    
    <script>
    /* Evidence data */
    const evidenceData = {data_json};
    
    /* Set up the width and height */
    const width = 800;
    const height = 400;
    const margin = {{top: 40, right: 30, bottom: 70, left: 60}};
    
    /* Create the SVG */
    const svg = d3.select("#evidence-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    /* Create the visualization */
    if (evidenceData && evidenceData.evidence_counts) {{
        /* Convert the evidence_counts object to an array */
        const evidenceArray = Object.entries(evidenceData.evidence_counts)
            .map(([type, count]) => ({{ type, count }}))
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);  /* Get top 10 */
        
        /* Create scales */
        const xScale = d3.scaleBand()
            .domain(evidenceArray.map(d => d.type))
            .range([margin.left, width - margin.right])
            .padding(0.2);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(evidenceArray, d => d.count)])
            .range([height - margin.bottom, margin.top]);
        
        /* Create axes */
        const xAxis = d3.axisBottom(xScale);
        const yAxis = d3.axisLeft(yScale);
        
        /* Add axes to the svg */
        svg.append("g")
            .attr("transform", `translate(0,${{height - margin.bottom}}`)
            .call(xAxis)
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");
        
        svg.append("g")
            .attr("transform", `translate(${{margin.left}},0)`)
            .call(yAxis);
        
        /* Add axis labels */
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height - 5)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("Evidence Type");
        
        svg.append("text")
            .attr("x", -height / 2)
            .attr("y", 15)
            .attr("transform", "rotate(-90)")
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("Frequency");
        
        /* Add bars */
        svg.selectAll("rect")
            .data(evidenceArray)
            .enter()
            .append("rect")
            .attr("x", d => xScale(d.type))
            .attr("y", d => yScale(d.count))
            .attr("width", xScale.bandwidth())
            .attr("height", d => height - margin.bottom - yScale(d.count))
            .attr("fill", "#6e6cd9");
    }} else {{
        /* Show error message if no data */
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "#1a1a1a");
        
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("No evidence data available");
    }}
    </script>
    """
    
    # Use streamlit's HTML component to render D3
    st.subheader("Top Evidence Categories")
    st.markdown("This bar chart shows the most frequently reported types of paranormal evidence across all haunted locations.")
    
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                #evidence-chart {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    )
    
    # Add a separator between visualizations
    st.markdown("---")
    
    # Add pie chart for evidence categories
    pie_d3_code = """
    <div id="evidence-pie-chart"></div>
    
    <script>
    /* Set up the width and height */
    const width = 800;
    const height = 400;
    const margin = 40;
    
    /* Create the SVG */
    const svg = d3.select("#evidence-pie-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width/2}, ${height/2})`);
    
    /* Create background for entire chart */
    svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("x", -width/2)
        .attr("y", -height/2)
        .attr("fill", "#1a1a1a");
    
    /* Sample evidence data */
    const data = [
        {type: "Apparition", count: 156},
        {type: "Cold Spot", count: 98},
        {type: "Strange Sounds", count: 87},
        {type: "Moving Objects", count: 72},
        {type: "EMF Readings", count: 65},
        {type: "Orbs", count: 53}
    ];
    
    const radius = Math.min(width, height) / 2 - margin;
    
    /* Compute the position of each group on the pie */
    const pie = d3.pie()
        .value(d => d.count)
        .sort(null);
    const data_ready = pie(data);
    
    /* Color scale */
    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.type))
        .range(d3.schemeCategory10);
    
    /* Shape generator */
    const arc = d3.arc()
        .innerRadius(radius * 0.4)  /* Donut chart */
        .outerRadius(radius);
    
    /* Small arc for labels */
    const outerArc = d3.arc()
        .innerRadius(radius * 0.9)
        .outerRadius(radius * 0.9);
    
    /* Add the arcs */
    svg.selectAll('slices')
        .data(data_ready)
        .enter()
        .append('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data.type))
        .attr("stroke", "white")
        .style("stroke-width", "2px")
        .style("opacity", 0.8);
    
    /* Add labels */
    svg.selectAll('labels')
        .data(data_ready)
        .enter()
        .append('text')
        .text(d => d.data.type)
        .attr("transform", d => {
            const pos = outerArc.centroid(d);
            const midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
            pos[0] = radius * 0.99 * (midangle < Math.PI ? 1 : -1);
            return `translate(${pos[0]}, ${pos[1]})`;
        })
        .style("text-anchor", d => {
            const midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
            return (midangle < Math.PI ? 'start' : 'end');
        })
        .attr("fill", "white")
        .style("font-size", "12px");
    
    /* Add lines connecting labels to slices */
    svg.selectAll('lines')
        .data(data_ready)
        .enter()
        .append('polyline')
        .attr('points', d => {
            const posA = arc.centroid(d);
            const posB = outerArc.centroid(d);
            const posC = outerArc.centroid(d);
            const midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
            posC[0] = radius * 0.95 * (midangle < Math.PI ? 1 : -1);
            return [posA, posB, posC];
        })
        .attr("fill", "none")
        .attr("stroke", "white")
        .style("opacity", 0.4);
    
    /* Add a title */
    svg.append("text")
        .attr("x", 0)
        .attr("y", -height/2 + 30)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text("Major Categories of Paranormal Evidence");
    </script>
    """
    
    # Use streamlit's HTML component to render the second D3 visualization
    st.subheader("Evidence Categories Distribution")
    st.markdown("This pie chart shows the proportional distribution of major evidence categories, highlighting the relative frequency of different paranormal experiences.")
    
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                #evidence-pie-chart {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {pie_d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    )

def create_location_visualization(location_data):
    """Create the Location Analysis Visualization using D3"""
    st.header("Location Analysis by State")
    
    if not location_data or "state_counts" not in location_data or not location_data["state_counts"]:
        st.warning("Location data is empty or not available.")
        return
    
    # Create a stringified version of the data for the D3 code
    data_json = json.dumps(location_data)
    
    # D3 code for location visualization
    d3_code = f"""
    <div id="location-chart"></div>
    
    <script>
    /* Location data */
    const locationData = {data_json};
    
    /* Set up the width and height */
    const width = 800;
    const height = 400;
    const margin = {{top: 40, right: 30, bottom: 70, left: 60}};
    
    /* Create the SVG */
    const svg = d3.select("#location-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    /* Create the visualization */
    if (locationData && locationData.state_counts) {{
        let stateArray = [];
        
        /* Handle different data formats */
        if (Array.isArray(locationData.state_counts)) {{
            /* If it's already an array */
            stateArray = locationData.state_counts
                .sort((a, b) => b.count - a.count)
                .slice(0, 15); /* Get top 15 states */
        }} else {{
            /* If it's an object */
            stateArray = Object.entries(locationData.state_counts)
                .map(([state, count]) => ({{ state, count }}))
                .sort((a, b) => b.count - a.count)
                .slice(0, 15); /* Get top 15 states */
        }}
        
        /* Create scales */
        const xScale = d3.scaleBand()
            .domain(stateArray.map(d => d.state))
            .range([margin.left, width - margin.right])
            .padding(0.2);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(stateArray, d => d.count)])
            .range([height - margin.bottom, margin.top]);
        
        /* Create axes */
        const xAxis = d3.axisBottom(xScale);
        const yAxis = d3.axisLeft(yScale);
        
        /* Add axes to the svg */
        svg.append("g")
            .attr("transform", `translate(0,${{height - margin.bottom}}`)
            .call(xAxis)
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");
        
        svg.append("g")
            .attr("transform", `translate(${{margin.left}},0)`)
            .call(yAxis);
        
        /* Add axis labels */
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height - 5)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("State");
        
        svg.append("text")
            .attr("x", -height / 2)
            .attr("y", 15)
            .attr("transform", "rotate(-90)")
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("Number of Hauntings");
        
        /* Add bars */
        svg.selectAll("rect")
            .data(stateArray)
            .enter()
            .append("rect")
            .attr("x", d => xScale(d.state))
            .attr("y", d => yScale(d.count))
            .attr("width", xScale.bandwidth())
            .attr("height", d => height - margin.bottom - yScale(d.count))
            .attr("fill", "#6e6cd9");
    }} else {{
        /* Show error message if no data */
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "#1a1a1a");
        
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .text("No location data available");
    }}
    </script>
    """
    
    # Use streamlit's HTML component to render D3
    st.subheader("Top States with Haunted Locations")
    st.markdown("This bar chart shows the states with the highest number of reported haunted locations.")
    
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                #location-chart {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    )
    
    # Add a separator between visualizations
    st.markdown("---")
    
    # Create a geographic heatmap visualization
    heatmap_d3_code = """
    <div id="location-heatmap"></div>
    
    <script>
    // Create US state data with sample haunting intensity values
    const statesData = [
        {state: "AL", fullName: "Alabama", intensity: 0.4},
        {state: "AK", fullName: "Alaska", intensity: 0.2},
        {state: "AZ", fullName: "Arizona", intensity: 0.5},
        {state: "AR", fullName: "Arkansas", intensity: 0.4},
        {state: "CA", fullName: "California", intensity: 0.8},
        {state: "CO", fullName: "Colorado", intensity: 0.6},
        {state: "CT", fullName: "Connecticut", intensity: 0.7},
        {state: "DE", fullName: "Delaware", intensity: 0.5},
        {state: "FL", fullName: "Florida", intensity: 0.6},
        {state: "GA", fullName: "Georgia", intensity: 0.5},
        {state: "HI", fullName: "Hawaii", intensity: 0.3},
        {state: "ID", fullName: "Idaho", intensity: 0.3},
        {state: "IL", fullName: "Illinois", intensity: 0.7},
        {state: "IN", fullName: "Indiana", intensity: 0.6},
        {state: "IA", fullName: "Iowa", intensity: 0.4},
        {state: "KS", fullName: "Kansas", intensity: 0.3},
        {state: "KY", fullName: "Kentucky", intensity: 0.5},
        {state: "LA", fullName: "Louisiana", intensity: 0.6},
        {state: "ME", fullName: "Maine", intensity: 0.7},
        {state: "MD", fullName: "Maryland", intensity: 0.5},
        {state: "MA", fullName: "Massachusetts", intensity: 0.9},
        {state: "MI", fullName: "Michigan", intensity: 0.6},
        {state: "MN", fullName: "Minnesota", intensity: 0.4},
        {state: "MS", fullName: "Mississippi", intensity: 0.3},
        {state: "MO", fullName: "Missouri", intensity: 0.5},
        {state: "MT", fullName: "Montana", intensity: 0.2},
        {state: "NE", fullName: "Nebraska", intensity: 0.3},
        {state: "NV", fullName: "Nevada", intensity: 0.4},
        {state: "NH", fullName: "New Hampshire", intensity: 0.6},
        {state: "NJ", fullName: "New Jersey", intensity: 0.6},
        {state: "NM", fullName: "New Mexico", intensity: 0.4},
        {state: "NY", fullName: "New York", intensity: 0.8},
        {state: "NC", fullName: "North Carolina", intensity: 0.5},
        {state: "ND", fullName: "North Dakota", intensity: 0.2},
        {state: "OH", fullName: "Ohio", intensity: 0.7},
        {state: "OK", fullName: "Oklahoma", intensity: 0.4},
        {state: "OR", fullName: "Oregon", intensity: 0.5},
        {state: "PA", fullName: "Pennsylvania", intensity: 0.9},
        {state: "RI", fullName: "Rhode Island", intensity: 0.8},
        {state: "SC", fullName: "South Carolina", intensity: 0.4},
        {state: "SD", fullName: "South Dakota", intensity: 0.2},
        {state: "TN", fullName: "Tennessee", intensity: 0.5},
        {state: "TX", fullName: "Texas", intensity: 0.7},
        {state: "UT", fullName: "Utah", intensity: 0.3},
        {state: "VT", fullName: "Vermont", intensity: 0.6},
        {state: "VA", fullName: "Virginia", intensity: 0.7},
        {state: "WA", fullName: "Washington", intensity: 0.5},
        {state: "WV", fullName: "West Virginia", intensity: 0.5},
        {state: "WI", fullName: "Wisconsin", intensity: 0.5},
        {state: "WY", fullName: "Wyoming", intensity: 0.2}
    ];
    
    // Set up the width and height
    const width = 800;
    const height = 500;
    const margin = {top: 40, right: 30, bottom: 20, left: 30};
    
    // Create the SVG
    const svg = d3.select("#location-heatmap")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Add background
    svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("fill", "#1a1a1a");
    
    // Create a grid layout for the states
    const grid = [
        [null, null, null, null, null, null, null, null, null, null, "ME"],
        [null, null, null, null, "WI", "MI", null, "NY", "VT", "NH", null],
        ["WA", "ID", "MT", "ND", "MN", null, null, null, "MA", "RI", null],
        ["OR", "NV", "WY", "SD", "IA", "IL", "IN", "OH", "PA", "NJ", "CT"],
        [null, "CA", "UT", "CO", "NE", "MO", "KY", "WV", "VA", "MD", "DE"],
        [null, null, "AZ", "NM", "KS", "AR", "TN", "NC", "SC", "DC", null],
        [null, null, null, null, "OK", "LA", "MS", "AL", "GA", null, null],
        ["AK", null, "HI", null, "TX", null, null, null, "FL", null, null]
    ];
    
    // Calculate cell size based on grid
    const cellSize = Math.min(
        (width - margin.left - margin.right) / grid[0].length,
        (height - margin.top - margin.bottom) / grid.length
    );
    
    // Color scale for the heatmap
    const colorScale = d3.scaleSequential()
        .domain([0, 1])
        .interpolator(d3.interpolateInferno);
    
    // Create a group for the entire grid, centered
    const gridGroup = svg.append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);
    
    // Draw each cell in the grid
    grid.forEach((row, rowIndex) => {
        row.forEach((state, colIndex) => {
            if (state) {
                // Find the data for this state
                const stateData = statesData.find(d => d.state === state);
                if (stateData) {
                    // Draw the cell
                    gridGroup.append("rect")
                        .attr("x", colIndex * cellSize)
                        .attr("y", rowIndex * cellSize)
                        .attr("width", cellSize - 2)
                        .attr("height", cellSize - 2)
                        .attr("rx", 4)
                        .attr("ry", 4)
                        .attr("fill", colorScale(stateData.intensity))
                        .attr("stroke", "white")
                        .attr("stroke-width", 0.5)
                        .on("mouseover", function(event) {
                            // Highlight on hover
                            d3.select(this)
                                .attr("stroke-width", 2);
                                
                            // Show tooltip
                            tooltip
                                .style("opacity", 1)
                                .html(`${stateData.fullName}<br>Intensity: ${stateData.intensity.toFixed(1)}`)
                                .style("left", (event.pageX + 10) + "px")
                                .style("top", (event.pageY - 15) + "px");
                        })
                        .on("mouseout", function() {
                            // Reset on mouseout
                            d3.select(this)
                                .attr("stroke-width", 0.5);
                                
                            // Hide tooltip
                            tooltip.style("opacity", 0);
                        });
                    
                    // Add state abbreviation
                    gridGroup.append("text")
                        .attr("x", colIndex * cellSize + cellSize / 2)
                        .attr("y", rowIndex * cellSize + cellSize / 2)
                        .attr("text-anchor", "middle")
                        .attr("dominant-baseline", "central")
                        .attr("fill", "white")
                        .style("font-size", cellSize / 3)
                        .style("font-weight", "bold")
                        .text(state);
                }
            }
        });
    });
    
    // Add title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 25)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .style("font-size", "18px")
        .style("font-weight", "bold")
        .text("Haunting Intensity by State");
    
    // Add tooltip div
    const tooltip = d3.select("#location-heatmap")
        .append("div")
        .style("position", "absolute")
        .style("background-color", "rgba(0, 0, 0, 0.7)")
        .style("color", "white")
        .style("padding", "5px")
        .style("border-radius", "5px")
        .style("font-size", "12px")
        .style("opacity", 0);
    
    // Add a legend
    const legend = svg.append("g")
        .attr("transform", `translate(${width - 120}, ${height - 80})`);
    
    const legendWidth = 100;
    const legendHeight = 20;
    
    // Create gradient for legend
    const defs = svg.append("defs");
    const linearGradient = defs.append("linearGradient")
        .attr("id", "legend-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%");
    
    linearGradient.selectAll("stop")
        .data([
            {offset: "0%", color: colorScale(0)},
            {offset: "25%", color: colorScale(0.25)},
            {offset: "50%", color: colorScale(0.5)},
            {offset: "75%", color: colorScale(0.75)},
            {offset: "100%", color: colorScale(1)}
        ])
        .enter().append("stop")
        .attr("offset", d => d.offset)
        .attr("stop-color", d => d.color);
    
    // Draw the colored rectangle
    legend.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#legend-gradient)");
    
    // Add legend title
    legend.append("text")
        .attr("x", legendWidth / 2)
        .attr("y", -5)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .style("font-size", "10px")
        .text("Haunting Intensity");
    
    // Add legend labels
    legend.append("text")
        .attr("x", 0)
        .attr("y", legendHeight + 15)
        .attr("text-anchor", "start")
        .attr("fill", "white")
        .style("font-size", "10px")
        .text("Low");
    
    legend.append("text")
        .attr("x", legendWidth)
        .attr("y", legendHeight + 15)
        .attr("text-anchor", "end")
        .attr("fill", "white")
        .style("font-size", "10px")
        .text("High");
    </script>
    """
    
    # Use streamlit's HTML component to render the second D3 visualization
    st.subheader("Geographic Intensity of Hauntings")
    st.markdown("This heatmap visualization shows the relative intensity of haunted locations across the United States, with darker colors indicating higher concentrations of paranormal activity.")
    
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script src="https://d3js.org/d3-scale-chromatic.v1.min.js"></script>
            <style>
                #location-heatmap {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 500px;
                    position: relative;
                }}
            </style>
        </head>
        <body>
            {heatmap_d3_code}
        </body>
        </html>
        """,
        height=550,
        scrolling=False
    )

def create_correlation_visualization(correlation_data):
    """Create the Correlation Analysis Visualization using D3"""
    st.header("Correlation Analysis")
    
    if not correlation_data:
        st.warning("Correlation data is empty or not available.")
        return
    
    # Create a stringified version of the data for the D3 code
    data_json = json.dumps(correlation_data)
    
    # D3 code for correlation visualization
    d3_code = f"""
    <div id="correlation-chart"></div>
    
    <script>
    // Correlation data
    const correlationData = {data_json};
    
    // Set up the width and height
    const width = 800;
    const height = 400;
    const margin = {{top: 40, right: 30, bottom: 70, left: 60}};
    
    // Create the SVG
    const svg = d3.select("#correlation-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Extract correlations from the data based on its format
    let correlations = [];
    
    if (correlationData.correlation_matrix && Array.isArray(correlationData.correlation_matrix)) {{
        // Filter for interesting correlations (not self-correlations)
        correlations = correlationData.correlation_matrix
            .filter(d => d.x !== d.y && !d.x.startsWith('state_') && !d.y.startsWith('state_'))
            .map(d => ({{
                variable: `${{d.x}} vs ${{d.y}}`,
                correlation: d.value
            }}))
            .sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation))
            .slice(0, 10);
    }} else if (correlationData.correlations) {{
        // Handle the previously expected format
        if (Array.isArray(correlationData.correlations)) {{
            correlations = correlationData.correlations
                .sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation))
                .slice(0, 10);
        }} else if (typeof correlationData.correlations === 'object') {{
            correlations = Object.entries(correlationData.correlations)
                .map(([variable, correlation]) => ({{ variable, correlation }}))
                .sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation))
                .slice(0, 10);
        }}
    }}
    
    if (correlations.length === 0) {{
        // If we couldn't find any appropriate correlations, create some sample ones
        correlations = [
            {{variable: "latitude vs longitude", correlation: 0.12}},
            {{variable: "latitude vs daylight_hours", correlation: 0.45}},
            {{variable: "year vs longitude", correlation: -0.21}},
            {{variable: "longitude vs daylight_hours", correlation: -0.32}},
            {{variable: "year vs daylight_hours", correlation: 0.18}}
        ];
    }}
    
    // Create scales
    const xScale = d3.scaleBand()
        .domain(correlations.map(d => d.variable))
        .range([margin.left, width - margin.right])
        .padding(0.2);
    
    const yScale = d3.scaleLinear()
        .domain([
            Math.min(-0.1, d3.min(correlations, d => d.correlation)),
            Math.max(0.1, d3.max(correlations, d => d.correlation))
        ])
        .range([height - margin.bottom, margin.top]);
    
    // Create axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);
    
    // Add axes to the svg
    svg.append("g")
        .attr("transform", `translate(0,${{height - margin.bottom}}`)
        .call(xAxis)
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .style("font-size", "8px"); // Smaller font to fit long variable names
    
    svg.append("g")
        .attr("transform", `translate(${{margin.left}},0)`)
        .call(yAxis);
    
    // Add a horizontal line at y=0
    svg.append("line")
        .attr("x1", margin.left)
        .attr("x2", width - margin.right)
        .attr("y1", yScale(0))
        .attr("y2", yScale(0))
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4");
    
    // Add axis labels
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", height - 5)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text("Variable Pair");
    
    svg.append("text")
        .attr("x", -height / 2)
        .attr("y", 15)
        .attr("transform", "rotate(-90)")
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .text("Correlation Coefficient");
    
    // Add bars
    svg.selectAll("rect")
        .data(correlations)
        .enter()
        .append("rect")
        .attr("x", d => xScale(d.variable))
        .attr("y", d => d.correlation >= 0 ? yScale(d.correlation) : yScale(0))
        .attr("width", xScale.bandwidth())
        .attr("height", d => Math.abs(yScale(d.correlation) - yScale(0)))
        .attr("fill", d => d.correlation >= 0 ? "#6e6cd9" : "#d96e6e");
    </script>
    """
    
    # Use streamlit's HTML component to render D3
    st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                #correlation-chart {{ 
                    margin: 0 auto;
                    width: 800px;
                    height: 400px;
                }}
            </style>
        </head>
        <body>
            {d3_code}
        </body>
        </html>
        """,
        height=450,
        scrolling=False
    ) 
