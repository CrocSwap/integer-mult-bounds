"""Rebuild PR533's kernel92 supplier and transfer PR534's native-body lifts.
Prepared by OpenAI Codex. Frozen source assignments, no discovery search.
"""
from pathlib import Path
from collections import Counter
import copy,gzip,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'vendor/pr531';out=Path(sys.argv[1]).resolve();assert not out.exists();out.mkdir()
subprocess.run([sys.executable,'-B',str(ROOT/'code/run.py'),str(P/'code/construct_504.py'),str(P/'inputs/hamming'),str(out/'raw')],check=True)
sys.path.insert(0,str(P/'vendor/gk'));import gk_word as G;import gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
raw=json.load(gzip.open(out/'raw/FULL-WORD.json.gz'));selection=json.loads((ROOT/'data/SELECTION.json').read_text());ours=G.build(raw,selection,check=True)
assert sum(len(c['pivots'])for c in selection['kernel'])==92 and len(selection['gauge'])==72
for key in ('global_profile','live','complex_coarse_float','gain_percent_float'):ours['report'].pop(key,None)
ours['report']['local_rank_mass']=sum(int(r)*n for r,n in ours['report']['local_profile'].items())
(out/'SELECTED.json.gz').write_bytes(G.dump(ours))
theirs=json.load(gzip.open(ROOT/'vendor/pr534/FULL-WORD.json.gz'));word=copy.deepcopy(ours);lifts=[]
for sec in ('A','B'):
    count=len(raw[sec]);our_prefix=len(ours[sec])-count;source_prefix=len(theirs[sec])-count
    assert count>0 and min(our_prefix,source_prefix)>=0
    if sec=='B':assert our_prefix==source_prefix==0
    for i,(r,o,t)in enumerate(zip(raw[sec],ours[sec][our_prefix:],theirs[sec][source_prefix:])):
        assert r[:-1]==o[:-1]==t[:-1],(sec,i,'scalar body mismatch')
        assert G.span(r[-1])<=G.span(t[-1]),(sec,i,'not a constructor-frame lift')
        word[sec][our_prefix+i][-1]=copy.deepcopy(t[-1])
        if G.basis(o[-1])!=G.basis(t[-1]):lifts.append(dict(section=sec,index=our_prefix+i,old=o[-1],new=t[-1]))
for key in ('ports','cut','precondition','centers','center_frames','scatter','target_levels'):assert ours.get(key)==theirs.get(key),key
for key in ('start_extra','cleanup'):assert word[key]==ours[key],key
profile=G.profile(word);widths=Counter(G.widths_of(word))
assert sum(r*n for r,n in profile.items())==6228 and widths=={8:164,9:340}
assert len(lifts)==662
word['report'].update(local_profile=dict(sorted(profile.items())),local_rank_mass=6228,status='SAME_SCALAR_BODY_WITH_FROZEN_PR534_FRAME_LIFTS')
framed=out/'framed';framed.mkdir();(framed/'FULL-WORD.json.gz').write_bytes(G.dump(word))
(out/'TRANSFER.json').write_text(json.dumps(dict(status='PASS_EXACT_NATIVE_BODY_FRAME_TRANSFER',source_frame_word_sha256=hashlib.sha256((ROOT/'vendor/pr534/FULL-WORD.json.gz').read_bytes()).hexdigest(),selected_word_sha256=hashlib.sha256((out/'SELECTED.json.gz').read_bytes()).hexdigest(),frame_lifts=len(lifts),local_profile=dict(sorted(profile.items())),widths=dict(widths),unchanged_scalar_body=True,unchanged_kernel_prefix=True,unchanged_cleanup=True,lifts=lifts),indent=2)+'\n')
