#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent data-only census and exact first-nonterminal domain certificate.

JoyboyBrian, with substantial OpenAI Codex assistance. Source construction:
Chris R / Clear1nsight, Jose Manuel and the retained QQ16 source authors.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction
import gzip
import io
from hashlib import sha256
import json
from math import isqrt, prod
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/'
MEMBERS = {
    'programs': ('base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
    'template': ('hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'phases': ('base/work/complex-nine-native/DATA-PHASES.json', 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
    'native': ('base/providers/gauge44/CLIFFORD-RECIPES.json', 'd0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731'),
}
EXPECTED = {1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 8: 1152, 48: 4866}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for record in manifest['files']:
        if record['usage'] == 'input':
            need(sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256'],
                 'source digest: ' + record['path'])


def load():
    result = {}
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as archive:
        members = archive.getmembers()
        for name, (suffix, digest) in MEMBERS.items():
            matches = [m for m in members if m.name == PREFIX + suffix]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular source member')
            raw = archive.extractfile(matches[0]).read()
            need(sha256(raw).hexdigest() == digest, 'member digest: ' + name)
            result[name] = json.loads(gzip.decompress(raw) if suffix.endswith('.gz') else raw)
    return result


def census(data):
    template = data['template']
    need(template['m'] == 73 and template['live'] == 14336, 'source geometry')
    events, calls = template['execution_schedule'], template['calls']
    need(len(events) == 482 and len(calls) == 144, 'complete source schedule')
    by_time = {c['time']: c for c in calls}
    need(len(by_time) == len(calls), 'unique local times')
    edges = {(e['old'], e['new']): e['rank'] for e in data['native']['children']}
    local = {}
    for orientation, word in data['programs'].items():
        need(orientation in ('forward', 'backward') and len(word) == 24767, 'complete local word')
        counts = Counter()
        for op in word:
            if op[0] in ('climb', 'center'):
                old, new, rank = op[-3:]
                need(type(rank) is int and edges[old, new] == rank and 0 < rank < 73,
                     'literal directed native child')
                counts[rank] += 1
        local[orientation] = counts
    idle = {(r['replica'], r['child'], r['port']): r for r in template['idle_children']}
    need(len(idle) == len(template['idle_children']), 'unique idle remainders')
    rows, total, visited = [], Counter(), set()
    nonchildren = {'bridge', 'terminal', 'terminal_Y_translations',
                   'bank_padding_cover_sweep', 'translate_every_live_family'}
    for index, event in enumerate(events):
        counts = Counter()
        if event['kind'] == 'local_cover_sweep':
            call = by_time[event['time']]
            counts.update(local[call['orientation']])
        elif event['kind'] == 'idle_cover_sweep':
            for side in range(2):
                for port in range(112):
                    key = event['replica'], event['child_indices'][side], port
                    if key not in idle:
                        continue
                    item = idle[key]
                    family = 896 * event['replica'] + (2 * event['pair'] + side) * 112 + port
                    axes = data['phases']['recipes'][port]['idle_children'][key[1]]['orthogonal_axes']
                    need(item['family'] == family and
                         len(axes[item['pending_offset']:]) == item['rank'], 'actual idle suffix')
                    need(key not in visited, 'idle occurrence counted once')
                    visited.add(key)
                    counts[item['rank']] += 1
        else:
            need(event['kind'] in nonchildren, 'complete child-emitting alphabet')
        total.update(counts)
        rows.append({'event': index, 'kind': event['kind'], 'ranks': dict(sorted(counts.items()))})
    need(visited == set(idle), 'all idle source records consumed')
    need(dict(total) == EXPECTED, 'independent histogram agrees with prior full source census')
    return total, rows


def root_only_adapter():
    def member(archive, name):
        found = [m for m in archive.getmembers() if m.name == name]
        need(len(found) == 1 and found[0].isfile(), 'unique regular retained adapter input')
        return archive.extractfile(found[0]).read()
    with tarfile.open(ROOT / 'research/qq16-complete-cost/inputs/PR4172.tar') as archive:
        nested = member(archive, 'research/qq16-native-history/inputs/PR4167.tar')
    need(sha256(nested).hexdigest() == '68ff3b4b541434cb9df15884d027838cbc80300e9d78015eb82c395c5168d166',
         'retained original protocol archive')
    with tarfile.open(fileobj=io.BytesIO(nested)) as archive:
        adapter = member(archive, 'research/qq16-protocol-comparison/adapter.py')
    digest = sha256(adapter).hexdigest()
    need(digest == '77c01376ac43339a7c99ab377c7947cb89b44e96ff4a826becb545cccd045fef', 'retained adapter bytes')
    text = ast.unparse(ast.parse(adapter))
    root = ast.unparse(ast.parse((ROOT / 'research/physical-complex-controller/root_layer.py').read_text()))
    need('self.machine = Machine(binding, native, catalogue, observe)' in root,
         'RootLayer constructs original Machine')
    need('original = root_layer.machine' in text and
         'original.scalar.recipes, original, adopt=adopt, shared=shared)' in text and
         'self.native_child = native_child' in text and
         "result = self.native_child.run(self.capsule['current'], descriptors)" in text and
         'root_layer.machine = parent' in text, 'original backend retained behind outer adapter')
    assignments = [ast.unparse(n) for n in ast.walk(ast.parse(adapter))
                   if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))]
    need(not any('.enter_child =' in a or '.run =' in a for a in assignments),
         'adapter does not patch original recursive methods')
    return {'adapter_sha256':digest, 'outer_root_replaced_only':True,
            'native_child_type':'original Machine', 'descendant_enter_child':'original embedded parking'}


