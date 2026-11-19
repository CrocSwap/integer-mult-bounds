"""Check the three exact orbital solves, class representatives, and independent diagonal probes."""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import flag_weights as F
from compile_row import apply, pairing


def check_pins():
    root = Path(__file__).resolve().parent
    inventory = json.loads((root/'SOURCE-PINS.json').read_bytes())
    expected = {p.relative_to(root).as_posix() for p in (root/'predecessor').rglob('*')
                if p.is_file() and '__pycache__' not in p.parts}
    F.P.require({pin['local'] for pin in inventory} == expected, "retained inventory")
    for pin in inventory:
        content = (root/pin['local']).read_bytes()
        F.P.require(hashlib.sha256(content).hexdigest() == pin['sha256'], "retained SHA256")


def check_inverse():
    data = json.loads((F.P.HERE/'predecessor/source/CLASS-ALGEBRA.json').read_bytes())
    classes = data['classes']
    recip = F.P.class_inverse(data)
    bases, masks, _ = F.spaces()
    # At an aligned marked flag, the full group sum can be averaged over all
    # flags of that type. This uses conjugacy masses directly, independently
    # of the two class operators and their polynomial interpolation.
    census = [Counter() for _ in range(3)]
    for c, k in zip(classes, recip, strict=True):
        s = c['representatives'][0]
        action = [apply(s,v) for v in range(256)]
        fixed = sum(1 << v for v in range(256) if action[v] == v)
        rank = 8 - (fixed.bit_count().bit_length()-1)
        if c['size'] in (255,5355):
            chosen = c['size'] == 5355
            F.P.require(rank == 1 + chosen and
                        all(not pairing(v,action[v]^v) for v in range(256)) == chosen,
                        "pinned transvection and alternating rank-two classes")
        counts = [Counter() for _ in range(3)]
        for B,L in zip(bases,masks,strict=True):
            X = F.P.point_set(tuple(action[v] for v in B))
            j = F.P.distance(L, X)
            n = (L & fixed).bit_count()
            for counter,value in zip(counts,(1,n-1,fixed.bit_count()-n),strict=True):
                counter[j] += value
        for acc, by_shell in zip(census,counts,strict=True):
            for j,m in by_shell.items():
                acc[j] += c['size']*k*m
    for root, dim, orbit_count, totals in zip((0,1,16),(2295,34425,550800),
                                               (28,77,249),census,strict=True):
        labels, reps = F.orbits(root)
        F.P.require(len(reps) == orbit_count and len(labels) == 587520, "orbit count")
        sol = F.solution(root)
        raw = tuple(F.rhs(F.P.distance(F.BASE,masks[i])) if w == root else Fraction(0)
                    for i,w in reps)
        F.P.require(F.apply_gram(root,sol,False) == raw, "full orbital normal equations")
        aligned = sum(F.rhs(j)*n for j,n in totals.items())/dim
        F.P.require(F.weight(F.BASE,root,F.BASE,root) == aligned, "direct central inverse probe")
    print("PASS all 354 orbital equations, both conjugacy classes and three direct inverse probes")


if __name__ == '__main__':
    check_pins()
    check_inverse()
