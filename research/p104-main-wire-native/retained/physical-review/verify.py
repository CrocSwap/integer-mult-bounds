#!/usr/bin/env python3
"""Independent finite physical/invoice audit of exact #6726.

Jerry Chen (@CubeJerry), with substantial OpenAI assistance. Apache-2.0.
No construction, pricing, scalar, or physical implementation is imported.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import reduce
from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent


def require(test, reason):
    if not test:
        raise ValueError(reason)


def read(name):
    raw = (HERE / 'frozen' / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        relative = Path(pin['path']).relative_to('research/p104-fragment-physical-invoice-audit')
        raw = (HERE / relative).read_bytes()
        require(len(raw) == pin['bytes'], 'source length: ' + pin['path'])
        require(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        require(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'], 'source Git blob: ' + pin['path'])
    return pins


def span(vectors):
    values = {0}
    for value in vectors:
        require(isinstance(value, int) and 0 < value < 512, 'native nine-axis vector')
        require(value not in values, 'frame axes independent')
        values |= {old ^ value for old in values}
    return sum(1 << value for value in values)


def native_ledger(word, check_rows=True):
    """Scan physical charts and scalar rows; MOVE changes chart, not chart coordinates."""
    frames = word['frames']
    spaces = [span(frame) for frame in frames]
    ranks = [len(frame) for frame in frames]
    public = word['public']
    total = public + word['owned_fields']
    require(len(word['initial']) == len(word['final']) == public, 'public boundaries')
    chart = word['initial'][:] + [None] * word['owned_fields']
    rows = [{i: Fraction(1)} for i in range(public)] + [{} for _ in range(word['owned_fields'])]
    live_owned = set()
    lifetime = peak = 0
    paid = Counter()
    operations = Counter()
    paid_records = []
    scalar_units = 0
    for index, event in enumerate(word['program']):
        op, *args = event
        operations[op] += 1
        if op == 'INIT':
            field, frame = args
            require(public <= field < total and chart[field] is None, 'owned INIT before use')
            chart[field] = frame
            rows[field] = {}
            live_owned.add(field)
            lifetime += 1
            peak = max(peak, len(live_owned))
        elif op == 'CLEAR':
            field, frame = args
            require(field in live_owned and chart[field] == frame, 'owned CLEAR at current frame')
            chart[field] = None
            rows[field] = {}
            live_owned.remove(field)
        elif op == 'MOVE':
            field, start, end, backward = args
            require(chart[field] == start, 'chronological MOVE source frame')
            lo, hi = ((end, start) if ranks[end] < ranks[start] else (start, end)) if backward else (start, end)  # DECLARED CHANGE (assumption A6): an owned MOVE may be nested in either direction; it is paid |delta dim| either way. Predecessor line: lo, hi = (end, start) if backward else (start, end)
            require(spaces[lo] & spaces[hi] == spaces[lo] and ranks[lo] < ranks[hi], 'strict nested paid MOVE')
            rank = ranks[hi] - ranks[lo]
            paid[rank] += 1
            paid_records.append((index, field, rank))
            chart[field] = end
        elif op in ('ADD', 'COPY'):
            dst, src, value, frame = args
            require(dst != src and chart[dst] == chart[src] == frame, 'scalar common current chart')
            value = Fraction(value)
            require(value and value.denominator & (value.denominator - 1) == 0, 'nonzero dyadic scalar')
            if op == 'COPY':
                require(dst in live_owned and not rows[dst], 'COPY requires cleared owned destination')
            if check_rows:
                for column, coefficient in rows[src].items():
                    new = rows[dst].get(column, 0) + value * coefficient
                    if new:
                        rows[dst][column] = new
                    else:
                        rows[dst].pop(column, None)
            scalar_units += 4 * (abs(value.numerator).bit_length() + abs(value.numerator).bit_count() + value.denominator.bit_length() + 1)
        elif op == 'SCALE':
            field, value, frame = args
            value = Fraction(value)
            require(chart[field] == frame and value, 'scale at current live chart')
            require(abs(value.numerator) & (abs(value.numerator)-1) == 0 and value.denominator & (value.denominator-1) == 0, 'invertible dyadic scale')
            if check_rows:
                rows[field] = {column: value * coefficient for column, coefficient in rows[field].items()}
            scalar_units += 4 * (abs(value.numerator).bit_length() + value.denominator.bit_length() + 1)
        else:
            raise ValueError('unknown native opcode ' + op)
    require(not live_owned and chart[:public] == word['final'], 'complete native return and owned clearance')
    ports = word['ports']
    live = word['live']
    require(len(set(ports)) == len(ports) == len(set(live)) == len(live) == 104, '104 distinct retained ports')
    main = set(live) | {112 + i for i in live}
    require(len(main) == 208, 'disjoint native X/Y pairs')
    helpers = Counter()
    helper_labels = []
    for field in range(public):
        if check_rows:
            expected = {field: Fraction(1)}
            if field >= 112 and field - 112 in live:
                expected[field - 112] = Fraction(1)
            require(rows[field] == expected, 'all arbitrary native input row ' + str(field))
        if field not in main:
            start, end = word['initial'][field], word['final'][field]
            require(spaces[start] & spaces[end] == spaces[start] and ranks[start] < ranks[end], 'productive helper strict nested endpoint')
            rank = ranks[end] - ranks[start]
            helpers[rank] += 1
            helper_labels.append((field, rank))
    for i, q in zip(live, ports):
        require(frames[word['initial'][i]] == [q] and frames[word['initial'][112+i]] == [], 'native incoming Q/I main interface')
        require(frames[word['final'][i]] == list(1 << j for j in range(9)), 'native complete nine-axis X endpoint')
        require(ranks[word['final'][112+i]] == 8 and all((q & a).bit_count()%2 == 0 for a in frames[word['final'][112+i]]), 'native rank-eight q-orthogonal Y endpoint')
    return dict(paid=paid, helpers=helpers, helper_labels=helper_labels, paid_records=paid_records,
                public=public, owned=word['owned_fields'], lifetimes=lifetime, peak=peak,
                operations=operations, scalar_upper=scalar_units,
                scalar_rows=public if check_rows else 0)


def terms(entries):
    counts = Counter()
    for vector, coefficient in entries:
        counts[vector] += coefficient
    return {vector: coefficient % 4 for vector, coefficient in counts.items() if vector and coefficient % 4}


def difference(a, b):
    return terms(list(a.items()) + [(v, -c) for v, c in b.items()])


def phase(coefficients, frequency):
    return sum(c * ((vector & frequency).bit_count() & 1) for vector, c in coefficients.items()) % 4


def axes_of(mask):
    out = []
    while mask:
        bit = mask & -mask
        out.append(bit)
        mask ^= bit
    return out


def translation_for(delta):
    """Parity is degree <=2 modulo four; weight<=2 frequencies determine it."""
    support = axes_of(reduce(int.__or__, delta, 0))
    shift = 0
    single = {}
    for bit in support:
        single[bit] = phase(delta, bit)
        require(single[bit] in (0, 2), 'contact linear phase must be an ordinary translation')
        if single[bit] == 2:
            shift |= bit
    for a, b in combinations(support, 2):
        require(phase(delta, a | b) == (single[a] + single[b]) % 4, 'contact residual quadratic phase')
    return shift


def route_function(q, basis, stage):
    fresh = [1 << (9 + 8*(stage-1) + i) for i in range(8)]
    old_mask = 511
    fresh_mask = sum(fresh)
    require(q.bit_count() % 2 == 1, 'odd central port')
    require(len(basis) == 8 and all(0 < v < 512 for v in basis), 'native eight-dimensional basis')
    require(all((a & b).bit_count() % 2 == (i == j) for i, a in enumerate([q]+basis) for j, b in enumerate([q]+basis)), 'complete orthonormal native basis')
    def route(value):
        old = value & old_mask
        result = value & ~(old_mask | fresh_mask)
        if (old & q).bit_count() % 2:
            result ^= q
        for native_axis, fresh_axis in zip(basis, fresh):
            if value & fresh_axis:
                result ^= native_axis
            if (old & native_axis).bit_count() % 2:
                result ^= fresh_axis
        return result
    affected = [1 << i for i in range(9)] + fresh
    images = [route(v) for v in affected]
    require(all(route(image) == axis for axis, image in zip(affected, images)), 'route involution')
    require(all((a & b).bit_count() % 2 == (i == j) for i, a in enumerate(images) for j, b in enumerate(images)), 'route orthogonality')
    require(route(q) == q, 'route fixes Q')
    return route


def contact(before, after, route, omit_translation=False):
    moved = terms((route(v), c) for v, c in before.items())
    shift = translation_for(difference(after, moved))
    supplied = 0 if omit_translation else shift
    require(translation_for(difference(after, terms(list(moved.items()) + [(supplied, 2)]))) == 0, 'full forward absolute phase')
    inverse = route(supplied)
    require(translation_for(difference(before, terms([(route(v), c) for v, c in after.items()] + [(inverse, 2)]))) == 0, 'full inverse absolute phase')
    require(shift.bit_count() <= 17 and inverse.bit_count() <= 17, 'fixed seventeen-axis translation budget')
    return {'translation': shift, 'inverse_translation': inverse}


def physical(word, native, recipes, omit_translation=False):
    stages = word['stages']
    require(word['ambient_rank'] == 9 + 8*stages, 'declared ambient axes')
    axes = [1 << i for i in range(word['ambient_rank'])]
    full_events = [(i, e) for i, e in enumerate(word['events']) if e[0] == 'LOCAL']
    require([e[1] for _, e in full_events] == list(range(1, stages+1)), 'fresh native stage chronology')
    by_port = {r['q']: r for r in recipes['recipes']}
    require(set(native['ports']) <= set(by_port), 'every retained port has a phase recipe')
    records = []
    for _, (_, stage, src, dst) in full_events:
        require(src != dst and 0 <= src < word['roles'] and 0 <= dst < word['roles'], 'distinct valid native caller fields')
        before_axes = axes[:9+8*(stage-1)]
        after_axes = axes[:9+8*stage]
        spectator = axes[9:9+8*stage]
        for q in native['ports']:
            basis = by_port[q]['idle_children'][0]['orthogonal_axes'][:8]
            route = route_function(q, basis, stage)
            x0 = terms((a, 1) for a in before_axes)
            y0 = terms(list(x0.items()) + [(q, -1)])
            x1 = terms((a, 1) for a in after_axes)
            y1 = terms(list(x1.items()) + [(q, -1)])
            native_x0 = terms([(a, 1) for a in spectator] + [(q, 1)])
            native_y0 = terms((a, 1) for a in spectator)
            native_x1 = terms((a, 1) for a in spectator + axes[:9])
            native_y1 = terms(list(native_x1.items()) + [(q, -1)])
            maps = [contact(a, b, route, omit_translation) for a, b in ((x0,native_x0),(y0,native_y0),(native_x1,x1),(native_y1,y1))]
            body = terms((a, 1) for a in axes[9+8*(stage-1):9+8*stage])
            require(translation_for(difference(difference(x1,x0),body)) == 0 and translation_for(difference(difference(y1,y0),body)) == 0, 'native diagonal is fresh D_stage with absolute phase')
            require(translation_for(difference(difference(y1,x0),terms(list(body.items())+[(q,-1)]))) == 0, 'native cross coefficient is D_stage Q^-1')
            records.append([stage,q,maps])
    main = Counter()
    output_shifts = 0
    for term in word['diagonal']:
        qp, zero, *selected = term
        require(qp in (-1,0,1) and zero == 0 and len(selected) == stages and set(selected) <= {0,1}, 'literal physical endpoint exponent domain')
        for q in native['ports']:
            body_axes = [axis for stage, yes in enumerate(selected,1) if yes for axis in axes[9+8*(stage-1):9+8*stage]]
            positive = ([q] if qp else []) + body_axes
            require(all((a & b).bit_count()%2 == (i == j) for i,a in enumerate(positive) for j,b in enumerate(positive)), 'all positive endpoint axes orthonormal')
            actual = terms([(q,qp)] + [(a,1) for a in body_axes])
            target = terms((a,1) for a in positive)
            shift = translation_for(difference(target,actual))
            require(shift == (q if qp == -1 else 0), 'exact endpoint translation')
            output_shifts += bool(shift)
            main[len(positive)] += 1
    idle = Counter()
    idle_records = []
    for index,event in enumerate(word['events']):
        if event[0] not in ('IDLE','IDLE_ONE'):
            continue
        owners, selection = (event[1:3], event[3]) if event[0] == 'IDLE' else ([event[1]],event[2])
        require(len(set(owners)) == len(owners) and all(0 <= r < word['roles'] for r in owners), 'distinct valid idle owners')
        require(selection and len(set(selection)) == len(selection) and all(1 <= s <= stages for s in selection), 'distinct valid complete idle axes')
        positive = [axis for stage in selection for axis in axes[9+8*(stage-1):9+8*stage]]
        require(len(set(positive)) == len(positive), 'whole idle independent Gaussian factors')
        idle[len(positive)] += len(native['ports']) * len(owners)
        idle_records.extend((index,owner,q,len(positive)) for owner in owners for q in native['ports'])
    require(len(word['diagonal']) == word['roles'], 'one target for every arbitrary caller input')
    return dict(contacts=4*len(records), contact_digest=sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest(),
                nonzero_contact_translations=sum(bool(m['translation']) for _,_,maps in records for m in maps),
                main=main, idle=idle, idle_records=idle_records, output_translations=output_shifts,
                dimension=word['ambient_rank'])


def allocation(word, native, ledger, alias=False):
    main = {(role,q) for role in range(word['roles']) for q in native['ports']}
    names = {('main',role,q) for role,q in main}
    helper_jobs = []
    local_number = 0
    for event_index, event in enumerate(word['events']):
        if event[0] != 'LOCAL':
            continue
        _,stage,src,dst = event
        public_map = {}
        for i,q in zip(native['live'],native['ports']):
            public_map[i] = ('main',src,q)
            public_map[112+i] = ('main',dst,q)
        for field,rank in ledger['helper_labels']:
            key = ('helper',0 if alias else local_number,field)
            require(key not in names, 'fresh native helper cannot alias an earlier public input')
            names.add(key)
            public_map[field] = key
            helper_jobs.append((event_index,stage,field,rank,key))
        require(len(public_map) == ledger['public'] and len(set(public_map.values())) == ledger['public'], 'injective local public-input allocation')
        local_number += 1
    owned = {('owned',i) for i in range(ledger['owned'])}
    thin = {('query_scratch',0)}
    require(not (names & owned or names & thin or owned & thin), 'owned/query scratch is disjoint and uncredited')
    return dict(main_fields=len(main), helper_fields=len(helper_jobs), productive_fields=len(names),
                reserved_native_owned=len(owned), reserved_query_owned=len(thin),
                peak_native_owned=ledger['peak'], maximum_live_owned=max(ledger['peak'],1),
                invocations=local_number, helper_jobs=helper_jobs)


def invoice(word, ledger, physics, fields):
    paid = Counter()
    targets = Counter(physics['main'])
    for _,_,_,rank,_ in fields['helper_jobs']:
        targets[rank] += 1
    for event in word['events']:
        if event[0] == 'LOCAL':
            paid.update(ledger['paid'])
        elif event[0] == 'QUERY':
            require(event[3] in (-1,1), 'legal thin query orientation')
            paid[1] += 104
    paid.update(physics['idle'])
    require(sum(targets.values()) == fields['productive_fields'], 'productive count equals distinct arbitrary inputs')
    return {'targets':targets, 'paid':paid, 'productive_fields':sum(targets.values()), 'paid_calls':sum(paid.values()),
            'target_mass':sum(r*n for r,n in targets.items()), 'paid_mass':sum(r*n for r,n in paid.items())}


def compare_invoice(actual, expected):
    require(actual['targets'] == Counter({int(k):v for k,v in expected['targets'].items()}), 'complete productive rank histogram')
    require(actual['paid'] == Counter({int(k):v for k,v in expected['paid'].items()}), 'complete paid rank histogram')
    require(actual['productive_fields'] == expected['productive_fields'] and actual['paid_calls'] == expected['paid_calls'], 'independent count totals')
    require(actual['target_mass'] - actual['paid_mass'] == expected['rank_mass_surplus'], 'independent rank-mass surplus')


def chronology(word, witnesses):
    slots = {'ADD':(1,2),'SCALE':(1,),'SWAP':(1,2),'LOCAL':(2,3),'QUERY':(1,2),'IDLE':(1,2),'IDLE_ONE':(1,),'LAMBDA':(1,),'Q_POWER':(1,)}
    actual_handoffs = []
    for number, witness in enumerate(witnesses):
        # Witness zero belongs to the intermediate 33-field word. Later input
        # bases precede that whole word and shift its earlier cut chronologically.
        offset = sum(len(later['input_basis']) for later in witnesses[number+1:])
        handoff = witness['handoff_after'] + offset
        pivot,fresh = witness['pivot'], witness['fresh']
        require(all(event[j] != fresh for event in word['events'][:handoff+1] for j in slots[event[0]]), 'fresh handoff input untouched in entire prefix')
        cut_basis = witness['cut_basis']
        require(word['events'][handoff-len(cut_basis)+1:handoff+1] == cut_basis, 'complete cut basis at actual chronological handoff')
        require(word['events'][handoff-len(cut_basis)] == ['IDLE_ONE',2,witness['prefix_stages']], 'handoff immediately follows the paid fragment')
        require(word['diagonal'][pivot] == witness['prefix_target'] and word['diagonal'][fresh] == witness['suffix_target'], 'retirement endpoint credit matches literal witness')
        first_fresh = next(i for i,event in enumerate(word['events']) if any(event[j] == fresh for j in slots[event[0]]))
        require(first_fresh == handoff+1, 'fresh suffix starts immediately after completed prefix')
        require(all(event[j] != pivot for event in word['events'][handoff+1:] for j in slots[event[0]]), 'retired productive output retained untouched through the full suffix')
        actual_handoffs.append(handoff)
    return {'fresh_inputs': [w['fresh'] for w in witnesses], 'witness_handoffs':[w['handoff_after'] for w in witnesses], 'literal_final_handoffs':actual_handoffs}


def central_normalization():
    def mul(a,b):
        return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
    values = [(1,0),(0,1),(-1,0),(0,-1)]
    for j,q in enumerate(values):
        lam = (1,0) if j%2 == 0 else (0,1)
        inverse = (lam[0],-lam[1])
        require(mul(lam,inverse)==(1,0), 'ordinary lambda and inverse are exact')
        central = mul(lam,(q[0],-q[1]))
        require(mul(central,central)==(1,0), 'normalized central S is an involution')
    # At two odd factor characters Q_total=-1, lambda(Q_total)=+1,
    # whereas tensoring the two factor lambdas would incorrectly give -1.
    require((1,0) != mul((0,1),(0,1)), 'global lambda must remain outside tensor powers')
    return {'central_characters':4,'two_factor_lambda_disagreement':True,
            'rule':'Physical Gaussian maps tensor factorwise; ordinary scalar coefficients and lambda polynomials act on the total Q outside tensor powers.'}


def coordinate_swaps(selected, dimension):
    """Map a subset of canonical axes to the first r axes by explicit exchanges."""
    require(len(set(selected)) == len(selected), 'adapter axes distinct')
    require(all(0 <= axis < dimension for axis in selected), 'adapter axes in ambient carrier')
    wanted = set(range(len(selected)))
    swaps = list(zip(sorted(set(selected)-wanted), sorted(wanted-set(selected))))
    def move(axis):
        for a,b in swaps:
            if axis == a:
                axis = b
            elif axis == b:
                axis = a
        return axis
    require({move(axis) for axis in selected} == wanted, 'explicit Gaussian axis permutation')
    require(all(move(move(axis)) == axis for axis in range(dimension)), 'permutation adapter inverse')
    require(len(swaps) <= len(selected), 'rank-many two-axis exchanges suffice')
    return swaps


def adapter_inventory(word, native, recipes):
    """Charge complete canonical-job input/output conversions, including full idles."""
    by_port = {r['q']:r for r in recipes['recipes']}
    for q in native['ports']:
        basis = [q]+by_port[q]['idle_children'][0]['orthogonal_axes'][:8]
        # This nine-axis map sends q to coordinate zero, fixes all spectators,
        # and sends its orthonormal complement to coordinates one through eight.
        def convert(value):
            return (value & ~511) | sum(((value & axis).bit_count()%2) << i for i,axis in enumerate(basis))
        require([convert(axis) for axis in basis] == [1 << i for i in range(9)], 'explicit nine-axis q-to-coordinate adapter')
        require(all((a&b).bit_count()%2 == (i==j) for i,a in enumerate(basis) for j,b in enumerate(basis)), 'q adapter orthogonal and invertible')
    records = {'main':[], 'idle':[], 'query':[]}
    for role,(qp,zero,*selection) in enumerate(word['diagonal']):
        axes = ([0] if qp else []) + [axis for stage,yes in enumerate(selection,1) if yes for axis in range(9+8*(stage-1),9+8*stage)]
        exchanges = coordinate_swaps(axes,word['ambient_rank'])
        for q in native['ports']:
            # Both whole-job boundaries are charged, even though a target
            # interface may permit some of these maps to remain implicit.
            records['main'].append([role,q,len(exchanges),2*bool(qp),int(qp==-1)])
    for index,event in enumerate(word['events']):
        if event[0] in ('IDLE','IDLE_ONE'):
            owners,stages = (event[1:3],event[3]) if event[0]=='IDLE' else ([event[1]],event[2])
            axes = [axis for stage in stages for axis in range(9+8*(stage-1),9+8*stage)]
            exchanges = coordinate_swaps(axes,word['ambient_rank'])
            records['idle'].extend([index,owner,q,len(exchanges)] for owner in owners for q in native['ports'])
        elif event[0]=='QUERY':
            _,dst,src,power = event
            require(dst != src and all(0<=r<word['roles'] for r in (dst,src)), 'query uses distinct public fields')
            require(power in (-1,1), 'query Gaussian orientation')
            # Two nine-axis q-basis conversions and, for Q^-1, Q^2 translation.
            records['query'].extend([index,q,2,int(power==-1)] for q in native['ports'])
    return records


def check_adapter_inventory(records,word,physics):
    require(len(records['main']) == 104*word['roles'], 'adapter for every main input/output job')
    require(len(records['idle']) == sum(physics['idle'].values()), 'two adapters for every whole paid idle job')
    require(len(records['query']) == 104*sum(e[0]=='QUERY' for e in word['events']), 'adapters for every thin query')
    for name,rows in records.items():
        keys = [tuple(row[:3] if name=='idle' else row[:2]) for row in rows]
        require(len(set(keys)) == len(keys), 'distinct '+name+' adapter jobs')
    return {'main_jobs':len(records['main']),'idle_jobs':len(records['idle']),'query_jobs':len(records['query']),
            'main_two_axis_exchanges':2*sum(row[2] for row in records['main']),
            'main_nine_axis_basis_maps':sum(row[3] for row in records['main']),
            'main_phase_translations':sum(row[4] for row in records['main']),
            'idle_two_axis_exchanges':2*sum(row[3] for row in records['idle']),
            'query_nine_axis_basis_maps':sum(row[2] for row in records['query']),
            'query_phase_translations':sum(row[3] for row in records['query']),
            'payload_sha256':sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest()}


def ordinary(word, ledger, fields, bill, adapters):
    caller_work = height = 0
    counts = Counter(event[0] for event in word['events'])
    for event in word['events']:
        op = event[0]
        work = growth = 0
        if op in ('ADD','SCALE'):
            value = Fraction(event[-1])
            numerator,denominator = abs(value.numerator),value.denominator
            require(numerator and denominator & (denominator-1) == 0, 'caller dyadic coefficient')
            if op == 'SCALE':
                require(numerator & (numerator-1) == 0, 'caller dyadic scale unit')
            # Binary multiply, additions, halvings and signs, charged for both
            # real and imaginary components with a factor-two safety margin.
            work = 4*(numerator.bit_length()+numerator.bit_count()+denominator.bit_length()+1)
            growth = (numerator+denominator).bit_length()+denominator.bit_length()+1
        elif op == 'SWAP':
            work,growth = 8,4
        elif op == 'LAMBDA':
            require(event[2] in (-1,1), 'ordinary lambda orientation')
            work,growth = 16,8
        elif op not in ('LOCAL','QUERY','IDLE','IDLE_ONE'):
            raise ValueError('unbudgeted ordinary caller opcode '+op)
        require(work <= 32 and growth <= 32, 'per-gate ordinary and height envelope')
        caller_work += work
        height += growth
    # The native scalar allowance is separately reconstructed and is deliberately
    # larger than the source's optimized scalar allowance. The same 10^7 cap holds.
    helper_normalizers = 2*sum(ledger['helpers'].values())
    native_routes = (sum(ledger['paid'].values())+helper_normalizers+208+416+4*ledger['lifetimes'])*1000
    local_upper = ledger['scalar_upper']+native_routes
    require(local_upper < 10**7, 'independent local ordinary count below retained per-call cap')
    caller_envelope = 32*word['roles']*104*len(word['events'])
    require(104*caller_work <= caller_envelope and 104*height <= caller_envelope, 'caller work and height within full-field overcount')
    query_work = counts['QUERY']*16*104
    main_maps = adapters['main_two_axis_exchanges']+adapters['main_nine_axis_basis_maps']+adapters['main_phase_translations']
    idle_maps = adapters['idle_two_axis_exchanges']
    query_maps = adapters['query_nine_axis_basis_maps']+adapters['query_phase_translations']
    outputs = fields['main_fields']*26+main_maps*1000
    idle_adapter_work = idle_maps*1000
    query_adapter_work = query_maps*1000
    complete = fields['invocations']*10**7+caller_envelope+query_work+outputs+idle_adapter_work+query_adapter_work
    require(complete < 10**9, 'complete ordinary budget')
    return {'native_scalar_upper':ledger['scalar_upper'],'native_route_upper':native_routes,'native_per_call_upper':local_upper,
            'native_per_call_budget':10**7,'helper_normalizers_per_call':helper_normalizers,'main_adapters_per_call':208,
            'caller_scalar_upper_per_port':caller_work,'caller_height_per_port':height,'caller_envelope':caller_envelope,
            'ordinary_lambda_calls_per_port':counts['LAMBDA'],'thin_query_scalar_upper':query_work,
            'main_input_output_adapter_and_normalizer_upper':outputs,'whole_idle_adapter_upper':idle_adapter_work,
            'thin_query_adapter_upper':query_adapter_work,'complete_scalar_upper':complete,'complete_scalar_budget':10**9,
            'paid_rank_mass':bill['paid_mass'],'growth_bound':'2^(10^9 + 178080*f), subject to retained physical precision/tape implementation rates',
            'route_rate_per_fixed_map':1000,'route_rate_status':'Retained rate applies to each native whole-job fixed map or each <=17-axis elementary map separately. Full153-axis main/idle permutations are decomposed and charged exchange by exchange; no blanket1000 charge for an arbitrary ambient map.'}


def rejection(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('negative control accepted')


def run():
    pins = authenticate()
    word,native,recipes,witnesses,author = [read(name) for name in ('CONTROLLER.json','NATIVE-WORD.json.gz','DATA-PHASES.json','RETIREMENT-WITNESSES.json','AUTHOR-RESULT.json')]
    expected = author['candidate']
    local = native_ledger(native)
    print('PASS independent native chronology, all public scalar rows, paid and helper ranks',flush=True)
    phys = physical(word,native,recipes)
    require(phys['contact_digest'] == expected['physical']['route_payload_sha256'], 'independent contact payload equals retained exact receipt')
    fields = allocation(word,native,local)
    bill = invoice(word,local,phys,fields)
    compare_invoice(bill,expected['complete_cost'])
    cuts = chronology(word,witnesses)
    adapter_records = adapter_inventory(word,native,recipes)
    adapters = check_adapter_inventory(adapter_records,word,phys)
    work = ordinary(word,local,fields,bill,adapters)
    controls = {}
    controls['omitted_contact_translation'] = rejection(lambda: physical(word,native,recipes,True))
    controls['native_helper_alias'] = rejection(lambda: allocation(word,native,local,True))
    bad_adapters=deepcopy(adapter_records);bad_adapters['idle'].pop()
    controls['omitted_whole_idle_adapter'] = rejection(lambda: check_adapter_inventory(bad_adapters,word,phys))
    bad=deepcopy(word)
    event=next(e for e in bad['events'] if e[0]=='IDLE_ONE')
    bad['events'].remove(event)
    controls['omitted_paid_whole_idle'] = rejection(lambda: compare_invoice(invoice(bad,local,physical(bad,native,recipes),allocation(bad,native,local)),expected['complete_cost']))
    bad=deepcopy(word);bad['diagonal'][33][0]=-1
    controls['unearned_fresh_central_target'] = rejection(lambda: compare_invoice(invoice(bad,local,physical(bad,native,recipes),allocation(bad,native,local)),expected['complete_cost']))
    bad=deepcopy(witnesses);bad[1]['handoff_after']-=1
    controls['early_second_cut'] = rejection(lambda: chronology(word,bad))
    bad=deepcopy(word);bad['events'][witnesses[1]['handoff_after']]=['SCALE',4,'1']
    controls['omitted_cut_normalizer'] = rejection(lambda: chronology(bad,witnesses))
    bad=deepcopy(bill);bad['paid'][1]-=1;bad['paid'][2]+=1
    controls['same_count_wrong_mass'] = rejection(lambda: compare_invoice(bad,expected['complete_cost']))
    bad=deepcopy(bill);bad['paid'][1]-=1;bad['paid'][3]-=1;bad['paid'][2]+=2
    require(sum(bad['paid'].values())==bill['paid_calls'] and sum(r*n for r,n in bad['paid'].items())==bill['paid_mass'], 'moment mutant preserves both count and mass')
    controls['same_count_and_mass_wrong_histogram'] = rejection(lambda: compare_invoice(bad,expected['complete_cost']))
    bad=deepcopy(native);first=next(e for e in bad['program'] if e[0]=='MOVE');first[2]=first[3]
    controls['wrong_native_chronological_chart'] = rejection(lambda: native_ledger(bad))
    return {'status':'PASS_INDEPENDENT_PR6726_PHYSICAL_INVOICE','source_head':pins['source_head'],
            'physical':{k:v for k,v in phys.items() if k!='idle_records'},
            'native':{k:v for k,v in local.items() if k not in ('helper_labels','paid_records')},
            'allocation':{k:v for k,v in fields.items() if k!='helper_jobs'},'invoice':bill,'cuts':cuts,
            'ordinary':work,'canonical_job_adapters':adapters,'central_normalization':central_normalization(),'controls':controls,'caller_gates':len(word['events']),
            'caller_opcode_counts':Counter(e[0] for e in word['events']),
            'assumptions':['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
            'limits':'Finite independent contact/phase, native chart/scalar-row, ownership allocation and complete invoice audit. Scalar caller endpoint theorem, general native physical adapters, all-column tensor contract, compiler and outer transfer are retained dependencies; no new kappa, admission or all-size discharge.'}


if __name__ == '__main__':
    require(sys.argv[1:] in ([],['--write']), 'only --write is supported')
    result=run()
    raw=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if sys.argv[1:]:
        (HERE/'RESULT.json').write_text(raw)
    else:
        require((HERE/'RESULT.json').read_text()==raw,'frozen independent receipt')
    print(result['status'],flush=True)
