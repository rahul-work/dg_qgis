from .cmd_parser import create_parser


def handle(cmd):
	try:
		p = create_parser()
		args = p.parse_args(cmd.split())
	except Exception as e:
		return p.format_help()
		# return repr(e)
	# return str(args)
	return args.func(**vars(args))


if __name__ == '__main__':
	args = create_parser().parse_args()
	print(args)
	print( args.func(**vars(args)) )