"""Fresh finite certificate of a conditional construction; standard library only.
Apache-2.0. No network, search, WSL, GPU, compiler or persistent workers.
"""
import argparse,gzip,hashlib,importlib.util,json,shutil,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent

def need(x,m):
 if not x:raise RuntimeError(m)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8',newline='\n')
def inventory():
 manifest=read(P/'MANIFEST.json');actual={x.relative_to(P).as_posix() for x in P.rglob('*') if x.is_file() and x.name!='MANIFEST.json'}
 need(actual==set(manifest),'exact package file inventory')
 for n,h in manifest.items():need(sha(P/n)==h,'source sha256 '+n)
 return manifest
def ancestor_pins():
 pins=read(P/'vendor/pr1117/data/UPSTREAM-PINS.json')
 targets={
 'local/data/PARENT-ROUTING.json.gz':'base/split-centres/CANONICAL-WORD.json.gz',
 'inputs/DATA-PHASES.json':'complex-nine-native/DATA-PHASES.json',
 'inputs/ROUND20-PARENT-TEMPLATE.json.gz':'vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz',
 'inputs/PRIOR-ALLOWANCE.json':'vendor531/evidence/audit/PREFIX-AND-INVOICE.json',
 'vendor/engines/moment.py':'/moment.py',
 'vendor/engines/base_two_moment.py':'/base_two_moment.py',
 'vendor/engines/outer.py':'/outer.py'}
 for name,suffix in targets.items():
  hs={h for n,h in pins.items() if n.endswith(suffix)}
  need(len(hs)==1 and sha(P/name) in hs,'upstream source pin '+name)
 need(sha(P/'data/OWNERS.json.gz')=='d7df90d10fefcd94d2893c559ea507bc057c34ac59296281492220036c8ae48e','final literal owners pin')
 need(sha(P/'data/DISPATCH.json')=='5b1924fc0da6de00e681e7773ad59f70e3f69f0772100cce7b65768b0fd0d3eb','final dispatch pin')

