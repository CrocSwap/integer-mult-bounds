#!/usr/bin/env python3
"""Independent binary controls for PR144 arbitrary-subspace frame identities.

Apache-2.0. Maintainer review with OpenAI Codex assistance. Exhaustive in
dimensions 2 through 4, including degenerate subspaces. Binary identities do
not establish exact Gaussian phases or tape complexity; those need proof.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
from itertools import product
import json


def spaces(h):
    found = {frozenset([0])}
    pending = list(found)
    while pending:
        U = pending.pop()
        for v in range(1 << h):
            if v not in U:
                V = frozenset(U | {u^v for u in U})
                if V not in found:
                    found.add(V)
                    pending.append(V)
    return found


def check():
    pair_count = complement_count = degenerate_count = 0
    for h in (2,3,4):
        all_spaces = spaces(h)
        assert len(all_spaces) == {2:5,3:16,4:67}[h]
        def dim(U):
            assert len(U)&(len(U)-1)==0
            return len(U).bit_length()-1
        def perp(U):
            return frozenset(v for v in range(1 << h) if all((u&v).bit_count()%2==0 for u in U))
        labels = {U:frozenset((u,u^v) for u in U for v in perp(U)) for U in all_spaces}
        for U,L in labels.items():
            assert len(L)==1<<h
            assert all(((x&zz).bit_count()+(z&xx).bit_count())%2==0
                       for x,z in L for xx,zz in L)
            assert frozenset((x^z,z) for x,z in L)==labels[perp(U)]
            degenerate_count += int(len(U&perp(U))>1)
            for V in all_spaces:
                distance = h-dim(L&labels[V])
                assert distance == dim(U)+dim(V)-2*dim(U&V)
                pair_count += 1
                if len(U&V)==1 and dim(U)+dim(V)==h:
                    for A in all_spaces:
                        if U <= A:
                            assert h-dim(labels[A]&labels[V]) == h-dim(A)+dim(U)
                            complement_count += 1
    return dict(status='PASS', pair_distance_identities=pair_count,
                dirty_tail_complement_identities=complement_count,
                degenerate_subspaces=degenerate_count,
                scope='Exhaustive small binary geometry only; exact lifts and all-size costs reviewed in prose')


if __name__=='__main__':
    print(json.dumps(check(),indent=2))
