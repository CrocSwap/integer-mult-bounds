#!/usr/bin/env python3
"""Check source-pinned finite exhaustion, its hypotheses and attaining edit."""
import copy
import itertools
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import audit as a
import independent


def compatible(edges,uses):
    helpers=[h for h,_ in edges]
    if len(set(helpers))!=len(helpers):return False
    for (h,lender),(g,other) in itertools.combinations(edges,2):
        if lender==other and not (uses[h][-1][0]<uses[g][0][0] or uses[g][-1][0]<uses[h][0][0]):return False
    return True


def run():
    words=a.load();results={};controls=[]
    wanted=[[606,68],[635,68],[638,68],[639,68],[653,49],[653,68],[653,83],[653,98],[653,101]]
    def reject(name,fn):
        try:fn()
        except ValueError as err:controls.append({'name':name,'reason':str(err)})
        else:raise ValueError('ineffective control '+name)
    for tag in ('base','extra'):
        before,after=words['2526-'+tag],words['2559-'+tag]
        old,new=a.inspect(before),a.inspect(after)
        a.need(old['pairs']==wanted and not new['pairs'],'nine initial / zero final candidates')
        a.need(independent.census(before)==old['pairs'] and independent.census(after)==new['pairs'],'independent timeline census')
        changes=a.check_edit(before,after)
        pairs=old['pairs'];helpers=sorted({h for h,_ in pairs});lenders=sorted({l for _,l in pairs})
        a.need(all(l<112 for l in lenders),'all candidates lend sources')
        common=(max(old['uses'][h][0][0] for h in helpers),min(old['uses'][h][-1][0] for h in helpers))
        a.need(common[0]<common[1],'all candidate lifetimes overlap')
        # Every original selected helper's late required frame has dimension8.
        # Any replacement source has nondecreasing dimension after its new warp.
        a.need(all(old['uses'][h][-1][1]==8 for h in helpers),'late dimension premise')
        a.need(all(a.dimension(old['retirement'][l])==4 for l in lenders),'retired dimension premise')
        allowed=[]
        for bits in range(1<<len(pairs)):
            choice=[pairs[i] for i in range(len(pairs)) if bits>>i&1]
            if compatible(choice,old['uses']):allowed.append(choice)
        maximum=max(map(len,allowed));optimal=[x for x in allowed if len(x)==maximum]
        a.need(maximum==2 and len(optimal)==16,'sharp graph bound')
        a.need([[606,68],[653,49]] in optimal,'shipped upper-bound attainer')
        delta={r:new['profile'].get(r,0)-old['profile'].get(r,0) for r in set(old['profile'])|set(new['profile'])}
        delta={r:n for r,n in delta.items() if n}
        a.need(delta=={1:1,5:-2},'exact paid delta')
        results[tag]={'initial_helper_candidates':len(old['helpers']),'initial_lender_candidates':len(old['lenders']),
            'initial_pairs':pairs,'initial_rejections':old['rejections'],'final_pairs':new['pairs'],
            'helper_lifetimes_B_indices':{str(h):[(old['uses'][h][0][0]-old['base']-1)//2,(old['uses'][h][-1][0]-old['base']-1)//2] for h in helpers},
            'lender_retirements_B_indices':{str(l):[(old['uses'][l][-1][0]-old['base']-1)//2,a.dimension(old['retirement'][l])] for l in lenders},
            'all_candidate_lifetimes_common_B_interval':[(common[0]-old['base']-1)//2,(common[1]-old['base']-1)//2],
            'graph_subsets_checked':1<<len(pairs),'compatible_subsets':len(allowed),'maximum_matching_size':maximum,
            'maximum_matchings':optimal,'shipped_aliases':[[606,68],[653,49]],'shipped_warps':changes,
            'profile_before':old['profile'],'profile_after':new['profile'],'profile_delta':delta,
            'widths_before':old['widths'],'widths_after':new['widths']}
    old=words['2526-base'];new=words['2559-base'];info=a.inspect(old)
    reject('overlapping source reuse',lambda:a.need(compatible([[606,68],[635,68]],info['uses']),'lender lifetime overlap'))
    reject('one helper cannot be removed twice',lambda:a.need(compatible([[653,49],[653,83]],info['uses']),'duplicate helper'))
    bad=copy.deepcopy(new);bad['warps'][-1][2][0]=bad['warps'][-1][2][1]
    reject('singular replacement warp',lambda:a.check_edit(old,bad))
    bad=copy.deepcopy(new);bad['cleanup'].pop()
    reject('missing inverse cleanup',lambda:a.check_edit(old,bad))
    bad=copy.deepcopy(new);bad['report']['local_profile']['1']-=1
    reject('omitted new rank-one climb',lambda:a.inspect(bad))
    bad=copy.deepcopy(new);bad['warps'][-1][4]=[1,2,4,8]
    reject('wrong equal-dimensional image',lambda:a.check_edit(old,bad))
    # Equivalent generators change no subspace or candidate; this is a positive control.
    equivalent=copy.deepcopy(old)
    for e in equivalent['A']+equivalent['B']+equivalent['restore']:
        if e[0]!='warp': e[-1]=list(reversed(e[-1]))
    a.need(a.inspect(equivalent)['pairs']==wanted,'equivalent frame bases')
    return {'status':'PASS_RETIRED_LENDER_EXHAUSTION','words':results,'controls':controls,
            'scope':'Fixed noncold one-warp retired-lender class; all-sequence upper bound2 via noncreation and common interval. No general alias/supplier optimality.'}


def main():
    a.need(sys.argv[1:] in ([],['--write']),'usage: verify.py [--write]')
    receipt=HERE/'RESULT.json'
    if sys.argv[1:]:
        with receipt.open('x',encoding='utf-8') as out:json.dump(run(),out,sort_keys=True,indent=2);out.write('\n')
    else:
        result=run()
        a.need(json.dumps(result,sort_keys=True)==json.dumps(json.loads(receipt.read_text()),sort_keys=True),'typed receipt mismatch')
    print('PASS_RETIRED_LENDER_EXHAUSTION words=4 initial_pairs=9 maximum=2 matchings=16 controls=6')


if __name__=='__main__':main()
