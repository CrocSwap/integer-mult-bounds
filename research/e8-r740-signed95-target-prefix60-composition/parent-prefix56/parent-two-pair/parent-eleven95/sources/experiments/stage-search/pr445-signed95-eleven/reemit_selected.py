"""Stdlib exact selected collective word reemission; no discovery solver."""
from pathlib import Path
from collections import defaultdict
import json,gzip,hashlib,copy,subprocess,sys
P=Path(__file__).resolve().parent;S=P/'signed';ROOT=P.parents[2]
sel=json.loads((S/'SELECTION.json').read_text());base=json.loads((S/'baseline.json').read_text());word=json.loads((S/'word.json').read_text());frames={tuple(f):i for i,f in enumerate(word['frames'])};groups=defaultdict(list);ps=set()
assert hashlib.sha256((S/'baseline.json').read_bytes()).hexdigest()==sel['source_sha256']
w=copy.deepcopy(base);w['frames']=word['frames']
for e in sel['entries']:
 p=e['pivot'];assert p not in ps;ps.add(p);f=frames[tuple(e['entrance'])];w['start'][p]=f
 for d,c in e['donor_coefficients']:groups[d,f].extend([p]*abs(c))
assert not ps&{d for d,f in groups} and len(ps)==95
w['A']=[[f,d,sorted(v)]for(d,f),v in sorted(groups.items())]+w['A'];w['C']+=[[base['final'][0],d,sorted(v)]for(d,f),v in sorted(groups.items())];w['D']=[[f,d,[s for s in ss if s not in ps]]for f,d,ss in w['D']]
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();assert raw==(S/'word.json').read_bytes()==(P/'word.json').read_bytes();assert gzip.decompress((S/'word.json.gz').read_bytes())==gzip.decompress((P/'word.json.gz').read_bytes())==raw;assert hashlib.sha256(raw).hexdigest()==sel['output_sha256']
out=P/'reemit-records';out.mkdir(exist_ok=True);export=ROOT/'experiments/bit-search/pr434/source/research/split-centres-global/vendor/export_records.py';subprocess.run([sys.executable,'-B',str(export),str(S/'word.json'),str(out)],check=True)
for n in ['249-records.bin','249-states.json','frames.json']:assert(out/n).read_bytes()==(S/'records'/n).read_bytes(),n
print('PASS exact collective selected word and native record reemission')
