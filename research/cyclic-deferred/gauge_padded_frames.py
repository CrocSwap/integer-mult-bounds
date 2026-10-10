"""Padded triple objective for exact source-gauge and shared-plateau descent.
Input must contain the exact local source state,
current arbitrary operation frames and fixed compensated reuse pairs.
"""
from collections import Counter,defaultdict
from functools import lru_cache
from reuse import basis,complement,nondeg,contained as plain_contained
from arbitrary_frames import general_frame

@lru_cache(None)
def contained(A,B):return plain_contained(A,B)

@lru_cache(None)
def intersection(A,B,h):
    return complement(basis(complement(A,h)+complement(B,h)),h)

# Frozen integer search weights; no floating result enters any certificate.
WEIGHTS = (0, 10000000000000000000000000000000000000000, 19995379552591837382775889827050449904979, 29989015888449392928645236540478701956455, 39981520345220774690768272038046978013735, 49973183228757330836823088833072358339525, 59964175509825272502769082288517196077212, 69954610152207694202574952004534640790419, 79944567439236201753790348429080145493684, 89934107395767013189839565186018423885624, 99923276611021966935579916938258879056401, 109912112302259010906160819839182212710832, 119900644887718846958874586969063870269385, 129888899695720170457234823823425114507787, 139876898144698708970082643468833997994746, 149864658584359632812685622102969862143699, 159852196911530273460627424580342355718650, 169839527031456604018724816697495391901760, 179826661210191807363562888188255624208623, 189813610348441151070503826377433151796525, 199800384197600682599437329947280431748835, 209786991532483974684540213818179734824257, 219773440291076756696113170334150098302772, 229759737688831192394197057459135847609982, 239745890313046845226998719817503395211757, 249731904201495296533012312534849449897105, 259717784908445522472210278494992615266707, 269703537560517101440408324572479956281500, 279689166904247967984995767237230697931084, 289674677346858433464531831432946135319808, 299660072991386137626417202966245749314891, 309645357667131309906013996018901817201642, 319630534956169648883469413861820322206269, 329615608216547946239711841226446070755662, 339600580602665602194156349433186737938982, 349585455083256285454287582466019631567456, 359570234457312897947927495239884378681063, 369554921368241751885243866479822165261943, 379539518316485457755435908822079205273288, 389524027670816171047685041694426412781394, 399508451678469795277115663814408216486410, 409492792474266127696541637300126708888982, 419477052088838699518395411801356466137245, 429461232456080370092893903902666862183135, 439445335419895924660946452619916239478452, 449429362740340473454711911343481884793238, 459413316099211936499973859286203787200282, 469397197105156986089196347967265083247119, 479381007298342234812418820326263672833330, 489364748154735979704796570095644671054616, 499348421090040261669862310776885137110086, 509332027463308225615245127768430435396110, 519315568580277648622735578578711551751269, 529299045696447940039842136448730430345222, 539282460019924824848306569868258868529645, 549265812714054230231448809753163047120645, 559249104899864546551611414841015531401954, 569232337658334378973755920378990083220073, 579215512032501103483286733598126059114324, 589198629029423956201542610683504258368037, 599181689622013988175317443766342623852270, 609164694750741984112709954242943473197095, 619147645325234351466410660273449000512923, 629130542225766017543652267331872731462200, 639113386304658511279126095898030443669003, 649096178387590639477537839434436583250988, 659078919274828483115809426326380440602354, 669061609742380827673467686881910531243346, 679044250543085593761985443132138642637733, 689026842407632343026430549588026886175730, 699009386045525492854112974747077346226498)

