from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Negative controls for the independent fresh-bank and price certificate."""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,struct,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
P=contract.BANK;A=contract.SOURCE
def read(n):
 b=Path(n).read_bytes();return json.loads(gzip.decompress(b) if str(n).endswith('.gz') else b)
B=read(P/'BANK-RESULT.json');C=read(P/'endpoint-charts.json.gz');price=read(P/'PRICE-RESULT.json');controls=[]
def rejects(name,fn):
 try:fn()
 except (AssertionError,ValueError):controls.append(name)
 else:raise AssertionError('accepted '+name)
def chart_check(cols,inv):
 assert len(cols)==len(inv)==20
 for i in range(20):
  for j in range(20):assert sum(Q(cols[k][i])*Q(inv[k][j]) for k in range(20))==int(i==j)
x=C['charts'][0];chart_check(x['basis_columns'],x['inverse']);bad=[r[:] for r in x['basis_columns']];bad[0][0]+=1
rejects('changed_chart_column',lambda:chart_check(bad,x['inverse']))
badinv=[r[:] for r in x['inverse']];badinv[0][0]=str(Q(badinv[0][0])+1);rejects('changed_chart_inverse',lambda:chart_check(x['basis_columns'],badinv))
def cover(blocks):
 a=list(range(200));used=set()
 for o,w in blocks:
  assert isinstance(o,int) and isinstance(w,int) and 0<=o<o+w<=100
  for j in range(o,o+w):assert j not in used;used.add(j);a[j],a[199-j]=a[199-j],a[j]
 assert used==set(range(100)) and a==list(range(199,-1,-1))
for width in [4,20]:
 blocks=[(i,width) for i in range(0,100,width)];cover(blocks)
 rejects('unpaid_padding_'+str(width),lambda:cover(blocks[:-1]));rejects('duplicate_block_'+str(width),lambda:cover(blocks+blocks[:1]));bad=blocks[:];bad[-1]=(bad[-1][0]-1,width);rejects('overlapping_block_'+str(width),lambda:cover(bad))
raw=gzip.decompress((P/'literal-bank-assignments.bin.gz').read_bytes());rows=list(struct.iter_unpack('>6I',raw));r0=rows[0]
def assignment_check(row):
 r,t,b,o,w,s=row;roles=C['roles'];assert 0<=t<60 and r in roles and w==(4 if str(r) in C['gauge_frames'] else 20)
 assert 0<=b<85680 and o%w==0 and 0<=o<o+w<=100 and 1<=s<=25
 assert s==o//w+1
assignment_check(r0)
rejects('wrong_role_width',lambda:assignment_check((*r0[:4],20,r0[5])))
rejects('out_of_range_bank',lambda:assignment_check((r0[0],r0[1],85680,*r0[3:])))
rejects('out_of_range_replica',lambda:assignment_check((r0[0],60,*r0[2:])))
rejects('wrong_block_scalar',lambda:assignment_check((*r0[:5],0)))
def stock_check(stock):assert isinstance(stock,int) and stock==230400+5*85680==B['literal_stock']
stock_check(658800);rejects('normalized_stock_as_literal_index',lambda:stock_check(10980));rejects('fractional_stock_index',lambda:stock_check(Q(658800)))
def bill_check(terms):
 E=14514000;assert terms['generic_wrappers']==E*80008 and terms['matrix_preparation']==E*128*200**3
 assert terms['bank_selectors']==170009279400 and sum(terms.values())==B['coefficient']
bill_check(B['terms']);bad=B['terms'].copy();bad['generic_wrappers']-=80008;rejects('omitted_child_wrapper',lambda:bill_check(bad));bad=B['terms'].copy();bad['bank_selectors']-=1;rejects('omitted_selector_call',lambda:bill_check(bad))
assert Q(price['exact_bit_bracket']['lower_moment'][1])<1<Q(price['exact_bit_bracket']['upper_moment'][0]);controls.append('adjacent_root_tick_rejected')
assert price['assembly']['adjacent_kappa_rejected']==['compact_phase_layer_above_kappa'];controls.append('adjacent_kappa_tick_rejected')
for name in ['check_base_ledger.py','check_admitted_banks.py','price_admitted_profile.py']:
 z=subprocess.run([sys.executable,'-O',str(contract.HERE/'bank'/name)],capture_output=True);assert z.returncode!=0 and b'Assertions must be enabled' in z.stderr;controls.append('optimized_python_'+name)
out={'status':'PASS_NEGATIVE_CONTROLS','count':len(controls),'controls':controls,'bank_result_sha256':hashlib.sha256((P/'BANK-RESULT.json').read_bytes()).hexdigest(),'price_result_sha256':hashlib.sha256((P/'PRICE-RESULT.json').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(P/'CONTROLS.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n');print(len(controls),'controls PASS')
