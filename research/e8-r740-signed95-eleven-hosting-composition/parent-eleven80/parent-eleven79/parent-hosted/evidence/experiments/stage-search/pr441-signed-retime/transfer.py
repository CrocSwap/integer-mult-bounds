from pathlib import Path
import json,hashlib,copy
P=Path(__file__).resolve().parent;ROOT=P.parents[2];S=ROOT/'experiments/verification/proposal-scout/pr441/stages';B=ROOT/'experiments/stage-search/pr440-signed-retime'
canon=lambda w:json.dumps(w,sort_keys=True,separators=(',',':')).encode()
sha=lambda w:hashlib.sha256(canon(w)).hexdigest()
old=json.loads((ROOT/'experiments/stage-search/pr440-source/stages/final-word.json').read_bytes());final=json.loads((S/'final-word.json').read_bytes());q=json.loads((B/'baseline.json').read_bytes());w=json.loads((B/'word.json').read_bytes());sel=json.loads((B/'SELECTION.json').read_bytes())
assert sha(old)=='bae58f0692326f180ba49642360fd55557f59a93a96a8fa62bf7babd55d2384e'
assert sha(final)=='00d8aa8608e40b53fd8752399de06cb730cc55caaadc528f88379cb31b8460a6'
assert old['frames']==final['frames']==q['frames'];assert old['B']==q['B']==w['B'];assert all(old[ph]==final[ph]for ph in ('A','C','D'))
current=copy.deepcopy(old);fmap={tuple(sorted(f)):i for i,f in enumerate(q['frames'])};receipts=[]
for name in ('pair-retime-selection.json','window-retime-selection.json'):
 r=json.loads((S/name).read_bytes());assert sha(current)==r['input_sha256']
 for ph,i,of,nf in r['gates']:
  assert ph=='B';assert tuple(sorted(current[ph][i][0] and current['frames'][current[ph][i][0]] or current['frames'][0]))==tuple(sorted(of))
  current[ph][i][0]=fmap[tuple(sorted(nf))]
 assert sha(current)==r['output_sha256'];receipts.append(dict(file=name,sha256=hashlib.sha256((S/name).read_bytes()).hexdigest(),changes=len(r['gates'])))
assert current==final
moves=[]
for i,(a,b)in enumerate(zip(old['B'],final['B'])):
 assert a[1:]==b[1:]
 if a[0]!=b[0]:moves.append(dict(index=i,old_frame=a[0],new_frame=b[0],destination=a[1],sources=a[2]))
assert len(moves)==126
q['B']=copy.deepcopy(final['B']);w['B']=copy.deepcopy(final['B']);sel['source_sha256']=sha(q);sel['output_sha256']=sha(w)
for name,obj in [('baseline.json',q),('word.json',w),('SELECTION.json',sel)]: (P/name).write_bytes(canon(obj))
report=dict(status='FRAME_TRANSFER_NOMINATION_REQUIRES_SIGNED_ADMISSION',source='https://github.com/CrocSwap/integer-mult-bounds/pull/441',head='6160c13526f5f957902910b462164c93c1d8f39a',candidate_sha256=sha(w),baseline_sha256=sha(q),prior_signed_candidate_sha256=sha(json.loads((B/'word.json').read_bytes())),source_selection=receipts,moves=moves)
(P/'TRANSFER.json').write_bytes(canon(report));print(report['candidate_sha256'])
