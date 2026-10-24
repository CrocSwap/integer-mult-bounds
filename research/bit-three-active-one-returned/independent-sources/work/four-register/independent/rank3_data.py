"""Convert the scalar catalogue and each search result to the next input."""
import argparse,hashlib,json,struct
from pathlib import Path

ROOT=Path(__file__).parent

def catalogue():
    return json.loads((ROOT/'off-pattern-spaces.json').read_text())['levels'][2]['representatives']

def families():
    return [json.loads(line) for line in (ROOT/'rank3-multisets.jsonl').read_text().splitlines()]

def outer(x,y):
    return sum(y<<(4*i) for i in range(4) if x>>i&1)

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('stage',choices=['pools','orders','binary'])
stage=parser.parse_args().stage
pools=catalogue()
if stage=='pools':
    path=ROOT/'rank3-pools.txt'
    with path.open('w') as f:
        f.write(f'{len(pools)}\n')
        for pool in pools:
            s=pool['space'];assert all(s[i]^s[j]==s[i^j] for i in range(8) for j in range(8))
            ns=pool['projectors'];f.write(f'{len(ns)}\n')
            for x,y in ns:f.write(f'{x} {y} {s.index(outer(x,y)&0x7bde)}\n')
elif stage=='orders':
    fs=families();path=ROOT/'rank3-word-input.txt'
    with path.open('w') as f:
        f.write(f'{len(fs)}\n')
        for rec in fs:
            ns=pools[rec['class']]['projectors'];f.write(f"{len(ns)} {rec['possible_ancilla']}\n")
            for (x,y),c in zip(ns,rec['counts']):f.write(f'{x} {y} {c}\n')
else:
    fs=families();path=ROOT/'rank3-words.bin';count=0
    with path.open('wb') as f,(ROOT/'rank3-parity-survivors.jsonl').open() as inp:
        for line in inp:
            rec=json.loads(line);pool=pools[fs[rec['family']]['class']]['projectors']
            f.write(struct.pack('<9H',*(outer(*pool[j]) for j in rec['order']),rec['ancilla_mask']));count+=1
    print(json.dumps({'records':count,'bytes':path.stat().st_size}))
print(json.dumps({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
