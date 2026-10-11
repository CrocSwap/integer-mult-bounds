"""Reconstruct rank151 kernel from the frozen PR436 word and PR440/441 retiming.
Chafreaky with OpenAI Codex assistance; upstream notices in NOTICE.md. Apache-2.0.
"""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'e8-r740-replica32'
sys.path.insert(0,str(OLD/'code'))
from e8core import load_word,replay
from stages import content_sha,retime
from iface386 import check
from hosted_kernel import kernel
parent=load_word(str(OLD/'parent436/data/bit/bitE8-r740.json.gz'))
timing=json.loads((OLD/'data/retiming.json').read_text());assert content_sha(parent)==timing['input_sha256']
primitive=copy.deepcopy(parent)
for phase in ('D','A','B','C'):primitive[phase]=[[f,d,[s]] for f,d,ss in parent[phase] for s in ss]
retimed=retime(primitive,timing['changes']);assert len(timing['changes'])==57 and content_sha(retimed)==timing['output_sha256']
selected=json.loads((ROOT/'data/kernel.json').read_text());word,entries,rank,donors=kernel(retimed,selected)
assert (entries,rank)==(123,151)
hashes=[content_sha(retimed),content_sha(word)]
for name in ['pair-retime-selection.json','window-retime-selection.json']:
 stage=json.loads((OLD/'data/upstream441'/name).read_text());assert all(g[0]=='B' for g in stage['gates'])
 assert len(stage['gates'])==dict(zip(['pair-retime-selection.json','window-retime-selection.json'],[112,42]))[name]
 word=retime(word,stage['gates']);hashes.append(content_sha(word))
import subprocess,tempfile,gzip as _gz
with tempfile.TemporaryDirectory() as td:
 src=Path(td)/'in.json';dst=Path(td)/'out.json';src.write_text(json.dumps(word))
 mixinfo=subprocess.run([sys.executable,'-B',str(ROOT/'code/mix_target.py'),str(src),str(dst)],check=True,capture_output=True,text=True).stdout
 word=json.loads(dst.read_text())
mixinfo=json.loads(mixinfo);assert mixinfo['receivers']==46,mixinfo
hashes.append(content_sha(word))
assert word==load_word(str(ROOT/'data/word.json.gz'))
assert content_sha(word)=='bc1a9cc3b8d2277674a39ef580bd77b48d8d7eedecd93fc295b869b49b94005d'
audit=replay(word,span_mode='z');assert not audit['viol'],audit['viol'][:5]
interface=check(word,192);assert interface['prefix_ok']
rejected=[]
for name,mutate in [('retained row pivot',lambda s:s[0].__setitem__(1,parent['ret'][0])),('duplicate pivot',lambda s:s.append(copy.deepcopy(s[0])))]:
 bad=copy.deepcopy(selected);mutate(bad)
 try:kernel(retimed,bad)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('accepted '+name)
bad=copy.deepcopy(word);bad['A'][0][2].pop()
try:res=replay(bad,span_mode='z')
except AssertionError:pass
else:assert res['viol']
rejected.append('omit dirty response correction')
print(json.dumps(dict(status='PASS_RANK151_REBUILD',word_sha256=content_sha(word),intermediate_hashes=hashes,
 entries=entries,target_mix=mixinfo,entrance_rank=rank,donor_slots=donors,local_columns=audit['n'],local_profile=dict(sorted(audit['H'].items())),
 interface=interface,mutations_rejected=rejected),sort_keys=True))
