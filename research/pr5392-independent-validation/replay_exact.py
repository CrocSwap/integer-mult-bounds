#!/usr/bin/env python3
"""Fresh exact funding with source AST and current predicate inventory binding."""
from pathlib import Path
import json,sys
h=Path(sys.argv[1]).resolve();sys.path.insert(0,str(h))
from exact_engine import evaluate,need
import funding,invoice
r=invoice.read(h/'FUNDING-v2.json');inv=invoice.read(h/'INVOICE-v1.json')
need(funding.parameters()==r['source']['typed_constants'],'exact candidate AST constants changed')
source=funding.source_inventory();expected=dict(r['source_predicate_inventory'])
need(source.pop('path').startswith(str(h)),'local canonical predicate fixture')
expected.pop('path');need(source==expected,'complete source predicate inventory changed')
fresh=evaluate(inv['histograms']['productive'],inv['histograms']['paid'],r['config'])
for k,v in fresh.items():
 if k not in ('status','seconds','external_gate_requirements'):need(v==r[k],'complete exact result differs '+k)
need(set(fresh['outer']['strict_checks'])==set(source['strict_keys']) and set(fresh['outer']['functional_checks'])==set(source['functional_keys']),'uncovered predicate inventory')
# Invalid domains fail before enclosure work; the exact engine also runs its
# root, derivative/away, reserve, tail, compiler and outer semantic controls.
controls={}
for name,patch in [('unsupported_model',{'model':'unsupported-transpose'}),('unsupported_cutoff',{'tuple':dict(r['config']['tuple'],cutoff=22)})]:
 try:evaluate(inv['histograms']['productive'],inv['histograms']['paid'],dict(r['config'],**patch))
 except ValueError as e:controls[name]=str(e)
 else:raise ValueError('unsupported source domain accepted '+name)
print(json.dumps(dict(status='PASS_COMPLETE_EXACT_SOURCE_BOUND_FUNDING',result=fresh,source_predicate_inventory=source,domain_controls=controls),sort_keys=True))
