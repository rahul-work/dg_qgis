import os
from pathlib import Path
import zipfile

import shapely
import pandas as pd
import geopandas as gpd
import osmnx

from .gtfs import (
	gtfs_stops_from_msrtc_stops_file as read_stops,
	gtfs_stop_times_trips_routes_from_msrtc_form_4 as read_form_4
)


# def read_stops(csv_file, name, func):
# 	df = pd.read_csv(csv_file)
# 	geometry = gpd.points_from_xy(df['longitude'], df['latitude'], crs='EPSG:4326')
# 	gdf = gpd.GeoDataFrame(data=df, geometry=geometry, crs='EPSG:4326')
	
# 	dirpath = Path(r'D:\iitbgis\work\Transport\data\workspace')
# 	filepath = dirpath / f'{name}_pt_stops.gpkg'
# 	gdf.to_file(filepath, driver='GPKG', layer='pt_stops')
# 	return {
# 		'type': 'add layers from file',
# 		'layers': [{
# 			'title': name,
# 			'filepath': str(filepath)
# 		}]
# 	}


# # def nearest_nodes():
# # 	nearest_nodes = osmnx.distance.nearest_nodes(graph, df['longitude'], df['latitude'])


class BusDepot:

	POTENTIAL_DATA = {
		'sources': {
			'Id': None,
			'dirpath': None,
			'osm_call_signature': None,
			'data': {
				'stops': None,
				'form_4': None,
				'osm_nodes': None,
				'osm_edges': None,
			}
		},
		'dg_stops': {},
		'dg_routes': {},
		'dg_POIs': {},
		'GTFS': {
			'agency.txt': None,
			'stops.txt': None,
			'routes.txt': None,
			'trips.txt': None,
			'stop_times.txt': None,
			'calendar.txt': None,
		},
	}

	def __init__(self) -> None:
		self.data_dict = {}
	
	def read_file_sources(self, dirpath):
		if not isinstance(dirpath, Path):
			dirpath = Path(dirpath)
		self.data_dict['sources'] = self.POTENTIAL_DATA['sources']
		for k in self.data_dict['sources']['data'].keys():
			self.data_dict['sources']['data'][f'{k}_df'] = pd.read_csv(dirpath / f'{k}.csv')

	def write_gtfs_zipfile(self, dirpath):
		if not isinstance(dirpath, Path):
			dirpath = Path(dirpath)
		if not os.path.exists(Path(dirpath)):
			os.mkdir(dirpath)
		with zipfile.ZipFile(Path(dirpath) / 'gtfs.zip', 'w') as zf:
			for filename, filedata_df in self.data_dict['GTFS'].items():
				filepath = dirpath / filename
				filedata_df.to_csv(filepath)
				zf.write(filepath, arcname=filename)
	
	def save(self, filepath):
		if not isinstance(filepath, Path):
			filepath = Path(filepath)
		for name, gdf in self.data_dict.items():
			gdf.to_file(filepath, driver='GPKG', layer=name)
	
	def digest(self):
		self.digest_stops()
		self.digest_routes()	

	def digest_stops(self):
		stops_df = self.data_dict['stops']
		dg_stops_gdf = gpd.GeoDataFrame(
			stops_df,
			geometry=gpd.points_from_xy(stops_df['stop_lon'], stops_df['stop_lat']),
			crs='EPSG:4326'
		)
		self.data_dict['dg_stops'] = dg_stops_gdf
		
		west, south, east, north = dg_stops_gdf.geometry.total_bounds
		buffer = 0.1*max(abs(north-south), abs(east-west))
		osm_graph = osmnx.graph_from_bbox(north+buffer, south-buffer, east+buffer, west-buffer)
		osm_nodes, osm_edges = osmnx.graph_to_gdfs(osm_graph)
		self.data_dict['osm_nodes'], self.data_dict['osm_edges'] = osm_nodes, osm_edges

		dg_stops_gdf['nearest_osm_node_osmid'] = osmnx.nearest_nodes(osm_graph, dg_stops_gdf['stop_lon'], dg_stops_gdf['stop_lat'])
		dg_stops_nearest_nodes = dg_stops_gdf.join(
			osm_nodes, on='nearest_osm_node_osmid', lsuffix='_stops'
		)[['name', 'nearest_osm_node_osmid', 'geometry']]
		self.data_dict['dg_stops_nearest_nodes'] = dg_stops_nearest_nodes
		
		dg_stops_route_to_nearest_node = dg_stops_gdf.merge(dg_stops_nearest_nodes, on='name')
		dg_stops_route_to_nearest_node['geometry'] = dg_stops_route_to_nearest_node.apply(
			lambda r: shapely.geometry.LineString([r['geometry_x'], r['geometry_y']]),
			axis=1
		)
		dg_stops_route_to_nearest_node = gpd.GeoDataFrame(
			dg_stops_route_to_nearest_node[['name', 'nearest_osm_node_osmid_x', 'geometry']]
		)
		self.data_dict['dg_stops_route_to_nearest_node'] = dg_stops_route_to_nearest_node
		
		
	def digest_routes(self):
		stop_times_df = self.data_dict['stop_times']

		trips_gdf = stop_times_df.merge(self.data_dict['dg_stops'], on='stop_id')[
			['trip_id', 'stop_id', 'stop_sequence', 'geometry']
		].rename(columns={'geometry': 'stop_geometry'})
		def stops_id_and_geom(gb_df):
			stops_in_sequence = gb_df.sort_values(['stop_sequence'])
			return pd.Series({
				'stops_in_sequence': ','.join(stops_in_sequence['stop_id']),
				'nearest_osmids_sequence': list(stops_in_sequence.merge(
					self.data_dict['dg_stops'], on='stop_id'
				)['nearest_osm_node_osmid'])
			})
		trips_gdf = trips_gdf.merge(trips_gdf.groupby(['trip_id']).apply(stops_id_and_geom), on='trip_id')
		
		Xs = []; Ys = []
		for idx, row in trips_gdf.iterrows():
			Xs.extend(row['nearest_osmids_sequence'][:-1])
			Ys.extend(row['nearest_osmids_sequence'][1:])
		Xs, Ys = list(zip(*list(set(zip(Xs, Ys)))))
		osm_graph = osmnx.graph_from_gdfs(
			self.data_dict['osm_nodes'], self.data_dict['osm_edges']
		)
		shortest_osmid_paths_df = pd.DataFrame({
			'X': Xs, 'Y': Ys, 'shortest_path_osmids': osmnx.shortest_path(osm_graph, Xs, Ys)
		}).set_index(['X', 'Y'])
		
		trips_gdf['shortest_path_route_geometry'] = trips_gdf.apply(
			lambda r: shapely.geometry.MultiLineString([
				self.data_dict['osm_edges'].loc[(u, v, 0), 'geometry']
					for successive_stops_shortest_path_osmids in list(map(
						lambda successive_stops: shortest_osmid_paths_df.loc[successive_stops]['shortest_path_osmids'],
						zip(r['nearest_osmids_sequence'][:-1], r['nearest_osmids_sequence'][1:])
					))
						for u, v in zip(
							successive_stops_shortest_path_osmids[:-1],
							successive_stops_shortest_path_osmids[1:]
						)
			]),
			axis=1
		)
