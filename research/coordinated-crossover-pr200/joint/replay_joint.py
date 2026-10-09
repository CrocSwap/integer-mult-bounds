from pathlib import Path
import json,hashlib,gzip,sys,time
sys.dont_write_bytecode=True
from joint_word import Candidate,P,D
from terminal import prove
from prime_witnesses import certificate
W=Candidate();pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [*W.input_paths,W.framepath,D/'joint_word.py',D/'joint-selection.json',D/'pairs.json',P/'selected/bit/sinks.json',P/'bit/base_word.py',P/'bit/word.py',P/'bit/terminal.py',P/'bit/prime_witnesses.py',Path(W.module.__file__)]}
W.exact_frames();print('PASS exact frames and alias endpoints',flush=True)
record=prove(W,json.loads((P/'selected/bit/sinks.json').read_text()));record.pop('seconds');record.pop('maxrss');print('PASS full reflected supplier replay',flush=True)
primes=certificate(W);(D/'joint-primes.json.gz').write_bytes(gzip.compress((json.dumps(primes,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
record['input_pins']=pins;record['prime_summary']={k:v for k,v in primes.items()if k!='frame_witnesses'}
assert pins=={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in pins}
(D/'joint-replay.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS joint gauge whole-word and prime admission',record['profile']['child_histogram'],flush=True)

control=Candidate()
omitted=control.newroles[0]
control.order.remove(omitted)
try:control.formal(2)
except ValueError as error:
 assert 'defining decoder' in str(error),str(error)
 print('PASS omitted new compensation read rejected',flush=True)
else:raise AssertionError('Omitted new gauge compensation was accepted')

control=Candidate()
role=next(s for s in control.newroles if control.gauge[s]['dim']==19)
control.order.remove(role);control.order.insert(0,role)
control.exact_frames()
try:control.row()
except (ValueError,AssertionError) as error:
 assert 'target frame chronology' in str(error),str(error)
 print('PASS reversed nested gauge read order rejected',flush=True)
else:raise AssertionError('Rank19 read before rank18 was accepted')
control=Candidate();control.order.remove(role)
try:control.formal(2)
except ValueError as error:
 assert 'defining decoder' in str(error),str(error)
 print('PASS omitted nested rank19 compensation rejected',flush=True)
else:raise AssertionError('Omitted nested compensation was accepted')

for dim in (12,13):
 control=Candidate();role=next(s for s in control.newroles if control.gauge[s]['dim']==dim);control.order.remove(role)
 try:control.formal(2)
 except ValueError as error:
  assert 'defining decoder' in str(error),str(error)
  print('PASS omitted rank'+str(dim)+' shared gauge compensation rejected',flush=True)
 else:raise AssertionError('Shared compensation omission accepted')
