from pathlib import Path
import sys,json,hashlib,time
sys.dont_write_bytecode=True
pkg=Path(sys.argv[1]);out=Path(sys.argv[2]);sys.path.insert(0,str(pkg))
import prepare
start=time.monotonic();ctx=prepare.prepare();W=ctx['W'];C=ctx['C']
roles=ctx['regs'];gauges=[dict(role=r,dim=W.gauge[r]['dim'],frame=W.gauge[r]['frame'],basis=C.B[W.gauge[r]['frame']],annihilator=C.A[W.gauge[r]['frame']])for r in roles if r in W.gauge]
obj=dict(roles=roles,gauges=gauges,source_owned_roles=sorted(ctx['borrow']),physical_role_map=W.phys,source_alias_count=len(ctx['borrow']))
(out/'BANK-INPUTS527.json').write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
(out/'LABELS527.json').write_text(json.dumps(W.g['labels'],separators=(',',':'))+'\n')
from collections import Counter
G=Counter(z['dim']for z in gauges)
receipt=dict(status='PASS_PREPARED527_OWNERSHIP_EXPORT',physical_R=len(roles),source_aliases=len(ctx['borrow']),independent_nonzero_gauges=len(gauges),gauge_rank_histogram={str(k):v for k,v in sorted(G.items())},source_pins=ctx['portable_source_pins'],seconds=time.monotonic()-start,scope='Actual freshly prepared527context; no scalar orbank conclusion from preparation alone')
(out/'PREPARED-OWNERSHIP.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='source_pins'}))
