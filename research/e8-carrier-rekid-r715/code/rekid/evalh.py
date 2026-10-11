"""evaluate a pickled hierarchy snapshot: compile2 R, f2 replay, reuse R. usage evalh.py snap.h [outdir]"""
import os,sys,pickle,json
os.environ['E8COORD']='ham'
sys.path.insert(0,'../reg/code/reuse')
import ham1
import c2x as C2, compile as C, fullword, frames as Fm
import reuse as RU, retime as RT
h=pickle.load(open(sys.argv[1],'rb'))
for t in range(120):
    x=0
    for u in h.need[t]: x^=h.content[u]
    assert x==Fm.HYP[t],t
W=C2.compile2(h); bad=C.f2_check(W)
print('compile2 R',W.nh,'f2 bad',len(bad[0]),len(bad[1]),W.stats)
raw=fullword.build(W); re_,nre=RU.reuse(raw); print('reused R',re_['R'],'(raw',raw['R'],')')
if len(sys.argv)>2:
    od=sys.argv[2]; os.makedirs(od,exist_ok=True)
    fullword.save(raw,od+'/raw.json.gz'); fullword.save(re_,od+'/reused.json.gz')
    fin,mv=RT.retime(re_,sweeps=6,M=64); fullword.save(fin,od+'/final.json.gz'); print('final R',fin['R'],'retime moves',mv)
    json.dump(dict(helpers=nre['helpers'],totals=nre['totals'],eliminations=nre['eliminations']),open(od+'/ledger.json','w'))
