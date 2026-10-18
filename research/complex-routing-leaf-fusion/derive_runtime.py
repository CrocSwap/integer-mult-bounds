#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Apply the credited PR2733 frame refit to an authenticated PR2751 runtime.
The predecessor is copied before this function runs. Its four changed paths,
exact preimages, and complete final manifest are checked; all original audits
and mutations remain in the runtime, with one new omission control added.
"""
import json,gzip,hashlib,shutil
from pathlib import Path

REBUILD_INSERT="    # Compose PR2733's exact five-frame refit with PR2751's twelve-source word.\n    # Gate identity and both profiles are checked; no original control is removed.\n    import copy as refit_copy\n    previous_joint=chain[-1]\n    assert previous_joint['B'][1151]==['add',393,515,1,1,[259,132,66,36,16,9]]\n    assert previous_joint['report']['local_profile']=={'1':2366,'2':646,'3':297,'4':120,'5':26,'8':8}\n    refined=refit_copy.deepcopy(previous_joint)\n    refined['B'][1151][-1]=[259,148,66,36,9]\n    refined['report']['local_profile']={'1':2364,'2':647,'3':297,'4':120,'5':26,'8':8}\n    assert refined['cleanup']==previous_joint['cleanup']\n    chain.append(refined);steps.append('joint-twelve-refit393')\n"
REBUILD_CONTROL="        # Undo just this refit while retaining its cheaper invoice: reject it.\n        omitted=refit_copy.deepcopy(final);omitted['B'][1151][-1]=previous_joint['B'][1151][-1]\n        omitted_path=Path(tempfile.mkdtemp())/'refit393_omitted.json.gz'\n        omitted_path.write_bytes(gzip.compress(json.dumps(omitted,separators=(',',':')).encode(),mtime=0))\n        omitted_run=run_audit(omitted_path,None,omitted_path.parent/'audit.json')\n        omitted_ok=omitted_run.returncode!=0 and 'paid profile mismatch' in (omitted_run.stdout+omitted_run.stderr)\n        ok&=omitted_ok;res['refit393_omission_rejected_by_profile']=omitted_ok\n"

def derive_runtime(D, C):
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    orig=json.loads((D/'MANIFEST.json').read_text());patch=json.loads((C/'PATCH.json').read_text())
    for tag in ['base','extra']:
     src=C/'inputs'/f'WORD-{tag}.json.gz';dst=D/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
     assert sha(dst)==patch['providers'][tag]['source_sha256'];shutil.copy2(src,dst)
    p=D/'new/BORROW-PROVIDERS.json';j=json.loads(p.read_text())
    for v in j.values():
     assert v['actual_paid_profile']=={'1':2366,'2':646,'3':297,'4':120,'5':26,'8':8}
     v['actual_paid_profile']={'1':2364,'2':647,'3':297,'4':120,'5':26,'8':8}
    p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
    p=D/'new/rebuild_borrow.py';s=p.read_text();old='    final=json.loads(gzip.decompress(shipped.read_bytes()))\n';assert s.count(old)==1
    new=REBUILD_INSERT+old
    s=s.replace(old,new)
    old="    if '--no-controls' not in sys.argv:\n";assert s.count(old)==1
    new=old+REBUILD_CONTROL
    s=s.replace(old,new);p.write_text(s)
    # Exclude only root manifest; nested manifests remain authenticated.
    new={p.relative_to(D).as_posix():sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p!=D/'MANIFEST.json'}
    assert set(new)==set(orig)
    (D/'MANIFEST.json').write_text(json.dumps(new,sort_keys=True,indent=2)+'\n')
    changes={n:{'before':orig[n],'after':h} for n,h in new.items() if h!=orig[n]}
    return changes
