# Military Installations Flood Hazard Analysis

This repository contains Python code for analyzing the vulnerability of U.S. military installations to flood hazards using geospatial analysis techniques. The code performs a spatial intersection between military installation boundaries and FEMA flood hazard areas, including a 1/2 mile buffer analysis to identify installations with nearby flood risks.

## Overview

The analysis uses two primary data sources from ArcGIS REST services:
1. Military installation boundaries (polygons)
2. FEMA flood hazard areas (polygons)

The code performs the following operations:
- Fetches data from ArcGIS REST services with pagination
- Converts ArcGIS JSON responses to GeoDataFrames
- Validates and repairs geometries
- Creates 1/2 mile buffers around military installations
- Performs spatial intersection analysis
- Calculates affected areas and percentages
- Generates GeoJSON files for visualization

## Requirements

The code requires the following Python packages:
- geopandas
- pandas
- shapely
- requests
- json
- time

Install dependencies using:
```bash
pip install geopandas shapely pandas requests
```

## Data Sources

The analysis uses the following ArcGIS REST services:
- Military Installations: `https://services.arcgis.com/hRUr1F8lE8Jq2uJo/arcgis/rest/services/milbases/FeatureServer/0`
- Flood Hazard Areas: `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0`

## Key Functions

### `fetch_arcgis_data(url, max_records=None, chunk_size=1000)`
Fetches data from ArcGIS REST API with pagination support.

### `features_to_gdf(features, geometry_type)`
Converts ArcGIS JSON features to a GeoDataFrame.

### `check_layer_metadata(url)`
Retrieves and displays metadata about an ArcGIS layer.

## Analysis Process

1. **Data Retrieval**: Fetches military installation and flood hazard data from ArcGIS REST services.
2. **Data Preparation**: Converts data to GeoDataFrames and ensures consistent coordinate reference systems.
3. **Geometry Validation**: Checks for and repairs invalid geometries.
4. **Buffer Creation**: Creates a 1/2 mile (804.5 meter) buffer around military installations.
5. **Spatial Analysis**: Performs intersection analysis between installations (both original and buffered) and flood hazard areas.
6. **Results Calculation**: Calculates affected areas, percentages, and categorizes installations by risk level.
7. **Output Generation**: Creates GeoJSON files for visualization and reporting.

## Output Files

The code generates the following output files:
1. `military_installations_flood_analysis_buffered.geojson`: Contains all military installations with their buffered geometries and analysis results.
2. `military_installations_at_risk_buffered.geojson`: Contains only the installations that are in or near flood zones.

## Analysis Results

The analysis identifies:
- Installations directly in flood zones
- Installations with buffer zones intersecting flood hazards
- Percentage of each installation affected
- Types of flood hazards affecting each installation

## Example Usage

# Run the full analysis
python military_flood_analysis.py

# To modify buffer distance (in meters)
# Edit the line: military_gdf_proj['buffered_geometry'] = military_gdf_proj.geometry.buffer(804.5)

## Visualization

The generated GeoJSON files can be visualized using:
- QGIS
- ArcGIS
- Web mapping libraries like Leaflet or Mapbox
- Streamlit with folium or pydeck for interactive dashboards

## Limitations

- The analysis is dependent on the accuracy and completeness of the source data
- Flood hazard designations represent historical risk and may not account for climate change
- The 1/2 mile buffer is a simplified approximation of potential impact areas
- The analysis does not account for elevation or flood mitigation measures

## Future Improvements

Potential enhancements to the analysis include:
- Integration with climate change projections
- Incorporation of Digital Elevation Models for more accurate flood risk assessment
- Analysis of critical infrastructure within installations
- Temporal analysis of historical flooding events
- Cost-benefit analysis of potential mitigation measures



## Citation

If you use this code or methodology in your work, please cite:

Military Installations Flood Hazard Analysis
https://github.com/yourusername/military-flood-analysis


