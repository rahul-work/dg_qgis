import os
import copy
import pickle
from pathlib import Path
import zipfile

import shapely
import pandas as pd
import geopandas as gpd
import osmnx

from .. import osm

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
		'data': {
			'stops': None,
			'form_4': None,
			'osm_graph': None,
		},
		'GPKG': {
			'dg_stops': None,
			'dg_routes': None,
			'dg_POIs': None,
		},
		'GTFS': {
			'agency': None,
			'stops': None,
			'routes': None,
			'trips': None,
			'stop_times': None,
			'calendar': None,
		},
	}
	

	def __init__(self, /,
		user_id: str|None = None,
		name: str|None = 'bus_depot',
		data_directory: os.PathLike|None = None
	) -> None:
		
		self.user_id = user_id
		self.name = name
		self.data_directory = data_directory
		
		self.data_dict = copy.deepcopy(self.POTENTIAL_DATA)
		if data_directory is not None:
			if not isinstance(data_directory, Path):
				data_directory = Path(data_directory)
			self.read_data_directory(data_directory)
		

	def read_data_directory(self, dirpath):
		if not isinstance(dirpath, Path):
			dirpath = Path(dirpath)
		for k in self.data_dict['data'].keys():
			if k in ['osm_graph']:
				continue
			self.data_dict['data'][k] = pd.read_csv(dirpath / f'{k}.csv')
	

	def load_osm(self, district=None, taluka=None):
		graph_and_polygon = osm.load_osm_within_taluka(district, taluka, f'{district}_{taluka}', False, None)
		self.data_dict['data']['osm_graph'] = graph_and_polygon['graph']
		self.data_dict['GPKG']['region'] = graph_and_polygon['taluka_polygon']

	
	def _sources_to_gtfs(self):
		
		# agency.txt
		self.data_dict['GTFS']['agency'] = """agency_id,agency_name,agency_url,agency_timezone
MSRTC,Maharashtra State Road Transport Corporation,https://msrtc.maharashtra.gov.in/,Asia/Kolkata
"""

		#stops.txt
		stops_df = self.data_dict['data']['stops'].rename(columns={
			'name': 'stop_id', 'latitude': 'stop_lat', 'longitude': 'stop_lon'
		})[['stop_id', 'stop_lat', 'stop_lon']]
		stops_df.insert(1, 'stop_name', stops_df['stop_id'])
		stops_df.set_index('stop_id', inplace=True)
		self.data_dict['GTFS']['stops'] = stops_df

		#stop_times.txt
		form_4_df =  self.data_dict['data']['form_4']
		form_4_df = form_4_df[(form_4_df['s_eng'].isin(stops_df.index)) & (form_4_df['d_eng'].isin(stops_df.index))]
		stop_times_srcs_df = form_4_df[['serviceid', 'arrival', 's_eng']].rename(
			columns={'serviceid': 'trip_id', 'arrival': 'arrival_time', 's_eng': 'stop_id'}
		)
		stop_times_srcs_df.insert(2, 'departure_time', stop_times_srcs_df['arrival_time'])
		stop_times_srcs_df['stop_sequence'] = 1
		stop_times_dests_df = form_4_df[['serviceid', 'depart', 'd_eng']].rename(
			columns={'serviceid': 'trip_id', 'depart': 'arrival_time', 'd_eng': 'stop_id'}
		)
		stop_times_dests_df.insert(2, 'departure_time', None)
		stop_times_dests_df['stop_sequence'] = 2
		stop_times_df = pd.concat([
			stop_times_srcs_df, stop_times_dests_df
		]).sort_values(by=[
			'trip_id', 'departure_time'
		])
		self.data_dict['GTFS']['stop_times'] = stop_times_df

		#trips.txt
		trips_df = self.data_dict['data']['form_4'][['route_no', 'serviceid']].rename(
			columns={'route_no': 'route_id', 'serviceid': 'trip_id'}
		)
		trips_df.insert(1, 'service_id', 1)
		trips_df.set_index('trip_id', inplace=True)
		self.data_dict['GTFS']['trips'] = trips_df

		#routes.txt
		routes_df = self.data_dict['data']['form_4'][['route_no', 'road_seg']].rename(
			columns={'route_no': 'route_id', 'road_seg': 'route_short_name'}
		).drop_duplicates()
		routes_df['route_type'] = 3
		routes_df.set_index('route_id', inplace=True)
		self.data_dict['GTFS']['routes'] = routes_df
		
		#calendar.txt
		# tentative
		self.data_dict['GTFS']['calendar'] = """service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
1,1,1,1,1,1,1,1,20230101,20231201
2,1,1,1,1,1,0,0,20230101,20231201"""

	
	def write_gtfs_zipfile(self, dirpath):
		if not isinstance(dirpath, Path):
			dirpath = Path(dirpath)
		if not os.path.exists(Path(dirpath)):
			os.mkdir(dirpath)
		self._sources_to_gtfs()
		with zipfile.ZipFile(Path(dirpath) / 'gtfs.zip', 'w') as zf:
			for filename, filedata in self.data_dict['GTFS'].items():
				print(filedata)
				filepath = dirpath / f'{filename}.txt'
				if filedata is None:
					continue
				if type(filedata) == str:
					with open(filepath, 'w') as f:
						f.write(filedata)
				elif filename == 'stop_times':
					filedata.to_csv(filepath, index=False)
				else:
					filedata.to_csv(filepath)
				zf.write(filepath, arcname=filename)
	
	
	def save_gpkg(self, filepath):
		osmnx.save_graph_geopackage(self.data_dict['data']['osm_graph'], filepath)
		for name, gdf in self.data_dict['GPKG'].items():
			if gdf is None or 'osm' in name:
				continue
			gdf.to_file(filepath, driver='GPKG', layer=name)
	
	def digest(self):
		self._sources_to_gtfs()
		self.digest_stops()
		self.digest_routes()	


	def digest_stops(self):
		if self.data_dict['GTFS']['stops'] is None:
			self._sources_to_gtfs()
		stops_df = self.data_dict['GTFS']['stops']
		dg_stops_gdf = gpd.GeoDataFrame(
			stops_df,
			geometry=gpd.points_from_xy(stops_df['stop_lon'], stops_df['stop_lat']),
			crs='EPSG:4326'
		)
		self.data_dict['GPKG']['dg_stops'] = dg_stops_gdf
		
		# west, south, east, north = dg_stops_gdf.geometry.total_bounds
		# buffer = 0.1*max(abs(north-south), abs(east-west))
		# osm_graph = osmnx.graph_from_bbox(north+buffer, south-buffer, east+buffer, west-buffer)
		if self.data_dict['data']['osm_graph'] is None:
			return
		osm_nodes, osm_edges = osmnx.graph_to_gdfs(self.data_dict['data']['osm_graph'])
		self.data_dict['GPKG']['osm_nodes'], self.data_dict['GPKG']['osm_edges'] = osm_nodes, osm_edges

		dg_stops_gdf['nearest_osm_node_osmid'] = osmnx.nearest_nodes(
			self.data_dict['data']['osm_graph'],
			dg_stops_gdf['stop_lon'], dg_stops_gdf['stop_lat']
		)
		dg_stops_nearest_nodes = dg_stops_gdf.join(
			osm_nodes, on='nearest_osm_node_osmid', lsuffix='_stops'
		)[['nearest_osm_node_osmid', 'geometry']]
		self.data_dict['GPKG']['dg_stops_nearest_nodes'] = dg_stops_nearest_nodes
		
		dg_stops_route_to_nearest_node = dg_stops_gdf.join(dg_stops_nearest_nodes, lsuffix='_stops')
		dg_stops_route_to_nearest_node['geometry'] = dg_stops_route_to_nearest_node.apply(
			lambda r: shapely.geometry.LineString([r['geometry_stops'], r['geometry']]),
			axis=1
		)
		dg_stops_route_to_nearest_node = gpd.GeoDataFrame(
			dg_stops_route_to_nearest_node[['nearest_osm_node_osmid', 'geometry']]
		)
		self.data_dict['GPKG']['dg_stops_route_to_nearest_node'] = dg_stops_route_to_nearest_node
		
		
	def digest_routes(self):
		if self.data_dict['GTFS']['stop_times'] is None:
			self._sources_to_gtfs()
		stop_times_df = self.data_dict['GTFS']['stop_times']
		
		if self.data_dict['GPKG']['dg_stops'] is None:
			self.digest_stops()
		trips_stops_temp_gdf = stop_times_df.merge(self.data_dict['GPKG']['dg_stops'], on='stop_id')[
			['trip_id', 'stop_id', 'stop_sequence', 'geometry']
		].rename(columns={'geometry': 'stop_geometry'})
		def stops_id_and_geom(gb_df):
			stops_in_sequence = gb_df.sort_values(['stop_sequence'])
			return pd.Series({
				'stops_in_sequence': ','.join(stops_in_sequence['stop_id']),
				'nearest_osmids_sequence': list(stops_in_sequence.merge(
					self.data_dict['GPKG']['dg_stops'], on='stop_id'
				)['nearest_osm_node_osmid'])
			})
		trips_gdf = trips_stops_temp_gdf.groupby(['trip_id']).apply(stops_id_and_geom)
		
		Xs = []; Ys = []
		for idx, row in trips_gdf.iterrows():
			Xs.extend(row['nearest_osmids_sequence'][:-1])
			Ys.extend(row['nearest_osmids_sequence'][1:])
		Xs, Ys = list(zip(*list(set(zip(Xs, Ys)))))
		shortest_osmid_paths_df = pd.DataFrame({
			'X': Xs, 'Y': Ys, 'shortest_path_osmids': osmnx.shortest_path(
				self.data_dict['data']['osm_graph'], Xs, Ys
			)
		}).set_index(['X', 'Y'])
		
		_, osm_edges = osmnx.graph_to_gdfs(self.data_dict['data']['osm_graph'])
		trips_gdf['shortest_path_route_geometry'] = trips_gdf.apply(
			lambda r: shapely.geometry.MultiLineString([
				osm_edges.loc[(u, v, 0), 'geometry']
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
		trips_gdf['nearest_osmids_sequence'] = ','.join(str(trips_gdf['nearest_osmids_sequence']))

		self.data_dict['GPKG']['trips'] = gpd.GeoDataFrame(
			trips_gdf, geometry='shortest_path_route_geometry'
		)


def save_obj_bus_depot(bus_depot, filepath):
	if not isinstance(filepath, Path):
		filepath = Path(filepath)
	with open(filepath, 'wb') as f:
		pickle.dump(bus_depot, f)

def load_obj_bus_depot(filepath):
	if not isinstance(filepath, Path):
		filepath = Path(filepath)
	with open(filepath, 'rb') as f:
		bus_depot = pickle.load(f)
	return bus_depot