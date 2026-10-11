"""plans.pkl -> raw/reused/final words (same pipeline as parent436 regen.py: compile2 -> fullword -> reuse -> retime)."""
import os,sys,pickle,json
os.environ['E8COORD']='ham'
sys.path.insert(0,'../reg/code/reuse'); 
import hx, fullword, compile as C
import reuse as RU, retime as RT
plans_file=sys.argv[1]; outdir=sys.argv[2]; pfile=sys.argv[3] if len(sys.argv)>3 else 'params-r740.json'
os.makedirs(outdir,exist_ok=True)
h,atoms=hx.load(pfile)
plans=pickle.load(open(plans_file,'rb')) if plans_file!='-' else hx.default_plans(atoms)
S=hx.Search(h,atoms,plans,0)
R,W=hx.R_of(h)
bad=C.f2_check(W); print('compile2 R',R,'f2 replay bad (y,x):',len(bad[0]),len(bad[1]),W.stats)
raw=fullword.build(W); fullword.save(raw,outdir+'/raw.json.gz')
re_,nre=RU.reuse(raw); fullword.save(re_,outdir+'/reused.json.gz')
fin,mv=RT.retime(re_,sweeps=6,M=64); fullword.save(fin,outdir+'/final.json.gz')
json.dump(dict(helpers=nre['helpers'],totals=nre['totals'],eliminations=nre['eliminations']),open(outdir+'/ledger.json','w'))
print('raw R',raw['R'],'reused R',re_['R'],'final R',fin['R'],'retime moves',mv)
