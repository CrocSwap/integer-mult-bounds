"""Complete source invoice and positive ordinary-cost comparison.

Local algebra/native correctness is inherited, not inferred from these counts.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction


def require(test, message):
    if not test:
        raise ValueError(message)


def space(vectors):
    span = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512 and v not in span, 'independent nine-axis frame')
        span |= {x ^ v for x in span}
    return span


def local_invoice(word):
    n = word['public']
    frames = word['frames']
    spans = [space(f) for f in frames]
    ranks = list(map(len, frames))
    hosted = word['hosted']
    require(len(word['live']) == len(set(word['live'])) == 104 and
            len(hosted['X2']) == len(hosted['Y2']) == 96, 'exact first/second main list sizes')
    main = set(word['live']) | {r+112 for r in word['live']} | set(hosted['X2']) | set(hosted['Y2'])
    require(len(main) == 400 and len(hosted['Dports']) == 96, '104 first pairs and 96 second pairs')
    require(len(word['ports']) == len(set(word['ports'])) == len(word['live']) == 104, 'literal native port inventory')
    require(len(word['initial']) == len(word['final']) == n, 'literal native boundaries')
    helpers = Counter()
    for r in set(range(n))-main:
        a, b = word['initial'][r], word['final'][r]
        require(spans[a] < spans[b], 'positive productive helper endpoint')
        helpers[ranks[b]-ranks[a]] += 1
    current = word['initial'][:] + [None]*word['owned_fields']
    live = set()
    paid = Counter()
    lifetimes = peak = rises = rise_mass = 0
    allowance = reviewed_scalar = 0
    for event in word['program']:
        op, r = event[:2]
        if op == 'INIT':
            require(n <= r < len(current) and r not in live and current[r] is None, 'local fresh owned initialization')
            live.add(r); current[r] = event[2]
            lifetimes += 1; peak = max(peak, len(live)); allowance += 2
        elif op == 'CLEAR':
            require(r in live and current[r] == event[2], 'local current owned clearance')
            live.remove(r); current[r] = None; allowance += 2
        elif op == 'MOVE':
            a, b, owned = event[2:]
            require(current[r] == a and ((r in live) == owned), 'actual MOVE ownership and chart')
            require(spans[a] < spans[b] or spans[b] < spans[a], 'strict nested MOVE')
            rank = abs(ranks[b]-ranks[a]); paid[rank] += 1
            if owned and ranks[b] > ranks[a]:
                rises += 1; rise_mass += rank
            current[r] = b
        elif op in ('ADD', 'COPY', 'SCALE'):
            require(current[r] == event[-1] and (r < n or r in live), 'local live scalar destination')
            if op != 'SCALE':
                src = event[2]
                require(src != r and current[src] == current[r] and (src < n or src in live), 'local live scalar source')
            f = Fraction(event[-2]); a, d = abs(f.numerator), f.denominator
            require(a > 0, 'nonzero local coefficient')
            if op == 'SCALE':
                allowance += 2*(abs(a.bit_length()-d.bit_length())+int(f < 0))
                reviewed_scalar += 4*(a.bit_length()+d.bit_length()+1)
            else:
                allowance += 2*(3+a.bit_length()-1+a.bit_count()+d.bit_length()-1)
                reviewed_scalar += 4*(a.bit_length()+a.bit_count()+d.bit_length()+1)
        else:
            raise ValueError('unexpected local opcode')
    require(not live and current[:n] == word['final'], 'local complete lifetime/chart return')
    routes = 1000*(sum(paid.values())+2*sum(helpers.values())+208+2*96+4*104+4*96+4*lifetimes)
    return dict(public=n, helpers=helpers, paid=paid, lifetimes=lifetimes, peak_owned=peak,
                owned_labels=word['owned_fields'], owned_rises=rises, owned_rise_mass=rise_mass,
                allowance=allowance, reviewed_scalar=reviewed_scalar, routes=routes,
                allowance_per_call=allowance+routes, reviewed_per_call=reviewed_scalar+routes)


def outer_invoice(caller, local):
    targets = Counter({r: 18*n for r, n in local['helpers'].items()})
    paid = Counter({r: 18*n for r, n in local['paid'].items()})
    for ty in ('A', 'B'):
        t = caller['types'][ty]; multiplicity = len(t['ports'])
        for d in t['diagonal']:
            targets[d[0] % 2 + 8*sum(d[2:])] += multiplicity
        for e in caller['events']:
            if e[0] != ty:
                continue
            if e[1] in ('QUERY', 'QSELF'):
                paid[1] += multiplicity
            elif e[1] == 'IDLE_ONE':
                paid[8*len(e[3])] += multiplicity
    return targets, paid


def exchanges(selected):
    require(len(set(selected)) == len(selected), 'adapter distinct selected axes')
    return len(set(selected)-set(range(len(selected))))


def caller_cost(caller):
    out = dict(caller_envelope=0, thin_lifecycle=0, qself_extra_lifecycle=0,
               main_normalizers=0, main_maps=0, idle_maps=0, query_maps=0,
               lambda_recharge=0)
    for ty in ('A', 'B'):
        t = caller['types'][ty]; ports = len(t['ports']); roles = t['roles']
        events = [e for e in caller['events'] if e[0] in (ty, 'J')]
        out['caller_envelope'] += 32*roles*ports*len(events)
        out['main_normalizers'] += 26*roles*ports
        for qp, zero, *mask in t['diagonal']:
            axes = ([0] if qp else []) + [a for k, yes in enumerate(mask, 1) if yes for a in range(9+8*(k-1), 9+8*k)]
            out['main_maps'] += 1000*ports*(2*exchanges(axes)+2*bool(qp)+int(qp == -1))
        for e in events:
            if e[0] == 'J':
                continue
            op = e[1]
            if op in ('QUERY', 'QSELF'):
                out['thin_lifecycle'] += 16*ports
                out['query_maps'] += 1000*ports*(2+int(e[-1] == -1))
                if op == 'QSELF':
                    # Additional explicit charge: four lifecycle/scalar operations,
                    # each at the inherited 32-unit ordinary gate envelope.
                    out['qself_extra_lifecycle'] += 128*ports
            elif op == 'IDLE_ONE':
                axes = [a for k in e[3] for a in range(9+8*(k-1), 9+8*k)]
                out['idle_maps'] += 2000*ports*exchanges(axes)
            elif op == 'LAMBDA':
                out['lambda_recharge'] += 1000*ports
    # The extra LAMBDA reading is deliberately separate and charged twice below.
    out['raw_rest'] = sum(v for k, v in out.items() if k != 'lambda_recharge')
    return out


def verify(old, new, word):
    require(old['types']['A']['ports'] == new['types']['A']['ports'] == word['hosted']['Dports'], 'same actual 96 second-plane ports')
    require(old['types']['B']['ports'] == new['types']['B']['ports'], 'same remaining eight ports')
    require(new['types']['A']['roles'] == new['types']['B']['roles'] == 38, 'E-free main role count')
    require(all(sum(d[2:]) > 0 for t in new['types'].values() for d in t['diagonal']), 'no E or other empty-mask main target')
    old_j = [e for e in old['events'] if e[0] == 'J']
    new_j = [e for e in new['events'] if e[0] == 'J']
    require([e[1] for e in old_j] == [e[1] for e in new_j] == list(range(1, 19)), 'same 18 complete local calls')
    # Bind every concrete local public field at every new source contact.
    mains = {(ty, role, port) for ty, t in new['types'].items()
             for role in range(t['offset'], t['offset']+t['roles']) for port in t['ports']}
    helpers = set()
    for e in new_j:
        fields = {}
        second = dict(zip(word['hosted']['Dports'], zip(word['hosted']['X2'], word['hosted']['Y2'])))
        for port in new['types']['A']['ports']:
            first = word['live'][port]; x, y = second[port]
            for field, role in zip((first, first+112, x, y), e[2]):
                fields[field] = ('main', 'A', role, port)
        for port in new['types']['B']['ports']:
            first = word['live'][port]
            for field, role in zip((first, first+112), e[3][:2]):
                fields[field] = ('main', 'B', role, port)
        require(len(fields) == 400 and len(set(fields.values())) == 400, 'all concrete source mains map injectively')
        for field in range(word['public']):
            if field not in fields:
                target = ('helper', e[1], field)
                require(target not in helpers, 'fresh arbitrary helper input for each local invocation')
                helpers.add(target); fields[field] = target
        require(set(fields) == set(range(word['public'])) and len(set(fields.values())) == word['public'], 'complete concrete local public map')
    require(len(mains) == 3952 and len(helpers) == 19098, 'complete distinct main/helper inventory')
    # Exact B stream equality after the public-role offset changes by two.
    def bstream(c):
        off = c['types']['B']['offset']; result = []
        for e in c['events']:
            if e[0] != 'B':
                continue
            z = e[:]; z[2] -= off
            if e[1] in ('ADD', 'SWAP', 'QUERY'):
                z[3] -= off
            result.append(z)
        return result
    require(bstream(old) == bstream(new), 'whole B stream unchanged after offset relabeling')
    require(old['types']['B']['diagonal'] == new['types']['B']['diagonal'], 'B targets unchanged')
    local = local_invoice(word)
    oldT, oldP = outer_invoice(old, local)
    newT, newP = outer_invoice(new, local)
    for rank in set(oldT)|set(oldP)|set(newT)|set(newP):
        need = 192 if rank == 1 else 0
        require(oldT[rank]-newT[rank] == need and oldP[rank]-newP[rank] == need, 'complete rankwise target/paid delta')
    a, b = caller_cost(old), caller_cost(new)
    old_upper = 18*local['reviewed_per_call'] + a['raw_rest']
    new_upper = 18*local['reviewed_per_call'] + b['raw_rest']
    scale = 18*word['public']*104  # #6936's explicit per-input 1125 conversion reading
    require(old_upper == 832255648, 'exact reconstruction of predecessor reviewed raw count')
    require(old_upper+a['lambda_recharge']+scale == 847550640, 'exact predecessor double-charge reading')
    require(new_upper+b['lambda_recharge']+scale < 10**9, 'positive complete new conditional ordinary budget')
    return {'local_source_counts': local,
            'old_targets': dict(sorted(oldT.items())), 'old_paid': dict(sorted(oldP.items())),
            'new_targets': dict(sorted(newT.items())), 'new_paid': dict(sorted(newP.items())),
            'target_count': sum(newT.values()), 'paid_count': sum(newP.values()),
            'rank_mass_surplus': sum(r*(newT[r]-newP[r]) for r in set(newT)|set(newP)),
            'new_paid_rank_mass': sum(r*n for r,n in newP.items()),
            'old_caller_cost': a, 'new_caller_cost': b,
            'old_reviewed_raw': old_upper, 'new_reviewed_raw': new_upper,
            'per_call_scale_recharge': scale,
            'new_double_recharged_raw': new_upper+b['lambda_recharge']+scale,
            'ordinary_margin': 10**9-new_upper-b['lambda_recharge']-scale,
            'owned_query_bank_count': 1, 'old_outer_query_lifetimes': 608,
            'new_outer_query_lifetimes': 416, 'new_qself_lifetimes': 192,
            'selected_kappa_change': False,
            'status': 'Conditional source invoice; no native, rounded, physical fullcaller or supplier admission follows from counting.'}
