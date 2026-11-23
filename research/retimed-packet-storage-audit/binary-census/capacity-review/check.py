"""Independent source binding and exact arithmetic for the binary capacity join.

No author checker imports; no production calendar or physical execution.
"""
import argparse
import ast
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from itertools import product
import gzip
import json
from math import prod
from pathlib import Path
from types import SimpleNamespace
import sys

COROLLARY = '0170a085fb126ae4e2ab556cd41a446241e42bf9f602aac5418ae5b6a87d16f3'
CENSUS = '672289a9a52ffdc710b4ff037c03c7149097fb99a9083ba9da62021edc77c97f'
MASS = 'b92516aaa39192c6713654fa6f41b4c4f8367b1f71c7e374b95fd31687464c1b'
MASS_REVIEW = '281ad36f151c2e63620a2a08a9eaf099615de47e71e180fd24de32a4f9e236ad'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def select(source, names, namespace):
    nodes = [x for x in ast.parse(source).body
             if isinstance(x, (ast.FunctionDef, ast.ClassDef)) and x.name in names]
    need({x.name for x in nodes} == set(names), 'Missing literal source declaration')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<retained-source-declarations>', 'exec'), namespace)
    return namespace

def authenticate(root):
    need(digest(root/'COROLLARY.md') == COROLLARY, 'Corollary changed')
    need(digest(root/'PROOF.md') == CENSUS, 'Census changed')
    need(digest(root/'dependencies/mass-PROOF.md') == MASS, 'Numerical proof changed')
    need(digest(root/'dependencies/mass-CROSS-REVIEW.md') == MASS_REVIEW, 'Numerical review changed')
    for manifest in ('SOURCE-BINDINGS.json', 'COROLLARY-BINDINGS.json'):
        data = json.loads((root/manifest).read_text())
        for name, pin in data['files'].items():
            path = root/('sources/'+name if manifest == 'SOURCE-BINDINGS.json' else name)
            need(digest(path) == pin['sha256'], 'Retained binding changed '+str(path))
            if 'size' in pin:
                need(path.stat().st_size == pin['size'], 'Retained size changed')
    return json.loads((root/'COROLLARY-BINDINGS.json').read_text())

def grades(root):
    graph = json.loads(gzip.decompress((root/'sources/strong-bit.json.gz').read_bytes()))
    caller = json.loads(gzip.decompress((root/'sources/binary-caller.gz').read_bytes()))
    need(graph == json.loads((root/'sources/graph.json').read_text()), 'Decoded graph differs')
    need(caller == json.loads((root/'sources/caller.json').read_text()), 'Decoded caller differs')
    dimensions = {int(i): v['dim'] for i, v in graph['frames'].items()}
    ports = caller['ports']
    expected_targets = [(('root', d, p), 1+7*len(row['stages']))
                        for d, row in enumerate(caller['diagonal']) for p in range(ports)]
    expected_paid = []
    for clock, event in enumerate(caller['events']):
        if event[0] == 'LOCAL':
            for i in range(2*ports, len(graph['start'])):
                expected_targets.append((('helper', clock, i),
                    abs(dimensions[graph['final'][i]]-dimensions[graph['start'][i]])))
            for site, row in enumerate(graph['program']):
                if row[0] == 'MOVE':
                    expected_paid.append((('move', clock, site, row[1]),
                        abs(dimensions[row[3]]-dimensions[row[2]])))
        elif event[0] in ('QUERY', 'IDLE_ONE'):
            rank = 1 if event[0] == 'QUERY' else 7*len(event[2])
            expected_paid.extend(((event[0], clock, p), rank) for p in range(ports))
    ns = {'dataclass': dataclass, 'product': product, 'prod': prod}
    select((root/'dependencies/powered.py').read_text(), ('Port', 'PoweredWord', 'bit_word'), ns)
    select((root/'sources/tagged_sources.py').read_text(), ('binary_ports',), ns)
    literal = ns['binary_ports'](graph, caller)
    need([(p.tag, p.rank) for p in literal.targets] == expected_targets, 'Actual target tuples differ')
    need([(p.tag, p.rank) for p in literal.paid] == expected_paid, 'Actual paid tuples differ')
    target = tuple(x[1] for x in expected_targets)
    paid = tuple(x[1] for x in expected_paid)
    need(literal.ambient == 134 and len(target) == 18906 and len(paid) == 104904, 'Raw unpowered inventory')
    need(min(target) > 0 and max(target) == 127 and min(paid) == 1, 'Production grade domain')
    # This inexpensive literal count corroborates the separate lifetime theorem;
    # its alias/custody argument is still an imported reviewed dependency.
    public = graph['public']; live = set(range(public)); peak = 0
    for row in graph['program']:
        if row[0] == 'INIT':
            need(row[1] not in live, 'Repeated live initialization')
            live.add(row[1]); peak = max(peak, len(live)-public)
        elif row[0] == 'CLEAR':
            need(row[1] in live and row[1] >= public, 'Invalid private retirement')
            live.remove(row[1])
    need(live == set(range(public)) and peak == 3433, 'Private peak census')
    need(len(target)+peak == 22339, 'Per-origin coefficient')
    return literal, target, paid, peak

