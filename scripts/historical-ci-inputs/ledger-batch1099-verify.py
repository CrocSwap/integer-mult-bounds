"""Independent complete PR967 single-ADD omission atlas.
No predecessor code imports. Prepared for @woklerx with substantial
OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
INPUTS=('research/r439-helper-stars-seed19/candidate.json.gz',
        'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz')
N=661


def need(ok,message):
    if not ok:raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def load(raw):
    def pairs(items):
        result={}
        for k,v in items:
            need(k not in result,'duplicate JSON key')
            result[k]=v
        return result
    def bad(value):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)


def load_inputs():
    manifest=load((HERE/'SOURCES.json').read_bytes())
    need(set(manifest)=={'base_commit','files'},'source manifest fields')
    need(manifest['base_commit']==BASE and set(manifest['files'])==set(INPUTS),'source pin inventory')
    words=[]
    for name in INPUTS:
        raw=(ROOT/name).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==manifest['files'][name],'source pin mismatch: '+name)
        words.append(load(gzip.decompress(raw)))
    candidate,selected=words
    need(candidate['v']==111 and candidate['R']==439 and len(candidate['start'])==N,'word dimensions')
    need(set(candidate)==set(selected),'word field inventory')
    need(all(canonical(candidate[k])==canonical(selected[k]) for k in selected if k!='D'),
         'non-D source fields changed')
    return words


def expand(word):
    gates=[]
    for record,(frame,d,sources) in enumerate(word['D']):
        need(type(frame) is int and frame==0,'D frame')
        need(type(d) is int and 0<=d<N and isinstance(sources,list),'D gate')
        for position,s in enumerate(sources):
            need(type(s) is int and 0<=s<N and d!=s,'ADD operands')
            gates.append((d,s,record,position))
    return gates


def replay(gates,omit=-1):
    rows=[1<<i for i in range(N)]
    for k,(d,s,_,__) in enumerate(gates):
        if k!=omit:rows[d]^=rows[s]
    return rows


def factors(gates):
    # Forward row action obtains the covector immediately BEFORE each gate.
    rows=[1<<i for i in range(N)]
    incoming=[]
    for d,s,_,__ in gates:
        incoming.append(rows[s]);rows[d]^=rows[s]
    # Right-multiply suffix matrices: appending gate on their input updates
    # column s by column d. Columns are stored as output-bit vectors.
    columns=[1<<i for i in range(N)]
    outgoing=[0]*len(gates)
    for k in range(len(gates)-1,-1,-1):
        d,s,_,__=gates[k]
        outgoing[k]=columns[d];columns[s]^=columns[d]
    return list(zip(outgoing,incoming))


def bits(mask):
    return [i for i in range(N) if mask>>i&1]


def vector_run(gates,input_mask,omit=-1):
    values=[bool(input_mask>>i&1) for i in range(N)]
    for k,(d,s,_,__) in enumerate(gates):
        if k!=omit:values[d]=values[d]!=values[s]
    return sum(int(v)<<i for i,v in enumerate(values))


def region(k):
    if k<221:return 'helper_preparation'
    if k<527:return 'target_preparation'
    if k<5036:return 'middle_injection'
    if k<5342:return 'target_restoration'
    return 'helper_restoration'


def run():
    candidate,selected=load_inputs()
    gates=expand(candidate);baseline=replay(gates)
    need(len(gates)==5563 and len(candidate['D'])==1165,'frozen D domain')
    need(baseline==replay(expand(selected)),'semantic D boundary differs from PR589')
    # Source/target/helper block boundaries are physical, not inferred labels.
    need(all(baseline[i]==1<<i for i in list(range(111))+list(range(222,N))),
         'baseline source/helper restoration')
    for i in range(111,222):
        need((baseline[i]^(1<<i))&((1<<222)-1)==0,'unexpected D source or target dependence')
    target=((1<<111)-1)<<111
    helper=((1<<439)-1)<<222
    for k,(d,s,_,__) in enumerate(gates):
        part=region(k)
        if part.startswith('helper_'):
            need(222<=d<N and 222<=s<N,'helper region operands')
        elif part.startswith('target_'):
            need(111<=d<222 and 111<=s<222,'target region operands')
        else:
            need(111<=d<222 and 222<=s<N,'middle region operands')
    atlas=factors(gates)
    region_counts=defaultdict(Counter);full_unique=Counter();target_unique=Counter()
    invisible=[];allones_blind=[];digest=hashlib.sha256()
    for k,((u,v),(d,s,record,position)) in enumerate(zip(atlas,gates)):
        need(u and v,'zero omission factor')
        # Independent literal mutant replays EVERY prefix/suffix, using no
        # precomputed factors or inverse shortcut.
        changed=replay(gates,k)
        for row,(a,b) in enumerate(zip(baseline,changed)):
            need((a^b)==(v if u>>row&1 else 0),'literal omission delta disagrees at '+str(k))
        seen_target=bool(u&target)
        region_counts[region(k)]['total']+=1
        region_counts[region(k)]['target_visible' if seen_target else 'target_invisible']+=1
        full_unique[u,v]+=1
        if seen_target:target_unique[u&target,v]+=1
        else:invisible.append(k)
        if v.bit_count()%2==0:allones_blind.append(k)
        digest.update(canonical([k,d,s,record,position,str(u),str(v)])+b'\n')
    # A singleton input in v's support activates exactly u. Provide literal
    # Boolean witnesses for every distinct invisible output/input pair.
    witnesses=[]
    distinct={}
    for k in invisible:
        u,v=atlas[k]
        distinct.setdefault((u,v),k)
    for (u,v),k in distinct.items():
        singleton=v&-v
        before=vector_run(gates,singleton);after=vector_run(gates,singleton,k)
        need(before^after==u and not u&target and bool(u&helper),'helper-only witness')
        d,s,record,position=gates[k]
        witnesses.append({'gate':k,'record':record,'source_position':position,'destination':d,'source':s,
            'input_register':singleton.bit_length()-1,'changed_output_registers':bits(u)})
    # A representative input-blind fault is also replayed as literal Booleans:
    # all ones misses it, whereas a single selected input bit exposes it.
    blind=allones_blind[0]
    u,v=atlas[blind]
    singleton=v&-v
    allones=(1<<N)-1
    need(vector_run(gates,allones)==vector_run(gates,allones,blind),'all-ones blind replay')
    need(vector_run(gates,singleton)^vector_run(gates,singleton,blind)==u,
         'singleton detects all-ones blind fault')
    blind_witness={'gate':blind,'input_register':singleton.bit_length()-1,
        'changed_output_registers':bits(u),'covector_input_registers':bits(v)}
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name);return
        raise ValueError('negative control accepted: '+name)
    reject('missing omission index',lambda:need(len(atlas[:-1])==len(gates),'coverage'))
    reject('zero covector accepted',lambda:need(all(u and v for u,v in [(1,0)]),'zero factor'))
    reject('target-only equals full boundary',lambda:need(not invisible,'target misses helper dirt'))
    reject('all-ones proves arbitrary-input boundary',lambda:need(not allones_blind,'even covectors invisible'))
    reject('duplicate JSON key',lambda:load('{"n":1,"n":2}'))
    reject('nonfinite JSON',lambda:load('{"n":Infinity}'))
    need(canonical({'n':1})!=canonical({'n':True}),'receipt type sensitivity')
    # Concrete wrong orientation: suffix effects need not be the destination
    # singleton. Find and reject a fault with a nontrivial suffix column.
    nontrivial=next(k for k,(u,v) in enumerate(atlas) if u!=1<<gates[k][0])
    reject('unpropagated destination singleton',lambda:need(atlas[nontrivial][0]==1<<gates[nontrivial][0],
                                                          'suffix effect omitted'))
    return {'format':'r439-single-omission-atlas/1','base_commit':BASE,'seed':81,
        'status':'PASS_R439_OMISSION_ATLAS','original_records':1165,'expanded_ADDs':5563,
        'input_columns':N,'full_omission_replays':len(gates),'factor_ranks':{'1':len(gates)},
        'full_unique_syndromes':len(full_unique),'full_collision_histogram':dict(Counter(full_unique.values())),
        'target_visible':len(gates)-len(invisible),'target_invisible':len(invisible),
        'target_unique_nonzero_syndromes':len(target_unique),
        'target_invisible_indices':invisible,'all_ones_blind':len(allones_blind),
        'all_ones_blind_indices':allones_blind,'all_ones_blind_witness':blind_witness,'regions':{k:dict(v) for k,v in sorted(region_counts.items())},
        'helper_only_witnesses':witnesses,'atlas_sha256':digest.hexdigest(),
        'baseline_matrix_sha256':hashlib.sha256(canonical([str(x) for x in baseline])).hexdigest(),
        'controls_rejected':controls,
        'scope':'one elementary ADD omission in frozen PR967 D; complete D output observation versus target-only; no multi-fault or whole-word propagation claim'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if args.write_certificate:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    else:need(canonical(load(canonical(result)))==canonical(load(path.read_bytes())),'certificate mismatch')
    print('PASS_R439_OMISSION_ATLAS gates={} target_invisible={} unique={} controls={} no_new_kappa'.format(
        result['expanded_ADDs'],result['target_invisible'],result['full_unique_syndromes'],len(result['controls_rejected'])))


if __name__=='__main__':main()
