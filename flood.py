import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
import json
import time

# Function to fetch data from ArcGIS REST API with pagination
def fetch_arcgis_data(url, max_records=None, chunk_size=1000):
    all_features = []

    params = {
        'where': '1=1',
        'outFields': '*',
        'outSR': '4326',  # Explicitly request WGS84 coordinates
        'resultRecordCount': chunk_size,
        'resultOffset': 0,
        'f': 'json'  # Use JSON instead of GeoJSON for more control
    }

    more_records = True
    total_fetched = 0

    while more_records:
        print(f"Fetching records {params['resultOffset']} to {params['resultOffset'] + chunk_size} from {url}...")
        response = requests.get(f"{url}/query", params=params)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()
        features = data.get('features', [])

        if not features:
            break

        all_features.extend(features)
        total_fetched += len(features)

        # Check if we've reached the maximum number of records
        if max_records and total_fetched >= max_records:
            break

        # Update offset for next batch
        params['resultOffset'] += chunk_size

        # Small delay to avoid overwhelming the server
        time.sleep(0.5)

    print(f"Total features fetched: {len(all_features)}")
    return all_features

# Function to convert ArcGIS JSON to GeoDataFrame
def features_to_gdf(features, geometry_type):
    if not features:
        return None

    # Extract attributes and geometry
    rows = []
    for feature in features:
        attributes = feature.get('attributes', {})
        geometry = feature.get('geometry', {})

        if geometry_type == 'esriGeometryPolygon':
            # Handle polygon geometry
            rings = geometry.get('rings', [])
            if rings:
                # Create a GeoJSON-like geometry
                geom = {
                    'type': 'Polygon',
                    'coordinates': rings
                }
                attributes['geometry'] = shape(geom)
                rows.append(attributes)

        elif geometry_type == 'esriGeometryPoint':
            # Handle point geometry
            x = geometry.get('x')
            y = geometry.get('y')
            if x is not None and y is not None:
                # Create a GeoJSON-like geometry
                geom = {
                    'type': 'Point',
                    'coordinates': [x, y]
                }
                attributes['geometry'] = shape(geom)
                rows.append(attributes)

    if not rows:
        return None

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(rows, geometry='geometry')
    gdf = gdf.set_crs("EPSG:4326")
    return gdf

# First, let's check the metadata of the new military bases layer
def check_layer_metadata(url):
    response = requests.get(f"{url}?f=json")
    if response.status_code == 200:
        layer_info = response.json()
        print(f"Layer Name: {layer_info.get('name')}")
        print(f"Geometry Type: {layer_info.get('geometryType')}")

        # Get field information
        fields = layer_info.get('fields', [])
        print(f"Fields ({len(fields)}):")
        for field in fields:
            print(f"  - {field.get('name')}: {field.get('type')}")

        # Get feature count
        count_params = {
            'where': '1=1',
            'returnCountOnly': 'true',
            'f': 'json'
        }
        count_response = requests.get(f"{url}/query", params=count_params)
        if count_response.status_code == 200:
            count_data = count_response.json()
            print(f"Total features: {count_data.get('count', 'Unknown')}")

        return layer_info
    else:
        print(f"Failed to get layer info: {response.status_code}")
        return None

# URLs for the data sources
military_url = "https://services.arcgis.com/hRUr1F8lE8Jq2uJo/arcgis/rest/services/milbases/FeatureServer/0"
flood_url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0"

# Check metadata for the new military layer
print("Checking military layer metadata...")
military_metadata = check_layer_metadata(military_url)
geometry_type = military_metadata.get('geometryType') if military_metadata else 'esriGeometryPolygon'

# Fetch military installation data
print("Fetching military installation data...")
military_features = fetch_arcgis_data(military_url)

# Fetch flood hazard data - fetch more to ensure better coverage
print("Fetching flood hazard data...")
flood_features = fetch_arcgis_data(flood_url, max_records=10000)  # Increased to 10,000

