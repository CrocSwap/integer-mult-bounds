"""Fresh finite certificate of a conditional construction. Apache-2.0.
Standard library only; no network, search, WSL, GPU or persistent workers.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,shutil,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent
def need(x,m):
 if not x:raise RuntimeError(m)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8',newline='\n')
def inventory():
 pins=read(P/'MANIFEST.json');actual={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file() and f.name!='MANIFEST.json'}
 need(actual==set(pins),'exact source inventory')
 for n,h in pins.items():need(sha(P/n)==h,'source sha256 '+n)
def ancestors():
 pins=read(P/'vendor/pr1148/SOURCE-PINS.json')
 for name,suffix in {
 'local/data/PARENT-ROUTING.json.gz':'base/split-centres/CANONICAL-WORD.json.gz',
 'inputs/DATA-PHASES.json':'complex-nine-native/DATA-PHASES.json',
 'inputs/ROUND20-PARENT-TEMPLATE.json.gz':'vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz',
 'inputs/PRIOR-ALLOWANCE.json':'vendor531/evidence/audit/PREFIX-AND-INVOICE.json',
 'vendor/engines/moment.py':'/moment.py','vendor/engines/base_two_moment.py':'/base_two_moment.py','vendor/engines/outer.py':'/outer.py'}.items():
  hs={h for n,h in pins.items() if n.endswith(suffix)};need(len(hs)==1 and sha(P/name) in hs,'upstream source pin '+name)
 claim=read(P/'vendor/pr1148/CLAIM.json');need(Q(claim['kappa'])==Q('0.001675121647789207'),'frozen PR1148 comparison')

def main():
 need(__debug__,'normal Python required; -O disables vendor checks')
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);z=a.parse_args();out=z.out.resolve()
 need(out!=P and P not in out.parents,'output must be outside the package');need(not out.exists(),'fresh output directory required')
 start=time.monotonic();inventory();ancestors();out.mkdir(parents=True)
 rows=read(P/'vendor/pr1148/OWNERS.json.gz');edits=read(P/'data/EDITS-FROM-PR1148.json');seen=set();need(len(edits)==1409,'complete literal difference')
 for e in edits:
  i=e['index'];need(type(i)is int and 0<=i<len(rows) and i not in seen,'unique literal edit');seen.add(i);need(rows[i]==e['before'],'literal before');rows[i]=e['after']
 need(rows==read(P/'data/OWNERS.json.gz') and len(rows)==69120,'reconstructed complete final owner table')
 print('PASS_SOURCE_PINS_AND_LITERAL_RECONSTRUCTION',flush=True)
 native={};local=[]
 for k in range(1,4):
  dest=out/('provider-'+str(k));flags=0x4000 if sys.platform=='win32' else 0
  r=subprocess.run([sys.executable,'-I','-B',str(P/'local/check_local.py'),'--selector',str(k),'--out',str(dest)],capture_output=True,text=True,timeout=120,creationflags=flags)
  (out/('provider-'+str(k)+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8');need(r.returncode==0,'fresh prefix '+str(k)+' failed '+r.stderr[-1400:]);native[k]=dest/'native';local.append(read(dest/'RESULT.json'));print('PASS_FRESH_PREFIX',k,flush=True)
 old=out/'old-native';old.mkdir();shutil.copyfile(P/'local/data/OLD-CANONICAL-WORD.json.gz',old/'CANONICAL-WORD.json.gz')
 plan=read(P/'data/PLAN.json');spec=read(P/'vendor/pr1148/SPEC.json');dispatch=read(P/'data/DISPATCH.json');canon=read(P/'local/data/PARENT-ROUTING.json.gz');ph=read(P/'inputs/DATA-PHASES.json');parent=read(P/'inputs/ROUND20-PARENT-TEMPLATE.json.gz')
 auditor=module('candidate',P/'audit_candidate.py')
 audit,ctx=auditor.audit(plan,spec,rows,canon,ph,parent,variants=native,dispatch=dispatch,inherited_native=old)
 controls=auditor.mutations(ctx)
 for name,kind in [('wrong_dispatch_helpers','helpers'),('wrong_dispatch_variant','variant')]:
  d=copy.deepcopy(dispatch)
  if kind=='helpers':d[0]['helpers'][0]=-1
  else:d[0]['variant']=1 if d[0]['variant']!=1 else 2
  try:auditor.audit(plan,spec,rows,canon,ph,parent,variants=native,dispatch=d,inherited_native=old)
  except RuntimeError as e:controls.append(dict(name=name,rejected=str(e)))
  else:raise RuntimeError('accepted '+name)
 need(len(controls)==13,'all owner and dispatch controls');audit['negative_controls']=controls
 for n in ('sigmas','remainders'):(out/(n.upper()+'.json.gz')).write_bytes(gzip.compress(json.dumps(audit.pop(n),sort_keys=True,separators=(',',':')).encode(),mtime=0))
 expected=read(P/'expected/OWNER-AUDIT.json')
 for n in ('roles','calls','helper_per_call','profile','idle_profile','idle_remainders','rank_mass','deficit','cross_replica','actual_73column_sigmas','sigma_stream_sha256','mixed_calls','default_calls','variant_counts'):
  need(json.loads(json.dumps(audit[n]))==expected[n],'fresh owner result '+n)
 need(sum(x['variant']for x in dispatch)==89,'89 actual extra group demotions')
 write(out/'OWNER-AUDIT.json',audit);print('PASS_OWNER_CHARTS_AND_13_CONTROLS',flush=True)
 invoice=module('invoice',P/'finite_invoice.py').calculate(spec,audit,dispatch,native,read(P/'inputs/PRIOR-ALLOWANCE.json'))
 need(len(invoice['strict_checks'])==9 and all(invoice['strict_checks'].values()) and len(invoice['negative_controls'])==4,'nine finite guards and four controls')
 need(invoice['conservative_pervertex_used']==6467145011279720 and invoice['local_adapters']==387120,'actual complete charged bill');write(out/'FINITE-INVOICE.json',invoice);print('PASS_FRESH_FINITE_INVOICE',flush=True)
 pricing=module('pricing',P/'pricing.py');M,B,A=[module(n,P/'vendor/engines'/(n+'.py'))for n in ('moment','base_two_moment','outer')]
 bitrecord=read(P/'inputs/PR589-EXPECTED.json');bit=Q(bitrecord['nine']['bit_lower']);bitH={int(r):n for r,n in bitrecord['nine']['profile'].items()};live=bitrecord['nine']['bit']['live'];need(live==28416 and 64*live-sum(r*n for r,n in bitH.items())==10272,'inherited bit complete mass')
 bitchecks=[]
 for b,accept in [(bit,True),(bit+Q(1,10**24),False)]:
  i=M.moment(bitH,64,live,b,True);j=B.moment(64,live,list(bitH.items()),b);c=B.moment(64,live,[(1,32*64**2*sum(bitH.values()))],b);j=(j[0]+c[0]/10**16,j[1]+c[1]/10**16)
  need(i[1]<1 and j[1]<1 if accept else i[0]>1 and j[0]>1,'two bit moment brackets');bitchecks.append(dict(point=b,accepted=accept,mercator=i,base_two=j))
 H={int(r):n for r,n in audit['profile'].items()};result=pricing.price(H,bit,M,B,A);conservative=pricing.price(H,bit,M,B,A,True)
 base=pricing.price({int(r):n for r,n in read(P/'vendor/pr1148/CLAIM.json')['global_profile'].items()},bit,M,B,A)
 need(base['kappa']==Q('0.001675121647789207'),'baseline outer compatibility')
 need(result['kappa']==Q('0.001675224519162937') and conservative['kappa']==Q('0.001675224516317980'),'exact claimed endpoints');need(result['kappa']>base['kappa'],'strict improvement')
 result.update(status='PASS_CROSSCALL_KERNEL_DEMOTION',conservative=conservative,baseline=base['kappa'],gain=result['kappa']-base['kappa'],profile=H,extra_groups=89,bit_moment_checks=bitchecks,local_checks=local,seconds=time.monotonic()-start,source_manifest_sha256=sha(P/'MANIFEST.json'),owner_audit='OWNER-AUDIT.json',finite_invoice='FINITE-INVOICE.json',scope='Finite conditional certificate: fresh changed local programs/phases, full new owner geometry and dispatch, complete profile, invoice and exact outer assembly. Unchanged baseline local and bit circuits, compiler/all-size, hosting/labels, precision/recovery and analytic interfaces remain inherited. No new Lean certificate or unconditional theorem.')
 write(out/'RESULT.json',pricing.encode(result));print('PASS_CROSSCALL_KERNEL_DEMOTION kappa='+result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
