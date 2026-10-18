"""Complete differential validation of a credited workload-specific port.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,ast,copy,gzip,hashlib,importlib.util,json,platform,statistics,subprocess,sys,tarfile,tempfile,time
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('emitted_run',HERE/'run.py');run=importlib.util.module_from_spec(spec);spec.loader.exec_module(run)
fast=run.fast;need=run.require;sha=run.sha
ARCHIVE='research/community-frontier1042-audit/selected-replay.tar.gz'
REQUIRED={ARCHIVE,run.CHECKER,'research/community-frontier1042-audit/RESULT.json','research/community-frontier1094-audit/RESULT.json','research/community-frontier1094-audit/ASSEMBLY.json'}

def pairs(xs):
 d={}
 for k,v in xs:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def loads(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def canonical(x):return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'))
def fsha(path):
 raw=path.read_bytes();return sha(raw if path.suffix=='.gz' else raw.replace(b'\r\n',b'\n'))
def check_pins(pins):
 need(set(pins)==REQUIRED,'required source set')
 for p,d in pins.items():need(fsha(ROOT/p)==d,'source hash: '+p)
 receipt=loads((ROOT/'research/community-frontier1094-audit/RESULT.json').read_bytes())
 need(receipt['baseline_receipt_sha256']==sha((ROOT/'research/community-frontier1042-audit/RESULT.json').read_bytes().replace(b'\r\n',b'\n')),'reviewed ancestor receipt')
 need(receipt['kappa']=='836330098538459/500000000000000000','selected-at-base kappa')

def materialize(directory):
 metadata={}
 with tarfile.open(ROOT/ARCHIVE) as t:
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz'):
   members=[m for m in t.getmembers() if m.name=='slots/local/'+name]
   need(len(members)==1 and members[0].isfile(),'unique selected member')
   raw=t.extractfile(members[0]).read();(directory/name).write_bytes(raw)
   metadata[name]={'container_sha256':sha(raw),'payload_sha256':sha(gzip.decompress(raw))}
 need(metadata['CANONICAL-WORD.json.gz']['payload_sha256']=='4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c','selected R480 payload')
 return metadata

def assertion_list(text):return [ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Assert)]
def identity(x):need(type(x.get('seed')) is int and x['seed']==90,'exact seed identity')

def tracing(directory,engine):
 text=run.source();text=fast.transform(text) if engine=='integer' else text
 marker='            prefix=max(prefix,norm[target])'
 need(text.count(marker)==1,'trace hook source boundary')
 text=text.replace(marker,marker+'\n            observe(rows[target],norm[target],prefix)')
 tree=ast.parse(text);nodes=[]
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='profiles' for t in node.targets):break
  nodes.append(node)
 records=[]
 def observe(row,norm,prefix):
  if isinstance(row,fast.Row):row={k:Q(v,1<<row.exponent) for k,v in row.values.items()}
  records.append([[[k,str(v)] for k,v in sorted(row.items())],str(norm),str(prefix)])
 argv=sys.argv;sys.argv=[str(ROOT/run.CHECKER),str(directory)];env={'Row':fast.Row,'observe':observe}
 try:exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/run.CHECKER),'exec',optimize=0),env)
 finally:sys.argv=argv
 outputs={};traces={}
 for direction in ('forward','backward'):
  records.clear();env['local'](env['ir']['local_programs'][direction],direction=='backward')
  outputs[direction]={'scalar_prefixes':len(records),'all_changed_rows_norms_and_peaks_sha256':sha(canonical(records).encode())}
  traces[direction]=records.copy()
 return outputs,traces

def arithmetic_controls():
 count=0
 for a in [-9,-2,-1,0,1,2,9]:
  for d in range(7):
   for left in [{},{0:3,2:-2},{1:0}]:
    for right in [{},{0:-1,1:7},{2:0}]:
     q=Q(a,1<<d);x=fast.Row(left);y=fast.Row(right);expected={k:Q(v) for k,v in left.items()}
     for k,v in right.items():
      z=expected.get(k,Q(0))+q*v
      if z:expected[k]=z
      else:expected.pop(k,None)
     x.add_scaled(y,q);need(x==expected,'row arithmetic mismatch')
     need(fast.Row(left).scale(q)=={k:q*v for k,v in left.items()},'scale zero-pattern mismatch');count+=1
 x=fast.Row({0:1});y=x.clone();y.add_scaled(fast.Row({1:1}),Q(1));need(x=={0:1} and y=={0:1,1:1},'COPY must not alias')
 return count

def build(pins):
 check_pins(pins);source=run.source();new=fast.transform(source)
 need(assertion_list(source)==assertion_list(new),'original assertions changed')
 arithmetic=arithmetic_controls()
 with tempfile.TemporaryDirectory(prefix='verify-',dir=HERE) as td:
  directory=Path(td);members=materialize(directory)
  reference_outcomes=[];candidate_outcomes=[]
  reference,ref_log=run.execute(directory,'reference',outcomes=reference_outcomes);candidate,fast_log=run.execute(directory,'integer',outcomes=candidate_outcomes)
  need(reference==candidate and ref_log==fast_log,'complete receipt/stdout mismatch')
  need(reference_outcomes==candidate_outcomes and len(reference_outcomes)==27,'all pass/rejection outcome signatures')
  ref_trace,ref_entries=tracing(directory,'reference');fast_trace,fast_entries=tracing(directory,'integer')
  need(ref_entries==fast_entries and ref_trace==fast_trace,'complete scalar-prefix state mismatch')
  rejected=[]
  def reject(name,fn):
   try:fn()
   except (AssertionError,ValueError,KeyError):rejected.append(name);return
   raise ValueError('control accepted: '+name)
  reject('missing_source_pin',lambda:check_pins(dict(list(pins.items())[1:])))
  reject('duplicate_JSON',lambda:loads('{"x":1,"x":2}'))
  reject('nonfinite_JSON',lambda:loads('[NaN]'))
  reject('floating_seed',lambda:identity({'seed':90.0}))
  reject('changed_rewrite_boundary',lambda:fast.transform(source.replace('rows={','rows = {',1)))
  class DroppedADD(fast.Row):
   def clone(self):
    r=DroppedADD();r.values=self.values.copy();r.exponent=self.exponent;return r
   def add_scaled(self,other,q):pass
  reject('faulty_engine_drops_ADD',lambda:run.execute(directory,'integer',DroppedADD))
  class UnclearedZero(fast.Row):
   def __init__(self,values=None):
    super().__init__(values)
    if values is None:self.values={0:1}
  reject('faulty_engine_does_not_clear',lambda:run.execute(directory,'integer',UnclearedZero))
  receipt=loads(reference)
  need(len(receipt['negative_controls_rejected'])==25,'full retained mutation coverage')
  return {'seed':90,'base':'ce7ad1b6ab09452c3478723a2e96ed5ff212dc08','sources':pins,'members':members,
   'original_assertions_preserved':len(assertion_list(source)),'source_rewrites':len(fast.REWRITES),'arithmetic_cases':arithmetic,
   'retained_receipt':receipt,'receipt_LF_sha256':sha(reference.replace(b'\r\n',b'\n')),'stdout_sha256':sha(ref_log.encode()),'complete_scalar_prefixes':ref_trace,
   'complete_outcome_signatures':reference_outcomes,'extra_controls':rejected}

def benchmark(pairs_count):
 need(pairs_count>=3,'at least three alternating pairs')
 results=[]
 with tempfile.TemporaryDirectory(prefix='bench-',dir=HERE) as td:
  directory=Path(td);materialize(directory)
  for i in range(pairs_count):
   pair=[]
   for engine in (('reference','integer') if i%2==0 else ('integer','reference')):
    timing=directory/'TIMING.json';started=time.perf_counter()
    p=subprocess.run([sys.executable,'-I','-B',str(HERE/'run.py'),str(directory),'--engine',engine,'--timing',str(timing)],capture_output=True,text=True)
    need(p.returncode==0,'benchmark subprocess failed: '+p.stderr)
    sample=loads(timing.read_bytes());sample['fresh_process_wall_seconds']=time.perf_counter()-started;pair.append(sample)
   need(len({x['receipt_LF_sha256'] for x in pair})==1 and len({x['stdout_sha256'] for x in pair})==1,'benchmark receipt coverage mismatch')
   results.append(pair)
 ratios=[];process_ratios=[];cpu_ratios=[]
 for pair in results:
  d={x['engine']:x for x in pair};ratios.append(d['reference']['wall_seconds']/d['integer']['wall_seconds'])
  process_ratios.append(d['reference']['fresh_process_wall_seconds']/d['integer']['fresh_process_wall_seconds'])
  cpu_ratios.append(d['reference']['cpu_seconds']/d['integer']['cpu_seconds'])
 return {'python':sys.version,'platform':platform.platform(),'pairs':results,'paired_wall_ratios':ratios,'median_full_audit_wall_ratio':statistics.median(ratios),
  'paired_fresh_process_wall_ratios':process_ratios,'median_fresh_process_wall_ratio':statistics.median(process_ratios),'paired_audit_CPU_ratios':cpu_ratios,'median_audit_CPU_ratio':statistics.median(cpu_ratios),
  'implementation_LF_hashes':{p:fsha(HERE/p) for p in ['fast.py','run.py','verify.py']},'source_hashes':loads((HERE/'SOURCES.json').read_bytes()),
  'timing_scope':'fresh process; reported audit interval includes source authentication, imports inside pinned audit, input reads, full two-orientation checker, all25 mutations, output write and captured stdout; archive materialization excluded; no cold-chain or multiplication speedup'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--benchmark',action='store_true');args=ap.parse_args()
 pins=loads((HERE/'SOURCES.json').read_bytes());result=build(pins)
 if args.write:(HERE/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 else:
  saved=loads((HERE/'CERTIFICATE.json').read_bytes());identity(saved);need(canonical(saved)==canonical(result),'complete saved receipt mismatch')
 if args.benchmark:(HERE/'BENCHMARK.json').write_text(json.dumps(benchmark(3),indent=2)+'\n')
 print('PASS_EMITTED_LOCAL_INTEGER_S90 columns=704 orientations=2 retained_controls=25 extra_controls='+str(len(result['extra_controls']))+' scalar_prefixes='+str(sum(v['scalar_prefixes'] for v in result['complete_scalar_prefixes'].values())))

if __name__=='__main__':main()
