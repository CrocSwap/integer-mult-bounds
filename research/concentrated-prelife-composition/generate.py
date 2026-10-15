"""Deterministic exact composition using unchanged, source-pinned generic builders.

Credits: PR2696 Mason Hale; PR2679 Philippe Van Velzen; PR2673 Jeremy Kothe; PR2530 zxv;
PR2621 scheduling idea; PR2559 evacuation. Composition: Marius-Paul Dumitrean,
with substantial OpenAI Codex assistance. Apache-2.0. No source writes.
"""
if not __debug__:
 raise RuntimeError('Optimized Python disables required upstream assertions; run without -O.')
from pathlib import Path
import argparse,collections,copy,gzip,hashlib,json,os,sys,subprocess,time
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True

def read(p):
 raw=Path(p).read_bytes();return json.loads(gzip.decompress(raw)if str(p).endswith('.gz')else raw)
def write(p,w):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(w,separators=(',',':')).encode();p.write_bytes(gzip.compress(raw,mtime=0)if p.suffix=='.gz'else raw)
def sem(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def patch(WP,before,after,kind):
 # Frozen experimental metadata below is retained exactly; PR2679 is Philippe
 # Van Velzen's work. NOTICE corrects the historical credit without changing inputs.
 return {'kind':kind,'fields':{k:copy.deepcopy(v)for k,v in after.items()if k not in ['report','cleanup']and v!=before.get(k)},'report':after['report'],'removed_added':sorted(set(after['removed'])-set(before['removed'])),'declared_gate_edit':WP.kernel_gate_edit(before['B'],after['B']),'prelude_events':after.get('prelude_events',0),'credit':'PR2696 Mason Hale concentrated source partners; PR2679 Jeremy Kothe pre-life/refit; exact composition by Marius-Paul Dumitrean with substantial OpenAI Codex assistance.'}
def registry(w,basis):
 regs=sorted(set(range(224,704))-set(w['removed']));return regs,[len(basis(w['helper_final'].get(str(r),[1<<i for i in range(9)])))-len(basis(w['start_extra'].get(str(r),[])))for r in regs]
def generate(P,REF,out):
 assert __debug__;P=P.resolve();REF=REF.resolve();out=out.resolve();assert not out.exists();assert not out.is_relative_to(HERE.resolve());out.mkdir(parents=True);start=time.process_time()
 pins=read(HERE/'SOURCE-PINS.json');sources={}
 for label,root in [('2679',P),('2696',REF)]:
  for n,want in pins[label].items():
   raw=(root/n).read_bytes();assert hashlib.sha256(raw).hexdigest()==want,(label,n);sources[label+'/'+n]=want
 S=P/'new/borrow/prelife/search';sys.path[:0]=[str(S),str(P/'new/borrow')];import prelife2 as PL,repair2,alias_build as AB,word_patch as WP,audit_local as AU
 # Execute precisely the immutable supplier's seed construction prefix, ending
 # before alias8. No original source is rewritten or imported as a full replay.
 seedfile=P/'new/rebuild_borrow.py';src=seedfile.read_text();boundary='    af3=D/';assert src.count(boundary)==1;src=src[:src.index(boundary)]+"    _SEEDS[wt]=chain[-1]\n";seeds={};os.environ['BORROW_RECEIPTS']=str(out/'seed-receipts');ns={'__file__':str(seedfile),'__name__':'composition_seed_replay','_SEEDS':seeds};exec(compile(src,str(seedfile),'exec'),ns)
 records={};newpv={};maps={};allstage={};hosting={482:273,483:275,494:289,495:291,507:305,519:321}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  pp0=read(P/f'new/borrow/inputs/prelife_43{tag}.json');images={r[1]:r[4]for r in pp0['fields']['warps'][-6:]};frame=read(P/f'new/borrow/inputs/refit563_43{tag}.json')['frames'][0][2];recs={}
  for label,ip in [('positive2679',REF/f'inputs/pr2588-{tag}.json.gz'),('combined',REF/f'inputs/candidate/eight-alias-{tag}.json.gz')]:
   w=read(ip);before=copy.deepcopy(w);PL.TRACE,_=repair2.run(copy.deepcopy(w),None)
   for pair in pp0['pairs']:w=PL.build(w,pair['L'],pair['h'],images[pair['h']]);PL.TRACE,_=repair2.run(copy.deepcopy(w),None)
   prepatch=patch(WP,before,w,'COMPOSED_PRELIFE_HOSTING');prepatch['pairs']=pp0['pairs'];assert sem(WP.apply_prelife(before,prepatch))==sem(w)
   idxs=[i for i,g in enumerate(w['B'])if g[:5]==['add',515,563,1,1]];assert len(idxs)==1;idx=idxs[0];assert len(w['B'][idx][-1])==6 and len(frame)==5;w['B'][idx][-1]=frame;repair2.run(copy.deepcopy(w),None);lp,wi=AB.profile(w);w['report']=dict(w['report'],local_profile=lp,width_inventory=wi);refit={'kind':'COMPOSED_REFIT563','frames':[['B',idx,frame]],'local_profile':lp};beforealias=copy.deepcopy(w);w,ar=AB.alias(w,653,563);lp,wi=AB.profile(w);w['report']=dict(w['report'],local_profile=lp,width_inventory=wi);aliaspatch=patch(WP,beforealias,w,'COMPOSED_ALIAS653');aliaspatch['aliases']=[ar];assert sem(WP.apply_lowfour(beforealias,aliaspatch))==sem(w)
   dest=out/label/f'{tag}.json.gz';write(dest,w);AU.run(dest,out/label/f'{tag}-AUDIT.json');recs[label]={'semantic_sha256':sem(w),'profile':lp,'width_inventory':wi,'refit_index':idx}
   if label=='positive2679':assert w==read(P/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')
   else:
    alias8=patch(WP,seeds[tag],read(ip),'CONCENTRATED_SOURCE_PARTNER_ALIAS8');assert sem(WP.apply_lowfour(seeds[tag],alias8))==sem(read(ip));stages={'alias8':alias8,'prelife':prepatch,'refit563':refit,'alias1':aliaspatch}
    for name,obj in stages.items():f=out/f'patches/{name}_43{tag}.json';f.parent.mkdir(exist_ok=True);f.write_text(json.dumps(obj)+'\n')
    write(out/f'words/{tag}.json.gz',w);allstage[tag]=stages;newregs,widths=registry(w,AU.basis);oldregs,oldwidths=registry(read(ip),AU.basis);oldpv=read(REF/'inputs/pr2588-PROVIDERS.json');pools=collections.defaultdict(list)
    for i,v in enumerate(oldwidths):pools[v].append(i)
    first={i:pools[v].pop(0)for i,v in enumerate(oldpv[pid]['widths'])};assert sorted(first.values())==list(range(422));second={i:newregs.index(hosting.get(r,r))for i,r in enumerate(oldregs)if r not in set(hosting.values())|{653}and hosting.get(r,r)in newregs};assert sorted(second.values())==list(range(415));assert all(oldwidths[i]==widths[j]for i,j in second.items());composed={i:second[j]for i,j in first.items()if j in second};assert all(oldpv[pid]['widths'][i]==widths[j]for i,j in composed.items());maps[pid]={'first':first,'second':second,'composed':composed};newpv[pid]={'widths':widths,'actual_paid_profile':lp}
  records[tag]=recs
 assert maps['gauge44']==maps['extra'];assert newpv['gauge44']==newpv['extra'];m=maps['gauge44']['composed'];fill=read(REF/'inputs/pr2673/FILL.json.gz');rows=[]
 for t,h,r,ch,port,off in fill['rows']:
  if h in m:rows.append([t,m[h],r,ch,port,off])
 bins=collections.defaultdict(list)
 for i,row in enumerate(rows):bins[tuple(row[2:5])].append(i)
 for ids in bins.values():
  off=0
  for i in sorted(ids,key=lambda i:rows[i][5]):rows[i][5]=off;off+=newpv['gauge44']['widths'][rows[i][1]]
 assert len(rows)==276390;write(out/'FILL.json.gz',dict(fill,rows=rows));order=read(REF/'inputs/pr2673/ORDER.json');(out/'ORDER.json').write_text(json.dumps(order));(out/'PROVIDERS.json').write_text(json.dumps(newpv));(out/'MAPS.json').write_text(json.dumps(maps,indent=2)+'\n')
 ctx=out/'literal-context';(ctx/'new/borrow-fill').mkdir(parents=True)
 for n in ['inputs','vendor']:(ctx/n).symlink_to(P/n,target_is_directory=True)
 (ctx/'reconstruct.py').write_bytes((P/'reconstruct.py').read_bytes())
 for dest,source in [('new/BORROW-PROVIDERS.json',out/'PROVIDERS.json'),('new/borrow-fill/ORDER.json',out/'ORDER.json'),('new/borrow-fill/FILL.json.gz',out/'FILL.json.gz'),('new/borrow-fill/DISPATCH.json',P/'new/borrow-fill/DISPATCH.json')]: (ctx/dest).write_bytes(source.read_bytes())
 r=subprocess.run([sys.executable,'-B',str(ctx/'reconstruct.py'),'--out',str(out/'literal')],capture_output=True,text=True);(out/'LITERAL.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;(out/'PROFILE.json').write_bytes((out/'literal/PROFILE.json').read_bytes())
 manifest=read(HERE/'expected/MANIFEST.json');assert hashlib.sha256((HERE/'expected/MANIFEST.json').read_bytes()).hexdigest()=='f9b8b8cbed9e55b32d821c50ab76fef0afb1466f29d11204254fb50d2533e680';matched=[]
 for name,want in manifest.items():
  assert hashlib.sha256((HERE/'expected'/name).read_bytes()).hexdigest()==want,name
  if name=='PR2696-SOURCES.json':continue
  assert read(out/name)==read(HERE/'expected'/name),('decoded output mismatch',name)
  matched.append(name)
 result={'status':'PASS_PORTABLE_EXACT_COMPOSITION_GENERATOR','positive_controls':'Both complete PR2679 words exactly regenerated and audited before composition.','outputs_equal':matched,'sources':sources,'records':records,'cpu_seconds':time.process_time()-start,'scope':'Exact local operator/frame/cleanup and literal hosting checks; full native/global/outer admission is separate.'};(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source2679',type=Path,default=HERE.parent/'gmx-t74-borrow43-handoff');ap.add_argument('--source2696',type=Path,default=HERE.parent/'t74-concentrated-source-partners');ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();generate(a.source2679,a.source2696,a.work)
