"""Bind the mixed root to native phases and every whole Gaussian job.

Adapted from Ali Romman's PR5544 physical checker. The Clifford recipes,
phase interpreter and local interface retain their predecessor credit.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json


def physical(word, local, L):
    need = L.need
    N = L.load(L.ROOT/'research/pr4359-p7-padding/native_inventory.py', 'productive_p104_phase_polynomial')
    source = L.read(L.ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json')
    recipes = {r['q']:r for r in source['recipes']}
    dimension = word['ambient_rank']
    axes = tuple(1 << i for i in range(dimension))
    def completed(stage):
        return N.norm((axis,1) for axis in axes[:9+8*stage])
    contacts, squares, target_profile = [], 0, Counter()
    idle_jobs = Counter()
    for _,stage,x,y in (e for e in word['events'] if e[0] == 'LOCAL'):
        spectator = N.norm((axis,1) for axis in axes[9:9+8*stage])
        for q in local['ports']:
            basis = recipes[q]['idle_children'][0]['orthogonal_axes'][:8]
            need(all((x&q).bit_count()%2 == 0 for x in basis), 'Fresh-block basis fixes central port')
            need(all((a&b).bit_count()%2 == int(i==j) for i,a in enumerate(basis) for j,b in enumerate(basis)), 'Actual orthonormal basis')
            swaps = [] if stage == 0 else [b ^ axes[9+8*(stage-1)+i] for i,b in enumerate(basis)]
            route = tuple(e ^ N.act(swaps,sum(((e&v).bit_count()%2) << i for i,v in enumerate(swaps))) for e in axes)
            need(all(N.act(route,route[i]) == axes[i] for i in range(dimension)), 'Route inverse')
            need(all((a&b).bit_count()%2 == int(i==j) for i,a in enumerate(route) for j,b in enumerate(route)), 'Orthogonal physical route')
            need(N.act(route,q) == q, 'Route preserves Q')
            raw_x = N.norm([(q,1)]) if stage == 0 else completed(stage-1)
            raw_y = () if stage == 0 else N.norm(list(raw_x)+[(q,-1)])
            entry_x, entry_y = N.norm(list(spectator)+[(q,1)]), spectator
            out0 = N.norm(list(spectator)+[(axis,1) for axis in axes[:9]])
            exit_x, exit_y = out0, N.norm(list(out0)+[(q,-1)])
            out_x, out_y = completed(stage), N.norm(list(completed(stage))+[(q,-1)])
            maps = [N.contact(a,b,route,dimension) for a,b in [(raw_x,entry_x),(raw_y,entry_y),(exit_x,out_x),(exit_y,out_y)]]
            delta = N.norm([(axis,1) for axis in axes[:9]]+[(q,-1)]) if stage == 0 else N.norm((axis,1) for axis in axes[9+8*(stage-1):9+8*stage])
            for incoming,outgoing in [(raw_x,out_x),(raw_y,out_y)]:
                need(N.polynomial(N.norm(list(outgoing)+[(a,-c) for a,c in incoming]),dimension) == N.polynomial(delta,dimension), 'Actual diagonal D_s')
            cross = N.norm(list(out_y)+[(a,-c) for a,c in raw_x])
            need(N.polynomial(cross,dimension) == N.polynomial(N.norm(list(delta)+[(q,-1)]),dimension), 'Actual cross term D_s Q^-1')
            need(sum(route[i] != axes[i] for i in range(dimension)) <= 17 and all(m['translation'].bit_count() <= 17 and m['inverse_translation'].bit_count() <= 17 for m in maps), 'Fixed seventeen-axis route allowance')
            contacts.append([stage,q,maps])
    for q in local['ports']:
        # Multiply the Gaussian pair twice with exact real and imaginary parts.
        a,b = (Q(1,2),Q(1,2)), (Q(1,2),Q(-1,2))
        mul = lambda z,w: (z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0])
        plus = lambda z,w: (z[0]+w[0],z[1]+w[1])
        diagonal,off = plus(mul(a,a),mul(b,b)), plus(mul(a,b),mul(b,a))
        need(diagonal == (0,0) and off == (1,0), 'Q^2 is translation with phase +1')
        for address in range(512):
            need({address:diagonal,address^q:off}[address^q] == (1,0), 'Every central square column')
            squares += 1
        for term in word['diagonal']:
            qp,selected = term[0],term[1:]
            physical = N.norm([(q,qp)]+[(axis,1) for s,yes in enumerate(selected) if yes for axis in (axes[:9] if s == 0 else axes[9+8*(s-1):9+8*s])]+[(q,-1)]*selected[0])
            need(qp in (-1, 0, 1) and not (qp == 0 and selected[0]), 'Declared central phase and fresh-stage target')
            positive = list(axes[:9]) if selected[0] else ([q] if qp else [])
            positive += [axis for s in range(1,len(selected)) if selected[s] for axis in axes[9+8*(s-1):9+8*s]]
            need(N.polynomial(physical,dimension) == N.polynomial(N.norm([(x,1) for x in positive]+[(q,2)]*(qp == -1)),dimension), 'Full main output phase and rank')
            target_profile[len(positive)] += 1
    for e in word['events']:
        if e[0] not in ('IDLE', 'IDLE_ONE'):
            continue
        stages = e[3] if e[0] == 'IDLE' else e[2]
        need(len(stages) == len(set(stages)), 'Whole idle has no repeated stage')
        for q in local['ports']:
            positive, physical = [], []
            for stage in stages:
                if stage == 0:
                    positive += recipes[q]['idle_children'][0]['orthogonal_axes'][:8]
                    physical += [(x,1) for x in axes[:9]]+[(q,-1)]
                else:
                    block = axes[9+8*(stage-1):9+8*stage]
                    positive += block
                    physical += [(x,1) for x in block]
            need(len(positive) == 8*len(stages), 'All idle Gaussian axes')
            need(all((a&b).bit_count()%2 == int(i==j) for i,a in enumerate(positive) for j,b in enumerate(positive)), 'Independent orthonormal idle axes')
            N.contact(N.norm(physical),N.norm((x,1) for x in positive),axes,dimension)
            idle_jobs[len(positive)] += 2 if e[0] == 'IDLE' else 1
    return {'ports':104,'full_calls':len(contacts)//104,'physical_contacts':4*len(contacts),'central_square_columns':squares,
            'main_targets':dict(target_profile),'whole_idle_jobs':dict(idle_jobs),'route_payload_sha256':sha256(json.dumps(contacts,separators=(',',':')).encode()).hexdigest(),
            'central_translations':sum(e[0] == 'Q_POWER' for e in word['events']),
            'ordinary_normalizations':sum(e[0] == 'LAMBDA' for e in word['events']),'new_paid_jobs':0,'tensor_rule':'Factorwise native maps; scalar signs stay outside the tensor power.'}
