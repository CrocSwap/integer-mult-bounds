"""Producer adapter: PR117's replayed h=24 complex DAG for the PR110/PR114/PR116 deferral compiler.

replayed.py and complex-dag.json.gz are copied unchanged from PR117 (eumemic, Apache-2.0,
scripts/deferred_product/replayed.py and certificates/deferred-product-complex-dag.json.gz).
replayed.build recomputes every support, label, rank, root identity, the /21 decoder and
scatter identity, frame nesting and nondegeneracy from the operand pairs. Pair-star roots are
listed in ascending i order, hence ORDER below. Adapter by Rohan Arun with Anthropic Claude assistance.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
_s=importlib.util.spec_from_file_location('replayed117',HERE/'replayed.py');_m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
ORDER=lambda i,a,b:(i,)
def build(h,prefix,central_disjoint=24,base=2):
    assert (h,central_disjoint)==(24,24)
    return _m.build(HERE/'complex-dag.json.gz',prefix)
