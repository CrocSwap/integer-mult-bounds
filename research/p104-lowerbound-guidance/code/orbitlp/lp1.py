"""ORBITLP lp1.py: symmetrized first-moment LP over all maximal rectangles of P104 (profiles.txt).
Families: FRAME (>=8 active rows per frame) and DIAG (each port in D∩S of some row). Column generation + exact dual check."""
import numpy as np, sys, highspy
from fractions import Fraction as Fr
from geo import *
import collections
F=frames(); A=aut()
txt=np.loadtxt('profiles.txt',usecols=range(24),dtype=np.int64)
np.save('prof.npy',txt)
