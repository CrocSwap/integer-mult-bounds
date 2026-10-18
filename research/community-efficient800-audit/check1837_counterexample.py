import json
from fractions import Fraction

def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
I=[[int(i==j) for j in range(3)] for i in range(3)]
R=[[1,1,0],[0,1,0],[0,0,1]]
T=[[1,0,0],[0,1,1],[0,0,1]]
Ti=[[1,0,0],[0,1,-1],[0,0,1]]
assert mul(T,R)!=mul(R,T)
assert mul(Ti,R)!=mul(R,Ti)
assert mul(Ti,T)==I
assert mul(mul(Ti,T),R)==mul(R,mul(Ti,T))==R
print(json.dumps(dict(status='PASS_COUNTEREXAMPLE',R=R,T=T,T_inverse=Ti,original=mul(mul(Ti,T),R),moved=mul(R,mul(Ti,T)),scope='Two individually noncommuting intervening touches cancel. Operator equality does not imply absence of noncommuting individual touches.')))
