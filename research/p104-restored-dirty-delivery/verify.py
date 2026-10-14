"""Read-only portable exact local replay; no full supplier claim."""
from pathlib import Path
import importlib.util,json,hashlib
P=Path(__file__).resolve().parent
def require(c,msg):
 if not c:raise ValueError(msg)
def load(name,file):
 s=importlib.util.spec_from_file_location(name,P/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pins=json.loads((P/'UPSTREAM.json').read_text())
for path,row in pins['inputs'].items():
 require(hashlib.sha256((P/'source'/path).read_bytes()).hexdigest()==row['sha256'],'source changed: '+path)
producer=load('dirty_producer','dirty_delivery.py')
w=producer.build();require(json.loads(json.dumps(w))==json.loads((P/'DIRTY-WITNESS.json').read_text()),'witness mismatch')
r=producer.run();require(json.loads(json.dumps(r))==json.loads((P/'DIRTY-RESULT.json').read_text()),'receipt mismatch')
ind=load('free_charts','operator_verify.py');ind.main()
print('PASS_P104_RESTORED_DIRTY_DELIVERY columns=144 carriers=32 width=9 COPY=56 controls=9 no_new_kappa')
