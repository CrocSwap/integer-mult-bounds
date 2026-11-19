"""Bind the complete formal invoice and prove an exact validity interval."""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import ast
import gzip
import json
import re
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
FORMAL = HERE / 'retained/proof7783'
DATA = FORMAL / 'lean/Nov15'
SOURCE = HERE / 'retained/graph7761'
GRAPH_HASH = 'c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(file):
    raw = file.read_bytes()
    return json.loads(gzip.decompress(raw) if file.suffix == '.gz' else raw)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def literal(name, file):
    matches = re.findall(r'^def ' + name + r' : [^\n]+ := (\[[^\n]+\])$', file.read_text(), re.M)
    need(len(matches) == 1, 'one literal list ' + name)
    return ast.literal_eval(matches[0].replace('true', 'True').replace('false', 'False'))


def word(name, file):
    matches = re.findall(r'^def ' + name + r' : Nat := 0x([0-9a-f]+)$', file.read_text(), re.M)
    need(len(matches) == 1, 'one packed literal ' + name)
    return int(matches[0], 16)


def slots(value, width, count):
    need(value >= 0 and value >> (width * count) == 0, 'zero packed padding')
    return [(value >> (width * i)) & ((1 << width) - 1) for i in range(count)]


def span(basis):
    result = {0}
    for vector in basis:
        need(0 <= vector < 512, 'ambient nine-bit vector')
        result |= {x ^ vector for x in result}
    return result


def dimension(space):
    n = len(space)
    need(n > 0 and n & (n - 1) == 0, 'binary subspace size')
    return n.bit_length() - 1


def graph():
    with tempfile.TemporaryDirectory(prefix='invoice-source-') as directory:
        out = Path(directory) / 'graph.json.gz'
        cmd = [sys.executable, '-B', str(FORMAL / 'lean/tools/bridgegen/apply.py'),
               str(SOURCE / 'pr7756/data/BASE-GRAPH.json.gz'),
               str(SOURCE / 'pr7756/data/BASE-INTERFACE.json'),
               str(SOURCE / 'pr7756/EDITS.json'), str(out)]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
        need(GRAPH_HASH in result.stdout, 'source builder receipt')
        value = read(out)
    need(digest(value) == GRAPH_HASH, 'exact source graph')
    return value


def main_mask(value, layout):
    source = set(layout['live']) | {i + 112 for i in layout['live']}
    source |= set(layout['hosted']['X2']) | set(layout['hosted']['Y2'])
    mask = slots(value, 1, 1262)
    need({i for i, x in enumerate(mask) if x} == source, 'all source main owners')
    need(sum(mask) == 400, '400 main owners')
    return mask


def native_profiles(g, mask):
    spaces = list(map(span, g['frames']))
    bases = slots(word('BASK', DATA / 'Bridge7761R1D.lean'), 16, 9 * len(spaces))
    declared = literal('chBasis', DATA / 'Bridge7761D1.lean')
    for i, space in enumerate(spaces):
        basis = [x for x in bases[9*i:9*i+9] if x]
        need(basis == declared[i] and span(basis) == space, 'actual formal chart span')
    banks = [k for k in g['schedule'] if k < g['first_output']]
    moves = {k: (a, b) for k, a, b in g['moves']}
    geometry = DATA / 'Bridge7761G1D.lean'
    for name, expected in [('FAK', g['initial']), ('FBK', g['final']),
                           ('BSK', [moves[k][0] for k in banks]),
                           ('BTK', [moves[k][1] for k in banks])]:
        need(slots(word(name, geometry), 11, len(expected)) == expected, 'formal endpoint ' + name)
    paid, targets = Counter(), Counter()
    for a, b in moves.values():
        u, v = spaces[a], spaces[b]
        need(u <= v or v <= u, 'nested bank endpoints')
        rank = dimension(u) + dimension(v) - 2 * dimension(u & v)
        need(rank > 0, 'positive SPEC bank rank')
        paid[rank] += 1
    climbs = []
    for i, (a, b) in enumerate(zip(g['initial'], g['final'], strict=True)):
        u, v = spaces[a], spaces[b]
        need(u <= v, 'nested productive endpoints')
        rank = dimension(v) - dimension(u)
        climbs.append(rank)
        if mask[i]:
            need(rank == 8, 'main climb eight')
        else:
            need(rank > 0, 'positive helper rank')
            targets[rank] += 1
    return targets, paid, climbs


