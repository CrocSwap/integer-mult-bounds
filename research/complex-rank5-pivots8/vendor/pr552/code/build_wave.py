from pathlib import Path
import argparse,json,gzip,hashlib,copy,sys
if not __debug__:raise SystemExit('Assertions must remain enabled.')
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--gk',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.gk.resolve()))
import gk_word as g,gk_common as c
g.V=c.V=112;g.DATA=c.DATA=7168
w=json.loads(gzip.decompress(a.input.read_bytes()));old=copy.deepcopy(w);recipe=json.loads(a.recipe.read_text());canon=lambda z:json.dumps(z,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(canon(w)).hexdigest()==recipe['source_canonical_sha256']
before=g.profile(w);controls=[];changes=[]
for k,move in enumerate(recipe['passes']):
 previous=copy.deepcopy(w);covectors=move.get('covectors',[move.get('v')]);assert all(isinstance(v,int)and 0<v<512 for v in covectors)
 for sec,i in move['events']:
  assert sec in ('A','B');E=w[sec][i][-1];new=g.basis(x for x in g.span(E)if all((x&v).bit_count()%2==0 for v in covectors));assert len(new)<len(g.basis(E));w[sec][i][-1]=list(new)
 after=g.profile(w)
 # At least one omitted frame change in each collective wave must violate an actual register chain.
 rejected=None
 for sec,i in move['events']:
  changed=w[sec][i][-1];w[sec][i][-1]=previous[sec][i][-1]
  try:g.profile(w)
  except AssertionError:rejected=[sec,i]
  finally:w[sec][i][-1]=changed
  if rejected is not None:break
 assert rejected is not None,('no collective-dependency negative control',k)
 controls.append({'wave':k,'omitted_event':rejected,'rejected':True});changes.append({'wave':k,'events':len(move['events']),'covectors':covectors,'profile':dict(after)})
after=g.profile(w)
assert dict(after)=={1:2300,2:440,3:472,4:184,5:56,6:56,8:8}
for key in old:
 if key not in ['A','B','cleanup','report']:assert old[key]==w[key],key
for sec in ['A','B']:assert len(old[sec])==len(w[sec])and all(e[:-1]==f[:-1] for e,f in zip(old[sec],w[sec]))
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
w['report']['local_profile']={str(k):n for k,n in sorted(after.items())}
a.out.mkdir(parents=True,exist_ok=False);raw=canon(w);data=gzip.compress(raw,compresslevel=9,mtime=0);data=data[:9]+b'\xff'+data[10:];(a.out/'FULL-WORD.json.gz').write_bytes(data)
r=dict(status='PASS_COLLECTIVE_HYPERPLANE_FRAME_CONTRACTION',source_content_sha256=hashlib.sha256(canon(old)).hexdigest(),word_content_sha256=hashlib.sha256(raw).hexdigest(),before=dict(before),after=dict(after),delta={k:after[k]-before[k]for k in set(before)|set(after)if after[k]!=before[k]},changes=changes,controls=controls,scalar_program_unchanged=True,boundaries_unchanged=True,scope='Exact finite subspace chains and unchanged scalar word. Fresh Clifford phases, full local physical columns and global owner realization are required separately.')
(a.out/'WAVE-REVIEW.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r))
