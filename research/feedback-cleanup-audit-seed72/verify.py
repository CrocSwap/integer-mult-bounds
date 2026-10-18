"""Exact audit of target exclusion in the interleaved cleanup interface.

Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter,deque
import copy
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE='abdc6a7002abdbcd9e21bfc5e1a795784deacfdf'
WORD='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
LEMMA='research/e8-bit-r420/README.md'
CHECKER='research/e8-bit-p111-tuned/code/xcheck_p.py'
REQUIRED={WORD,LEMMA,CHECKER}
GATES=tuple((d,s) for d in range(3) for s in range(3) if d!=s)
I=(1,2,4);S=(1,2,5)

def need(ok,why):
    if not ok:raise ValueError(why)
def xor(xs):
    out=0
    for x in xs:out^=x
    return out
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest_obj(obj):return hashlib.sha256(canonical(obj).encode()).hexdigest()
def file_digest(path):
    raw=path.read_bytes()
    return hashlib.sha256(raw if path.suffix=='.gz' else raw.replace(b'\r\n',b'\n')).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def check_pins(pins):
    need(pins['base_commit']==BASE and set(pins['files'])==REQUIRED,'required source inventory')
    for path,h in pins['files'].items():need(file_digest(ROOT/path)==h,'source digest')
def gate(rows,d,s):
    result=list(rows);result[d]^=result[s];return tuple(result)
def multiply(a,b):
    return tuple(xor(b[j] for j in range(len(b)) if row>>j&1) for row in a)
def apply(rows,value):return sum(((row&value).bit_count()%2)<<j for j,row in enumerate(rows))
def truth(gates,value):
    for d,s in gates:value^=((value>>s)&1)<<d
    return value
def cleanup(word):return tuple(g for g in reversed(word) if g[0]<2)
def inverse(a):
    n=len(a);rows=[row|(1<<(n+i)) for i,row in enumerate(a)]
    for i in range(n):
        pivot=next((j for j in range(i,n) if rows[j]>>i&1),None)
        need(pivot is not None,'invertible matrix')
        rows[i],rows[pivot]=rows[pivot],rows[i]
        for j in range(n):
            if j!=i and rows[j]>>i&1:rows[j]^=rows[i]
    return tuple(row>>n for row in rows)
def naive(raw):return raw[2]==5 and not ((raw[0]|raw[1])&4)

def block_conditions(raw,clean,zcount,nrows):
    """N is the preliminary target shear, L is each target's source x_i."""
    n=len(raw);v=n-zcount;zmask=(1<<zcount)-1
    need(len(nrows)==v,'N target rows')
    U=tuple(row&zmask for row in raw[:zcount])
    V=tuple(row>>zcount for row in raw[:zcount])
    J=tuple(row&zmask for row in raw[zcount:])
    K=tuple(row>>zcount for row in raw[zcount:])
    P=tuple(row&zmask for row in clean[:zcount])
    Q=tuple(row>>zcount for row in clean[:zcount])
    need(clean[zcount:]==tuple(1<<(zcount+i) for i in range(v)),'cleanup fixes targets')
    pu_qj=tuple(a^b for a,b in zip(multiply(P,U),multiply(Q,J)))
    pv_q=tuple(a^b for a,b in zip(multiply(P,V),Q))
    return {'K_identity':K==tuple(1<<i for i in range(v)),
            'J_plus_N_is_L':tuple(a^b for a,b in zip(J,nrows))==tuple(1<<i for i in range(v)),
            'PV_plus_Q_zero':not any(pv_q),'PU_plus_QJ_identity':pu_qj==tuple(1<<i for i in range(zcount))}

