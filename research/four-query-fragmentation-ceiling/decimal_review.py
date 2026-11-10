from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction
import json
p=Path(__file__).resolve().parent
result=json.loads((p/'RESULT.json').read_text())
def rational(x):
 q=Fraction(x);return D(q.numerator)/q.denominator
out={}
with localcontext() as ctx:
 ctx.prec=85
 for name in ('complex','bit'):
  x=result[name];s=D(x['body_rank']);ports=D(x['ports']);k=rational(x['uniform_interval'][0]);t=1-k
  def H(n):return D(n)**t
  def inc(n):return H(s*n+1)-H(s*n)
  ell=(sum(D(c)*H(r)for r,c in x['native_helpers'].items())-sum(D(c)*H(r)for r,c in x['native_paid'].items()))/ports
  A=2*inc(2)-1
  B=50*ell+44*A+4*inc(1)+H(50*s+1)+2*H(25*s+1)-2
  derivative=ell+A+s*t*(D(50*s+1)**(-k)+D(25*s+1)**(-k))
  for value,key in ((B,'tail_at_lower'),(derivative,'tail_derivative_at_lower')):
   enclosure=x[key]
   if not D(enclosure['lower'])<=value<=D(enclosure['upper']):raise ValueError(key)
  ceiling=rational(x['raw_ceiling']);t=1-ceiling
  raw=json.loads((p/'inputs'/f'{name.upper()}-INVOICE.json').read_text())
  def find(q):
   if isinstance(q,dict):
    if q.get('status')=='PASS_TWO_PAID_FRAGMENTS_COMPLETE_PRICE':return q
    for v in q.values():
     z=find(v)
     if z is not None:return z
  raw=find(raw)if name=='complex'else raw
  moment=(sum(D(c)*D(r)**t for r,c in raw['targets'].items())-sum(D(c)*D(r)**t for r,c in raw['paid'].items()))/ports
  enc=x['finite_maximum_at_ceiling']
  if not D(enc['lower'])<=moment<=D(enc['upper']):raise ValueError('literal invoice moment')
  out[name]={'B50_decimal85':str(B),'Bprime50_decimal85':str(derivative),'literal_invoice_margin_at_ceiling_decimal85':str(moment),'inside_C_exact_enclosures':True}
expected=json.loads((p/'DECIMAL-REVIEW.json').read_text())
if out!=expected:raise ValueError('retained independent Decimal review differs')
print(json.dumps(out,indent=2))
