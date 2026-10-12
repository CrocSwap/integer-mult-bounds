"""Conservative finite union invoice and global prefix for two selected words.
Each full homogeneous source invoice is recounted independently. Their sum
bounds every mixed call, wrapper, private work and route without undercharging.
"""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,subprocess,os,sys
ROOT=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();BASE=R/'local';H=R/'mixed';O=H/'invoice';O.mkdir(exist_ok=False)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
t=read(H/'GLOBAL-TEMPLATE.json.gz');control=read(H/'AUDIT.json');profile={int(r):n for r,n in control['profile'].items()};mass=sum(r*n for r,n in profile.items());assert 73*7680-mass==2496;receipts={}
for name in ['baseline','middle']:
 d=O/name;d.mkdir();assert read(BASE/name/'RECEIPT.json')['status']=='PASS_LOCAL_WORD_SCALAR_PHASE_LABEL_GUARDED_PHYSICS'
 (d/'OWNERS-AND-PROFILE.json').write_text(json.dumps(dict(rank_mass=mass,paid_profile=profile,live=7680))+'\n')
 log=d/'recount.log'
 with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(ROOT/'code/audit_scalar_invoice.py'),str(d),str(BASE/name),str(H)],env=dict(os.environ,PYTHONINTMAXSTRDIGITS='0',PYTHONDONTWRITEBYTECODE='1'),stdout=f,stderr=subprocess.STDOUT)
 assert q.returncode==0,(name,log.read_text()[-3000:]);receipts[name]=read(d/'PREFIX-AND-INVOICE.json')
# The nonnegative cost of the selected 64+8 calls and all static adapters is
# bounded by the union of both complete 72-call programs and their overcharges.
used=sum(x['conservative_pervertex_used'] for x in receipts.values());compiler=max(x['compiler'] for x in receipts.values());M=73;P=8258;r=M//2;group=2**(r*r)
for i in range(1,r+1):group*=2**(2*i)-1
stock=group*P;smass=group*mass;logical=group*used+64;router=compiler*(logical+1)*(stock+1)**2;G,E,C0=2**30000,2**100000,2**210000;B=smass+E;literal=2*G*stock**2+8*smass+4*stock+4+32*M;row=2*stock.bit_length()+9909+252
checks=dict(logical=logical<2**6050,router=router<G,literal=literal<E,mass=B<2**100001,precision=32*M*B*B<C0,tape=2*B+18<C0,row=row<20161,halving=M*M>2*max(profile)**2);assert all(checks.values())
assert len(t['idle_children'])<=min(sum(z['replicas'] for z in read(BASE/name/'split-centres/GLOBAL-TEMPLATE.json.gz')['idle_children']) for name in receipts)
peak=max(F(z['prefix_l1']) for x in receipts.values() for z in x['local'].values());localbits=peak.numerator.bit_length()-peak.denominator.bit_length()+1;bridges=sum(e['kind']=='bridge' for e in t['recipe']);payload=localbits+37+len(t['calls'])+bridges+4;assert payload<192
for name in receipts:
 c=BASE/name/'lemmaG'
 for script in ['lg_instances','lg_e2e']:
  guard=read(c/('PREOP-GUARDS-'+script+'.json'));assert guard['identity_assertions_passed'] and guard['maximum_proved_numerator_bits']<63;f=c/guard['checked_result_file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==guard['checked_result_sha256']
report=dict(status='PASS_MIXED_GLOBAL_PREFIX_AND_CONSERVATIVE_UNION_INVOICE',pervertex_union=used,pervariant_pervertex={k:v['conservative_pervertex_used'] for k,v in receipts.items()},actual_variant_invocations={name:sum(c['variant']==name for c in t['calls']) for name in receipts},strict_checks=checks,physical_row_coefficient=row,retained_row_coefficient=20161,local_prefix_bits=localbits,global_prefix_bits=payload,retained_payload_bits=192,physical_stock_bits=stock.bit_length(),logical_bits=logical.bit_length(),router_bits=router.bit_length(),required_C0_bits=(32*M*B*B).bit_length(),template_sha256=control['template_sha256'],proof='For each variant, the independently recounted full72call nonnegative invoice includes its local scalar primitives, selectors, wrappers, idle remainders and private workspace. Their sum dominates the actual selected64baseline+8middle calls and unchanged global geometry. Whole-owner injections and actual orthogonal maps make each completed helper endpoint unitary under the verified local identities. Each completed data invocation and each of9bridges contributes at most one factor2 in the maximum streamL2 norm; the maximum recounted local coefficient-work envelope plus37input-L2 bits and4primitive bits gives the global prefix. All-size compiler and analytic contracts remain inherited.',scope='Finite mixed-program admission under inherited all-size contracts. Bit supplier is source-pinned; no fresh bit replay here.')
(O/'MIXED-INVOICE.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
