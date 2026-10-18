# SPDX-License-Identifier: Apache-2.0
"""Literal three-by-three matrix audit of #2828's bounded gap tables.

No packed active/dirty correction formula or predecessor implementation is used.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def outer(x, y, n=3):
    return sum(((x >> i) & 1) * ((y >> j) & 1) << (n*i+j)
               for i in range(n) for j in range(n))


@lru_cache(maxsize=None)
def mm(a, b):
    return sum((sum(((a >> (3*i+k)) & 1) * ((b >> (3*k+j)) & 1)
                    for k in range(3)) % 2) << (3*i+j)
               for i in range(3) for j in range(3))


def active(mask):
    return sum(((mask >> (3*i+j)) & 1) << (2*i+j)
               for i in range(2) for j in range(2))


def dirty(mask, orientation):
    if orientation == 'column':  # x has a dirty component: bottom-left row.
        return (mask >> 6) & 3
    return ((mask >> 2) & 1) | (((mask >> 5) & 1) << 2)


def alphabet(orientation):
    xs, ys = (range(1, 8), range(1, 4)) if orientation == 'column' else (range(1, 4), range(1, 8))
    return tuple(sorted(outer(x,y) for x,y in product(xs,ys)))


def single_table(choices, orientation):
    result = []
    for k in range(4):
        counts = Counter()
        for word in product(choices, repeat=k):
            s = 0
            used = 0
            for n in word:
                s ^= n
                used |= bool(dirty(n, orientation))
            counts[active(s), dirty(s, orientation), used] += 1
        result.extend([k, *state, count] for state, count in sorted(counts.items()))
    return result


def joint_table(a_choices, c_choices, a_orientation, c_orientation):
    # A^2=C^2=ACA=CAC=0. Thus only 1, A, C, AC survive within a gap.
    # Retain full 3x3 A/C coefficients; compute products before taking HH.
    tables = {(0,0): {(0,0,0): 1}}
    rows = [[0,0,0,0,0,0,0,1]]
    for total in range(1,5):
        for ka in range(total+1):
            kc = total-ka
            if max(ka,kc)>3:
                continue
            counts = Counter()
            for letter, choices, previous in (
                ('a', a_choices, (ka-1,kc)), ('c', c_choices, (ka,kc-1))):
                for (a,c,q), count in tables.get(previous,{}).items():
                    for n in choices:
                        if letter == 'a':
                            state = (a^n,c,q^active(mm(c,n)))
                        else:
                            state = (a,c^n,q^active(mm(a,n)))
                        counts[state] += count
            tables[ka,kc] = counts
            rows.extend([ka,kc,active(a),dirty(a,a_orientation),active(c),dirty(c,c_orientation),q,count]
                        for (a,c,q),count in counts.items())
    return sorted(rows)


def run():
    result={}
    for case, ao, co in (('I','column','row'),('II','row','column')):
        aa, cc = alphabet(ao), alphabet(co)
        at,ct=single_table(aa,ao),single_table(cc,co)
        joint=joint_table(aa,cc,ao,co)
        result[case]={
            'a_single_sha256':sha256(canonical(at)).hexdigest(),
            'c_single_sha256':sha256(canonical(ct)).hexdigest(),
            'joint_sha256':sha256(canonical(joint)).hexdigest(),
            'joint_states':len(joint),
            'joint_words':sum(row[-1] for row in joint),
        }
    return result


if __name__=='__main__':
    import time
    start=time.perf_counter()
    print(json.dumps(run(),indent=2))
    print('seconds',time.perf_counter()-start)
