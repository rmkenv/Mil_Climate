Checking military layer metadata...
Layer Name: USA Military Bases
Geometry Type: esriGeometryPolygon
Fields (9):
  - OBJECTID: esriFieldTypeOID
  - COMPONENT: esriFieldTypeString
  - SITE_NAME: esriFieldTypeString
  - JOINT_BASE: esriFieldTypeString
  - STATE_TERR: esriFieldTypeString
  - BRAC_SITE: esriFieldTypeString
  - STPOSTAL: esriFieldTypeString
  - STFIPS: esriFieldTypeString
  - Transparency: esriFieldTypeSmallInteger
Total features: 654
Fetching military installation data...
Fetching records 0 to 1000 from https://services.arcgis.com/hRUr1F8lE8Jq2uJo/arcgis/rest/services/milbases/FeatureServer/0...
Fetching records 1000 to 2000 from https://services.arcgis.com/hRUr1F8lE8Jq2uJo/arcgis/rest/services/milbases/FeatureServer/0...
Total features fetched: 654
Fetching flood hazard data...
Fetching records 0 to 1000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 1000 to 2000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 2000 to 3000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 3000 to 4000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 4000 to 5000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 5000 to 6000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 6000 to 7000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 7000 to 8000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 8000 to 9000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Fetching records 9000 to 10000 from https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer/0...
Total features fetched: 10000
Converting military data to GeoDataFrame...
Created GeoDataFrame with 654 military installations

Sample of military data (first 5 rows):
   OBJECTID    COMPONENT                 SITE_NAME JOINT_BASE      STATE_TERR  \
0         1  Army Active     Fort Bliss AAA Ranges        N/A      New Mexico   
1         2    MC Active  MCAS Beaufort LB Housing        N/A  South Carolina   
2         3    MC Active             MCAS Beaufort        N/A  South Carolina   
3         4    MC Active        MCSF Blount Island        N/A         Florida   
4         5    MC Active              OLF Atlantic        N/A  North Carolina   

  BRAC_SITE STPOSTAL STFIPS  Transparency  
0        NO       NM     35            50  
1        NO       SC     45            50  
2        NO       SC     45            50  
3        NO       FL     12            50  
4        NO       NC     37            50  
Converting flood data to GeoDataFrame...
Created GeoDataFrame with 10000 flood hazard areas
Military GDF CRS: EPSG:4326
Flood GDF CRS: EPSG:4326
Reprojecting to a projected CRS for accurate area calculations...
Validating geometries...
Warning: 198 military installation geometries are invalid
Warning: 108 flood hazard geometries are invalid
After validation: 654 military installations, 10000 flood hazard areas
Adding 1/2 mile buffer around military installations...
Performing spatial analysis with buffered installations...
Analysis Results:
Total Military Installations: 654
Installations directly in Flood Zones: 15 (2.3%)
Installations with 1/2 mile buffer in Flood Zones: 42 (6.4%)
Installations with only buffer in Flood Zones: 35 (5.4%)

Saving results to military_installations_flood_analysis_buffered.geojson...
Done!
Saving at-risk installations to military_installations_at_risk_buffered.geojson...

Top 5 most affected installations (including buffer zone):
- NS Mayport FISC (Florida): 23.8% of base in flood zone (183532.0 sq meters)
  Flood type: 0.2% Annual Chance Flood Hazard
- Homestead ARB (Florida): Buffer zone only in flood zone (407658.0 sq meters)
  Flood type: 1% Annual Chance Flood Hazard
- Langley FH Annex (Virginia): Buffer zone only in flood zone (191333.0 sq meters)
  Flood type: 1% Annual Chance Flood Hazard
- NAS Oceana Dam Neck (Virginia): 2.8% of base in flood zone (207570.0 sq meters)
  Flood type: 0.2% Annual Chance Flood Hazard
- Aberdeen Proving Ground (Maryland): Buffer zone only in flood zone (14310.0 sq meters)
  Flood type: 0.2% Annual Chance Flood Hazard
Done!