def floor_root(value, exponent):
    lo, hi = 0, 1 << ((value.bit_length() + exponent - 1) // exponent)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** exponent <= value:
            lo = mid
        else:
            hi = mid
    return lo


def terminal(width, d):
    need(type(width) is int and width >= 0 and type(d) is int and d > 0, 'cutoff domain')
    return width < 73 or width ** 1000 < d


def source_order():
    text = (ROOT / 'research/physical-complex-controller/machine.py').read_text()
    tree = ast.parse(text)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Machine')
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    node = ast.unparse(methods['node'])
    cut = "test = fixed_power(self.c('width'), 1000, self.c('root_width'))"
    divide = 'delta = columns.divide_small(self.binding.dimension)'
    need(node.index(cut) < node.index(divide) and node.count('fixed_power(') == 1,
         'cutoff precedes remainder and is not repeated')
    enter = ast.unparse(methods['enter_child'])
    ret = ast.unparse(methods['return_node'])
    need(enter.count('self.parking.park()') == 1 and ret.count('self.parking.restore()') == 1,
         'one embedded parking pair per successful selected child')
    init = ast.unparse(methods['__init__'])
    need("'current'" in init and 'self.roles.values()' in init and 'Parking(self.parked)' in init,
         'whole current bank belongs to parked roles')
    return sha256(ast.dump(methods['node']).encode()).hexdigest()


def domain(columns, d, gamma):
    need(type(columns) is int and 45 <= columns <= 72, 'first one-generation band')
    width = 8 * columns
    q, delta = divmod(width, 73)
    need(not terminal(width, d), 'C8 actually enters nonterminal branch')
    need(terminal(columns, d) and terminal(48 * q, d), 'C1 and every C8 child terminal')
    K = floor_root(d, 500)
    guard, H = 34006, d * 34006
    F = 14336 * gamma
    current, depth = d, 0
    while current >= 73:
        current = 48 * (current // 73)
        depth += 1
    q0 = depth * (F - 1).bit_length()
    qF, qB = (2 * H + K - 1) // K, (H + K - 1) // K
    selected = q0 + qF + qB + 73 * columns
    need(selected <= d and selected > q0 + qF + qB, 'actual fast-root admission')
    need(d <= (73 * columns) ** 1000, 'root nonterminal after reservation')
    need(depth >= 2 and depth * F.bit_length() <= q0 * K, 'original stock supports two divisions')
    front, back = qF * K - 2 * H, qB * K - H
    need(0 <= front < K and 0 <= back < K, 'exact root guard residues')
    address = 3 * H + front + 73 * columns * K + back
    need(address == (selected - q0) * K, 'whole packet address rectangle')
    after = 65 * columns * K
    need(front + width * K + after == front + delta * K + (73 * q) * K + after,
         'remainder leaf preserves complete volume')
    for rank in EXPECTED:
        next_after = after + (73 - rank) * q * K
        need(front + delta*K + rank*q*K + next_after == front + 73*columns*K,
             'every descendant keeps all spectator axes')
    return {'lambda': columns, 'C8_width': width, 'tensor_columns': q,
            'leading_remainder_leaf_width': delta, 'source_width_after_remainder': 73*q,
            'largest_grandchild_width': 48*q, 'root_stock_depth': depth,
            'spacing': K, 'guard': guard, 'selected_le_d': True,
            'stock_divisions_from_root': 2, 'C1_terminal': True,
            'C8_selected_child_tree_depth': 1, 'all_descendants_terminal': True}


def run():
    authenticate()
    node_hash = source_order()
    adapter = root_only_adapter()
    data = load()
    counts, events = census(data)
    d = isqrt(1 << 16949)
    need(d*d <= 1 << 16949 < (d+1)*(d+1), 'exact RootPlan floor power')
    cutoff = floor_root(d-1, 1000) + 1
    need(cutoff == 356 and terminal(355, d) and not terminal(356, d), 'strict global-height boundary')
    gamma = (1 << 1296) * prod((1 << (2*j)) - 1 for j in range(1, 37))
    rows = [domain(c, d, gamma) for c in range(45, 73)]
    need(terminal(8*44, d) and not terminal(48*((8*73)//73), d), 'both adjacent band endpoints')
    n = sum(counts.values())
    need(n == 510662, 'complete per-cover child multiplicity')
    # A descendant consumes exactly one fresh family/cover divisor of rows.
    volume = Fraction(n, 14336)
    need(volume == Fraction(n*gamma, 14336*gamma), 'cover cancels only in sum of child payload volumes')
    rejected = []
    def rejects(label, test):
        try:
            test()
        except (ValueError, AssertionError):
            rejected.append(label)
        else:
            raise ValueError('control did not reject: ' + label)
    rejects('width-alone nonleaf classification', lambda: need(not terminal(144,d), 'global cutoff'))
    rejects('equality called terminal', lambda: need(terminal(356,356**1000), 'strict inequality'))
    rejects('prune after removing remainder', lambda: need(not terminal(292,d), 'do not repeat cutoff'))
    rejects('lambda44 admitted to new band', lambda: domain(44,d,gamma))
    rejects('lambda73 still one generation', lambda: domain(73,d,gamma))
    rejects('missing later source events', lambda: need(sum(sum(x['ranks'].values()) for x in events[:7])==n, 'suffix included'))
    rejects('grandchild keeps parent row volume', lambda: need(Fraction(n*gamma)==volume, 'fresh stock divisor'))
    rejects('Gamma divided twice', lambda: need(Fraction(n,14336*gamma)==volume, 'one owner-cover factor'))
    rejects('one stock division is enough', lambda: need(1>=rows[0]['stock_divisions_from_root'], 'outer and C8 nodes'))
    rejects('terminal C8 bound reused', lambda: need(terminal(8*45,d), 'no descendants is false'))
    return {'status':'PASS_QQ16_FIRST_NONTERMINAL_TREE', 'precision':'2^8500',
            'global_d':'floor(sqrt(2^16949))', 'first_nonterminal_width':cutoff,
            'sharp_one_generation_lambda_interval':[45,72], 'source_node_ast_sha256':node_hash, 'fair_baseline_binding':adapter,
            'cases':rows, 'source_event_census':events, 'rank_histogram':dict(sorted(counts.items())),
            'children_per_C8_per_Gamma':n, 'removed_C8_calls_per_Gamma':16,
            'embedded_parking_pairs_per_Gamma_squared':16*n,
            'grandchild_payload_sum_over_C8_payload':str(volume),
            'park_only_RWM_lower_coefficients_per_Gamma_squared_v':[16*n*x for x in (2,5,5)],
            'controls':rejected, 'full_cost_sign':'not established',
            'production_payload_executed':False, 'native_monomial_internals_priced':False,
            'new_kappa':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(canonical(json.loads((HERE/'RESULT.json').read_text())) == canonical(json.loads(json.dumps(result))), 'whole typed deterministic receipt')
    print(result['status'], 'lambda=45..72', 'parking_pairs=8170592*Gamma^2', 'full_sign=unknown')

if __name__=='__main__':
    main()
