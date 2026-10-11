"""PR417/435 independent all-column replay, including integer source-span legality."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'vendor/kernel417'))
from e8core import Lat,replay
w=json.loads(Path(sys.argv[1]).read_text());frames=json.loads(Path(sys.argv[2]).read_text())['frames'];L=Lat(w['lines']);masks=[sum(1<<x for x in f) for f in w['frames']]
# These ranks/bases are independently checked over Q by bit_audit.py in the wrapper.
for i,m in enumerate(masks):L._close[m]=m;L._dim[m]=frames[str(i)]['dim']
r=replay(w,L=L,masks=masks,span_mode='z');assert not r['viol'],r['viol'][:10]
print(json.dumps(dict(status='PASS_INDEPENDENT_F2_AND_INTEGER_SOURCE_SPANS',columns=r['n'],profile=dict(r['H']),word_sha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())))
