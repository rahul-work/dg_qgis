from pathlib import Path

import pandas as pd
import geopandas as gpd
import osmnx


def read_stops(csv_file, name, func):
	df = pd.read_csv(csv_file)
	geometry = gpd.points_from_xy(df['longitude'], df['latitude'], crs='EPSG:4326')
	gdf = gpd.GeoDataFrame(data=df, geometry=geometry, crs='EPSG:4326')
	
	dirpath = Path(r'D:\iitbgis\work\Transport\data\workspace')
	filepath = dirpath / f'{name}_pt_stops.gpkg'
	gdf.to_file(filepath, driver='GPKG', layer='pt_stops')
	return {
		'type': 'add layers from file',
		'layers': [{
			'title': name,
			'filepath': str(filepath)
		}]
	}


# def nearest_nodes():
# 	nearest_nodes = osmnx.distance.nearest_nodes(graph, df['longitude'], df['latitude'])