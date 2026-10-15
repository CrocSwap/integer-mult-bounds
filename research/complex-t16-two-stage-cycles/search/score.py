"""Print the exact kappa (pinned engines) and idle profile of owner maps. argv: LIBDIR OWNERS..."""
import sys; sys.path.insert(0, sys.argv[1]); import lib
for f in sys.argv[2:]:
    au = lib.audit(lib.read(f)); print(f, lib.price(au['profile'])['kappa_decimal'], au['idle'], flush=True)
