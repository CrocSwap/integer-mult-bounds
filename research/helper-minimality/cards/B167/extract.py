# Extract block-4567 instance: registers, bounds (subspaces of the 4-dim label space W), targets, shipped macro program
exec(open((__import__('os').environ['HM_ROOT']+'/cards/B98c/work/gate.py')).read().split("good=[")[0])
import json
A=[list(e) for e in d['A']]
cols=[20,21,36,37,46,47,110,111]; S=list(range(432,448)); st=d['start']
vec={l:F.fr[st[l]][0] for l in cols}
B=[161,289,51,30]
def coords(v):
    for m in range(16):
        s=0
        for i in range(4):
            if m>>i&1:s^=B[i]
        if s==v:return m
    return None
def span_set(basis):
    s={0}
    for b in basis: s|={x^b for x in s}
    return s
# end-of-A frames (full A) = shipped bound
cur=list(d['start'])
for e in A:
    f=e[-1]
    for q in regs(e):f=F.join(f,cur[q])
    for q in regs(e):cur[q]=f
Wv={coords(vec[l]) for l in cols}
inst={'cols':cols,'lines_vec':{l:coords(vec[l]) for l in cols},'regs':[]}
for r in cols+S:
    E=span_set(F.fr[cur[r]])
    bound=sorted({coords(x) for x in E if x and coords(x) is not None}) if True else None
    # vectors of E that lie in W (coords not None)
    inst['regs'].append({'id':r,'bound':bound,'row':{str(j):str(x) for j,x in rows0[r].items()}})
# shipped program ops (stage1: 3608..3671, stage2 3672..3759)
ops=[]
for i in range(3608,3760):
    e=A[i]
    ops.append([i]+[ (str(x) if not isinstance(x,(int,)) else x) for x in e[:5]] if e[0]=='add' else [i,'scl',e[1],e[2],e[3]])
inst['ops']=[ [o[0],o[1],o[2],o[3],o[4]] + ([o[5]] if len(o)>5 else []) for o in ops]
json.dump(inst,open(__import__('os').environ['HM_ROOT']+'/cards/B167/inst4567.json','w'))
print(len(inst['regs']))
for r in inst['regs']: print(r['id'],len(r['bound']),sorted(r['row'].keys()))
print(inst['lines_vec'])