def bind_invoice(targets, paid, tb, pb, calls, application):
    signed, invoice = application['signed'], application['invoice']
    need(tb == {int(k): v for k, v in signed['fixed_root_targets'].items()}, 'caller root table')
    need(pb == {int(k): v for k, v in signed['fixed_caller_paid'].items()}, 'caller paid table')
    need(calls == application['calls'] == 2048, 'native call multiplicity')
    full_t, full_p = Counter(tb), Counter(pb)
    full_t.update({r: calls * n for r, n in targets.items()})
    full_p.update({r: calls * n for r, n in paid.items()})
    need(full_t == {int(k): v for k, v in invoice['targets'].items()}, 'complete productive invoice')
    need(full_p == {int(k): v for k, v in invoice['paid'].items()}, 'complete paid invoice')
    return full_t, full_p


def reject(label, operation):
    try:
        operation()
    except ValueError as error:
        return dict(control=label, rejection=str(error))
    raise ValueError('accepted mutation ' + label)


def ordered(profile):
    return {str(k): v for k, v in sorted(profile.items())}


def run():
    pins = read(HERE / 'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE / pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
             'retained source bytes')
    g = graph()
    need(len(g['initial']) == 1262 and len(g['moves']) == 5746 and len(g['frames']) == 1099,
         'source graph dimensions')
    layout = read(SOURCE / 'pr7756/data/BASE-INTERFACE.json')
    packed = word('MB', DATA / 'Bridge7761R3D.lean')
    mask = main_mask(packed, layout)
    need(mask == literal('mainL0', DATA / 'Bridge7761D2.lean'), 'literal main list')
    targets, paid, climbs = native_profiles(g, mask)
    caller_text = (DATA / 'Bridge7761S2.lean').read_text()
    match = re.search(r'noncomputable def caller7761.*?Caller ℚ \(Fin 1262\) \(Fin 5746\) (\d+) where\s+G := fun _ => G7761 hO\s+T := BankBannerCert.TB\s+P := BankBannerCert.PB', caller_text, re.S)
    need(match is not None, 'actual constant caller declaration')
    calls = int(match.group(1))
    tb = dict(literal('TB', DATA / 'BankBannerCert.lean'))
    pb = dict(literal('PB', DATA / 'BankBannerCert.lean'))
    need(len(tb) == len(pb) == 9 and all(r > 0 and n > 0 for p in [tb, pb] for r, n in p.items()),
         'positive caller tables')
    application = read(SOURCE / 'evidence/application.json')['result']['candidate']
    full_t, full_p = bind_invoice(targets, paid, tb, pb, calls, application)
    margin = sum(r*n for r, n in full_t.items()) - sum(r*n for r, n in full_p.items())
    bins = {r: (r-1).bit_length() for r in full_t}
    need(all(r <= 2**b and (b == 0 or 2**(b-1) < r) for r, b in bins.items()), 'exact binary rank bounds')
    slope = sum(n*r*bins[r] for r, n in full_t.items())
    end = Fraction(1, 1000)
    lower = margin - end*slope
    need(margin == 169984 and slope == 169886720 and lower == Fraction(2432, 25) > 0,
         'positive exact interval margin')
    controls = []
    for label, args in [
        ('one extra caller root', (targets, paid, tb | {9: tb[9]+1}, pb, calls)),
        ('one missing caller charge', (targets, paid, tb, pb | {1: pb[1]-1}, calls)),
        ('one missing native call', (targets, paid, tb, pb, calls-1)),
        ('credit all 400 mains', (targets + Counter({8: 400}), paid, tb, pb, calls)),
        ('omit one native bank', (targets, paid - Counter({1: 1}), tb, pb, calls)),
        ('omit one helper credit', (targets - Counter({9: 1}), paid, tb, pb, calls))]:
        controls.append(reject(label, lambda args=args: bind_invoice(*args, application)))
    controls.append(reject('change main identity', lambda: main_mask(packed ^ 1, layout)))
    return dict(source_files=len(pins), graph_sha256=GRAPH_HASH, calls=calls,
                fields=1262, mains=sum(mask), helpers=1262-sum(mask), banks=5746, charts=1099,
                main_mask_sha256=digest(mask), endpoint_climbs_sha256=digest(climbs),
                native_targets=ordered(targets), native_paid=ordered(paid),
                caller_targets=ordered(tb), caller_paid=ordered(pb),
                complete_targets=ordered(full_t), complete_paid=ordered(full_p),
                margin_at_zero=margin, binary_slope_bound=slope,
                interval=['0', str(end)], endpoint_margin_lower_bound=str(lower),
                exact_binary_exponents=ordered(bins), controls=controls,
                lean_executed=False, full_caller_replayed=False,
                source_builder_mode='normal Python subprocess in both audit modes; exact graph digest required')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = run()
    if args.record:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == read(HERE / 'RESULT.json'), 'deposited invoice certificate')
    print('PASS_P104_LEAN_INVOICE_BINDING', result['calls'], 'calls', result['helpers'],
          'helpers', result['endpoint_margin_lower_bound'], 'margin',
          len(result['controls']), 'controls', round(time.monotonic()-start, 2), 'seconds')
