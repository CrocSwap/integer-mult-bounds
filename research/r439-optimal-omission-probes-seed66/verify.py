"""Exact optimal two-probe certificate for frozen PR967 elementary omissions."""
import argparse,gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import independent
ROOT=HERE.parents[1]
BASE='abdc6a7002abdbcd9e21bfc5e1a795784deacfdf'
INPUTS=('research/r439-helper-stars-seed19/candidate.json.gz',
        'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz')
N=661
def need(ok,msg):
    if not ok:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def load(raw):
    def pairs(items):
        d={}
        for k,v in items:
            need(k not in d,'duplicate JSON key');d[k]=v
        return d
    def bad(x):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
def pins(manifest):
    need(set(manifest)=={'base_commit','files'},'manifest fields')
    need(manifest['base_commit']==BASE and set(manifest['files'])==set(INPUTS),'source pin inventory')
    words=[]
    for name in INPUTS:
        raw=(ROOT/name).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==manifest['files'][name],'source pin mismatch')
        words.append(load(gzip.decompress(raw)))
    return words
def expand(word):
    gates=[];locations=[]
    for record,op in enumerate(word['D']):
        need(type(op) is list and len(op)==3,'D record')
        f,d,ss=op
        need(type(f) is int and f==0 and type(d) is int and 0<=d<N and type(ss) is list,'D shape')
        for p,s in enumerate(ss):
            need(type(s) is int and 0<=s<N and d!=s,'ADD operands')
            gates.append((d,s));locations.append([record,p])
    return gates,locations
def forward(gates):
    rows=[1<<i for i in range(N)];activation=[]
    for d,s in gates:activation.append(rows[s]);rows[d]^=rows[s]
    return rows,activation
def indices(v):return [i for i in range(N) if v>>i&1]
def check_probes(vs,probes):
    need(len(probes)==2 and all(type(p) is int and 0<=p<1<<N for p in probes),'two legal probes')
    need(all(any((v&p).bit_count()%2 for p in probes) for v in vs),'probe misses activation')
