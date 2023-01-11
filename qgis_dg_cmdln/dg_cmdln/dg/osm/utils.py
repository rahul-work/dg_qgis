import random
import pandas as pd
import shapely, geopandas as gpd, osmnx as ox



def path_geometry_from_osmids(edges_gdf, osmids):
	return shapely.geometry.MultiLineString([
		edges_gdf.loc[(u, v, 0), 'geometry'] for u, v in zip(osmids[:-1], osmids[1:])
	])


def random_OD_pairs(nodes, N: int) -> list[tuple[int, int]]:
	n = N # n is 'remaining to be sampled'
	origin_destination_pairs_collection = []
	while N > 0:
		sample_nodes = random.sample(list(nodes.index), 2*n)
		Os, Ds = sample_nodes[:n], sample_nodes[n:]
		OD_df = pd.DataFrame({'origin': Os, 'destination': Ds})
		OD_df = OD_df[OD_df['origin'] != OD_df['destination']]
		origin_destination_pairs_collection.append(OD_df)
		n -= len(OD_df)
		if n == 0:
			break
	return pd.concat(origin_destination_pairs_collection)


def edge_congestion(row, power):
	if row['highway'] in ['primary', 'trunk']:
		return row['length']/pow(1.5, power)
	elif row['highway'] in ['secondary', 'service']:
		return row['length']/pow(1.2, power)
	else:
		return row['length']


def actual_static_congestion(OD_df, seq_col, edges_gdf):
	num_routes = pd.Series([0]*len(edges_gdf), index=edges_gdf.index)
	for idx, row in OD_df.iterrows():
		for u, v in zip(row[seq_col][:-1], row[seq_col][1:]):
			num_routes.loc[(u, v, 0)] += 1
	return num_routes


def snap_path(path: shapely.geometry.LineString, graph, edges_gdf=None) -> shapely.geometry.MultiLineString:
	Xs, Ys = list(zip(*(path.coords)))
	nrst_edges = ox.nearest_edges(graph, Xs, Ys)
	
	nrst_edge_us, nrst_edge_vs, nrst_edge_keys = zip(*nrst_edges)
	
	path_vertices_nearest_edges = pd.DataFrame({
		'X': Xs, 'Y': Ys,
		'nearest_edge_u': nrst_edge_us, 'nearest_edge_v': nrst_edge_vs, 'nearest_edge_key': nrst_edge_keys
	})

	if edges_gdf is None:
		_, edges_gdf = ox.graph_to_gdfs(graph)
	snap_vertices_osmids = []
	for idx, row in path_vertices_nearest_edges.iterrows():
		path_vertex = shapely.geometry.Point(row['X'], row['Y'])
		nrst_edge = edges_gdf.loc[
			(row['nearest_edge_u'], row['nearest_edge_v'], row['nearest_edge_key']),
			'geometry'
		]
		nrst_edge_vertices = [shapely.geometry.Point(*cc) for cc in nrst_edge.coords]
		nrst_edge_nrst_vertex_osmid = int(row['nearest_edge_u'] if (
			path_vertex.distance(nrst_edge_vertices[0]) < path_vertex.distance(nrst_edge_vertices[1])
		) else row['nearest_edge_v'])
		snap_vertices_osmids.append(nrst_edge_nrst_vertex_osmid)

	consecutive_shortest_paths = ox.shortest_path(graph, snap_vertices_osmids[:-1], snap_vertices_osmids[1:])
	snap_path_osmids = [consecutive_shortest_paths[0][0]] + [
		osmid for sp in consecutive_shortest_paths for osmid in sp[1:]
	]

	# eliminate cycles
	final_snap_path_osmids = []
	while True:
		if snap_path_osmids[0] in snap_path_osmids[1:]:
			# take the last such;
			# it is worth validating the following index-calculation code;
			# it hasn't been, as of this comment
			snap_path_osmids = snap_path_osmids[ (
				len(snap_path_osmids)-1 - snap_path_osmids[::-1].index(snap_path_osmids[0])
			): ]
			continue
		final_snap_path_osmids.append(snap_path_osmids[0])
		if len(snap_path_osmids) == 1:
			break
		snap_path_osmids = snap_path_osmids[1:]


	return {
		'snap_vertices_osmids': snap_vertices_osmids,
		'snap_path_osmids': final_snap_path_osmids,
		'snap_path': path_geometry_from_osmids(edges_gdf, snap_path_osmids)
	}

