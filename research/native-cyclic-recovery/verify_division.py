from fractions import Fraction
from pathlib import Path
import json,random,time,hashlib,importlib.util,sys
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fixed_divisor',ROOT/'fixed_divisor.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
divide_unsigned=module.divide_unsigned;divide_signed=module.divide_signed;fixed_rational=module.fixed_rational;need=module.need
start=time.monotonic();cases=0;maxops=0;large=[]
for divisor in (2,3,5,7,9,17):
 for width in range(1,10):
  for value in range(1<<width):
   q,r,ops=divide_unsigned(value,divisor,width)
   need((q,r)==divmod(value,divisor),'exhaustive exact quotient/remainder')
   cases+=1;maxops=max(maxops,ops)
rng=random.Random(20261022)
for divisor in (2,3,7,31,76545,40131624960):
 for width in (8,16,31,32,63,64,65,127,128,129,256,512,1024,4096):
  if width<divisor.bit_length()+1:continue
  values=[0,1,divisor-1,divisor,divisor+1,(1<<width)-1]
  values += [rng.getrandbits(width)for unused in range(4)]
  for value in values:
   q,r,ops=divide_unsigned(value,divisor,width)
   need((q,r)==divmod(value,divisor),'large exact quotient/remainder')
   cases+=1;maxops=max(maxops,ops)
  large.append({'divisor':divisor,'width':width,'cases':len(values),'operations':ops})
rounds=0
for width in range(1,9):
 for divisor in (1,2,3,5,7,17,76545):
  for value in range(-((1<<width)-1),1<<width):
   for mode in ('floor','toward_zero','nearest_even'):
    got,_=divide_signed(value,divisor,width,mode);ref=Fraction(value,divisor)
    expected=ref.numerator//ref.denominator if mode=='floor'else int(ref)if mode=='toward_zero'else round(ref)
    need(got==expected,'all-small-width signed rounding');rounds+=1
for divisor in (2,3,5,7,17,76545):
 width=max(16,divisor.bit_length()+1)
 for value in list(range(-100,101))+[-divisor-1,-divisor,-divisor+1,divisor-1,divisor,divisor+1]:
  for rounding in ('floor','toward_zero','nearest_even'):
   result,ops=divide_signed(value,divisor,width,rounding)
   ref=Fraction(value,divisor)
   expected=ref.numerator//ref.denominator if rounding=='floor' else int(ref)if rounding=='toward_zero'else round(ref)
   need(result==expected,'signed rounding')
   rounds+=1
rational=0
for numerator in (-111, -2,-1,0,1,2,37,219800272896):
 for denominator in (1,2,7,76545,40131624960):
  for value in (-65535,-17,-1,0,1,17,65535):
   for rounding in ('floor','toward_zero','nearest_even'):
    got,ops,width=fixed_rational(value,numerator,denominator,16,rounding)
    ref=Fraction(value*numerator,denominator)
    expected=ref.numerator//ref.denominator if rounding=='floor'else int(ref)if rounding=='toward_zero'else round(ref)
    need(got==expected,'fixed rational signed rounding')
    rational+=1
controls=[]
for mutation in ('wrong_weight','wrong_suffix'):
 witness=None
 for value in range(256):
  try:q,r,_=divide_unsigned(value,7,8,mutation)
  except ValueError:witness=value;break
  if (q,r)!=divmod(value,7):witness=value;break
 need(witness is not None,'mutation must fail')
 controls.append({'mutation':mutation,'witness':witness})
for args in ((256,7,8),(1,0,8)):
 try:divide_unsigned(*args)
 except ValueError:continue
 raise ValueError('invalid contract accepted')
out={'status':'PASS_FIXED_DIVISOR_BITPLANE_SCAN','unsigned_cases':cases,'signed_rounding_cases':rounds,'fixed_rational_cases':rational,'maximum_counted_word_operations':maxops,'large_cases':large,'controls':controls,'algorithm_source_sha256':hashlib.sha256((ROOT/'fixed_divisor.py').read_bytes()).hexdigest(),'new_kappa':None}
expected=ROOT/'DIVISION-RESULT.json'
if '--write' in sys.argv:expected.write_text(json.dumps(out,indent=2)+'\n')
else:need(json.dumps(json.loads(expected.read_text()),sort_keys=True)==json.dumps(out,sort_keys=True),'frozen receipt mismatch')
print(out['status'],cases,rounds,rational,'seconds',round(time.monotonic()-start,3))
