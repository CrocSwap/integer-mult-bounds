#!/usr/bin/env python3
"""IMMUTABLE. Runs the lane's producer.py in its own process and serializes its DAG (evaluate.py never imports it).
Producer contract: module constant H (int), build_side(C, h) -> dict(out={(c, T): node for every triple T and c in T},
ret={c: node for every point c})."""
import sys, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from circuit import BitCircuit

lane, out_path = os.path.abspath(sys.argv[1]), sys.argv[2]
sys.path.insert(0, lane)
spec = importlib.util.spec_from_file_location('producer', os.path.join(lane, 'producer.py'))
prod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prod)
h = int(getattr(prod, 'H', 23))
C = BitCircuit(h)
res = prod.build_side(C, h)
v = C.v
json.dump(dict(h=h, args=[list(C.args[x]) for x in range(v + 1, len(C.args))],
               out=[[c, list(T), res['out'][(c, T)]] for T in C.triples for c in T],
               ret=[res['ret'][c] for c in range(h)]), open(out_path, 'w'))