def quotient():
    # Independently enumerate GL(3,2) by bijective action on all eight vectors.
    gl=tuple(rows for rows in product(range(1,8),repeat=3) if len({apply(rows,x) for x in range(8)})==8)
    parabolic=tuple(rows for rows in gl if rows[2]==4)
    need((len(gl),len(parabolic))==(168,24),'finite ambient group sizes')
    inverses={a:inverse(a) for a in gl}
    start=(I,I);paths={start:()};q=deque([start]);edges=0
    while q:
        raw,proj=q.popleft();word=paths[(raw,proj)]
        for d,s in GATES:
            nxt=(gate(raw,d,s),gate(proj,d,s) if d<2 else proj);edges+=1
            if nxt not in paths:paths[nxt]=word+((d,s),);q.append(nxt)
    need(set(paths)==set(product(gl,parabolic)),'complete quotient coverage, not cutoff search')
    good=[];bad=[];states=[];modes={}
    for raw,proj in sorted(paths):
        word=paths[(raw,proj)];c=inverses[proj];out=multiply(c,raw)
        conditions=block_conditions(raw,c,2,(0,))
        need(all(conditions.values())==(out==S),'necessary and sufficient block conditions')
        for value in range(8):
            need(truth(word,value)==apply(raw,value),'independent raw truth-table replay')
            need(truth(cleanup(word),value)==apply(c,value),'independent cleanup truth-table replay')
            need(truth(word+cleanup(word),value)==apply(out,value),'independent complete truth table')
        if naive(raw):
            (good if out==S else bad).append((raw,proj))
            key=str(int(conditions['PV_plus_Q_zero']))+str(int(conditions['PU_plus_QJ_identity']))
            modes.setdefault(key,[]).append((raw,proj))
        states.append([list(raw),list(proj),len(word)])
    witness=min(bad,key=lambda state:(len(paths[state]),paths[state]))
    word=paths[witness];out=multiply(inverses[witness[1]],witness[0])
    # Separate exhaustive literal-program minimality check below length three.
    small=0
    for length in range(len(word)):
        for candidate in product(GATES,repeat=length):
            raw=I
            for d,s in candidate:raw=gate(raw,d,s)
            if naive(raw):need(all(truth(candidate+cleanup(candidate),x)==apply(S,x) for x in range(8)),'shorter literal counterexample')
            small+=1
    need(len(paths)==4032 and edges==24192 and len(good)==6 and len(bad)==138,'census constants')
    need(len(word)==3 and small==43,'sharp three-ADD raw boundary')
    mode_records={}
    for key,entries in sorted(modes.items()):
        state=min(entries,key=lambda a:(len(paths[a]),paths[a]));p=paths[state]
        mode_records[key]={'count':len(entries),'shortest_raw_word':p,'cleanup_word':cleanup(p),
                           'complete_matrix':multiply(inverses[state[1]],state[0]),
                           'conditions':block_conditions(state[0],inverses[state[1]],2,(0,))}
    need('01' in modes and '10' in modes,'each cleanup equation independently necessary')
    return {'states':len(paths),'edges':edges,'diameter':max(map(len,paths.values())),
            'layers':sorted(Counter(map(len,paths.values())).items()),'ordered_distance_table_sha256':digest_obj(states),
            'naive_endpoint_states':len(good)+len(bad),'restoring_states':len(good),'nonrestoring_states':len(bad),
            'truth_table_inputs':8*len(paths),'shorter_literal_programs':small,'cleanup_equation_modes':mode_records,
            'witness':{'raw_word':word,'cleanup_word':cleanup(word),'raw_matrix':witness[0],
                       'projected_product':witness[1],'complete_matrix':out,
                       'block_conditions':block_conditions(witness[0],inverses[witness[1]],2,(0,)),
                       'truth_table':[[x,truth(word+cleanup(word),x),apply(S,x)] for x in range(8)]}}

