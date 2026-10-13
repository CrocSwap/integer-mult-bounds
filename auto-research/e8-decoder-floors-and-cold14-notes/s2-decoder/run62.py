import sys
from dec9sat import *
P = [int(x) for x in sys.argv[1].split(',')]
print('result', check_budget(P, int(sys.argv[2])))