# Convert features to GeoDataFrames
print("Converting military data to GeoDataFrame...")
military_gdf = features_to_gdf(military_features, geometry_type)
if military_gdf is not None:
    print(f"Created GeoDataFrame with {len(military_gdf)} military installations")

    # Print a sample of the data to understand its structure
    print("\nSample of military data (first 5 rows):")
    print(military_gdf.drop('geometry', axis=1).head())
else:
    print("Failed to create military GeoDataFrame")
    exit(1)

print("Converting flood data to GeoDataFrame...")
flood_gdf = features_to_gdf(flood_features, 'esriGeometryPolygon')
if flood_gdf is not None:
    print(f"Created GeoDataFrame with {len(flood_gdf)} flood hazard areas")
else:
    print("Failed to create flood GeoDataFrame")
    exit(1)

# Ensure both GeoDataFrames have the same CRS
print(f"Military GDF CRS: {military_gdf.crs}")
print(f"Flood GDF CRS: {flood_gdf.crs}")

# Reproject to a projected CRS for accurate area calculations
print("Reprojecting to a projected CRS for accurate area calculations...")
# Use USA Contiguous Albers Equal Area Conic projection
military_gdf_proj = military_gdf.to_crs("EPSG:5070")
flood_gdf_proj = flood_gdf.to_crs("EPSG:5070")

# Check for valid geometries
print("Validating geometries...")
invalid_military = military_gdf_proj[~military_gdf_proj.geometry.is_valid]
invalid_flood = flood_gdf_proj[~flood_gdf_proj.geometry.is_valid]

if len(invalid_military) > 0:
    print(f"Warning: {len(invalid_military)} military installation geometries are invalid")
    # Try to fix invalid geometries
    military_gdf_proj['geometry'] = military_gdf_proj.geometry.buffer(0)

if len(invalid_flood) > 0:
    print(f"Warning: {len(invalid_flood)} flood hazard geometries are invalid")
    # Try to fix invalid geometries
    flood_gdf_proj['geometry'] = flood_gdf_proj.geometry.buffer(0)

# Remove any remaining invalid geometries
military_gdf_proj = military_gdf_proj[military_gdf_proj.geometry.is_valid & ~military_gdf_proj.geometry.is_empty]
flood_gdf_proj = flood_gdf_proj[flood_gdf_proj.geometry.is_valid & ~flood_gdf_proj.geometry.is_empty]

print(f"After validation: {len(military_gdf_proj)} military installations, {len(flood_gdf_proj)} flood hazard areas")

# Perform spatial analysis using intersection
print("Performing spatial analysis...")

# Create a new column to store flood zone information
military_gdf_proj['in_flood_zone'] = False
military_gdf_proj['flood_type'] = None
military_gdf_proj['intersection_area_sqm'] = 0.0
military_gdf_proj['installation_area_sqm'] = military_gdf_proj.geometry.area
military_gdf_proj['percent_in_flood_zone'] = 0.0

# For each military installation, check intersection with flood zones
# Use a small buffer to catch even tiny intersections
for idx, installation in military_gdf_proj.iterrows():
    # Calculate the area of the installation in square meters
    installation_area = installation.geometry.area

    # Add a tiny buffer to the installation geometry to catch even small intersections
    # This ensures that even if just a corner touches, it will be counted
    buffered_geom = installation.geometry.buffer(1)  # 1 meter buffer

    # Find intersecting flood zones using the buffered geometry
    intersecting_zones = flood_gdf_proj[flood_gdf_proj.intersects(buffered_geom)]

    if len(intersecting_zones) > 0:
        # Calculate the total area of intersection with the original geometry
        total_intersection_area = 0
        flood_types = []

        for _, flood_zone in intersecting_zones.iterrows():
            intersection = installation.geometry.intersection(flood_zone.geometry)
            intersection_area = intersection.area

            # Even if the intersection area is very small, count it
            if intersection_area > 0:
                total_intersection_area += intersection_area
                flood_type = flood_zone.get('esri_symbology', 'Unknown')
                if flood_type not in flood_types:
                    flood_types.append(flood_type)
            # If the buffered geometry intersects but the original doesn't,
            # it means they're very close but not quite touching
            elif buffered_geom.intersection(flood_zone.geometry).area > 0:
                # Mark as in flood zone with a minimal area
                military_gdf_proj.at[idx, 'in_flood_zone'] = True
                flood_type = flood_zone.get('esri_symbology', 'Unknown')
                if flood_type not in flood_types:
                    flood_types.append(flood_type)
                # Set a minimal intersection area
                total_intersection_area = 0.1  # Very small area to indicate proximity

        # If there's any intersection or very close proximity, mark as in flood zone
        if total_intersection_area > 0 or len(flood_types) > 0:
            military_gdf_proj.at[idx, 'in_flood_zone'] = True
            military_gdf_proj.at[idx, 'flood_type'] = ", ".join(flood_types)
            military_gdf_proj.at[idx, 'intersection_area_sqm'] = total_intersection_area

            # Calculate percentage of installation in flood zone
            percent_in_flood = (total_intersection_area / installation_area) * 100
            military_gdf_proj.at[idx, 'percent_in_flood_zone'] = percent_in_flood

