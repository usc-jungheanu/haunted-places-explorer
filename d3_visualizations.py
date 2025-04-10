import json
import os
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class D3VisualizationGenerator:
    def __init__(self, data_dir: str = "output", output_dir: str = "visualizations"):
        """Initialize D3 visualization generator"""
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.template_dir = "templates"
        
        # Create necessary directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(template_dir, exist_ok=True)
        
    def load_data(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(os.path.join(self.data_dir, filename), 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            raise
    
    def create_map_visualization(self) -> None:
        """Create interactive map visualization"""
        try:
            logger.info("Creating map visualization")
            map_data = self.load_data('map_data.json')
            
            # Create HTML template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Haunted Places Map</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <script src="https://d3js.org/topojson.v1.min.js"></script>
                <style>
                    .map-container {
                        width: 100%;
                        height: 800px;
                    }
                    .tooltip {
                        position: absolute;
                        padding: 8px;
                        background: rgba(0, 0, 0, 0.8);
                        color: white;
                        border-radius: 4px;
                        pointer-events: none;
                    }
                </style>
            </head>
            <body>
                <div class="map-container" id="map"></div>
                <script>
                    const data = {map_data};
                    
                    const width = 960;
                    const height = 600;
                    
                    const svg = d3.select("#map")
                        .append("svg")
                        .attr("width", width)
                        .attr("height", height);
                    
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
                        .data(data.map_data)
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
                </script>
            </body>
            </html>
            """
            
            # Save visualization
            with open(os.path.join(self.output_dir, 'map.html'), 'w') as f:
                f.write(template.format(map_data=json.dumps(map_data)))
                
            logger.info("Map visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating map visualization: {e}")
            raise
    
    def create_time_analysis_visualization(self) -> None:
        """Create time analysis visualization"""
        try:
            logger.info("Creating time analysis visualization")
            time_data = self.load_data('time_analysis.json')
            
            # Create HTML template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Time Analysis</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    .chart-container {
                        width: 100%;
                        height: 400px;
                    }
                    .axis-label {
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <div class="chart-container" id="year-chart"></div>
                <div class="chart-container" id="time-chart"></div>
                <script>
                    const data = {time_data};
                    
                    // Year chart
                    const yearSvg = d3.select("#year-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 400);
                    
                    const yearMargin = {top: 20, right: 20, bottom: 30, left: 50};
                    const yearWidth = 960 - yearMargin.left - yearMargin.right;
                    const yearHeight = 400 - yearMargin.top - yearMargin.bottom;
                    
                    const yearG = yearSvg.append("g")
                        .attr("transform", `translate(${yearMargin.left},${yearMargin.top})`);
                    
                    const yearX = d3.scaleLinear()
                        .domain(d3.extent(data.year_counts, d => d.year))
                        .range([0, yearWidth]);
                    
                    const yearY = d3.scaleLinear()
                        .domain([0, d3.max(data.year_counts, d => d.count)])
                        .range([yearHeight, 0]);
                    
                    yearG.append("path")
                        .datum(data.year_counts)
                        .attr("fill", "none")
                        .attr("stroke", "steelblue")
                        .attr("stroke-width", 1.5)
                        .attr("d", d3.line()
                            .x(d => yearX(d.year))
                            .y(d => yearY(d.count))
                        );
                    
                    // Time of day chart
                    const timeSvg = d3.select("#time-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 400);
                    
                    const timeMargin = {top: 20, right: 20, bottom: 30, left: 50};
                    const timeWidth = 960 - timeMargin.left - timeMargin.right;
                    const timeHeight = 400 - timeMargin.top - timeMargin.bottom;
                    
                    const timeG = timeSvg.append("g")
                        .attr("transform", `translate(${timeMargin.left},${timeMargin.top})`);
                    
                    const timeX = d3.scaleBand()
                        .domain(data.time_of_day_counts.map(d => d.time_of_day))
                        .range([0, timeWidth])
                        .padding(0.1);
                    
                    const timeY = d3.scaleLinear()
                        .domain([0, d3.max(data.time_of_day_counts, d => d.count)])
                        .range([timeHeight, 0]);
                    
                    timeG.selectAll(".bar")
                        .data(data.time_of_day_counts)
                        .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", d => timeX(d.time_of_day))
                        .attr("y", d => timeY(d.count))
                        .attr("width", timeX.bandwidth())
                        .attr("height", d => timeHeight - timeY(d.count))
                        .attr("fill", "steelblue");
                </script>
            </body>
            </html>
            """
            
            # Save visualization
            with open(os.path.join(self.output_dir, 'time_analysis.html'), 'w') as f:
                f.write(template.format(time_data=json.dumps(time_data)))
                
            logger.info("Time analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating time analysis visualization: {e}")
            raise
    
    def create_evidence_visualization(self) -> None:
        """Create evidence analysis visualization"""
        try:
            logger.info("Creating evidence analysis visualization")
            evidence_data = self.load_data('evidence_analysis.json')
            
            # Create HTML template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Evidence Analysis</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    .chart-container {
                        width: 100%;
                        height: 400px;
                    }
                    .pie-label {
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <div class="chart-container" id="evidence-chart"></div>
                <div class="chart-container" id="apparition-chart"></div>
                <script>
                    const data = {evidence_data};
                    
                    // Evidence type chart
                    const evidenceSvg = d3.select("#evidence-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 400);
                    
                    const evidenceRadius = Math.min(960, 400) / 2;
                    
                    const evidenceG = evidenceSvg.append("g")
                        .attr("transform", `translate(${960/2},${400/2})`);
                    
                    const evidenceColor = d3.scaleOrdinal()
                        .domain(Object.keys(data.evidence_counts))
                        .range(d3.schemeCategory10);
                    
                    const evidencePie = d3.pie()
                        .value(d => d[1]);
                    
                    const evidenceArc = d3.arc()
                        .innerRadius(0)
                        .outerRadius(evidenceRadius);
                    
                    const evidenceArcs = evidenceG.selectAll(".arc")
                        .data(evidencePie(Object.entries(data.evidence_counts)))
                        .enter().append("g")
                        .attr("class", "arc");
                    
                    evidenceArcs.append("path")
                        .attr("d", evidenceArc)
                        .attr("fill", d => evidenceColor(d.data[0]));
                    
                    // Apparition type chart
                    const apparitionSvg = d3.select("#apparition-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 400);
                    
                    const apparitionRadius = Math.min(960, 400) / 2;
                    
                    const apparitionG = apparitionSvg.append("g")
                        .attr("transform", `translate(${960/2},${400/2})`);
                    
                    const apparitionColor = d3.scaleOrdinal()
                        .domain(data.apparition_counts.map(d => d.apparition_type))
                        .range(d3.schemeCategory10);
                    
                    const apparitionPie = d3.pie()
                        .value(d => d.count);
                    
                    const apparitionArc = d3.arc()
                        .innerRadius(0)
                        .outerRadius(apparitionRadius);
                    
                    const apparitionArcs = apparitionG.selectAll(".arc")
                        .data(apparitionPie(data.apparition_counts))
                        .enter().append("g")
                        .attr("class", "arc");
                    
                    apparitionArcs.append("path")
                        .attr("d", apparitionArc)
                        .attr("fill", d => apparitionColor(d.data.apparition_type));
                </script>
            </body>
            </html>
            """
            
            # Save visualization
            with open(os.path.join(self.output_dir, 'evidence_analysis.html'), 'w') as f:
                f.write(template.format(evidence_data=json.dumps(evidence_data)))
                
            logger.info("Evidence analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating evidence analysis visualization: {e}")
            raise
    
    def create_location_visualization(self) -> None:
        """Create location analysis visualization"""
        try:
            logger.info("Creating location analysis visualization")
            location_data = self.load_data('location_analysis.json')
            
            # Create HTML template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Location Analysis</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    .chart-container {
                        width: 100%;
                        height: 400px;
                    }
                    .bar {
                        fill: steelblue;
                    }
                    .bar:hover {
                        fill: brown;
                    }
                </style>
            </head>
            <body>
                <div class="chart-container" id="state-chart"></div>
                <div class="chart-container" id="country-chart"></div>
                <script>
                    const data = {location_data};
                    
                    // State chart
                    const stateSvg = d3.select("#state-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 400);
                    
                    const stateMargin = {top: 20, right: 20, bottom: 30, left: 50};
                    const stateWidth = 960 - stateMargin.left - stateMargin.right;
                    const stateHeight = 400 - stateMargin.top - stateMargin.bottom;
                    
                    const stateG = stateSvg.append("g")
                        .attr("transform", `translate(${stateMargin.left},${stateMargin.top})`);
                    
                    const stateX = d3.scaleBand()
                        .domain(data.state_counts.map(d => d.state))
                        .range([0, stateWidth])
                        .padding(0.1);
                    
                    const stateY = d3.scaleLinear()
                        .domain([0, d3.max(data.state_counts, d => d.count)])
                        .range([stateHeight, 0]);
                    
                    stateG.selectAll(".bar")
                        .data(data.state_counts)
                        .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", d => stateX(d.state))
                        .attr("y", d => stateY(d.count))
                        .attr("width", stateX.bandwidth())
                        .attr("height", d => stateHeight - stateY(d.count));
                    
                    // Country chart
                    const countrySvg = d3.select("#country-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 400);
                    
                    const countryMargin = {top: 20, right: 20, bottom: 30, left: 50};
                    const countryWidth = 960 - countryMargin.left - countryMargin.right;
                    const countryHeight = 400 - countryMargin.top - countryMargin.bottom;
                    
                    const countryG = countrySvg.append("g")
                        .attr("transform", `translate(${countryMargin.left},${countryMargin.top})`);
                    
                    const countryX = d3.scaleBand()
                        .domain(data.country_counts.map(d => d.country))
                        .range([0, countryWidth])
                        .padding(0.1);
                    
                    const countryY = d3.scaleLinear()
                        .domain([0, d3.max(data.country_counts, d => d.count)])
                        .range([countryHeight, 0]);
                    
                    countryG.selectAll(".bar")
                        .data(data.country_counts)
                        .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", d => countryX(d.country))
                        .attr("y", d => countryY(d.count))
                        .attr("width", countryX.bandwidth())
                        .attr("height", d => countryHeight - countryY(d.count));
                </script>
            </body>
            </html>
            """
            
            # Save visualization
            with open(os.path.join(self.output_dir, 'location_analysis.html'), 'w') as f:
                f.write(template.format(location_data=json.dumps(location_data)))
                
            logger.info("Location analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating location analysis visualization: {e}")
            raise
    
    def create_correlation_visualization(self) -> None:
        """Create correlation analysis visualization"""
        try:
            logger.info("Creating correlation analysis visualization")
            correlation_data = self.load_data('correlation_data.json')
            
            # Create HTML template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Correlation Analysis</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    .chart-container {
                        width: 100%;
                        height: 800px;
                    }
                    .cell {
                        stroke: #fff;
                    }
                    .text {
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <div class="chart-container" id="correlation-chart"></div>
                <script>
                    const data = {correlation_data};
                    
                    const svg = d3.select("#correlation-chart")
                        .append("svg")
                        .attr("width", 960)
                        .attr("height", 800);
                    
                    const margin = {top: 80, right: 25, bottom: 30, left: 40};
                    const width = 960 - margin.left - margin.right;
                    const height = 800 - margin.top - margin.bottom;
                    
                    const g = svg.append("g")
                        .attr("transform", `translate(${margin.left},${margin.top})`);
                    
                    // Get unique variables
                    const variables = [...new Set(data.correlation_matrix.map(d => d.x))];
                    
                    const x = d3.scaleBand()
                        .domain(variables)
                        .range([0, width])
                        .padding(0.05);
                    
                    const y = d3.scaleBand()
                        .domain(variables)
                        .range([0, height])
                        .padding(0.05);
                    
                    const color = d3.scaleSequential()
                        .domain([-1, 1])
                        .interpolator(d3.interpolateRdBu);
                    
                    // Add cells
                    g.selectAll("rect")
                        .data(data.correlation_matrix)
                        .enter().append("rect")
                        .attr("x", d => x(d.x))
                        .attr("y", d => y(d.y))
                        .attr("width", x.bandwidth())
                        .attr("height", y.bandwidth())
                        .attr("fill", d => color(d.value))
                        .attr("class", "cell");
                    
                    // Add text
                    g.selectAll("text")
                        .data(data.correlation_matrix)
                        .enter().append("text")
                        .attr("x", d => x(d.x) + x.bandwidth() / 2)
                        .attr("y", d => y(d.y) + y.bandwidth() / 2)
                        .attr("dy", ".35em")
                        .attr("text-anchor", "middle")
                        .attr("class", "text")
                        .text(d => d.value.toFixed(2));
                </script>
            </body>
            </html>
            """
            
            # Save visualization
            with open(os.path.join(self.output_dir, 'correlation_analysis.html'), 'w') as f:
                f.write(template.format(correlation_data=json.dumps(correlation_data)))
                
            logger.info("Correlation analysis visualization created successfully")
            
        except Exception as e:
            logger.error(f"Error creating correlation analysis visualization: {e}")
            raise
    
    def create_all_visualizations(self) -> None:
        """Create all D3 visualizations"""
        try:
            self.create_map_visualization()
            self.create_time_analysis_visualization()
            self.create_evidence_visualization()
            self.create_location_visualization()
            self.create_correlation_visualization()
            
            logger.info("All visualizations created successfully")
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            raise

def main():
    """Main function to generate D3 visualizations"""
    generator = D3VisualizationGenerator()
    generator.create_all_visualizations()

if __name__ == "__main__":
    main() 