from .cmd_parser import create_parser, create_pt_parser


def handle(cmd):
	try:
		p = create_parser()
		args = p.parse_args(cmd.split())
	except Exception as e:
		return p.format_help()
		# return repr(e)
	# return str(args)
	return args.func(**vars(args))


# if __name__ == '__main__':
bus_depot = None
while True:
	cmd = input('cmd>')
	if cmd == 'exit':
		exit(0)
	print(cmd.split())
	args = create_pt_parser().parse_args(cmd.split())
	# print(args)
	bus_depot = args.func(args, bus_depot)