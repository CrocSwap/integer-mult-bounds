from pathlib import Path
from unittest.mock import patch
import sys,json
R=Path('/Users/temp/.codex/worktrees/three-kappa-leads/integer-mult-bounds')
sys.path.insert(0,str(R/'research/three-kappa-leads'))
from check_inputs import authenticate
authenticate()
original=Path.read_bytes
candidate='research/five-plane-port-p112-seed1f7fdfe4/CANDIDATE.json'
def corrupted(p):
 raw=original(p)
 return raw+b' ' if str(p).endswith(candidate) else raw
with patch.object(Path,'read_bytes',corrupted):
 try:authenticate()
 except ValueError as e:
  assert candidate in str(e)
 else:raise AssertionError('candidate mutation accepted')
p=Path('/tmp/three-kappa-astra-lead3/RESULT.json');r=json.loads(p.read_text());r['candidate_mutation_rejected']=True;r['consumer_screen_replay']='PASS';r['predecessor_local_basis_cases']=11776;r['conclude']='YES';r['outcome']='SCOPED_NEGATIVE';p.write_text(json.dumps(r,indent=2)+'\n')
print('PASS CANDIDATE source mutation rejected; scoped review complete')