def selected():
    w=json.loads(gzip.decompress((ROOT/WORD).read_bytes()));v,r=w['v'],w['R'];n=2*v+r;zcount=v+r
    need((v,r)==(111,439),'selected dimensions')
    order=list(range(v))+list(range(2*v,n))+list(range(v,2*v));where={old:new for new,old in enumerate(order)}
    def gates(phase):return [(where[d],where[s]) for f,d,ss in w[phase] for s in ss]
    scatter=[(zcount+t,where[w['ret'][k]]) for k in range(len(w['ret'])) for t,row in enumerate(w['scatter']) if k in row]
    rawg=gates('A')+scatter+gates('B');cg=gates('C');dg=gates('D');identity=tuple(1<<i for i in range(n))
    def replay(gs,initial=identity):
        rows=list(initial)
        for d,s in gs:rows[d]^=rows[s]
        return tuple(rows)
    # A gate's sources must reverse internally when it is expanded into ADDs.
    # Distinct same-destination transvections commute, so a block reversal is
    # equivalent; compare grouped source sets after reversing gate order.
    z_original=[(f,d,ss) for phase in ('A','B') for f,d,ss in w[phase] if not v<=d<2*v]
    need([(d,ss) for f,d,ss in w['C']]==[(d,ss) for f,d,ss in reversed(z_original)],'source grouped literal cleanup')
    need(all(s<zcount for d,s in rawg if d<zcount),'selected target exclusion H1/H3')
    need(all(d>=zcount and v<=s<zcount for d,s in dg),'selected D reads only helpers')
    raw=replay(rawg);clean=replay(cg);pre=replay(dg);full=replay(dg+rawg+cg)
    nrows=tuple(row^identity[zcount+i] for i,row in enumerate(pre[zcount:]))
    conditions=block_conditions(raw,clean,zcount,nrows)
    want=identity[:zcount]+tuple((1<<(zcount+i))^(1<<i) for i in range(v))
    need(all(conditions.values()) and full==want,'selected complete dirty-state interface')
    need(multiply(clean,multiply(raw,pre))==full,'independent block composition equals stream')
    return {'v':v,'R':r,'input_columns':n,'z_columns':zcount,'raw_adds':len(rawg),'D_adds':len(dg),'C_adds':len(cg),
            'block_conditions':conditions,'target_exclusion':True,'grouped_literal_cleanup':True,
            'raw_matrix_sha256':digest_obj(raw),'cleanup_matrix_sha256':digest_obj(clean),'complete_matrix_sha256':digest_obj(full)}

def run():
    pins=read(HERE/'SOURCES.json');check_pins(pins)
    census=quotient();baseline=selected();passed=[]
    def reject(label,fn):
        try:fn()
        except ValueError:passed.append(label)
        else:raise ValueError('control accepted: '+label)
    w=census['witness'];raw=tuple(w['raw_matrix']);proj=tuple(w['projected_product']);clean=inverse(proj)
    need(naive(raw),'counterexample really passes proposed weakened premise')
    reject('endpoint-only cleanup implication',lambda:need(multiply(clean,raw)==S,'helper leak'))
    reject('raw z block equals projected z product',lambda:need(raw[:2]==proj[:2],'interleaved feedback changes U'))
    reject('checking targets alone certifies restoration',lambda:need(all(want==got for _,got,want in w['truth_table']),'non-target corruption'))
    # Empty dirty helper input still leaks x: input x=1,h=y=0.
    reject('zero helper initialization repairs feedback',lambda:need(w['truth_table'][1][1]==w['truth_table'][1][2],'helper output differs'))
    for key,equation in (('01','PV_plus_Q_zero'),('10','PU_plus_QJ_identity')):
        conditions=census['cleanup_equation_modes'][key]['conditions']
        need(all(value for name,value in conditions.items() if name!=equation),'other three equations hold')
        reject('omit '+equation,lambda conditions=conditions:need(all(conditions.values()),'independent cleanup obligation'))
    # One feedback is forbidden under H1; two cancel if the target stays unchanged.
    neutral=((1,2),(1,2),(2,0));need(all(truth(neutral+cleanup(neutral),x)==apply(S,x) for x in range(8)),'feedback exclusion is sufficient, not necessary')
    changed=copy.deepcopy(pins);changed['files'].pop(CHECKER)
    reject('omitted source pin',lambda:check_pins(changed))
    changed=copy.deepcopy(pins);changed['files'][WORD]='0'*64
    reject('corrupted word pin',lambda:check_pins(changed))
    return {'status':'PASS_FEEDBACK_CLEANUP_AUDIT_S72','seed':72,'base_commit':BASE,'source_pins':pins,
            'quotient':census,'selected_baseline':baseline,'neutral_feedback_control':neutral,'negative_controls':passed,
            'scope':'F2 scalar projected cleanup; target exclusion relaxed in both H1 and H3, frame legality not generalized.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if args.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    else:need(canonical(result)==canonical(read(path)),'deterministic receipt mismatch')
    print('PASS_FEEDBACK_CLEANUP_AUDIT_S72 states=4032 naive=144 bad=138 minimum=3 selected_columns=661 controls='+str(len(result['negative_controls'])))

if __name__=='__main__':main()
