#!/usr/bin/env python3
"""Exact audit of one scalar-to-recursive cost implication; Apache-2.0.

Ross Richardson with substantial OpenAI Codex assistance. The primitive emitter
is credited source code; the symbolic interpreter, typed model, invoice, and
tariff countermodel below do not use its matrix or verification functions.
"""
import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIZE = 56


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity():
    return [[int(i == j) for j in range(SIZE)] for i in range(SIZE)]


def add(rows, target, source, sign):
    rows[target] = [a + sign*b for a, b in zip(rows[target], rows[source])]


def rotate(rows, start, size, power):
    for first in range(start, start + size, 4):
        old = rows[first:first+4]
        rows[first:first+4] = [old[(j-power) % 4][:] for j in range(4)]


def typed_apply(trace):
    rows = identity()
    for kind, arg, sign in trace:
        if kind == 'copy':
            for j in range(24):
                add(rows, 32+j, 8+j, sign)
        elif kind == 'P':
            rotate(rows, 32, 24, arg)
        elif kind == 'Q':
            rotate(rows, 0, 8, arg)
        elif kind == 'child':
            if sign == -1:
                rotate(rows, 32, 24, -1)
            for j in range(8):
                add(rows, j, 32+8*arg+j, sign)
            if sign == 1:
                rotate(rows, 32, 24, 1)
        else:
            raise ValueError('unknown typed operation')
    return rows


def inverse(trace):
    return [(kind, -arg if kind in ('P', 'Q') else arg,
             -sign if kind in ('copy', 'child') else sign)
            for kind, arg, sign in reversed(trace)]


def batch(states, blocks):
    require(len(states) == len(blocks)+1, 'phase path length')
    trace = [('P', states[0], 1), ('Q', states[0], 1)]
    for old, new, block in zip(states, states[1:], blocks):
        trace += [('child', block, 1), ('P', (new-old-1) % 4, 1),
                  ('Q', (new-old) % 4, 1)]
    return trace


def echo(body):
    return [('copy', 0, 1)] + body + [('copy', 0, -1)] + inverse(body)


def expected(blocks):
    rows = identity()
    for block in blocks:
        for j in range(8):
            rows[j][8+8*block+j] += 1
    return rows


def primitive_apply(word):
    rows = identity()
    for kind, target, source, sign in word:
        if kind == 'ADD':
            require(source is not None and sign in (-1, 1), 'bad ADD')
            add(rows, target, source, sign)
        elif kind == 'NEG':
            rows[target] = [-a for a in rows[target]]
        else:
            raise ValueError('unknown scalar primitive')
    return rows


def primitive_inverse(word):
    return [(kind, target, source, -sign if kind == 'ADD' else sign)
            for kind, target, source, sign in reversed(word)]


def invoice(trace):
    # Actual PR1391 leaf invoice and phase implementation. Every literal inverse
    # has the same ADD/NEG count; no recursive tariff is inferred from these.
    phases = [(0, 0), (18, 2), (12, 4), (18, 2)]
    adds = negs = 0
    for kind, arg, sign in trace:
        if kind == 'child':
            a, n = 62, 6
        elif kind == 'copy':
            a, n = 24, 0
        else:
            a, n = phases[arg % 4]
            if kind == 'P':
                a, n = 3*a, 3*n
        adds += a
        negs += n
    return {'ADD': adds, 'NEG': negs, 'total': adds+negs}


def child_counts(trace):
    return Counter((arg, sign) for kind, arg, sign in trace if kind == 'child')


def tariff(trace, charges):
    out = Counter()
    for key, count in child_counts(trace).items():
        for rank, multiplicity in charges[key].items():
            require(rank > 0 and multiplicity >= 0, 'nonnegative tariff required')
            out[rank] += count*multiplicity
    return dict(sorted(out.items()))


