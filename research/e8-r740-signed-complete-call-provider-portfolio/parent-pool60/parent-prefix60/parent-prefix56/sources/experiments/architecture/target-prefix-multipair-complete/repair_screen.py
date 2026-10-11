from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parent;x=json.loads((P/'SINGLES.json').read_text())
for e in x['candidates']:
 if e['passed']:continue
 (P/'PAIR-SELECTION.json').write_text(json.dumps(dict(pairs=[e['pair']]),indent=2)+'\n')
 with(P/'repair.log').open('w')as f:q=subprocess.run([sys.executable,'-B',P/'construct.py'],stdout=f,stderr=subprocess.STDOUT)
 e['previous_failure']=e.pop('error');e['passed']=q.returncode==0
 if e['passed']:
  a=json.loads((P/'RESULT.json').read_text());e.update(profile=a['profile'],units=a['signed_units'],forward_prefix=a['forward']['prefix'],inverse_prefix=a['inverse']['prefix'])
 else:e['error']=(P/'repair.log').read_text()[-1500:]
 print(e['pair']['receiver'],e['passed'],flush=True)
x['status']='ACTUAL_SINGLES_LAST_DONOR_FRAME_CUT_CORRECTION';(P/'SINGLES.json').write_text(json.dumps(x,indent=2)+'\n')
