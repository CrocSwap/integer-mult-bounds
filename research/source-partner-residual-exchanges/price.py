"""Independent exact rational enclosure of the literal candidate profile's moment.

Uses Colkitt's pinned exact interval engine, without its historical outer map.
Apache-2.0; OpenAI Codex assistance. This check alone does not admit an outer κ.
"""
import argparse
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location('exact_ceiling', HERE.parent/'complex-local-word-ceiling/ceiling.py')
engine = importlib.util.module_from_spec(sp)
sp.loader.exec_module(engine)


def price(profile):
    if not __debug__:
        raise RuntimeError('Assertions are required')
    def moment(a):
        costs = [(n, engine.child_cost(int(r), 73, a)) for r, n in profile.items()]
        return (sum(n*c[0] for n, c in costs)/66304,
                sum(n*c[1] for n, c in costs)/66304)
    lo, hi, grid = Q(0), Q(1, 100), Q(1, 10**24)
    assert moment(lo)[1] < 1 < moment(hi)[0]
    while hi-lo > grid:
        mid = (int((lo+hi)/2/grid))*grid
        mid = max(mid, lo+grid)
        low, high = moment(mid)
        if high < 1:
            lo = mid
        elif low > 1:
            hi = mid
        else:
            raise ValueError('interval could not separate grid point')
    assert moment(lo)[1] < 1 < moment(hi)[0]
    return dict(lower=str(lo), upper=str(hi), grid=str(grid),
                lower_moment_upper=str(moment(lo)[1]), upper_moment_lower=str(moment(hi)[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    h = json.loads(a.profile.read_text())
    assert sum(int(r)*n for r, n in h.items()) == 4816512
    result = dict(scope='Exact moment endpoint only; complete admission and outer checks are separate',
                  dimension=73, live=66304, global_profile=h, endpoint=price(h))
    a.out.write_text(json.dumps(result, indent=2))
    print(result['endpoint'], flush=True)


if __name__ == '__main__':
    main()
