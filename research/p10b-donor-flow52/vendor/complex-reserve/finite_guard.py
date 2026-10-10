"""Recompute all p10 complex finite charges and retained precision inequalities.
Derived from byte-pinned PR315 portable_complex.finite_guard, with explicit
parameter-sensitive calculations. Prepared with OpenAI Codex; Apache-2.0.
"""
from fractions import Fraction as Q
from math import prod

def need(x,msg):
 if not x:raise ValueError(msg)

def finite_guard(manifest,bill,basis):
 p=manifest['parameters'];l=manifest['ledger'];dim=p['m'];R=p['R'];h=p['h'];v=p['v'];W=p['W_live']
 need((dim,h,v)==(100,20,960) and R>0 and W==4*v+R,'p10 complex dimensions')
 need(l['deficit']==4*v-5*h*(h-2)==2040 and l['max_child']==2*h+2==42,'p10 five-stage endpoint invoice')
 scalar=max(bill[o]['totals']['real_component_primitive_steps'] for o in ['forward','backward'])
 macros=max(bill[o]['totals']['scalar_macros'] for o in ['forward','backward'])
 scalar5=3*bill['forward']['totals']['real_component_primitive_steps']+2*bill['backward']['totals']['real_component_primitive_steps']
 physical=W+R+h+1
 adapters=8*(macros+manifest['checks']['invocation_calls']+p['invocation_live']+h)+32*dim
 outside=8*(l['idle_calls']+6*v+physical)+32*dim
 compiler=64*(dim+1)**3
 local=scalar+adapters*compiler
 pervertex=scalar5+12*v+(5*adapters+outside)*compiler+64*physical
 group=(1<<(dim-1+(dim//2-1)**2))*prod((1<<(2*i))-1 for i in range(1,dim//2))
 live_stock=group*W;physical_stock=group*physical;s=group*l['rank_mass']
 K=group*pervertex+64;router=compiler*(K+1)*(physical_stock+1)**2
 G,E,C0=1<<30000,1<<100000,1<<210000;B=s+E
 literal=2*G*physical_stock**2+8*s+4*physical_stock+4+32*dim
 need(local<1<<48 and K<1<<6050,'recomputed p10 local/global bill exceeds retained overcharge')
 need(router<G and literal<E and B<1<<100001,'recomputed p10 router/literal guard')
 induction_multiple=2*(dim-l['max_child'])-1
 need(induction_multiple==115 and 2*B*(dim-l['max_child'])-s-E==induction_multiple*B,'p10 completed-child induction')
 need(32*dim*B*B<C0 and 2*B+18<C0 and 2*l['max_child']<dim,'semantic and half-shrink guard')
 # The retained row proof explicitly permits the conservative <10000 stock term,
 # the bit-coarse reserve 9909 and the ordinary-leaf reserve 252. Check the new
 # actual stocks before retaining their sum 20161; never reuse p11 stock bits.
 coarse_leaf_reserve,ordinary_leaf_reserve,stock_overcharge=9909,252,10000
 need(live_stock.bit_length()<=physical_stock.bit_length()<stock_overcharge,'actual p10 physical stock row bound')
 row=live_stock.bit_length()+coarse_leaf_reserve+ordinary_leaf_reserve
 rowphysical=physical_stock.bit_length()+coarse_leaf_reserve+ordinary_leaf_reserve
 retained_row=stock_overcharge+coarse_leaf_reserve+ordinary_leaf_reserve
 need(row<=rowphysical<retained_row,'external rows')
 gap=Q(10**6)-Q(51,25)*retained_row;need(gap>0,'row reserve gap')
 need(2*(dim*(dim-1)+3*dim+dim+3*dim*(dim-1)//2+dim+1)+2*dim<compiler,'explicit quadratic-phase lowering')
 for e in range(1,100001):need((e-1).bit_length()+1<=2*e,'grid-depth endpoint')
 def validate(c):
  need(c['physical']==c['live']+R+h+1,'missing work stock')
  need(dim*c['live']-l['rank_mass']==l['deficit'],'wrong live normalization')
  need(c['copy_calls']==5*h,'missing center child')
  need(c['denominators']==[1,2,3,6],'unrecorded denominator')
  need(physical_stock<1<<c['stock_exponent'],'false stock bound')
 stockbits=physical_stock.bit_length();original=dict(physical=physical,live=W,copy_calls=5*h,denominators=[1,2,3,6],stock_exponent=stockbits)
 validate(original);controls={}
 for name,key,value in [('missing_tableau','physical',physical-R),('scratch_in_live','live',physical),('dropped_center','copy_calls',5*h-1),('unrecorded_divisor','denominators',[1,2,3,5,6]),('stale_stock_bound','stock_exponent',stockbits-1)]:
  bad=dict(original);bad[key]=value
  try:validate(bad)
  except ValueError:controls[name]=True
  else:raise ValueError('finite guard mutation accepted: '+name)
 return dict(status='PASS_FRESH_EXACT_P10_COMPLEX_GUARD',m=dim,live_per_vertex=W,physical_per_vertex=physical,coefficient_denominators=[1,2,3,6],semantic_C1=1,complete_local_group_upper=local,complete_local_group_bits=local.bit_length(),global_logical_groups_bits=K.bit_length(),simple_global_logical_bound_exponent=6050,router_bits=router.bit_length(),G_exponent=30000,literal_charge_bits=literal.bit_length(),E_exponent=100000,required_C0_bits=(32*dim*B*B).bit_length(),C0_exponent=210000,induction_gap_multiple_of_B=induction_multiple,group_bits=group.bit_length(),live_stock_bits=live_stock.bit_length(),physical_stock_bits=physical_stock.bit_length(),rank_mass_bits=s.bit_length(),live_row_coefficient=row,physical_row_overcharge_coefficient=rowphysical,retained_row_coefficient=retained_row,retained_row_gap=str(gap),row_terms=dict(stock_overcharge=stock_overcharge,actual_live_stock_bits=live_stock.bit_length(),actual_physical_stock_bits=physical_stock.bit_length(),inherited_bit_coarse_reserve=coarse_leaf_reserve,inherited_ordinary_leaf_reserve=ordinary_leaf_reserve),controls=controls,binary_basis_count_tests=basis.gl_count_test(),odd_denominator_grid='2^(-P)3^(-G(D+1)); no return rounding',complete_invoice=dict(scalar_max=scalar,scalar_five_invocations=scalar5,macros_max=macros,adapters=adapters,outside=outside,compiler=compiler,pervertex=pervertex,orthogonal_group=group,live_stock=live_stock,physical_stock=physical_stock,rank_mass=s,logical_groups=K,router=router,literal=literal))
