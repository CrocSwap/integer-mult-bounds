"""Produce only the two changed native recipes with the retained compiler."""
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from common import authenticate,need


def main():
    need(__debug__, 'The retained producer requires assertions')
    word,specs = authenticate()
    spec = importlib.util.spec_from_file_location('retained_clifford',P/'inputs/clifford_exact.py')
    C = importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
    records = []
    for item in specs:
        a,b = item['E'],item['G']
        left = C.canonical_frame(9,tuple(word['frames'][a]))
        right = C.canonical_frame(9,tuple(word['frames'][b]))
        recipe,compiled = C.lower_child(left.adjoint().then(right))
        need(recipe['rank'] == 5, 'Exact changed rank')
        records.append(dict(old=a,new=b,role=item['role'],recipe=recipe,circuit=compiled.circuit))
    print(json.dumps(records,sort_keys=True,separators=(',',':')))


if __name__ == '__main__': main()
