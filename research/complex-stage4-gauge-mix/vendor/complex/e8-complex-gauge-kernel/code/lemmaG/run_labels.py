# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
import sys, time, json
from lg_lib import *
import os
SP=os.environ['LG_BASE']          # the output directory of verify.py: <SP>/<variant>/{split-centres,hosted}
out={}
for name in sys.argv[1:]:
    t=time.time(); d=load(f'{SP}/{name}')
    c=d['c']; res={'inputs':d['shas']}
    for o in ('forward','backward'):
        ev=d['progs'][o]; back=o=='backward'
        viol,info,gates=check_labels(c,ev,back); sv=scalar_replay(c,ev,back)
        comp,kern=classify(c,gates)
        res[o]=dict(label_violations=viol[:10],n_label_violations=len(viol),scalar_violations=sv[:5],events=len(ev),sha256=digest(ev),
                    compensation_gates=len(comp),kernel_updates=len(kern),**{k:v for k,v in info.items() if k!='centre_paths'})
    calls=d['tpl']['calls'] if d['tpl'] else []
    res['calls']=dict(n=len(calls),ok=all(cl['local_program_sha256']==res[cl['orientation']]['sha256'] for cl in calls),
                      orient=dict(__import__('collections').Counter(cl['orientation'] for cl in calls)))
    res['seconds']=round(time.time()-t,1); out[name]=res
    print(name, json.dumps({o:{k:res[o][k] for k in ('n_label_violations','scalar_violations','compensation_gates','kernel_updates','entering','entrance_rank','local_mass','paid_profile')} for o in ('forward','backward')}), res['calls'], res['seconds'],flush=True)
    for o in ('forward','backward'):
        for x in res[o]['label_violations'][:5]: print('  ',o,x)
json.dump(out,open('LABELS-'+'-'.join(sys.argv[1:])+'.json','w'),indent=1)
