"""Check the frozen chain edit against the public #7786 graph, exactly."""
import argparse, gzip, hashlib, json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = 'c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb'
CANDIDATE = '320847d42f2655c3cc0fd29fe670ae77277e9c2f377c1c92f33d7df050872f54'
READERS = {97129:2, 97135:3, 103327:2, 104203:-2, 104416:-4, 104438:2, 104446:2, 155676:-1, 156022:-4}

def load(path, expected):
    obj = json.loads(gzip.decompress(path.read_bytes()))
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('canonical graph hash mismatch: ' + str(path))
    return obj

def add(out, row, factor):
    for k, v in row.items():
        new = out.get(k, Q(0)) + factor * v
        if new: out[k] = new
        else: out.pop(k, None)

def main(source):
    a, b = load(source, SOURCE), load(HERE/'CANDIDATE.json.gz', CANDIDATE)
    for k in a:
        if k not in ('forms', 'moves', 'schedule') and a[k] != b[k]:
            raise ValueError('changed graph field ' + k)
    am = {i:(x,y) for i,x,y in a['moves']}; bm = {i:(x,y) for i,x,y in b['moves']}
    if set(am)-set(bm) != {94318} or set(bm)-set(am) or any(bm[i] != ((2,306) if i == 87 else am[i]) for i in bm):
        raise ValueError('unexpected movement delta')
    if [i for i in a['schedule'] if i != 94318] != b['schedule']: raise ValueError('schedule delta')
    forms = lambda graph: {i:{k:Q(v) for k,v in row if Q(v)} for i,row in graph['forms']}
    af,bf = forms(a),forms(b)
    if set(af)-set(bf) != {94318} or set(bf)-set(af) or bf[87] != {-1255:Q(-1,4)}: raise ValueError('form delta')
    if [i for i in af if 94318 in af[i]] != [87] or {i for i in af if 87 in af[i]} != set(READERS): raise ValueError('reader roster')
    for i in set(af)&set(bf)-{87}:
        expected = af[i].copy(); n=READERS.get(i,0)
        if n:
            if expected[87] != n: raise ValueError('reader coefficient')
            add(expected,{94028:Q(-1,4),90122:Q(-2)},Q(n))
        if expected != bf[i]: raise ValueError('unexpected form change: '+str(i))
    # Independently propagate source rows on every arbitrary input coordinate.
    positions={i:n for n,i in enumerate(a['schedule'])}
    needs={87, 94028, 90122}
    for i in reversed(a['schedule']):
        if i in needs: needs.update(k for k in af[i] if k >= 0)
    values={~i:{i:Q(1)} for i in range(len(a['initial']))}
    for i in a['schedule']:
        if i in needs:
            row={}
            for k,c in af[i].items(): add(row,values[k],c)
            values[i]=row
    identity={}; add(identity,values[-1255],Q(-1,4)); add(identity,values[94028],Q(-1,4)); add(identity,values[90122],Q(-2))
    if identity != values[87]: raise ValueError('source stock identity failed')
    for i in READERS:
        if not (positions[94028] < positions[i] and positions[90122] < positions[i] and positions[87] < positions[i]): raise ValueError('noncausal reader')
    print('PASS_EXACT_CHAIN_DELTA_AND_STOCK_IDENTITY', CANDIDATE)

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--source-word',type=Path,required=True); main(p.parse_args().source_word)
