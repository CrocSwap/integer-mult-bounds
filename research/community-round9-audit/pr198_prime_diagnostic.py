import sys,json,gzip
from pathlib import Path
base=Path('/tmp/integer-mult-export198/research/paired-cube-twin-local-168/bit');sys.path.insert(0,str(base))
from word import Candidate
from prime_witnesses import certificate
w=Candidate();w.exact_frames();w.row();r=certificate(w);old=json.loads(gzip.decompress((base/'prime-witnesses.json.gz').read_bytes()))
different=[k for k in r if r[k]!=old.get(k)]
result=dict(different_top_fields=different,all_exact_frame_witnesses_identical=r['frame_witnesses']==old['frame_witnesses'])
if 'input_sha256'in different:result['input_hash_differences']={k:[v,old['input_sha256'].get(k)] for k,v in r['input_sha256'].items()if v!=old['input_sha256'].get(k)}
for k in different:
 if k not in ('frame_witnesses','input_sha256'):result[k]={'fresh':r[k],'saved':old.get(k)}
print(json.dumps(result,indent=2))
Path('/tmp/integer-mult-pr198-prime-fresh.json').write_text(json.dumps(r))
