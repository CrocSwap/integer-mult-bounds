#!/usr/bin/env python3
"""Check the global Gaussian rounder and finite Hall witnesses.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def ring_point(r, index):
    side, offset = divmod(index % (4*r), r)
    if side == 0:
        return r-2*offset, r
    if side == 1:
        return -r, r-2*offset
    if side == 2:
        return -r+2*offset, -r
    return r, -r+2*offset


def partner(point):
    """Use doubled odd coordinates on one square ring."""
    x, y = point
    require(x % 2 == y % 2 == 1, 'half-grid domain')
    r = max(abs(x), abs(y))
    if y == r and x > -r:
        index = (r-x)//2
    elif x == -r and y > -r:
        index = r+(r-y)//2
    elif y == -r and x < r:
        index = 2*r+(x+r)//2
    else:
        index = 3*r+(y+r)//2
    return ring_point(r, index ^ 1)


def rotate(point, sign):
    x, y = point
    return -sign*y, sign*x


def round_pair(value, sign=1):
    """Return the positive rounder or its explicit inverse."""
    require(sign in (-1, 1), 'provider sign')
    a, b, c, d = value
    sx, sy, dx, dy = a+c, b+d, a-c, b-d
    if (sx-sy) % 2 == 0:
        ex, ey = rotate((dx, dy), sign)
    elif sign == 1:
        px, py = partner((dx-dy, -dx-dy))
        ex, ey = (px+py)//2, (px-py)//2
    else:
        px, py = partner((dx+dy, dx-dy))
        ex, ey = (px-py)//2, -(px+py)//2
    require((sx-ex) % 2 == (sy-ey) % 2 == 0, 'output parity')
    return (sx+ex)//2, (sy+ey)//2, (sx-ex)//2, (sy-ey)//2


def norm(value):
    return sum(x*x for x in value)


def below_limit(a, b):
    """Decide abs(sqrt(b)-sqrt(a)) < 1/sqrt(2) exactly."""
    a, b = sorted((a, b))
    difference = b-a
    return difference == 0 or (2*difference-1)**2 < 8*a


def check_pair(value):
    n = norm(value)
    for sign in (-1, 1):
        out = round_pair(value, sign)
        a, b, c, d = value
        sx, sy = a+c, b+d
        require((out[0]+out[2], out[1]+out[3]) == (sx, sy), 'sum')
        ex, ey = rotate((a-c, b-d), sign)
        twice_ideal = (sx+ex, sy+ey, sx-ex, sy-ey)
        error4 = sum((2*u-v)**2 for u, v in zip(out, twice_ideal))
        require(error4 == (0 if (sx-sy) % 2 == 0 else 4), 'direct ideal error')
        require(round_pair(out, -sign) == value, 'two-sided inverse')
        require(below_limit(n, norm(out)), 'strict radial bound')
        swapped = value[2:]+value[:2]
        require(round_pair(swapped, sign) == out[2:]+out[:2], 'swap covariance')
        shifted = (a+3, b-2, c+3, d-2)
        require(round_pair(shifted, sign) == (out[0]+3, out[1]-2, out[2]+3, out[3]-2), 'common translation')
    return (sx % 2, sy % 2)


def color(point):
    return ((point[0]+point[1])//2) % 2


def neighbors(point):
    x, y = point
    return {(x-2,y), (x+2,y), (x,y-2), (x,y+2)}


def half_norm(point):
    """Return the pair squared norm at sum one."""
    x, y = point
    require((x*x+y*y+2) % 4 == 0, 'half norm parity')
    return (x*x+y*y+2)//4


def gap_le_rational(a, b, p, q):
    difference = (b-a)*q*q-p*p
    return difference <= 0 or difference*difference <= 4*a*p*p*q*q


def hall_square(r):
    points = {(x,y) for x in range(-r, r+1, 2) for y in range(-r, r+1, 2)}
    source = {z for z in points if color(z) == 0}
    target = points-source
    corners = {z for z in target if abs(z[0]) == abs(z[1]) == r}
    # A boundary step has radial jump above 1/sqrt(2). Both target corners
    # need the stated inward step. These exact facts prove the exclusion.
    low = (r*r+(r-2)**2+2)//4
    high = (2*r*r+2)//4
    require(len(source) == len(target) == (r+1)**2//2, 'square color counts')
    require(len(corners) == 2 and below_limit(low,high), 'corner threshold')
    internal = set()
    boundary = 0
    for u in source:
        for v in neighbors(u):
            if v not in points:
                require(not below_limit(half_norm(u),half_norm(v)), 'outward boundary')
                require(half_norm(v)>half_norm(u), 'boundary direction')
                boundary += 1
            elif v in corners:
                require((half_norm(u),half_norm(v)) == (low,high), 'corner edge cost')
            else:
                internal.add(v)
    require(internal == target-corners, 'remaining neighbors')
    return {'r_doubled':r,'sources':len(source),'remaining_targets':len(internal),
            'corner_gap_squared_norms':[low,high],'boundary_edges':boundary}


def verify():
    ring_count = 129
    points_checked = 0
    fingerprint = hashlib.sha256()
    for k in range(ring_count):
        r=2*k+1
        # Build the cycle by four directed walks, separate from ring_point.
        cycle=[]
        x,y=r,r
        for dx,dy in [(-2,0),(0,-2),(2,0),(0,2)]:
            for _ in range(r):
                cycle.append((x,y));x+=dx;y+=dy
        require((x,y)==(r,r) and len(set(cycle))==4*r,'cycle partition')
        actual={(a,b) for a in range(-r,r+1,2) for b in range(-r,r+1,2)
                if max(abs(a),abs(b))==r}
        require(set(cycle)==actual,'complete ring')
        for index,u in enumerate(cycle):
            v=partner(u)
            require(v==cycle[index ^ 1] and v in neighbors(u), 'consecutive pairing')
            require(partner(v)==u and color(v)!=color(u), 'matching involution')
            require(partner((-u[0],-u[1]))==(-v[0],-v[1]), 'odd matching')
            require(below_limit(half_norm(u),half_norm(v)), 'ring radial bound')
            fingerprint.update(f'{u}:{v};'.encode())
            points_checked+=1
    parity=Counter()
    for value in product(range(-5,6),repeat=4):
        parity[check_pair(value)]+=1
    large=[]
    for bits in [16,64,256,1024,4096]:
        n=2**bits+7
        for signs in product((-1,1),repeat=2):
            for value in [(signs[0]*n,signs[1]*(n-1),0,0),
                          (signs[0]*n,signs[1]*n,1,-2),
                          (n,n-1,-n,2-n),(n,0,1-n,0)]:
                check_pair(value);large.append(bits)
    sequence_values = list(range(1,65)) + [2**b+7 for b in [16,64,256,1024,4096]]
    for k in sequence_values:
        require(round_pair((0,-k,1,k))==(k+1,0,-k,0), 'forward sharpness sequence')
        require(round_pair((1,-k,0,k),-1)==(-k,0,k+1,0), 'inverse sharpness sequence')
        require(norm((0,-k,1,k))==2*k*k+1 and norm((k+1,0,-k,0))==2*k*k+2*k+1, 'sharpness norms')
    halls=[hall_square(r) for r in range(3,66,2)]
    # A separate neighbor census tests the Hall deficit at rational slacks.
    rational=[]
    for p,q,r in [(1,2,3),(3,5,5),(7,10,65),(707,1000,4097)]:
        low=(r*r+(r-2)**2+2)//4;high=(2*r*r+2)//4
        require(not gap_le_rational(low,high,p,q),'Hall gap exceeds trial slack')
        if r<=65:
            source={(x,y) for x in range(-r,r+1,2) for y in range(-r,r+1,2) if color((x,y))==0}
            targets=set().union(*({v for v in neighbors(u) if gap_le_rational(half_norm(u),half_norm(v),p,q)} for u in source))
            require(len(targets)<len(source),'direct Hall deficit')
            rational.append([p,q,r,len(source),len(targets)])
        else:
            rational.append([p,q,r,'symbolic corner and boundary counts'])
    controls=[]
    for value in [(0,1),(2,2)]:
        try:partner(value)
        except ValueError:controls.append('non-half-grid '+str(value))
        else:raise ValueError('domain control accepted')
    try:round_pair((1,0,0,0),0)
    except ValueError:controls.append('invalid provider sign')
    else:raise ValueError('sign control accepted')
    # The exact square and phase identities are not properties of this map.
    faults={}
    for value in product(range(-2,3),repeat=4):
        out=round_pair(value)
        if 'square_to_swap' not in faults and round_pair(out)!=value[2:]+value[:2]:
            faults['square_to_swap']=[value,out,round_pair(out)]
        phase=(-value[1],value[0],-value[3],value[2])
        phased_out=(-out[1],out[0],-out[3],out[2])
        if 'phase_covariance' not in faults and round_pair(phase)!=phased_out:
            faults['phase_covariance']=[value,round_pair(phase),phased_out]
    require(len(faults)==2,'excluded identity controls')
    # Zero slack fails even though same-ring pairing preserves max norm.
    witness=next(value for value in product(range(-2,3),repeat=4)
                 if norm(round_pair(value))>norm(value))
    controls.append('zero radial slack: '+str(witness))
    result={'status':'PASS_GAUSSIAN_EXACT_SUM_GLOBAL_OPTIMUM',
            'theorem':'global forward optimum 1/sqrt(2); explicit bijection has the same bilateral and inverse suprema',
            'complete_rings':ring_count,'half_grid_points':points_checked,
            'pair_cube':[-5,5],'pair_inputs':sum(parity.values()),
            'sum_parities':{str(k):v for k,v in sorted(parity.items())},
            'large_inputs':len(large),'largest_input_bits':4097,
            'sharpness_sequence_indices':len(sequence_values),
            'hall_squares':halls,'rational_hall_checks':rational,
            'ring_pairing_sha256':fingerprint.hexdigest(),
            'fault_controls':controls,'excluded_identity_witnesses':faults}
    return json.loads(json.dumps(result))


if __name__=='__main__':
    result=verify()
    require(result==json.loads((ROOT/'RESULT.json').read_text()),'retained receipt differs')
    print(json.dumps(result,indent=2,sort_keys=True))
