"""Admit the cascade-optimized operation frames on PR200's bit word with PR200's own exact checkers.

The replacement list opframe-bases.json gives, for each changed operation, an integer basis of its new
frame. Only frames change; the scalar word, sources, gauges, aliases, root frames and terminal selection are
PR200's. PR200's modules re-check value spans, nondegeneracy, nested physical chains, alias containment, the
complete terminal-modified word on every source/target/dirty column over F2 and the integers, prime witnesses
for every used frame, and the paid coarse/atom certificate. Frame-substitution checking follows PR207's
admission route. Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from pathlib import Path
import contextlib, gzip, hashlib, json, sys
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
PACKAGE = 'research/paired-cube-diagonal-bit-168'


def admit(BIT):
    pkg = Path(BIT) / PACKAGE
    for p in (pkg / 'bit', pkg / 'arithmetic'):
        if str(p) not in sys.path: sys.path.insert(0, str(p))
    from word import Candidate
    from terminal import prove
    from prime_witnesses import certificate as primes
    from prove import certify
    W = Candidate(); bases = json.loads((HERE / 'opframe-bases.json').read_text())
    public = list(W.opframe)
    assert len({i for i, _ in bases}) == len(bases)
    for i, rows in bases: W.opframe[i] = W.register(rows)
    changed = [i for i in range(len(public)) if W.opframe[i] != public[i]]
    assert len(changed) == len(bases), 'every listed frame differs from PR200'
    W.changed_frames = [i for i, (x, y) in enumerate(zip(W.original_opframe, W.opframe)) if x != y]
    W.endframe = {s: W.opframe[xs[-1]] for s, xs in W.role_ops.items()}
    W.exact_frames(); overridden = W.row()
    selection = json.loads((pkg / 'selected/bit/sinks.json').read_text())
    with contextlib.redirect_stdout(sys.stderr): record = prove(W, selection)
    record.pop('seconds'); record.pop('maxrss')
    row = record['profile']; row['child_histogram'] = {int(k): v for k, v in row['child_histogram'].items()}
    assert row['W_per_vertex'] == overridden['W_per_vertex'] - len(selection) and record['scalar_addition_delta'] <= 0
    prime = primes(W); digest = hashlib.sha256(json.dumps(prime, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    coarse = certify(row)
    ser = lambda x: {str(k): (str(v) if not isinstance(v, (int, str, list, dict, bool, type(None))) else v) for k, v in x.items()}
    return dict(status='PASS PR200 exact frame, chain, alias, terminal F2/integer and prime-witness checks',
                changed_frames=len(bases), used_frames=len(prime['frame_witnesses']), prime_witness_sha256=digest,
                overridden_profile=overridden, profile=row, terminal_status=record['status'],
                terminal_child_delta=record['child_delta'], integer_residual_bound=record['integer_residual_bound'],
                coarse=ser(coarse))
