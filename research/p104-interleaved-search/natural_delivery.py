#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One natural-source P104 rank-one increment, not a complete supplier.

The original selected centre cut is omitted in both comparison programs.
The candidate constructs its query in a punctured Y role, delivers it through
one owned descending copy, and compensates all query dirt. Exact replay proves
only the stated rank-one difference on live Y; the omitted other seven terms
and restoration of the comparison baseline's punctured Y roles remain open.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import heapq
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


D = module('delivery')
S = module('scalar_surgery')
require = D.require
FULL = D.FULL
ZERO = frozenset({0})


def basis(frame):
    values, generated = [], ZERO
    for x in sorted(frame):
        if x not in generated:
            values.append(x)
            generated = D.join(generated, frozenset({0, x}))
    require(generated == frame, 'frame is not a binary subspace')
    return values


def schedule(data, word, live, labels):
    """Derive every public gate order and private contact frame from contracts."""
    v, n, bword = word['v'], 2 * word['v'] + word['R'], word['B']
    m, contacts = len(bword), data['contacts']
    frames = [D.span(f) for f in word['frames']]
    ai, bi = data['pair_hamming_root_indices']
    qa, qb = labels[ai], labels[bi]
    hb = frozenset(x for x in range(512) if not D.pairing(x, qb))
    uses = [[] for _ in range(n)]
    last, dependencies = {}, []
    for k, e in enumerate(bword):
        rr = e[1:3] if e[0] == 'add' else e[1:2]
        dependencies.append({last[r] for r in rr if r in last})
        for r in rr:
            last[r] = k
            uses[r].append(k)
    def ancestors(k):
        found, todo = {k}, [k]
        while todo:
            for j in dependencies[todo.pop()]:
                if j not in found:
                    found.add(j)
                    todo.append(j)
        return found
    # These independent dependency slices only choose deterministic tie breaks.
    hoisted, seen = [], set()
    for root in data['query_hoist_root_order']:
        role = v + word['ports'].index(labels[root])
        block = ancestors(last[role])
        hoisted.extend(sorted(block - seen))
        seen |= block
    hoisted.extend(k for k in range(m) if k not in seen)
    priority = {k: i for i, k in enumerate(hoisted)}
    current = [frames[i] for i in word['start']]
    for t in range(v):
        if t not in live:
            current[t] = ZERO
    for e in word['A']:
        for r in e[1:3] if e[0] == 'add' else e[1:2]:
            require(current[r] <= frames[e[-1]], 'nonmonotone source A')
            current[r] = frames[e[-1]]
    before = {}
    for k, e in enumerate(bword):
        for r in e[1:3] if e[0] == 'add' else e[1:2]:
            before[k, r] = current[r]
            current[r] = frames[e[-1]]
    # Undirected frame propagation is stronger than scalar response support:
    # even a source operand must share the promoted chart of its destination.
    future = [{r-v} if v <= r < 2*v and r-v in live else set() for r in range(n)]
    upper = {}
    for k in range(m-1, -1, -1):
        e = bword[k]
        rr = e[1:3] if e[0] == 'add' else e[1:2]
        reached = set().union(*(future[r] for r in rr))
        for r in rr:
            future[r] = reached.copy()
            cap = hb
            for t in sorted(reached):
                cap &= frames[word['final'][v+t]]
            upper[k, r] = cap
    succ = [set() for _ in range(m + len(contacts))]
    for k, deps in enumerate(dependencies):
        for j in deps:
            succ[j].add(k)
    lower, caps = [], []
    source_ready = last[data['query_register']]
    for i, contact in enumerate(contacts):
        k, r = contact['before_B_event'], contact['register']
        require(type(k) is int and type(r) is int and (k, r) in before, 'invalid contact anchor')
        require(Q(contact['coefficient']) != 0, 'zero contact coefficient')
        index = uses[r].index(k)
        if index:
            succ[uses[r][index-1]].add(m+i)
        succ[m+i].add(k)
        succ[source_ready].add(m+i)
        lo = D.join(before[k, r], frozenset({0, qa}))
        cap = upper[k, r]
        require(lo <= cap, 'contact has no legal common frame')
        lower.append(lo)
        caps.append(cap)
    for i in range(len(contacts)):
        for j in range(len(contacts)):
            if i != j and not lower[j] <= caps[i]:
                succ[m+j].add(m+i)
    degrees = [0] * len(succ)
    for out in succ:
        for j in out:
            degrees[j] += 1
    def key(node):
        return priority[node] if node < m else node
    queue = [(key(i), i) for i, d in enumerate(degrees) if d == 0]
    heapq.heapify(queue)
    order = []
    while queue:
        _, node = heapq.heappop(queue)
        order.append(node)
        for j in sorted(succ[node]):
            degrees[j] -= 1
            if not degrees[j]:
                heapq.heappush(queue, (key(j), j))
    require(len(order) == len(succ), 'query/contact dependency cycle')
    cframes, remaining = {}, ZERO
    for node in reversed(order):
        if node >= m:
            i = node - m
            remaining = D.join(remaining, lower[i])
            require(remaining <= caps[i], 'private chain interval failure')
            cframes[i] = remaining
    return order, cframes, hb, frozenset({0, qa}), source_ready


