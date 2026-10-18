"""Lower every actual operation of the complete credited borrowing trace.

Native records are checked by a separately implemented signed-Pauli interpreter
and an exact Gaussian zero-column phase check. Checkpoints are immutable.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
import time
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / 'vendor'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

CE = load('borrow_native_clifford', VENDOR / 'clifford_exact.py')
N = load('borrow_native_independent', VENDOR / 'native_verify.py')

def need(condition, message):
    if not condition:
        raise ValueError(message)

def canonical(vectors):
    rows = {}
    for value in vectors:
        while value:
            j = value.bit_length() - 1
            if j in rows:
                value ^= rows[j]
            else:
                rows[j] = value
                break
    for j in sorted(rows):
        for k in rows:
            if k > j and rows[k] >> j & 1:
                rows[k] ^= rows[j]
    return tuple(rows[j] for j in sorted(rows, reverse=True))

@lru_cache(None)
def chart(vectors):
    return CE.canonical_frame(9, canonical(vectors))

def inverse_columns(cols):
    return CE.transpose(CE.inv(CE.transpose(cols, 9), 9), 9)

def linear_columns(cols, value):
    out = 0
    for i, c in enumerate(cols):
        if value >> i & 1:
            out ^= c
    return out

def change_columns(old, new):
    a, b = CE.basis_extend(old, 9), CE.basis_extend(new, 9)
    return tuple(linear_columns(b, col) for col in inverse_columns(a))

def logical_operator(warp):
    cols = change_columns(tuple(warp['from_basis']), tuple(warp['to_basis']))
    inverse = inverse_columns(cols)
    transposed_inverse = CE.transpose(inverse, 9)
    quadratic = tuple((1 << i) ^ linear_columns(transposed_inverse, inverse[i]) for i in range(9))
    return CE.perm(9, CE.transpose(cols, 9)).then(CE.diag(9, quadratic))

def make_jobs(trace, literal_bound=False):
    logical = {w['operator']: logical_operator(w) for w in trace['warps']}
    fourier = CE.fourier(9)
    dual = {symbol: fourier.adjoint().then(op.adjoint()).then(fourier)
            for symbol, op in logical.items()}
    jobs, event_refs = {}, []
    def add(kind, metadata, actual, rank):
        payload = [kind, metadata]
        if literal_bound:
            payload.append(actual.circuit)
        key = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        jobs.setdefault(key, dict(kind=kind, metadata=metadata, actual=actual, rank=rank))
        return key
    for index, event in enumerate(trace['events']):
        kind = event[0]
        if kind == 'transport':
            old, new = canonical(event[2]), canonical(event[3])
            key = add(kind, dict(old=old, new=new), chart(old).adjoint().then(chart(new)), event[4])
        elif kind in ('handoff', 'dual_handoff'):
            old, new, symbol = canonical(event[2]), canonical(event[3]), event[4]
            reference = dual if kind == 'dual_handoff' else logical
            op = chart(old).adjoint().then(reference[symbol]).then(chart(new))
            key = add(kind, dict(old=old, new=new, symbol=symbol), op, 0)
        elif kind in ('logical_monomial', 'dual_monomial'):
            symbol, frame = event[2], canonical(event[3])
            reference = dual if kind == 'dual_monomial' else logical
            op = reference[abs(symbol)]
            if symbol < 0:
                op = op.adjoint()
            op = chart(frame).adjoint().then(op).then(chart(frame))
            key = add(kind, dict(frame=frame, symbol=symbol), op, 0)
        else:
            key = None
        event_refs.append(key)
    residual_refs = {}
    for register, endpoints in trace['endpoints'].items():
        if int(register) < 224:
            continue
        old, new = canonical(endpoints['initial']), canonical(endpoints['final'])
        residual_refs[register] = add('helper_residual', dict(old=old, new=new),
                                    chart(old).adjoint().then(chart(new)), len(new) - len(old))
    return jobs, event_refs, residual_refs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    parser.add_argument('--orientation', choices=('forward', 'backward'), default='forward')
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--out-dir', type=Path)
    args = parser.parse_args()
    source = args.trace or HERE / (args.orientation + '-physical-events.json')
    trace = json.loads(source.read_bytes())
    jobs, refs, residuals = make_jobs(trace, literal_bound=bool(args.trace))
    destination = args.out_dir or HERE / ('native-' + args.orientation)
    records_dir = destination / 'records'
    records_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    count = 0
    retained = {}
    def operation_key(circuit, rank):
        return hashlib.sha256(json.dumps([circuit,rank],separators=(',',':')).encode()).hexdigest()
    for orientation in ('forward','backward'):
        for path in (HERE/('native-'+orientation)/'records').glob('*.json'):
            record=json.loads(path.read_bytes())
            retained.setdefault(operation_key(record['literal_expected'],record['recipe']['rank']),record)
    for key, job in sorted(jobs.items()):
        path = records_dir / (key + '.json')
        if path.exists():
            continue
        previous=retained.get(operation_key(job['actual'].circuit,job['rank']))
        if previous is not None:
            recipe=previous['recipe']
        else:
            recipe, compiled = CE.lower_child(job['actual'])
        need(recipe['rank'] == job['rank'], ('actual physical rank', job['kind'], job['metadata'], recipe['rank'], job['rank']))
        N.equal(N.recipe(recipe), tuple(job['actual'].circuit), 'complete borrowing ' + job['kind'])
        record = dict(kind=job['kind'], metadata=job['metadata'], recipe=recipe,
                      literal_expected=job['actual'].circuit,
                      signed_pauli_rows=job['actual'].tab,
                      exact_gaussian_zero_state=(previous.get('exact_gaussian_zero_state') if previous is not None else
                          CE.monomial(compiled)[1] if recipe['rank'] == 0 else None))
        path.write_text(json.dumps(record, separators=(',', ':')) + '\n', encoding='utf-8')
        count += 1
        if count % 50 == 0:
            print('NATIVE_COMPILED', count, 'new;', len(list(records_dir.glob('*.json'))), '/', len(jobs), 'seconds', round(time.monotonic() - started, 2), flush=True)
        if args.limit and count >= args.limit:
            break
    present = {p.stem for p in records_dir.glob('*.json')}
    complete = set(jobs) <= present
    report = dict(status='PASS_ALL_' + args.orientation.upper() + '_NATIVE_RECIPES' if complete else 'PARTIAL_' + args.orientation.upper() + '_NATIVE_CHECKPOINT',
                  jobs=len(jobs), present=len(present), newly_compiled=count,
                  trace_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  compiler_sha256=hashlib.sha256((VENDOR / 'clifford_exact.py').read_bytes()).hexdigest(),
                  independent_checker_sha256=hashlib.sha256((VENDOR / 'native_verify.py').read_bytes()).hexdigest(),
                  events=len(refs), helper_residuals=len(residuals),
                  literal_bound_keys=bool(args.trace),
                  limitation='Finite exact native operators for the ' + args.orientation + ' word only; whole-call hosting, precision and all-size admission separate.')
    (destination / 'STATUS.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if complete:
        out = dict(event_recipe_refs=refs, helper_residual_refs=residuals,
                   records={key: json.loads((records_dir / (key + '.json')).read_bytes()) for key in sorted(jobs)})
        (destination / ('NATIVE-' + args.orientation.upper() + '.json.gz')).write_bytes(gzip.compress((json.dumps(out, separators=(',', ':')) + '\n').encode(), mtime=0))
    print(json.dumps(report, indent=2), flush=True)
