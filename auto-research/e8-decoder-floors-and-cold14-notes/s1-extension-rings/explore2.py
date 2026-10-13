import sys, numpy as np
sys.path.insert(0,'/Users/joelpulikkan/imb-main/research/format-limits/scripts')
exec(open(sys.argv[0].replace('explore2','explore1')).read().split('from minrank_sat')[0])
from e8units import f2_rank
B0=(~nonorth).astype(int); 
print('rank of [orth or diag] matrix', f2_rank(B0))
from collections import Counter
Hv=Counter((int(a),int(b)) for a,b in zip(R.flatten(),I.flatten()))
print(Hv)
