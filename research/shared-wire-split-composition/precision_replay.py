#!/usr/bin/env python3
"""Authenticated reuse of #6970 grid and #6985 envelope engines.
Not an independently implemented precision proof. Prepared with OpenAI assistance.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,types
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run without -O; assertions are proof checks.')
def engine(name,relative,changes=()):
 path=HERE/relative;src=path.read_text()
 for before,after in changes:
  assert src.count(before)==1;src=src.replace(before,after)
 mod=types.ModuleType(name);mod.__file__=str(path);sys.modules[name]=mod;exec(compile(src,str(path),'exec'),mod.__dict__);return mod

def run(word,caller,gate,manifest):
 for item in manifest['files']:
  if item['path'].startswith('retained/'):
   assert hashlib.sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256']
 G=engine('source_grid_integer','retained/odd-native-common-grid/independent_bounds.py')
 B=engine('source_binding','retained/query-only-precision-envelope/source_binding.py')
 helper_count=word['public']-400
 changes=[('word["public"] - len(mains) == 1061',f'word["public"] - len(mains) == {helper_count}'),('fresh_arbitrary_helpers=18 * 1061',f'fresh_arbitrary_helpers=18 * {helper_count}')]
 E=engine('source_precision_envelopes','retained/query-only-precision-envelope/envelopes.py',changes)
 wg=G.word_run(word);cg=G.caller_run(caller);wp,wr=E.native_envelope(word);cp,cr=E.caller_envelope(caller,wp,word)
 height=max(cg['denominator_height'],cg['pre_joint_height']+wg['dyadic_height'])
 mass=max(B.strict_power(F(cg['maximum_mass'])),B.strict_power(F(cg['pre_joint_mass']))+B.strict_power(F(wg['maximum_scaled_mass'])))
 controls={}
 for scale,frac in ((375,24),(225,24),(1125,23)):
  try:G.word_run(word,scale,frac)
  except ValueError as e:controls[f'S{scale}_f{frac}']=str(e)
  else:raise AssertionError('Insufficient grid accepted')
 H=int(gate['H']);lp=gate['written_log_power'];step=F(gate['compiler_gap']).denominator;j=H//step;kstar=1920*153**1920*(H+1)**2
 assert (H+1)**lp<2**j and (H-step+1)**lp>=2**(j-1) and (4096*kstar).bit_length()<H
 return dict(method='attributed source-engine reuse',helper_census_substitutions=changes,common_grid=dict(word=wg,caller=cg,context_height=height,context_mass_bits=mass,context_c=2*max(height,mass)),rounded_envelope=dict(native=wr,caller=cr),threshold=dict(H=H,LP=lp,Kstar_bits=kstar.bit_length(),scaled4096_Kstar_bits=(4096*kstar).bit_length()),negative_grid_controls=controls,scope='Exact children for common grid. Total RDiv plus complete-fibre unitary contracts for rounded envelopes. Neither is a physical provider admission.')
