import ast,subprocess,types,sys,json
from pathlib import Path
R=Path('/tmp/integer-mult-efficient600-20261014');F=Path('/tmp/pr-efficient800/sources/1752');sys.path.insert(0,str(F/'scripts'))
import experiments.single_intersection as new
old_src=subprocess.check_output(['git','show','66849e14:scripts/experiments/single_intersection.py'],cwd=R,text=True)
new_src=(F/'scripts/experiments/single_intersection.py').read_text()
def fn(src,name):return ast.dump(next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
assert fn(old_src,'spectral_parity_bound')==fn(new_src,'spectral_parity_bound')
old=types.ModuleType('old');exec(compile(old_src,'pinned_old','exec'),old.__dict__)
from itertools import combinations
cases=[(h,k,j) for h in range(4,11) for k in range(2,min(4,h//2)+1) for j in range(k)]
for h,k,j in cases:
 labels=[sum(1<<x for x in comb) for comb in combinations(range(h),k)]
 assert old.minor_rows(labels,j)==new.minor_rows(labels,j),(h,k,j)
print('PASS unchanged spectral function; all',len(cases),'minor row lists identical')
