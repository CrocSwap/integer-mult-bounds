"""Carry the predecessor relative-root repair into a new immutable version."""
import json
import re
from pathlib import Path
D=Path(__file__).resolve().parent
P=D/'repair-v2';N=D/'repair-v3'
assert not N.exists();N.mkdir()
for base in ('implementation','proof'):
    for p in (P/base).rglob('*'):
        if not p.is_file():continue
        q=N/p.relative_to(P);q.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes()
        if '/stages/' not in str(p) and p.suffix in ('.py','.json'):
            raw=raw.replace(str(P).encode(),str(N).encode())
            # The first assembly's builder already handled root-relative literals.
            # Preserve that repair when versioning, as well as absolute roots.
            raw=raw.replace(b"'outputs/connected-caller-assembly-20261107T2053Z'",
                            b"'outputs/connected-caller-assembly-20261107T2053Z/repair-v3'")
        q.write_bytes(raw);q.chmod(0o444)
for name in ('build_source_assembly.py','freeze_source_assembly.py'):
    (N/name).write_bytes((P/name).read_bytes())
(N/'control').mkdir();(N/'validation').mkdir()
for p in (P/'validation').glob('test_*.py'):(N/'validation'/p.name).write_bytes(p.read_bytes())
(N/'control/REPAIR-RECONCILIATION-v1.json').write_text(json.dumps({'prior_failed_version':str(P),'failure':'Eight targeted controls passed, including all six timer regressions; two source/loader checks correctly rejected fixed Python paths still selected by root-relative literals at v1.','recurrence_reconciliation':'The original builder repaired both absolute and root-relative paths. The first version-copy carried only the absolute repair. This version carries the exact predecessor relative-root repair rather than weakening loader checks. Failed v2 manifest/source/results remain unchanged.','actual_source_controls_must_recheck':True,'original_credit_delta':0},indent=2)+'\n')
print(str(N))
