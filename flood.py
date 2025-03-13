import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import requests
import json
from shapely.geometry import Point, shape
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Military Installations in Flood Hazard Areas",
    page_icon="🌊",
    layout="wide"
)

# Add title and description
st.title("Military Installations in Flood Hazard Areas")
st.markdown("""
This dashboard visualizes military installations and their locations relative to flood hazard areas across the United States.
The analysis helps identify which military bases are potentially at risk from flooding.
""")

# Function to fetch data from ArcGIS REST API
@st.cache_data
def fetch_arcgis_data(url, params=None):
    if params is None:
        params = {
            'where': '1=1',
            'outFields': '*',
            'outSR': '4326',
            'f': 'geojson'
        }
    
    response = requests.get(f"{url}/query", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None

# URLs for the data sources
military_url = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/MIRTA_Points_A_view/FeatureServer/0"
flood_url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0"

# Fetch data
with st.spinner("Fetching military installation data..."):
    military_data = fetch_arcgis_data(military_url)

with st.spinner("Fetching flood hazard data..."):
    # For flood data, we'll limit to a smaller area initially due to the large dataset
    # Users can select states to view more specific data
    flood_data_params = {
        'where': '1=1',
        'outFields': '*',
        'outSR': '4326',
        'resultRecordCount': 1000,  # Limit initial load
        'f': 'geojson'
    }
    flood_data = fetch_arcgis_data(flood_url, flood_data_params)

# Process military data
if military_data:
    military_gdf = gpd.GeoDataFrame.from_features(military_data['features'])
    # Filter to US only
    if 'countryName' in military_gdf.columns:
        military_gdf = military_gdf[military_gdf['countryName'] == 'United States']
    
    # Ensure we have the site name
    if 'siteName' not in military_gdf.columns and 'featureName' in military_gdf.columns:
        military_gdf['siteName'] = military_gdf['featureName']
    
    # Get states for filtering
    if 'stateNameCode' in military_gdf.columns:
        states = sorted(military_gdf['stateNameCode'].dropna().unique())
    else:
        states = []
else:
    st.error("Failed to load military installation data")
    military_gdf = None
    states = []

# Process flood data
if flood_data:
    flood_gdf = gpd.GeoDataFrame.from_features(flood_data['features'])
    # Get flood hazard types
    if 'esri_symbology' in flood_gdf.columns:
        flood_types = sorted(flood_gdf['esri_symbology'].dropna().unique())
    else:
        flood_types = []
else:
    st.error("Failed to load flood hazard data")
    flood_gdf = None
    flood_types = []

# Sidebar for filters
st.sidebar.header("Filters")

# State filter
selected_states = st.sidebar.multiselect(
    "Select States",
    options=states,
    default=states[:5] if len(states) > 5 else states
)

# Flood hazard type filter
selected_flood_types = st.sidebar.multiselect(
    "Select Flood Hazard Types",
    options=flood_types,
    default=flood_types
)

# Filter data based on selections
if military_gdf is not None and len(selected_states) > 0:
    filtered_military = military_gdf[military_gdf['stateNameCode'].isin(selected_states)]
else:
    filtered_military = military_gdf

if flood_gdf is not None and len(selected_flood_types) > 0:
    filtered_flood = flood_gdf[flood_gdf['esri_symbology'].isin(selected_flood_types)]
else:
    filtered_flood = flood_gdf

# Function to check if a point is within any polygon in the flood data
def is_in_flood_zone(point, flood_polygons):
    for _, flood_row in flood_polygons.iterrows():
        if point.within(flood_row.geometry):
            return True, flood_row['esri_symbology']
    return False, None

# Analyze which military installations are in flood zones
if filtered_military is not None and filtered_flood is not None:
    # Create a copy to avoid SettingWithCopyWarning
    analysis_military = filtered_military.copy()
    analysis_military['in_flood_zone'] = False
    analysis_military['flood_type'] = None
    
    # This can be slow for large datasets, so we'll use a progress bar
    with st.spinner("Analyzing military installations in flood zones..."):
        for idx, row in analysis_military.iterrows():
            in_zone, zone_type = is_in_flood_zone(row.geometry, filtered_flood)
            analysis_military.at[idx, 'in_flood_zone'] = in_zone
            analysis_military.at[idx, 'flood_type'] = zone_type
    
    # Count installations in flood zones
    in_flood_count = analysis_military['in_flood_zone'].sum()
    total_count = len(analysis_military)
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Military Installations", total_count)
    with col2:
        st.metric("Installations in Flood Zones", in_flood_count)
    with col3:
        if total_count > 0:
            percentage = round((in_flood_count / total_count) * 100, 1)
            st.metric("Percentage in Flood Zones", f"{percentage}%")
    
    # Create map
    st.subheader("Interactive Map")
    
    # Create a folium map centered on the US
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    
    # Add flood hazard areas
    for _, row in filtered_flood.iterrows():
        # Convert the flood hazard type to a color
        if row['esri_symbology'] == '1% Annual Chance Flood Hazard':
            color = 'red'
            fill_opacity = 0.3
        elif row['esri_symbology'] == '0.2% Annual Chance Flood Hazard':
            color = 'orange'
            fill_opacity = 0.3
        else:
            color = 'blue'
            fill_opacity = 0.2
        
        # Add the polygon to the map
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x, color=color, fill_opacity=fill_opacity: {
                'fillColor': color,
                'color': color,
                'weight': 1,
                'fillOpacity': fill_opacity
            },
            tooltip=row['esri_symbology']
        ).add_to(m)
    
    # Create a marker cluster for military installations
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add military installations to the map
    for _, row in analysis_military.iterrows():
        # Determine marker color based on whether it's in a flood zone
        if row['in_flood_zone']:
            icon_color = 'red'
            prefix = 'fa'
            icon = 'warning'
        else:
            icon_color = 'blue'
            prefix = 'fa'
            icon = 'building'
        
        # Create popup content
        popup_content = f"""
        <b>Site Name:</b> {row['siteName']}<br>
        <b>State:</b> {row['stateNameCode']}<br>
        <b>In Flood Zone:</b> {'Yes' if row['in_flood_zone'] else 'No'}<br>
        """
        
        if row['in_flood_zone'] and row['flood_type']:
            popup_content += f"<b>Flood Type:</b> {row['flood_type']}<br>"
        
        # Add marker to the cluster
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['siteName'],
            icon=folium.Icon(color=icon_color, icon=icon, prefix=prefix)
        ).add_to(marker_cluster)
    
    # Display the map
    folium_static(m)
    
    # Create a table of military installations in flood zones
    st.subheader("Military Installations in Flood Hazard Areas")
    
    if in_flood_count > 0:
        at_risk = analysis_military[analysis_military['in_flood_zone'] == True]
        at_risk_table = at_risk[['siteName', 'stateNameCode', 'flood_type']].rename(
            columns={
                'siteName': 'Site Name',
                'stateNameCode': 'State',
                'flood_type': 'Flood Hazard Type'
            }
        )
        st.dataframe(at_risk_table, use_container_width=True)
    else:
        st.info("No military installations found in flood hazard areas based on current filters.")
    
    # Create charts
    st.subheader("Analysis Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of installations in flood zones
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        labels = ['In Flood Zone', 'Not in Flood Zone']
        sizes = [in_flood_count, total_count - in_flood_count]
        colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)
        
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
    
    with col2:
        # Bar chart of flood types
        if in_flood_count > 0:
            flood_type_counts = at_risk['flood_type'].value_counts()
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            flood_type_counts.plot(kind='bar', color='skyblue', ax=ax2)
            ax2.set_title('Military Installations by Flood Hazard Type')
            ax2.set_xlabel('Flood Hazard Type')
            ax2.set_ylabel('Number of Installations')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info("No data available for flood type distribution.")
    
    # State-wise analysis
    if in_flood_count > 0:
        st.subheader("State-wise Analysis")
        
        # Group by state and count installations in flood zones
        state_analysis = analysis_military.groupby('stateNameCode').agg({
            'in_flood_zone': 'sum',
            'siteName': 'count'
        }).reset_index()
        
        state_analysis.columns = ['State', 'In Flood Zone', 'Total Installations']
        state_analysis['Percentage'] = (state_analysis['In Flood Zone'] / state_analysis['Total Installations'] * 100).round(1)
        state_analysis = state_analysis.sort_values('Percentage', ascending=False)
        
        # Display state analysis table
        st.dataframe(state_analysis, use_container_width=True)
        
        # Bar chart of states with highest percentage of installations in flood zones
        top_states = state_analysis.head(10)
        
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        bars = ax3.bar(top_states['State'], top_states['Percentage'], color='skyblue')
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height}%', ha='center', va='bottom')
        
        ax3.set_title('Top 10 States by Percentage of Military Installations in Flood Zones')
        ax3.set_xlabel('State')
        ax3.set_ylabel('Percentage in Flood Zones')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig3)

# Add information about the data sources
st.sidebar.markdown("---")
st.sidebar.subheader("Data Sources")
st.sidebar.markdown("""
- Military Installations: MIRTA Points from ArcGIS
- Flood Hazard Areas: USA Flood Hazard Reduced Set from ArcGIS
""")

# Add disclaimer
st.sidebar.markdown("---")
st.sidebar.info("""
**Disclaimer:** This analysis is for informational purposes only. The accuracy of the flood hazard data and military installation locations depends on the source data.
""")
