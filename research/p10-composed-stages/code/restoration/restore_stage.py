"""Portable h20 restoration stage. Freshly recomputes frozen selection, actual F2 word, integer commutation, both reflected ledgers and changed endpoint registry. Prepared with OpenAI Codex assistance; PR280/283 provenance in restore_transform.py. Apache-2.0."""
if not __debug__:raise SystemExit("assertions required")
import sys,json,hashlib,struct
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
from restore_screen import *
HERE=Path(__file__).resolve().parent
rt=load('generic_restore',HERE/'restore_transform.py');km=load('generic_replay',HERE/'kernel_transform.py');w.module=m.Module
before=km.replay(R,n,v);H=Counter(R[k+4]for k in range(0,len(R),6)if R[k]==0 and R[k+4]);H[h-2]+=h;cats=list(S['physical']['category_names']);maxcat=max(R[k+5]for k in range(0,len(R),6)if R[k]==1);cats+=['native_category_'+str(k)for k in range(len(cats),maxcat+1)]
selection=dict(n=n,v=v,input_raw_sha256=hashlib.sha256(R.tobytes()).hexdigest(),input_scalar_sha256=before['event_sha256'],selected=len(entries),eligible=len(entries),eligible_helpers=[e['helper']for e in entries],entries=entries)
physical=dict(S['physical']);physical['category_names']=cats;physical['scalar_projection_sha256']=before['event_sha256'];physical['weighted_scalar_events']=before['scalar_additions'];physical['paid_histogram']=dict(H);physical['paid_rank_mass']=sum(r*k for r,k in H.items());producer=dict(W=w,C=c,records=R,initial_state=I,context={'regs':list(range(n-2*v))},ZERO=S['ZERO'],FULL=S['FULL'],physical=physical,producer_physical=physical)
word,ini,fin,_,_,proof,_,_=rt.transform(producer,selection);newH=Counter(word[k+4]for k in range(0,len(word),6)if word[k]==0 and word[k+4]);newH[h-2]+=h;delta=Counter(newH);delta.subtract(H);selection['expected_local_delta']={str(r):x for r,x in delta.items()if x};
if args.selection:assert json.loads(args.selection.read_text())==json.loads(json.dumps(selection)),'frozen restoration selection differs from fresh actual-word screen'
(O/'SELECTION.json').write_text(json.dumps(selection,sort_keys=True,indent=2)+'\n')
out=O;out.mkdir(exist_ok=True);
for sourcefile in P.iterdir():
 if sourcefile.is_file() and sourcefile.name not in {'SELECTION.json','SCREEN.json'}:__import__('shutil').copyfile(sourcefile,out/sourcefile.name)
res=rt.run(producer,out,O/'SELECTION.json');assert res['records']==word and res['final_state']==fin
res['physical']['initial_independent_entrances']=dict(Counter(c.dimf[ini[r]]for r in range(2*v,n)if c.dimf[ini[r]]))
raw=word.tobytes();sha=hashlib.sha256(raw).hexdigest();S.update(record_sha256=sha,record_count=len(word)//6,initial=ini,final=fin,physical=res['physical']);(out/'249-states.json').write_text(json.dumps(S,sort_keys=True)+'\n');(out/'COHORT249-RECORDS.bin').write_bytes(raw);(out/'249-records.bin').write_bytes(raw);(out/'COHORT249-INITIAL.json').write_text(json.dumps(ini,sort_keys=True)+'\n');(out/'COHORT249-FINAL.json').write_text(json.dumps(fin,sort_keys=True)+'\n');(out/'frames.json').write_text(json.dumps(dict(h=h,frames=c.frames),sort_keys=True)+'\n')
nf=json.loads((P/'COHORT249-FRAMES.json').read_text())if(P/'COHORT249-FRAMES.json').exists()else {};nf.update({str(f):z for f,z in c.frames.items()if f not in original_frame_ids});(out/'COHORT249-FRAMES.json').write_text(json.dumps(nf,sort_keys=True)+'\n')
basefinal={int(k):v for k,v in json.loads((P/'COHORT249-FINAL.json').read_text()).items()};bank=Counter(c.dimf[fin[r]]-c.dimf[ini[r]]for r in range(2*v,n));rankmass=sum(r*k for r,k in bank.items());result=dict(status='PASS_GENERIC_H20_EARLY_RESTORATION_WORD_AND_BOTH_REFLECTED_LEDGERS',h=h,v=v,n=n,input_sha256=selection['input_raw_sha256'],output_sha256=sha,records=len(word)//6,scalar_adds=res['physical']['weighted_scalar_events'],paid_calls=sum(newH.values()),paid_rank_mass=sum(r*k for r,k in newH.items()),paid_histogram=dict(newH),bank_residual_census=dict(bank),bank_rank_mass=rankmass,replicas=60,m=100,bank_integrality=(rankmass*60)%100==0,banks_per_stage=rankmass*60//100,changed_endpoints=sum(fin[r]!=basefinal[r]for r in fin),proof=proof,scope='Word transform only; complete bank scalar realization and exact finite geometry/price still required')
(O/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,sort_keys=True,indent=2))

if (out/'SOURCE-BINDING.json').exists():
 bind=json.loads((out/'SOURCE-BINDING.json').read_text());bind.update(word_sha256=sha,record_count=len(word)//6,pre_restoration_word_sha256=selection['input_raw_sha256']);(out/'SOURCE-BINDING.json').write_text(json.dumps(bind,sort_keys=True)+'\n')
