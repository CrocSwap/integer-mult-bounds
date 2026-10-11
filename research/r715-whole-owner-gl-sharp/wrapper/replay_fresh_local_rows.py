"""Independent local-row replay using chafreaky's pinned PR458 auditor.

Adapts PR471's wrapper event names, preserving every body event and auditing
the source-bound monomial circuits separately through normalize-local.py.
No numerical kappa claim is made by this check. OpenAI Codex assistance.
"""
import gzip,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;P=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'vendor/transport/receipts79'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'INDEPENDENT-LOCAL-ROWS.json'
sys.path.insert(0,str(ROOT.parent/'complex/vendor/transport'))
spec=importlib.util.spec_from_file_location('audit458',ROOT/'pr458_local_audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
c=json.loads(gzip.decompress((P/'CANONICAL-WORD.json.gz').read_bytes()))
programs=json.loads(gzip.decompress((P/'NORMALIZED-PROGRAMS.json.gz').read_bytes()))
result={}
for orientation,program in programs.items():
    events=[]
    for z in program:
        if z[0]=='monomial-wrapper':
            events.append(['residual_adapter','pre' if z[1]=='entry' else 'post',z[2],z[3]])
        else:events.append(z)
    result[orientation]=audit.replay(c,events,orientation=='backward')
DEST.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
