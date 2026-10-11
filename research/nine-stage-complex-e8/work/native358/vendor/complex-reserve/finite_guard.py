"""Parity-correct exact binary orthogonal cover invoice for the pinned E8 supplier.
OpenAI Codex assistance; corrects PR352 even-dimension formula at m=45.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from math import prod
def orth_order(m):
 if m%2:
  r=m//2;return(1<<(r*r))*prod((1<<(2*i))-1 for i in range(1,r+1))
 return(1<<(m-1+(m//2-1)**2))*prod((1<<(2*i))-1 for i in range(1,m//2))

def finite_guard(raw,cert):
 enumeration={}
 for d in [1,2,3,4,5]:
  odd=[x for x in range(1,1<<d)if x.bit_count()%2]
  def count(rows):return 1 if len(rows)==d else sum(count(rows+[x])for x in odd if all((x&y).bit_count()%2==0 for y in rows))
  actual=count([]);assert actual==orth_order(d);enumeration[d]=actual
 h,v,R=cert['h'],cert['v'],cert['R'];assert (h,v,R)==(9,120,783);m=5*h;W=4*v+R;physical=W+R+h+1;ledger=raw['ledger'];b=raw['scalar_bill'];checks=raw['label_checks'];scalar=max(b[o]['totals']['real_component_primitive_steps']for o in ['forward','backward']);macros=max(b[o]['totals']['scalar_macros']for o in ['forward','backward']);scalar5=3*b['forward']['totals']['real_component_primitive_steps']+2*b['backward']['totals']['real_component_primitive_steps'];adapters=8*(macros+checks['invocation_calls']+(2*v+R)+h)+32*m;outside=8*(ledger['idle_calls']+6*v+physical)+32*m;compiler=64*(m+1)**3;local=scalar+adapters*compiler;pervertex=scalar5+12*v+(5*adapters+outside)*compiler+64*physical;group=orth_order(m);live_stock=group*W;physical_stock=group*physical;s=group*ledger['rank_mass'];K=group*pervertex+64;router=compiler*(K+1)*(physical_stock+1)**2;Glim,E,C0=1<<30000,1<<100000,1<<210000;Bbig=s+E;literal=2*Glim*physical_stock**2+8*s+4*physical_stock+4+32*m
 assert local<1<<48 and K<1<<6050 and router<Glim and literal<E and Bbig<1<<100001
 assert 32*m*Bbig*Bbig<C0 and 2*Bbig+18<C0 and 2*ledger['max_child']<m
 assert 2*Bbig*(m-ledger['max_child'])-s-E==49*Bbig
 row=live_stock.bit_length()+9909+252;rowphysical=physical_stock.bit_length()+9909+252;assert row<=rowphysical<20161
 bill=dict(scalar_max=scalar,scalar_five_invocations=scalar5,macros_max=macros,adapters=adapters,outside=outside,compiler=compiler,pervertex=pervertex,orthogonal_group=group,live_stock=live_stock,physical_stock=physical_stock,rank_mass=s,logical_groups=K,router=router,literal=literal)
 correct=dict(status='PASS_CORRECTED_ODD_DIMENSION_COMPLETE_FINITE_INVOICE',orthogonal_order_formula='|O(2r+1,2)|=|Sp(2r,2)|=2^(r*r)*product(2^(2*i)-1,i=1..r)',small_dimension_complete_orthogonal_basis_enumeration=enumeration,group_bits=group.bit_length(),live_stock_bits=live_stock.bit_length(),physical_stock_bits=physical_stock.bit_length(),rank_mass_bits=s.bit_length(),global_logical_groups_bits=K.bit_length(),router_bits=router.bit_length(),literal_charge_bits=literal.bit_length(),live_row_coefficient=row,physical_row_overcharge_coefficient=rowphysical,retained_row_coefficient=20161,induction_gap_multiple_of_B=49,all_retained_guards_pass=True,complete_invoice=bill)
 old_group=(1<<(m-1+(m//2-1)**2))*prod((1<<(2*i))-1 for i in range(1,m//2));controls={}
 def validate(z):
  assert z['physical']==z['live']+R+h+1
  assert m*z['live']-ledger['rank_mass']==ledger['deficit']
  assert z['copy_calls']==5*ledger['centres']
  assert z['denominators']==[1,2,3,6]
  assert z['group']==group and physical_stock<1<<z['stock_exponent']
 original=dict(physical=physical,live=W,copy_calls=5*ledger['centres'],denominators=[1,2,3,6],group=group,stock_exponent=physical_stock.bit_length());validate(original)
 for name,key,value in [('missing_tableau','physical',physical-R),('scratch_in_live','live',physical),('dropped_center','copy_calls',5*ledger['centres']-1),('unrecorded_divisor','denominators',[1,2,3,5,6]),('stale_stock_bound','stock_exponent',physical_stock.bit_length()-1),('even_dimension_order_at_odd_m','group',old_group)]:
  z=dict(original);z[key]=value
  try:validate(z)
  except AssertionError:controls[name]=True
  else:raise AssertionError('invalid finite guard accepted: '+name)
 result=dict(raw['precision_guard']);result.update(correct);result.update(m=m,live_per_vertex=W,physical_per_vertex=physical,controls=controls,complete_local_group_upper=local,complete_local_group_bits=local.bit_length(),coefficient_denominators=[1,2,3,6],semantic_C1=1,required_C0_bits=(32*m*Bbig*Bbig).bit_length(),C0_exponent=210000,E_exponent=100000,G_exponent=30000)
 return result
