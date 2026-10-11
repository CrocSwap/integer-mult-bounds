from pathlib import Path
from collections import Counter
import json,sys,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';sys.path.insert(0,str(BASE));import hosting_core as HC
N=json.loads((BASE/'NOMINATION.json').read_text());win={int(i):(p,r,set(ss))for i,(p,r,ss)in N['windows'].items()};orig=json.loads((BASE/'local/records/249-states.json').read_text());F=json.loads((BASE/'local/records/frames.json').read_text())['frames'];basewidth=[8-F[str(orig['initial'][str(h)])]['dim']for h in range(240,980)];lazy=json.loads((P/'drop970-948-lazy/records/249-states.json').read_text());newwidth=[8-F[str(lazy['initial'][str(h)])]['dim']for h in range(240,980)]
calls=int(sys.argv[sys.argv.index('--calls')+1])if '--calls'in sys.argv else 5;tag=('-count%d'%calls)if '--calls'in sys.argv else'';choose={(5,rep)for rep in range(calls)}
if '--all'in sys.argv:tag='-all';choose={(s,rep)for s in range(11)for rep in range(8)}
allwidth={s:[w for rep in range(8)for w in(newwidth if(s,rep)in choose else basewidth)]for s in range(11)};avail=Counter((s,w)for s,ws in allwidth.items()for w in ws)
if '--replay'not in sys.argv:
 ys,zs,val=HC.solve(win,1920,dict(avail),78,group={w:10000 for s,w in avail});HC.save_selection(P/('POOL-SELECTION'+tag+'.json'),'bit',ys,zs,val)
ys,zs,val=HC.load_selection(P/('POOL-SELECTION'+tag+'.json'),'bit');slots,rem=HC.expand(win,ys,zs,{s:list(enumerate(ws))for s,ws in allwidth.items()},1920);assert len(slots)==65120
base=json.loads((BASE/'LOCAL-SUMMARY.json').read_text())['local_profile'];H=Counter({int(r):v*88 for r,v in base.items()})
for r,d in {1:-2,4:-4,5:4}.items():H[r]+=len(choose)*d
for r in rem.values():
 if r:H[r]+=1
assert sum(r*n for r,n in H.items())==745536
s=importlib.util.spec_from_file_location('M',ROOT/'experiments/architecture/complex-direct8-eleven451/work/pr361/code/engines/moment.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);cap=M.certify(dict(H),78,9600,True)
r=dict(status='SIGNED_COMPLETE_PROVIDER_POOL_ASSIGNMENT_PROFILE_SCREEN',chosen=sorted(choose),profile=dict(sorted(H.items())),rankmass=745536,deficit=3264,slots=slots,remainder_profile=dict(Counter(rem.values())),cap=cap,scope='Fullsignedprovideralreadyverified. This is only exact expandedassignment/profile; needsactualheterogeneouscallstream/sourcecharts/prefix/invoice before score admission.')
(P/('POOL-NOMINATION'+tag+'.json')).write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items()if k not in ['slots','scope']})
