# SPDX-License-Identifier: Apache-2.0
"""Compare fixed 17-call invoices with #7644's independent directed engines."""
import importlib.util,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent; spec=importlib.util.spec_from_file_location('independent',D/'source7644/independent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def h(path):
 d=json.loads(path.read_text());p={int(k):v for k,v in d['paid'].items()};t={int(k):v for k,v in d['targets'].items()};return {r:t.get(r,0)-p.get(r,0) for r in p.keys()|t.keys()}
a=h(D/'source7644/data/invoice.json');b=h(D/'candidate-invoice.json');x=m.crossing(a);y=m.crossing(b)
r={'source_bracket':[str(v) for v in x],'candidate_bracket':[str(v) for v in y],'strict_lower_gain':str(y[0]-x[1]),'method':'#7644 decimal directed bisection, independently checked by dyadic integer-root signs','invoice_sha256':hashlib.sha256((D/'candidate-invoice.json').read_bytes()).hexdigest()};(D/'PRICE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
