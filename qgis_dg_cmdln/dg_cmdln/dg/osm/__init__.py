import os.path
from pathlib import Path
import json

import osmnx
import networkx
import pandas as pd
import geopandas as gpd

# purely for 'export'
from . import utils


def load_osm_around_point(lat, lon, bbox_dist_mts, name, no_simplify, func):
	try:
		graph = osmnx.graph_from_point(
			(lat, lon), dist=bbox_dist_mts, simplify=not no_simplify
		)
	except networkx.exception.NetworkXPointlessConcept:
		return {'type': 'message', 'message': "No location/route in the given region!"}
	
	osmnx.save_graphml(graph, Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{name}.graphml")
	filepath = Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{name}.gpkg"
	osmnx.save_graph_geopackage(graph, filepath)
	return {
		'type': 'add layers from file',
		'layers': [{
			'title': name,
			'filepath': str(filepath)
		}]
	}
	# return 'osmnx usage begins'
	# return get_response_for_osm_load(graph, name)
	# return resp['layers'][1]['geojson']


def load_osm_within_taluka(district, taluka, name, no_simplify, func):
	taluka_polygons_filepath = (Path(os.path.dirname(__file__)) / '..' / 'ref_data' / 'state_Maharashtra_talukas_geom.json').resolve()
	talukas_gdf = gpd.read_file(taluka_polygons_filepath)
	polygon_gdf = talukas_gdf.loc[(talukas_gdf['district'] == district) & (talukas_gdf['label'] == taluka)]

	dirpath = Path(r'D:\iitbgis\work\Transport\data\workspace')
	region_boundary_layer_name = f'{name} - district {district} taluka {taluka}'
	filepath = dirpath / f"{name}.gpkg"
	try:
		graph = osmnx.graph_from_polygon(polygon_gdf['geometry'].iloc[0], simplify=not no_simplify)
	except networkx.exception.NetworkXPointlessConcept:
		return {'type': 'message', 'message': "No location/route in the given region!"}
	
	return {
		'graph': graph,
		'taluka_polygon': polygon_gdf
	}
	
	# response = get_response_for_osm_load(workspace, graph, name)
	# filepath = dirpath / f'{name}.gpkg'
	osmnx.save_graphml(graph, Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{name}.graphml")
	osmnx.save_graph_geopackage(graph, filepath)

	polygon_gdf.to_file(
		filepath, driver='GPKG', layer=region_boundary_layer_name
	)
	
	return {
		'type': 'add layers from file',
		'layers': [{
			'title': name,
			'filepath': str(filepath)
		# }, {
		# 	'title': region_boundary_layer_name,
		# 	'filepath': str(polygon_filepath)
		}]
	}
	# workspace[name]['associated_layers'].append(region_boundary_layer_name)
	# response['layers'].append({
	# 	'title': region_boundary_layer_name,
	# 	'geojson': json.loads(polygon_gdf.to_json())
	# })
	# return response


def get_response_for_osm_load(graph, name):
	# gdf_nodes, gdf_edges = osmnx.graph_to_gdfs(graph)
	
	# nodes_layer_name, edges_layer_name = f'{name} - nodes', f'{name} - edges'
	# workspace[name] = {
	# 	'type': 'graph',
	# 	'value': graph,
	# 	'associated_layers': [nodes_layer_name, edges_layer_name]
	# }
	osmnx.save_graphml(graph, Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{name}.graphml")
	osmnx.save_graph_geopackage(graph, Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{name}.gpkg")

	return {
		'type': 'add layer-group',
		'title': name,
		# 'layers': [{
		# 	'title': 'nodes',
		# 	# 'geojson': gdf_nodes.to_json(),
		# 	'filename': nodes_layer_name
		# }, {
		# 	'title': 'edges',
		# 	# 'geojson': gdf_edges.to_json()
		# 	'filename': edges_layer_name
		# }],
		# 'extent_layer_title': name
	}


def shortest_path(origin, destination, osm_layer, func):
	graph = osmnx.load_graphml(Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{osm_layer}.graphml")
	path = osmnx.shortest_path(graph, origin, destination)
	segments = [(path[i], path[i+1]) for i in range(len(path)-1)]

	edges_gdf = osmnx.graph_to_gdfs(graph, nodes=False, node_geometry=False)
	layer_name = f"{origin}_{destination}_shortest_path_using_{osm_layer}"
	filepath = Path(r'D:\iitbgis\work\Transport\data\workspace') / f"{layer_name}.gpkg"
	edges_gdf.to_file(
		filepath, driver='GPKG', layer="shortest_path"
	)

	return {
		'type': 'add layers from file',
		'layers': [{
			'title': layer_name,
			'filepath': str(filepath)
		}]
	}


def load_osm_within_bbox(north, south, east, west, func):
	graph = osmnx.graph_from_bbox(north, south, east, west)
	