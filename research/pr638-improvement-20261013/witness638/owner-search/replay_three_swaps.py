#!/usr/bin/env python3
"""Three exact ownership exchanges. Chi Zhao with substantial Codex assistance; Apache-2.0."""
import argparse,json,gzip
from collections import defaultdict
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("literal_owner_export",HERE/"replay_owner_map.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
require,sha,validate=module.require,module.sha,module.validate
p=argparse.ArgumentParser();p.add_argument('--base-data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
s=json.loads((HERE/'SOURCE.json').read_text());data=(a.base_data/'OWNERS.json.gz').read_bytes()
require(sha(data)==s['base']['owners_sha256'],'base owner pin mismatch');require(sha((a.base_data/'PLAN.json').read_bytes())==s['base']['plan_sha256'],'base plan pin mismatch')
rows=json.loads(gzip.decompress(data));byrole={(r['time'],r['helper']):r for r in rows}
for left,right in s['swaps_time_helper']:
 x,y=byrole[tuple(left)],byrole[tuple(right)]
 for field in ['owner_replica','child','port','copy','family']:x[field],y[field]=y[field],x[field]
bins=defaultdict(list)
for r in rows:bins[r['owner_replica'],r['child'],r['port']].append(r)
for entries in bins.values():
 offset=0
 for r in sorted(entries,key=lambda r:(r['time'],r['helper'])):r['offset']=offset;offset+=r['width']
rows.sort(key=lambda r:(r['time'],r['helper']));template_bytes=(HERE/'OWNER-TEMPLATE.json').read_bytes();require(sha(template_bytes)==s['template_sha256'],'template pin mismatch');receipt=validate(rows,json.loads(template_bytes));payload=json.dumps(rows,sort_keys=True,separators=(',',':')).encode();require(sha(payload)==s['target_owners_content_sha256'],'three swaps payload mismatch')
a.out.mkdir(parents=True,exist_ok=True);packed=gzip.compress(payload,mtime=0);packed=packed[:9]+b'\xff'+packed[10:];(a.out/'OWNERS.json.gz').write_bytes(packed);receipt.update(status='PASS_THREE_EXCHANGES',owners_content_sha256=sha(payload));(a.out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