def build_result():
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if entry['usage'] == 'input':
            require(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()
                    == entry['sha256'], 'source mismatch: '+entry['path'])
    external = json.loads((HERE/'EXTERNAL-SOURCE.json').read_text())
    for entry in external['files']:
        require(hashlib.sha256((HERE/entry['path']).read_bytes()).hexdigest()
                == entry['sha256'], 'external source mismatch: '+entry['path'])
    legacy = load(ROOT/'research/z4-persistent-pair-seed57/inputs/PR1391-verify.py', 'pinned1391')
    primary = load(HERE/'inputs/pr2464/verify.py', 'pinned2464')
    joint_body = batch([0, 1, 0], [0, 1])
    joint = echo(joint_body)
    separate = echo(batch([0, 0], [0])) + echo(batch([0, 0], [1]))
    want = expected([0, 1])
    require(typed_apply(joint) == want == typed_apply(separate), 'typed dirty map')
    require(typed_apply(joint+inverse(joint)) == identity(), 'typed literal cleanup')
    jw = primary.echo_word(legacy, [0, 1, 0], [0, 1])
    sw = (primary.echo_word(legacy, [0, 0], [0]) +
          primary.echo_word(legacy, [0, 0], [1]))
    for name, word, trace in [('joint', jw, joint), ('separate', sw, separate)]:
        require(primitive_apply(word) == want, name+' source primitive dirty map')
        require(primitive_apply(word+primitive_inverse(word)) == identity(), name+' inverse')
        count = Counter(row[0] for row in word)
        bill = invoice(trace)
        require(dict(count) == {'ADD': bill['ADD'], 'NEG': bill['NEG']}, name+' invoice')

    # Complete 4^k path census for k=1,2, independently of PR2464's DP.
    minima = {}
    for k in (1, 2):
        costs = []
        for prefix in itertools.product(range(4), repeat=k):
            body = batch(list(prefix)+[0], list(range(k)))
            require(typed_apply(echo(body)) == expected(list(range(k))), 'phase census map')
            costs.append(invoice([x for x in body if x[0] != 'child'])['total'])
        minima[str(k)] = {'paths': len(costs), 'boundary_min': min(costs)}
    require(minima == {'1': {'paths': 4, 'boundary_min': 60},
                      '2': {'paths': 16, 'boundary_min': 88}}, 'boundary minima')
    require(child_counts(joint) == child_counts(separate), 'typed child multiset')
    saved = invoice(separate)['total'] - invoice(joint)['total']
    wrapper_saved = (invoice([x for x in separate if x[0]=='copy'])['total'] -
                     invoice([x for x in joint if x[0]=='copy'])['total'])
    boundary_saved = (invoice([x for x in separate if x[0] in ('P','Q')])['total'] -
                      invoice([x for x in joint if x[0] in ('P','Q')])['total'])
    require((saved,wrapper_saved,boundary_saved) == (112,48,64), 'scalar saving decomposition')
    require(saved == wrapper_saved+boundary_saved, 'complete saving invoice')
    symbolic_counts = {f'C{b}{"+" if sign > 0 else "-"}': n
                       for (b, sign), n in sorted(child_counts(joint).items())}
    tariffs = {
        'rank8_per_child': {key: {8: 1} for key in child_counts(joint)},
        'baseline_matched_rank8': {key: {8: 4} for key in child_counts(joint)},
        'orientation_dependent': {(0, 1): {1: 2, 7: 1}, (0, -1): {2: 3},
                                  (1, 1): {8: 2}, (1, -1): {3: 1, 48: 1}},
    }
    tariff_results = {}
    for name, charges in tariffs.items():
        a, b = tariff(joint, charges), tariff(separate, charges)
        require(a == b, 'tariff equality: '+name)
        tariff_results[name] = a
    require(tariff_results['rank8_per_child'] == {8: 4}, 'concrete tariff countermodel')
    require(tariff_results['baseline_matched_rank8'] == {8: 16}, 'baseline-matched countermodel')

    # Bind the audited transfer to the exact source, not an invented headline.
    tree = ast.parse((HERE/'inputs/pr2464/verify.py').read_text())
    assignments = []
    hist = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'hist_base':
                    hist = ast.literal_eval(node.value)
                if (isinstance(target, ast.Subscript) and
                    isinstance(target.value, ast.Name) and target.value.id == 'hist_shared'):
                    assignments.append({'line': node.lineno, 'rank': ast.literal_eval(target.slice),
                                        'count': ast.literal_eval(node.value)})
    selected = json.loads((ROOT/'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    require(hist == {int(k):v for k,v in selected['complex_profile'].items()}, 'selected baseline binding')
    require(assignments == [{'line': 524, 'rank': 8, 'count': 576}], 'audited literal ledger assignment')

    # Semantic controls exercise maps, cleanup, child counts, and the claim's
    # missing implication. They do not merely check the source hash.
    controls = []
    def reject(name, ok):
        require(ok, 'semantic control failed: '+name)
        controls.append(name)
    omitted = [x for x in joint_body if x != ('child', 1, 1)]
    reject('omitted_second_child', typed_apply(echo(omitted)) != want)
    wrong = joint_body[:]
    pos = next(i for i,x in enumerate(wrong) if x == ('Q', 1, 1))
    wrong[pos] = ('Q', 2, 1)
    reject('wrong_output_phase', typed_apply(echo(wrong)) != want)
    reject('forward_substituted_for_inverse', typed_apply(
        [('copy',0,1)]+joint_body+[('copy',0,-1)]+joint_body) != want)
    reject('copy_out_omitted', typed_apply([('copy',0,1)]+joint_body+inverse(joint_body)) != want)
    damaged_word = jw[:]
    i = next(i for i,x in enumerate(damaged_word) if x[0]=='ADD' and x[1]<8)
    k,t,s,sign = damaged_word[i]
    damaged_word[i] = (k,t,s,-sign)
    reject('primitive_sign_mutation', primitive_apply(damaged_word) != want)
    removed = joint[:]
    removed.pop(next(i for i,x in enumerate(removed) if x[0]=='child' and x[2]==-1))
    reject('missing_inverse_child_changes_tariff', tariff(removed,tariffs['rank8_per_child']) != {8:4})
    reject('eight_child_saving_not_entailed',
           tariff(joint,tariffs['baseline_matched_rank8']).get(8,0) !=
           tariff(separate,tariffs['baseline_matched_rank8']).get(8,0)-8)
    # Under the charged-wrapper premise, one can attain a deletion. This is a
    # positive premise control, not a model of selected native COPY/ERASE.
    count_wrappers = lambda tr: sum(k=='copy' and s==1 for k,a,s in tr)
    require(count_wrappers(separate)-count_wrappers(joint) == 1, 'wrapper count')
    require(8*(count_wrappers(separate)-count_wrappers(joint)) == 8, 'conditional wrapper tariff')
    return {
        'result': 'PASS_Z4_CENTRE_TRANSFER_AUDIT', 'scope': 'typed tariff non-entailment; no native obstruction or new kappa',
        'source_head': external['head'], 'phase_census': minima,
        'basis_columns': SIZE, 'matrix_coefficients_per_map': SIZE*SIZE,
        'joint_invoice': invoice(joint), 'separate_invoice': invoice(separate),
        'saving': {'total_primitives': saved, 'wrapper_ADD': wrapper_saved, 'boundary_primitives': boundary_saved},
        'same_child_multiset': symbolic_counts, 'tariff_countermodels': tariff_results,
        'source_histogram_assignment': assignments,
        'hypothetical_rank8_deletion_global': hist[8]-assignments[0]['count'],
        'hypothetical_pairs': 72, 'claimed_deletion_per_pair': 8,
        'recursive_transfer': 'NOT_ESTABLISHED_BY_TYPED_CONTRACT',
        'conditional_charged_wrapper_control': 'one deleted wrapper saves eight rank8 children ONLY if that tariff binding is added',
        'semantic_controls': controls,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = build_result()
    payload = json.loads(json.dumps(result))
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    else:
        require(payload == json.loads((HERE/'RESULT.json').read_text()), 'complete result mismatch')
    print('PASS_Z4_CENTRE_TRANSFER_AUDIT scalar_saving=112 child_multiset_unchanged=4 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()
