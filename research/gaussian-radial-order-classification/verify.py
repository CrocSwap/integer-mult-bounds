#!/usr/bin/env python3
"""Check exact ring classifications and the fourth-power obstruction.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
from math import gcd,isqrt
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent
SCALE=10**24
LOW=isqrt(19*SCALE*SCALE)-isqrt(13*SCALE*SCALE)-1
HIGH=LOW+3


def need(value,message):
    if not value:raise ValueError(message)


def color(point):return ((point[0]+point[1])//2)%2

def neighbors(point):
    x,y=point
    return {(x-2,y),(x+2,y),(x,y-2),(x,y+2)}


def norm(point):return (point[0]*point[0]+point[1]*point[1]+2)//4

def at_most_rho(a,b):
    difference=b-a
    return difference<=0 or (2*difference-1)**2<=8*a


def gap_le(a,b,p,q):
    remainder=(b-a)*q*q-p*p
    return remainder<=0 or remainder*remainder<=4*a*p*p*q*q


def beta_category(a,b):
    if (a,b)==(13,19):return 0
    if gap_le(a,b,LOW,SCALE):return -1
    need(not gap_le(a,b,HIGH,SCALE),'Unresolved beta comparison')
    return 1


def cycle(r):
    points=[];x=y=r
    for dx,dy in [(-2,0),(0,-2),(2,0),(0,2)]:
        for _ in range(r):points.append((x,y));x+=dx;y+=dy
    need((x,y)==(r,r) and len(set(points))==4*r,'Complete ring walk')
    return points


def matchings(points):
    target={z for z in points if color(z)==1}
    source=[z for z in points if color(z)==0]
    edges={z:sorted(neighbors(z)&target) for z in source}
    need(all(len(v)==2 for v in edges.values()),'Ring degree two')
    found=[]
    def visit(index,used,mapping):
        if index==len(source):
            found.append(dict(mapping));return
        u=source[index]
        for v in edges[u]:
            if v not in used:
                used.add(v);mapping[u]=v;visit(index+1,used,mapping);used.remove(v);del mapping[u]
    visit(0,set(),{})
    return found


def cycles(mapping):
    need(set(mapping)==set(mapping.values()) and len(mapping)==len(set(mapping.values())),'Permutation coverage')
    seen=set();sizes=[]
    for u in sorted(mapping):
        if u in seen:continue
        current=u;length=0
        while current not in seen:
            seen.add(current);length+=1;current=mapping[current]
        need(current==u,'Closed orbit');sizes.append(length)
    return sorted(sizes)


def source_pair(t):
    x,y=t
    return ((2+x-y)//4,-(x+y)//4,(2-x+y)//4,(x+y)//4)


def target_pair(u):
    x,y=u
    return ((2+x+y)//4,(x-y)//4,(2-x-y)//4,(-x+y)//4)


def direct_error(source,target):
    a,b,c,d=source;sx,sy=a+c,b+d;dx,dy=a-c,b-d
    ideal2=(sx-dy,sy+dx,sx+dy,sy-dx)
    need((target[0]+target[2],target[1]+target[3])==(sx,sy)==(1,0),'Exact sum')
    return sum((2*a-b)**2 for a,b in zip(target,ideal2))


def verify():
    ring_rows=[];boundary_edges=0;digest=hashlib.sha256();critical=None
    for r in range(1,66,2):
        points=cycle(r);index={z:j for j,z in enumerate(points)}
        square={(x,y) for x in range(-r,r+1,2) for y in range(-r,r+1,2)}
        a={z for z in square if color(z)==0};b=square-a
        need(len(a)==len(b)==(r+1)**2//2,'Equal square capacities')
        for u in a:
            for v in neighbors(u)-square:
                need(norm(v)>norm(u) and not at_most_rho(norm(u),norm(v)),'Every exterior edge costs more than rho')
                need(direct_error(source_pair(u),target_pair(v))==4,'Direct exterior Gaussian error')
                boundary_edges+=1
        ms=matchings(points);need(len(ms)==2,'Exactly two complete ring matchings')
        periods=[];records=[]
        for matching in ms:
            g={u:(v[1],-v[0]) for u,v in matching.items()}
            lengths=cycles(g);periods.append(lengths[0])
            need(len(set(lengths))==1,'Uniform ring periods')
            shifts={(index[g[u]]-index[u])%(4*r) for u in g}
            need(len(shifts)==1 and shifts <= {(1-r)%(4*r),(-1-r)%(4*r)},'Forced Gaussian shift')
            step=next(iter(shifts))//2;expected=2*r//gcd(2*r,step)
            need(lengths[0]==expected,'Independent cycle and gcd orders')
            rows=[]
            for u,v in sorted(matching.items()):
                source,target=source_pair(u),target_pair(v)
                need(direct_error(source,target)==4,'Direct ring Gaussian error')
                need(at_most_rho(norm(u),norm(v)),'Ring radial bound')
                rows.append([source,target]);digest.update(f'{u}:{v};'.encode())
            records.append({'cycles':lengths,'map':rows})
        need(sorted(periods)==[r,2*r],'Both possible exact orders')
        ring_rows.append({'r_doubled':r,'source_points':2*r,'matching_count':2,'orders':sorted(periods)})
        if r==5:critical=records
    need(critical is not None,'Critical ring')
    critical_boundaries=[]
    for r in [3,5]:
        square={(x,y) for x in range(-r,r+1,2) for y in range(-r,r+1,2)}
        edges=[]
        for u in sorted(z for z in square if color(z)==0):
            for v in sorted(neighbors(u)-square):
                category=beta_category(norm(u),norm(v))
                need(category>=0,'Square is closed below beta')
                edges.append({'source':u,'target':v,'squared_norms':[norm(u),norm(v)],'beta_category':category})
        critical_boundaries.append({'r_doubled':r,'source_points':(r+1)**2//2,'exterior_edges':edges})
    need(all(row['orders']==[5,10] for row in ring_rows if row['r_doubled']==5),'No fourth-power matching')
    need(2237**2>5*1000**2 and 4359**2>19*1000**2 and 3605**2<13*1000**2,'Exact strict boundary separation')
    finite_order=[]
    for m in range(4,65,4):
        r=2*m+1;a=(r*r+1)//2;b=(r*r+2*r+3)//2
        need(not at_most_rho(a,b),'Positive finite-order gap')
        orders=sorted(2*r//gcd(2*r,(sign-r)//2) for sign in [-1,1])
        need(orders==[r,2*r] and all(m%order for order in orders),'Large ring defeats prescribed finite order')
        finite_order.append({'order':m,'r_doubled':r,'gap_squared_norms':[a,b],'ring_orders':orders})
    # The known source four-cycle attains beta and crosses the critical ring.
    upper_cycle=[(3,0,-2,0),(0,3,1,-3),(-2,0,3,0),(1,-3,0,3)]
    for a,b in zip(upper_cycle,upper_cycle[1:]+upper_cycle[:1]):
        need(direct_error(a,b)==4,'Retained attaining cycle error')
        need(beta_category(sum(x*x for x in a),sum(x*x for x in b))<=0,'Retained attaining cycle radial cost')
    need([sum(x*x for x in z) for z in upper_cycle]==[13,19,13,19],'Attaining squared norms')
    bad={z:(0,0) for z in [(1,-1),(-1,1)]}
    try:cycles(bad)
    except ValueError:pass
    else:raise ValueError('Collision control accepted')
    need(not at_most_rho(1,3),'Outward central edge is not rho-admissible')
    need(beta_category(13,19)==0,'Strict-boundary control')
    result={'status':'PASS_GAUSSIAN_RADIAL_ORDER_CLASSIFICATION','claim':'Every optimal sum-one map has ring orders R or 2R; no finite global order; sharp fourth-power slack sqrt(19)-sqrt(13)',
            'complete_ring_domains':ring_rows,'ring_classifications':len(ring_rows),'ring_matchings':2*len(ring_rows),'exterior_edges':boundary_edges,'ring_maps_sha256':digest.hexdigest(),
            'critical_ring_maps':critical,'critical_square_boundaries':critical_boundaries,'finite_order_gap_checks':finite_order,'beta_bracket':[LOW,HIGH,SCALE],
            'retained_attaining_four_cycle':upper_cycle,'upper_proof_source':'CubeJerry PR7570@053c42c68165cf24fd4e8bc33c2b20d6ac3d399b:proof/PROOF.md; full predecessor replay not run',
            'controls':['colliding target map','forbidden outward edge at rho','strict beta boundary; equality is allowed']}
    return json.loads(json.dumps(result))


if __name__=='__main__':
    result=verify();need(result==json.loads((ROOT/'RESULT.json').read_text()),'Retained receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