# Convert back to WGS84 for GeoJSON output
result_gdf = military_gdf_proj.to_crs("EPSG:4326")

# Determine the name field based on available columns
name_field = None
possible_name_fields = ['SITE_NAME', 'NAME', 'siteName', 'featureName', 'INSTALLATION']
for field in possible_name_fields:
    if field in result_gdf.columns:
        name_field = field
        break

# Determine the state field based on available columns
state_field = None
possible_state_fields = ['STATE', 'stateNameCode', 'STATE_CODE']
for field in possible_state_fields:
    if field in result_gdf.columns:
        state_field = field
        break

# Select relevant columns
columns_to_keep = ['geometry', 'in_flood_zone', 'percent_in_flood_zone',
                   'intersection_area_sqm', 'installation_area_sqm']

if name_field:
    columns_to_keep.append(name_field)
if state_field:
    columns_to_keep.append(state_field)
if 'flood_type' in result_gdf.columns:
    columns_to_keep.append('flood_type')

# Create a clean GeoDataFrame with just the needed columns
result_gdf = result_gdf[columns_to_keep].copy()

# Rename columns for clarity
column_renames = {}
if name_field:
    column_renames[name_field] = 'site_name'
if state_field:
    column_renames[state_field] = 'state'

if column_renames:
    result_gdf = result_gdf.rename(columns=column_renames)

# Count installations in flood zones
in_flood_count = result_gdf['in_flood_zone'].sum()
total_count = len(result_gdf)
percentage = round((in_flood_count / total_count) * 100, 1) if total_count > 0 else 0

print(f"\nAnalysis Results:")
print(f"Total Military Installations: {total_count}")
print(f"Installations in Flood Zones: {in_flood_count}")
print(f"Percentage in Flood Zones: {percentage}%")

# Save to GeoJSON
output_file = "military_installations_flood_analysis.geojson"
print(f"\nSaving results to {output_file}...")
result_gdf.to_file(output_file, driver="GeoJSON")
print("Done!")

# Create a simplified version with just the at-risk installations
at_risk_gdf = result_gdf[result_gdf['in_flood_zone'] == True].copy()
if len(at_risk_gdf) > 0:
    # Sort by percentage in flood zone
    at_risk_gdf = at_risk_gdf.sort_values('percent_in_flood_zone', ascending=False)

    at_risk_file = "military_installations_at_risk.geojson"
    print(f"Saving at-risk installations to {at_risk_file}...")
    at_risk_gdf.to_file(at_risk_file, driver="GeoJSON")

    # Print some examples of at-risk installations
    print("\nTop 5 most affected installations:")
    for idx, row in at_risk_gdf.head(5).iterrows():
        site_name = row.get('site_name', 'Unknown')
        state = row.get('state', 'Unknown')
        percent = round(row.get('percent_in_flood_zone', 0), 1)
        area_sqm = round(row.get('intersection_area_sqm', 0), 0)
        flood_type = row.get('flood_type', 'Unknown')
        print(f"- {site_name} ({state}): {percent}% in flood zone ({area_sqm} sq meters) - {flood_type}")

    print("Done!")
else:
    print("No installations found in flood zones.")
