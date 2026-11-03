"""Check the complete scalar consumer, prefixes and failure controls."""
import ast
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import random
import statistics
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pins import authenticate, check
from rows import Sparse, packed_type, radix_bound, coefficient
from driver import replay
from run import retained, read_word

def need(ok, why):
    if not ok:
        raise ValueError(why)

def failure(call):
    try:
        call()
    except ValueError as error:
        return str(error)
    raise ValueError('A failure control was accepted')

def guards(candidate):
    """Compare the complete driver AST after the declared representation edits."""
    source = (HERE/'inputs/local.py').read_text()
    original_functions={n.name:n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
    new_functions={n.name:n for n in ast.parse(candidate).body if isinstance(n,ast.FunctionDef)}
    for name in ('need','span'):
        need(ast.dump(original_functions[name])==ast.dump(new_functions[name]),'Retained scalar helper control flow')
    source = source[source.index('def replay(w):'):source.index('\ndef reverse_columns')]
    edits = [
        ('def replay(w):', 'def replay(w, Row, observe=None):'),
        ('rows = [{r:Q(1)} for r in range(public+owned)]', 'rows = [Row.unit(r) for r in range(public+owned)]'),
        ('rows[r] = {}', 'rows[r] = Row.zero()'),
        ('rows[r] = {k:q*x for k,x in rows[r].items()}', 'rows[r] = rows[r].scale(q)'),
        ('rows[r] = {k:q*x for k,x in rows[s].items()}', 'rows[r] = rows[s].scale(q)'),
        ('add(rows[r], rows[s], q)', 'rows[r].add(rows[s], q)'),
        ('Q(e[-2])', 'coefficient(e[-2])'),
        ('abs(q)+1 < 2**16', 'n+d < (2**16)*d'),
        ('    need(not live_owned', '        if observe is not None:\n            observe(e, rows)\n    need(not live_owned')]
    for before, after in edits:
        need(before in source, 'Declared source edit exists')
        source = source.replace(before, after)
    functions = [n for n in ast.parse(candidate).body if isinstance(n, ast.FunctionDef)]
    function = next(n for n in functions if n.name == 'replay')
    need(ast.dump(function) == ast.dump(ast.parse(source).body[0]), 'Complete retained scalar control flow')
    return sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'need'
               for n in ast.walk(function))

def prefix_audit(word, reference):
    size = word['public']+word.get('owned_fields', 8)
    width, _, bound, exponent_bound = radix_bound(word)
    Packed = packed_type(width, size)
    old = [{i: Q(1)} for i in range(size)]
    packed = [Packed.unit(i) for i in range(size)]
    count, coefficient_count = 0, 0
    digest = sha256()
    def observe(event, rows):
        nonlocal count, coefficient_count
        op, r = event[:2]
        if op in ('INIT', 'CLEAR'):
            old[r], packed[r] = {}, Packed.zero()
        elif op != 'MOVE':
            q = Q(event[-2])
            if op == 'SCALE':
                old[r] = {k: q*v for k, v in old[r].items()}
                packed[r] = packed[r].scale(q)
            elif op == 'COPY':
                old[r] = {k: q*v for k, v in old[event[2]].items()}
                packed[r] = packed[event[2]].scale(q)
            else:
                reference.add(old[r], old[event[2]], q)
                packed[r].add(packed[event[2]], q)
        need(rows[r].exact() == old[r], 'All sparse prefix coefficients')
        # The independent Fraction row supplies every digit, including all zeros.
        expected = 0
        for index, value in old[r].items():
            num = value*(1 << packed[r].exponent)
            need(num.denominator == 1 and abs(num.numerator) <= bound, 'Certified packed numerator bound')
            expected += num.numerator << (width*index)
        need(packed[r].value == expected, 'All packed prefix coefficients')
        need(packed[r].exponent <= exponent_bound, 'Certified denominator bound')
        digest.update(json.dumps([r, sorted((k,str(v)) for k,v in old[r].items())],separators=(',',':')).encode())
        coefficient_count += size
        count += 1
    result = replay(word, Sparse, observe)
    need(result == reference.replay(word), 'Complete retained receipt')
    return dict(events=count, coefficient_positions=coefficient_count, prefix_sha256=digest.hexdigest(),
                radix_bits=width, numerator_bound=str(bound), denominator_exponent_bound=exponent_bound)

