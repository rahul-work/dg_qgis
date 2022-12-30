import sys
import argparse

from . import cmd_effects
from .dg import osm
from .dg import pt


class ArgumentParserWithErrorCatching(argparse.ArgumentParser):
	# def error(self, message):
	# 	return self.format_help() + message
	pass


def create_pt_parser():
	Parser = argparse.ArgumentParser(prog='DG-PT')
	subparsers = Parser.add_subparsers()

	parser_create_pt = subparsers.add_parser('create-bus-depot')
	parser_create_pt.add_argument('--data-directory', required=True)
	parser_create_pt.add_argument('--user-id')
	parser_create_pt.add_argument('--name', default='bus_depot')
	parser_create_pt.set_defaults(func=cmd_effects.create_bus_depot)

	parser_load_osm = subparsers.add_parser('load-depot-taluka-osm')
	parser_load_osm.add_argument('--district', required=True)
	parser_load_osm.add_argument('--taluka', required=True)
	parser_load_osm.set_defaults(func=cmd_effects.load_depot_taluka_osm)

	parser_save_bus_depot_file = subparsers.add_parser('save-to-file')
	parser_save_bus_depot_file.add_argument('--filepath', required=True)
	parser_save_bus_depot_file.set_defaults(func=cmd_effects.save_depot_file)
	
	parser_load_bus_depot_file = subparsers.add_parser('load-from-file')
	parser_load_bus_depot_file.add_argument('--filepath', required=True)
	parser_load_bus_depot_file.set_defaults(func=cmd_effects.load_depot_file)

	parser_write_gtfs = subparsers.add_parser('write-gtfs-zipfile')
	parser_write_gtfs.add_argument('--directory', required=True)
	parser_write_gtfs.set_defaults(func=cmd_effects.write_gtfs)

	parser_digest_bus_depot = subparsers.add_parser('digest')
	parser_digest_bus_depot.add_argument('--data-slice', choices=['stops', 'routes'], required=True)
	parser_digest_bus_depot.set_defaults(func=cmd_effects.digest_depot)

	parser_save_depot_gpkg = subparsers.add_parser('save-layers-gpkg')
	parser_save_depot_gpkg.add_argument('--filepath', required=True)
	parser_save_depot_gpkg.set_defaults(func=cmd_effects.save_gpkg)
	
	# load_osm_within_region = load_subparsers.add_parser('osm-within-taluka')
	# load_osm_within_region.add_argument('--district', required=True)
	# load_osm_within_region.add_argument('--taluka', required=True)
	# load_osm_within_region.add_argument('--name', required=True)
	# load_osm_within_region.add_argument('--no-simplify', action='store_true')
	# load_osm_within_region.set_defaults(func=osm.load_osm_within_taluka)

	# # unload_parser = subparsers.add_parser('unload')
	# # unload_parser.add_argument('--names', nargs='+')
	# # unload_parser.set_defaults(func=handlers.unload)

	# upload_parser = subparsers.add_parser('upload')
	# upload_subparsers = upload_parser.add_subparsers()

	# upload_pt_stops = upload_subparsers.add_parser('pt-stops')
	# upload_pt_stops.add_argument('--csv-file', type=argparse.FileType('r'), required=True)
	# upload_pt_stops.add_argument('--name', required=True)
	# upload_pt_stops.set_defaults(func=pt.read_stops)

	# calculate_parser = subparsers.add_parser('calculate')
	# calculate_subparsers = calculate_parser.add_subparsers()

	# calculate_osm_shortest_path = calculate_subparsers.add_parser('osm-shortest-path')
	# calculate_osm_shortest_path.add_argument('-o', '--origin', type=int, required=True)
	# calculate_osm_shortest_path.add_argument('-d', '--destination', type=int, required=True)
	# calculate_osm_shortest_path.add_argument('--osm-layer', required=True)
	# calculate_osm_shortest_path.set_defaults(func=osm.shortest_path)
	# # download_parser = subparsers.add_parser('download')
	# # download_parser.add_argument('--name', required=True)
	# # download_parser.add_argument('--gpkg-filepath', required=True)
	# # download_parser.set_defaults(func=handlers.download)

	return Parser




def create_parser():
	Parser = ArgumentParserWithErrorCatching(prog='DG')
	subparsers = Parser.add_subparsers()

	load_parser = subparsers.add_parser('load')
	load_subparsers = load_parser.add_subparsers()

	load_osm_around_point = load_subparsers.add_parser('osm-around-point')
	load_osm_around_point.add_argument('--lat', type=float)
	load_osm_around_point.add_argument('--lon', type=float)
	load_osm_around_point.add_argument('--bbox-dist-mts', type=float)
	load_osm_around_point.add_argument('--name', required=True)
	load_osm_around_point.add_argument('--no-simplify', action='store_true')
	load_osm_around_point.set_defaults(func=osm.load_osm_around_point)

	load_osm_within_region = load_subparsers.add_parser('osm-within-taluka')
	load_osm_within_region.add_argument('--district', required=True)
	load_osm_within_region.add_argument('--taluka', required=True)
	load_osm_within_region.add_argument('--name', required=True)
	load_osm_within_region.add_argument('--no-simplify', action='store_true')
	load_osm_within_region.set_defaults(func=osm.load_osm_within_taluka)

	# unload_parser = subparsers.add_parser('unload')
	# unload_parser.add_argument('--names', nargs='+')
	# unload_parser.set_defaults(func=handlers.unload)

	upload_parser = subparsers.add_parser('upload')
	upload_subparsers = upload_parser.add_subparsers()

	upload_pt_stops = upload_subparsers.add_parser('pt-stops')
	upload_pt_stops.add_argument('--csv-file', type=argparse.FileType('r'), required=True)
	upload_pt_stops.add_argument('--name', required=True)
	upload_pt_stops.set_defaults(func=pt.read_stops)

	calculate_parser = subparsers.add_parser('calculate')
	calculate_subparsers = calculate_parser.add_subparsers()

	calculate_osm_shortest_path = calculate_subparsers.add_parser('osm-shortest-path')
	calculate_osm_shortest_path.add_argument('-o', '--origin', type=int, required=True)
	calculate_osm_shortest_path.add_argument('-d', '--destination', type=int, required=True)
	calculate_osm_shortest_path.add_argument('--osm-layer', required=True)
	calculate_osm_shortest_path.set_defaults(func=osm.shortest_path)
	# download_parser = subparsers.add_parser('download')
	# download_parser.add_argument('--name', required=True)
	# download_parser.add_argument('--gpkg-filepath', required=True)
	# download_parser.set_defaults(func=handlers.download)

	return Parser


if __name__ == '__main__':
	print('load --lat 18.75 --lon 73.75 --bbox-dist-mts 2000 --name lat_1875_lon_7375 --no-simplify'.split())
	print(create_parser().parse_args(
		'load --lat 18.75 --lon 73.75 --bbox-dist-mts 2000 --name lat_1875_lon_7375 --no-simplify'.split()
	))