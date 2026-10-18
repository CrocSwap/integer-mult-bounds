#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministically construct the new 145-row cap exchange from PR3133's fill.

Jeremy Diviney with OpenAI Codex assistance. The interleaved-copy machinery
and differential checker are retained from Nick Petalas (PR3024).
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from common import P, DELTA, authenticate, context, need, read


def construct(c):
    need(__debug__, 'construction requires enabled assertions')
    N=len(c.base)
    def row(i):return c.lift.row_at(c.base,i)
    def width(i):r=row(i);return c.widths[r[0]//10][r[1]]
    def lifted_members(key):
     copy,owner=divmod(key[0],74)
     return [copy*N+i for i in c.bins.get((owner,key[1],key[2]),[])]
    bad0=[k for k in c.bins if c.pattern(k) not in c.cap.TIGHT]
    bad=[(k[0]+74*j,k[1],k[2]) for j in range(10) for k in bad0]
    four=[];eight=[];nine=[]
    for k in bad:
     for i in lifted_members(k):{4:four,8:eight,9:nine}[width(i)].append(i)
    assert (len(four),len(eight),len(nine))==(20,20,90)
    donors0=[k for k in sorted(c.bins) if c.pattern(k)==(32,(9,9,9))]
    donors=[(k[0]+74*j,k[1],k[2]) for j in range(10) for k in donors0]
    occupied=defaultdict(set)
    for i,r in enumerate(c.base):occupied[r[0]].add((r[2],c.families[r[3]],r[4]))
    def collision(time,key):
     original,copy=divmod(time,10);owner,child,port=key
     oc,oo=divmod(owner,74)
     return copy==oc and (oo,c.families[child],port) in occupied[original]
    def fits(i,key):
     time=row(i)[0];cap,lo,hi=c.lift.destination_window(key,c.win)
     return lo<time<=hi and not collision(time,key)
    used=set();after={}
    for i in four:
     key=next(k for k in donors if k not in used and fits(i,k))
     used.add(key);after[i]=row(i)[:2]+list(key)+[27]
    # Every old bad-48 bin is emptied, so its previous occupancy may be reassigned.
    eight_lo=min(row(i)[0] for i in eight);eight_hi=max(row(i)[0] for i in eight)
    safe_hi=min(c.lift.destination_window(k,c.win)[2] for k in bad)
    chosen=[]
    for k in donors:
     if k in used:continue
     cap,lo,hi=c.lift.destination_window(k,c.win)
     members=lifted_members(k)
     if lo<eight_lo and eight_hi<=hi and max(row(i)[0] for i in members)<=safe_hi:
      chosen.append(k);used.add(k);nine.extend(members)
      if len(chosen)==5:break
    assert len(chosen)==5
    for b,k in enumerate(chosen):
     for j,i in enumerate(eight[4*b:4*b+4]):
      assert fits(i,k)
      after[i]=row(i)[:2]+list(k)+[8*j]
    assert len(nine)==105
    # A greedy five-per-bin coloring; explicit window and family checks follow.
    members={k:[] for k in bad};free=sorted(nine,key=lambda i:(row(i)[0],i))
    for i in free:
     time=row(i)[0]
     for k in bad:
      if len(members[k])>=5 or any(row(j)[0]==time for j in members[k]):continue
      _,lo,hi=c.lift.destination_window(k,c.win)
      if not lo<time<=hi:continue
      # Existing collision is allowed only when its original role is also evacuated.
      oc,oo=divmod(k[0],74);original,copy=divmod(time,10)
      if copy==oc:
       same=[j for j in range(original*408,(original+1)*408) if (c.base[j][2],c.families[c.base[j][3]],c.base[j][4])==(oo,c.families[k[1]],k[2])]
       if any(copy*N+j not in nine+four+eight for j in same):continue
      members[k].append(i);break
     else:raise ValueError(('no destination',i,time))
    assert sorted(len(v) for v in members.values())==[0]*9+[5]*21
    for k,indices in members.items():
     for j,i in enumerate(indices):after[i]=row(i)[:2]+list(k)+[9*j]
    edits=[[i,row(i),r] for i,r in sorted(after.items()) if r!=row(i)]
    journal=dict(copies=10,base_head='51eb9c4ee9e4722010d308aa3309e039d3940cc2',base_fill_sha256=hashlib.sha256((P/'vendor/PR3133-FILL.json.gz').read_bytes()).hexdigest(),edits=edits)
    patched=c.lift.patch(c.base,journal)
    d=c.lift.differential(c.base,patched,c.widths,c.win,c.families)
    assert d['idle_delta']==DELTA,d
    return journal,d


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    need(__debug__, 'construction requires enabled assertions')
    authenticate()
    journal, delta = construct(context())
    need(journal == read(P/'EXCHANGE.json'), 'deterministic journal regeneration')
    if args.write:
        args.write.write_text(json.dumps(journal, indent=1, sort_keys=True)+'\n')
    print('PASS_DETERMINISTIC_145_ROW_EXCHANGE', json.dumps(delta, sort_keys=True))
