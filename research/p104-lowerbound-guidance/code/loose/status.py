"""Summarise the F2T campaign: union of cubes/F2T.log (base f55n, mkcube2) and AF2T.state.json (arun on f55e)."""
import json,os
m=[int(x) for x in open('masks0.txt').read().split()]
first={}
for l in open('cubes/F2T.log'):
    p=l.split()
    if p and p[0].isdigit() and 'UNSAT' in l: first[int(p[0])]='UNSAT'
st=json.load(open('AF2T.state.json')) if os.path.exists('AF2T.state.json') else {'queue':[],'done':[]}
sat=[d for d in st['done'] if d[2]=='SATISFIABLE']; unres=[d for d in st['done'] if d[2]=='UNRESOLVED']
pend=st['queue']
print('masks total',len(m),'| closed by F2T.log',len(first),'| arun done',len(st['done']),'SAT',len(sat),'UNRESOLVED',len(unres),'| queue',len(pend))
if not pend and not sat and not unres and os.path.exists('AF2T.state.json'):
    print('VERDICT: F2-tight + exemptions, budget 55: ALL CUBES UNSAT')
for d in sat: print('SAT cube',d)
