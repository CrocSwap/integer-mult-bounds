"""Fractional depth row bound: nine rank64 steps in dimension89 shrink by 16.
The inherited reserve contract charges stock bits once per actual recursion
level, plus the retained old-leaf and conversion slopes 9909+252.
Chafreaky with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q

def bound(stock_bits,minimum_log2=32):
 assert stock_bits==3929
 assert 89**9>16*64**9
 slope=Q(9,4)*stock_bits+9909+252;additive=9*stock_bits
 gap=Q(20161)-slope
 assert gap>0 and gap*minimum_log2>additive
 # e < 2^minimum_log2 uses the retained small-leaf supplier; this cutoff is
 # far below the already retained finite semantic guard 2^210000.
 assert 0<minimum_log2<210000
 assert 89**2<=2*64**2 and 89**3>2*64**3
 return dict(status='PASS_FRACTIONAL_DEPTH_ROW_RESERVE',block_steps=9,block_halvings=4,
  exact_shrink_inequality=[89**9,16*64**9],stock_bits=stock_bits,row_slope=str(slope),
  additive_stock_charge=additive,minimum_log2_width=minimum_log2,retained_row_coefficient=20161,
  threshold_margin=str(gap*minimum_log2-additive),coarse_three_level_row=3*stock_bits+9909+252,
  finite_three_level_halving=[89**3,2*64**3])

def controls():
 rejected=[]
 assert 3*3929+9909+252>20161;rejected.append('coarse three-level row exceeds reserve')
 assert 89**9<=32*64**9;rejected.append('nine steps do not guarantee five halvings')
 try:bound(3929,30)
 except AssertionError:rejected.append('insufficient row cutoff')
 else:raise AssertionError('accepted insufficient row cutoff')
 return rejected
