"""Exact plateau descent for common operation frames under padded rank cost.

Equal-frame gates connected along a role are moved together to the span of
external predecessor frames or intersection of external successor frames.
Source gauges, source injections and roots stay fixed. Reuse donor
terminal frames may move inside the recipient source gauge. Thus the scalar chronology and compensated-read deadlines stay valid.
The frozen integer weights affect search order only; final moment bounds are
certified independently. Prepared with OpenAI Codex assistance.
"""
from collections import defaultdict,Counter
from reuse import basis
from gauge_padded_frames import intersection,contained,WEIGHTS

def optimize(S,max_rounds=20):
    h=S['h'];v=S['v'];R=S['R'];ops=S['ops'];sigma=S['placed'];original=S['op_frames'];frames={i:basis(F)for i,F in original.items()};FULL=basis(1<<i for i in range(h));events=defaultdict(list);first={};frozen=set();weights=WEIGHTS
    for i,o in enumerate(ops):
     for s in(o[1:2]if o[0]=='src'else o[1:3]):events[s].append(i);first.setdefault(s,i)
     if o[0]=='src':frozen.add(i)
    end={s:basis(S['root_frame'].get(s,FULL))for s in range(R)};prev={};nxt={}
    for p in S['reuse_pairs']:end[p['donor']]=sigma[p['recipient']]
    for s,es in events.items():
     for j,i in enumerate(es):prev[i,s]=es[j-1]if j else None;nxt[i,s]=es[j+1]if j+1<len(es)else None

    def solo(reverse):
     changes=0;gain=0
     for i in(reversed(range(len(ops)))if reverse else range(len(ops))):
      if i in frozen:continue
      o=ops[i];a,b=o[1:3];F=frames[i]
      starts=[frames[prev[i,s]]if prev[i,s]is not None else sigma.get(s,())for s in(a,b)]
      ends=[frames[nxt[i,s]]if nxt[i,s]is not None else end[s]for s in(a,b)]
      low=basis(starts[0]+starts[1]);high=intersection(*ends,h)
      assert contained(low,F)and contained(F,high)
      def cost(C):return sum(weights[len(C)-len(P)]+weights[len(N)-len(C)]for P,N in zip(starts,ends))
      best=min((F,low,high),key=cost);diff=cost(F)-cost(best)
      if diff:frames[i]=best;changes+=1;gain+=diff
     return dict(changes=changes,gain=str(gain))

    def plateau():
     parents=list(range(len(ops)))
     def find(i):
      while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
      return i
     for es in events.values():
      for a,b in zip(es,es[1:]):
       if frames[a]==frames[b]:parents[find(a)]=find(b)
     groups=defaultdict(list)
     for i in range(len(ops)):groups[find(i)].append(i)
     changes=changed_ops=gain=eligible=0;max_group=max(map(len,groups.values()));fixed_groups=0
     for group in sorted(groups.values(),key=lambda g:(-len(g),g)):
      if len(group)<2:continue
      if any(i in frozen for i in group):fixed_groups+=1;continue
      members=set(group);F=frames[group[0]];assert all(frames[i]==F for i in group)
      starts=[];ends=[]
      for i in group:
       for s in ops[i][1:3]:
        a,b=prev[i,s],nxt[i,s]
        if a not in members:starts.append(frames[a]if a is not None else sigma.get(s,()))
        if b not in members:ends.append(frames[b]if b is not None else end[s])
      low=basis(x for A in starts for x in A);high=FULL
      for B in ends:high=intersection(high,B,h)
      assert contained(low,F)and contained(F,high)
      if low==high:continue
      eligible+=1
      def cost(C):return sum(weights[len(C)-len(A)]for A in starts)+sum(weights[len(B)-len(C)]for B in ends)
      best=min((F,low,high),key=cost);diff=cost(F)-cost(best)
      if diff:
       for i in group:frames[i]=best
       changes+=1;changed_ops+=len(group);gain+=diff
     return dict(changes=changes,changed_operations=changed_ops,gain=str(gain),groups=len(groups),max_group=max_group,frozen_groups=fixed_groups,eligible=eligible)

    records=[]
    for turn in range(max_rounds):
     a=solo(turn%2==0);b=plateau();record=dict(turn=turn,solo=a,plateaus=b);records.append(record)
     if a['changes']==b['changes']==0:break
    else:raise AssertionError('No fixed point')
    assert all(frames[i]==original[i]for i in frozen)
    checked_steps=0
    for role,es in events.items():
     chain=[sigma.get(role,())]+[frames[i]for i in es]+[end[role],FULL]
     assert all(contained(A,B)for A,B in zip(chain,chain[1:])),role
     checked_steps+=len(chain)-1
    return frames,dict(checked_auxiliary_chain_steps=checked_steps,fixed_source_gauges=True,fixed_read_deadlines=True,fixed_reuse_handoffs=False,reuse_donor_ends_at_recipient_gauge=True,fixed_source_injection_frames=True,fixed_root_frames=True,changed_operations=sum(frames[i]!=original[i]for i in frames),descent=records)
