import geopandas as gpd


def gtfs_stops_from_msrtc_stops_file(filepath):
    
    stops_df = gpd.read_file(filepath)
    
    gtfs_stops_df = stops_df.drop(['name', 'village', 'taluka', 'latitude', 'longitude'], axis=1)
    gtfs_stops_df['stop_id'], gtfs_stops_df['stop_name'] = stops_df['name'], stops_df['name']
    gtfs_stops_df['stop_lat'], gtfs_stops_df['stop_lon'] = stops_df['latitude'], stops_df['longitude']
    
    return { 'stops': gtfs_stops_df }


def gtfs_stop_times_trips_routes_from_msrtc_form_4(filepath):
    form_4_df = gpd.read_file(filepath)
    
    trips_df = form_4_df[['route_no', 'serviceid']].rename(
        columns={'route_no': 'route_id', 'serviceid': 'trip_id'}
    )
    trips_df.insert(1, 'service_id', 1)

    routes_df = form_4_df[['route_no', 'road_seg']].rename(
        columns={'route_no': 'route_id', 'road_seg': 'route_short_name'}
    ).drop_duplicates()
    routes_df['route_type'] = 3

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
    ]).sort_values(
        by=['trip_id', 'departure_time']
    )

    return {
        'stop_times': stop_times_df,
        'trips': trips_df,
        'routes': routes_df
    }