# SPDX-License-Identifier: Apache-2.0
"""Independent source-event / grouped-flow / literal binding audit (stdlib only).

No optimizer, source owner engine, solver.py or verify.py is imported/executed.
Chronology and coloring method credited to the PR2979/PR2857/PR2751 lineage;
this implementation and the accompanying sufficiency derivation were prepared
with OpenAI GPT-6.1 Sol assistance. Native/outer admission is outside its scope.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'sources'
WIDTHS = (4, 5, 6, 7, 8, 9)
INVENTORY = Counter({4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213})
PINS = {
    'allocation/ORDER.json': '519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1',
    'allocation/DISPATCH.json': '65e435bd68e97243c003677271b88485a29d4d0fae2dff1354100404a145e74c',
    'allocation/PROVIDERS.json': 'f2edb7922f3029a5d607437e737775ff3371bca49ebab62e5e2495d16d3bf573',
    'allocation/FILL.json.gz': 'c2136be9434cda511a1a8a44d98f9f72ea5376830a8426674253b4ee351c4c39',
    'allocation/vendor/PLAN.json.gz': 'd566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e',
    'allocation/vendor/TEMPLATE.json.gz': '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def target(k):
    need(type(k) is int and 0 <= k <= 1063, 'family parameter')
    entries = [
        (8, (8,), 24864), (16, (7, 9), 16253-k),
        (16, (8, 8), 323+k), (32, (7, 8, 8, 9), 1063-k),
        (32, (7, 7, 9, 9), k), (32, (9, 9, 9), 864),
        (32, (6, 8, 9, 9), 5328), (32, (5, 9, 9, 9), 666),
        (32, (4, 9, 9, 9), 8655), (48, (), 14095),
        (48, (9, 9, 9, 9, 9), 2478),
        (48, (4, 8, 9, 9, 9, 9), 3),
    ]
    return Counter({(cap, tuple(ws.count(w) for w in WIDTHS)): n
                    for cap, ws, n in entries if n})


def family_invariants(order, windows, identities, active):
    """Check the two premises which a width/window-only flow otherwise loses."""
    byfamily = defaultdict(list)
    for (owner, child), (cap, lo, hi) in windows.items():
        pair, side = identities[child]
        times = set(range(max(0, lo+1), min(len(order), hi+1)))
        for t in times:
            s, r = order[t]
            need(r != owner or active[s] != pair, 'active data family in window')
        for oldtimes in byfamily[owner, pair, side]:
            need(times.isdisjoint(oldtimes), 'overlapping same-family child windows')
        byfamily[owner, pair, side].append(times)
    return len(byfamily)


def chronology():
    for rel, digest in PINS.items():
        need(sha(SRC / rel) == digest, 'source pin '+rel)
    source_order = read(SRC / 'allocation/ORDER.json')
    source_dispatch = read(SRC / 'allocation/DISPATCH.json')
    need(len(source_order) == 666, 'source T74 order length')
    order = []
    for t in range(333):
        s, r = source_order[2*t]
        need(0 <= r < 37 and source_order[2*t+1] == [s, r+37], 'source copy interleaving')
        order.append([s, r])
    need(set(map(tuple, order)) == {(s, r) for s in range(9) for r in range(37)},
         'complete source call set')
    times = {tuple(call): t for t, call in enumerate(order)}
    for r in range(37):
        need([s for s, rr in order if r == rr] == list(range(9)), 'replica source order')
    dispatch74 = {(s, r): p for s, r, p in source_dispatch}
    need(len(dispatch74) == len(source_dispatch) == 666, 'source dispatch uniqueness')
    dispatch = {}
    for s, r in order:
        need(dispatch74[s, r] == dispatch74[s, r+37], 'source copy provider binding')
        dispatch[s, r] = dispatch74[s, r]
    providers = read(SRC / 'allocation/PROVIDERS.json')
    for p in providers.values():
        need(len(p['widths']) == 408 and Counter(p['widths']) == INVENTORY,
             'ordered provider inventory')
    need(set(dispatch.values()) <= set(providers), 'provider dispatch coverage')
    plan = read(SRC / 'allocation/vendor/PLAN.json.gz')
    template = read(SRC / 'allocation/vendor/TEMPLATE.json.gz')
    need(plan['order'] == order, 'PLAN order binding')
    active = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    need(set(active) == set(range(9)), 'source local stage set')
    ranks = {}
    for e in template['idle_children']:
        c = e['child']
        ranks.setdefault(c, e['rank'])
        need(ranks[c] == e['rank'] and 0 <= e['port'] < 112, 'source child rank binding')
    need(Counter(e['child'] for e in template['idle_children']) == Counter({c:112 for c in ranks}),
         'source child port coverage')
    # Build each replica's event line first; for every pending sweep, search
    # backward for its nearest preceding touch, instead of invoking last-touch
    # logic from the retained owner engine.
    events = []
    stage = None
    for e in template['execution_schedule']:
        kind = e['kind']
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if kind == 'local_cover_sweep':
            stage = e['stage']
        need(stage is not None, 'unbound source event')
        events.append((stage, e))
    windows, identities = {}, {}
    for j, (stage, e) in enumerate(events):
        if e['kind'] != 'idle_cover_sweep':
            continue
        pair = e['pair']
        previous = None
        for oldstage, old in reversed(events[:j]):
            touched = ((old['kind'] == 'local_cover_sweep' and active[oldstage] == pair)
                       or (old['kind'] == 'bridge' and pair in (old['src'], old['dst'])))
            if touched:
                previous = oldstage
                break
        for side, c in enumerate(e['child_indices']):
            if c not in ranks:
                continue
            need(c not in identities and side in (0, 1), 'child identity uniqueness')
            identities[c] = pair, side
            need((plan['pairs'][str(c)], plan['sides'][str(c)]) == (pair, side),
                 'PLAN physical family binding')
            for r in range(37):
                lo = -1 if previous is None else times[previous, r]
                hi = times[stage, r]
                windows[r, c] = ranks[c], lo, hi
    need(len(windows) == 666 and set(identities) == set(ranks), 'complete reconstructed windows')
    reconstructed = {f'{r},{c}': [cap, list(range(lo+1, hi+1))]
                     for (r,c), (cap,lo,hi) in windows.items()}
    need(plan['windows'] == reconstructed, 'PLAN exact window binding')
    families = family_invariants(order, windows, identities, active)
    groups = defaultdict(list)
    for (r,c), (cap,lo,hi) in windows.items():
        for port in range(112):
            groups[cap, tuple(range(lo+1, hi+1))].append((r,c,port))
    keys = sorted(groups)
    return order, dispatch, providers, windows, identities, active, groups, keys, families


def check_flow(path, groups, keys):
    f = read(path)
    x, z = {}, {}
    for gi, rawq, n in f['x']:
        q = tuple(rawq)
        need(type(gi) is int and 0 <= gi < len(keys) and type(n) is int and n > 0,
             'integer positive pattern variable')
        need(len(q) == 6 and all(type(v) is int and v >= 0 for v in q), 'integer pattern shape')
        cap, ts = keys[gi]
        need((cap, q) in target(473), 'fixed pattern support')
        need((gi,q) not in x, 'duplicate pattern variable')
        x[gi,q] = n
    for gi, rawq, t, w, n in f['z']:
        q = tuple(rawq)
        need(all(type(v) is int for v in (gi,t,w,n)) and n > 0, 'integer positive flow variable')
        need((gi,q) in x and t in keys[gi][1] and w in WIDTHS and q[WIDTHS.index(w)] > 0,
             'flow window pattern eligibility')
        need((gi,q,t,w) not in z, 'duplicate flow variable')
        z[gi,q,t,w] = n
    bygroup, totalpattern = Counter(), Counter()
    for (gi,q), n in x.items():
        bygroup[gi] += n
        totalpattern[keys[gi][0],q] += n
    need(bygroup == Counter({gi:len(groups[key]) for gi,key in enumerate(keys)}), 'all group bins')
    need(totalpattern == target(473), 'exact boundary target mix')
    bywidth, bycall, demand = Counter(), Counter(), Counter()
    for (gi,q,t,w), n in z.items():
        bywidth[gi,q,w] += n
        bycall[gi,q,t] += n
        demand[t,w] += n
    for (gi,q), n in x.items():
        need(all(bywidth[gi,q,w] == n*q[j] for j,w in enumerate(WIDTHS)), 'pattern width degree')
    need(all(n <= x[gi,q] for (gi,q,t),n in bycall.items()), 'call-distinct degree bound')
    need(demand == Counter({(t,w):n for t in range(333) for w,n in INVENTORY.items()}),
         'complete call width demand')
    # At k473 the predecessor's cut is attained. Check its forced routing,
    # rather than silently treating the solver's extra zero bounds as choices.
    for (gi,q), n in x.items():
        cap, ts = keys[gi]
        need(cap != 16 or not any(t >= 45 for t in ts) or q[3] == 1,
             'boundary saturated intersecting cap16 bins')
    for (gi,q,t,w), n in z.items():
        cap, ts = keys[gi]
        need(w != 7 or t >= 45 or (cap == 16 and not any(u >= 45 for u in ts)),
             'boundary saturated width7 routing')
    return x, z


def check_literal(directory, source, flow):
    order, dispatch, providers, windows, identities, active, groups, keys, _ = source
    need(read(directory/'ORDER.json') == order, 'literal ORDER source binding')
    raw_dispatch = read(directory/'DISPATCH.json')
    need(len(raw_dispatch) == 333 and len({(s,r) for s,r,p in raw_dispatch}) == 333,
         'literal dispatch uniqueness')
    need({(s,r):p for s,r,p in raw_dispatch} == dispatch, 'literal dispatch source binding')
    if (directory/'PROVIDERS.json').exists():
        need(read(directory/'PROVIDERS.json') == providers, 'literal ordered widths binding')
    fill = read(directory/'FILL.json.gz')
    need(fill['columns'] == ['time','helper','owner_replica','child','port','offset'], 'literal columns')
    need(len(fill['rows']) == 135864, 'literal complete role count')
    role_seen, family_seen, contents = set(), set(), defaultdict(list)
    for row in fill['rows']:
        need(len(row) == 6 and all(type(v) is int for v in row), 'literal integer row')
        t,h,r,c,p,offset = row
        need(0 <= t < 333 and 0 <= h < 408 and 0 <= p < 112 and (r,c) in windows,
             'literal role bounds')
        cap,lo,hi = windows[r,c]
        need(lo < t <= hi, 'literal open closed source window')
        need((t,h) not in role_seen, 'literal duplicate helper')
        role_seen.add((t,h))
        pair,side = identities[c]
        fam = t,r,pair,side,p
        need(fam not in family_seen, 'literal same-call physical family')
        family_seen.add(fam)
        s,rr = order[t]
        need(r != rr or active[s] != pair, 'literal active data family')
        w = providers[dispatch[s,rr]]['widths'][h]
        need(0 <= offset and offset+w <= cap, 'literal capacity')
        contents[r,c,p].append((offset,w,t))
    need(len(role_seen) == 333*408, 'literal helper coverage')
    gx, gz, idle = Counter(), Counter(), Counter()
    for gi,key in enumerate(keys):
        cap,ts = key
        for b in groups[key]:
            roles = sorted(contents[b])
            used = 0
            for offset,w,t in roles:
                need(offset == used, 'literal compact disjoint prefix')
                used += w
            q = tuple(sum(w == ww for _,w,_ in roles) for ww in WIDTHS)
            gx[gi,q] += 1
            for _,w,t in roles:
                gz[gi,q,t,w] += 1
            if used < cap:
                idle[cap-used] += 1
    need(gx == Counter(flow[0]) and gz == Counter(flow[1]), 'literal realizes exact grouped flow')
    return {'roles':len(role_seen), 'idle':dict(sorted(idle.items())),
            'literal_sha256':{name:sha(directory/name) for name in
                              ('ORDER.json','DISPATCH.json','FILL.json.gz')}}


def check_direct_repairs(directory, source):
    """Reconstruct every legal frozen C+D -> B+A edge, then check its certificate."""
    order, dispatch, providers, windows, identities, active, groups, keys, _ = source
    original = read(SRC/'allocation/FILL.json.gz')
    projected = []
    for row in original['rows']:
        t,h,r,c,p,offset = row
        if t % 2 == 0:
            need(0 <= r < 37, 'source even-call owner projection')
            projected.append([t//2,h,r,c,p,offset])
    need(len(projected) == 135864, 'projected source complete role count')
    seen, families, bins, widths = set(), set(), defaultdict(list), []
    for i, (t,h,r,c,p,offset) in enumerate(projected):
        need(0 <= t < 333 and 0 <= h < 408 and 0 <= p < 112 and (r,c) in windows,
             'projected source bounds')
        need((t,h) not in seen, 'projected source duplicate role')
        seen.add((t,h))
        cap,lo,hi = windows[r,c]
        need(lo < t <= hi, 'projected source window')
        pair,side = identities[c]
        fam = t,r,pair,side,p
        need(fam not in families, 'projected source physical family')
        families.add(fam)
        w = providers[dispatch[tuple(order[t])]]['widths'][h]
        widths.append(w)
        need(0 <= offset and offset+w <= cap, 'projected source capacity')
        bins[r,c,p].append(i)
    need(len(seen) == 135864, 'projected source all helper identities')
    for b, rows in bins.items():
        endpoint = 0
        for i in sorted(rows, key=lambda i:projected[i][5]):
            need(projected[i][5] == endpoint, 'projected source compact prefix')
            endpoint += widths[i]
    baseline_patterns = Counter()
    for (r,c), (cap,lo,hi) in windows.items():
        for p in range(112):
            q = tuple(sum(widths[i] == w for i in bins[r,c,p]) for w in WIDTHS)
            baseline_patterns[cap,q] += 1
    need(baseline_patterns == target(1063), 'projected source full pattern inventory')
    left, right = [], []
    for b in sorted(bins):
        rows = bins[b]
        cap,lo,hi = windows[b[:2]]
        pattern = sorted(widths[i] for i in rows)
        item = [list(b), rows, lo, hi]
        if cap == 16 and pattern == [8,8]:
            left.append(item)
        if cap == 32 and pattern == [7,7,9,9]:
            right.append(item)
    need(len(left) == 1386 and len(right) == 1063, 'source direct-repair vertices')
    # Enumeration is independent of the producer: retain all legal exchanged
    # role pairs, rather than the producer's first passing pair alone.
    choices = {}
    for ci, (_,crows,clo,chi) in enumerate(left):
        ctimes = [projected[i][0] for i in crows]
        for di, (_,drows,dlo,dhi) in enumerate(right):
            if not all(dlo < t <= dhi for t in ctimes):
                continue
            legal = set()
            for a in drows:
                if widths[a] != 7 or not clo < projected[a][0] <= chi:
                    continue
                for b in drows:
                    if widths[b] != 9 or not clo < projected[b][0] <= chi:
                        continue
                    cnew = [projected[a][0], projected[b][0]]
                    dnew = ctimes + [projected[i][0] for i in drows if i not in (a,b)]
                    if len(set(cnew)) == 2 and len(set(dnew)) == 4:
                        legal.add((a,b))
            if legal:
                choices[ci,di] = legal
    graphpath = directory/'PAIR-GRAPH.json.gz'
    graph, cert = read(graphpath), read(directory/'MATCHING-CERT.json')
    need(graph['left'] == left and graph['right'] == right, 'direct graph exact vertex binding')
    for vertices in (graph['left'], graph['right']):
        need(all(len(key) == 3 and all(type(v) is int for v in key+rows+[lo,hi])
                 for key,rows,lo,hi in vertices), 'direct graph integer vertices')

    def graph_document(g):
        stored = {}
        for ci,di,a,b in g['edges']:
            need(all(type(v) is int for v in (ci,di,a,b)), 'direct graph integer edge')
            need((ci,di) not in stored, 'direct graph duplicate edge')
            need((ci,di) in choices and (a,b) in choices[ci,di], 'direct graph legal edge witness')
            stored[ci,di] = a,b
        need(set(stored) == set(choices), 'direct graph complete edge set')
        return set(stored)

    edges = graph_document(graph)

    def certificate(c):
        need(all(len(e) == 2 and all(type(v) is int for v in e) for e in c['matching']),
             'direct graph integer matching')
        matching = [tuple(e) for e in c['matching']]
        need(len(set(a for a,b in matching)) == len(matching)
             and len(set(b for a,b in matching)) == len(matching)
             and all(e in edges for e in matching), 'direct graph matching')
        lc,rc = set(c['cover_left']),set(c['cover_right'])
        need(len(lc) == len(c['cover_left']) and len(rc) == len(c['cover_right'])
             and all(type(a) is int and 0 <= a < len(left) for a in lc)
             and all(type(b) is int and 0 <= b < len(right) for b in rc), 'direct graph cover vertices')
        need(all(a in lc or b in rc for a,b in edges), 'direct graph vertex cover')
        need(len(matching) == len(lc)+len(rc) == c['matching_cardinality']
             == c['cover_cardinality'], 'direct graph matching cover equality')
        return len(matching)

    need(cert['graph_sha256'] == sha(graphpath), 'direct graph certificate hash')
    optimum = certificate(cert)
    need(optimum == 123 and len(edges) == 26959, 'direct graph certified counts')
    rejected = []
    def reject(name, fn, reason):
        try:
            fn()
        except ValueError as error:
            need(str(error) == reason, 'wrong direct control failure '+name+': '+str(error))
            rejected.append(name)
        else:
            raise ValueError('accepted direct control '+name)
    reject('missing_eligible_direct_edge',
           lambda:graph_document({**graph, 'edges':graph['edges'][1:]}),
           'direct graph complete edge set')
    badedge = list(graph['edges'][0])
    badedge[2] = left[badedge[0]][1][0]
    reject('edge_witness_moves_width8_as_width7',
           lambda:graph_document({**graph, 'edges':[badedge]+graph['edges'][1:]}),
           'direct graph legal edge witness')
    reject('incomplete_vertex_cover',
           lambda:certificate({**cert, 'cover_left':cert['cover_left'][1:]}),
           'direct graph vertex cover')
    result = dict(status='PASS_INDEPENDENT_COMPLETE_DIRECT_REPAIR_GRAPH',
                left=len(left),right=len(right),edges=len(edges),maximum_matching=optimum,
                swaps_needed_for_k473=590,controls=list(rejected),
                constructed_family_interval=[940,1063],
                family_proof_level='Written finite-family subset composition from the certified disjoint matching; not 124 literal replays',
                graph_sha256=sha(graphpath),certificate_sha256=sha(directory/'MATCHING-CERT.json'),
                scope='Only disjoint direct inverse swaps on the projected frozen source fill; no general k473 infeasibility')
    attained = directory/'attained'
    if (attained/'FILL.json.gz').exists():
        need(read(attained/'ORDER.json') == order, 'attained source ORDER')
        rawdispatch = read(attained/'DISPATCH.json')
        need(len(rawdispatch) == 333 and {(s,r):p for s,r,p in rawdispatch} == dispatch,
             'attained source dispatch')
        need(read(attained/'PROVIDERS.json') == providers, 'attained ordered provider widths')
        row_targets = {i:tuple(row[2:5]) for i,row in enumerate(projected)}
        edge_witness = {(ci,di):(a,b) for ci,di,a,b in graph['edges']}
        expected_journal = []
        for ci,di in cert['matching']:
            cbin,crows,_,_ = left[ci]
            dbin,_,_,_ = right[di]
            a,b = edge_witness[ci,di]
            moves = []
            for i,newbin in [(i,dbin) for i in crows]+[(a,cbin),(b,cbin)]:
                row_targets[i] = tuple(newbin)
                moves.append(dict(source_row=i,before=projected[i],after_owner=newbin,width=widths[i]))
            expected_journal.append(dict(C=cbin,D=dbin,moves=moves))
        def journal_document(journal):
            need(journal == expected_journal
                 and json.dumps(journal,sort_keys=True) == json.dumps(expected_journal,sort_keys=True),
                 'attained exact matching journal')
        journal_document(read(attained/'JOURNAL.json.gz'))
        assigned = defaultdict(list)
        for i,b in row_targets.items():
            assigned[b].append(i)
        expected_rows, attained_patterns, idle = [], Counter(), Counter()
        for (r,c),(cap,lo,hi) in windows.items():
            for p in range(112):
                b = r,c,p
                roles = sorted(assigned[b],key=lambda i:tuple(projected[i][:2]))
                used = 0
                times_in_bin = set()
                for i in roles:
                    t,h = projected[i][:2]
                    need(lo < t <= hi and t not in times_in_bin, 'attained literal window and distinct times')
                    times_in_bin.add(t)
                    expected_rows.append([t,h,r,c,p,used])
                    used += widths[i]
                need(used <= cap, 'attained literal bin capacity')
                q = tuple(sum(widths[i] == w for i in roles) for w in WIDTHS)
                attained_patterns[cap,q] += 1
                if used < cap:
                    idle[cap-used] += 1
        actual = read(attained/'FILL.json.gz')
        sorted_expected = sorted(expected_rows)
        def literal_document(document):
            need(document['columns'] == ['time','helper','owner_replica','child','port','offset']
                 and all(len(row) == 6 and all(type(v) is int for v in row) for row in document['rows'])
                 and document['rows'] == sorted_expected, 'attained exact literal from matching')
        literal_document(actual)
        need(attained_patterns == target(940), 'attained full k940 pattern inventory')
        paid = Counter(idle)
        for call in order:
            paid.update({int(r):n for r,n in providers[dispatch[tuple(call)]]['actual_paid_profile'].items()})
        need(paid == Counter({int(r):n for r,n in read(attained/'PROFILE.json').items()}),
             'attained complete conditional profile')
        before_controls = len(rejected)
        badjournal = list(expected_journal)
        badjournal[0] = {**badjournal[0], 'moves':list(badjournal[0]['moves'])}
        firstmove = badjournal[0]['moves'][0]
        badjournal[0]['moves'][0] = {**firstmove, 'after_owner':firstmove['before'][2:5]}
        reject('journal_fails_to_move_role', lambda:journal_document(badjournal),
               'attained exact matching journal')
        badrows = list(actual['rows'])
        badrows[0] = list(badrows[0])
        badrows[0][5] += 1
        reject('literal_offset_not_the_reconstructed_prefix',
               lambda:literal_document({**actual,'rows':badrows}),
               'attained exact literal from matching')
        result['attained'] = dict(status='PASS_EXACT_123_SWAP_LITERAL_JOURNAL',k=940,
                                  roles=len(expected_rows),moves=4*optimum,
                                  controls=rejected[before_controls:],
                                  profile=dict(sorted(paid.items())),
                                  fill_sha256=sha(attained/'FILL.json.gz'),
                                  journal_sha256=sha(attained/'JOURNAL.json.gz'),
                                  scope='T37 literal geometry and conditional child profile; stock/native/outer premises inherited')
    return result


def controls(source):
    order, _, _, windows, identities, active, _, _, _ = source
    rejected = []
    def reject(name, fn, reason):
        try:
            fn()
        except ValueError as error:
            need(str(error) == reason, 'wrong control failure '+name+': '+str(error))
            rejected.append(name)
        else:
            raise ValueError('accepted control '+name)
    r,c = next(iter(windows))
    cap,lo,hi = windows[r,c]
    # Two bins of one physical family may have disjoint coordinates but
    # overlapping call sets; those require a stronger flow than this model.
    reject('overlapping_same_family_windows',
           lambda:family_invariants([[0,1],[0,1]], {(0,0):(8,-1,1),(0,1):(8,0,1)},
                                    {0:(1,0),1:(1,0)}, {0:0}),
           'overlapping same-family child windows')
    reject('active_pair_window',
           lambda:family_invariants([[0,0]], {(0,0):(8,-1,0)}, {0:(0,0)}, {0:0}),
           'active data family in window')
    return rejected


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, default=HERE/'candidate')
    ap.add_argument('--require-literal', action='store_true')
    ap.add_argument('--out', type=Path)
    ap.add_argument('--check-result', type=Path)
    args = ap.parse_args()
    source = chronology()
    order, dispatch, providers, windows, identities, active, groups, keys, families = source
    result = dict(status='PASS_SOURCE_SUFFICIENCY_PREMISES', replicas=37, calls=333,
                  child_windows=len(windows), groups=len(keys), bins=sum(map(len,groups.values())),
                  replica_pair_side_families=families, controls=controls(source),
                  source_head='be191346391661f4d35fc0d1508d0a6029572576',
                  predecessor_head='02c3047a1e78e6e35e7573c12434ba26f6f9bd96',
                  proof_level='Exact finite source geometry; written all-parameter flow lemma in INDEPENDENT.md; no formal kernel proof')
    flowpath = args.candidate/'FLOW.json.gz'
    repairpath = args.candidate/'repair'
    if (repairpath/'PAIR-GRAPH.json.gz').exists():
        result['direct_repair'] = check_direct_repairs(repairpath, source)
        result['status'] = 'PASS_INDEPENDENT_SOURCE_DIRECT_REPAIR_AUDIT'
    if flowpath.exists():
        flow = check_flow(flowpath, groups, keys)
        result.update(status='PASS_EXACT_GROUPED_FLOW_SUFFICIENCY',
                      flow_sha256=sha(flowpath), positive_x=len(flow[0]), positive_z=len(flow[1]))
        if (args.candidate/'FILL.json.gz').exists():
            result.update(check_literal(args.candidate, source, flow))
            result['status'] = 'PASS_INDEPENDENT_SOURCE_FLOW_LITERAL_BINDING'
        else:
            need(not args.require_literal, 'required literal candidate missing')
    else:
        need(not args.require_literal, 'required exact flow missing')
    if args.check_result is not None:
        need(read(args.check_result) == json.loads(json.dumps(result)), 'independent result binding')
    output = json.dumps(result, sort_keys=True)
    if args.out is not None:
        need(not args.out.exists(), 'fresh independent output')
        args.out.write_text(output+'\n')
    print(output)


if __name__ == '__main__':
    main()
