"""Reconstruct the hosted-cost-selected kernel from the pinned R740 precursor.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
import gzip,hashlib,json,sys
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'e8-rank138-idle-hosting'
UP=PRIOR/'upstream443'
read=lambda p:json.loads(p.read_text())
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
w=json.loads(gzip.decompress((UP/'parent436/data/bit/bitE8-r740.json.gz').read_bytes()))
for ph in ('D','A','B','C'):w[ph]=[[f,d,[s]] for f,d,ss in w[ph] for s in ss]
ids={tuple(sorted(f)):i for i,f in enumerate(w['frames'])}
for ph,i,old,new in read(UP/'data/retiming.json')['changes']:
    assert sorted(w['frames'][w[ph][i][0]])==sorted(old)
    w[ph][i][0]=ids[tuple(sorted(new))]
priorword=json.loads(gzip.decompress((UP/'data/word.json.gz').read_bytes()))
assert len(w['B'])==len(priorword['B']) and all(a[1:]==b[1:] for a,b in zip(w['B'],priorword['B']))
w['B']=priorword['B']
sel=read(ROOT/'SELECTION.json')
assert hashlib.sha256(canonical(w)).hexdigest()==sel['frozen_precursor_sha256'] and w==read(ROOT/'PRECURSOR.json')
sys.path.insert(0,str(UP/'code'))
from replica_kernel import kernel
from e8core import replay
out,entries,rank,donors=kernel(w,sel['entries'],sel['replicas'])
a=replay(out,span_mode='z');assert not a['viol']
assert dict(a['H'])=={int(k):n for k,n in sel['local_profile'].items()}
assert out==read(ROOT/'WORD.json') and out['frames']==w['frames']
raw=canonical(out);receipt=dict(status='PASS_RECONSTRUCTED_HOSTING_SELECTED_KERNEL',entries=entries,total_entrance_rank=rank,donor_slots=donors,new_frames=0,output_sha256=hashlib.sha256(raw).hexdigest(),local_columns=a['n'],local_profile=dict(a['H']))
d=Path(sys.argv[1]);d.mkdir();(d/'bit-source-centres.json').write_bytes(raw);(d/'bit-kernel-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,sort_keys=True))
