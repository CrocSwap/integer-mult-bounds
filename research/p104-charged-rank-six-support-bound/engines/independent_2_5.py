"""Independent reverse-first census for charged rank-six 2+5 helper extensions."""
from argparse import ArgumentParser
from ast import FunctionDef, Module, parse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import runpy
from signal import alarm, signal, SIGALRM

PINS = {
    'round35/verify.py': 'c906fffec26f043e159f8e314b0f245cde432cf72d2bc6a6ade6235a4c798c5a',
    'round36/predecessor_search.py': '668022953f53929fd4d95ed1b5c01ac2ba3b4bdf6be7babae511757eb21b7e6a',
    'round37/preflight/PRICE.json': 'bc6134776a077b4ae3ef595c6000563062b2a42a3684a3852ba4f2f77b8dc726',
}
HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
PARTS = ((2, 5),)


def add(row, other, factor):
    for k,x in other.items():
        y = row.get(k,0) + factor*x
        if y:
            row[k] = y
        else:
            row.pop(k,None)


def read_json(data):
    def unique(pairs):
        result = dict(pairs)
        assert len(result) == len(pairs), 'duplicate JSON key'
        return result
    return json.loads(data, object_pairs_hook=unique)


def source(roots, inventory_hash, support_hash):
    PINS["round51/INVENTORY.json"] = inventory_hash
    PINS["round51/SUPPORT.json"] = support_hash
    loaded = {}
    for name,digest in PINS.items():
        label,path = name.split('/',1)
        file = roots[label]/path
        assert sha256(file.read_bytes()).hexdigest() == digest, name
        loaded[name] = file
    audit = runpy.run_path(str(loaded['round35/verify.py']))
    tree = parse(loaded['round36/predecessor_search.py'].read_text())
    function, = [x for x in tree.body if isinstance(x,FunctionDef) and x.name == 'pure_combinations']
    env = {'add':add,'Q':Q}
    exec(compile(Module(body=[function],type_ignores=[]), 'pinned-pure-combinations', 'exec'), env)
    receipts = [read_json(path.read_bytes()) for key,path in loaded.items() if key.endswith('.json')]
    return audit,env['pure_combinations'],receipts


def write(out,name,obj):
    temp = out/(name+'.tmp')
    temp.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    temp.replace(out/name)


def geometry(word,caller,early,audit,receipt):
    frames = audit['spaces'](word['frames'])
    dims = [len(s).bit_length()-1 for s in frames]
    main = set(word['live']) | {i+112 for i in word['live']} | set(word['hosted']['X2']+word['hosted']['Y2'])
    helpers = defaultdict(set)
    for i,(a,b) in enumerate(zip(word['initial'],word['final'],strict=True)):
        if i not in main:
            helpers[a,b].add(i)
    extensions = {}
    for (a,b),roles in helpers.items():
        if dims[b]-dims[a] != 6:
            continue
        assert frames[a] < frames[b]
        for f,span in enumerate(frames):
            if dims[f] == dims[a]-1 and span < frames[a]:
                extensions['input',(a,b),(f,b)] = roles
            if dims[f] == dims[b]+1 and frames[b] < span:
                extensions['output',(a,b),(a,f)] = roles
    typed = {(*key,part):roles for key,roles in extensions.items() for part in PARTS}
    source_rows = [r for r in receipt['rows'] if r['old_rank'] == 6 and tuple(r['parts']) in PARTS]
    keys = [(r['side'],tuple(r['prior']),tuple(r['new']),tuple(r['parts'])) for r in source_rows]
    assert len(keys) == len(set(keys)) == len(typed) == 83
    declared = dict(zip(keys,source_rows,strict=True))
    assert typed.keys() == declared.keys()
    for key,roles in typed.items():
        r = declared[key]
        assert roles == set(r['extender_roles'])
        assert helpers.get(key[2],set()) == set(r['new_cohort_before_extension'])
        assert not roles & helpers.get(key[2],set())
    assert Counter(r['old_rank'] for r in receipt['rows']) == {8:24,7:90,6:166,5:432,4:15,3:50}

    @cache
    def relative(a,b):
        return dims[a]+dims[b]-2*(len(frames[a]&frames[b]).bit_length()-1)

    tape = word['program']
    remove = next(i for i,e in enumerate(tape) if e[0] == 'MOVE')
    paid = audit['literal_move_bill'](tape,word,relative)
    contacts,_ = audit['whole_contact_recount']([(i,e) for i,e in enumerate(tape) if e[0]!='MOVE'],word,relative)
    assert sum(paid.values()) == 6280 and contacts == paid
    try:
        audit['literal_move_bill'](tape[:remove]+tape[remove+1:],word,relative)
    except AssertionError:
        pass
    else:
        raise AssertionError('omitted paid MOVE accepted')
    P,T,copies = audit['full_bill'](word,caller,paid,relative)
    assert copies == receipt['copies'] == 17
    assert {str(r):v for r,v in P.items()} == early['invoice']['P']
    assert {str(r):v for r,v in T.items()} == early['invoice']['T']
    net = T.copy()
    net.subtract(P)
    k = Q(early['price']['independent_raw_bracket'][1])
    assert k == Q(receipt['crossing_upper'])
    baseline = audit['price'](net,k)
    assert baseline[1] < 0
    bounds = {}
    for parts in PARTS:
        change = Counter(parts)
        change[6] -= 1
        change[1] -= 1
        assert sum(rank*n for rank,n in change.items()) == 0
        delta = audit['price']({r:v*copies for r,v in change.items()},k)
        bounds[parts] = tuple(a+b for a,b in zip(delta,baseline,strict=True))
        assert 0 < bounds[parts][0] <= bounds[parts][1]
    for key,row in declared.items():
        lo,hi = map(Q,row['complete_margin_interval'])
        lower,upper = bounds[key[3]]
        assert lo <= lower <= upper <= hi
    interval_rank = sorted(PARTS,key=lambda part:bounds[part][0],reverse=True)
    assert all(bounds[a][0] > bounds[b][1] for a,b in zip(interval_rank,interval_rank[1:]))
    assert [r['parts'] for r in source_rows] == [
        list(part) for part in interval_rank for _ in range(len(extensions))]
    assert [tuple(x) for x in interval_rank] == [(2,5)]
    return frames,dims,helpers,typed,bounds,interval_rank


