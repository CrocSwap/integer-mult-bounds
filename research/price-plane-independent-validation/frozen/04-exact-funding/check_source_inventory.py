#!/usr/bin/env python3
"""Static inventory comparison only; never execute the source ledger."""
from pathlib import Path
import ast,json,hashlib
H=Path(__file__).resolve().parent
cap=H.parent/'09-capsule-cold/capsule-v1'
p=cap/'snapshot/research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
r=json.loads((H/'receipt-v1.json').read_bytes())
node=next(n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='ledger')
x={}
for n in node.body:
    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Dict):x[n.targets[0].id]=[k.value for k in n.value.keys]
strict=set(x['checks'])|{k+'_above_kappa' for k in x['margins']}
functional=set(x['functional'])|{'actual_new_BIT_stock_sublinear'}
assert strict==set(r['outer']['strict_checks'])
assert functional==set(r['outer']['functional_checks'])
a={'status':'PASS_STATIC_CURRENT_SOURCE_PREDICATE_INVENTORY','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'direct_strict_names':x['checks'],'margin_derived_strict_names':[k+'_above_kappa' for k in x['margins']],'source_functional_names':x['functional'],'typed_interface_added_functional':['actual_new_BIT_stock_sublinear'],'strict_count':len(strict),'functional_count':len(functional),'scope':'Checks key inventory. Values independently transcribed and recomputed in exact_engine.py. Same source applicability is external role03 obligation.'}
q=H/'source-inventory-v1.json'
assert not q.exists(),'immutable receipt exists'
q.write_text(json.dumps(a,indent=2,sort_keys=True)+'\n')
print(hashlib.sha256(q.read_bytes()).hexdigest())
