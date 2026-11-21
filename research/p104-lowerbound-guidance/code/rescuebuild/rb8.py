from rb1 import *
C1m=[(F({1,2}),[]),(F({1,2}),[]),(F({0,1,2}),[F({1,2})]),(F({0,1,2}),[F({1}),F({2})])]
C1mm=[(F({1,2}),[]),(F({1,2}),[]),(F({0,1,2}),[F({1,2})]),(F({0,1,2}),[F({1,2})])]
for nm,d in [('C1 one 2-piece',C1m),('C1 two 2-pieces',C1mm)]:
    out=run(nm,3,d,seeds=3,tries=10)
    for nr,S,z in out:
        if nr<1e-9:print('   ',S.diag(z)['eff'],S.diag(z)['own']);break
