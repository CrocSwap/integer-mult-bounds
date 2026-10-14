"""Fresh fine-engine checks at the new interior point; unchanged source engines."""
import importlib.util,json,hashlib,argparse,sys
from pathlib import Path
from fractions import Fraction as F
import ledger as L
if not __debug__:raise RuntimeError('Assertions must be enabled')
sys.set_int_max_str_digits(0)
P=Path(__file__).resolve().parent

def load(name):
 path=L.PARENT/'code'/(name+'.py')
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module,path

ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
merc,mp=load('fine_mercator');base,bp=load('fine_moment')
left=merc.moment(L.profile,L.m,L.W,L.b,False)
right=base.moment(L.m,L.W,list(L.profile.items()),L.b)
assert left[0]<=left[1]<1 and right[0]<=right[1]<1
assert L.q<L.b<L.certified_complex
result={'status':'PASS_FRESH_FINE_ENGINES_AT_INTERIOR_POINT','b':str(L.b),'q':str(L.q),'certified_endpoint':str(L.certified_complex),'mercator_margin':[str(x-1) for x in left],'base_two_margin':[str(x-1) for x in right],'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [mp,bp]},'profile':L.profile,'m':L.m,'W':L.W,'scope':'Actual unchanged fine engines at the new interior supplier point. Primitive endpoint/word/profile unchanged; complete supplier admission is source-bound reuse of the prior personal full replay. No new endpoint certification or theorem claim.'}
args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(result['status'])
