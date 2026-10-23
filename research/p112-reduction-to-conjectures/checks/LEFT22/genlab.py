# writes lines.txt: 120 lines: label9 and doubled coords (impl A numbering = CARRIER lib order)
import sys; sys.path.insert(0,'../CARRIER')
from lib import *
with open('lines.txt','w') as f:
    for t in range(n): f.write('%d %s\n'%(lab[t],' '.join(map(str,lines[t]))))
