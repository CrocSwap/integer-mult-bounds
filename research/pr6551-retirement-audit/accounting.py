#!/usr/bin/env python3
"""Independent PR6551/PR6545 invoice delta from literal caller data.

No predecessor Python module is imported. Native costs cancel only after checking
that the candidate retains the exact predecessor native archive and that both
callers invoke LOCAL once for each of the same eighteen stages. The native
archive is authenticated as bytes here, not mathematically replayed.
Prepared for DLamdata with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import io
import gzip
import json
from pathlib import Path
import tarfile


class AccountingError(ValueError):
    pass


def need(test, message):
    if not test:
        raise AccountingError(message)


def member(raw, path):
    """Read one unique ordinary member, without extracting archive paths."""
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
        found = [m for m in archive.getmembers() if m.name == path]
        need(len(found) == 1 and found[0].isfile(), 'unique regular archive member: '+path)
        need(found[0].size <= 20_000_000, 'bounded archive member')
        return archive.extractfile(found[0]).read()


def old_root(raw):
    for path in [
        'research/p104-scaled-transport-fusion/source.tar',
        'research/p104-third-anchor-clean-mixed-root/root-source.tar',
        'research/mixed-projector-query-root/ROOT.json',
    ]:
        raw = member(raw, path)
    return json.loads(raw)


def tree_inventory(root):
    """Derive stage sets and internal-node sizes by literal leaf traversal."""
    next_stage = 1
    internal = []

    def descend(tree):
        nonlocal next_stage
        if type(tree) is int:
            need(tree == 1, 'leaf marker')
            stages = (next_stage,)
            next_stage += 1
            return stages
        need(type(tree) is list and len(tree) == 2, 'binary tree')
        stages = descend(tree[0])+descend(tree[1])
        internal.append(stages)
        return stages

    need(len(root['children']) == 4, 'four root children')
    children = [descend(tree) for tree in root['children']]
    need(root['child_sizes'] == [len(s) for s in children], 'declared child sizes')
    need(next_stage == 19 and len(internal) == 14, 'eighteen leaves and fourteen binary nodes')
    return children, internal


def root_targets(root, children, internal):
    """Count root masks and node pairs, then split the C pivot's Q C target."""
    need(root['fields'] == 6, 'six root fields')
    need(root['full_sites'] == [0, 1, 5, 6] and root['thin_sites'] == [2, 3, 4], 'retained full/thin sites')
    masks = root['masks']
    need(len(masks) == 6 and all(len(m) == 4 and all(type(x) is int and x in (0,1) for x in m) for m in masks), 'binary root target masks')
    need(masks[4] == [0,0,1,0], 'retired root pivot is C')
    counts = Counter()
    for mask in masks:
        counts[1+8*sum(len(s)*yes for s,yes in zip(children,mask))] += 1
    for stages in internal:
        counts[1+8*len(stages)] += 2
    counts[1+8*len(children[2])] -= 1
    counts[1] += 1
    counts[8*len(children[2])] += 1
    return +counts


