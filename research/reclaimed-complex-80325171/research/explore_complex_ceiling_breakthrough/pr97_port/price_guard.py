"""Original conservative scalar/precision/row ledger from the emitted h24 word."""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Optimized Python is not permitted')
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import json
p=Path(__file__).resolve().parent;s=json.loads((p/'H24_WITNESS_STATS.json').read_text());v=2024;h=24;m=576;N=v*v;R=s['profile']['R'];W=s['profile']['W'];mass=s['profile']['mass']
assert s['max_scalar_numerator']==s['max_scalar_denominator']==1
Jside=20240;Jcenter=4*comb(23,3)+22*comb(23,2);J=Jside+Jcenter
L=s['literal_mixer_scalar_gate_upper'];V=s['events']['inject']
local=4*L+2*V+2*J+8*h+4*R
G=2*v*local+4*N
E=64*(W+m+G+1)**3;literal=2*G*W**2+8*mass+4*W+4+32*m;assert literal<E
B=mass+E;C0=32*m*B**2;assert 2*B*(m-552)>=mass+E
least=lambda mm,rr:next(t for t in range(1,1000)if mm**t>2*rr**t)
tc=least(m,552);tb=least(529,527);wb=(108516254).bit_length();wc=W.bit_length();rows=tb*wb+tc*wc;gap=Q(12000)-Q(51,25)*rows;assert gap>0
out=dict(status='Author conservative finite guard arithmetic from emitted h24 witness; physical and all-size admission remain separate',local_mixer_scalar_upper=L,source_injection_incidence=V,side_scatter_incidence=Jside,center_scatter_incidence=Jcenter,local_weighted_word_and_copy_scan_upper=local,global_scalar_group_upper=G,scalar_max_abs='19/2',scalar_denominator_max=2,E=E,literal_charge=literal,semantic_B=B,C0=C0,C1=1,complex_halving_degree=tc,complex_wire_bits=wc,bit_halving_degree=tb,bit_wire_bits=wb,row_coefficient=rows,row_degree=12000,row_gap=str(gap),suffix_slope=48000,assembly='Current bit saving31987/500000000 stays binding; no assembled-kappa improvement follows from this component alone')
(p/'PRECISION_AND_ROWS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in('E','literal_charge','semantic_B','C0')},indent=2))
