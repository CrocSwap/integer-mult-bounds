"""Compute exact signed defect transfers and check them in reverse order.

The forward/reverse method credits the selected-word analysis in PR6526.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt


def need(ok, label):
    if not ok:
        raise ValueError(label)


def add(row, other, q):
    for j, v in other.items():
        z = row.get(j, Q(0))+q*v
        if z:
            row[j] = z
        else:
            row.pop(j,None)


def digest(row):
    return sha256(''.join(f'{j}:{v};' for j,v in sorted(row.items())).encode()).hexdigest()


def noise_weight(e, rank):
    if e[0] == 'MOVE':
        return rank, 0
    if e[0] in {'ADD','SCALE'} and Q(e[-2]).denominator > 1:
        return 0, 1
    return 0, 0


def score(row, weights):
    out = [Q(0)]*4
    for j,c in row.items():
        m,s = weights[j]
        out = [a+b for a,b in zip(out,(c*c*m,c*c*s,abs(c)*m,abs(c)*s))]
    return out


def reverse(word, weights, cut, role):
    row, errors = {role:Q(1)}, {}
    for j in reversed(range(cut)):
        e = word['program'][j]
        op,r = e[:2]
        c = row.get(r,Q(0))
        if c and any(weights[j]):
            errors[j] = c
        if op in {'INIT','CLEAR'}:
            row.pop(r,None)
        elif op == 'SCALE' and c:
            row[r] = c*Q(e[-2])
        elif op in {'ADD','COPY'}:
            if c:
                add(row,{e[2]:c},Q(e[-2]))
            if op == 'COPY':
                row.pop(r,None)
    return row, errors


def analyze(word, ranks):
    public = word['public']
    count = public+word['owned_fields']
    rows = [{} for _ in range(count)]
    ideal = [{r:Q(1)} if r<public else {} for r in range(count)]
    scores = [[Q(0)]*4 for _ in range(count)]
    weights = [noise_weight(e,r) for e,r in zip(word['program'],ranks)]
    frames = list(word['initial'])+[None]*word['owned_fields']
    live = set()
    peaks = [[Q(0),0,0] for _ in range(7)]
    ideal_peak = [Q(1),0,0]
    erasures = []
    scalar_seed_bits = scale_residue_units = 0
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':
            need(frames[r]==e[2] and bool(e[4])==(r in live), 'MOVE frame/owner')
            frames[r] = e[3]
        elif op in {'INIT','CLEAR'}:
            if op == 'INIT':
                need(r>=public and r not in live and frames[r] is None, 'INIT')
                live.add(r)
                frames[r] = e[2]
            else:
                need(r in live and frames[r]==e[2], 'CLEAR')
                erasures.append([j,r,sum(map(abs,ideal[r].values()),Q(0))])
                live.remove(r)
                frames[r] = None
            rows[r],ideal[r],scores[r] = {},{},[Q(0)]*4
        else:
            need(op in {'ADD','COPY','SCALE'}, 'opcode')
            q=Q(e[-2])
            need(q and q.denominator & (q.denominator-1)==0 and frames[r]==e[-1], 'scalar ABI')
            bits=q.denominator.bit_length()-1
            scalar_seed_bits += bits
            if op == 'SCALE':
                need(abs(q.numerator)==1 or q.denominator==1, 'division numerator')
                scale_residue_units += bits
                rows[r] = {k:q*v for k,v in rows[r].items()}
                ideal[r] = {k:q*v for k,v in ideal[r].items()}
                scores[r] = [v*(q*q if k<2 else abs(q)) for k,v in enumerate(scores[r])]
            else:
                s=e[2]
                need(s!=r and frames[s]==frames[r], 'scalar operands')
                if op=='COPY':
                    need(r in live and not ideal[r] and q==1, 'selected COPY')
                    rows[r],ideal[r],scores[r] = rows[s].copy(),ideal[s].copy(),scores[s].copy()
                else:
                    add(ideal[r],ideal[s],q)
                    for k,v in rows[s].items():
                        old=rows[r].get(k,Q(0));new=old+q*v
                        m,sweight=weights[k]
                        delta=(new*new-old*old,abs(new)-abs(old))
                        scores[r]=[a+b for a,b in zip(scores[r],(delta[0]*m,delta[0]*sweight,delta[1]*m,delta[1]*sweight))]
                        if new:
                            rows[r][k]=new
                        else:
                            rows[r].pop(k,None)
        if any(weights[j]):
            rows[r][j]=Q(1)
            m,s=weights[j]
            scores[r]=[a+b for a,b in zip(scores[r],(m,s,m,s))]
        norm=sum(map(abs,ideal[r].values()),Q(0))
        if norm>ideal_peak[0]:
            ideal_peak=[norm,j+1,r]
        m,s,am,ass=scores[r]
        for k,v in enumerate((m,s,am,ass,m+s,m+4*s,am+2*ass)):
            if v>peaks[k][0]:
                peaks[k]=[v,j+1,r]
    need(not live and frames[:public]==word['final'], 'all final frames')
    for r in range(count):
        target={r:Q(1)} if r<public else {}
        if r-112 in word['live']:
            target[r-112]=Q(1)
        need(ideal[r]==target,'complete ideal endpoint')
    # One reverse sweep carries all final observables through transposed events.
    columns=[{r:Q(1)} for r in range(count)]
    back=[{} for _ in range(count)]
    for j in reversed(range(len(word['program']))):
        e=word['program'][j];op,r=e[:2]
        if any(weights[j]):
            for output,c in columns[r].items():
                back[output][j]=c
        if op in {'INIT','CLEAR'}:
            columns[r]={}
        elif op=='SCALE':
            columns[r]={k:Q(e[-2])*v for k,v in columns[r].items()}
        elif op in {'ADD','COPY'}:
            add(columns[e[2]],columns[r],Q(e[-2]))
            if op=='COPY':
                columns[r]={}
    need(back==rows,'every final coefficient: forward versus transposed sweep')
    need([score(row,weights) for row in back]==scores,'all final weighted sums')
    peak_checks=[]
    for index,(value,cut,role) in enumerate(peaks):
        initial,noise=reverse(word,weights,cut,role)
        values=score(noise,weights);m,s,am,ass=values
        peak_checks.append([cut,role,digest(noise)])
        need(value == (values+[m+s,m+4*s,am+2*ass])[index], 'reverse peak certificate')
    return {'opcodes':dict(Counter(e[0] for e in word['program'])),
            'noise_events':sum(any(w) for w in weights),'peak_order':['M','S','AM','AS','M+S','M+4S','AM+2AS'],
            'prefix_peaks':peaks,'final_scores':scores,'final_coefficient_sha256':[digest(r) for r in rows],
            'reverse_peak_checks':peak_checks,'ideal_peak':ideal_peak,'erasures':erasures,
            'native_seed_bits_per_tensor_axis':sum(ranks),'scalar_seed_bits':scalar_seed_bits,
            'division_residue_bits_per_complex_coordinate':2*scale_residue_units},weights


def tail_certificate(peaks):
    q=peaks[5][0]
    rms=next(g for g in range(32) if peaks[4][0] < 2*(1 << (2*g)))
    for g in range(32):
        x=Q(1 << (2*g),q)
        term=lower=Q(1)
        for k in range(1,65):
            term*=x/k
            lower+=term
        if lower > 45606*(1 << 40):
            need(Q(1 << 32,512*q) >= x, 'binary grid tail follows from exact exponential bound')
            return {'normalized_width_one_rms_guard':rms,'normalized_width_one_tail_guard':g,
                    'tail_exponent':x,'positive_taylor_degree':64,'positive_taylor_lower':lower,
                    'failure_bound':'2^-40','union_changed_fields':22803,
                    'width_one_binary_grid_rms_bits':next(t for t in range(32) if 256*peaks[4][0] < (1 << (2*t))),
                    'width_one_binary_grid_tail_bits':16,
                    'width_one_binary_grid_tail_exponent':Q(1 << 32,512*q)}
    raise ValueError('tail certificate range')