def inspect_caller(word, root):
    need(word['schema'] == 'mixed-projector-query-root/2', 'caller schema')
    need(word['roles'] == 35 and word['stages'] == 18 and word['ambient_rank'] == 153, 'caller dimensions')
    children, internal = tree_inventory(root)
    # The declarative nodes and executable idles are separate checks against
    # the literal root tree. Neither is used as the other's expected invoice.
    need(Counter(tuple(n['stages']) for n in word['nodes']) == Counter(internal), 'tree-to-node stage sets')
    need(len(word['nodes']) == 14, 'node count')
    roles = [tuple(n['roles']) for n in word['nodes']]
    need(roles == [(i,i+1) for i in range(6,34,2)], 'distinct node role pairs')
    need(all(n['exponent'] in (-1,1) for n in word['nodes']), 'node central orientations')
    targets = Counter()
    need(len(word['diagonal']) == 35, 'one target per arbitrary input')
    for row in word['diagonal']:
        need(len(row) == 20 and row[0] in (-1,0,1), 'target Laurent signature')
        need(all(type(x) is int and x in (0,1) for x in row[1:]), 'binary fresh-stage exponents')
        need(row[1] == 0, 'no stage-zero target in this caller')
        rank = abs(row[0])+8*sum(row[2:])
        need(rank > 0, 'strictly productive target')
        targets[rank] += 1
    need(targets == root_targets(root,children,internal), 'tree-to-endpoint productive ranks')
    # Pin which field is retired, not just its rank histogram.
    need(word['diagonal'][4] == [-1]+[0]*19, 'returned pivot has only central Q inverse')
    need(word['diagonal'][34] == [0,0]+[int(s in children[2]) for s in range(1,19)], 'fresh independent suffix has exactly C')
    paid = Counter()
    idles, singles, stages = [], [], []
    query_count = 0
    ordinary = Counter()
    for event in word['events']:
        need(type(event) is list and event, 'event encoding')
        op = event[0]
        if op == 'LOCAL':
            need(len(event) == 4 and type(event[1]) is int and 1 <= event[1] <= 18, 'LOCAL stage')
            stages.append(event[1])
        elif op == 'QUERY':
            need(len(event) == 4 and event[3] in (-1,1), 'rank-one QUERY sign')
            query_count += 1
            paid[1] += 1
        elif op in ('IDLE','IDLE_ONE'):
            expected_len = 4 if op == 'IDLE' else 3
            need(len(event) == expected_len, 'idle arity')
            subset = event[-1]
            need(type(subset) is list and subset and len(set(subset)) == len(subset) and all(type(s) is int and 1<=s<=18 for s in subset), 'distinct fresh idle stages')
            if op == 'IDLE':
                idles.append(tuple(subset)); multiplicity = 2
            else:
                singles.append(tuple(subset)); multiplicity = 1
            paid[8*len(subset)] += multiplicity
        elif op == 'Q_POWER':
            need(len(event) == 3 and event[2] in (-2,2), 'ordinary Q-square translation only')
            ordinary[op] += 1
        elif op in ('ADD','SWAP','SCALE','LAMBDA'):
            ordinary[op] += 1
        else:
            raise AccountingError('unaccounted event '+str(op))
    need(stages == list(range(1,19)), 'same ordered LOCAL stage calls')
    need(query_count == len(internal)+len(root['thin_sites']), 'all binary and root thin queries paid')
    need(Counter(idles) == Counter(internal), 'all binary-node whole idles paid')
    need(Counter(singles) == Counter((children[1],children[2])), 'both additional root whole idles paid')
    need(sum(targets.values()) == 35, 'all independent targets counted')
    return {
        'target_per_port': targets,
        'paid_per_port': paid,
        'internal_nodes': Counter(map(len,internal)),
        'children': [len(s) for s in children],
        'ordinary_events': ordinary,
        'local_stages': stages,
    }


def delta(old,new,multiplier=104):
    return {str(r):multiplier*(new[r]-old[r]) for r in sorted(old.keys()|new.keys()) if new[r]!=old[r]}


def plain(counter):
    return {str(k):counter[k] for k in sorted(counter)}


def rejects(fn, expected):
    try:
        fn()
    except AccountingError as error:
        need(str(error) == expected, 'wrong rejection reason: '+str(error))
        return str(error)
    raise AccountingError('invalid control accepted: '+expected)


