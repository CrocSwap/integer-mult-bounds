from pathlib import Path
from collections import Counter
import sys,json,hashlib
r=Path.cwd();out=r/'nested-basis-exchange-pricing';assert not out.exists();out.mkdir();sys.path.insert(0,str(r/'source454-review/e8-r740-replica32/code'));import e8core as E
ledger=json.loads((r/'r715-nested-basis-exchanges/LEDGER.json').read_text());seen={};records=[];L=None
for row in ledger:
 tag=row['tag'];digest=row['word_sha256']
 if digest in seen:records.append(dict(tag=tag,status='IDENTICAL_WORD_REUSES_EXACT_PRICE',same_as=seen[digest]));continue
 seen[digest]=tag;w=json.loads((r/'r715-nested-basis-exchanges'/tag/'WORD.json').read_text());L=L or E.Lat(w['lines']);m=E.to_masks(w,L);a=E.replay(w,L=L,masks=m,span_mode='z');assert not a['viol'];local=out/(tag+'-LOCAL.json');local.write_text(json.dumps(dict(profile=dict(a['H']),widths=[8-L.dim(m[f]) for f in w['start'][240:]]),indent=2)+'\n')
 s=(r/'search_r715_rational_hosting.py').read_text().replace("out=r/'r715-rational-hosting-fixed'","out=r/'nested-basis-exchange-pricing/"+tag+"'").replace('r715-factored-replica-screen/WORD/LOCAL.json',local.relative_to(r).as_posix()).replace('r715-factor-replica64-strong-RESULT.json','response-replica28-strong-RESULT.json');exec(compile(s,'PR485-exact-pricing','exec'),{})
 price=json.loads((r/'nested-basis-exchange-pricing'/tag/'RESULT.json').read_text());records.append(dict(tag=tag,status=price['status'],replicas=price['replicas'],projected_kappa=price['projected_kappa'],bit_lower=price['bit_lower']))
(r/'nested-basis-exchange-pricing/COMPLETE.json').write_text(json.dumps(dict(status='FINISHED',cases=records),indent=2)+'\n')
