from .dg import pt



def create_bus_depot(args, bus_depot):
	del args.func
	bus_depot = pt.BusDepot(**vars(args))
	return bus_depot
	# pt.save_obj_bus_depot(bd, bd.save_directory / f'{bd.name}.pkl')


def load_depot_taluka_osm(args, bus_depot):
	del args.func
	bus_depot.load_osm(**vars(args))
	return bus_depot


def save_depot_file(args, bus_depot):
	pt.save_obj_bus_depot(bus_depot, args.filepath)
	return bus_depot


def load_depot_file(args, bus_depot):
	bus_depot = pt.load_obj_bus_depot(args.filepath)
	return bus_depot


def write_gtfs(args, bus_depot):
	bus_depot.write_gtfs_zipfile(args.directory)
	return bus_depot


def digest_depot(args, bus_depot):
	if args.data_slice == 'stops':
		bus_depot.digest_stops()
	elif args.data_slice == 'routes':
		bus_depot.digest_routes()
	return bus_depot


def save_gpkg(args, bus_depot):
	bus_depot.save_gpkg(args.filepath)
	return bus_depot