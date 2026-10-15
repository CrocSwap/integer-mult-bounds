"""naive fill for an alias stack: delete the removed helpers' roles, compact; usage: naive.py BASEWORD EXTRAWORD OUT.FILL.json.gz"""
import sys,collections,json,gzip,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fillbase import *
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../borrow'))
wb=read(sys.argv[1]);we=read(sys.argv[2])
old_removed=read(P/'new/borrow/words/BORROW-WORD-43base.json.gz')['removed']
assert sorted(wb['removed'])==sorted(we['removed'])
def wid(w):
    v=112;rem=[r for r in range(224,704) if r not in set(w['removed'])];se={int(k):x for k,x in w['start_extra'].items()};hf={int(k):x for k,x in w['helper_final'].items()}
    return [len(hf.get(r,range(9)))-len(se.get(r,[])) for r in rem]
widths={'gauge44':wid(wb),'extra':wid(we)}
paid={'gauge44':{int(k):v for k,v in wb['report']['local_profile'].items()},'extra':{int(k):v for k,v in we['report']['local_profile'].items()}}
rows=reindex_rows(fill['rows'],old_removed,wb['removed'])
rows=compact(rows,lambda x:widths[dispatch[tuple(order[x[0]])]][x[1]])
idle,H=check(rows,widths,paid)
print('idle',dict(sorted(idle.items())));print('H',dict(sorted(H.items())))
print('kappa naive',kappa(H))
H2=collections.Counter(H)
json.dump(dict(widths=widths,paid={k:{str(a):b for a,b in v.items()} for k,v in paid.items()}),open(sys.argv[3]+'.prov.json','w'))
open(sys.argv[3],'wb').write(gzip.compress(json.dumps(dict(columns=fill['columns'],dispatch_overrides=fill['dispatch_overrides'],rows=rows),separators=(',',':')).encode()))
