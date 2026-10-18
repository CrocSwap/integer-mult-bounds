"""Complete frozen-word single-transport census using either existing engine.

Brian Ross with substantial OpenAI Codex assistance. Apache-2.0.
No new search framework: this calls the two previously reviewed enumerators.
Frame/touch caching is valid for a final profile, never for continuation.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / 'pr1048-certified-repair'


def load(name):
    spec = importlib.util.spec_from_file_location('complete_' + name, PREVIOUS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(engine):
    start = time.monotonic()
    independent = load('independent')
    inventory = independent.audit_inventory(json.loads((PREVIOUS / 'SOURCE-PINS.json').read_text()))
    endpoints = [independent.residual(independent.BASE, x) for x in (independent.LOW, independent.HIGH)]
    independent.require(endpoints[0][1] < 0 < endpoints[1][0], 'reference root signs')
    if engine == 'primary':
        coverage = load('coverage')
        word = json.loads(gzip.decompress(coverage.WORD.read_bytes()))
        state = coverage.State(word, coverage.Frames(word))
        operations = [(oid, t, u) for sec in 'AB' for _, t, u, oid in state.sections[sec]]
        moves_for = lambda oid: coverage.legal_moves(state, oid)
        profile = lambda s, regs=None: s.profile(regs)
        apply = lambda oid, q, f: state.moved(oid, q, f)
        pricer = load('pricing').ReferencePricer()
    else:
        checker = independent.WordCheck()
        state = checker.initial
        operations = [(oid, t, u) for sec in 'AB' for oid, _, t, u in state[sec]]
        moves_for = lambda oid: checker.literal_moves(state, oid)
        profile = checker.profile
        apply = lambda oid, q, f: checker.apply(state, oid, q, f)
        pricer = None
    base = profile(state)
    independent.require(base == independent.BASE, 'replayed baseline profile')
    histogram, domains = Counter(), []
    for oid, t, u in operations:
        before = profile(state, (t, u))
        moves = moves_for(oid)
        cached = {}
        for q, frame, signature in moves:
            key = frame, signature
            if key not in cached:
                candidate = profile(apply(oid, q, frame), (t, u))
                cached[key] = independent.profile_delta(before, candidate)
            histogram[cached[key]] += 1
        domains.append(dict(id=list(oid), moves=len(moves), classes=len(cached),
                            sha256=independent.candidate_hash(moves)))
    counts, cases = Counter(), []
    strict_worse = 0
    for key, occurrences in sorted(histogram.items()):
        delta = dict(key)
        independent.require(sum(r * n for r, n in key) == 0, 'transport rank mass changed')
        candidate = {r: base.get(r, 0) + delta.get(r, 0) for r in set(base) | set(delta)}
        independent.require(all(n >= 0 for n in candidate.values()), 'negative profile')
        independent.require(independent.residual(candidate, Fraction(0))[1] < 0, 'candidate positive root')
        if pricer is None:
            interval = independent.signed_price(delta)
            status = independent.status_of(interval)
        else:
            result = pricer.compare_delta(delta)
            interval = tuple(map(Fraction, result['interval']))
            status = result['status']
        counts[status] += occurrences
        if interval[0] > 0:
            strict_worse += occurrences
        cases.append(dict(delta=delta, occurrences=occurrences, status=status,
                          interval=list(map(str, interval))))
    return dict(complete=True, engine=engine, elapsed=time.monotonic()-start,
                source_inventory=inventory, operations=len(operations),
                moves=sum(histogram.values()), delta_classes=len(histogram), counts=dict(counts),
                ties=histogram[()], strictly_worse=strict_worse,
                reference_bracket=list(map(str, (independent.LOW, independent.HIGH))),
                endpoint_residuals=[list(map(str, x)) for x in endpoints],
                domains=domains, profile_deltas=cases,
                driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', choices=('primary', 'independent'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.engine)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('domains', 'profile_deltas', 'endpoint_residuals')}, sort_keys=True))
