"""Check causal-library separating duals by direct binary pairings."""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from math import prod
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scaled(row):
    values = [Fraction(x) for x in row]
    scale = prod(x.denominator for x in values)
    return [int(x*scale) for x in values]


def all_geometry(word):
    frames = {int(c): (f['dim'], [scaled(r) for r in f['B']], [scaled(r) for r in f['A']])
              for c,f in word['frames'].items()}
    result = []
    for destination in sorted(frames):
        for donor in sorted(frames):
            x, y = frames[destination], frames[donor]
            small, large = (x,y) if x[0] <= y[0] else (y,x)
            if all(sum(a*b for a,b in zip(left,right)) == 0 for left in small[1] for right in large[2]):
                result.append([destination,donor,abs(x[0]-y[0])])
    return result


def check_pairings(target, library, dual, other):
    other.require(len(target & dual) % 2 == 1, 'required arrival differs')
    other.require(all(len(row & dual) % 2 == 0 for row in library), 'causal library agrees')


def coordinates(value):
    return {i for i in range(value.bit_length()) if value >> i & 1}


def check_coverage(cases, expected, other):
    other.require([row[:3] for row in cases] == expected, 'complete ordered cheaper-delivery domain')


def evaluate():
    generator = load(HERE/'generate.py', 'producer')
    engine, other = generator.module('census'), generator.module('independent')
    generator.module('verify').run()
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())
    for pin in pins:
        data = (HERE/pin['path']).read_bytes()
        other.require(sha256(data).hexdigest() == pin['sha256'], 'source SHA-256')
        other.require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'], 'source Git blob')
    certificate = engine.read(HERE/'CERTIFICATE.json.gz')
    other.require(generator.produce() == certificate, 'complete primary certificate')
    word, caller = engine.source()
    pairs = all_geometry(word)
    other.require(pairs == certificate['geometry'], 'complete rational containment domain')
    other.require(not any(a != b and r == 0 for a,b,r in pairs), 'distinct charts have distinct frames')
    dimensions = {int(c): f['dim'] for c,f in word['frames'].items()}
    legal = {c: [(b,r) for d,b,r in pairs if c == d] for c in dimensions}
    receipts, controls, control_case, altered_case = [], [], None, None
    coverage_control = None
    for reverse, record in enumerate(certificate['orientations']):
        direction = 'transpose' if reverse else 'forward'
        other.require(record['direction'] == direction, 'orientation order')
        _, _, banks, moves = other.replay(word, bool(reverse))
        for clock, (source, destination) in moves.items():
            target = banks[destination][clock]
            library = [row for key,row in banks[source].items() if key < clock]
            other.require(other.rank(library+[target]) == len(library), 'original source attains the rank floor')
            other.require((source, abs(dimensions[source]-dimensions[destination])) in legal[destination], 'original nested route')
        expected = [[clock,b,r] for clock,(a,c) in moves.items() for b,r in legal[c]
                    if r < abs(dimensions[a]-dimensions[c])]
        check_coverage(record['cases'], expected, other)
        weights, ranks, pairings, peak = Counter(), Counter(), 0, 0
        for clock, donor, rank, encoded in record['cases']:
            destination = moves[clock][1]
            target = banks[destination][clock]
            library = [row for key,row in banks[donor].items() if key < clock]
            dual = coordinates(int(encoded, 16))
            other.require(all(i < word['public'] for i in dual), 'public dual coordinates')
            check_pairings(target, library, dual, other)
            pairings += len(library)
            peak = max(peak,len(library))
            weights[len(dual)] += 1
            ranks[rank] += 1
            if control_case is None and donor == destination:
                control_case = target, library, dual
            if altered_case is None:
                for row in library:
                    extra = row-target
                    if extra:
                        altered_case = target, library, dual ^ {min(extra)}
                        break
        if coverage_control is None:
            coverage_control = record['cases'], expected
        receipts.append(dict(direction=direction, arrivals=len(moves), original_sources_verified=len(moves), cheaper_cases=len(expected),
                             rank_counts=dict(sorted(ranks.items())), bank_pairings=pairings,
                             target_pairings=len(expected), maximum_library=peak,
                             nonunit_duals=sum(n for w,n in weights.items() if w > 1), maximum_dual_weight=max(weights)))
    other.require(len(receipts) == 2 and len(certificate['orientations']) == 2, 'both directions')

    def reject(label, action, expected):
        try:
            action()
        except ValueError as error:
            other.require(str(error) == expected, label+' failed at wrong gate: '+str(error))
            controls.append(label)
        else:
            raise ValueError('accepted mutation: '+label)

    target, library, dual = control_case
    reject('zero separator', lambda: check_pairings(target,library,set(),other), 'required arrival differs')
    reject('separator fails a donor row', lambda: check_pairings(*altered_case,other), 'causal library agrees')
    reject('arrival incorrectly available at its own deadline', lambda: check_pairings(target,library+[target],dual,other), 'causal library agrees')
    cases, expected = coverage_control
    reject('omit a cheaper delivery', lambda: check_coverage(cases[:-1],expected,other), 'complete ordered cheaper-delivery domain')
    changed = [row[:] for row in cases];changed[0][2] += 1
    reject('change the paid rank', lambda: check_coverage(changed,expected,other), 'complete ordered cheaper-delivery domain')
    reject('omit a nested chart pair', lambda: other.require(pairs[:-1] == certificate['geometry'], 'complete rational containment domain'), 'complete rational containment domain')
    return dict(status=certificate['status'], source_pins=len(pins), public=word['public'], frames=len(word['frames']),
                geometry_pairs=len(pairs), orientations=receipts,
                total_cases=sum(r['cheaper_cases'] for r in receipts),
                total_bank_pairings=sum(r['bank_pairings'] for r in receipts),
                source_invoice=engine.invoice(word,caller), controls=controls,
                savings_upper=0, scope='One original arrival replaced from one original causal chart library and a cheaper nested transfer; no adaptive library changes.')


def run():
    receipt = evaluate()
    if json.loads(json.dumps(receipt)) != json.loads((HERE/'RESULT.json').read_text()):
        raise ValueError('summary receipt')
    print(receipt['status'], receipt['total_cases'], receipt['total_bank_pairings'], 'zero replacements')


if __name__ == '__main__':
    run()
