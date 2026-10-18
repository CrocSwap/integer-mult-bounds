"""Check that verifier-command crashes cannot be mistaken for successful logs."""
from pathlib import Path
import os, subprocess, tempfile, time, json, hashlib
P=Path('/tmp/pr-efficient1800');rel=Path('research/two-sided-ten-term-floor');original=P/'prior-revisions/2854-original'/rel;resolved=P/'sources/2854'/rel
start=time.monotonic();results=[]
with tempfile.TemporaryDirectory(prefix='floor-wrapper-') as tmp:
    tmp=Path(tmp);fake=tmp/'fake-python';fake.write_text('''#!/bin/sh
case "$2" in
 *manifest_check.py) if [ "$FAIL_STAGE" = manifest ]; then exit 7; fi; echo 'PASS synthetic manifest';;
 *check_logs.py) if [ "$FAIL_STAGE" = summary ]; then exit 7; fi; echo 'PASS synthetic assertions';;
 -) for n in 0 1 2 3; do : > "ics_$n.txt"; done;;
esac
exit 0
''');fake.chmod(0o755)
    for stage in ['manifest','summary']:
        for label,pkg in [('original',original),('resolved',resolved)]:
            env=dict(os.environ,PYTHON=str(fake),JOBS='2',FAIL_STAGE=stage)
            r=subprocess.run(['bash',str(pkg/'verify.sh'),str(tmp/(label+'-'+stage))],capture_output=True,text=True,env=env,timeout=30)
            assert r.returncode==(0 if label=='original' else 1),(stage,label,r.returncode,r.stdout,r.stderr)
            results.append(dict(stage=stage,version=label,returncode=r.returncode))
out=dict(status='passed',seconds=time.monotonic()-start,checks=results,scope='Synthetic executor failures: original wrapper accepts a silent manifest/summary-command crash; resolved wrapper rejects both. No mathematical execution is mocked in the separate full census replay.')
(P/'provenance-2854-wrapper.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
