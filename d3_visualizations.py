import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class D3VisualizationGenerator:
    def __init__(self, data_dir: str = "output", output_dir: str = "visualizations"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create templates directory
        self.templates_dir = self.output_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Create necessary files
        self._create_template_files()
    
    def _create_template_files(self):
        """Create necessary template files for D3 visualizations"""
        # Create index.html
        index_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Haunted Places Visualizations</title>
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
                .tooltip { 
                    position: absolute; 
                    padding: 8px; 
                    background: rgba(0, 0, 0, 0.8); 
                    color: white; 
                    border-radius: 4px;
                    pointer-events: none;
                }
                .tab-container {
                    display: flex;
                    margin-bottom: 20px;
                }
                .tab {
                    padding: 10px 20px;
                    background-color: #4a4a4a;
                    cursor: pointer;
                    border-radius: 4px 4px 0 0;
                    margin-right: 5px;
                }
                .tab:hover {
                    background-color: #5a5a5a;
                }
                .tab.active {
                    background-color: #6e6cd9;
                }
                .tab-content {
                    display: none;
                }
                .tab-content.active {
                    display: block;
                }
            </style>
        </head>
        <body>
            <h1>Haunted Places Analysis</h1>
            
            <div class="tab-container">
                <div class="tab active" data-tab="map">Map Visualization</div>
                <div class="tab" data-tab="time">Time Analysis</div>
                <div class="tab" data-tab="evidence">Evidence Analysis</div>
                <div class="tab" data-tab="location">Location Analysis</div>
                <div class="tab" data-tab="correlation">Correlation Analysis</div>
            </div>
            
            <div id="map-visualization" class="tab-content visualization active">
                <h2>Interactive Map of Haunted Locations</h2>
                <div id="map-container"></div>
            </div>
            
            <div id="time-visualization" class="tab-content visualization">
                <h2>Temporal Analysis of Haunted Sightings</h2>
                <div id="time-chart"></div>
            </div>
            
            <div id="evidence-visualization" class="tab-content visualization">
                <h2>Evidence Type Analysis</h2>
                <div id="evidence-chart"></div>
            </div>
            
            <div id="location-visualization" class="tab-content visualization">
                <h2>Geographical Analysis</h2>
                <div id="location-chart"></div>
            </div>
            
            <div id="correlation-visualization" class="tab-content visualization">
                <h2>Variables Correlation</h2>
                <div id="correlation-chart"></div>
            </div>
            
            <script>
                // Tab switching functionality
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.addEventListener('click', () => {
                        // Remove active class from all tabs and contents
                        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                        
                        // Add active class to clicked tab
                        tab.classList.add('active');
                        
                        // Show corresponding content
                        const tabId = tab.getAttribute('data-tab');
                        document.getElementById(`${tabId}-visualization`).classList.add('active');
                    });
                });
            </script>
            
            <script src="visualizations.js"></script>
        </body>
        </html>
        """
        
        with open(self.output_dir / "index.html", "w", encoding='utf-8') as f:
            f.write(index_html)
    
    def load_data(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(self.data_dir / filename, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data from {filename}: {str(e)}")
            return {}
    
    def create_map_visualization(self):
        """Create map visualization using D3"""
        data = self.load_data("map_data.json")
        if not data:
            return
        
        # Create map visualization JavaScript
        map_js = """
        // Load map data
        const mapData = """ + json.dumps(data) + """;
        
        // Create map visualization
        const width = 800;
        const height = 600;
        
        const svg = d3.select("#map-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
            
        // Create projection
        const projection = d3.geoMercator()
            .scale(100)
            .center([0, 0]);
            
        const path = d3.geoPath().projection(projection);
        
        // Add tooltip
        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        // Add points
        svg.selectAll("circle")
            .data(mapData.map_data)
            .enter()
            .append("circle")
            .attr("cx", d => projection([d.longitude, d.latitude])[0])
            .attr("cy", d => projection([d.longitude, d.latitude])[1])
            .attr("r", 5)
            .style("fill", "red")
            .style("opacity", 0.6)
            .on("mouseover", function(event, d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(`<strong>${d.location}</strong><br/>
                    State: ${d.state}<br/>
                    Country: ${d.country}<br/>
                    Description: ${d.description.substring(0, 100)}...`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function() {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
        """
        
        with open(self.output_dir / "visualizations.js", "w", encoding='utf-8') as f:
            f.write(map_js)
    
    def create_time_analysis_visualization(self):
        """Create time analysis visualization"""
        data = self.load_data("time_analysis.json")
        if not data:
            return
        
        # Add time analysis visualization code
        time_js = """
        // Load time analysis data
        const timeData = """ + json.dumps(data) + """;
        
        // Create time analysis visualization
        const width = 800;
        const height = 400;
        const margin = {top: 20, right: 20, bottom: 30, left: 50};
        
        const svg = d3.select("#time-chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
            
        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);
            
        // Create scales
        const x = d3.scaleLinear()
            .domain(d3.extent(timeData.year_counts, d => d.year))
            .range([0, width - margin.left - margin.right]);
            
        const y = d3.scaleLinear()
            .domain([0, d3.max(timeData.year_counts, d => d.count)])
            .range([height - margin.top - margin.bottom, 0]);
            
        // Add axes
        g.append("g")
            .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
            .call(d3.axisBottom(x).tickFormat(d3.format("d")));
            
        g.append("g")
            .call(d3.axisLeft(y));
            
        // Add line
        g.append("path")
            .datum(timeData.year_counts)
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 1.5)
            .attr("d", d3.line()
                .x(d => x(d.year))
                .y(d => y(d.count))
            );
        """
        
        with open(self.output_dir / "visualizations.js", "a", encoding='utf-8') as f:
            f.write(time_js)
    
    def create_evidence_visualization(self):
        """Create evidence analysis visualization"""
        data = self.load_data("evidence_analysis.json")
        if not data:
            return
        
        # Add evidence visualization code
        evidence_js = """
        // Load evidence data
        const evidenceData = """ + json.dumps(data) + """;
        
        // Create evidence visualization
        const width = 800;
        const height = 400;
        const radius = Math.min(width, height) / 2;
        
        const svg = d3.select("#evidence-chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
            
        const g = svg.append("g")
            .attr("transform", `translate(${width/2},${height/2})`);
            
        // Create pie chart
        const pie = d3.pie()
            .value(d => d[1]);
            
        const arc = d3.arc()
            .innerRadius(0)
            .outerRadius(radius);
            
        const color = d3.scaleOrdinal()
            .domain(Object.keys(evidenceData.evidence_counts))
            .range(d3.schemeCategory10);
            
        // Add arcs
        g.selectAll(".arc")
            .data(pie(Object.entries(evidenceData.evidence_counts)))
            .enter()
            .append("path")
            .attr("class", "arc")
            .attr("d", arc)
            .attr("fill", d => color(d.data[0]));
            
        // Add labels
        g.selectAll(".label")
            .data(pie(Object.entries(evidenceData.evidence_counts)))
            .enter()
            .append("text")
            .attr("class", "label")
            .attr("transform", d => `translate(${arc.centroid(d)})`)
            .attr("text-anchor", "middle")
            .text(d => d.data[0]);
        """
        
        with open(self.output_dir / "visualizations.js", "a", encoding='utf-8') as f:
            f.write(evidence_js)
    
    def create_location_visualization(self):
        """Create location analysis visualization"""
        data = self.load_data("location_analysis.json")
        if not data:
            return
        
        # Add location visualization code
        location_js = """
        // Load location data
        const locationData = """ + json.dumps(data) + """;
        
        // Create location visualization
        const width = 800;
        const height = 400;
        const margin = {top: 20, right: 20, bottom: 30, left: 50};
        
        const svg = d3.select("#location-chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
            
        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);
            
        // Create scales
        const x = d3.scaleBand()
            .domain(locationData.state_counts.map(d => d.state))
            .range([0, width - margin.left - margin.right])
            .padding(0.1);
            
        const y = d3.scaleLinear()
            .domain([0, d3.max(locationData.state_counts, d => d.count)])
            .range([height - margin.top - margin.bottom, 0]);
            
        // Add axes
        g.append("g")
            .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");
            
        g.append("g")
            .call(d3.axisLeft(y));
            
        // Add bars
        g.selectAll(".bar")
            .data(locationData.state_counts)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.state))
            .attr("y", d => y(d.count))
            .attr("width", x.bandwidth())
            .attr("height", d => height - margin.top - margin.bottom - y(d.count))
            .attr("fill", "steelblue");
        """
        
        with open(self.output_dir / "visualizations.js", "a", encoding='utf-8') as f:
            f.write(location_js)
    
    def create_correlation_visualization(self):
        """Create correlation analysis visualization"""
        data = self.load_data("correlation_data.json")
        if not data:
            return
        
        # Add correlation visualization code
        correlation_js = """
        // Load correlation data
        const correlationData = """ + json.dumps(data) + """;
        
        // Create correlation visualization
        const width = 800;
        const height = 800;
        const margin = {top: 50, right: 50, bottom: 100, left: 100};
        
        const svg = d3.select("#correlation-chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
            
        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);
            
        // Get unique variables and group them
        const variables = [...new Set(correlationData.correlation_matrix.map(d => d.x))];
        
        // Group variables by type
        const groupedVars = {
            geographic: variables.filter(v => ['latitude', 'longitude', 'daylight_hours', 'elevation'].includes(v)),
            temporal: variables.filter(v => ['year', 'month', 'day'].includes(v)),
            state: variables.filter(v => v.startsWith('state_')),
            apparition: variables.filter(v => v.startsWith('apparition_type_')),
            evidence: variables.filter(v => v.startsWith('evidence_type_'))
        };
        
        // Combine all variables in order
        const sortedVars = [
            ...groupedVars.geographic,
            ...groupedVars.temporal,
            ...groupedVars.state,
            ...groupedVars.apparition,
            ...groupedVars.evidence
        ];
        
        // Create scales
        const x = d3.scaleBand()
            .domain(sortedVars)
            .range([0, width - margin.left - margin.right])
            .padding(0.05);
            
        const y = d3.scaleBand()
            .domain(sortedVars)
            .range([0, height - margin.top - margin.bottom])
            .padding(0.05);
            
        const color = d3.scaleSequential()
            .domain([-1, 1])
            .interpolator(d3.interpolateRdBu);
            
        // Add group dividers
        const addGroupDivider = (startVar, endVar, label) => {
            const startY = y(startVar);
            const endY = y(endVar) + y.bandwidth();
            
            // Add vertical divider
            g.append("line")
                .attr("x1", -5)
                .attr("x2", -5)
                .attr("y1", startY)
                .attr("y2", endY)
                .attr("stroke", "#666")
                .attr("stroke-width", 2);
                
            // Add group label
            g.append("text")
                .attr("x", -10)
                .attr("y", (startY + endY) / 2)
                .attr("text-anchor", "end")
                .attr("alignment-baseline", "middle")
                .attr("transform", `rotate(-90, -10, ${(startY + endY) / 2})`)
                .style("font-size", "12px")
                .style("font-weight", "bold")
                .text(label);
        };
        
        // Add dividers for each group
        if (groupedVars.geographic.length > 0) {
            addGroupDivider(groupedVars.geographic[0], groupedVars.geographic[groupedVars.geographic.length - 1], "Geographic");
        }
        if (groupedVars.temporal.length > 0) {
            addGroupDivider(groupedVars.temporal[0], groupedVars.temporal[groupedVars.temporal.length - 1], "Temporal");
        }
        if (groupedVars.state.length > 0) {
            addGroupDivider(groupedVars.state[0], groupedVars.state[groupedVars.state.length - 1], "States");
        }
        if (groupedVars.apparition.length > 0) {
            addGroupDivider(groupedVars.apparition[0], groupedVars.apparition[groupedVars.apparition.length - 1], "Apparitions");
        }
        if (groupedVars.evidence.length > 0) {
            addGroupDivider(groupedVars.evidence[0], groupedVars.evidence[groupedVars.evidence.length - 1], "Evidence");
        }
        
        // Add cells
        g.selectAll("rect")
            .data(correlationData.correlation_matrix)
            .enter()
            .append("rect")
            .attr("x", d => x(d.x))
            .attr("y", d => y(d.y))
            .attr("width", x.bandwidth())
            .attr("height", y.bandwidth())
            .attr("fill", d => color(d.value))
            .attr("stroke", "#fff")
            .attr("stroke-width", 0.5)
            .on("mouseover", function(event, d) {
                d3.select(this)
                    .attr("stroke", "#000")
                    .attr("stroke-width", 2);
                    
                // Show tooltip
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(`<strong>${d.x} ↔ ${d.y}</strong><br/>Correlation: ${d.value.toFixed(3)}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function() {
                d3.select(this)
                    .attr("stroke", "#fff")
                    .attr("stroke-width", 0.5);
                    
                // Hide tooltip
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
            
        // Add text for strong correlations
        g.selectAll("text.correlation")
            .data(correlationData.correlation_matrix)
            .enter()
            .append("text")
            .attr("class", "correlation")
            .attr("x", d => x(d.x) + x.bandwidth() / 2)
            .attr("y", d => y(d.y) + y.bandwidth() / 2)
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .style("font-size", "8px")
            .text(d => Math.abs(d.value) > 0.3 ? d.value.toFixed(2) : "");
            
        // Add axes
        g.append("g")
            .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end")
            .style("font-size", "10px");
            
        g.append("g")
            .call(d3.axisLeft(y))
            .selectAll("text")
            .style("font-size", "10px");
            
        // Add title
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", margin.top / 2)
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text("Correlation Matrix of Variables (Grouped by Type)");
            
        // Add color scale legend
        const legendWidth = 200;
        const legendHeight = 20;
        const legendX = width - margin.right - legendWidth;
        const legendY = height - margin.bottom + 40;
        
        const legendScale = d3.scaleLinear()
            .domain([-1, 1])
            .range([0, legendWidth]);
            
        const legendAxis = d3.axisBottom(legendScale)
            .ticks(5);
            
        const legend = svg.append("g")
            .attr("transform", `translate(${legendX},${legendY})`);
            
        const defs = svg.append("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", "correlation-gradient")
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "100%")
            .attr("y2", "0%");
            
        gradient.selectAll("stop")
            .data(color.ticks(10).map((t, i, n) => ({offset: `${100*i/n.length}%`, color: color(t)})))
            .enter().append("stop")
            .attr("offset", d => d.offset)
            .attr("stop-color", d => d.color);
            
        legend.append("rect")
            .attr("width", legendWidth)
            .attr("height", legendHeight)
            .style("fill", "url(#correlation-gradient)");
            
        legend.append("g")
            .call(legendAxis);
            
        // Add tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0)
            .style("position", "absolute")
            .style("background-color", "white")
            .style("border", "1px solid #ddd")
            .style("padding", "10px")
            .style("border-radius", "5px")
            .style("pointer-events", "none");
        """
        
        with open(self.output_dir / "visualizations.js", "a", encoding='utf-8') as f:
            f.write(correlation_js)
    
    def create_all_visualizations(self):
        """Create all visualizations"""
        self.create_map_visualization()
        self.create_time_analysis_visualization()
        self.create_evidence_visualization()
        self.create_location_visualization()
        self.create_correlation_visualization()
        logger.info("All D3 visualizations have been created successfully")

def main():
    generator = D3VisualizationGenerator()
    generator.create_all_visualizations()

if __name__ == "__main__":
    main() 