def controls(word, clean):
    old_events = set(map(tuple, clean['program']))
    new = [i for i,e in enumerate(word['program']) if tuple(e) not in old_events
           and 782 not in (e[1], e[2] if len(e)>3 else -1)]
    events = word['program']
    moves = [i for i in new if events[i][0] == 'MOVE']
    adds = {f:[i for i in new if events[i][0]=='ADD' and events[i][-1]==f] for f in (246,3,127)}
    out = []
    for frame in (245,127):
        bad=deepcopy(word);bad['final'][234]=frame;out.append(bad)
    for index in (moves[0], adds[246][0], adds[3][0], adds[127][-1]):
        bad=deepcopy(word);del bad['program'][index];out.append(bad)
    bad=deepcopy(word);bad['program'][adds[246][0]][3]=str(2*Q(bad['program'][adds[246][0]][3]));out.append(bad)
    inherited=len(out)
    for key,value in [('owned_fields',30),('public',766)]:
        bad=deepcopy(word);bad[key]=value;out.append(bad)
    bad=deepcopy(word);bad['initial'].pop();out.append(bad)
    bad=deepcopy(word);bad['frames'][0]=[0];out.append(bad)
    scalar=next(i for i,e in enumerate(events) if e[0]=='ADD')
    scaling=next(i for i,e in enumerate(events) if e[0]=='SCALE')
    move=next(i for i,e in enumerate(events) if e[0]=='MOVE')
    for value in ('0','1/3','65535'):
        bad=deepcopy(word);bad['program'][scalar][-2]=value;out.append(bad)
    bad=deepcopy(word);bad['program'][scaling][-2]='3';out.append(bad)
    bad=deepcopy(word);bad['program'][scalar][2]=bad['program'][scalar][1];out.append(bad)
    bad=deepcopy(word);bad['program'][scalar][0]='INVALID';out.append(bad)
    bad=deepcopy(word);bad['program'][move][-1]=not bad['program'][move][-1];out.append(bad)
    bad=deepcopy(word);bad['program'][move][2]=-1;out.append(bad)
    bad=deepcopy(word);bad['program'][0][1]=word['public']+word['owned_fields'];out.append(bad)
    return out,inherited

def arithmetic():
    rng=random.Random(34104);cases=0
    for size in (1,2,7,19):
        Packed=packed_type(128,size)
        for trial in range(80):
            a=Sparse.zero();b=Packed.zero();expected={}
            for step in range(12):
                source=rng.randrange(size);q=Q(rng.randint(-7,7),1<<rng.randrange(5))
                a.add(Sparse.unit(source),q);b.add(Packed.unit(source),q)
                expected[source]=expected.get(source,Q(0))+q
                expected={k:v for k,v in expected.items() if v}
                need(a.exact()==b.exact()==expected,'Independent small arithmetic')
                cases+=1
            q=Q(-3,8);ac=a.scale(q);bc=b.scale(q)
            ac.add(Sparse.unit(0),Q(1));bc.add(Packed.unit(0),Q(1))
            need(a.exact()==b.exact()==expected,'COPY and SCALE source isolation')
    for value in ('1','1/2','-3/8',0,1,True,Q(3,4)):
        need(coefficient(value)==Q(value),'Typed coefficient cache')
    coefficient.cache_clear()
    for i in range(257):
        need(coefficient(str(i))==Q(i),'Coefficient cache eviction')
    need(coefficient.cache_info().currsize==128,'Bounded coefficient cache')
    return cases

