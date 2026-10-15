"""evaluate alias stacks with minimal-change refits. usage: eval1.py WORD.json.gz 'h:L,h:L' [...]  (each arg one stack)
prints per stack: refit changes, new local profile, delta vs word profile"""
import sys, json, gzip, copy
from collections import Counter
from bounds import Bounds, basis, contained, regs
from refit import Refit
import alias_build as mkalias


def apply_stack(path, stack, verbose=False):
    b = Bounds(path); R = Refit(b); Wd = b.Wd; w = Wd.w
    log = []
    for h, L in stack:
        gh = [x for x in b.byreg[h] if x[1] == 'gate'][0][0]
        gl = [x for x in b.byreg[L] if x[1] == 'gate'][-1][0]
        U = R.F(gl); F1 = R.F(gh)
        if len(U) > len(F1):
            X = b.lo[gl]
            if len(X) > len(F1):
                # lower as far as needed: lo, and raise follower to hi
                pass
            r1 = R.lower(gl, X) if len(X) < len(U) else []
            if isinstance(r1, str):
                return None, 'lower-fail ' + r1
            U = R.F(gl)
            r2 = []
            if len(U) > len(F1):
                r2 = R.raise_(gh, b.hi[gh])
                if isinstance(r2, str):
                    return None, 'raise-fail ' + r2
                F1 = R.F(gh)
            if len(U) > len(F1):
                return None, 'still-blocked'
            log.append((h, L, len(r1), len(r2), [(t, len(o), len(n)) for t, o, n in r1], [(t, len(o), len(n)) for t, o, n in r2]))
        else:
            log.append((h, L, 0, 0, [], []))
    # recompute profile on the refit word (before aliasing) as control and then alias
    w = copy.deepcopy(w)
    for h, L in stack:
        # E: a dim|U| subspace of F1 (F1 itself when dims agree, else the lowest |U| basis vectors of F1)
        first = min(p for p, e in enumerate(w['B']) if e[0] != 'warp' and h in mkalias.registers(e))
        U = mkalias.frame_at_B(w, L, first); F1 = basis(w['B'][first][-1])
        E = list(F1) if len(F1) == len(U) else None
        if E is None:
            S = basis(w['start_extra'][str(h)])
            if len(S) == len(U):
                E = list(S)
            elif len(U) < len(F1):
                E = list(F1)[len(F1) - len(U):]
                assert len(basis(E)) == len(U)
            else:
                return None, 'E-choice'
        w, rec = mkalias.alias(w, h, L, E)
    lp, wi = mkalias.profile(w)
    w['report'] = dict(w['report'], local_profile=lp, width_inventory=wi)
    return w, log


if __name__ == '__main__':
    path = sys.argv[1]
    base = mkalias.profile(mkalias.load(path))[0]
    for arg in sys.argv[2:]:
        stack = [tuple(map(int, x.split(':'))) for x in arg.split(',')]
        w, log = apply_stack(path, stack)
        if w is None:
            print(arg, 'FAIL', log); continue
        lp = {int(k): v for k, v in w['report']['local_profile'].items()}
        d = Counter(lp); d.subtract({int(k): v for k, v in base.items()})
        print(arg, 'profile', lp, 'delta', {k: v for k, v in sorted(d.items()) if v}, 'widths', w['report']['width_inventory'])
        for x in log:
            print('   ', x[:4], 'lowered', x[4][:12], 'raised', x[5][:12])
