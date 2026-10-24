"""Exact corroboration of a projection matching obstruction, stdlib only."""
from collections import Counter, defaultdict
from itertools import combinations
import json

WORD = '341236425430103051216402'
MATCHING = [(22,24),(86,30),(122,70),(123,0),(121,66),(83,113),
            (87,98),(85,8),(21,81),(5,26),(4,114)]
VERTEX_COVER = {24,26,66,81,83,85,86,87,70,114,123}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def prefixes(word):
    out=[]; q=0
    for a in word:
        out.append(q); q ^= 1 << int(a)
    need(q == 0, 'word must restore')
    return out

def differences(points):
    return {a ^ b for a in points for b in points}

def representations(points):
    r=defaultdict(list)
    for a,b in combinations(sorted(points),2):
        r[a ^ b].append((a,b))
    return r

def check_matching(points, matching):
    r=representations(points); used=set()
    for a,b in matching:
        need(a in points and b in points and a!=b,'invalid endpoint')
        need(a not in used and b not in used,'not a matching')
        need(r[a ^ b] == [tuple(sorted((a,b)))], 'difference is not unique')
        used.update((a,b))
    return len(matching)

def lift_criterion(P,n):
    mask=(1<<n)-1
    Q={x & mask for x in P}
    S={q for q in Q if q in P and q+(1<<n) in P}
    need(len(P)==len(Q)+len(S),'fiber cardinality')
    if not S:
        return False,Q,S
    R=representations(Q)
    for d in range(1,1<<n):
        pairs=R[d]
        if any(a in S or b in S for a,b in pairs):
            continue
        colors={((0 if a in P else 1) ^ (0 if b in P else 1)) for a,b in pairs}
        if colors!={0,1}:
            return False,Q,S
    return True,Q,S

def rejected(fn):
    try:
        fn()
    except ValueError:
        return 1
    raise ValueError('negative control accepted')

def main():
    Q=set(prefixes(WORD))
    need(len(WORD)==24 and len(Q)==24,'simple projected word')
    need(sorted(Counter(WORD).values())==[2,2,4,4,4,4,4],'counts')
    need(differences(Q)==set(range(128)),'seven-source universal')
    k=check_matching(Q,MATCHING)
    need(k==11,'matching size')
    need(len(VERTEX_COVER)==11 and all(a in VERTEX_COVER or b in VERTEX_COVER
         for pairs in representations(Q).values() if len(pairs)==1
         for a,b in pairs),'matching cover dual certificate')
    gray=[i^(i>>1) for i in range(16)]+[0]
    half=[(a^b).bit_length()-1 for a,b in zip(gray,gray[1:])]
    upper=half+[i+4 for i in half]
    need(len(upper)==32 and differences(prefixes(upper))==set(range(256)),
         'known 32-step upper construction')
    near='5643251350361472024502071341'
    near_states=prefixes(near); near_differences=differences(near_states)
    intervals={0}
    for i in range(len(near)):
        d=0
        for c in near[i:]:
            d^=1<<int(c); intervals.add(d)
    need(intervals==near_differences,'independent interval oracle')
    need(len(near)==28 and sorted(Counter(near).values())==[2,2,4,4,4,4,4,4],
         '28-step sample counts')
    need(len(near_differences)==246,'sample is not universal')
    domain=valid=0
    for n in range(1,4):
        ambient=1<<(n+1)
        for bits in range(1,1<<ambient):
            P={x for x in range(ambient) if bits>>x&1}
            pred,Q0,S=lift_criterion(P,n)
            actual=differences(P)==set(range(ambient))
            need(pred==actual,'exact static lifting equivalence')
            if actual:
                valid+=1
                for pairs in representations(Q0).values():
                    if len(pairs)==1:
                        a,b=pairs[0]
                        need(a in S or b in S,'unique-edge cover')
            domain+=1
    # A repeated projected state may split without a new-coordinate call at
    # that state. Therefore |S| <= number of new-coordinate calls is false.
    repeated='2010120101'
    P=set(prefixes(repeated)); _,Q0,S=lift_criterion(P,2)
    need(len(S)==4 and repeated.count('2')==2,'revisit counterexample')
    controls=0
    controls+=rejected(lambda:check_matching(Q,[(0,8)]))
    controls+=rejected(lambda:check_matching(Q,[MATCHING[0],MATCHING[0]]))
    controls+=rejected(lambda:check_matching(Q,[(0,127)]))
    controls+=rejected(lambda:need(len(S)<=repeated.count('2'),'false split bound'))
    need(not lift_criterion({0,1,2,3},2)[0],'one-layer negative fixture')
    print(json.dumps({
        'status':'PASS_PROJECTION_MATCHING_OBSTRUCTION',
        'word':WORD,'distinct_projected_states':len(Q),'coverage':128,
        'unique_difference_matching':MATCHING,
        'matching_size':k,'lifted_state_lower_bound':len(Q)+k,
        'minimum_vertex_cover_size':len(VERTEX_COVER),
        'closed_lift_word_length_lower_bound':2*((len(Q)+k+1)//2),
        'exhaustive_small_lift_subsets':domain,'universal_small_lifts':valid,
        'rejected_controls':controls,
        'known_universal_upper_word':''.join(map(str,upper)),
        'nonuniversal_28_word':near,
        'nonuniversal_28_missing_masks':sorted(set(range(256))-near_differences),
        'scope':'General written matching lemma and one fixed-projection exclusion; f(8) remains unresolved.'
    },indent=2))

if __name__=='__main__':
    main()
