"""An all-forward caller for the credited P104 supplier.

The Laurent controller is by Cinna Davis. Its replay and signed-swap
identity follow Ali Romman's PR5398. This inverse wrapper and source binding
are by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import json
import local as L
need = L.need

def replay(word):
    """Check the literal p16 word and both rational boundary programs."""
    need((word['kind'], word['pairs'], word['prefix_pairs'], word['ambient_rank']) == ('complex', 16, 7, 145), 'Source p16/a7 controller')
    zero = (0,) * 34
    def plus(dst, src, q):
        for k, v in src.items():
            value = dst.get(k, Q(0)) + q * v
            if value: dst[k] = value
            else: dst.pop(k, None)
    def shifted(row, term, sign=1):
        return [{tuple(a + b for a, b in zip(k, term)): sign * v for k, v in cell.items()} for cell in row]
    for side in ('left', 'right'):
        matrix = [[Q(i == j) for j in range(32)] for i in range(32)]
        for e in word['boundaries'][side + '_program']:
            if e[0] == 'SWAP': matrix[e[1]], matrix[e[2]] = matrix[e[2]], matrix[e[1]]
            elif e[0] == 'SCALE': matrix[e[1]] = [Q(e[2]) * x for x in matrix[e[1]]]
            else:
                need(e[0] == 'ADD', 'Boundary scalar opcode')
                matrix[e[1]] = [x + Q(e[3]) * y for x, y in zip(matrix[e[1]], matrix[e[2]])]
        need(matrix == [[Q(x) for x in row] for row in word['boundaries'][side]], 'Exact scalar boundary program')
    rows = [[{zero: Q(x)} if Q(x) else {} for x in row] for row in word['boundaries']['right']]
    for e in word['physical_events']:
        if e[0] in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            x, y = 2 * pair, 2 * pair + 1
            if back: x, y = y, x
            term = (1 if back else -1,) + (0,) * 33
            for dst, src in zip(rows[y], shifted(rows[x], term)):
                plus(dst, src, Q(-1 if back else 1))
            if e[0] == 'LOCAL':
                term = (0,) + tuple(int(s == stage) for s in range(33))
                for r in (x, y): rows[r] = shifted(rows[r], term)
        elif e[0] == 'Q_POWER':
            need(e[2] in (-2, 2), 'Only even central powers are free')
            rows[e[1]] = shifted(rows[e[1]], (e[2],) + (0,) * 33)
        elif e[0] == 'IDLE':
            term = (0,) + tuple(int(s in e[2]) for s in range(33))
            for r in (2 * e[1], 2 * e[1] + 1): rows[r] = shifted(rows[r], term)
        elif e[0] == 'ADD':
            for dst, src in zip(rows[e[1]], rows[e[2]]): plus(dst, src, Q(e[3]))
        else:
            need(e[0] in ('SWAP', 'SIGNED_SWAP'), 'Controller physical opcode')
            rows[e[1]], rows[e[2]] = rows[e[2]], shifted(rows[e[1]], zero, -1 if e[0] == 'SIGNED_SWAP' else 1)
    out = [[{} for _ in range(32)] for _ in range(32)]
    for i, row in enumerate(word['boundaries']['left']):
        for k, q in enumerate(row):
            if Q(q):
                for j in range(32): plus(out[i][j], rows[k][j], Q(q))
    expected = [[{tuple(word['diagonal'][i]): Q(1)} if i == j else {} for j in range(32)] for i in range(32)]
    need(out == expected, 'All p16 Laurent coefficients, central signs and boundary factors')
    return word



def construct():
    source = L.read(L.ROOT/'research/joint-helper-lattice/CONTROLLER.json')
    replay(source)
    word = deepcopy(source)
    events, sites = [], []
    for e in source['physical_events']:
        if e[0] == 'LOCAL' and e[3]:
            _, stage, pair, _ = e
            x, y = 2*pair, 2*pair+1
            events += [['Q_POWER',x,-2], ['SIGNED_SWAP',x,y], ['LOCAL',stage,pair,False],
                       ['Q_POWER',y,2], ['SIGNED_SWAP',y,x]]
            sites.append(stage)
        else:
            events.append(deepcopy(e))
    word['physical_events'] = events
    word['wrapper_sites'] = sites
    word.pop('invoice')
    need(len(sites) == 16 and all(not e[3] for e in events if e[0] == 'LOCAL'), 'Eighteen forward suppliers')
    replay(word)
    return word


def physical(word, local):
    N = L.load(L.ROOT/'research/pr4359-p7-padding/native_inventory.py', 'productive_p104_phase_polynomial')
    source = L.read(L.ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json')
    recipes = {r['q']:r for r in source['recipes']}
    dimension = 265
    axes = tuple(1 << i for i in range(dimension))
    def completed(stage):
        return N.norm((axis,1) for axis in axes[:9+8*stage])
    contacts, squares, target_profile = [], 0, Counter()
    idle_jobs = Counter()
    for _,stage,pair,back in (e for e in word['physical_events'] if e[0] == 'LOCAL'):
        need(not back, 'No inverse-transpose local implementation')
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
            positive = list(axes[:9]) if selected[0] else [q]
            positive += [axis for s in range(1,len(selected)) if selected[s] for axis in axes[9+8*(s-1):9+8*s]]
            need(N.polynomial(physical,dimension) == N.polynomial(N.norm([(x,1) for x in positive]+[(q,2)]*(qp == -1)),dimension), 'Full main output phase and rank')
            target_profile[len(positive)] += 1
    for e in word['physical_events']:
        if e[0] != 'IDLE':
            continue
        stages = e[2]
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
            idle_jobs[len(positive)] += 2
    return {'ports':104,'full_calls':18,'physical_contacts':4*len(contacts),'central_square_columns':squares,
            'main_targets':dict(target_profile),'whole_idle_jobs':dict(idle_jobs),'route_payload_sha256':sha256(json.dumps(contacts,separators=(',',':')).encode()).hexdigest(),
            'wrapper_sites':word['wrapper_sites'],'new_paid_jobs':0,'tensor_rule':'Factorwise native maps; scalar signs stay outside the tensor power.'}


def controls(word):
    bad = deepcopy(word)
    bad['physical_events'].remove(next(e for e in bad['physical_events'] if e[0] == 'Q_POWER'))
    try:
        replay(bad)
    except ValueError:
        return {'missing_central_translation':'Rejected by the complete Laurent endpoint'}
    raise ValueError('Missing central translation accepted')
