"""Check the exact two-profile target installer and scoped corruptions.

The serial envelope assumes the inherited source indexed-action census; the
new-word preprocessing allowance is charged separately. It is not a WASI trace.
"""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json,sys

if not __debug__: raise RuntimeError('Run with assertions enabled')
root=Path(sys.argv[1]).resolve()
runtime=root/'runtime';peer=root/'research'/'frequency-weighted-native-multiplier'
portable=peer/'portable';tier=peer.parent/'tiered-native-multiplier'
expected={
 'installations.py':'5df81fddba26013b142195f5c3119491fa2f07b1e72c3616ae76e7d7ffbb0fd1',
 'raw_binary_stage.py':'e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0',
 'grades.py':'6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d',
 'transport.py':'9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818',
 'retimed_supplier.py':'2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c',
 'strong_complex.py':'8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d',
 'w5669_shortcut5.json.gz':'6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149',
}
for name,want in expected.items(): assert sha256((runtime/name).read_bytes()).hexdigest()==want, name
sys.path[:0]=[str(runtime),str(portable),str(tier/'source'),str(tier)]
from upstream import install
install()
import installations
from band_product import prepare_native,production_supplier
from compiler_state import construct
from grades import WeightedRecipe
from record_census import inspect
from tape_directory import dump
from transport import Recipe
from activation import resource_receipt
from outer_budget import qualify

entry,terminal=installations.ENTRY,installations.TERMINAL
assert list(installations.PROFILES.values())==[entry,terminal]
assert (entry.rank_logs,entry.complex_log,entry.kappa)==((3000,3080),1024,Q(345,100000))
assert (terminal.rank_logs,terminal.complex_log,terminal.kappa,terminal.eta)==((8192,106000,1681001),85406,Q(39,10000),Q(1,256))
heights=(*entry.rank_logs,entry.complex_log,*terminal.rank_logs,terminal.complex_log)
assert all(1024<=h<2**25 for h in heights) and len(heights)==7

def scalar_values(p):
 return {'kappa_numerator':p.kappa.numerator,'kappa_denominator':p.kappa.denominator,
         'eta_numerator':p.eta.numerator,'eta_denominator':p.eta.denominator,
         'positive_stop_denominator':p.positive_stop_denominator}
def bounded(p):
 vals=scalar_values(p)
 return p.positive_stop_denominator>0 and all(type(x) is int and abs(x).bit_length()<=128 for x in vals.values())
assert all(bounded(p) for p in installations.PROFILES.values())
scalar_bits={name:{k:abs(v).bit_length() for k,v in scalar_values(p).items()} for name,p in installations.PROFILES.items()}
negative={
 'kappa_numerator':replace(terminal,kappa=Q(1<<128,1)),
 'kappa_denominator':replace(terminal,kappa=Q(1,1<<128)),
 'eta_numerator':replace(terminal,eta=Q(1<<128,1)),
 'eta_denominator':replace(terminal,eta=Q(1,1<<128)),
 'stop_oversized':replace(terminal,positive_stop_denominator=1<<128),
 'stop_zero':replace(terminal,positive_stop_denominator=0),
}
assert all(not bounded(p) for p in negative.values())
stock=resource_receipt(terminal);entry_stock=resource_receipt(entry)
assert tuple(stock['binary_cuts'])==(8290,114354,1795419)
assert stock['retimed_first_stripe_margin']>1024 and stock['retimed_all_size_margin_floor']>1024

def rejected(fn):
 try: fn()
 except (ArithmeticError,AssertionError,ValueError,ZeroDivisionError): return True
 return False

bad_stock=replace(terminal,rank_logs=(8192,stock['binary_cuts'][0]+2,terminal.rank_logs[-1]))
assert rejected(lambda:resource_receipt(bad_stock))
assert not all(1024<=h<2**25 for h in (*terminal.rank_logs,2**25))
positive=installations.GAUSSIAN_C-Q(1039776,2**23*terminal.complex_log)
g=Q(1,terminal.positive_stop_denominator)
signed=qualify(terminal.kappa,g,terminal.ordinary,positive)
assert rejected(lambda:qualify(terminal.kappa,Q(0),terminal.ordinary,positive))
assert rejected(lambda:qualify(terminal.kappa,Q(1,10**6),terminal.ordinary,positive))
conversion=((terminal.kappa-entry.kappa)*stock['public_exponent_A']).__ceil__()
assert conversion-1<(terminal.kappa-entry.kappa)*stock['public_exponent_A']<=conversion

