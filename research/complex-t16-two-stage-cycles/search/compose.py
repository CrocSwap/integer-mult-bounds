"""Composition test: apply each subset of PR2077's relocations to another owner map. argv: LIBDIR BASE_OWNERS PR2077_OWNERS"""
import sys, itertools, json; sys.path.insert(0, sys.argv[1]); import lib
A = lib.selroles; P = lib.read(sys.argv[2]); V = lib.read(sys.argv[3])
key = lambda z: (z['owner_replica'], z['child'], z['port'])
d77 = [i for i in range(len(A)) if key(A[i]) != key(V[i])]
print('2077 relocations', d77, 'state in 1407:', [(i, key(A[i]), key(P[i]), key(V[i])) for i in d77])
for r in range(1, len(d77)+1):
    for sub in itertools.combinations(d77, r):
        m = lib.Limbo(P); m._out = set(); ok = True
        for i in sub: m.lift(i)
        for i in sub:
            if not m.put(i, key(V[i])): ok = False; break
        if not ok: print(sub, 'illegal'); continue
        roles = lib.compact(m.roles)
        try: au = lib.audit(roles)
        except Exception as e: print(sub, 'audit reject', e); continue
        print(sub, 'idle', au['idle'], 'kappa', lib.price(au['profile'])['kappa_decimal'])
