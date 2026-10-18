"""Exact moment certificate for invertibility of I-K on the E8 squared norm4 shell."""
from pathlib import Path
import sys,json
from fractions import Fraction as F
import numpy as np
PACKAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e
roots,fourth,ports,profiles=e.construct_shell();ports=ports[(profiles&4)==0,:16].astype(np.int64)
checks=[]
for name,rows,norm in [('roots',roots,2),('norm4',fourth,4)]:
 rows=rows.astype(np.int64);N=len(rows)
 for powers,wick in [([2],1),([4],3),([2,2],1),([6],15),([4,2],3),([2,2,2],1)]:
  degree=sum(powers);numerator=int(np.prod(np.stack([rows[:,i]**power for i,power in enumerate(powers)]),axis=0).sum());actual=F(numerator,2**degree)
  denominator=1
  for j in range(degree//2):denominator*=8+2*j
  expected=F(N*norm**(degree//2)*wick,denominator)
  e.require(actual==expected,'Exact spherical moment representative')
  checks.append(dict(shell=name,powers=powers,moment=str(actual)))
# Every odd-exponent moment below degree8 vanishes under even coordinate sign flips;
# coordinate permutation symmetry covers all permutations of the even patterns checked above.
lambda3=F(1080*4**3+28800*2**3,48*160)
lambdamix=F(2*30*12,16)
e.require(lambda3==39 and lambdamix==45,'Harmonic-sector eigenvalues')
C=[[F(1,60),-F(1,30)],[-F(1,30),-F(13,480)]];mass=[540,7200]
M=[[C[i][j]*mass[j]for j in range(2)]for i in range(2)]
trace=M[0][0]+M[1][1];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
e.require(trace==-186 and det==-6075,'Linear-radial sector characteristic polynomial')
N=len(ports);rank=224+560+2*16
e.require(rank==816 and 39*224+45*560+trace*16==N,'Kernel rank and exact trace')
trace2=39**2*224+45**2*560+(trace**2-2*det)*16
row_squares=[]
for index,count in [(0,2160),(2160,28800)]:
 raw=ports@ports[index];e.require(not(raw%4).any(),'Integral shell inner products');t=raw//4;num=t**3-4*t
 row_squares.append((count,F(int(num@num),48**2)))
e.require(sum(count*value for count,value in row_squares)==trace2,'Independent exact trace-of-square check using the two shell orbits')
print(json.dumps(dict(status='PASS_FULL_COMPENSATION_RANK',ports=N,real_kernel_rank=816,compensation_rank=N,
 moment_checks=checks,
 moment_symmetry_proof='Both E8 shells are closed under coordinate permutations and even coordinate sign changes. Any odd-exponent moment of degree at most6 changes sign under an even sign flip, since fewer than8 coordinates occur. The six checked even patterns therefore establish all moments needed through degree6.',
 kernel_spectrum=[dict(eigenvalue='39',multiplicity=224),dict(eigenvalue='45',multiplicity=560),dict(eigenvalue='each root of lambda^2+186*lambda-6075',multiplicity_each=16),dict(eigenvalue='0',multiplicity=N-816)],
 linear_radial_matrix=[[str(x)for x in row]for row in M],
 trace=str(N),trace_square=str(trace2),row_square_checks=[dict(multiplicity=count,row_square_sum=str(value))for count,value in row_squares],
 proof='Under the two E8 orthogonal groups, the independent degree-three feature space splits into harmonic cubics in each block (2*112), linear times traceless quadratic across blocks (2*8*35), and two radial linear copies for each block (2*2*8). The exact moments give eigenvalues39,45 and the displayed two-by-two radial matrix. None equals1 (the radial polynomial is -5888 at1). Thus I-K is invertible on every nonzero kernel eigenspace and is the identity on its30144-dimensional nullspace.',
 scoped_consequence='Any sum of scalar rank-one weighted rectangles representing I-K requires at least30960 terms. This does not lower-bound a general reusable arithmetic DAG or its number of physical helpers.'),indent=2,sort_keys=True))