def main():
 need(__debug__,'normal Python required; optimized Python disables vendor checks')
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);z=a.parse_args();out=z.out.resolve()
 need(out!=P and P not in out.parents,'output must be outside the source package')
 need(not out.exists(),'fresh output directory required')
 start=time.monotonic();manifest=inventory();ancestor_pins();out.mkdir(parents=True)
 # Rebuild every changed literal row from the pinned old map. No optimizer runs.
 rows=read(P/'vendor/pr1117/data/OWNERS.json.gz');edits=read(P/'data/EDITS-FROM-PR1117.json');seen=set()
 need(len(edits)==4594,'complete literal difference count')
 for e in edits:
  i=e['index'];need(type(i) is int and 0<=i<len(rows) and i not in seen,'unique literal edit index');seen.add(i)
  need(rows[i]==e['before'],'literal edit before');rows[i]=e['after']
 need(rows==read(P/'data/OWNERS.json.gz'),'rebuilt complete final map');need(len(rows)==69120,'complete role count')
 print('PASS_SOURCE_PINS_AND_LITERAL_RECONSTRUCTION',flush=True)
 # Five freshly reconstructed, emitted and independently checked joint programs.
 native={};local=[]
 for k in range(1,6):
  dest=out/('provider-'+str(k));flags=0x4000 if sys.platform=='win32' else 0
  r=subprocess.run([sys.executable,'-I','-B',str(P/'local/check_local.py'),'--selector',str(k),'--out',str(dest)],capture_output=True,text=True,timeout=120,creationflags=flags)
  (out/('provider-'+str(k)+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8')
  need(r.returncode==0,'fresh local prefix '+str(k)+' failed: '+r.stderr[-1200:]);local.append(read(dest/'RESULT.json'));native[k]=dest/'native'
  print('PASS_FRESH_PREFIX',k,flush=True)
 old=out/'old-native';old.mkdir();shutil.copyfile(P/'local/data/OLD-CANONICAL-WORD.json.gz',old/'CANONICAL-WORD.json.gz')
 mixed=module('mixed',P/'audit_mixed.py')
 audit,context=mixed.run(P/'vendor/pr1117',P/'data/OWNERS.json.gz',P/'data/DISPATCH.json',old,native[1],P/'local/data/PARENT-ROUTING.json.gz',P/'inputs/DATA-PHASES.json',P/'inputs/ROUND20-PARENT-TEMPLATE.json.gz',variants=native)
 audit['negative_controls']=mixed.negative_controls(context);need(len(audit['negative_controls'])==11,'mixed mutation controls')
 for n in ('sigmas','remainders'):
  x=audit.pop(n);(out/(n.upper()+'.json.gz')).write_bytes(gzip.compress(json.dumps(x,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 expected=read(P/'expected/OWNER-AUDIT.json')
 for n in ('roles','calls','helper_per_call','profile','idle_profile','idle_remainders','rank_mass','deficit','cross_replica','actual_73column_sigmas','sigma_stream_sha256','mixed_calls','default_calls','variant_counts'):
  # JSON maps use string keys; the fresh checker may use integer keys.
  need(json.loads(json.dumps(audit[n]))==expected[n],'fresh complete owner result '+n)
 write(out/'OWNER-AUDIT.json',audit);print('PASS_COMPLETE_OWNER_CHARTS_AND_11_CONTROLS',flush=True)
 spec=read(P/'vendor/pr1117/data/SPEC.json');dispatch=read(P/'data/DISPATCH.json')
 inv=module('invoice',P/'finite_invoice.py').calculate(spec,audit,dispatch,native,read(P/'inputs/PRIOR-ALLOWANCE.json'))
 need(len(inv['strict_checks'])==9 and all(inv['strict_checks'].values()) and len(inv['negative_controls'])==4,'all nine finite guards and four controls')
 need(inv['conservative_pervertex_used']==6466906000439144,'complete fresh bill');write(out/'FINITE-INVOICE.json',inv)
 print('PASS_FRESH_FINITE_INVOICE_9_GUARDS',flush=True)
 pricing=module('pricing',P/'pricing.py');M,B,A=[module(n,P/'vendor/engines'/(n+'.py')) for n in ('moment','base_two_moment','outer')]
 bitrecord=read(P/'inputs/PR589-EXPECTED.json');bit=Q(bitrecord['nine']['bit_lower']);bitH={int(r):n for r,n in bitrecord['nine']['profile'].items()};live=bitrecord['nine']['bit']['live']
 need(live==28416 and 64*live-sum(r*n for r,n in bitH.items())==10272,'inherited bit exact mass')
 bitchecks=[]
 for b,accept in [(bit,True),(bit+Q(1,10**24),False)]:
  i=M.moment(bitH,64,live,b,True);j=B.moment(64,live,list(bitH.items()),b);c=B.moment(64,live,[(1,32*64**2*sum(bitH.values()))],b);j=(j[0]+c[0]/10**16,j[1]+c[1]/10**16)
  need(i[1]<1 and j[1]<1 if accept else i[0]>1 and j[0]>1,'unchanged bit two-engine bracket');bitchecks.append(dict(b=b,accepted=accept,mercator=i,base_two=j))
 H={int(r):n for r,n in audit['profile'].items()}
 # Probability weights are normalized from the complete positive histogram.
 weights={r:Q(r*n,audit['rank_mass']) for r,n in H.items()};need(all(n>0 for n in H.values()) and sum(weights.values())==1,'complete positive normalized weights')
 result=pricing.price(H,bit,M,B,A);conservative=pricing.price(H,bit,M,B,A,True)
 base=pricing.price({int(r):n for r,n in spec['expected']['global_profile'].items()},bit,M,B,A)
 need(base['kappa']==Q(spec['expected']['kappa']),'baseline assembly compatibility')
 need(result['kappa']==Q('0.001673260706543984') and conservative['kappa']==Q('0.001673260703699378'),'exact claimed endpoints')
 need(result['kappa']>base['kappa'],'strict improvement over frozen baseline')
 result.update(status='PASS_ADAPTIVE_KERNEL_DEMOTION',conservative=conservative,baseline=base['kappa'],gain=result['kappa']-base['kappa'],profile=H,normalized_weights=weights,bit_moment_checks=bitchecks,local_checks=local,finite_invoice='FINITE-INVOICE.json',owner_audit='OWNER-AUDIT.json',source_manifest_sha256=sha(P/'MANIFEST.json'),seconds=time.monotonic()-start,scope='Conditional artifact certificate. Changed local programs, new owner map, fresh invoice and exact assembly checked. Inherited unchanged supplier, compiler, all-size, precision/recovery and analytic interfaces remain assumptions. No new Lean certification or unconditional multiplication claim.')
 write(out/'RESULT.json',pricing.encode(result));print('PASS_ADAPTIVE_KERNEL_DEMOTION kappa='+result['kappa_decimal'],flush=True)

if __name__=='__main__':main()
