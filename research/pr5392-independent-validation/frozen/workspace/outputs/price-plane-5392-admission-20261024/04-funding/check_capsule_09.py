#!/usr/bin/env python3
"""Read-only consumer authentication of later09scientific provenance capsule."""
from pathlib import Path
import json
from invoice import H,W,HEAD,BASE,PKG,read,sha,checked,need
C=W/'09-cold/capsule-5392-v1';expected='43cc19d5b9b0200693cba33b5d0d8b593f45104f37b261969e1ab3c9626d149c'
need(sha(C/'IMMUTABLE-MANIFEST.json')==expected,'later09manifest drift');m=read(C/'IMMUTABLE-MANIFEST.json');need((m['candidate_head'],m['canonical_main'],m['package'])==(HEAD,BASE,PKG),'later source pins mismatch')
for row in m['rows']:checked(row,(C/row['capsule_path']).read_bytes())
need(all(r['candidate_ancestor_exit']==0 for r in m['history']),'registered runtime source is not candidate ancestor')
need(next(r for r in m['history'] if r['commit']==BASE)['canonical_ancestor_exit']==0,'canonical base ancestry failed')
newrows={r['path']:r for r in m['rows'] if r['source_commit']==HEAD}
for row in read(W/'source-capsule/ROOT-MANIFEST.json')['rows']:need(newrows[row['path']]['sha256']==row['sha256'] and newrows[row['path']]['git_blob']==row['git_blob'],'earlier23root and54rowlatercapsule disagree')
a={'status':'PASS_CONSUMER_54_ROW_PRIMARY_RUNTIME_SOURCE_BINDINGS','candidate_head':HEAD,'capsule_manifest_sha256':expected,'rows_rechecked':len(m['rows']),'matches_initial23_root_rows':True,'primary_runtime_pin_ancestry':m['history'],'original_source_bindings':m['original_source_bindings'],'funding_receipt_sha256':sha(H/'FUNDING-v2.json'),'scope':'Independent consumer blob/SHA check. Primary vendored pin5eb is candidate ancestor and is explicitly not canonical-main ancestor. Original-source descriptive metadata retains producer statuses; no absent source history is silently accepted. Source-history/export/cold publication assembly is separate09/root work.'}
p=H/'SOURCE-CONSUMER-v1.json';need(not p.exists(),'immutable source consumer receipt exists');p.write_text(json.dumps(a,sort_keys=True,indent=2)+'\n');p.chmod(0o444);print(json.dumps({'sha256':sha(p),'rows':len(m['rows'])}))
