"""Prepared for Thiago with OpenAI GPT-6 Astra and Codex assistance. Apache-2.0.

Independently check the selected P111 corollary from two pinned raw inputs.
No other verifier or producer is imported. The universal rank/entropy proof
is the same Petersen reduction in README; this checks its new finite inputs.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROTOTYPE=ROOT/'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
WORD=ROOT/'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PROTOTYPE_PIN='327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'
WORD_PIN='e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
MAP={2:12,10:16,16:26,32:38,34:40,57:63,68:69,70:71,
     78:74,84:84,100:99,102:97,108:107,110:109}
CLIQUES=[[2,16,57,70,78,84,100,102],[10,16,57,70,78,84,108,110],
         [2,10,16,32,34,57,70,84],[16,32,57,68,70,84,100,108]]
UNIVERSAL=[16,57,70,84]
PAIRS={2:(0,2),10:(1,2),32:(2,3),34:(2,4),68:(3,4),
       78:(0,1),100:(0,3),102:(0,4),108:(1,3),110:(1,4)}

def need(test,message):
    if not test:raise ValueError(message)

def pinned(raw,pin):
    need(hashlib.sha256(raw).hexdigest()==pin,'source SHA-256')

def canonical(root):
    return max(tuple(root),tuple(-x for x in root))

def graph(roots):
    need(len(roots)==111,'selected P111 vertex count')
    need(len({canonical(r) for r in roots})==111,'distinct root lines')
    need(all(len(r)==8 and all(type(x) is int for x in r)
             and sum(x*x for x in r)==4 for r in roots),'integer E8 root coordinates')
    edges=set()
    for i,j in combinations(range(111),2):
        dot=sum(a*b for a,b in zip(roots[i],roots[j]))
        need(dot in (-2,0,2),'normalized integral Gram off diagonal')
        if dot:edges.add((i,j))
    return edges

def embedding(original,roots,edges,mapping):
    need(set(mapping)==set(UNIVERSAL)|set(PAIRS),'all fourteen witness vertices')
    need(len(set(mapping.values()))==14,'injective witness map')
    for old,new in mapping.items():
        reflected=list(original[old+8]);reflected[1]*=-1
        need(0<=new<111 and canonical(reflected)==canonical(roots[new]),
             'coordinate-one sign reflection into selected P111')
    for i,j in combinations(sorted(mapping),2):
        want=i in UNIVERSAL or j in UNIVERSAL or bool(set(PAIRS[i])&set(PAIRS[j]))
        got=tuple(sorted((mapping[i],mapping[j]))) in edges
        need(got==want,'exact induced four-isolates-plus-Petersen fitting graph')
    mapped=[[mapping[i] for i in c] for c in CLIQUES]
    for clique in mapped:
        need(len(set(clique))==8 and all(tuple(sorted(p)) in edges
             for p in combinations(clique,2)),'four eight-cliques')
    incidence=Counter(i for c in mapped for i in c)
    odd=sorted(i for i,c in incidence.items() if c%2)
    need(odd==sorted(mapping[i] for i in [34,68,102,110]),'four-clique odd incidence')
    need(all(tuple(sorted(p)) in edges for p in combinations(odd,2)),
         'residual four-clique')
    return mapped,odd

def rank_binary(rows):
    basis={}
    for value in rows:
        while value:
            p=value.bit_length()-1
            if p in basis:value^=basis[p]
            else:basis[p]=value;break
    return len(basis)

def upper(roots,labels,edges):
    need(len(labels)==111 and all(type(x) is int and 0<x<512 for x in labels),
         'nine-coordinate binary labels')
    need(all(x.bit_count()%2 for x in labels),'odd binary diagonal')
    need(all(not (labels[i]&labels[j]).bit_count()%2 for i,j in edges),
         'all required zero entries')
    gram=[]
    for i in range(111):
        row=0
        for j in range(111):
            value=(labels[i]&labels[j]).bit_count()%2
            need(value==(1+sum(a*b for a,b in zip(roots[i],roots[j]))//2)%2,
                 'complete binary Gram identity')
            row|=value<<j
        gram.append(row)
    need(rank_binary(labels)==9 and rank_binary(gram)==9,'full binary rank nine')

def rejection(name,fn):
    try:fn()
    except ValueError as exc:return dict(control=name,outcome='REJECTED',reason=str(exc))
    raise ValueError('corruption accepted: '+name)

def main():
    raw=PROTOTYPE.read_bytes();word_raw=WORD.read_bytes()
    pinned(raw,PROTOTYPE_PIN);pinned(word_raw,WORD_PIN)
    source=json.loads(raw);word=json.loads(gzip.decompress(word_raw));roots=word['lines']
    need(word['v']==111 and word['R']==439 and word['h']==8,'selected word header')
    original=source['root_lines'];labels120=source['binary_ports']
    need(len(original)==len(labels120)==120,'full inherited upper-bound data')
    lookup={canonical(r):b for r,b in zip(original,labels120)}
    need(len(lookup)==120 and all(canonical(r) in lookup for r in roots),
         'selected labels are present in inherited upper construction')
    labels=[lookup[canonical(r)] for r in roots]
    edges=graph(roots);cliques,odd=embedding(original,roots,edges,MAP);upper(roots,labels,edges)
    badmap=dict(MAP);badmap[2]=13
    badroots=[r[:] for r in roots];badroots[0][0]+=1
    badlabels=labels[:];badlabels[0]^=1
    edge=tuple(sorted((MAP[16],MAP[2])))
    controls=[
        rejection('P111 source bytes changed',lambda:pinned(word_raw+b' ',WORD_PIN)),
        rejection('reflection map vertex changed',lambda:embedding(original,roots,edges,badmap)),
        rejection('root norm changed',lambda:graph(badroots)),
        rejection('induced required-zero edge omitted',lambda:embedding(original,roots,edges-{edge},MAP)),
        rejection('binary diagonal changed',lambda:upper(roots,badlabels,edges)),
        rejection('binary labels truncated to eight coordinates',lambda:upper(roots,[x&255 for x in labels],edges)),
    ]
    result=dict(status='PASS_SELECTED_P111_BLOCK_RANK_AND_BINARY_BROADCAST_9D',
        prototype_sha256=PROTOTYPE_PIN,selected_word_sha256=WORD_PIN,
        vertices=111,required_zero_unordered_edges=len(edges),binary_gram_entries=111**2,
        reflection='negate coordinate 1, using zero-based coordinate indices',
        P112_to_P111_witness_map=MAP,cliques=cliques,odd_incidence=odd,
        induced_witness_vertices=14,outside_messages_fixed_for_entropy_argument=97,
        all_field_block_rank_lower_bound='9*d for every positive integer d',
        characteristic_two_block_rank_and_binary_broadcast='exactly 9*d',
        corruption_controls=controls,
        scope='Finite embedding and upper-bound checks plus the same written Petersen rank/entropy reduction. No new native word, paid supplier saving or multiplication-exponent improvement.')
    (HERE/'P111-VERIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
