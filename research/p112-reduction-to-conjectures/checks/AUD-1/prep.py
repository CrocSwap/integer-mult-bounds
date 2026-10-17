import sys,pickle; sys.path.insert(0,'.')
from e8 import *
F=frames(); print('frames',len(F))
M=flats7(); print('distinct 7-flat masks',len(M))
pickle.dump((F,M),open('fm.pkl','wb'))
with open('base.txt','w') as f:
    f.write(' '.join(map(str,lab))+'\n'+str(len(M))+'\n')
    for m in M: f.write('%d %d\n'%(m&((1<<64)-1),m>>64))
