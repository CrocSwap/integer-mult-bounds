"""Exact compressed star-interaction test for a new recursive lift mechanism.
intqwq; substantial OpenAI Codex assistance. Apache-2.0.
This checks a changed Temperley--Lieb premise, not a larger frame menu.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = HERE / 'inputs'
SELECTED = (0, 7, 20, 27, 36, 46, 57, 111)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def overlap(n, rows, left, right):
    """V_left U_right, with U=(-R^t/2;12I), V=(R/2,I).

    Intermediate query-row arrays use the actual native common frame. The
    eight auxiliary owners inherit the eight authenticated selected ports.
    Each operator entry is a finite rational sum of actual linear routes.
    """
    out = [[{} for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            entry = out[i][j]
            for p, x in rows[i].items():
                if p in rows[j]:
                    route = n.product(left[p], right[p])
                    entry[route] = entry.get(route, Q(0)) - x * rows[j][p] / 4
            if i == j:
                route = n.product(left[112+i], right[112+i])
                entry[route] = entry.get(route, Q(0)) + 12
            out[i][j] = {g: c for g, c in entry.items() if c}
    return out


def apply(n, matrix, vector):
    out = [{} for _ in range(8)]
    cache = {}
    for i in range(8):
        for j in range(8):
            for route, coefficient in matrix[i][j].items():
                for address, value in vector[j].items():
                    key = route, address
                    if key not in cache:
                        cache[key] = n.act(route, address)
                    at = cache[key]
                    out[i][at] = out[i].get(at, Q(0)) + coefficient * value
        out[i] = {at: c for at, c in out[i].items() if c}
    return out


def difference(actual, expected):
    for i in range(8):
        for address in sorted(set(actual[i]) | set(expected[i])):
            coefficient = actual[i].get(address, Q(0)) - expected[i].get(address, Q(0))
            if coefficient:
                return dict(output_query_row=i, output_address=address, residual=str(coefficient),
                            actual=str(actual[i].get(address, Q(0))), expected=str(expected[i].get(address, Q(0))))
    return None


def main():
    began = time.monotonic()
    need(sys.version_info >= (3, 12), 'Python 3.12 or later')
    n = load(NATIVE / 'native_common.py', 'round8_actual_owner_routes')
    packet, phases = n.load_sources()
    rows = [{int(k): Q(x) for k, x in row.items()} for row in packet['R_rows']]
    need(all(sum((x * rows[j].get(p, 0) for p, x in row.items()), Q(0)) == 56 * int(i == j)
             for i, row in enumerate(rows) for j in range(8)), 'Authenticated R Gram')
    owners = list(range(112)) + list(SELECTED)
    routes = [[n.source_route(phases, stage, p) for p in owners] for stage in range(3)]
    results = []
    for s, t in [(0, 1), (1, 2)]:
        st, ts = overlap(n, rows, routes[s], routes[t]), overlap(n, rows, routes[t], routes[s])
        # Every route fixes zero. The compressed sandwich on this address is
        # 4I, so a scalar TL parameter, if present, is forced to be lambda=1.
        zero = [{0: Q(1)}] + [{} for _ in range(7)]
        want_zero = [{0: Q(4)}] + [{} for _ in range(7)]
        need(apply(n, st, apply(n, ts, zero)) == want_zero, 'Zero-address scalar parameter witness')
        witness = None
        for query in range(8):
            for address in n.AXES[:25]:
                initial = [{} for _ in range(8)]
                initial[query][address] = Q(1)
                actual = apply(n, st, apply(n, ts, initial))
                expected = [{} for _ in range(8)]
                expected[query][address] = Q(4)
                witness = difference(actual, expected)
                if witness:
                    witness.update(input_query_row=query, input_address=address)
                    break
            if witness:
                break
        need(witness is not None, 'This probe expected a finite counterexample, not a universal proof')
        results.append(dict(stages=[s, t], zero_address_forces_tl_parameter='1',
                            compressed_sandwich_not_4I=witness,
                            implication='E_s E_t E_s is not scalar times E_s, with E_s=(I-T_s)/2. '
                                        'One actual f=1 basis witness refutes this proposed all-f scalar TL family.'))
    inputs = [NATIVE / 'native_common.py', NATIVE / 'sources/certificate.json.gz',
              NATIVE / 'sources/DATA-PHASES.json']
    result = dict(status='PASS_EXACT_NEW_STAR_RELATION_COUNTERCONTROLS', author='intqwq', new_kappa=False,
                  mechanism='Scalar Temperley-Lieb closure of the transported rank-eight lift projectors',
                  compressed_identity='V_s U_t V_t U_s = 4 lambda I would imply E_s E_t E_s=lambda E_s',
                  results=results, inputs_sha256={str(p.relative_to(HERE)).replace('\\','/'): digest(p) for p in inputs},
                  script_sha256=digest(__file__), seconds=time.monotonic()-began,
                  scope='New relation rejected by exact physical f=1 witnesses. No obstruction to noncentral '
                        'operator-valued algebras, changed completions or a new coupled recursive supplier is claimed.')
    if '--write' in sys.argv:
        (HERE / 'STAR-RELATIONS.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n',
                                               encoding='utf-8', newline='\n')
    else:
        expected=json.loads((HERE/'STAR-RELATIONS.json').read_text(encoding='utf-8'))
        expected.pop('seconds',None)
        actual=dict(result);actual.pop('seconds',None)
        need(actual==expected,'Committed proof-relevant star relation result')
    print(result['status'], len(results), 'actual-stage witnesses', flush=True)


if __name__ == '__main__':
    main()
