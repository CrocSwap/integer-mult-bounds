"""Emit/gate bounded exact lattice nominees against frozen local80."""
import json,gzip,copy,hashlib,subprocess,struct
from pathlib import Path
from collections import defaultdict,Counter
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;P=R/'experiments/architecture/enlarged-even-donors/pivot954';nom=json.load(open(O/'SPARSE.json'))['rows'];results=[]
for row in nom:
 row['entrance']=json.load(open(P/'word.json'))['frames'][row['frame']]
 D=O/'single'/('f%d-p%d'%(row['frame'],row['pivot']));D.mkdir(parents=True,exist_ok=True)
 sel=json.load(open(P/'SELECTION.json'));w=json.load(gzip.open(P/'word.json.gz','rt'));base=json.load(open(P/'baseline.json'));frame={tuple(f):i for i,f in enumerate(w['frames'])}
 es=sel['entries']+[{'pivot':row['pivot'],'entrance':row['entrance'],'rank':1,'frame':frame[tuple(row['entrance'])],'donor_coefficients':row['coefficients']}];ps={e['pivot']for e in es};assert not ps&{d for e in es for d,c in e['donor_coefficients']};groups=defaultdict(list)
 for e in es:
  for d,c in e['donor_coefficients']:groups[d,frame[tuple(e['entrance'])]].extend([e['pivot']]*abs(c))
 z=copy.deepcopy(base);z['frames']=w['frames']
 for e in es:z['start'][e['pivot']]=frame[tuple(e['entrance'])]
 z['A']=[[f,d,sorted(v)]for(d,f),v in sorted(groups.items())]+z['A'];z['C']+=[[base['final'][0],d,sorted(v)]for(d,f),v in sorted(groups.items())];z['D']=[[f,d,[x for x in ss if x not in ps]]for f,d,ss in z['D']]
 raw=json.dumps(z,sort_keys=True,separators=(',',':')).encode();(D/'word.json').write_bytes(raw)
 with gzip.open(D/'word.json.gz','wb')as f:f.write(raw)
 sel.update(entries=es,pivots=81,entrance_rank=105,donor_count=len({d for e in es for d,c in e['donor_coefficients']}),output_sha256=hashlib.sha256(raw).hexdigest());(D/'SELECTION.json').write_text(json.dumps(sel,indent=2));(D/'baseline.json').write_bytes((P/'baseline.json').read_bytes())
 subprocess.run(['python3',str(R/'experiments/bit-search/pr434/source/research/split-centres-global/vendor/export_records.py'),str(D/'word.json'),str(D/'records')],check=True,stdout=subprocess.DEVNULL)
 s=(P/'signed_source.py').read_text().replace('coefficient in (-2,-1,1,2)','coefficient in tuple(range(-9,0))+tuple(range(1,10))').replace("selection['pivots']==80","selection['pivots']==81");(D/'signed_source.py').write_text(s)
 with open(D/'replay.log','w')as f:res=subprocess.run(['python3',str(D/'signed_source.py')],stdout=f,stderr=f)
 H=Counter()
 for op,a,b,c,f,z in struct.iter_unpack('<6i',(D/'records/249-records.bin').read_bytes()):
  if op==0 and f:H[f]+=1
  if op==2:H[z]+=1
 rec={'pivot':row['pivot'],'exit_code':res.returncode,'profile':dict(H),'rank_mass':sum(r*n for r,n in H.items()),'prelude_units':row['unit_additions'],'frame':row['frame'],'source_word_sha256':hashlib.sha256(raw).hexdigest()}
 if res.returncode==0:rec['signed_result']=json.load(open(D/'RESULT.json'))
 results.append(rec);print(row['pivot'],res.returncode,rec['rank_mass'],flush=True)
 (O/'PHYSICAL-SINGLES.json').write_text(json.dumps({'status':'ACTUAL_SIGNED81_SINGLE_EXTRA_GATE','rows':results},indent=2)+'\n')
