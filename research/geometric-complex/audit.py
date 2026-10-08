"""Audit complete physical invocation paths and their complex phases.

Unlike the side-DAG checks, this follows data and center roles through the
entire schedule, in both orientations and all three tensor stages. Binary
phase identities are compared exhaustively at the small ground sizes.
"""
from functools import lru_cache

from explore import Circuit
from verify import bits, projector, product, rank

PHASE_ADDRESSES = 0


def dot(a, b):
    return (a & b).bit_count() & 1


def independent(vectors):
    pivots = {}
    basis = []
    for original in vectors:
        v = original
        while v:
            p = v.bit_length()-1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                basis.append(original)
                break
    return basis


def orthonormal_basis(rows):
    """Construct a binary orthonormal basis, including alternating-plane absorption."""
    remaining = independent(rows)
    answer = []
    while remaining:
        unit = next((i for i,v in enumerate(remaining) if dot(v,v)), None)
        if unit is not None:
            w = remaining.pop(unit)
            answer.append(w)
            remaining = [v ^ (w if dot(v,w) else 0) for v in remaining]
            continue
        # A nonzero alternating remainder has a nondegenerate hyperbolic plane.
        assert answer, 'Alternating space has no orthonormal basis'
        a = remaining.pop(0)
        partner = next(i for i,v in enumerate(remaining) if dot(a,v))
        b = remaining.pop(partner)
        remaining = [v ^ (a if dot(v,b) else 0) ^ (b if dot(v,a) else 0)
                     for v in remaining]
        w = answer.pop()
        answer.extend((w ^ a, w ^ b, w ^ a ^ b))
    assert len(answer) == rank(rows)
    for i,a in enumerate(answer):
        for j,b in enumerate(answer):
            assert dot(a,b) == (i == j)
    return tuple(answer)


def apply(rows, x):
    return sum(dot(row,x) << i for i,row in enumerate(rows))


@lru_cache(maxsize=None)
def transition(tail, head):
    """Return signed rank; compare the full diagonal phase at every address."""
    global PHASE_ADDRESSES
    if tail == head:
        return 0, 0
    if product(tail,head) == tail == product(head,tail):
        smaller, larger, sign = tail, head, 1
    else:
        assert product(tail,head) == head == product(head,tail)
        smaller, larger, sign = head, tail, -1
    residual = tuple(a ^ b for a,b in zip(smaller,larger))
    assert product(residual,residual) == residual
    basis = orthonormal_basis(residual)
    assert len(basis) == rank(larger)-rank(smaller)
    for x in range(1 << len(tail)):
        actual = (apply(head,x).bit_count()-apply(tail,x).bit_count()) % 4
        factors = sum(sign*(v.bit_count() % 4)*dot(v,x) for v in basis) % 4
        assert actual == factors
        # Each factor has odd weight: its character eigenvalues are 1 and +/-i,
        # exactly those of C_v or its inverse. Fourier conjugation is invertible.
    PHASE_ADDRESSES += 1 << len(tail)
    return sign*len(basis), 1 << len(tail)


def invocation_audit(n, stage, reverse):
    circuits = [Circuit(n,r) for r in ('disjoint','intersection_two')]
    codes = [c.compile() for c in circuits]
    v,h = circuits[0].v,n+1
    m = h**3
    earlier = h**(stage-1)
    zero = (0,)*h
    full = tuple(1 << i for i in range(h))
    comp = lambda p: tuple(a ^ b for a,b in zip(full,p))
    lines = [projector(circuits[0],i) for i in range(v)]
    node_frames = [{z:projector(c,z) for z in c.active} for c in circuits]
    states = [(p,p) for p in lines] + [(p,zero) for p in lines]
    starts = []
    for code in codes:
        starts.append(len(states))
        states.extend([(zero,zero)]*code['roles'])
    centers = tuple(range(len(states),len(states)+h))
    states.extend([(zero,zero)]*h)
    source = v if reverse else 0
    target = 0 if reverse else v
    D0,D1 = (full,zero),(full,full)
    total = decrease = incidences = 0

    def touch(roles, frame, kind):
        nonlocal total,decrease,incidences
        for role in set(roles):
            before = states[role]
            b,_ = transition(before[0],frame[0]) if earlier > 1 else (0,0)
            p,_ = transition(before[1],frame[1])
            signed = (earlier-1)*b+p
            # Both summands must change in the same direction.
            assert b*p >= 0
            total += abs(signed)
            if signed < 0:
                assert kind == 'central'
                decrease -= signed
            states[role] = frame
            incidences += 1

    def mixer(frame=None, inverse=False, complemented=False):
        for c,code,start,ps in zip(circuits,codes,starts,node_frames):
            gates = reversed(code['gates']) if inverse else code['gates']
            for z,ins,outs in gates:
                U = comp(ps[z]) if complemented else ps[z]
                chosen = frame if frame is not None else (full,U)
                touch([start+s for s in ins+outs],chosen,'side')

    def load(frame=None, terminal=False):
        for i in range(v):
            slots = [start+code['sources'][i] for code,start in zip(codes,starts)]
            chosen = frame if frame is not None else (full,comp(lines[i]) if terminal else lines[i])
            touch([source+i]+slots,chosen,'data')

    def inject(frame=None, terminal=False):
        groups = {i:[] for i in range(v)}
        for c,code,start in zip(circuits,codes,starts):
            for key,slot in code['outputs'].items():
                i = key if c.relation == 'disjoint' else key[1]
                groups[i].append(start+slot)
        for i,slots in groups.items():
            chosen = frame if frame is not None else (full,comp(lines[i]) if terminal else lines[i])
            touch([target+i]+slots,chosen,'data')

    def central(bank,frame):
        touch(tuple(range(bank,bank+v))+centers,frame,'central')

    if not reverse:
        mixer(D0);inject(D0);mixer(D0,inverse=True);central(target,D0)
        load();central(source,D1);central(target,D0)
        mixer();inject(terminal=True);mixer(D1,inverse=True)
        central(source,D1);load(D1)
    else:
        load(D0);central(source,D0);mixer(D0);inject()
        mixer(inverse=True,complemented=True);central(target,D1)
        central(source,D0);load(terminal=True);central(target,D1)
        mixer(D1);inject(D1);mixer(D1,inverse=True)
    for i in range(v):
        touch([i],D1,'data')
        touch([v+i],(full,comp(lines[i])),'data')
    scratch = len(states)-2*v
    for role in range(2*v,len(states)):
        touch([role],D1,'side')
        total += m-h**stage  # The full future complement at the global sink.
    expected = scratch*m + 2*v*earlier*(h-1) + 2*h*h
    assert total == expected
    assert decrease == h*h
    return dict(n=n,stage=stage,reverse=reverse,physical_roles=len(states),
                checked_incidences=incidences,rank_sum=total,
                independently_derived_rank_sum=expected,decreasing_dimension=decrease)


def certificate():
    global PHASE_ADDRESSES
    PHASE_ADDRESSES = 0
    transition.cache_clear()
    rows = [invocation_audit(n,j,reverse)
            for n in (6,7) for j in (1,2,3) for reverse in (False,True)]
    # Each cache entry has actually checked all 2^h address phases. Count unique
    # transitions rather than multiplying repeated incidences into this statistic.
    unique = transition.cache_info().currsize
    return dict(invocations=rows,unique_binary_transitions=unique,
                exhaustive_phase_addresses=PHASE_ADDRESSES,
                complete_data_center_side_paths=True,all_three_tensor_stages=True,
                rank_sum_formula_verified=True)

if __name__ == '__main__':
    import json
    print(json.dumps(certificate(),indent=2,sort_keys=True))
