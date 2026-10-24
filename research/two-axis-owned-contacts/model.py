"""Five quotient charts with fully charged owned/shared-native contacts.

Cinna Davis / 1337isnot1337, substantial OpenAI Codex assistance. Apache-2.0.
Source and rank formula: Cao Yifan, Dugongue, Cinna Davis and retained lineage.
This is a discovery rank model, not a signed physical word or supplier.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(test, message):
    if not test:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
                 == row['sha256'], 'Pinned input: ' + row['path'])


authenticate()
spec = importlib.util.spec_from_file_location(
    'two_axis_shared_predecessor', ROOT / 'research/owned-kernel-shared-map/shared_maps.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
M = S.M


def quotient_domains(space, forms=(1, 2), width=9):
    """Preimages of all five subspaces of F2^2, intersected with U."""
    a, b = forms
    need(0 < a < 1 << width and 0 < b < 1 << width and a != b,
         'Two independent binary forms')
    kernels = [M.mask(x for x in range(1 << width) if (x & f).bit_count() % 2 == 0)
               for f in (a, b, a ^ b)]
    return list(dict.fromkeys([space] + [space & k for k in kernels]
                              + [space & kernels[0] & kernels[1]]))


def build(forms=(1, 2)):
    payload = S.payload()
    base = S.build(payload, [forms[0]])
    spaces = [quotient_domains(u, forms) for u in base['old_spaces']]
    domains = [spaces[f] if i not in base['fixed'] and i >= 2 else [spaces[f][0]]
               for i, f in enumerate(base['nodes'])]
    # The predecessor appends one synthetic center sink per owned lifetime.
    _, warps = S.trace(payload, dict(base, nodes=base['nodes'][:-len(base['owned_copies'])]))
    warp_at = {(w['input'], w['output']): w for w in warps}
    maps = {w['op']: w['G_columns'] for w in payload['canonical']['warps']}
    maps.update({-op: M.inv(g) for op, g in list(maps.items())})
    tables = []
    cache = {}
    for kind, a, b, old_ranks in base['edges']:
        left, right = domains[a], domains[b]
        if kind == 'warp' and (a, b) in base['shared_late_maps']:
            op = base['shared_late_maps'][a, b]
            line = base['prelude_lines'].get(op)
            key = kind, tuple(left), tuple(right), line
            if key not in cache:
                cache[key] = [[S.minimum_rank(u, v, line) for v in right] for u in left]
            ranks = cache[key]
        else:
            key = kind, tuple(left), tuple(right)
            if kind == 'warp':
                op = warp_at[a, b]['operator']
                key += (op,)
            if key not in cache:
                if kind == 'warp':
                    g = maps[op]
                    left = [M.mask(M.mv(g, x) for x in range(512) if u >> x & 1)
                            for u in left]
                cache[key] = [[M.fourier_rank(u, v) for v in right] for u in left]
            ranks = cache[key]
        need(ranks[0][0] == old_ranks[0], 'Original paid edge rank')
        tables.append((kind, a, b, ranks))
    helpers = []
    for role, a, b, old_ranks in base['helpers']:
        ranks = [[M.fourier_rank(u, v) for v in domains[b]] for u in domains[a]]
        need(ranks[0][0] == old_ranks[0] and min(map(min, ranks)) > 0,
             'Whole independent helper remains productive')
        helpers.append((role, a, b, ranks))
    result = dict(nodes=base['nodes'], domains=domains, edges=tables, helpers=helpers,
                  owned_copies=base['owned_copies'], forms=list(forms),
                  shared_late_maps=len(base['shared_late_maps']),
                  prelude_lines=len(base['prelude_lines']))
    need(invoice(result, {}) == M.invoice(base, []), 'Complete source baseline')
    return result


def invoice(model, assignment):
    need(all(isinstance(n, int) and 0 <= n < len(model['nodes']) and
             isinstance(s, int) and 0 <= s < len(model['domains'][n])
             for n, s in assignment.items()), 'Legal contact assignment')
    paid, helpers = Counter(), Counter()
    for _, a, b, ranks in model['edges']:
        rank = ranks[assignment.get(a, 0)][assignment.get(b, 0)]
        if rank:
            paid[rank] += 1
    for _, a, b, ranks in model['helpers']:
        rank = ranks[assignment.get(a, 0)][assignment.get(b, 0)]
        need(rank > 0, 'No independent productive helper dropped')
        helpers[rank] += 1
    return paid, helpers


def summary(model):
    return dict(nodes=len(model['nodes']),
                domain_counts=dict(sorted(Counter(map(len, model['domains'])).items())),
                paid_edges=len(model['edges']), helpers=len(model['helpers']),
                owned_centers=len(model['owned_copies']),
                shared_late_maps=model['shared_late_maps'], prelude_lines=model['prelude_lines'])
