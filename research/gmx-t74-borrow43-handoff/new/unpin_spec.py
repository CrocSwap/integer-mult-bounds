"""Discovery -> unpin -> freeze.  After a --discover replay, remove from the SPEC every expected/pinned value that the independent
recomputation (WITNESS-RECORD.jsonl) disagrees with (stale values from the pre-borrow package), listing each one; values that
agree are kept as independent cross-checks.  freeze_spec.py then writes the recomputed values.  usage: unpin_spec.py SPEC DISCOVERY_DIR"""
import json,sys
from pathlib import Path
spec_path,disc=Path(sys.argv[1]),Path(sys.argv[2]);spec=json.loads(spec_path.read_text());removed=[];kept=0
for line in (disc/'WITNESS-RECORD.jsonl').read_text().splitlines():
    key,value=json.loads(line);parts=key.split('.')
    if len(parts)>3 and parts[0]=='providers' and parts[2]=='artifacts':parts=parts[:3]+['.'.join(parts[3:])]
    t=spec
    for p in parts[:-1]:
        t=t.get(p) if isinstance(t,dict) else None
        if t is None:break
    if isinstance(t,dict) and parts[-1] in t:
        if t[parts[-1]]!=value:removed.append(key);del t[parts[-1]]
        else:kept+=1
spec_path.write_text(json.dumps(spec,indent=2)+'\n');print('unpinned',len(removed),'kept-agreeing',kept);[print(' ',k) for k in removed]
