#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only, standard-library replay of ten cold-host pattern bounds.

No optimizer, solver status, floating point, or cached bytecode is trusted.
Frozen source bytes are authenticated before the arithmetic engine executes.
The declared local profiles are conditional invoices, not new admitted words.
"""
import ast
import collections
import copy
import gzip
import hashlib
import itertools
import json
import pathlib
import sys
import types
from fractions import Fraction as Q
from functools import lru_cache

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ENGINE_SHA = 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098'
EXPECTED_INPUTS = {
    'vendor/base_two_moment.py', 'vendor/NOTICE-frame-domain-ceiling.md',
    'vendor/SOURCES-frame-domain-ceiling.json', 'vendor/LICENSE',
    'inputs/PR2802-CLAIM.json', 'inputs/PR2802-PROVIDERS.json',
    'inputs/PR2802-OWNER-CHECK.json', 'inputs/PR2802-WORD-base.json.gz',
    'inputs/PR2802-SOURCE-NOTICE', 'inputs/J-relax_host.py',
    'inputs/J-relax_host7.py',
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def counts(value):
    result = {int(r): n for r, n in value.items()}
    need(all(type(n) is int and n >= 0 for n in result.values()), 'nonintegral or negative counts')
    return {r: n for r, n in result.items() if n}

def authenticate(overrides=None):
    overrides = overrides or {}
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    need(set(pins['files']) == EXPECTED_INPUTS, 'unexpected frozen source inventory')
    for rel, record in pins['files'].items():
        path = pathlib.PurePosixPath(rel)
        need(not path.is_absolute() and '..' not in path.parts, 'unsafe source path')
        raw = overrides.get(rel, (HERE / rel).read_bytes())
        need(hashlib.sha256(raw).hexdigest() == record['sha256'], 'source hash mismatch: ' + rel)
        need(len(raw) == record['size'], 'source size mismatch: ' + rel)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == record['git_blob'], 'source Git blob mismatch: ' + rel)
    raw = (HERE / 'vendor/base_two_moment.py').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == ENGINE_SHA, 'frozen arithmetic source mismatch')
    need(hashlib.sha256((HERE / 'CERTIFICATES.json').read_bytes()).hexdigest()
         == pins['generated_certificate_sha256'], 'generated certificate hash mismatch')
    original = pins['files']['vendor/base_two_moment.py']['retained_original_source']
    need(original == json.loads((HERE / 'vendor/SOURCES-frame-domain-ceiling.json').read_text())
         ['files']['engines/base_two_moment.py'], 'retained engine provenance mismatch')
    need(original['git_blob'] == pins['files']['vendor/base_two_moment.py']['git_blob'],
         'retained engine bytes differ from recorded original')
    return raw

def source_constants(name):
    # These copied discovery scripts are parsed, never imported or executed.
    result = {}
    wanted = {'M', 'W', 'CALLS', 'NB', 'WID', 'LOC', 'INV', 'IDLE_PUB'}
    tree = ast.parse((HERE / name).read_text())
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        names = ([target.id] if isinstance(target, ast.Name) else
                 [x.id for x in target.elts] if isinstance(target, ast.Tuple)
                 and all(isinstance(x, ast.Name) for x in target.elts) else [])
        if not wanted.intersection(names):
            continue
        value = ast.literal_eval(node.value)
        for key, val in zip(names, [value] if len(names) == 1 else value):
            if key in wanted:
                result[key] = val
    need(set(result) == wanted, 'missing pinned discovery constants')
    return result

def model_from_sources(document):
    a = source_constants('inputs/J-relax_host.py')
    need(a == source_constants('inputs/J-relax_host7.py'), 'discovery models differ')
    claim = json.loads((HERE / 'inputs/PR2802-CLAIM.json').read_text())
    providers = json.loads((HERE / 'inputs/PR2802-PROVIDERS.json').read_text())
    owner = json.loads((HERE / 'inputs/PR2802-OWNER-CHECK.json').read_text())
    word = json.loads(gzip.decompress((HERE / 'inputs/PR2802-WORD-base.json.gz').read_bytes()))
    local, inventory, idle = a['LOC'], a['INV'], a['IDLE_PUB']
    for provider in providers.values():
        need(counts(provider['actual_paid_profile']) == local, 'provider paid profile mismatch')
        need(dict(collections.Counter(provider['widths'])) == inventory, 'provider inventory mismatch')
    removed = set(word['removed']); v = word['report']['v']; literal_inventory = collections.Counter()
    for r in range(2 * v, 2 * v + word['report']['R']):
        if r not in removed:
            end = len(word.get('helper_final', {}).get(str(r), range(9)))
            start = len(word.get('start_extra', {}).get(str(r), []))
            literal_inventory[end - start] += 1
    need(dict(literal_inventory) == inventory, 'frozen word inventory mismatch')
    need(counts(word['report']['local_profile']) == local, 'frozen word invoice mismatch')
    buffers = len(word['helper_final'])
    need(buffers == 72, 'baseline restored-helper stock mismatch')
    need(owner['owner']['calls'] == a['CALLS'] and owner['owner']['helpers_per_call'] == sum(inventory.values()),
         'owner call/helper counts mismatch')
    need(counts(owner['owner']['idle']) == idle, 'owner idle mismatch')
    global_profile = collections.Counter({r: a['CALLS'] * n for r, n in local.items()}); global_profile.update(idle)
    need(dict(global_profile) == counts(claim['profile']) == counts(owner['profile']), 'baseline global profile mismatch')
    model = {'m': a['M'], 'live': a['W'], 'calls': a['CALLS'], 'bin_counts': a['NB'],
             'width_alphabet': list(a['WID']), 'baseline_local': local,
             'baseline_inventory': inventory, 'baseline_idle': idle,
             'baseline_profile': dict(global_profile), 'rank_mass': sum(r*n for r,n in global_profile.items()),
             'incumbent_kappa': str(Q(claim['kappa'])), 'baseline_buffers': buffers}
    # Canonical JSON compares integer keys with their serialized decimal keys.
    need(json.loads(json.dumps(model)) == document['model'], 'certificate model differs from pinned sources')
    need(model['rank_mass'] == 4816512, 'baseline rank mass mismatch')
    return model

class Checker:
    def __init__(self, model, engine):
        self.model = model; self.engine = engine
        self.nb = model['bin_counts']; self.widths = tuple(model['width_alphabet'])
        self.n = model['calls']; self.W = model['live']; self.B = Q(model['incumbent_kappa'])
        self.patterns = [(R, p) for R in self.nb for k in range(R // min(self.widths) + 1)
                         for p in itertools.combinations_with_replacement(self.widths, k) if sum(p) <= R]
        self.pattern_set = set(self.patterns)
        need(len(self.patterns) == 1163, 'pattern census mismatch')

    @lru_cache(None)
    def cost(self, b, r):
        return self.engine.moment(self.model['m'], 1, [(r, 1)], b) if r else (Q(0), Q(0))

    def expected_case(self, name):
        if name == 'baseline':
            width, k = 9, 0
        else:
            w, t = name.split('-'); width, k = int(w[5:]), int(t[1:])
            need(width in (7, 8, 9) and k in (1, 2, 4), 'case outside declared scope')
        inv = dict(self.model['baseline_inventory']); loc = dict(self.model['baseline_local'])
        if k:
            inv[4] -= k; inv[8] -= k; inv[width] += k
            loc[3] -= k
            if width in (7, 8): loc[2] -= k
            if width == 8: loc[1] += k
        return width, k, inv, loc

    def dual(self, c, inv, loc, cap=False):
        b = Q(c['endpoint']); d = list(map(Q, c['dual']))
        need(0 < b < Q(1, 100), 'endpoint outside engine domain')
        need(len(d) == len(self.nb) + len(self.widths), 'wrong dual length')
        if not cap: need(b == self.B, 'incumbent endpoint changed')
        for R, p in self.patterns:
            lhs = d[list(self.nb).index(R)] + sum(p.count(w)*d[len(self.nb)+i] for i,w in enumerate(self.widths))
            need(lhs <= self.cost(b, R-sum(p))[0], 'dual constraint violation')
        rhs = list(self.nb.values()) + [self.n*inv.get(w, 0) for w in self.widths]
        idle = sum(x*y for x,y in zip(rhs, d))
        local = self.n*sum(n*self.cost(b, r)[0] for r,n in loc.items())
        total = idle + local
        need(idle == Q(c['idle_lower']) and local == Q(c['local_lower']), 'dual invoice mismatch')
        need(total == Q(c['moment_lower']) and total-self.W == Q(c['moment_lower_minus_W']), 'bound margin mismatch')
        need((total >= self.W) == c['certifies_no_improvement_at_endpoint'], 'bound conclusion mismatch')
        if cap: need(total > self.W, 'cap lacks strict rejection')
        allowance = (self.W-total)/(self.n*self.cost(b, 1)[0])
        need(allowance == Q(c['additional_H1_equivalent_per_call_budget_upper']), 'budget mismatch')
        return allowance

    def case(self, record):
        width, k, inv, loc = self.expected_case(record['case'])
        need(counts(record['inventory']) == counts(inv), 'unexpected inventory')
        need(counts(record['local_profile']) == counts(loc), 'unexpected or unbalanced local profile')
        mass = self.n*sum(r*n for r,n in loc.items()) + sum(R*n for R,n in self.nb.items()) - self.n*sum(r*n for r,n in inv.items())
        need(mass == self.model['rank_mass'], 'rank mass changed')
        local_delta = sum(r*n for r,n in loc.items()) - sum(r*n for r,n in self.model['baseline_local'].items())
        inv_delta = sum(r*n for r,n in inv.items()) - sum(r*n for r,n in self.model['baseline_inventory'].items())
        need(record['local_mass_change'] == local_delta == inv_delta == record['inventory_mass_change'], 'local/inventory mass mismatch')
        need(record['helpers'] == sum(inv.values()) and record['roles'] == self.n*sum(inv.values()), 'helper/role count mismatch')
        buffers = self.model['baseline_buffers'] - (k if width == 9 else 0)
        need(record['private_buffers'] == buffers, 'restored-helper stock mismatch')
        need(record['physical'] == self.W + sum(inv.values()) + 8 + buffers + 2, 'physical stock mismatch')
        allowance = self.dual(record['duals']['incumbent'], inv, loc)
        self.dual(record['duals']['cap'], inv, loc, cap=True)
        p = record['integer_pattern']; bins = collections.Counter(); roles = collections.Counter(); idle = collections.Counter()
        for R, pattern, n in p['pattern_fill']:
            need((R, tuple(pattern)) in self.pattern_set and type(n) is int and n > 0, 'invalid integer pattern')
            bins[R] += n
            roles.update({w: n*pattern.count(w) for w in self.widths})
            if R-sum(pattern): idle[R-sum(pattern)] += n
        need(dict(bins) == self.nb, 'bin capacity mismatch')
        need(dict(roles) == {w: self.n*inv.get(w,0) for w in self.widths}, 'helper pattern counts mismatch')
        need(dict(idle) == counts(p['idle']), 'idle invoice mismatch')
        paid = collections.Counter({r: self.n*n for r,n in loc.items()}); paid.update(idle)
        need(dict(paid) == counts(p['profile']), 'global invoice mismatch')
        need(sum(r*n for r,n in paid.items()) == p['rank_mass'] == self.model['rank_mass'], 'global rank mass mismatch')
        lo, hi = map(Q, p['root_bracket'])
        need(0 < lo < hi < Q(1, 100) and hi-lo == Q(1, 10**24), 'invalid root bracket')
        need(sum(n*self.cost(lo, r)[1] for r,n in paid.items()) < self.W, 'root lower endpoint not accepted')
        need(sum(n*self.cost(hi, r)[0] for r,n in paid.items()) > self.W, 'root upper endpoint not rejected')
        return allowance

def run():
    raw = authenticate()
    engine = types.ModuleType('cold_host_rational_moment')
    engine.__file__ = str(HERE / 'vendor/base_two_moment.py')
    exec(compile(raw, engine.__file__, 'exec'), engine.__dict__)
    doc = json.loads((HERE / 'CERTIFICATES.json').read_text())
    model = model_from_sources(doc); checker = Checker(model, engine)
    cases = {r['case']: r for r in doc['cases']}
    expected = {'baseline'} | {f'width{w}-k{k}' for w in (7,8,9) for k in (1,2,4)}
    need(len(cases) == len(doc['cases']) and set(cases) == expected, 'case set mismatch')
    budgets = {name: checker.case(record) for name, record in cases.items()}
    claim = doc['claims']
    need(claim['width9_batches_rejected_at_incumbent'] == [1,2,4], 'batch claim mismatch')
    for k in (1,2,4): need(budgets[f'width9-k{k}'] < 0, 'width9 batch not rejected')
    need(Q(claim['width7_k1_extra_net_tax_H1_less_than']) == Q(17959,1000000), 'rank7 budget claim changed')
    need(Q(claim['width8_k1_extra_net_tax_H1_less_than']) == Q(2893,500000), 'rank8 budget claim changed')
    need(budgets['width7-k1'] < Q(17959,1000000), 'rank7 budget not proved')
    need(budgets['width8-k1'] < Q(2893,500000), 'rank8 budget not proved')
    fixture = cases['width8-k1']
    controls = {
        'unbalanced_H1_undo': lambda d: d['local_profile'].__setitem__('1', d['local_profile']['1']+1),
        'unbound_dual_price': lambda d: d['duals']['incumbent']['dual'].__setitem__(0, str(Q(d['duals']['incumbent']['dual'][0])+1)),
        'omitted_private_buffer': lambda d: d.__setitem__('private_buffers', d['private_buffers']-1),
        'forged_rejection': lambda d: d['duals']['incumbent'].__setitem__('certifies_no_improvement_at_endpoint', True),
        'fractional_pattern_count': lambda d: d['integer_pattern']['pattern_fill'][0].__setitem__(2, '1/2'),
        'false_root_bracket': lambda d: d['integer_pattern'].__setitem__('root_bracket', ['1/1000', str(Q(1,1000)+Q(1,10**24))]),
    }
    rejected = {}
    for name, mutate in controls.items():
        d = copy.deepcopy(fixture); mutate(d)
        try: checker.case(d)
        except (ValueError, TypeError) as ex: rejected[name] = str(ex)
        else: raise ValueError('control incorrectly accepted: '+name)
    try: authenticate({'vendor/base_two_moment.py': raw+b'\n'})
    except ValueError as ex: rejected['changed_engine_before_execution'] = str(ex)
    else: raise ValueError('changed engine accepted')
    return {'status': 'PASS_EXACT_COLD_HOST_PRICING', 'cases': len(cases), 'patterns_per_dual': len(checker.patterns),
            'exact_duals': 2*len(cases), 'integer_pattern_root_brackets': len(cases),
            'rank_mass': model['rank_mass'], 'negative_controls': rejected,
            'scope': 'Exact conditional bounds for declared profiles and inventory; no literal owner-fill or new kappa claim.'}

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