def run(predecessor,candidate):
    old_bytes = (predecessor/'CONTROLLER.json').read_bytes()
    new_bytes = (candidate/'CONTROLLER.json').read_bytes()
    old_word,new_word = json.loads(old_bytes),json.loads(new_bytes)
    retained = (candidate/'source.tar').read_bytes()
    native_archive = member(retained,'research/gaussian-root-retirement/native-source.tar')
    # This hash was obtained independently from the exact PR6545 source head.
    need(sha256(native_archive).hexdigest() == '2e4e49580c51758281bd9e4618f99d38f3a3622117d5c73bae0fce2db3616fa4', 'exact predecessor native archive')
    original_root,new_root = old_root(native_archive),json.loads((candidate/'ROOT.json').read_bytes())
    for name in ('CONTROLLER.json','WITNESS.json'):
        need(member(retained,'research/gaussian-root-retirement/'+name) == (predecessor/name).read_bytes(), 'candidate retains exact predecessor '+name)
    need((candidate/'WITNESS.json').read_bytes() == (predecessor/'WITNESS.json').read_bytes(), 'unchanged retirement witness')
    omit = {'children','child_sizes'}
    need({k:v for k,v in original_root.items() if k not in omit} == {k:v for k,v in new_root.items() if k not in omit}, 'unchanged root outside child allocation')
    native = json.loads(gzip.decompress(member(native_archive, 'research/p104-scaled-transport-fusion/WORD.json.gz')))
    ports = len(native['ports'])
    need(ports == 104 and len(set(native['ports'])) == ports and len(native['live']) == ports, 'retained distinct native ports')
    native_moves = sum(e[0] == 'MOVE' for e in native['program'])
    native_helpers = native['public'] - 2*ports
    need(native_helpers == 562 and native_moves == 3456, 'retained structural call counts')
    before = inspect_caller(old_word,original_root)
    after = inspect_caller(new_word,new_root)
    # Independent controls perturb the boundary data actually read above.
    controls = {}
    missing_idle = deepcopy(new_word)
    index = next(i for i,e in enumerate(missing_idle['events']) if e[0] == 'IDLE_ONE' and len(e[-1])==5)
    del missing_idle['events'][index]
    controls['missing_third_child_idle'] = rejects(lambda:inspect_caller(missing_idle,new_root), 'both additional root whole idles paid')
    wrong_target = deepcopy(new_word)
    wrong_target['diagonal'][34][0] = -1
    controls['unearned_central_target'] = rejects(lambda:inspect_caller(wrong_target,new_root), 'tree-to-endpoint productive ranks')
    wrong_stage = deepcopy(new_word)
    wrong_stage['diagonal'][34][2+9] = 0
    controls['missing_suffix_stage'] = rejects(lambda:inspect_caller(wrong_stage,new_root), 'tree-to-endpoint productive ranks')
    missing_query = deepcopy(new_word)
    del missing_query['events'][next(i for i,e in enumerate(missing_query['events']) if e[0]=='QUERY')]
    controls['missing_rank_one_query'] = rejects(lambda:inspect_caller(missing_query,new_root), 'all binary and root thin queries paid')
    missing_local = deepcopy(new_word)
    del missing_local['events'][next(i for i,e in enumerate(missing_local['events']) if e[0]=='LOCAL')]
    controls['uncancelled_native_invocation'] = rejects(lambda:inspect_caller(missing_local,new_root), 'same ordered LOCAL stage calls')
    odd_translation = deepcopy(new_word)
    odd_translation['events'][next(i for i,e in enumerate(odd_translation['events']) if e[0]=='Q_POWER')][2] = 1
    controls['unpaid_gaussian_as_translation'] = rejects(lambda:inspect_caller(odd_translation,new_root), 'ordinary Q-square translation only')
    # A same-histogram wrong suffix must also fail the endpoint identity check.
    swapped_target = deepcopy(new_word)
    swapped_target['diagonal'][4],swapped_target['diagonal'][34] = swapped_target['diagonal'][34],swapped_target['diagonal'][4]
    controls['same_invoice_wrong_field'] = rejects(lambda:inspect_caller(swapped_target,new_root), 'returned pivot has only central Q inverse')
    td = delta(before['target_per_port'],after['target_per_port'],ports)
    pd = delta(before['paid_per_port'],after['paid_per_port'],ports)
    signed = Counter({int(k):v for k,v in td.items()})
    signed.subtract({int(k):v for k,v in pd.items()})
    signed = {str(k):signed[k] for k in sorted(signed) if signed[k]}
    need(td == {'16':-104,'40':104,'41':208,'57':-208}, 'derived target delta regression')
    need(pd == {'16':-104,'40':312,'56':-208}, 'derived paid delta regression')
    out = {
        'status':'PASS_INDEPENDENT_RETIREMENT_TREE_ACCOUNTING',
        'predecessor_head':'775722aa94a5e85b05d1d704d7dca10cbf016f0c',
        'candidate_head':'11ca568cd1a16776ade02b4df09ea04a784cc674',
        'caller_sha256':{'predecessor':sha256(old_bytes).hexdigest(),'candidate':sha256(new_bytes).hexdigest()},
        'native_source_sha256':sha256(native_archive).hexdigest(),
        'ports':ports,
        'native_paid_jobs_per_invocation':native_moves,
        'native_productive_helpers_per_invocation':native_helpers,
        'complete_target_counts':[18*native_helpers + ports*sum(x['target_per_port'].values()) for x in (before,after)],
        'complete_paid_counts':[18*native_moves + ports*sum(x['paid_per_port'].values()) for x in (before,after)],
        'native_invocations_cancelled':18,
        'target_delta':td,'paid_delta':pd,'signed_delta':signed,
        'target_count_delta':sum(td.values()),'paid_count_delta':sum(pd.values()),
        'target_rank_mass_delta':sum(int(k)*v for k,v in td.items()),
        'paid_rank_mass_delta':sum(int(k)*v for k,v in pd.items()),
        'old':{k:plain(v) if isinstance(v,Counter) else v for k,v in before.items()},
        'new':{k:plain(v) if isinstance(v,Counter) else v for k,v in after.items()},
        'controls':controls,
        'scope':'Exact recursive Gaussian invoice delta conditional on the shared native call and ordinary-operation contracts; no native, compiler, price-root, precision, or all-size replay.'
    }
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--predecessor',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.predecessor,args.candidate),sort_keys=True,indent=2))


if __name__=='__main__':
    main()
