import sys,pickle,collections,time
inc=pickle.load(open('inc.pkl','rb'))
which=sys.argv[1]  # 'h' = nh==0 classes only ; 'all'
nw=int(sys.argv[2]) if len(sys.argv)>2 else 2
tl=float(sys.argv[3]) if len(sys.argv)>3 else 100
idx=[i for i,x in enumerate(inc) if which=='all' or x['nh']==0]
def compat(a,b):
    if inc[a]['last']<inc[b]['first']:return not (inc[a]['Lm']&~inc[b]['cap'])
    if inc[b]['last']<inc[a]['first']:return not (inc[b]['Lm']&~inc[a]['cap'])
    return False
comp=[(a,b) for ii,a in enumerate(idx) for b in idx[ii+1:] if compat(a,b)]
print(which,'N',len(idx),'compat pairs',len(comp),flush=True)
# UB: greedy chain cover (clique cover in compat graph) -- sequential assignment by first time
order=sorted(idx,key=lambda i:inc[i]['first'])
chains=[]
for i in order:
    best=None
    for c in chains:
        if all(compat(j,i) for j in c):
            best=c;break
    if best is None:chains.append([i])
    else:best.append(i)
print('greedy chain cover (UB on registers for this set under model)',len(chains),flush=True)
from ortools.sat.python import cp_model
m=cp_model.CpModel()
x={i:m.NewBoolVar(str(i)) for i in idx}
for a,b in comp:m.AddBoolOr([x[a].Not(),x[b].Not()])
m.Maximize(sum(x.values()))
s=cp_model.CpSolver();s.parameters.num_workers=nw;s.parameters.max_time_in_seconds=tl
st=s.Solve(m)
print('status',s.StatusName(st),'MIS(max pairwise-conflicting incarnations) =',s.ObjectiveValue(),'bound',s.BestObjectiveBound(),flush=True)
sel=[i for i in idx if s.Value(x[i])]
pickle.dump((sel,len(chains)),open('mis_%s.pkl'%which,'wb'))
print('selected: carriers helper/non',collections.Counter(('H' if c>=224 else 'Y' if c>=112 else 'src') for i in sel for c in inc[i]['car']))
