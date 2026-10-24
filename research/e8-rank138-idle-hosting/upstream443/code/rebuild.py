"""Reconstruct primitive retiming and the kernel with 32 exact bank replicas.
Prepared by chafreaky with OpenAI Codex assistance; Apache-2.0.
"""
import copy
import json
from pathlib import Path
from e8core import load_word, replay
from iface386 import check
from stages import content_sha, retime
from replica_kernel import kernel
from config import REPLICAS

ROOT=Path(__file__).resolve().parents[1]
parent=load_word(str(ROOT/'parent436/data/bit/bitE8-r740.json.gz'))
timing=json.loads((ROOT/'data/retiming.json').read_text())
assert content_sha(parent)==timing['input_sha256']
primitive=copy.deepcopy(parent)
for phase in ('D','A','B','C'):
    primitive[phase]=[[f,d,[s]] for f,d,ss in parent[phase] for s in ss]
retimed=retime(primitive,timing['changes'])
assert len(timing['changes'])==57 and content_sha(retimed)==timing['output_sha256']
for phase in ('D','A','B','C'):
    assert [(d,s) for f,d,ss in parent[phase] for s in ss]==[(d,s) for f,d,ss in retimed[phase] for s in ss]
selected=json.loads((ROOT/'data/selection.json').read_text())
assert content_sha(retimed)==selected['input_sha256']
word,entries,rank,donors=kernel(retimed,selected['entries'],REPLICAS)
assert (entries,rank,donors,REPLICAS)==(114,138,103,32)
assert content_sha(word)==selected['output_sha256']
post=json.loads((ROOT/'data/post-retiming.json').read_text())
assert [len(s['gates']) for s in post]==[112,42]
for stage in post:
    original=json.loads((ROOT/'data/upstream441'/stage['source']).read_text())
    assert stage['gates']==original['gates'] and all(g[0]=='B' for g in stage['gates'])
    assert content_sha(word)==stage['input_sha256']
    word=retime(word,stage['gates'])
    assert content_sha(word)==stage['output_sha256']
assert word==load_word(str(ROOT/'data/word.json.gz'))
audit=replay(word,span_mode='z');assert not audit['viol'],audit['viol'][:5]
interface=check(word,192);assert interface['prefix_ok']

rejected=[]
for name,mutate in [
    ('retained row used as pivot',lambda s:s[0].__setitem__(1,parent['ret'][0])),
    ('duplicate pivot',lambda s:s.append(copy.deepcopy(s[0]))),
]:
    bad=copy.deepcopy(selected['entries']);mutate(bad)
    try:kernel(retimed,bad,REPLICAS)
    except AssertionError:rejected.append(name)
    else:raise AssertionError('accepted invalid kernel selection: '+name)
try:kernel(retimed,selected['entries'],8)
except AssertionError:rejected.append('eight replicas do not fill integral banks')
else:raise AssertionError('accepted nonintegral bank stock')
bad=copy.deepcopy(word);bad['A'][0][2].pop()
try:bad_audit=replay(bad,span_mode='z')
except AssertionError:pass
else:assert bad_audit['viol'],'missing dirty-response correction accepted'
rejected.append('omit a kernel dirty-response correction')
bad=copy.deepcopy(timing['changes']);bad[0][2]=[]
try:retime(primitive,bad)
except AssertionError:rejected.append('wrong primitive input frame')
else:raise AssertionError('accepted incorrect frame binding')
print(json.dumps(dict(status='PASS_FROZEN_RETIMING_KERNEL_REPLICA_REBUILD',
    input_sha256=content_sha(parent),retimed_sha256=content_sha(retimed),output_sha256=content_sha(word),
    pre_kernel_frame_changes=57,post_kernel_frame_changes=[112,42],entries=entries,entrance_rank=rank,donor_slots=donors,replicas=REPLICAS,
    interface=interface,mutations_rejected=rejected),sort_keys=True))
