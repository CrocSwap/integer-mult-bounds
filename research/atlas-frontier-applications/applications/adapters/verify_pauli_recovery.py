#!/usr/bin/env python3
"""Independent literal measurement-manifest endpoint validator (no repair import)."""
import argparse,copy,csv,hashlib,itertools,json
from pathlib import Path

def validate(folder):
 manifest=json.loads((folder/'MANIFEST.json').read_text())
 for name,digest in manifest.items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
 inp=json.loads((folder/'INPUT.json').read_text());out=json.loads((folder/'RECOVERY.json').read_text());full=json.loads((folder/'FULL-MEASUREMENT.json').read_text())
 n=inp['qubits'];assert n==full['qubits']==out['qubits'];D=1<<n;mask=D-1
 def commute(a,b):return (((a&mask)&(b>>n)).bit_count()+((b&mask)&(a>>n)).bit_count())%2==0
 def products(g):
  # P(v)=i^popcount(x&z) X^x Z^z. Track actual fourth-root phases.
  words={0:0}
  for v in g:
   x=v&mask;z=v>>n;pv=(x&z).bit_count()%4
   extra={}
   for u,pu in words.items():
    c=u^v;phase=(pu+pv+2*((u>>n)&x).bit_count())%4
    assert c not in words and c not in extra,'dependent literal Pauli products'
    extra[c]=phase
   words.update(extra)
  assert len(words)==D and words[0]==0
  for v,phase in words.items():assert (phase-((v&mask)&(v>>n)).bit_count())%2==0,'non-Hermitian subgroup product'
  return set(words)-{0}
 fullsets=[];seen=set()
 for g in full['classes']:
  assert len(g)==n and all(0<v<D*D for v in g)
  assert all(commute(a,b)for a,b in itertools.combinations(g,2))
  s=products(g);assert not seen&s;seen|=s;fullsets.append(s)
 assert len(fullsets)==D+1 and seen==set(range(1,D*D))
 partialsets=[products(g)for g in inp['classes']];assert len(partialsets)==D
 missing=products(out['missing_generators']);assert missing==set(out['missing_labels'])
 used=set.union(*partialsets);assert len(used)==D*(D-1) and missing==seen-used
 assert all(s in fullsets for s in partialsets)and missing in fullsets
 rows=list(csv.DictReader((folder/'PAULI-PARTITION.csv').open(newline='')));assert len(rows)==D*D-1
 for row in rows:
  k,v=int(row['class']),int(row['label']);assert v in fullsets[k]
  x=v&mask;z=v>>n;name=''.join('Y'if x>>i&1 and z>>i&1 else'X'if x>>i&1 else'Z'if z>>i&1 else'I'for i in range(n));assert row['pauli']==name
 assert len({int(row['label'])for row in rows})==D*D-1
 # Character projectors have trace D/D=1. Distinct classes have no common
 # nonidentity labels, so trace(P_b P_c)=D/D^2=1/D exactly.
 return dict(status='PASS_INDEPENDENT_LITERAL_PAULI_RECOVERY',qubits=n,dimension=D,classes=D+1,rank_one_projector_recipes=D*(D+1),nonidentity_paulis=D*D-1,projector_trace='1',cross_basis_overlap=f'1/{D}',source_manifest_sha256=hashlib.sha256((folder/'MANIFEST.json').read_bytes()).hexdigest())
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);a=ap.parse_args();print(json.dumps(validate(a.folder),indent=2))
