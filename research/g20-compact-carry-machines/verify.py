"""Check the complete transition and minimal quotient-machine certificates.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import gzip
import importlib.util
import json
from pathlib import Path
import random
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
spec = importlib.util.spec_from_file_location('machines',P/'machines.py')
m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
need = m.require


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def source():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],'source hash')
    return json.loads((ROOT/'research/g20-fused-qadic-carries/inputs/source-RESULT.json').read_text())


def partition(keys,labels):
    forward = {};backward = {}
    need(len(keys) == len(labels),'partition length')
    for key,label in zip(keys,labels):
        need(type(label) is int and label >= 0,'partition label')
        if key in forward:need(forward[key] == label,'equal observations stay together')
        if label in backward:need(backward[label] == key,'distinct observations stay apart')
        forward[key] = label;backward[label] = key
    need(set(backward) == set(range(len(backward))),'contiguous classes')


def check_machine(c):
    lo,hi,digits = c['model'];thresholds = list(range(lo+1,hi+1))
    alphabet = [[s,b] for s in digits for b in (0,1)]
    need(c['alphabet'] == alphabet,'complete aggregate alphabet')
    states = [tuple(s) for s in c['states']];edges = c['edges'];outputs = c['output']
    need(states[0] == (0,)*len(thresholds) and len(set(states)) == len(states),'unique zero-rooted states')
    need(len(states) == len(edges) == len(outputs),'table dimensions')
    reached = {0}
    for i,state in enumerate(states):
        need(i in reached and len(state) == len(thresholds),'reachable state order')
        need(outputs[i] == lo+sum(v>=0 for v in state),'quotient output')
        need(len(edges[i]) == len(alphabet),'complete outgoing edges')
        for (s,b),j in zip(alphabet,edges[i]):
            need(type(j) is int and 0 <= j < len(states),'edge index')
            # This uses the floor inequality, without the producer transition division.
            need(all(2*v <= old+s-t*b < 2*v+2 for v,old,t in zip(states[j],state,thresholds)),'exact transition')
            reached.add(j)
    levels = c['levels'];need(levels and levels[-1] == c['groups'],'complete refinement history')
    partition(outputs,levels[0])
    for old,new in zip(levels,levels[1:]):
        partition([(outputs[i],tuple(old[j] for j in edges[i])) for i in range(len(states))],new)
    groups = levels[-1]
    partition([(outputs[i],tuple(groups[j] for j in edges[i])) for i in range(len(states))],groups)
    count = max(groups)+1
    need(len(c['compact_edges']) == len(c['compact_output']) == count and c['start'] == groups[0],'compact dimensions')
    for i,g in enumerate(groups):
        need(c['compact_output'][g] == outputs[i],'compact output equivalence')
        need(c['compact_edges'][g] == [groups[j] for j in edges[i]],'compact transition equivalence')
    return dict(reachable=len(states),minimal_quotient_states=count,alphabet=len(alphabet),
                compact_edges=count*len(alphabet),state_bits=(count-1).bit_length()+14,
                quotient_index_bits=(count-1).bit_length())


def stream(low,q):
    return (tuple((x>>i)&1 for x in (*low,q)) for i in range(q.bit_length()))


def oracle(col,low,q):
    value = sum((a*x for a,x in zip(col,low)),Q(0))
    residue = value.numerator*pow(value.denominator,-1,q) % q
    result = 4*(value-residue)/q
    need(result.denominator == 1,'oracle integral code')
    return int(result)


def packet(col,c,data,low,q):
    bits = m.produce(col,c,data,stream(low,q))
    return sum(b<<i for i,b in enumerate(bits))-16


def rejects(fn):
    try:fn()
    except ValueError:return 1
    raise ValueError('negative control accepted')


def verify(write=False):
    records = list(m.columns(source()));need(len(records) == 3552,'all source routes')
    models = sorted({m.plan(col)[2] for _,col in records})
    if write:
        tables = [m.compile_model(model) for model in models]
        (P/'TABLES.json.gz').write_bytes(gzip.compress(canonical(tables),mtime=0))
    else:tables = json.loads(gzip.decompress((P/'TABLES.json.gz').read_bytes()))
    need([c['model'] for c in tables] == [[a,b,list(d)] for a,b,d in models],'all shared models')
    reports = [check_machine(c) for c in tables]
    descriptors,data,packed_bits = m.pack(tables)
    if write:
        (P/'RUNTIME.json').write_bytes(canonical(descriptors)+b'\n')
        (P/'RUNTIME.bin').write_bytes(data)
    else:
        need(descriptors == json.loads((P/'RUNTIME.json').read_text()) and data == (P/'RUNTIME.bin').read_bytes(),'complete packed runtime')
    for c,d in zip(tables,descriptors):
        for i,value in enumerate(c['compact_output']):
            need(m.read_bits(data,d['output_offset']+5*i,5)-16 == value,'packed output')
        for i,row in enumerate(c['compact_edges']):
            for j,value in enumerate(row):
                offset = d['edge_offset']+(i*len(row)+j)*d['index_bits']
                need(m.read_bits(data,offset,d['index_bits']) == value,'packed transition')
    lookup = dict(zip(models,descriptors))
    rng = random.Random(6474);digest = sha256();cases = exhaustive = 0;old_peak = 0
    for label,col in records:
        a,d,model = m.plan(col);c = lookup[model];lo,hi,_ = model;positive = sum(max(v,0) for v in a)
        old = 16+sum((positive-min(j,0)-lo+max(j,0)).bit_length() for j in range(lo+1,hi+1));old_peak = max(old_peak,old)
        for q in (1,3,5,25,2**89-1):
            low = [rng.randrange(q) for _ in range(8)]
            got = packet(col,c,data,low,q);need(got == oracle(col,low,q),'complete source packet')
            digest.update(canonical([label,q,low,got]));cases += 1
    unique = sorted({col for _,col in records})
    for col in unique:
        c = lookup[m.plan(col)[2]];active = [i for i,a in enumerate(col) if a]
        for values in product(range(3),repeat=len(active)):
            low = [0]*8
            for i,v in zip(active,values):low[i] = v
            need(packet(col,c,data,low,3) == oracle(col,low,3),'exhaustive active lows');exhaustive += 1
    for col in unique[::120]:
        q = 2**4097-1;low = [rng.randrange(q) for _ in range(8)]
        need(packet(col,lookup[m.plan(col)[2]],data,low,q) == oracle(col,low,q),'long stream')
    col = unique[-1];c = lookup[m.plan(col)[2]]
    controls = rejects(lambda:m.produce(col,c,data,[]))
    controls += rejects(lambda:packet(col,c,data,[0]*8,4))
    controls += rejects(lambda:packet(col,c,data,[5]+[0]*7,5))
    controls += rejects(lambda:m.produce(col,c,data,[(0,)*9]))
    bad = deepcopy(tables[0]);bad['compact_edges'][0][0] = (bad['compact_edges'][0][0]+1)%len(bad['compact_edges'])
    controls += rejects(lambda:check_machine(bad))
    bad = deepcopy(tables[0]);bad['compact_output'][0] += 1
    controls += rejects(lambda:check_machine(bad))
    bad = deepcopy(tables[0]);bad['groups'][1] = bad['groups'][0]
    controls += rejects(lambda:check_machine(bad))
    edge_bits = sum(r['compact_edges']*r['quotient_index_bits'] for r in reports)
    output_bits = sum(len(c['compact_output'])*5 for c in tables)
    return dict(status='PASS_G20_COMPACT_CARRY_MACHINES',routes=444,columns=3552,distinct_columns=len(unique),
                models=reports,model_count=len(models),source_cases=cases,exhaustive_cases=exhaustive,
                maximum_between_row_bits=max(r['state_bits'] for r in reports),old_separate_counter_bits=old_peak,
                transition_bits=edge_bits,output_bits=output_bits,transcript_sha256=digest.hexdigest(),
                runtime_table_bits=packed_bits,runtime_table_bytes=len(data),runtime_metadata_bytes=len(canonical(descriptors))+1,
                tables_sha256=sha256(canonical(tables)).hexdigest(),negative_controls=controls)


if __name__ == '__main__':
    need(sys.argv[1:] in ([],['--write']),'supported arguments')
    result = verify(sys.argv[1:] == ['--write'])
    if sys.argv[1:] == ['--write']:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result == json.loads((P/'RESULT.json').read_text()),'complete receipt')
    print(result['status'])