def groups_for(helpers,typed):
    grouping = defaultdict(dict)
    for key,roles in typed.items():
        grouping[key[2],key[3]][key] = roles
    universe = {g:helpers.get(g[0],set()) | set().union(*rows.values())
                for g,rows in grouping.items()}
    assert len(grouping) == 73
    return grouping,universe


def reverse_cuts(word,frames,dims,helpers,grouping,universe):
    n = word['public']
    tape = word['program']
    charts = word['final'] + [None]*word['owned_fields']
    banks = defaultdict(set)
    for r,f in enumerate(charts[:n]):
        banks[f].add(r)
    groups_by_frame = defaultdict(list)
    for g in grouping:
        (a,b),parts = g
        assert not any(word['initial'][r] == f
                       for f in range(len(frames)) if dims[f]-dims[a] in parts and frames[a]<frames[f]<frames[b]
                       for r in universe[g]), 'initial eligible chart requires a time-zero representative'
        for f,span in enumerate(frames):
            if dims[f]-dims[a] in parts and frames[a]<span<frames[b]:
                groups_by_frame[f].append(g)
    schedule, counts, typed_counts = defaultdict(list),Counter(),Counter()
    for t in reversed(range(len(tape))):
        op,r,*args = tape[t]
        touched = set(args[:2] if op == 'MOVE' else args[-1:])
        for f in touched:
            for g in groups_by_frame[f]:
                if not banks[f] & universe[g]:
                    continue
                schedule[t].append((g,f,tuple(sorted(banks[f]))))
                counts[g] += 1
                for key,roles in grouping[g].items():
                    if banks[f] & (helpers.get(g[0],set()) | roles):
                        typed_counts[key] += 1
        if op == 'MOVE':
            a,b,owned = args
            assert charts[r] == b and owned == (r>=n)
            assert frames[a]<frames[b] or (owned and frames[b]<frames[a])
            banks[b].remove(r)
            banks[a].add(r)
            charts[r] = a
        elif op == 'CLEAR':
            f = args[0]
            assert charts[r] is None and r>=n
            charts[r] = f
            banks[f].add(r)
        elif op == 'INIT':
            f = args[0]
            assert charts[r] == f and r>=n
            charts[r] = None
            banks[f].remove(r)
        else:
            assert charts[r] == args[-1]
            if op in ('ADD','COPY'):
                assert charts[args[0]] == charts[r]
    assert charts == word['initial']+[None]*word['owned_fields']
    return schedule,counts,typed_counts


