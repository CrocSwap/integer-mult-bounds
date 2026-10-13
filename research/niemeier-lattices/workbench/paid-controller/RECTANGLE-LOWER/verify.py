from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from portable import PACKAGE, output_path, source_name
"""Scoped independent-rectangle carrier lower bound, with exact moment signs."""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import importlib.util,hashlib,json
SOURCE=PACKAGE / 'code/costs.py'
s=importlib.util.spec_from_file_location('cost_bounds',SOURCE);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)


def moment_obstruction(N,C,R):
 h=16;minimum_m=3*(h-1)+1;a=c.FRONTIER/(1-c.FRONTIER)
 lo,hi=c.power_bounds(F(minimum_m,h),a)
 lower=h*R*(lo-1);upper=h*R*(hi-1)
 c.require(lower>N-C,'Independent ordinary helpers alone exclude every odd stage')
 # All-stage ceiling obtained by discarding all other paid pressure and
 # the negative -N/L term in D/L. This is deliberately a weak bound.
 nl,nh=c.logarithm(1+F(N-C,h*R));dl,dh=c.logarithm(F(minimum_m,h))
 al,ah=nl/dh,nh/dl
 return dict(N=N,C=C,ordinary_helpers_lower_bound=R,
  minimum_odd_stage=3,minimum_ambient_dimension=minimum_m,
  normalized_helper_pressure_interval_scaled_1e12=c.scaled(lower,upper,10**12),
  normalized_deficit_strict_upper_bound=N-C,
  all_stage_kappa_upper_bound_interval_scaled_1e18=c.scaled(al/(1+al),ah/(1+ah)),
  verdict='FAILS_FRONTIER_FOR_ALL_ODD_STAGES')


def run():
 rows=[]
 for k in range(1,16):
  A,B=2**(k-1),2**(15-k)
  rows.append(dict(source_span_dimension=k,target_span_dimension_upper_bound=16-k,
                   source_size_upper_bound=A,target_size_upper_bound=B,
                   edges_per_helper_upper_bound=str(F(A*B,A+B-1))))
 maximum=max(F(row['edges_per_helper_upper_bound']) for row in rows)
 c.require(maximum==F(16384,255),'Exact maximum rectangle efficiency')
 c.require([r['source_span_dimension'] for r in rows if F(r['edges_per_helper_upper_bound'])==maximum]==[8],
           'Unique dimensional maximum')
 vertices=2**14;degree=comb(16,8)//2;edges=vertices*degree
 required=F(edges)/maximum
 c.require(required.denominator==1 and required==1640925,'Integral helper lower bound')
 R=int(required)
 cases={name:moment_obstruction(N,C,R) for name,N,C in
        [('full_shell_bit',30960,13040),('spinor_bit',16384,9216),('full_shell_even_without_centers',30960,0)]}
 try:moment_obstruction(30960,13040,1)
 except ValueError as error:c.require('helpers alone' in str(error),'Control fails at the intended check')
 else:raise ValueError('One-helper negative control unexpectedly rejected')
 return dict(status='PASS_SCOPED_RECTANGLE_CARRIER_OBSTRUCTION',vertices=vertices,
  ordered_degree=degree,ordered_edges=edges,rectangle_rows=rows,
  maximum_edges_per_helper=str(maximum),ordinary_helpers_lower_bound=R,
  moment_cases=cases,frontier=str(c.FRONTIER),
  source=dict(path=source_name(SOURCE),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
  scope=['Each rectangle has mutually orthogonal source and target spans.',
         'Each independent addition-tree/output-carrier rectangle is charged a+b-1 roles.',
         'No carrier or DAG role is shared between rectangles; no free multi-target output-carrier reuse is assumed.',
         'Each ordinary helper starts at zero and ends at the full h=16 frame.',
         'Paid local children stay within one helper role, rank at most16; no cross-role child fusion.',
         'Partial or virtual endpoints, fused transforms and alternate scalar factorizations are outside this bound.'],
  negative_control='A single helper does not satisfy the same sufficient obstruction test.')

if __name__=='__main__':
 out=run();output_path('paid-controller/RECTANGLE-LOWER/RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(out['status'],out['ordinary_helpers_lower_bound'])
 for name,row in out['moment_cases'].items():print(name,row['all_stage_kappa_upper_bound_interval_scaled_1e18'])