def optimize(S, m=None, solo_rounds=8, joint_rounds=12):
    if m is None:m=3*S['h']
    ops=S['ops'];R=S['R'];h=S['h'];v=S['v'];FULL=basis(1<<i for i in range(h));old_sigma={s:basis(F)for s,F in S['placed'].items()};sigma=old_sigma.copy();frames={i:basis(F)for i,F in S['op_frames'].items()}
    merge={p['recipient']:p['donor']for p in S['reuse_pairs']};donors=set(merge.values());live=[s for s in range(R)if s not in merge];role_events=defaultdict(list);frozen=set();first={}
    for i,o in enumerate(ops):
     ss=o[1:2]if o[0]=='src'else o[1:3]
     for s in ss:role_events[s].append(i);first.setdefault(s,i)
     if o[0]=='src':frozen.add(i)
    for b,c in merge.items():frozen.update((S['last'][c],first[b]))
    prev={};after={};end={s:basis(S['root_frame'].get(s,FULL))for s in range(R)}
    for s,events in role_events.items():
     for j,i in enumerate(events):prev[i,s]=events[j-1]if j else None;after[i,s]=events[j+1]if j+1<len(events)else None
    reach={s:tuple(sorted(S['reach'][s]))for s in range(R)if s not in S['touched'] and not S['reach_all'][s] and s not in donors}
    targetend=[complement((t,),h)for t in S['tmask']]
    levels=[{}for _ in range(v)]
    for s,F in sigma.items():
     for t in reach[s]:
      d=len(F)
      if d in levels[t]:assert levels[t][d][0]==F;levels[t][d][1]+=1
      else:levels[t][d]=[F,1]
    assert 0<m<len(WEIGHTS), 'Gauge objective outside frozen weight range'
    weights=WEIGHTS
    cap=lambda A,B:intersection(A,B,h)

    def sweep_gauges(order):
     changes=added=removed=0;gain=0
     for s in order:
      targets=reach[s];old=sigma.get(s,());old_d=len(old);f=frames[first[s]];donorF=frames[S['last'][merge[s]]]if s in merge else ();e=len(donorF)
      # Remove this read from each target chain, leaving its exact neighbors.
      chains=[]
      for t in targets:
       chain=[(d,F)for d,(F,n)in sorted(levels[t].items())if not(d==old_d and n==1)]
       chains.append([(0,())]+chain+[(h-1,targetend[t])])
      def source_cost(d):return 3*weights[len(f)-d]+(3*weights[d-e]if s in merge else weights[3*d])
      # Total cost relative to deleting this target read.
      def cost(F):
       d=len(F);c=source_cost(d)
       for chain in chains:
        j=next((j for j,(nd,N)in enumerate(chain)if nd>=d),len(chain)-1)
        if j==0:P=N=();pd=nd=0
        else:pd,P=chain[j-1];nd,N=chain[j]
        assert contained(P,F)and contained(F,N),(s,d,pd,nd)
        c+=3*(weights[d-pd]+weights[nd-d]-weights[nd-pd])
       return c
      oldcost=cost(old);best=old;bestcost=oldcost
      # Every interval of chronological neighbor frames has a concave rank cost,
      # so an optimum occurs at the exact lower span or upper intersection.
      cuts=sorted({0}|{d for ch in chains for d,F in ch})
      seen=set()
      for k in cuts:
       Ps=[];Ns=[]
       for ch in chains:
        j=max(j for j,(d,F)in enumerate(ch)if d<=k)
        Ps.append(ch[j][1]);Ns.append(ch[min(j+1,len(ch)-1)][1])
       low=basis(donorF+tuple(x for F in Ps for x in F))
       if len(low)>len(f)or not contained(low,f):continue
       high=f
       for N in Ns:
        high=cap(high,N)
        if len(high)<len(low):break
       if not contained(low,high):continue
       for F in (low,high):
        if F in seen:continue
        seen.add(F);c=cost(F)
        if c<bestcost:best=F;bestcost=c
      if best!=old:
       for t in targets:
        if old_d:
         levels[t][old_d][1]-=1
         if levels[t][old_d][1]==0:del levels[t][old_d]
        d=len(best)
        if d:
         if d in levels[t]:assert levels[t][d][0]==best;levels[t][d][1]+=1
         else:levels[t][d]=[best,1]
       if best:sigma[s]=best
       else:del sigma[s]
       changes+=1;added+=not bool(old);removed+=not bool(best);gain+=oldcost-bestcost
     return dict(changes=changes,added=added,removed=removed,gain=str(gain))

    def sweep_ops(reverse):
     changes=0;gain=0
     for i in (reversed(range(len(ops)))if reverse else range(len(ops))):
      if i in frozen:continue
      o=ops[i];a,b=o[1:3];F=frames[i]
      starts=[frames[prev[i,s]]if prev[i,s]is not None else sigma.get(s,())for s in (a,b)]
      ends=[frames[after[i,s]]if after[i,s]is not None else end[s]for s in (a,b)]
      low=basis(starts[0]+starts[1]);high=cap(*ends)
      assert contained(low,F)and contained(F,high)
      def cost(d):return sum(weights[d-len(P)]+weights[len(N)-d]for P,N in zip(starts,ends))
      winner=min([F,low,high],key=lambda C:cost(len(C)));improvement=cost(len(F))-cost(len(winner))
      if improvement>0:frames[i]=winner;changes+=1;gain+=improvement
     return dict(changes=changes,gain=str(gain))

    def sweep_groups():
     # A plateau contains equal gauges joined by a common target read.
     # Move the complete component so duplicate readouts cannot pin it in place.
     parents={s:s for s in sigma};owner={}
     def find(s):
      while parents[s]!=s:parents[s]=parents[parents[s]];s=parents[s]
      return s
     for s,F in sigma.items():
      for t in reach[s]:
       key=(t,F)
       if key in owner:parents[find(s)]=find(owner[key])
       else:owner[key]=s
     groups=defaultdict(list)
     for s in sigma:groups[find(s)].append(s)
     changes=roles=removed=0;gain=0
     for ss in sorted(groups.values(),key=lambda ss:(-len(ss),ss)):
      if len(ss)<2:continue
      old=sigma[ss[0]];old_d=len(old);targetcounts=Counter(t for s in ss for t in reach[s]);targets=sorted(targetcounts)
      chains=[]
      for t in targets:
       chain=[(d,F)for d,(F,n)in sorted(levels[t].items())if not(d==old_d and n==targetcounts[t])]
       chains.append([(0,())]+chain+[(h-1,targetend[t])])
      f=FULL;donorF=();es=[];fs=[]
      for s in ss:
       f=cap(f,frames[first[s]]);fs.append(len(frames[first[s]]))
       if s in merge:
        F=frames[S['last'][merge[s]]];es.append(len(F));donorF=basis(donorF+F)
       else:es.append(None)
      def cost(F):
       d=len(F);c=sum(3*weights[fd-d]+(3*weights[d-e]if e is not None else weights[3*d])for fd,e in zip(fs,es))
       for chain in chains:
        j=next((j for j,(nd,N)in enumerate(chain)if nd>=d),len(chain)-1)
        if j==0:P=N=();pd=nd=0
        else:pd,P=chain[j-1];nd,N=chain[j]
        assert contained(P,F)and contained(F,N)
        c+=3*(weights[d-pd]+weights[nd-d]-weights[nd-pd])
       return c
      oldcost=cost(old);best=old;bestcost=oldcost;seen=set()
      for k in sorted({0}|{d for ch in chains for d,F in ch}):
       Ps=[];Ns=[]
       for ch in chains:
        j=max(j for j,(d,F)in enumerate(ch)if d<=k)
        Ps.append(ch[j][1]);Ns.append(ch[min(j+1,len(ch)-1)][1])
       low=basis(donorF+tuple(x for F in Ps for x in F))
       if len(low)>len(f)or not contained(low,f):continue
       high=f
       for N in Ns:
        high=cap(high,N)
        if len(high)<len(low):break
       if not contained(low,high):continue
       for F in(low,high):
        if F in seen:continue
        seen.add(F);c=cost(F)
        if c<bestcost:best=F;bestcost=c
      if best!=old:
       for t,n in targetcounts.items():
        levels[t][old_d][1]-=n
        if levels[t][old_d][1]==0:del levels[t][old_d]
        d=len(best)
        if d:
         if d in levels[t]:assert levels[t][d][0]==best;levels[t][d][1]+=n
         else:levels[t][d]=[best,n]
       for s in ss:
        if best:sigma[s]=best
        else:del sigma[s]
       changes+=1;roles+=len(ss);removed+=len(ss)if not best else 0;gain+=oldcost-bestcost
     return dict(changes=changes,roles=roles,removed=removed,gain=str(gain))


    records=[];candidates=list(reach)
    for phase,rounds in [('solo',solo_rounds),('joint',joint_rounds)]:
     for turn in range(rounds):
      order=sorted(candidates,key=lambda s:(-len(frames[first[s]]),len(reach[s]),s))
      if turn%2:order.reverse()
      g=sweep_gauges(order);joint=sweep_groups()if phase=='joint'else dict(changes=0);o=sweep_ops(turn%2==0)
      records.append(dict(phase=phase,turn=turn,gauges=g,joint=joint,operations=o))
      if not(g['changes']or joint['changes']or o['changes']):break
    checked_auxiliary_chain_steps=0
    for s,events in role_events.items():
     seq=[sigma.get(s,())]+[frames[i]for i in events]+[end[s],FULL]
     assert all(contained(A,B)for A,B in zip(seq,seq[1:])),s
     checked_auxiliary_chain_steps+=len(seq)-1
    checked_target_chain_steps=0
    for t in range(v):
     seq=[()]+[F for d,(F,n)in sorted(levels[t].items())]+[targetend[t]]
     assert all(contained(A,B)for A,B in zip(seq,seq[1:])),t
     checked_target_chain_steps+=len(seq)-1
    assert not set(sigma)&set(S['touched']), 'Deferred gauge touched before readout'
    assert all(contained(F,frames[first[s]]) and general_frame(F,h) for s,F in sigma.items()), 'Invalid source gauge'
    for b,c in merge.items():assert contained(frames[S['last'][c]],sigma[b])
    assert all(frames[i]==basis(S['op_frames'][i])for i in frozen)
    assert records[-1]['gauges']['changes']==records[-1]['joint']['changes']==records[-1]['operations']['changes']==0, 'Gauge descent has not reached its checked fixed point'
    stats=dict(padded_triple_objective=True,objective_ambient=m,checked_auxiliary_chain_steps=checked_auxiliary_chain_steps,checked_target_chain_steps=checked_target_chain_steps,checked_source_gauge_containments=len(sigma),checked_reuse_gauge_containments=len(merge),deferred_roles_untouched_early=True,source_injection_and_reuse_handoff_frames_fixed=True,reuse_mapping_fixed=True,source_injection_and_root_frames_fixed=True,initial_deferred_roles=len(old_sigma),changed_gauges=sum(sigma.get(s,())!=old_sigma.get(s,())for s in set(sigma)|set(old_sigma)),descent=records,deferred_roles=len(sigma),degenerate_gauges=sum(not nondeg(F)for F in sigma.values()),source_dimension_sum=sum(len(sigma.get(s,()))for s in live))
    return sigma,frames,stats