def literal_constants(root):
    tree = ast.parse((root/'dependencies/installations.py').read_text())
    assignment = next(x for x in tree.body if isinstance(x, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'BINARY_C' for t in x.targets))
    trial = eval(compile(ast.Expression(assignment.value), '<BINARY_C>', 'eval'), {'Q': F})
    t = 1-trial
    need(t == F(1148436507037532395, 1152921504606846976), 'Actual binary exponent')
    need(t > F(3,4) and t <= 1 and t.denominator == 2**60, 'Numerical theorem exponent domain')
    return trial, t

def recipe_binding(root, literal, target, paid, trial):
    text = (root/'sources/transport.py').read_text(); captured = []
    def capture(*args, **kwargs):
        captured.append((args, kwargs)); return args, kwargs
    ns = {'Plan': capture, 'F': F}
    select(text, ('Recipe',), ns)
    cells = object()
    word = SimpleNamespace(tagged=literal, targets=target, paid=paid, cells=cells)
    ns.update({'cache': cache, 'binary_word': lambda: word, 'BINARY_C': trial})
    select((root/'sources/raw_binary_stage.py').read_text(), ('binary_recipe',), ns)
    constructor = next(x for x in ast.parse(text).body if isinstance(x, ast.ClassDef) and x.name == 'Plan')
    init = next(x for x in constructor.body if isinstance(x, ast.FunctionDef) and x.name == '__init__')
    measure = next(x.value for x in init.body if isinstance(x, ast.Assign)
                   and isinstance(x.value, ast.Call) and isinstance(x.value.func, ast.Name)
                   and x.value.func.id == 'Measure')
    reports = []
    for h in (1024, 3000, 5610, 9100):
        recipe = ns['binary_recipe'](h); args, kw = recipe.open(); n = 1 << h
        need(args[:5] == (n, target, paid, cells, 1-trial), 'Recipe source parameters')
        need(args[5:] == (32768, 2*(n//(2048*134)), n**6, n**82, n**2), 'Recipe geometry')
        need(kw == {'width': n**92, 'delay_base': 2**19} and recipe.width == n**92, 'Recipe width/delay')
        margs = eval(compile(ast.Expression(measure), '<Plan Measure expression>', 'eval'),
                     {'Measure': lambda *x: x, 't': 1-trial, 'volume': n**6, 'n': n})
        need(margs == (1-trial, n**6, 64*(h+1)), 'Actual precision expression')
        need(64*(h+1) > 64*h, 'Grid does not dominate N^64')
        need(args[6] > args[5] and args[6] < n, 'Nonempty source bin domain')
        reports.append({'height': h, 'precision': margs[2], 'width_log': 92*h,
                        'delay_base': kw['delay_base'], 'constructor_capture_only': True})
    rejected = False
    try:
        ns['Recipe'](1023, 134, target, paid, cells, trial)
    except ValueError:
        rejected = True
    need(rejected, 'Recipe minimum rank guard disappeared')
    receiver = ast.parse((root/'sources/binary_receiver.py').read_text())
    choice = next(x.value for x in ast.walk(receiver) if isinstance(x, ast.Assign)
                  and any(isinstance(y, ast.Attribute) and y.attr == 'recipe' for y in x.targets))
    for h in (2999, 3000, 3001):
        answer = eval(compile(ast.Expression(choice), '<literal receiver dispatch>', 'eval'),
                      {'height': h, 'binary_recipe': lambda h: h})
        need(answer == (h if h >= 3000 else None), 'Receiver production threshold')
    return reports

def delay_loop(root):
    tree = ast.parse((root/'sources/transport.py').read_text())
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Plan')
    init = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == '__init__')
    loop = next(x for x in init.body if isinstance(x, ast.For) and
                any(isinstance(y, ast.While) for y in x.body))
    assignment = init.body[init.body.index(loop)-1]
    source_program = compile(ast.Module(body=[assignment, loop], type_ignores=[]), '<literal source level loop>', 'exec')
    ceilns = {}; select((root/'sources/transport.py').read_text(), ('ceil',), ceilns)
    checked = 0; counts = 0; exact_boundaries = 0
    for lower in (32768, 1250):
        endpoints = set()
        for k in range(241):
            threshold = F(lower)*F(6,5)**k
            if threshold.denominator == 1:
                exact_boundaries += 1
            even = 2*(threshold.numerator//(2*threshold.denominator))
            endpoints.update(x for x in (even-2, even, even+2, even+4) if x >= lower)
        bins = sorted(endpoints)
        state = SimpleNamespace(bands=bins, delay={}, count={})
        class Dummy:
            def mass(self, left, right):
                need(right == left+2, 'Changed source count bin width')
                return F(0), F(2*left+1, 7)
        ns = {'self': state, 'lower': lower, 'F': F, 'scale_step': F(6,5),
              'delay_base': 2**19, 'measure': Dummy(), 'ceil': ceilns['ceil']}
        exec(source_program, ns)
        for e in bins:
            d = state.delay[e]
            need(d > 0 and d.bit_count() == 1 and (d.bit_length()-1)%19 == 0, 'Non-power delay')
            level = (d.bit_length()-1)//19
            need(F(lower)*F(6,5)**level <= e < F(lower)*F(6,5)**(level+1), 'Level outside exact critical interval')
            need(d*lower**76 <= e**76, 'Claimed delay envelope')
            need(state.count[e] == (2*e+1+6)//7, 'Source count no longer upper ceiling')
            checked += 1; counts += 1
    return {'critical_even_bins': checked, 'literal_count_expressions': counts,
            'exact_threshold_fixtures': exact_boundaries}

def inequalities(t, q):
    # Universal certificates are exact integer/rational inequalities, evaluated
    # at the least allowed height where the monotone conclusions are weakest.
    need(6**76 > 2**19*5**76, 'Delay exponent certificate')
    need(q+1 < 1 << 1024, 'Inclusive endpoint slack at minimum height')
    need(22339 < 2**15 and 2*22339 < 2**16 < 2**(9*1024), 'Owner-to-width slack')
    need(t > F(1,2) and 32768 >= 16, 'Ideal mass coefficient below one')
    need(F(1891*2064) + F(61,2) < 2**22, 'Uniform mass error coefficient')
    need(F(2**24, 2**57) < F(1,4), 'Uniform endpoint error below quarter')
    need(2*2 <= 2**6, 'Monotone 2N <= N^6 base case')
    controls = {'insufficient_delay_exponent': 6**72 < 2**19*5**72,
                'reversed_delay_inequality': not (6**76 < 2**19*5**76),
                'inclusive_slack_fails_at_small_rank': not(q+1 < 2**16),
                'owner_margin_fails_at_tiny_rank': not(2*22339 < 2**9),
                'arbitrary_exponent_excluded': not(F(1,4) > F(1,2))}
    need(all(controls.values()), 'A scope rejection control was vacuous')
    return controls

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--author', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); root = args.author.resolve()
    authenticate(root)
    literal, target, paid, peak = grades(root)
    trial, t = literal_constants(root)
    result = {'status': 'PASS_INDEPENDENT_BINARY_CAPACITY_COROLLARY',
        'corollary_sha256': COROLLARY, 'census_sha256': CENSUS,
        'mass_proof_sha256': MASS, 'mass_review_sha256': MASS_REVIEW,
        'targets': len(target), 'paid': len(paid), 'ambient': literal.ambient,
        'target_max': max(target), 'paid_min': min(paid), 'private_peak': peak,
        'per_origin_coefficient': len(target)+peak, 't': str(t),
        'constructor_bindings': recipe_binding(root, literal, target, paid, trial),
        'delay_loop': delay_loop(root), 'controls': inequalities(t, len(paid)),
        'universal_consequences': ['sum_count < 2*N^6', 'q*delay+1 < N^77',
                                   'C_star < 2*N^83', 'fresh_owner_capacity < 2*N^92'],
        'scope': 'Successful actual binary production recipes; accepted census custody/free-first and accepted numerical enclosure retained. No production calendar or physical execution.',
        'python': sys.version.split()[0]}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
