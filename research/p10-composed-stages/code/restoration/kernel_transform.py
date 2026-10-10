"""F2 replay retained from kernel_transform.py (PR268 / gen4 multi-donor lineage, prepared with Anthropic Claude assistance). Portable extraction by OpenAI Codex; Apache-2.0."""
from collections import Counter
import json,hashlib
if not __debug__:raise SystemExit("assertions required")
def replay(records,n,v,reverse=False,omit_category=None):
    columns=[1<<i for i in range(n+1)];wanted=[1<<i for i in range(n)];norm=[1]*(n+1);largest=1;temporary=None;count=0;coeff=Counter();digest=hashlib.sha256()
    for t in range(v):wanted[v+t]^=1<<t
    for k in(range(len(records)-6,-1,-6)if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            if z==omit_category:continue
            assert c%2 and (b!=n or temporary is not None)
            columns[a]^=columns[b];norm[a]+=abs(c)*norm[b];largest=max(largest,norm[a]);count+=1;coeff[abs(c)]+=1
            digest.update(json.dumps([a,temporary if b==n else b,-c if reverse else c],separators=(',',':')).encode());digest.update(b'\n')
        elif op==(3 if reverse else 2):
            assert temporary is None and b==n;temporary=a;columns[b]=columns[a];norm[b]=norm[a]
        elif op==(2 if reverse else 3):
            assert temporary==a and b==n and columns[a]==columns[b];temporary=None
    assert temporary is None
    wrong=[i for i in range(n)if columns[i]!=wanted[i]]
    if omit_category is None:assert not wrong,('kernel scalar failure',reverse,wrong[:20])
    else:assert wrong,'vacuous kernel omitted-gate control'
    return dict(reverse=reverse,formal_columns=n,wrong_rows=len(wrong),all_sources_and_dirty_restored=not wrong,scalar_additions=count,coefficient_counts=dict(coeff),event_sha256=digest.hexdigest(),max_intermediate_row_l1=largest)