carrier_steps=2*2048*(2**25+1); scalar_steps=7*2**24
# Charge a full extra source numerical compiler, plus explicit shortcut
# decoding/authentication, without assuming unused predecessor slack.
new_word_compiler_allowance=2**64; shortcut_allowance=2**55
extra=carrier_steps+scalar_steps+new_word_compiler_allowance+shortcut_allowance
assert extra<2**65
w,n=2**38,2**68+2**65;h=2*w+2
S=4*w*n;L=8*S*512*128
E=2**16*(h+4)*(7*h+9)+8*2**16*(h+4)**2
serial=(n+1)*(L+E+2**120)*2**32
assert serial==274865081678638624429267135103304688028750991263086118674744387567616 and serial<2**228
def require_widths(layers):
 assert all(r.width_log==92*r.rank_log for layer in layers for r in layer)

saved=Recipe.open,Recipe.width,WeightedRecipe.open,WeightedRecipe.width

def forbidden(*args,**kwargs): raise AssertionError('fixed constructor touched a lazy opening or width')
Recipe.open=forbidden;Recipe.width=property(forbidden);WeightedRecipe.open=forbidden;WeightedRecipe.width=property(forbidden)
try:
 state=construct();layers=state[0]
 assert [[r.rank_log for r in layer] for layer in layers]==[list(heights[:3]),list(heights[3:])]
 assert tuple(prepare_native(terminal))==layers[1]
 require_widths(layers)
 target=layers[1][-1]; prior_width=target.width_log
 try:
  target.width_log=prior_width+1
  assert rejected(lambda:require_widths(layers))
 finally: target.width_log=prior_width
 require_widths(layers)
 assert all(r.level_floor==18960 for layer in layers for r in layer[:-1])
 assert all(r.targets is state[1].targets and r.paid is state[1].paid and r.cells is state[1].cells for layer in layers for r in layer[:-1])
 assert layers[0][-1].targets is layers[1][-1].targets and layers[0][-1].cells is layers[1][-1].cells
 suppliers=[production_supplier(p.complex_log,p.positive_stop_denominator) for p in (entry,terminal)]
 assert all(s.recipe is layer[-1] for s,layer in zip(suppliers,layers,strict=True))
 assert all(s.carrier.bit_length()==p.complex_log+1 and s.carrier.bit_count()==1 for s,p in zip(suppliers,(entry,terminal),strict=True))
 with TemporaryDirectory(prefix='target-8088-setup-') as tmp:
  out=Path(tmp)/'directory.dag'
  with out.open('wb') as f: count=dump(f,state)
  census=inspect(out);directory_sha=sha256(out.read_bytes()).hexdigest()
  assert count==census['records'] and count<2**32 and census['bytes']<2**38 and census['largest_integer_bits']<2**38
finally:
 Recipe.open,Recipe.width,WeightedRecipe.open,WeightedRecipe.width=saved

print(json.dumps({'scope':'actual fixed constructor, encoded profiles, stock and separately priced serial envelope; no portable trace or all-size admission',
 'runtime_sha256':expected,'heights':heights,'profile_scalar_bits':scalar_bits,'scalar_guard_bits':128,
 'scalar_corruptions_rejected':sorted(negative),'zero_and_weak_stop_rejected':True,'changed_recipe_width_rejected':True,'prefix_stock_corruption_rejected':True,'25_bit_boundary_rejected':True,
 'positive_margin':str(positive-terminal.kappa-5*g),'signed':signed,'entry_stock':entry_stock,'terminal_stock':stock,'entry_conversion_bits':conversion,
 'carrier_bits':[s.carrier.bit_length() for s in suppliers], 'directory_records':count,'directory_bytes':census['bytes'],
 'largest_directory_integer_bits':census['largest_integer_bits'],'directory_sha256':directory_sha,
 'carrier_scalar_actions':carrier_steps+scalar_steps,'new_word_preprocessing_actions_reserved':shortcut_allowance,
 'new_word_compiler_actions_reserved':new_word_compiler_allowance,
 'combined_extra_actions':extra,'extra_action_ceiling':2**65,'serial_transition_upper':serial,'power_of_two_upper':228,
 'inherited_bound_status':'Requires the inherited 2^68 action and 2^38 datum bounds, and a source-specific proof that the complete numerical compiler for the new word fits the separately reserved 2^64 actions; finite census alone does not establish them.'},indent=2,sort_keys=True))
print('PASS_8088_TARGET_FIXED_CONSTRUCTOR',flush=True)
