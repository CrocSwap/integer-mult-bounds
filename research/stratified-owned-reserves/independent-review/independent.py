"""Separate stratified-space review: descending paths and exact dual witnesses.

Prepared for CubeJerry with substantial OpenAI assistance. Standard library.
This does not rerun the author's verifier or execute a multiplication caller.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType
import json
import random

parser = argparse.ArgumentParser()
parser.add_argument('--package-root', type=Path)
parser.add_argument('--write-result', action='store_true')
args = parser.parse_args()
OUT = Path(__file__).resolve().parent
P = (args.package_root or OUT.parent).resolve()
ROOT = P.parents[1]


def need(condition, label):
    if not condition:
        raise ValueError(label)


def load(path):
    module = ModuleType(path.stem)
    module.__file__ = str(path)
    import sys
    sys.modules[path.stem] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


model = load(P / 'stack_model.py')
pins = [pin for pin in json.loads((P / 'SOURCES.json').read_text())['files']
        if pin['usage'] == 'input']
for pin in pins:
    raw = (ROOT / pin['path']).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
         == pin['git_blob'], 'source Git blob: ' + pin['path'])


def descending_paths(name, graph):
    # A path terminates in a full geometric self-chain, never in a guessed depth.
    yield ((name, F(1)),)
    for lower, factor in graph[name].lower:
        for tail in descending_paths(lower, graph):
            yield ((name, F(1)), (tail[0][0], F(factor)), *tail[1:])


def path_value(path, graph, tape, terminal_terms=None):
    prefix, scale = F(0), F(1)
    for index, (name, factor) in enumerate(path):
        scale *= factor
        stage = graph[name]
        if index + 1 < len(path):
            prefix += scale * stage.local[tape]
        else:
            if terminal_terms is None:
                tail = stage.local[tape] / (1-stage.contraction)
            else:
                tail = stage.local[tape] * sum((stage.contraction**j for j in range(terminal_terms)), F(0))
            return prefix + scale * tail, scale, stage
    raise ValueError('empty descending path')


coordinate_checks = 0
path_checks = 0
def check_graph(stages):
    global coordinate_checks, path_checks
    graph = {s.name: s for s in stages}
    certificate = model.potentials(stages)
    for stage in stages:
        paths = tuple(descending_paths(stage.name, graph))
        for tape in range(len(stage.local)):
            scored = [(path_value(path, graph, tape)[0], path) for path in paths]
            exact, path = max(scored, key=lambda x: x[0])
            got = certificate[stage.name][tape]
            need(exact == got, 'all descending-path supremum')
            finite, scale, terminal = path_value(path, graph, tape, 32)
            tail = scale * terminal.local[tape] * terminal.contraction**32 / (1-terminal.contraction)
            need(finite + tail == got and finite <= got, 'exact finite-path dual witness')
            c, rho = stage.local[tape], stage.contraction
            slacks = [got-c-rho*got]
            slacks += [got-c-a*certificate[n][tape] for n, a in stage.lower]
            need(min(slacks) == 0, 'tight feasible Bellman inequality')
            need(all(x >= 0 for x in slacks), 'all Bellman inequalities')
            coordinate_checks += 1
            path_checks += len(paths)
    return certificate


rng = random.Random(20261110)
for case in range(48):
    stages = []
    for i in range(7):
        rho = rng.choice((F(0), F(1, 7), F(1, 2), F(4, 5)))
        local = tuple(F(rng.randrange(10), rng.choice((1, 2, 3))) for _ in range(3))
        edges = tuple((str(j), rng.choice((F(1, 3), F(1), F(4), F(18))))
                      for j in range(i) if rng.randrange(2))
        stages.append(model.Stage(str(i), rho, local, edges))
    check_graph(stages)
selected = []
for q1, q2 in ((3, 3), (5, 7), (101, 103)):
    local = tuple(tuple(F(1+i+t, 1+t) for t in range(3)) for i in range(6))
    certificate = check_graph(model.selected_relaxation(q1, q2, local))
    selected.append({'q1': q1, 'q2': q2,
                     'root': [[x.numerator, x.denominator] for x in certificate['C']]})
unit = check_graph(model.selected_relaxation(3, 3))
need(unit['C'] == (F(6572),), 'source-graph unit example')

# A literal two-tape history, with unchanged dirty entry prefixes and retained tails.
initial = (7, 11)
local = (2, 3)
tapes = [bytearray([9])*n for n in initial]
def write_block(tape, start, extent, symbol):
    for position in range(start, start+extent):
        if position == len(tape):
            tape.append(0)
        need(position < len(tape), 'no remote capacity jump')
        tape[position] = symbol

for tape, origin, width in zip(tapes, initial, local):
    write_block(tape, origin, width, 7)
live_peak = 0
for child in ((11, 1), (1, 13))*17:
    live_peak = max(live_peak, sum(initial)+sum(local)+sum(child))
    for tape, origin, parked, width in zip(tapes, initial, local, child):
        write_block(tape, origin+parked, width, 5)
        need(tape[:origin] == bytearray([9])*origin, 'dirty entry prefix preserved')
        need(tape[origin:origin+parked] == bytearray([7])*parked, 'parent preserved')
        write_block(tape, origin+parked, width, 0)
history = {'entry': list(initial), 'retained': [len(t) for t in tapes], 'live_peak': live_peak}
need(history['retained'] == [20, 27] and live_peak == 37, 'crossed tape maxima')
need(sum(history['retained']) == sum(initial) + 13 + 16, 'coordinatewise certificate')
need(sum(history['retained']) > live_peak, 'live peak is not retained backing')

# Counterexample checked using power inequalities and bit lengths, without atom_width/ceil_log.
k = 3215
e0 = k**250
e1 = e0 + 1
need((k-1)**250 < e0 <= k**250 < e1 <= (k+1)**250, 'exact width straddling')
quotient0 = k**249
quotient1 = (e1+k)//(k+1)
need(2**2901 < quotient0 <= 2**2902, 'first depth interval')
need(2**2900 < quotient1 <= 2**2901, 'second depth interval')
depth0, depth1 = 2+(quotient0-1).bit_length(), 2+(quotient1-1).bit_length()
delta_l = depth1-depth0
delta_q = 4*(k*depth1-(k-1)*depth0)
need((depth0, depth1, delta_l, delta_q) == (2904, 2903, -1, -1244),
     'formula-only stock decrease for every q>1 and L>=1')
counter = {'k': k, 'rho': [1, 250], 'N': 2, 'depths': [depth0, depth1],
           'ratio_L_exponent': delta_l, 'ratio_q_exponent': delta_q}

controls = []
def rejects(label, function):
    try:
        function()
    except ValueError:
        controls.append(label)
    else:
        raise ValueError('surviving negative control: '+label)

rejects('one_less_than_least_root', lambda: need(F(6571) >= 1+unit['O2'][0], 'lower exit'))
rejects('live_peak_as_backing', lambda: need(live_peak >= sum(history['retained']), 'history'))
rejects('endpoint_stock_monotonicity', lambda: need(F(1, 96*3**1244) >= 1, 'stock formula'))
wrong = list(model.selected_relaxation(3, 3))
for index in (1, 3):
    s = wrong[index]
    wrong[index] = model.Stage(s.name, s.contraction, s.local, tuple((n, F(1)) for n, _ in s.lower))
wrong_root = model.potentials(wrong)['C'][0]
rejects('omitted_radix_atom_expansion', lambda: need(wrong_root >= unit['C'][0], 'actual lower volumes'))

receipt = {'status': 'PASS_INDEPENDENT_STRATIFIED_SPACE', 'seed': 20261110,
           'coordinate_certificates': coordinate_checks, 'descending_paths_checked': path_checks,
           'selected_graphs': selected, 'unit_root': 6572, 'history': history,
           'stock_counterexample': counter, 'negative_controls': controls,
           'source_pins': len(pins),
           'reviewed_files': {n: sha256((P/n).read_bytes()).hexdigest()
                              for n in ('PROOF.md', 'stack_model.py')},
           'author_suite_rerun': False, 'full_dispatcher_admission': False}
if args.write_result:
    (OUT/'RESULT.json').write_text(json.dumps(receipt, indent=2)+'\n')
else:
    need(receipt == json.loads((OUT/'RESULT.json').read_text()), 'frozen independent receipt')
print(receipt['status'], coordinate_checks, path_checks, len(controls))
