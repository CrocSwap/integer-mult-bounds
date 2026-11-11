"""Exact cochart and source-row gates for the selected BIT sends."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
PIN = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
TARGET = Fraction('0.0040075385047236')


def xor_rows(rows):
    total = 0
    for row in rows:
        total ^= row
    return total


def in_span(values, target):
    basis = {}
    for row in values:
        while row:
            lead = row & -row
            if lead not in basis:
                basis[lead] = row
                break
            row ^= basis[lead]
    while target:
        lead = target & -target
        if lead not in basis:
            return False
        target ^= basis[lead]
    return True


def trace(word):
    n = word['public']
    current = [(f,1 << r) for r,f in enumerate(word['start'])] + [None]*word['owned_fields']
    begins = [0]*len(current)
    spans, touch = defaultdict(list), defaultdict(list)
    moves = {}
    charts = defaultdict(set)

    def set_role(role, state, cut):
        old = current[role]
        if old is not None:
            spans[old[0]].append((begins[role],cut,role,old[1]))
            charts[role].add(old[0])
        current[role] = state
        begins[role] = cut

    for i, (op,a,*args) in enumerate(word['program']):
        touch[a].append(i)
        if op == 'ADD':
            b,f = args
            assert a != b and current[a][0] == current[b][0] == f
            touch[b].append(i)
            set_role(a,(f,current[a][1] ^ current[b][1]),i+1)
        elif op == 'MOVE':
            f,g = args
            assert current[a][0] == f
            row = current[a][1]
            if a < n:
                moves[i] = (a,f,g,row)
            set_role(a,(g,row),i+1)
        elif op == 'SWAP':
            b = args[0]
            touch[b].append(i)
            x,y = current[a],current[b]
            set_role(a,y,i+1)
            set_role(b,x,i+1)
        elif op == 'INIT':
            assert a >= n and current[a] is None
            set_role(a,(args[0],0),i+1)
        else:
            assert op == 'CLEAR' and a >= n and current[a][0] == args[0]
            set_role(a,None,i+1)
    assert n == 659 and len(moves) == 2862
    assert [c[0] for c in current[:n]] == word['final'] and not any(current[n:])
    for i,(_,row) in enumerate(current[:n]):
        expected = (1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0)
        assert row == expected
        set_role(i,None,len(word['program'])+1)
    return spans,touch,moves,charts


def verify(path):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    word = json.loads(gzip.decompress(raw))
    frames = {int(label):frame for label,frame in word['frames'].items()}
    dims = {label:frame['dim'] for label,frame in frames.items()}
    spans,touch,moves,charts = trace(word)
    p = word['program']
    groups = defaultdict(list)
    for owner,times in touch.items():
        if owner >= word['public']:
            continue
        for i,t,j in zip(times,times[1:],times[2:]):
            if i not in moves or j not in moves or p[t][0] != 'ADD' or p[t][2] != owner:
                continue
            a,f,h,row = moves[i]
            aa,hh,g,after = moves[j]
            b = p[t][1]
            assert a == aa == owner and h == hh == p[t][3] and row == after and row
            assert (dims[f],dims[h],dims[g]) == (6,7,8) and g == 1 and b >= word['public']
            assert all(dims[c] in (0,7) for c in charts[b])
            groups[b].append((t,i,j,owner,f,h,g,row))
    assert len(groups) == 120 and {len(v) for v in groups.values()} == {3}
    assert len({move[3] for group in groups.values() for move in group}) == 360
    def same_space(a,b):
        assert dims[a] == dims[b]
        return all(sum(Fraction(x)*Fraction(y) for x,y in zip(ann,vec,strict=True)) == 0
                   for ann in frames[a]['A'] for vec in frames[b]['B'])
    counts = Counter()
    subsets = Counter()
    for b, group in sorted(groups.items()):
        group.sort()
        h, = {v[5] for v in group}
        init,*writes,deadline = touch[b][:5]
        assert p[init] == ['INIT',b,h] and writes == [v[0] for v in group]
        assert not all(same_space(group[0][4],v[4]) for v in group[1:])
        counts['early_spaces_incompatible'] += 1
        if p[deadline][0] == 'MOVE':
            assert p[deadline] == ['MOVE',b,h,0]
            counts['late_summary_descent'] += 1
        else:
            _,c,s,frame = p[deadline]
            assert p[deadline][0] == 'ADD' and s == b and frame == h
            assert len(touch[b]) == 6 and all(dims[k] != 8 for k in charts[c])
            counts['late_consumer_never_full'] += 1
        pool = [(max(lo,init+1),min(hi,deadline+1),r,row) for lo,hi,r,row in spans[h]
                if r != b and lo <= deadline and hi > init+1]
        for n in range(1,4):
            for choice in combinations(group,n):
                release = {r:(i+1,j+1) for _,i,j,r,*_ in choice}
                donors = [row for lo,hi,r,row in pool
                          if r not in release or lo < release[r][0] or hi > release[r][1]]
                cargo = [v[-1] for v in choice]
                target = xor_rows(cargo)
                assert target and not in_span(donors,target)
                assert in_span([*donors,*cargo],target)
                subsets[n] += 1
    assert counts == {'early_spaces_incompatible':120,'late_summary_descent':9,'late_consumer_never_full':111}
    assert subsets == {1:360,2:360,3:120}
    # Three (1,1)->2 fusions save less than 6*kappa, while the late
    # owned rank 8->0 descent costs at least (1-kappa)/8 more.
    assert 6*TARGET < (1-TARGET)/8 and 0 < TARGET < 1
    assert in_span([0b110,0b011],0b101) and not in_span([0b110,0b011],0b100)
    return dict(status='PASS_BIT_SEND_COCHART_GATE', public_endpoint_rows=word['public'],
                sender_triples=360, owned_recipients=120, fixed_route_hits=0,
                rebind=counts, alias_subsets=subsets, alias_positive_controls=840,
                alias_hits=0, target=str(TARGET),dependencies={SOURCE:PIN})


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Use assertions')
    result = verify(HERE.parents[1]/SOURCE)
    assert json.dumps(result,indent=2,sort_keys=True)+'\n' == (HERE/'RECEIPT.json').read_text()
    print(result['status'])
