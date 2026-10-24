#!/usr/bin/env python3
"""Fresh directed rational audit of independent, literal-censused invoice."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1]).resolve().parent))
from exact_engine import evaluate,need
invoice=json.loads(Path(sys.argv[2]).read_bytes());receipt=json.loads(Path(sys.argv[3]).read_bytes())
fresh=evaluate(invoice['histograms']['productive'],invoice['histograms']['paid'],receipt['config'])
for k,v in fresh.items():
 if k not in ('seconds','status','external_gate_requirements'):need(v==receipt[k],'independent exact result changed '+k)
print(json.dumps(fresh,sort_keys=True))