def run():
    manifest=load((HERE/'SOURCES.json').read_bytes());word,selected=pins(manifest)
    need(set(word)==set(selected),'source field inventory')
    need(all(canonical(word[k])==canonical(selected[k]) for k in selected if k!='D'),'non-D fields differ')
    need(word['v']==111 and word['R']==439 and len(word['start'])==N,'frozen dimensions')
    gates,locations=expand(word);old,_=expand(selected)
    baseline,vs=forward(gates);oldmap,_=forward(old)
    need(baseline==oldmap,'D differs from selected semantic boundary')
    need(len(gates)==5563 and len(set(vs))==761,'fixed census')
    w=load((HERE/'WITNESS.json').read_bytes())
    need(set(w)=={'repair_steps','seed','cap','probes','odd_dependency_unique_indices','odd_dependency_gate_indices'},'witness fields')
    need(type(w['repair_steps']) is int and w['repair_steps']==688 and type(w['seed']) is int and w['seed']==66 and type(w['cap']) is int and w['cap']==10000,'discovery metadata')
    need(type(w['probes']) is list and all(type(p) is str and p==str(int(p)) for p in w['probes']),'canonical probe integers')
    probes=list(map(int,w['probes']));check_probes(vs,probes)
    unique=list(dict.fromkeys(vs));relation=w['odd_dependency_gate_indices']
    need(canonical(relation)==canonical([236,258,259]),'frozen lower-bound relation')
    need(canonical(w['odd_dependency_unique_indices'])==canonical([unique.index(vs[i]) for i in relation]),'relation unique indices')
    total=0;dependency=[]
    for k in relation:
        total^=vs[k]
        backward=independent.backward_activation(gates,k,N)
        need(backward==indices(vs[k]),'reverse-prefix activation mismatch')
        dependency.append({'gate':k,'record':locations[k][0],'source_position':locations[k][1],
                           'destination':gates[k][0],'source':gates[k][1],'input_support':backward})
    need(total==0 and len(relation)%2==1,'odd XOR dependency')
    packed=[sum(((p>>i)&1)<<j for j,p in enumerate(probes)) for i in range(N)]
    literal=independent.complete_single_coverage(word['D'],packed)
    need(literal['target_only_missed_indices']==list(range(5342,5563)),'target-only scope')
    algebra=Counter(sum(((v&p).bit_count()%2)<<j for j,p in enumerate(probes)) for v in vs)
    need(literal['detection_patterns']=={str(k):algebra[k] for k in (1,2,3)},'independent coverage mismatch')
    # A two-fault counterexample lies entirely inside the fixed injection region.
    # Equal packed source values need not be equal linear forms.
    seen={};pair=None
    for k in range(527,5036):
        d,s=gates[k];key=(d,sum(((vs[k]&p).bit_count()%2)<<j for j,p in enumerate(probes)))
        if key in seen and vs[seen[key]]!=vs[k]:pair=(seen[key],k);break
        seen[key]=k
    need(pair is not None,'no two-fault scope witness')
    need(independent.execute(word['D'],packed)==independent.execute(word['D'],packed,pair),'pair not blind')
    activation=vs[pair[0]]^vs[pair[1]];singleton=(activation&-activation).bit_length()-1
    onehot=[int(i==singleton) for i in range(N)]
    full=independent.execute(word['D'],onehot);mutant=independent.execute(word['D'],onehot,pair)
    changed=[i for i,(a,b) in enumerate(zip(full,mutant)) if a!=b]
    need(changed and all(111<=i<222 for i in changed),'pair must genuinely alter targets')
    controls=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,TypeError):controls.append(name);return
        raise ValueError('control accepted: '+name)
    reject('zero probes',lambda:check_probes(vs,[0,0]))
    reject('only first probe repeated',lambda:check_probes(vs,[probes[0]]*2))
    reject('only second probe repeated',lambda:check_probes(vs,[probes[1]]*2))
    reject('out of range probe',lambda:check_probes(vs,[1<<N,probes[1]]))
    reject('Boolean probe',lambda:check_probes(vs,[True,probes[1]]))
    reject('wrong lower bound parity',lambda:need(len(relation[:-1])%2==1,'even relation not contradiction'))
    reject('broken lower bound dependence',lambda:need(vs[relation[0]]^vs[relation[1]]==0,'nonzero XOR'))
    reject('target-only observation suffices',lambda:need(not literal['target_only_missed_indices'],'missed helper cleanup'))
    reject('all-ones suffices',lambda:check_probes(vs,[(1<<N)-1]*2))
    reject('missing source pin',lambda:pins({'base_commit':BASE,'files':{INPUTS[0]:manifest['files'][INPUTS[0]]}}))
    reject('duplicate JSON',lambda:load('{"x":1,"x":2}'))
    reject('nonfinite JSON',lambda:load('{"x":NaN}'))
    need(canonical({'n':True})!=canonical({'n':1}),'typed receipt comparison')
    return {'format':'r439-optimal-omission-probes/1','base_commit':BASE,'seed':66,
            'minimum_probes':2,'expanded_ADDs':len(gates),'activation_forms':len(set(vs)),
            'input_registers':N,'probe_input_supports':[indices(p) for p in probes],
            'lower_bound_dependency':dependency,'literal_coverage':literal,
            'activation_matrix_sha256':hashlib.sha256(canonical([str(v) for v in vs]).encode()).hexdigest(),
            'two_omission_blind_witness':{'omitted_gates':list(pair),'input_register':singleton,'changed_output_registers':changed,
                                          'gates':[list(gates[i]) for i in pair]},
            'discovery':{'method':'weighted local repair','steps':688,'cap':10000,'seed':66},
            'controls_rejected':controls,
            'scope':'minimum fixed nonadaptive binary inputs with complete D-output observation for exactly one elementary ADD omission; no arbitrary-map or multi-fault guarantee'}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-certificate',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if args.write_certificate:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    else:need(canonical(result)==canonical(load(path.read_bytes())),'certificate mismatch')
    print('PASS_R439_OPTIMAL_OMISSION_PROBES minimum=2 faults=5563 forms=761 controls=12 pair_counterexample=1 no_new_kappa')
if __name__=='__main__':main()
