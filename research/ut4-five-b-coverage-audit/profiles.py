# SPDX-License-Identifier: Apache-2.0
"""Independent 5-b active-profile and gap-cap audit; standard library only.

The profile method is due to Aaron Wang (#1690). Equations and the 5,664-pair
reference count are from steph4n-gh's #2828, building on Petalas and Davidson.
This implementation uses a separate 2+3 join, with no predecessor imports.
"""
from collections import defaultdict, Counter
from itertools import product


def mm(a, b, n=2):
    return sum((sum(((a >> (n*i+k)) & 1) * ((b >> (n*k+j)) & 1)
                    for k in range(n)) % 2) << (n*i+j)
               for i in range(n) for j in range(n))


M = [[mm(a,b) for b in range(16)] for a in range(16)]
XY = {sum(((x >> i) & 1) * ((y >> j) & 1) << (2*i+j)
          for i in range(2) for j in range(2)): (x,y)
      for x in range(1,4) for y in range(1,4)}
RANK = [0 if a == 0 else 1 if a in XY else 2 for a in range(16)]
COUPLINGS = sorted(XY)


def gaps(p):
    return tuple(x ^ y for x,y in zip((0,)+p, p+(0,)))


def key(middle,p):
    result=[0,0,0,0]
    for j,(b,a) in enumerate(zip(middle,p)):
        x,y=XY[b]
        for i in range(2):
            u=sum(((a >> (2*i+k)) & 1)*((x>>k)&1) for k in range(2))%2
            v=sum(((y >> k)&1)*((a>>(2*k+i))&1) for k in range(2))%2
            result[i]|=u<<j
            result[i+2]|=v<<j
    return tuple(result)


def dot(a,b):
    return (a&b).bit_count()%2


def enumerate_profiles(progress=False):
    stats=Counter()
    pairs=[]
    rank_pairs=Counter()
    caps=Counter()
    for mid4 in product(COUPLINGS,repeat=4):
        last=mid4[0]^mid4[1]^mid4[2]^mid4[3]
        if last not in XY:
            continue
        mid=mid4+(last,)
        stats['middles']+=1
        before=0
        tables=[]
        for b in mid:
            after=before^b
            row=[]
            for p in range(16):
                values=(M[p][b],M[b][p],M[M[p][b]][p],M[M[before][p]][b]^M[M[b][p]][after])
                row.append(sum(v<<(4*i) for i,v in enumerate(values)))
            tables.append(row)
            before=after
        t0,t1,t2,t3,t4=tables
        left=defaultdict(list)
        for p0,p1 in product(range(16),repeat=2):
            left[t0[p0]^t1[p1]].append((p0,p1,RANK[p0]+RANK[p0^p1]))
        aa=defaultdict(list)
        cc=defaultdict(list)
        for p2,p3,p4 in product(range(16),repeat=3):
            value=t2[p2]^t3[p3]^t4[p4]
            tail=RANK[p2^p3]+RANK[p3^p4]+RANK[p4]
            if tail>5:
                continue
            for wanted, dest, stat in ((0x8888,aa,'a_pass'),(0,cc,'c_pass')):
                for p0,p1,head in left.get(value^wanted,()):
                    if head+RANK[p1^p2]+tail<=5:
                        stats[stat]+=1
                        p=(p0,p1,p2,p3,p4)
                        k=key(mid,p)
                        if k[0] and k[1] and k[0]!=k[1] and k[2] and k[3] and k[2]!=k[3]:
                            dest[k].append(p)
        # Join by the two row equations, without the candidate's packed key routine.
        crows=defaultdict(list)
        for ck in cc:
            crows[ck[2:]].append(ck)
        for ak,ap in aa.items():
            row0=[v for v in range(32) if (dot(ak[0],v),dot(ak[1],v))==(1,0)]
            row1=[v for v in range(32) if (dot(ak[0],v),dot(ak[1],v))==(0,1)]
            for w0,w1 in product(row0,row1):
                for ck in crows.get((w0,w1),()):
                    if (dot(ck[0],ak[2]),dot(ck[0],ak[3]),dot(ck[1],ak[2]),dot(ck[1],ak[3]))!=(1,0,0,1):
                        continue
                    stats['key_pairs']+=1
                    for a,c in product(sorted(ap),sorted(cc[ck])):
                        stats['profile_pairs']+=1
                        ra=tuple(RANK[s] for s in gaps(a))
                        rc=tuple(RANK[s] for s in gaps(c))
                        rank_pairs[sum(ra),sum(rc)]+=1
                        # Zero projected calls allowed. Every other gap needs at least its rank.
                        ca=tuple(5-(sum(ra)-v) for v in ra)
                        ccaps=tuple(5-(sum(rc)-v) for v in rc)
                        caps[max(ca),max(ccaps),max(x+y for x,y in zip(ca,ccaps))]+=1
                        pairs.append((mid,a,c))
        if progress and stats['middles']%900==0:
            print('independent middle',stats['middles'],flush=True)
    return dict(stats), sorted(pairs), rank_pairs, caps
