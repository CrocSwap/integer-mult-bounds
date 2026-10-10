"""Exact subsets of the unchanged published166 witness; no duplicate bundles."""
import hashlib,json
from source_data import ROOT,OUTPUT

def selection():
    return json.loads((ROOT/'selection.json').read_text())
def case(label):return selection()['cases'][str(label)]
def render(label):
    plan=selection();row=plan['cases'][str(label)]
    raw=(ROOT.parent/plan['predecessor_witness']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==plan['predecessor_sha256']
    predecessor=json.loads(raw)['entries'];indices=row['entry_indices']
    assert len(indices)==len(set(indices))==row['metadata']['pivots']
    assert all(type(i)is int and 0<=i<len(predecessor)for i in indices)
    out={}
    for k,v in row['metadata'].items():
        out[k]=v
        if k=='pivots':out['entries']=[predecessor[i]for i in indices]
    raw=(json.dumps(out,indent=2)+'\n').encode()
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
    return raw

def write_case(label):
    OUTPUT.mkdir(parents=True,exist_ok=True);row=case(label);path=OUTPUT/row['file']
    path.write_bytes(render(label));return path
if __name__=='__main__':
    for label in ('154','156'):print(write_case(label))
