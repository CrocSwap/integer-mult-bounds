"""Emit fixed witness objects from the bounded, already completed screen."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collections import Counter
import gzip,json,hashlib
from source_contract import ROOT,HEAD
R=ROOT
cache=json.loads(gzip.decompress((R/'response-cache.json.gz').read_bytes()));roles=cache['roles'];best=json.loads((R/'best-residue-unions.json').read_text())
for residue,label in [('0','candidate15'),('4','candidate19-residue4')]:
 selected=best[residue];entries=[]
 for group in selected['groups']:
  i,j=group['line'];basis=[int(k==i)-int(k==j)for k in range(20)]
  for row in group['relations']:
   p=row['pivot'];ds=row['donors']
   entries.append(dict(virtual_pivot=p,virtual_donors=ds,pivot=roles[str(p)]['stream'],donors=[roles[str(d)]['stream']for d in ds],rank=1,basis=[basis],cut_read=cache['last_plain_read']['scalar'],line=[i,j]))
 assert len(entries)==selected['pivots']
 out=dict(source_head=HEAD,selection=label,pivots=len(entries),entries=entries,local_histogram_delta=selected['local_histogram_delta'],residual_family_delta={20:-len(entries),19:len(entries)},distinct_donors=selected['donors'],scalar_setup_pairs=selected['setup_pairs'],physical_members=selected['members'],rank_residue_mod5=int(residue),source_cache_sha256=hashlib.sha256((R/'response-cache.json.gz').read_bytes()).hexdigest(),physical_admission=False,scope='Exact shared response witness only. Candidate15 has a divisible rank census; candidate19 requires a separately admitted residual-rank correction before bank/pricing admission. Both require full frame/alias/scalar/chart/finite checks.')
 raw=(json.dumps(out,indent=2)+'\n').encode();(R/(label+'.json')).write_bytes(raw);print(label,len(entries),hashlib.sha256(raw).hexdigest())
