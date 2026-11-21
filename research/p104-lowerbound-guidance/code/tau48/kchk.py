import sys,numpy as np
from kphi import kbound
for f in sys.argv[1:]: kbound(np.load('g_W_%s.npy'%f),np.load('g_V_%s.npy'%f),f)
