from pathlib import Path
import json,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[2]
c=json.loads((R/'experiments/architecture/independent-audit/TARGET-PREFIX-SIGNED.json').read_text())['candidates']
# One literal operation per receiver/frame: longest matched prefix at same G.
pairs={}
for e in c:
 if e['rank']<5:continue
 k=e['receiver'],e['donor'],e['frame']
 if k not in pairs or e['prefix_terms']>pairs[k]['prefix_terms']:pairs[k]=e
out=[]
for i,e in enumerate(pairs.values()):
 (P/'PAIR-SELECTION.json').write_text(json.dumps(dict(pairs=[e]),indent=2)+'\n')
 with(P/'screen-local.log').open('w')as f:q=subprocess.run([sys.executable,'-B',P/'construct.py'],stdout=f,stderr=subprocess.STDOUT)
 row=dict(pair=e,passed=q.returncode==0)
 if q.returncode==0:
  a=json.loads((P/'RESULT.json').read_text());row.update(profile=a['profile'],units=a['signed_units'],forward_prefix=a['forward']['prefix'],inverse_prefix=a['inverse']['prefix'])
 else:row['error']=(P/'screen-local.log').read_text()[-1500:]
 out.append(row)
 if i%20==0:print(i,len(pairs),sum(x['passed']for x in out),flush=True)
(P/'SINGLES.json').write_text(json.dumps(dict(status='BOUNDED_ACTUAL_SIGNED_SINGLE_GATE_SCREEN',candidates=out),indent=2)+'\n')
print('done',len(out),sum(x['passed']for x in out))
