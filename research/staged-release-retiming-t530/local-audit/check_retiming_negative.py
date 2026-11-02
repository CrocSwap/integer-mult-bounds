#!/usr/bin/env python3
"""Exercise credited inherited free-algebra checker on semantic retiming mutations."""
from pathlib import Path
from copy import deepcopy
import argparse,tempfile
import gzip,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
WORDS=HERE/'words'
CHECKER=HERE/'vendor/audit_local.py'
old=json.loads(gzip.decompress((WORDS/'STAGED644-660-base.json.gz').read_bytes()))
new=json.loads(gzip.decompress((WORDS/'RETIMED644-660-base.json.gz').read_bytes()))
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path);args=parser.parse_args()
OUT=args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='retiming-negative-'))
if OUT==HERE or HERE in OUT.parents:raise ValueError('output must be outside package')
if args.out and OUT.exists():raise ValueError('fresh output directory required')
OUT.mkdir(parents=True,exist_ok=True)
mutations=[]
bad=deepcopy(new)
bad['B'][591:593]=[old['B'][591][:-1]+[new['B'][592][-1]],old['B'][592]]
mutations.append(('raised_frame_before_release',bad,'frame not monotone'))
bad=deepcopy(new);bad['B'][592][-1]=old['B'][591][-1]
mutations.append(('invoice_without_frame_jump',bad,'paid profile mismatch'))
bad=deepcopy(new);bad['B'][592][3]=3
matched=[i for i,g in enumerate(bad['cleanup']) if g[:5]==['add',640,644,-2,1]]
assert len(matched)==1,matched
bad['cleanup'][matched[0]][3]=-3
mutations.append(('coefficient_with_matching_inverse',bad,'target map failed'))
bad=deepcopy(new);bad['cleanup']=deepcopy(old['cleanup'])
mutations.append(('old_literal_cleanup_order',bad,'explicit cleanup differs'))
receipts=[]
for name,bad,expected in mutations:
    path=OUT/(name+'.json.gz');path.write_bytes(gzip.compress(json.dumps(bad,separators=(',',':')).encode(),mtime=0))
    command=[sys.executable,'-B',str(CHECKER),'--word',str(path),'--output',str(OUT/(name+'.result.json'))]
    done=subprocess.run(command,capture_output=True,text=True)
    (OUT/(name+'.log')).write_text(done.stdout+done.stderr)
    if done.returncode==0 or expected not in done.stderr:raise RuntimeError(name+': '+done.stdout+done.stderr)
    receipts.append(dict(name=name,expected_rejection=expected,returncode=done.returncode,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),log_sha256=hashlib.sha256((done.stdout+done.stderr).encode()).hexdigest()))
    print('REJECT',name,expected)
result=dict(status='PASS_SEMANTIC_RETIMING_NEGATIVE_CONTROLS',checker_sha256=hashlib.sha256(CHECKER.read_bytes()).hexdigest(),controls=receipts,scope='Inherited exact free-operator checker. Cleanup-order control checks literal inverse-reverse canonicality; the unchanged old cleanup remains operator-equivalent because the inverse shears commute.')
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
