from pathlib import Path
import json,struct
from collections import Counter
import tape_core as TC
ROOT=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;P=ROOT/'experiments/architecture/collective-common-frame-bit/composed';fs=json.load(open(P/'records/frames.json'))['frames'];st=json.load(open(P/'records/249-states.json'));width=[8-fs[str(st['initial'][str(240+h)])]['dim']for h in range(740)];path={}
for op,a,b,c,f,z in struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()):
 if op==0:path.setdefault(a,[]).append(c)
out=[]
for K in(4,5):
 L=2*K+1;sch=[dict(kind='local',stage=0,pair=0)];idx=0
 for j in range(K):
  s=2*j+1;sch.append(dict(kind='local',stage=s,pair=j))
  if j<K-1:sch.extend([dict(kind='idle',idx=idx,pair=j+1,rank=14*(j+1)),dict(kind='bridge',dst=j,src=j+1)]);idx+=1
  s+=1;sch.append(dict(kind='local',stage=s,pair=j))
  if j<K-1:sch.extend([dict(kind='idle',idx=idx,pair=j+1,rank=7),dict(kind='bridge',dst=j,src=j+1)]);idx+=1
  else:
   for p in range(K):sch.append(dict(kind='idle',idx=idx,pair=p,rank=7*(2*K-(2*p+2))));idx+=1
 win={i:w for i,w in TC.windows(sch).items()if w[1]and w[2]};counts,_=TC.load(O/'SELECTION.json',str(K));pieces,rem=TC.expand(win,counts,{s:list(enumerate(width))for s in range(L)},240)
 witnesses=[]
 for(s,h),(i,segs)in pieces.items():
  if len(segs)==2:
   frames=[int(st['initial'][str(240+h)])]+path[240+h];dims=[fs[str(f)]['dim']for f in frames]
   witnesses.append({'stage':s,'helper':240+h,'child':i,'child_pair':win[i][0],'child_rank':win[i][1],'parts':segs,'width':width[h],'frames':frames,'dimensions':dims})
 out.append({'K':K,'all_split_count':len(witnesses),'split_width_sum':sum(w['width']for w in witnesses),'split_min_piece_sum':sum(min(p[2]for p in w['parts'])for w in witnesses),'split_min_piece_histogram':dict(Counter(min(p[2]for p in w['parts'])for w in witnesses)),'split_width_histogram':dict(Counter(w['width']for w in witnesses)),'first_split_examples':witnesses[:10],'helper240_splits':[w for w in witnesses if w['helper']==240]})
(O/'BOUND-SPLITS.json').write_text(json.dumps({'status':'EXACT_ABSTRACT_TAPE_SPLIT_TO_ACTUAL_HELPER_FRAME_BINDING','cases':out,'scope':'Binds virtualsplitpieces toactualhelperMOVEframes; routeisometry fromlocalframes toaddresspieces notyet supplied.'},indent=2)+'\n');print(json.dumps(out,indent=2))
