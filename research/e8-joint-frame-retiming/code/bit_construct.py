"""Rebuild pinned PR436's R740 word from its producer parameters, reuse, and retiming.
PR436: eumemic with Anthropic Claude assistance; this integration: OpenAI Codex.
"""
import gzip, hashlib, json, os, subprocess, sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent
D=Path(os.environ['E8_OUTPUT'])/'bit426-source-centres'; D.mkdir(exist_ok=True)
B=P/'vendor/pr436'
subprocess.run([sys.executable,'-B',str(B/'code/reuse/regen.py'),str(B/'data/params/params-r740.json'),
 str(D/'pr436-raw.json.gz'),str(D/'pr436-reused.json.gz'),str(D/'pr436-final.json.gz'),str(D/'pr436-ledger.json')],check=True)
w=json.loads(gzip.decompress((D/'pr436-final.json.gz').read_bytes()))
pinned=json.loads(gzip.decompress((B/'data/bit/bitE8-r740.json.gz').read_bytes()))
assert w==pinned
assert json.loads((D/'pr436-ledger.json').read_text())==json.loads((B/'data/bit/reuse-ledger.json').read_text())
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(raw).hexdigest()=='d6ec8811541d6ab59a3bbbaaa15bccc8918b3b43b23d9f593198cfe90826fd20'
assert w['R']==740 and len(w['ret'])==9
(D/'bit-source-centres.json').write_bytes(raw)
sys.path.insert(0,str(P/'vendor/kernel417'))
from e8core import replay
r=replay(w,span_mode='z');assert not r['viol'],r['viol'][:5]
res=dict(status='PASS_PINNED_PR436_RECONSTRUCTION',R=w['R'],content_sha256=hashlib.sha256(raw).hexdigest(),
 all_columns=r['n'],local_histogram=dict(sorted(r['H'].items())),
 construction='Pinned #370 producer with #436 parameters, elimination reuse and six retiming sweeps; exact frozen #436 word and ledger equality')
(D/'bit-source-centres-receipt.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res))
