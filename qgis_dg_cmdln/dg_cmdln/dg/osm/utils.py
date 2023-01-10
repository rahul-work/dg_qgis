import random
import pandas as pd
import shapely



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
