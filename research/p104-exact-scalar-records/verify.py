"""Check every scalar record and the complete absolute-error interface.

Credit Adam Gall's signed native-defect method and the retained P104 sources.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import random
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


records = load('records',P/'records.py')
need = records.require


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def source():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source hash')
    return json.loads(gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))


def update(rows,e):
    op,r = e[:2]
    if op in ('INIT','CLEAR'):
        rows[r] = {}
    elif op != 'MOVE':
        q = Q(e[-2])
        if op == 'COPY':rows[r] = {k:q*v for k,v in rows[e[2]].items()}
        elif op == 'SCALE':rows[r] = {k:q*v for k,v in rows[r].items()}
        else:
            for k,v in rows[e[2]].items():
                z = rows[r].get(k,Q(0))+q*v
                if z:rows[r][k] = z
                else:rows[r].pop(k,None)


def certify(word):
    n = word['public']+word['owned_fields'];scale = 32
    grid = [{i:Q(1)} if i<word['public'] else {} for i in range(n)]
    error = [row.copy() for row in grid]
    integer = [{i:scale} if i<word['public'] else {} for i in range(n)]
    atom = n;peak = Q(1);hist = Counter();witness = None;digest = sha256()
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':
            grid[r] = {atom:Q(1)};integer[r] = {atom:scale};error[r][atom] = Q(1);atom += 1
        else:
            update(grid,e);update(error,e)
            if op in ('INIT','CLEAR'):integer[r] = {}
            else:
                q = Q(e[-2]);s = r if op == 'SCALE' else e[2]
                term = {k:records.quotient(q.numerator*v,q.denominator) for k,v in integer[s].items()}
                if op in ('SCALE','COPY'):integer[r] = term
                else:
                    for k,v in term.items():
                        z = integer[r].get(k,0)+v
                        if z:integer[r][k] = z
                        else:integer[r].pop(k,None)
        need({k:Q(v,scale) for k,v in integer[r].items()} == grid[r], 'independent integer row')
        degree = max((v.denominator.bit_length()-1 for v in grid[r].values()),default=0)
        hist[degree] += 1
        if degree == 5 and witness is None:
            k = next(k for k,v in grid[r].items() if v.denominator == 32)
            witness = dict(event=j,role=r,atom=k,value=str(grid[r][k]))
        peak = max(peak,sum(map(abs,error[r].values())))
        digest.update(canonical([j,r,sorted((k,str(v)) for k,v in grid[r].items()),sorted((k,str(v)) for k,v in error[r].items())]))
    final = max(sum(map(abs,row.values())) for row in error[:word['public']])
    need(witness is not None and max(hist) == 5, 'sharp free-return grid')
    need(final == Q(1323,2) and peak == 2764, 'complete native and entrance error')
    return dict(grid_bits=5,grid_histogram=dict(hist),grid_witness=witness,
                error_final=str(final),error_prefix=str(peak),guard_bits=10,
                final_error_rows=[str(sum(map(abs,row.values()))) for row in error],
                prefix_digest=digest.hexdigest(),native_returns=atom-n)


def trace(word, initial, native_values):
    values = list(map(Q,initial))+[Q(0)]*word['owned_fields']
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':values[r] = Q(native_values[j])
        elif op in ('INIT','CLEAR'):values[r] = Q(0)
        else:
            q = Q(e[-2])
            if op == 'SCALE':values[r] *= q
            elif op == 'COPY':values[r] = q*values[e[2]]
            else:values[r] += q*values[e[2]]
        yield j,r,values[r]


def rejects(fn):
    try:fn()
    except ValueError:return 1
    raise ValueError('negative control accepted')


def verify():
    word = source();result = certify(word)
    local = load('local',ROOT/'research/p104-unread-path-resynthesis/local.py')
    result['bill'] = local.replay(word)
    tr = load('transfer',ROOT/'research/p104-gauge-error-covariance/transfer.py')
    _,ideal = tr.ideal(word,set())
    sites = {j for j,e in enumerate(word['program']) if e[0] == 'MOVE'}
    reverse,_ = tr.transpose(word,[(Q(0),Q(0))]*len(word['program']),sites)
    expected = [row[2]+(1+int(r-112 in word['live']) if r<word['public'] else 0)
                for r,row in enumerate(reverse)]
    need(list(map(Q,result['final_error_rows'])) == expected, 'all independent error transpose rows')
    need(ideal == 850 and ideal+Q(result['error_prefix'])/1024 < 1024, 'ten range bits')
    result['ideal_peak'] = str(ideal)
    rng = random.Random(6030);checks = 0
    for _ in range(12):
        initial = [rng.randrange(-4096,4097) for _ in range(word['public'])]
        returns = {j:rng.randrange(-4096,4097) for j,e in enumerate(word['program']) if e[0] == 'MOVE'}
        for a,b in zip(records.run(word,initial,lambda j,r,v,s:returns[j]),trace(word,initial,returns),strict=True):
            need(a[:2] == b[:2] and Q(a[2],32) == b[2], 'complete integer execution')
            checks += 1
    witness = result['grid_witness'];initial = [int(i == witness['atom']) for i in range(word['public'])]
    atoms = {j:word['public']+word['owned_fields']+k for k,j in enumerate(j for j,e in enumerate(word['program']) if e[0] == 'MOVE')}
    returns = {j:int(a == witness['atom']) for j,a in atoms.items()}
    values = list(trace(word,initial,returns));value = values[witness['event']][2]
    need(value == Q(witness['value']) and (16*value).denominator != 1, 'attaining free-return witness')
    controls = rejects(lambda:list(records.run(word,initial,lambda j,r,v,s:returns[j],grid=4)))
    controls += rejects(lambda:list(records.run(word,initial,lambda j,r,v,s:Q(1,2))))
    controls += rejects(lambda:list(records.run(word,[True]*word['public'],lambda *args:0)))
    toy = dict(public=2,owned_fields=0,program=[['ADD',0,1,'1/3',0]])
    controls += rejects(lambda:list(records.run(toy,[0,1],lambda *args:0)))
    result.update(status='PASS_P104_EXACT_SCALAR_RECORDS',integer_trace_events=checks,
                  negative_controls=controls,witness_value=str(value),
                  component_record_bits='p+16',component_temporary_bits='p+21',
                  coarse_precision='p=t+10+floor(n/2), complex dimension 2^n')
    return result


if __name__ == '__main__':
    need(sys.argv[1:] in ([],['--write']), 'supported arguments')
    result = verify()
    if sys.argv[1:] == ['--write']:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(result) == canonical(json.loads((P/'RESULT.json').read_text())), 'complete receipt')
    print(result['status'])
