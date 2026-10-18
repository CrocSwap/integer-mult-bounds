# Compatibility shim: the working cards import their E8 setup as `blib`; here it is e8lib (same line order, so CNF regeneration is byte-identical).
import sys, itertools, pickle
from e8lib import *
