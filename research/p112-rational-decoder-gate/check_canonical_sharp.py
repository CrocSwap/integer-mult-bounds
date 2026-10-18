#!/usr/bin/env python3
"""Read-only exact premises and affine combination for C>=334+2s.

Explicit vector-set spaces and annihilators independently replay the existing
echelon-based closure. The universal rank argument is in the accompanying proof.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import argparse,hashlib,json,math,tarfile

CANDIDATE='dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
ARCHIVE='f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
PAYLOAD='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
MEMBER='candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'

def need(condition,message):
    if not condition:raise ValueError(message)

def strict_pairs(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,'duplicate JSON key')
        result[key]=value
    return result

def parse(raw):return json.loads(raw,object_pairs_hook=strict_pairs)
def dot(x,y):return (x&y).bit_count()&1
def space(vectors):
    result={0}
    for v in vectors:result|={x^v for x in result}
    return frozenset(result)
def join(a,b):return frozenset(x^y for x in a for y in b)
def dimension(a):
    need(len(a)>0 and len(a)&(len(a)-1)==0,'space cardinality')
    return len(a).bit_length()-1
def annihilator(a):return frozenset(x for x in range(512) if all(not dot(x,y) for y in a))
def rejects(callback,label):
    try:callback()
    except ValueError:return label
    raise ValueError('mutation accepted: '+label)
def closure_premises(spaces,seeds):
    need(frozenset({0}) in spaces and all(s in spaces for s in seeds),'missing generator')
    need(all(join(a,b) in spaces for a in spaces for b in seeds),'not closed under generators')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);args=parser.parse_args()
    repo=args.repo
    raw=(repo/'research/p112-rational-decoder-gate/CANDIDATE.json').read_bytes().replace(b'\r\n',b'\n')
    need(hashlib.sha256(raw).hexdigest()==CANDIDATE,'candidate LF pin');candidate=parse(raw)
    archive=repo/'research/community-frontier1094-audit/selected-replay.tar.gz'
    need(hashlib.sha256(archive.read_bytes()).hexdigest()==ARCHIVE,'archive pin')
    with tarfile.open(archive) as a:
        member=a.extractfile(MEMBER);need(member is not None,'payload member');raw=member.read()
    need(hashlib.sha256(raw).hexdigest()==PAYLOAD,'payload pin')
    recipes=sorted(parse(raw)['recipes'],key=lambda x:x['port'])
    need([x['port'] for x in recipes]==list(range(112)),'port enumeration')
    q=[x['q'] for x in recipes]
    need(all(type(x) is int and 0<x<512 and dot(x,x)==1 for x in q) and len(set(q))==112,'label typing and distinct odd norms')
    groups=candidate['groups']
    need(len(groups)==38 and list(map(len,groups))==[1]+[3]*37,'group dimensions')
    need(all(type(p) is int for g in groups for p in g) and sorted(p for g in groups for p in g)==list(range(112)),'group partition')
    E=[[q[p] for p in g] for g in groups]
    need(all(dot(x,y)==int(i==j) for g in E for i,x in enumerate(g) for j,y in enumerate(g)),'orthonormal triads')
    H=[space(E[i]+E[i+1]) for i in range(1,37,2)];J=space(E[37]);seeds=H+[J]
    allspaces={frozenset({0})};todo=list(allspaces)
    while todo:
        current=todo.pop()
        for seed in seeds:
            new=join(current,seed)
            if new not in allspaces:allspaces.add(new);todo.append(new)
    need(len(allspaces)==40,'forty-space closure');closure_premises(allspaces,seeds)
    orth={a:annihilator(a) for a in allspaces}
    def rho(a,b):return dimension(a)-dimension(a&orth[b])
    need(all(dimension(h)==6 and rho(h,h)==6 for h in H),'paired ranks')
    need(dimension(J)==3 and rho(J,J)==3,'J rank')
    need(all(rho(J,h)==rho(h,J)==3 for h in H),'pure-J tariff')
    need(all(rho(a,b)>=4 for a in H for b in H),'nonpure tariff floor')
    need(all(rho(join(J,a),join(J,b))>=6 for a in H for b in H),'both-J floor')
    residual=space(E[0]+E[15]+E[16])
    need(dimension(residual)==7 and dimension(residual)-dimension(residual&annihilator(residual))==7,'residual surcharge')
    supports={a:tuple(i for i,h in enumerate(seeds) if h<=a) for a in allspaces}
    full_hist=Counter();ordinary_hist=Counter();table=[]
    for a in allspaces:
        for b in allspaces:
            A=supports[a];B=supports[b];A0=tuple(i for i in A if i<18);B0=tuple(i for i in B if i<18)
            if not A0 or not B0:continue
            r=rho(a,b)
            if r>=6:continue
            need(r in (4,5) and not set(A)&set(B),'low rectangle classes and disjointness')
            full=Fraction(1,math.comb(len(A)+len(B),len(A)))
            ordinary=Fraction(1,math.comb(len(A0)+len(B0),len(A0)))
            need(6-r<=4*full and 6-r<=4*ordinary,'both discount bounds')
            full_hist[(len(A),len(B),r)]+=1;ordinary_hist[(len(A0),len(B0),r)]+=1
            table.append({'left':list(A),'right':list(B),'rank':r,'full_probability':str(full),'ordinary_probability':str(ordinary)})
    expected={(1,1,4):20,(1,1,5):178,(1,2,5):33,(2,1,5):33,(1,3,5):4,(3,1,5):4}
    need(dict(full_hist)==expected,'full low-rectangle census')
    # Coefficients are ordered (m, P, constant). No unbounded numerical scan.
    full_bound=(2,-3,229);ordinary_bound=(2,1,217)
    combined=tuple(Fraction(a,4)+Fraction(3*b,4) for a,b in zip(full_bound,ordinary_bound))
    need(combined==(2,0,220) and 2*57+220==334,'exact convex combination')
    need(Fraction(334)>Fraction(2672,9),'zero-saving allowance')
    derived=next(a for a in allspaces if dimension(a)==8 and a not in seeds)
    controls=[rejects(lambda:closure_premises(allspaces-{H[0]},seeds),'removed paired generator'),
              rejects(lambda:closure_premises(allspaces-{derived},seeds),'removed generated span'),
              rejects(lambda:parse('{"same":1,"same":2}'),'duplicate JSON key')]
    ordered=sorted(table,key=lambda x:(x['left'],x['right'],x['rank']))
    encoded=json.dumps(ordered,sort_keys=True,separators=(',',':')).encode()
    result={'candidate_lf_sha256':CANDIDATE,'archive_sha256':ARCHIVE,'payload_sha256':PAYLOAD,
            'generated_spaces':len(allspaces),'space_dimension_histogram':dict(sorted(Counter(dimension(a) for a in allspaces).items())),
            'full_low_rectangles':{str(k):v for k,v in sorted(full_hist.items())},
            'ordinary_low_rectangles':{str(k):v for k,v in sorted(ordinary_hist.items())},
            'rectangle_count':len(table),'rectangle_table_sha256':hashlib.sha256(encoded).hexdigest(),
            'full_bound_coefficients':full_bound,'ordinary_bound_coefficients':ordinary_bound,
            'combined_bound_coefficients':[int(x) for x in combined],
            'result':'C >= 2m+220 = 334+2s, m=57+s','controls':controls,
            'scope':'Any rank57 fit on the fixed mask with BOTH factor families in its column/row spaces; arbitrary rational coefficients and term count. Exterior factors and larger fitting rank excluded.'}
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
