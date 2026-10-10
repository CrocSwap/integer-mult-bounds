#!/usr/bin/env python3
"""Fresh raw source471 path ledger from the clean public loader, no receipts.

Reconstructs actual retimed source, target, auxiliary and copied-center paths.
No packed histogram, historical search, scalar replay or network input is used.
Assisted with ChatGPT. Retain supplied source licences and notices.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse, hashlib, json, sys
import source_loader
sys.dont_write_bytecode = True
if not __debug__: raise SystemExit('refusing optimized Python')


def clean(hist):
    return {str(k):v for k,v in sorted(hist.items()) if v}


def reconstruct(context):
    w, c = context['W'], context['C']
    kp = {e['passive']:e for e in w.k['entries']}
    borrow = context['borrow']; omitted = context['omitted']
    recipient = {d:b for b,d in w.pairs}
    roots = defaultdict(list)
    for j, role in enumerate(w.w['rootroles']):
        roots[role].append(w.w['root_frame'][j])
    def chain(role):
        out = [w.opframe[i] for i in w.role_ops[role] if i not in omitted]+roots[role]
        if role in recipient:
            r=recipient[role]
            out += [w.gauge[r]['frame']]+[w.opframe[i] for i in w.role_ops[r] if i not in omitted]+roots[r]
        return out+[w.w['full_frame']]
    inclusion_cache={}
    def included(a,b):
        if (a,b) not in inclusion_cache: inclusion_cache[a,b]=c.sub(a,b)
        return inclusion_cache[a,b]
    def hist(start,path):
        prev=start;rank=0 if start is None else c.dimf[start];result=Counter()
        for frame in path:
            assert prev is None or included(prev,frame), ('nonnested actual path',prev,frame)
            delta=c.dimf[frame]-rank;assert delta>=0
            if delta:result[delta]+=1
            prev=frame;rank=c.dimf[frame]
        return result
    start={r:w.w['source_frame'][n] for n,r in w.source.items()}
    start.update({r:g['frame'] for r,g in w.gauge.items()})
    internal=Counter()
    for r in context['regs']:
        hh=hist(start.get(r),chain(r))
        if r in w.source.values(): hh[1]+=1
        internal.update(hh)
    copies=Counter(c.dimf[w.w['root_frame'][j]] for j,r in enumerate(w.g['roots']) if r['kind']=='center')
    by_source={r['source']:r for r in context['selection']+context['gauge_selection']}
    source=Counter();source_paths=[]
    for n,e in kp.items():
        source.update(hist(e['carrier_chain'][0],e['carrier_chain'][1:]))
        if n not in by_source:
            source.update(hist(e['passive_chain'][0],e['passive_chain'][1:]));continue
        r=by_source[n];role=r['role'];path=chain(role)
        if 'early' in r:
            assert all(i>=r['early'] for i in w.role_ops[role] if i not in omitted)
            path=[e['mix_frame']]+path
        else:
            f=w.register(r['gauge_basis']) if 'gauge_basis' in r else w.gauge[role]['frame']
            path=[e['mix_frame'],f]+path
        hh=hist(w.w['source_frame'][n],path);source.update(hh)
        source_paths.append(dict(source=n,role=role,rank_path=[1]+[c.dimf[f] for f in path],histogram=clean(hh)))
    # Exact target chronology from the source preparation, including compensated
    # gauge reads, terminal writes/posts, side-root reads and partner deliveries.
    target=[[] for _ in range(w.v)]
    def read(t,frame): target[t].append(frame)
    for j,i in enumerate(w.rest):
        for role in context['at'][j]:
            for t in context['adj'][role]: read(t,w.gauge[role]['frame'])
        if i in context['bywrite']:
            e=context['bywrite'][i];read(e['pivot'],w.opframe[i])
        if i in context['afterwrite']:
            e=context['afterwrite'][i]
            for t in e['targets']:read(t,e['root_frame'])
    for role in context['at'][len(w.rest)]:
        for t in context['adj'][role]:read(t,w.gauge[role]['frame'])
    for j,r in enumerate(w.g['roots']):
        if r['kind']=='side' and j not in context['deletedroots']:
            for t in r['targets']:read(t,w.w['root_frame'][j])
        for e in context['deliveries'][j]:
            for t in e['receivers']:read(t,e['deliver_frame'])
    targets=Counter()
    for t,path in enumerate(target):
        assert path
        assert all(all(w.module.dot(c.cov[t],row)==0 for row in c.B[f]) for f in set(path))
        targets.update(hist(None,path));gap=w.h-1-c.dimf[path[-1]];assert gap>=0
        if gap:targets[gap]+=1
    entrances=Counter(g['dim'] for r,g in w.gauge.items() if r not in w.donor and r not in borrow)
    helper=internal+copies+source+targets
    R=len(context['regs']);v=w.v;h=w.h
    assert copies=={22:24} and entrances=={20:2200,18:13,12:18,13:48}
    assert len(source_paths)==len(borrow)==471
    assert sum(r*n for r,n in source.items())==sum(r*n for r,n in targets.items())==v*(h-1)
    assert sum(r*n for r,n in helper.items())==h*R+2*v*(h-1)+sum(r*n for r,n in copies.items())-sum(r*n for r,n in entrances.items())
    idle=Counter({r:2*v for r in (2*h-2,h-1,2*h+2,4)})
    five=Counter({r:5*n for r,n in helper.items()});five.update(idle)
    for a,n in entrances.items():five[5*a]+=n
    W=4*v+R;mass=sum(r*n for r,n in five.items())
    assert (sum(helper.values()),sum(five.values()),mass,5*h*W-mass,max(five))==(95789,495304,2837560,4400,100)
    return dict(schema='source471-clean-raw-ledger/1',source_head='df95878d11190518e45ef9717c9ee05011f88ace',
                h=h,v=v,physical_R=R,source_aliases=len(borrow),
                terminal_sinks=len(context['terminal']),physical_donor_recipient_identifications=len(w.pairs),
                physical_internal_excluding_center_copies=clean(internal),
                paid_center_copy_histogram=clean(copies),physical_source_histogram=clean(source),
                physical_target_histogram=clean(targets),one_stage_helper_histogram_including_copies=clean(helper),
                auxiliary_entrance_rank_histogram=clean(entrances),
                auxiliary_entrance_count=sum(entrances.values()),helper_rank_mass=sum(r*n for r,n in helper.items()),
                five_stage_profile=dict(m=5*h,W=W,histogram=clean(five),idle_histogram=clean(idle),calls=sum(five.values()),rank_mass=mass,deficit=5*h*W-mass,maxchild=max(five)),
                exact_nested_path_pairs_checked=len(inclusion_cache),
                source_paths=source_paths,
                scope='Fresh exact retimed physical-path/rank ledger; no scalar all-column replay or five-stage global-word admission.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr210-root',type=Path,required=True)
    ap.add_argument('--base-bit-root',type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(reconstruct(source_loader.prepare(args.pr210_root,args.base_bit_root)),sort_keys=True,indent=2))

if __name__=='__main__':main()
