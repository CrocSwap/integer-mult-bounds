"""Apply established completed entrance banks to the immutable PR200 physical word.
Light mode is candidate pricing, never complete word admission. --full replays all
source/target/dirty columns and exact frame/prime/terminal checks through PR200.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,sys,importlib.util,hashlib,contextlib,types
# Windows shim supplies only the removed resource diagnostic, never proof data.
try: import resource
except ImportError:
 resource=types.ModuleType("resource");resource.RUSAGE_SELF=0
 resource.getrusage=lambda _:types.SimpleNamespace(ru_maxrss=0)
 sys.modules["resource"]=resource
sys.set_int_max_str_digits(0);sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PKG=HERE.parents[2]/'research/paired-cube-diagonal-bit-168'
sys.path.insert(0,str(PKG/'bit'));sys.path.insert(0,str(PKG/'arithmetic'))
spec=importlib.util.spec_from_file_location('pr200_paid_proof',PKG/'bit/prove.py')
proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
# Match Linux provenance spelling only; determinants and factor identities untouched.
raw_prime_certificate=proof.prime_certificate
def portable_prime_certificate(word):
 record=raw_prime_certificate(word)
 record['input_sha256']={k.replace(chr(92),'/'):v for k,v in record['input_sha256'].items()}
 return record
proof.prime_certificate=portable_prime_certificate
def need(ok,why):
 if not ok:raise ValueError(why)
def encode(z):
 if isinstance(z,Q):return str(z)
 if isinstance(z,dict):return {str(k):encode(v) for k,v in z.items()}
 if isinstance(z,(tuple,list)):return [encode(v) for v in z]
 return z

def endpoint_checks():
 records=[]
 for width,copies in [(4,18),(24,3)]:
  for ring in [0,2,3,5]:
   def run(column,blocks):
    x=[int(j==column) for j in range(72)];y=[int(72+j==column) for j in range(72)]
    for block in blocks:
     for j in range(block*width,(block+1)*width):x[j],y[j]=y[j],x[j]
    return x+y
   for column in range(144):
    want=[int(j==(column+72)%144) for j in range(144)]
    need(run(column,range(copies))==want,'all dirty address columns full swap')
    need(run(column,list(range(copies))+list(reversed(range(copies))))==[int(j==column) for j in range(144)],'all inverse columns')
   for blocks in [list(range(copies-1)),list(range(copies))+[copies-1]]:
    need(run(72-width,blocks)!=[int(j==144-width) for j in range(144)],'adverse omitted/duplicate block')
   records.append(dict(width=width,blocks=copies,address_ring=ring,forward_columns=144,inverse_columns=144,negative_controls=2))
 return records

def literal_allocation(word_data):
 pairs=word_data['pairs'];donor={b:a for a,b in pairs}
 selected=sorted(z['role'] for z in word_data['gauges'] if z['role'] not in donor)
 sinks=json.loads((PKG/'selected/bit/sinks.json').read_text())
 removed={word_data['rootroles'][e['root']] for e in sinks}
 need(len(removed)==34 and not removed.intersection(selected),'terminal roles excluded from selected entrance banks')
 need(not set(selected).intersection(word_data['sources'].values()),'source births are not entrance gauges')
 allroles={donor.get(s,s) for s in range(18908)}-removed
 rest=sorted(allroles-set(selected))
 need(len(allroles)==17114 and len(selected)==2200 and len(rest)==14914,'every actual retained physical chain exactly once')
 records=[]
 for stage in range(3):
  totalbanks=0;assigned=set();digest=hashlib.sha256()
  for family,(roles,width,blocks) in enumerate([(selected,4,18),(rest,24,3)]):
   occurrences=[(replica,role) for replica in range(9) for role in roles]
   need(len(occurrences)%blocks==0,'exact full banks, no omitted residual child')
   for offset in range(0,len(occurrences),blocks):
    group=occurrences[offset:offset+blocks]
    need(len(group)==blocks and blocks*width==72,'each literal bank fills 72 coordinates')
    for block,label in enumerate(group):
     need(label not in assigned,'each role-copy receives one bank slot per stage');assigned.add(label)
     digest.update(f'{stage}:{family}:{offset//blocks}:{block}:{label[0]}:{label[1]}\n'.encode())
   totalbanks+=len(occurrences)//blocks
  need(len(assigned)==9*17114 and totalbanks==45842,'complete stage-private physical stock')
  records.append(dict(stage=stage,assigned_role_copies=len(assigned),selected_banks=1100,undeferred_banks=44742,total_banks=totalbanks,allocation_sha256=digest.hexdigest()))
 return dict(stages=records,data_registers=2*9*1760,total_persistent_registers=3*45842+2*9*1760,arbitrary_dirty_contents=True,normalization='Common ancestor weighted chart; literal disjoint coordinate partialSwap blocks; role normalizers chosen distinctly inside each bank by inherited fixed conjugation/routing construction.')

def packed(row,word_data):
 pairs=word_data['pairs'];recipients={b for a,b in pairs};gauges=word_data['gauges']
 starts={z['role']:z['dim'] for z in gauges if z['role'] not in recipients}
 need(Counter(starts.values())=={20:2200},'genuine surviving entrance gauges')
 need(not set(starts).intersection(word_data['sources'].values()),'source births are not bank entrance gauges')
 touched={s for i in word_data['phase1'] for s in word_data['ops'][i][:2]}
 need(not set(starts).intersection(touched),'entrance gauges untouched throughout centre phase')
 need(Counter(z['dim'] for z in gauges if z['role'] in recipients)=={21:1760},'spliced recipients not bank roles')
 need(row['R']==17114 and row['terminal_sinks']==34,'retained exact physical terminals')
 rest=row['R']-len(starts)
 H={int(k):v for k,v in row['child_histogram'].items()};need(H.pop(60)==2200,'remove exactly actual entrance exteriors')
 W=Q(2*row['v'])+3*(Q(len(starts),18)+Q(rest,3))
 mass=sum(k*v for k,v in H.items());need(72*W-mass==1936,'full telescoping deficit')
 t=9
 need(t*2200%18==0 and t*rest%3==0,'integral stage-private configuration')
 scaled=dict(row,W_per_vertex=int(3*W),rank_per_vertex=3*mass,deficit_per_vertex=3*1936,maxchild=max(H),child_histogram={k:3*v for k,v in H.items()})
 return dict(m=72,W_per_vertex=W,rank_per_vertex=mass,deficit_per_vertex=1936,maxchild=max(H),child_histogram=H,selected_entrances=2200,undeferred_physical_chains=rest,physical_replicas=t,selected_banks_per_stage=t*2200//18,undeferred_banks_per_stage=t*rest//3,scaled_moment_profile=scaled)

def main():
 import gzip
 cert=json.loads((PKG/'certificate.json').read_text());row=cert['bit']['profile']
 data=json.loads(gzip.decompress((PKG/'selected/bit/word_p12.json.gz').read_bytes()))
 full='--full' in sys.argv
 if full:
  import io
  sink=io.StringIO()
  with contextlib.redirect_stdout(sink):proof.main()
  actual=json.loads(sink.getvalue());need(actual==cert['bit'],'complete word admission reproduces frozen bit certificate')
  row=actual['profile']
 p=packed(row,data)
 coarse=proof.certify(p['scaled_moment_profile'])
 from base_two_moment import moment as alternate_moment
 q=p['scaled_moment_profile'];H=list(q['child_histogram'].items());a=coarse['coarse_saving'];W=q['W_per_vertex'];edgecount=sum(n for r,n in H)
 _,upper=alternate_moment(72,W,H,a);_,bad=alternate_moment(72,W,[(1,32*72**2*edgecount)],a)
 need(upper+Q(1,10**16)*bad<1,'independent base-two paid acceptance')
 lower,_=alternate_moment(72,W,H,a+Q(1,10**18));badlow,_=alternate_moment(72,W,[(1,32*72**2*edgecount)],a+Q(1,10**18))
 need(lower+Q(1,10**16)*badlow>1,'independent adjacent paid exclusion')
 out=dict(status='PASS_FULL_BIT_ADMISSION' if full else 'PRICED_CANDIDATE_NOT_ADMITTED',base_pin='a1175449f34d39ff933d9d8ab23ced1f32b290ec',base_certificate_sha256=hashlib.sha256((PKG/'certificate.json').read_bytes()).hexdigest(),profile=p,coarse=coarse,endpoints=endpoint_checks(),literal_allocation=literal_allocation(data),universal_proof='Established ring-general disjoint partialSwap endpoint, arbitrary dirty contents, nine physical replicas, same weighted chart and charged routing. No source-birth bank gauge or characteristic-two odd-field substitution.',scope='Bit endpoint, complete paid child profile and exact moments only. Full root balanced assembly remains primary-owned.')
 (HERE/('packed-pr200-full.json' if full else 'packed-pr200-priced.json')).write_text(json.dumps(encode(out),sort_keys=True,indent=2))
 print(json.dumps(encode(dict(status=out['status'],W=p['W_per_vertex'],rank=p['rank_per_vertex'],coarse=coarse['coarse_saving'],effective=coarse['ordinary_saving'],effective_float=float(coarse['ordinary_saving']),selected=2200,rest=p['undeferred_physical_chains'])),indent=2))
if __name__=='__main__':main()