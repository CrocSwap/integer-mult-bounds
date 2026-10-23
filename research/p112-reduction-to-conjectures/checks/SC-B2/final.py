import csv,ast,itertools,json
from rrc import g,N
rs=list(csv.DictReader(open('../SC-B/residue.csv')))
# earlier-method status
def jl(fn):
    out={}
    for f in fn:
        for l in open(f):
            r=json.loads(l); out[(r['d'],tuple(r['ws']))]=r
    return out
cov=jl(['fwd.jsonl','rev.jsonl','hard.jsonl'])
cnt={}
for l in csv.DictReader(open('old/killed.csv')): cnt[(int(l['d']),tuple(ast.literal_eval(l['weights'])))]=1
w=csv.writer(open('killed.csv','w'))
w.writerow(['d','s','weights','j','K=top(d-j)','comp','cap(comp)','family_weights(M piece removed)','family_size','N_j','status','second_proof'])
for r in rs:
    ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d']); s=sum(ws)-8*d
    j=2; comp=ws[d-j:]; cap=sum(g[x] for x in comp)
    # greedy family
    fam=[]
    for i in range(len(comp)):
        rest=cap-g[comp[i]]
        if rest<=77 and all(cap-g[comp[i]]-g[comp[k]]<=56 for k in fam): fam.append(i)
    # note: pairs (i,k) must satisfy cap(comp \ {i,k}) <= 56 ; check
    assert all(cap-g[comp[a]]-g[comp[b]]<=56 for a,b in itertools.combinations(fam,2))
    assert len(fam)>N[j], (ws,fam)
    key=(d,tuple(ws))
    sp=[]
    if key in cnt: sp.append('count(17)')
    if key in cov:
        c=cov[key]; sp.append('cover:%s'%('alive' if c['alive'] else 'dead'))
    w.writerow([d,s,ws,j,ws[:d-j],comp,cap,[comp[i] for i in fam],len(fam),N[j],'KILLED-PROVEN(relative RC j=2)'+('' if s==7 else ' + s=6 scenario variants dead (rrc6.py)'),';'.join(sp)])
open('residue.csv','w').write('d,s,weights,note\n')
print('ok',len(rs))