def construct(data=None, fault=None):
    """Return exact report and literal native transport/event witnesses."""
    data = deepcopy(data if data is not None else json.loads((HERE/'NATIVE-CHAIN.json').read_text()))
    word, prototype, live, roots, labels = D.load_sources(data)
    v, n = word['v'], 2*word['v'] + word['R']
    require((v, n) == (112, 704), 'selected dimensions')
    ai, bi = data['pair_hamming_root_indices']
    require((ai, bi, data['query_register']) == (3, 113, 146), 'this certificate binds one exact term')
    frames = [D.span(f) for f in word['frames']]
    start, terminal = [frames[i] for i in word['start']], [frames[i] for i in word['final']]
    live_y = {v+t for t in live}
    for t in range(v):
        if t not in live:
            start[t], terminal[v+t] = ZERO, FULL
    order, cframes, hb, cend, ready = schedule(data, word, live, labels)
    m = len(word['B'])
    query_baselines = {}
    query_last = {}
    probe = S.run(S.identity(n), word['precondition'], word['compensation'], word['A'])
    a_end_rows = deepcopy(probe)
    for root in data['query_hoist_root_order']:
        role = v + word['ports'].index(labels[root])
        query_last[root] = max(k for k,e in enumerate(word['B']) if role in (e[1:3] if e[0]=='add' else e[1:2]))
    for k,e in enumerate(word['B']):
        S.apply(e,probe)
        for root,last in query_last.items():
            if k == last:
                query_baselines[root] = probe[v+word['ports'].index(labels[root])].copy()
    baseline = S.run(S.identity(n), word['precondition'], word['compensation'], word['A'], word['B'], word['tail'], word['cleanup'])
    source_copy = Q(data['query_copy_coefficient'])
    if fault == 'source_coefficient':
        source_copy += 1
    raw_query = None
    response = [Q(0)]*n
    raw = S.run(S.identity(n), word['precondition'], word['compensation'], word['A'])
    for node in order:
        if node < m:
            e = word['B'][node]
            S.apply(e, raw)
            if e[0] == 'add':
                response[e[1]] += Q(e[3], e[4])*response[e[2]]
            else:
                response[e[1]] *= Q(e[2], e[3])
        else:
            if raw_query is None:
                raw_query = {j: source_copy*x for j, x in raw[data['query_register']].items()}
            c = data['contacts'][node-m]
            S.add_row(raw[c['register']], raw_query, Q(c['coefficient']))
            response[c['register']] += Q(c['coefficient'])
    expected_query = {t: Q(S.dot(roots[t], prototype['root_lines'][bi]), 8) for t in live if S.dot(roots[t], prototype['root_lines'][bi])}
    require({t:x for t,x in raw_query.items() if t in live} == expected_query, 'natural source coefficient or availability')
    dirt = {j:x for j,x in raw_query.items() if j not in live}
    require(not (set(dirt) & live_y), 'query depends on initial live Y')
    require(all(start[j] == ZERO for j in dirt), 'query dirt lacks initial zero frame')
    for phase in ('tail', 'cleanup'):
        for e in word[phase]:
            S.apply(e, raw)
            if e[0] == 'add':
                response[e[1]] += Q(e[3],e[4])*response[e[2]]
            else:
                response[e[1]] *= Q(e[2],e[3])
    require(response[data['query_register']] == 0, 'cleanup query was perturbed')
    entry = []
    for t in live:
        coefficient = Q(S.dot(roots[t], prototype['root_lines'][ai]))
        require(response[v+t] == coefficient, 'wrong final query response')
        require({j:x for j,x in baseline[v+t].items() if v <= j < 2*v} == {v+t:Q(1)}, 'nonidentity initial-Y transfer')
        for j,x in sorted(dirt.items()):
            if coefficient:
                value = -coefficient*x
                entry.append(['add',v+t,j,value.numerator,value.denominator,0])
    cleanup = []
    for r,c in enumerate(response):
        if c and r not in live_y:
            value = -c*source_copy
            cleanup.append(['add',r,data['query_register'],value.numerator,value.denominator,1])
    if fault == 'removed_cleanup':
        cleanup = cleanup[:-1]

    def replay(candidate):
        rows, current = S.identity(n), start.copy()
        paid, copy_paid, edges, events = Counter(), Counter(), [], []
        phases, copy_frame, copy_row = {}, None, None
        query_observations = {}
        copies_created = 0
        copy_active = False
        last_contact_node = next(node for node in reversed(order) if node >= m)
        def transport(register, target, phase, private=False):
            nonlocal copy_frame
            old = copy_frame if private else current[register]
            require((target <= old) if private else (old <= target), 'nonmonotone literal transport')
            rank = abs(D.dimension(target)-D.dimension(old))
            if rank:
                (copy_paid if private else paid)[rank] += 1
                edge = dict(occurrence=len(edges),register=register,phase=phase,source_frame=basis(old),target_frame=basis(target),rank=rank,private=private)
                edges.append(edge)
                events.append(dict(kind='transport', **edge))
            if private:
                copy_frame = target
            else:
                if register in live_y:
                    require(target <= terminal[register], 'live output terminal exceeded')
                current[register] = target
        def event(e, phase, promote=False):
            rr = e[1:3] if e[0] == 'add' else e[1:2]
            target = frames[e[-1]]
            if promote:
                for r in rr:
                    target = D.join(target,current[r])
            for r in rr:
                transport(r,target,phase)
            require(all(current[r] == target for r in rr), 'non-common-frame scalar gate')
            S.apply(e,rows)
            events.append(dict(kind=e[0],registers=list(rr),coefficient=str(Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])),frame=basis(target),phase=phase))
        if candidate:
            for e in entry:
                event(e,'new entry compensation')
        for phase in ('precondition','compensation','A'):
            for e in word[phase]:
                event(e,phase)
            phases[phase] = paid.copy()
        for root in range(8):
            expected = {t:Q(S.dot(roots[t],prototype['root_lines'][root]),2) for t in live if S.dot(roots[t],prototype['root_lines'][root])}
            banks = [r for r in word['centers'] if {t:x for t,x in rows[r].items() if t in live} == expected]
            require(len(banks) == 1, 'coordinate query bank mismatch')
            bank = banks[0]
            wanted_h = frozenset(x for x in range(512) if not D.pairing(x,labels[root]))
            query_observations['coordinate_'+str(root)] = dict(register=bank,at_phase='A end',frame_rank=D.dimension(current[bank]),original_query_frame_preserved=current[bank]==wanted_h,all_704_source_columns_preserved=rows[bank]==a_end_rows[bank])
        bnodes = order if candidate else list(range(m))
        for node in bnodes:
            if node < m:
                event(word['B'][node],f'B:{node}',candidate)
                for root in data['query_hoist_root_order']:
                    role = v+word['ports'].index(labels[root])
                    if node == query_last[root]:
                        wanted_h = frozenset(x for x in range(512) if not D.pairing(x,labels[root]))
                        clean = {t:rows[role].get(t,Q(0)) for t in live if rows[role].get(t,Q(0))}
                        expected = {t:-Q(S.dot(roots[t],prototype['root_lines'][root]),4) for t in live if S.dot(roots[t],prototype['root_lines'][root])}
                        query_observations[str(root)] = dict(register=role,at_original_B_event=node,frame_rank=D.dimension(current[role]),original_query_frame_preserved=current[role]==wanted_h,live_source_row_preserved=clean==expected,all_704_source_columns_preserved=rows[role]==query_baselines[root])
            else:
                i, contact = node-m, data['contacts'][node-m]
                if copy_row is None and fault != 'late_copy':
                    require(current[data['query_register']] == hb, 'query unavailable in H_b')
                    require(copies_created == 0, 'private role reused after discard')
                    copy_active = True
                    copy_row = {j:source_copy*x for j,x in rows[data['query_register']].items()}
                    copy_frame = hb
                    copies_created += 1
                    events.append(dict(kind='private_init',register=n,frame=basis(hb),phase='query copy'))
                    events.append(dict(kind='private_copy',registers=[n,data['query_register']],coefficient='1',frame=basis(hb),phase='query copy'))
                    events.append(dict(kind='scale',registers=[n],coefficient=str(source_copy),frame=basis(hb),phase='query scaling'))
                require(copy_active and copy_row is not None and copy_frame is not None, 'private read before query copy initialization')
                transport(n,cframes[i],f'contact:{i}',True)
                transport(contact['register'],cframes[i],f'contact:{i}')
                coefficient=Q(contact['coefficient'])
                S.add_row(rows[contact['register']],copy_row,coefficient)
                events.append(dict(kind='add',registers=[contact['register'],n],coefficient=str(coefficient),frame=basis(cframes[i]),phase=f'contact:{i}'))
                if node == last_contact_node:
                    transport(n,cend,'private endpoint',True)
                    events.append(dict(kind='private_discard',register=n,frame=basis(cend),phase='private endpoint'))
                    copy_active = False
        require(not copy_active, 'private role left live at B end')
        for phase in ('tail','cleanup'):
            for e in word[phase]:
                event(e,phase,candidate)
        if candidate:
            for e in cleanup:
                event(e,'new query cleanup',True)
        final = [D.join(terminal[r],current[r]) if candidate else terminal[r] for r in range(n)]
        for r in range(n):
            transport(r,final[r],'terminal')
        return dict(rows=rows,paid=paid,copy_paid=copy_paid,final=final,edges=edges,events=events,query_observations=query_observations,copies_created=copies_created)
    base = replay(False)
    new = replay(True)
    require(base['rows'] == baseline, 'baseline replay disagreement')
    for r,row in enumerate(new['rows']):
        expected = baseline[r].copy()
        if r in live_y:
            a = S.dot(roots[r-v],prototype['root_lines'][ai])
            for t,coefficient in expected_query.items():
                S.add_row(expected,{t:Q(1)},a*coefficient)
        require(row == expected, f'full-column rank-one increment mismatch at register {r}')
    require(sum(k*v for k,v in new['copy_paid'].items()) == 7, 'private COPY mass is not seven')
    old_residual, new_residual = Counter(), Counter()
    for r in range(n):
        if not (r<v and r in live) and r not in live_y:
            old_residual[9-D.dimension(base['final'][r])+D.dimension(start[r])] += 1
            new_residual[9-D.dimension(new['final'][r])+D.dimension(start[r])] += 1
    public_recount = Counter(e['rank'] for e in new['edges'] if not e['private'])
    private_recount = Counter(e['rank'] for e in new['edges'] if e['private'])
    require(public_recount == new['paid'], 'literal public transport profile mismatch')
    require(private_recount == new['copy_paid'], 'literal private transport profile mismatch')
    delta = D.difference(new['paid'],base['paid'])
    residual_delta = D.difference(new_residual,old_residual)
    report = dict(schema='natural-query-delivery-report-v1',scope='One exact rank-one difference against the centre-cut-omitted selected baseline; not a supplier or exponent improvement.',pair_hamming_root_indices=[ai,bi],public_registers=n,live_ports=len(live),original_B_events=m,contacts=len(data['contacts']),entry_compensation_additions=len(entry),query_cleanup_additions=len(cleanup),source_query_nonzero_columns=len(raw_query),source_query_dirty_columns=len(dirt),private_copies_created=new['copies_created'],peak_private_copies=1,additional_public_query_registers=0,full_704_column_increment_verified=True,baseline_profile=D.profile(base['paid']),candidate_public_profile=D.profile(new['paid']),public_profile_delta=D.profile(delta),private_COPY_profile=D.profile(new['copy_paid']),residual_width_delta=D.profile(residual_delta),public_rank_mass_delta=sum(k*v for k,v in delta.items()),residual_rank_mass_delta=sum(k*v for k,v in residual_delta.items()),other_natural_query_observations=new['query_observations'],endpoint_changes=[dict(register=r,old_frame=basis(base['final'][r]),new_frame=basis(new['final'][r])) for r in range(n) if base['final'][r]!=new['final'][r]],native_phase_compilation_verified=False,global_hosting_verified=False,complete_eight_term_supplier=False)
    return dict(report=report,ports=[word['ports'][t] for t in live],transport_edges=new['edges'],events=new['events'],entry_compensation=entry,query_cleanup=cleanup,derived_order=order,initial_frames=[basis(f)for f in start],final_frames=[basis(f)for f in new['final']])


def native_witness():
    """Literal chronological edges; private_transports is a subset of objects."""
    built = construct()
    data = json.loads((HERE/'NATIVE-CHAIN.json').read_text())
    word, _, live, _, _ = D.load_sources(data)
    edges = [dict(register=str(e['register']), old=e['source_frame'], new=e['target_frame'],
                  occurrence=e['occurrence'], private=e['private'], rank=e['rank'])
             for e in built['transport_edges']]
    return dict(transports=edges, private_transports=[e for e in edges if e['private']],
                ports=[word['ports'][t] for t in live],
                public_profile=built['report']['candidate_public_profile'],
                private_profile=built['report']['private_COPY_profile'])


def verify():
    result = construct()
    controls = {}
    for fault in ('source_coefficient','late_copy','removed_cleanup'):
        try:
            construct(fault=fault)
        except (ValueError, D.VerificationError) as error:
            controls[fault] = str(error)
        else:
            raise D.VerificationError('negative control accepted: '+fault)
    result['report']['negative_controls'] = controls
    return result['report']


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2,sort_keys=True))
