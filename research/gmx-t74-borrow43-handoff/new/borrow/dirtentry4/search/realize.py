import sys,os,pickle,json,gzip
sys.path.insert(0,os.path.join(os.environ['FILLPKG'],'new/borrow-fill/search'))
from agg import *
x,y=pickle.load(open(sys.argv[1],'rb'))
base=read(sys.argv[2])['rows']
rows,fails=realize(x,y,0,base);print('fails',fails,flush=True)
if not fails:
    paid={p:{int(k):v for k,v in d['actual_paid_profile'].items()} for p,d in prov.items()}
    widths={p:d['widths'] for p,d in prov.items()}
    idl,H=check(rows,widths,paid);print('check ok',dict(sorted(idl.items())),kappa(H),flush=True)
    save(rows,sys.argv[3])