def benchmark_check(record, result):
    names={'driver.py','rows.py','run.py','pins.py','benchmark.py'}
    need(set(record['sources'])==names,'Benchmark source inventory')
    for name in names:
        need(sha256((HERE/name).read_bytes()).hexdigest()==record['sources'][name],'Benchmark code binding')
    encoded=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    need(sha256(encoded).hexdigest()==record['receipt_sha256'],'Benchmark scientific receipt')
    samples=record['samples']
    need(len(samples)==15,'All benchmark samples retained')
    for engine in ('fraction','sparse','packed'):
        selected=[s for s in samples if s['engine']==engine]
        need(sorted(s['cycle'] for s in selected)==list(range(5)),'Five fresh runs per engine')
        for key in ('process_seconds','replay_seconds'):
            need(all(s[key]>0 for s in selected),'Positive measured duration')
            need(statistics.median(s[key] for s in selected)==record['medians'][engine][key],'Exact recorded median')

def main():
    pins=authenticate();reference=retained();word=read_word()
    clean=json.loads(gzip.decompress((HERE/'inputs/clean-WORD.json.gz').read_bytes()))
    driver=(HERE/'driver.py').read_text();guard_count=guards(driver)
    need('control flow' in failure(lambda:guards(driver.replace("need(q and current[r] == f, 'Scalar destination and coefficient')",'pass'))),'Omitted guard control')
    audits=[prefix_audit(w,reference) for w in (word,clean)]
    for w in (word,clean):
        width,size,_,_=radix_bound(w)
        need(replay(w,packed_type(width,size))==reference.replay(w),'Packed complete receipt')
    mutants,inherited=controls(word,clean)
    packed_message_changes=0
    for bad in mutants:
        expected=failure(lambda:reference.replay(bad))
        need(failure(lambda:replay(bad,Sparse))==expected,'Sparse rejection parity')
        def packed_bad():
            width,size,_,_=radix_bound(bad)
            return replay(bad,packed_type(width,size))
        packed_message_changes += failure(packed_bad) != expected
    corruption=0
    for pin in pins:
        raw=(HERE/pin['path']).read_bytes()
        failure(lambda:check(bytes([raw[0]^1])+raw[1:],pin));corruption+=1
    small=arithmetic()
    class LostAdd(Sparse):
        def add(self, other, q):
            pass
    failure(lambda:replay(word,LostAdd))
    copied=deepcopy(word)
    first=next(i for i,e in enumerate(copied['program']) if e[0]=='INIT')
    role=copied['program'][first][1]
    target=next(i for i in range(first+1,len(copied['program']))
                if copied['program'][i][0]=='ADD' and copied['program'][i][1]==role)
    copied['program'][target][0]='COPY'
    expected=reference.replay(copied)
    need(replay(copied,Sparse)==expected,'COPY complete caller')
    width,size,_,_=radix_bound(copied)
    need(replay(copied,packed_type(width,size))==expected,'Packed COPY complete caller')
    benchmark=json.loads((HERE/'BENCHMARK.json').read_text())
    benchmark_check(benchmark,replay(word,Sparse))
    changed=deepcopy(benchmark);changed['medians']['sparse']['process_seconds']=0
    failure(lambda:benchmark_check(changed,replay(word,Sparse)))
    receipt=dict(status='PASS_P104_FORWARD_INTEGER_REPLAY',prefixes=audits,retained_guards=guard_count,
                 inherited_scalar_controls=inherited,all_scalar_controls=len(mutants),arithmetic_cases=small,
                 packed_prepass_message_changes=packed_message_changes,copy_complete_callers=1,
                 source_corruptions=corruption,scope='Complete scalar replay only; no native, compiler or kappa claim')
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    else:
        need(receipt==json.loads((HERE/'RESULT.json').read_text()),'Exact replay receipt')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':
    main()
