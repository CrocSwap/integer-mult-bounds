"""Literal pending-allocation, native-capacity and warm-entry checks."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import load, require
from fixtures import call, fixture, preserved, saved


class Probe:
    def __init__(self, m, case, budgets=None, extension_bound=11):
        self.m, self.case = m, case
        self.arenas = (case.r, case.ix)
        self.entry = [len(a.live) for a in self.arenas]
        self.entry_backing = [len(a.words) for a in self.arenas]
        self.budgets = case.limits if budgets is None else budgets
        self.requests = [0, 0]
        self.peak = [0, 0]
        self.extension_peak = 0
        self.in_extension = False
        self.extension_bound = extension_bound
        self.trace = hashlib.sha256()
        self.rejected = None

    def allocate(self, arena):
        require(arena in self.arenas, 'no undeclared numerical arena')
        i = self.arenas.index(arena)
        demand = len(arena.live)+1-self.entry[i]
        self.requests[i] += 1
        self.peak[i] = max(self.peak[i], demand)
        self.trace.update(f'{i}:{demand};'.encode())
        require(demand <= self.budgets[i], 'pending request exceeds prefix budget')
        if self.in_extension and i == 1:
            self.extension_peak = max(self.extension_peak, demand)
            require(demand <= self.extension_bound, 'half extension needs eleven indices')
        try:
            result = self.original_zero(arena)
        except ValueError as error:
            self.rejected = {'arena':i, 'demand':demand, 'message':str(error),
                             'live':len(arena.live), 'backing':len(arena.words),
                             'capacity':arena.capacity, 'free':len(arena.available)}
            raise
        require(len(arena.words) == max(self.entry_backing[i], self.entry[i]+self.peak[i]),
                'retained backing includes pending demand')
        return result

    def __enter__(self):
        self.original_zero = self.m.words.Arena.zero
        self.original_extend = self.m.children.extend
        # Assign an ordinary function so Python supplies the Arena argument.
        owner = self
        self.m.words.Arena.zero = lambda arena: owner.allocate(arena)
        def extension(incoming, request):
            owner.in_extension = True
            try:
                return owner.original_extend(incoming, request)
            finally:
                owner.in_extension = False
        self.m.children.extend = extension
        return self

    def __exit__(self, *_):
        self.m.words.Arena.zero = self.original_zero
        self.m.children.extend = self.original_extend


def run(m, config, quota_delta=(0,0), extension_bound=11, budgets=None):
    case = fixture(m, **config)
    before = saved(case)
    probe = Probe(m, case, budgets, extension_bound)
    for i, a in enumerate(probe.arenas):
        a.capacity = max(len(a.words), len(a.live)+case.limits[i])+quota_delta[i]
        require(a.capacity >= len(a.words) and a.capacity > 0, 'canonical target capacity')
    error = None
    try:
        with probe:
            try:
                out = call(m, case)
                require(out.inspect() == case.expected, 'credited independent integer expectation')
                case.r.free(out)
            except ValueError as exc:
                error = str(exc)
        preserved(case, before)
        if quota_delta != (0,0):
            require(error == 'fixed register inventory', 'real source inventory failure')
            require(probe.rejected is not None and probe.rejected['free'] == 0, 'first quota failure captured')
            require(probe.rejected['live'] == probe.rejected['capacity'], 'failed request exceeds real capacity by one')
        else:
            require(error is None, 'quota is sufficient on literal fixture')
        return {'config':config, 'quota_delta':list(quota_delta), 'entry_live':probe.entry,
                'entry_backing':probe.entry_backing, 'capacities':[a.capacity for a in probe.arenas],
                'pending_peak':probe.peak, 'requests':probe.requests,
                'extension_peak':probe.extension_peak, 'request_sha256':probe.trace.hexdigest(),
                'error':error, 'rejected':probe.rejected}
    finally:
        case.r.rollback(set())
        case.ix.rollback(set())
        case.program.tape.clear()
        case.fields.tape.clear()


def receipt(m):
    configs = [
        {'branch':'adapter-good', 'rank':42},
        {'branch':'adapter-good', 'rank':1, 'depth':2, 'modulus':9},
        {'branch':'adapter-fallback', 'depth':0},
        {'branch':'child-good', 'rank':42},
        {'branch':'child-pair'},
        {'branch':'child-unit'},
        {'branch':'child-pair', 'depth':2, 'modulus':9, 'borrowed':7},
        {'branch':'adapter-good', 'rank':42, 'warm':(40000,64)},
        {'branch':'child-unit', 'depth':2, 'warm':(22000,64)},
    ]
    rows = [run(m, c) for c in configs]
    require(rows[0]['pending_peak'][0] == 37672, 'credited adapter sharp residue witness')
    require(rows[4]['pending_peak'][0] == 20494, 'credited child sharp residue witness')
    require(rows[5]['extension_peak'] == 11, 'corrected halved-unit extension peak')
    under = [run(m, configs[0], (-1,0)), run(m, configs[4], (-1,0)),
             run(m, configs[3], (0,-1))]
    return {'schema_version':1, 'scope':'literal prefix corroboration and actual quota guards; no_new_kappa',
            'cases':rows, 'underbudget':under}


def compare(actual, expected):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), 'complete typed receipt')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--emit', action='store_true')
    ap.add_argument('--quick', action='store_true')
    args = ap.parse_args()
    m = load()
    if args.quick:
        print(json.dumps(run(m, {'branch':'child-unit'}), indent=2))
        return
    actual = receipt(m)
    if args.emit:
        print(json.dumps(actual, indent=2))
    else:
        compare(actual, json.loads((Path(__file__).parent/'RESULT.json').read_text()))
        print('PASS_COEFFICIENT_CAPACITY_PREFIX cases=9 underbudget=3 half_extension=11 no_new_kappa')


if __name__ == '__main__':
    main()
