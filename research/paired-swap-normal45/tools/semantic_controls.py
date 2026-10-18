"""Semantic corruption controls for the unchanged combined candidate, with recalculated bookkeeping."""
from pathlib import Path
import sys,json,gzip,hashlib,types,copy,os,io,contextlib,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
import argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--candidates',type=Path,default=ROOT/'combined-2942-2957-01');parser.add_argument('--source',type=Path,default=ROOT/'source2942');parser.add_argument('--out',type=Path,default=ROOT/'combined-2957-controls-01');args=parser.parse_args();D=args.candidates;SRC=args.source
PINS={'base':'9258f5a81112e56232b79b92f05334ced69c2c00d68f430e08363a9836de6b3e','extra':'89f5502c75991a55d7b3c23826694537bbf5d6789f72cea1ad51c45c113219ed'}
def module(name,path,pin):
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==pin;m=types.ModuleType(name);exec(compile(b,str(path),'exec'),m.__dict__);return m
pm=module('pm',SRC/'vendor/preload_move.py','c8fda4674644fcd5cbf39b6645ce148a21daa90a998b678cbe51f970b78b0044');aud=module('aud',SRC/'vendor/audit_local.py','a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90')
out=args.out;fd=os.open(str(out)+'.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY)
try:
 assert not out.exists();out.mkdir();reports=[];start=time.time()
 for v in ['base','extra']:
  raw=(D/('WORD-'+v+'.json.gz')).read_bytes();input_sha=hashlib.sha256(raw).hexdigest();frozen=(ROOT.parent/'data'/('WORD-'+v+'.json.gz')).read_bytes();assert hashlib.sha256(frozen).hexdigest()==PINS[v];w=json.loads(gzip.decompress(raw));assert w==json.loads(gzip.decompress(frozen));ledger=json.loads((D/('WORD-'+v+'-EDITS.json')).read_text());positions={}
  for sec in ['A','B','restore']:
   offset=0
   for e in sorted([e for e in ledger['mapped_edits'] if e['section']==sec],key=lambda a:(a['normal45_start'],a['normal45_stop'])):
    a=e['normal45_start'];b=e['normal45_stop'];p=a+offset;assert w[sec][p:p+len(e['new'])]==e['new']
    if e['new'] and e['rewrite_id'] not in positions:positions[e['rewrite_id']]=(sec,p)
    offset+=len(e['new'])-(b-a)
  controls=[]
  def reject(label,bad,rebook=True):
   if rebook:
    try:
     profile,inventory=pm.frame_report(bad);bad['report']['local_profile']=profile;bad['report']['width_inventory']=inventory;t=copy.deepcopy(bad);t['A']=t['A'][t['prelude_events']:];bad['cleanup']=pm.derive_cleanup(t,set(map(int,bad['helper_final'])))
    except ValueError as e:controls.append({'label':label,'rejected':True,'stage':'literal frame reconstruction','reason':str(e)});return
   p=out/(v+'-'+label+'.json.gz');p.write_bytes(gzip.compress(json.dumps(bad,separators=(',',':')).encode(),mtime=0))
   try:
    with contextlib.redirect_stdout(io.StringIO()):aud.run(p,out/(v+'-'+label+'-unexpected.json'))
   except (RuntimeError,ValueError,AssertionError) as e:controls.append({'label':label,'rejected':True,'stage':'exact auditor','reason':str(e)});return
   raise AssertionError('Semantic control accepted '+label)
  for cls,(sec,p) in positions.items():
   bad=copy.deepcopy(w);assert bad[sec][p][0]=='add';bad[sec][p][3]=-bad[sec][p][3];reject(cls+'-wrong-inserted-sign',bad)
  bad=copy.deepcopy(w);bad['restore'].append(['add',408,105,1,1,[256,128,64,36,20,8,2,1]]);reject('double-count-overlapping-P-retime',bad)
  bad=copy.deepcopy(w)
  for rec,orig in zip(bad['warps'],ledger['warp_position_mapping']):rec[0]=orig['old_position']
  reject('unshifted-B-warp-positions',bad)
  bad=copy.deepcopy(w);t=copy.deepcopy(bad);t['A']=t['A'][t['prelude_events']:];oldset=set(map(int,bad['helper_final']))-{249,267,251,265};bad['cleanup']=pm.derive_cleanup(t,oldset);reject('stale-82-buffer-cleanup',bad,False)
  bad=copy.deepcopy(w);bad['report']['local_profile']={'1':2434,'2':632,'3':286,'4':104,'5':26,'8':8};reject('stale-normal45-paid-profile',bad,False)
  assert len(controls)==18;reports.append({'variant':v,'candidate_sha256':PINS[v],'controls':controls});print(v,'REJECTED',len(controls),flush=True)
  assert hashlib.sha256((D/('WORD-'+v+'.json.gz')).read_bytes()).hexdigest()==input_sha
 result={'status':'PASS_36_COMBINED_2957_SEMANTIC_CONTROLS','scope':'All 14 rewrite sign corruptions reprice frames and regenerate actual 86-buffer cleanup before semantic audit; no false reliance on stale bookkeeping. No native phase/global admission claim.','providers':reports,'elapsed_seconds':time.time()-start};(out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(result['status'],result['elapsed_seconds'])
finally:os.close(fd);Path(str(out)+'.lock').unlink()
