import os
import json,gzip,importlib.util
from pathlib import Path
from collections import defaultdict
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('M',P/'frame_model.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
w=json.loads(gzip.decompress(Path(os.environ['K8_BASE_WORD']).read_bytes()));m=M.Model(w);gs=defaultdict(list)
for q,E in w['helper_final'].items():
 q=int(q);prev=m.chains[q][-2];lo=m.lo[prev];old=M.basis(E)
 if len(lo)<len(old):gs[(old,lo)].append(q)
out=[dict(helpers=qs,old=list(old),new=list(new)) for (old,new),qs in gs.items()];(P/'END-GROUPS.json').write_text(json.dumps(out,indent=2)+'\n');print('free',len(m.domain),'groups',len(out));print(json.dumps(out,indent=2))