def step(rows,e,reverse):
    op,d,*args = e
    if op in ('CLEAR','INIT'):
        rows[d] = {}
    elif op == 'SCALE':
        q = Q(args[-2])
        rows[d] = {k:q*v for k,v in rows[d].items()}
    elif op in ('ADD','COPY'):
        s,q = args[0],Q(args[-2])
        assert s != d
        if reverse:
            add(rows[s],rows[d],q)
            if op == 'COPY':
                rows[d] = {}
        elif op == 'ADD':
            add(rows[d],rows[s],q)
        else:
            rows[d] = {k:q*v for k,v in rows[s].items()}


def run(roots,out,inventory_hash,support_hash):
    audit,pure,(pricing,inventory,lead) = source(roots,inventory_hash,support_hash)
    word,caller,early = audit['read_inputs'](roots['round30']/'complex/source')
    assert pricing['head'] == inventory['head'] == lead['head'] == HEAD
    frames,dims,helpers,typed,bounds,ranking = geometry(word,caller,early,audit,pricing)
    grouping,universe = groups_for(helpers,typed)
    schedule,cuts,typed_counts = reverse_cuts(word,frames,dims,helpers,grouping,universe)
    assert cuts == Counter({(tuple(r['endpoints']),tuple(r['parts'])):r['cuts'] for r in inventory['counts']})
    assert typed_counts == Counter({(r['side'],tuple(r['prior']),tuple(r['new']),tuple(r['parts'])):r['cuts'] for r in inventory['typed']})
    assert sum(cuts.values()) == inventory['cuts']
    result = {'head':HEAD,'typed_signatures':len(typed),'union_groups':len(grouping),
              'rank_six_3_plus_4_predecessor':83,'smaller_outside_scope':497,'cut_incidences':sum(cuts.values()),
              'part_price_order':[list(p) for p in ranking],
              'whole_margins':{'+'.join(map(str,p)):list(map(str,v)) for p,v in bounds.items()},
              'literal_paid_move_omission_rejected':True,'pins':PINS}
    write(out,'CUTS.json',result)
    n,tape = word['public'],word['program']
    def identity():
        return [{i:Q(1)} for i in range(n)]+[{} for _ in range(word['owned_fields'])]
    suffix, stored, seen = identity(),{},0
    for t in reversed(range(len(tape))):
        for group,f,roles in schedule.get(t,()):
            right = pure(suffix,roles,universe[group])
            seen += 1
            if right:
                stored[t,group,f] = tuple(d for d,_ in right)
        step(suffix,tape[t],True)
    prefix,positive,checked,comparisons = identity(),Counter(),0,0
    for t,e in enumerate(tape):
        step(prefix,e,False)
        for group,f,roles in schedule.get(t,()):
            left = pure(prefix,roles,universe[group])
            checked += 1
            if left:
                positive[group] += 1
            for c,_ in left:
                for d in stored.get((t,group,f),()):
                    comparisons += 1
                    assert not sum(x*d.get(i,0) for i,x in c.items()),(t,f,group)
    assert all(prefix[i] == {i:Q(1)} for u in universe.values() for i in u)
    assert seen == checked == inventory['cuts']
    assert positive == Counter({(tuple(r['endpoints']),tuple(r['parts'])):r.get('prefix_nonzero',0) for r in lead['by_parts']})
    assert lead['phase']=='exhausted'
    assert not lead['candidate'] and not lead['unresolved']
    result.update(status='PASS_INDEPENDENT_REVERSE_FIRST_RANK6_2_PLUS_5',positive_prefix_images=sum(positive.values()),
                  suffix_nonzero_cuts=len(stored),basis_pairings_tested=comparisons,positive_pairings=0)
    write(out,'RESULT.json',result)


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    for name in ('round30','round35','round36','round37','round51','out'):
        p.add_argument(name,type=Path)
    p.add_argument("--inventory-sha",required=True)
    p.add_argument("--support-sha",required=True)
    a = p.parse_args()
    a.out.mkdir()
    def timeout(*_):
        raise TimeoutError('independent replay watchdog')
    signal(SIGALRM,timeout)
    alarm(43)
    run({k:getattr(a,k) for k in ('round30','round35','round36','round37','round51')},a.out,a.inventory_sha,a.support_sha)
    alarm(0)
