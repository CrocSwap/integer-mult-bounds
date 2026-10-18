"""Literal shared-chart retiming and full rational boundary replay.

Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
Source construction: commdata2338/2662, ywz65/2586 and retained lineage.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import copy,hashlib,json,types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INTERPRETER='research/p104-native-channel/vendor/native_verify.py'
def need(value,message):
    if not value:raise ValueError(message)
def read(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=unique)
def same(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def authenticate():
    count=0
    for record in read(HERE/'SOURCES.json')['files']:
        if record['usage']=='input':
            raw=(ROOT/record['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==record['sha256'],'live source hash')
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==record['git_blob'],'live source blob');count+=1
    for record in read(HERE/'PREDECESSORS.json')['records']:
        raw=(HERE/record['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==record['sha256'],'predecessor hash')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==record['git_blob'],'predecessor blob');count+=1
    return count
def load_interpreter():
    authenticate()
    path=ROOT/INTERPRETER;raw=path.read_bytes()
    pin=next(r for r in read(HERE/'SOURCES.json')['files'] if r['path']==INTERPRETER)
    need(hashlib.sha256(raw).hexdigest()==pin['sha256'],'captured interpreter hash')
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'captured interpreter blob')
    # Execute the buffer just authenticated, not a timestamp-selected .pyc.
    module=types.ModuleType('retiming_native_interpreter');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module
def canonical(vectors):
    rows={}
    for x in vectors:
        need(type(x) is int and 0<x<512,'binary frame vector')
        for bit in sorted(rows,reverse=True):
            if x>>bit&1:x^=rows[bit]
        if x:
            bit=x.bit_length()-1
            for other in rows:
                if rows[other]>>bit&1:rows[other]^=x
            rows[bit]=x
    return tuple(rows[b] for b in sorted(rows,reverse=True))
def contains(large,small):return len(canonical((*large,*small)))==len(large)
def operands(event):return event[1:3] if event[0]=='add' else event[1:2]

def construct(source):
    """Replace exactly two complete, source-indexed early ADD stars."""
    program=source['program'];changes={}
    expected={104:['transport','Y0',[],[386],1],105:['transport','Y1',[],[391],1],
              380:['transport','N2',[],[391],1],381:['transport','N4',[],[386],1],
              382:['transport','N33',[],[391],1],383:['transport','N34',[],[386],1],
              384:['add','N2','Y1','2',[391]],385:['transport','N2',[391],[386,5],1],
              386:['add','N4','Y0','1',[386]],387:['transport','N4',[386],[386,5],1],
              388:['add','N33','Y1','1',[391]],389:['add','N34','Y0','1',[386]],
              980:['transport','Y1',[391],[273,145,81,49,9,5,2],6],
              981:['transport','Y0',[386],[273,145,96,12,2],4]}
    for index,event in expected.items():need(program[index]==event,'source star occurrence')
    # Every affected interval is read explicitly. No undeclared source use can
    # be crossed merely because its target is another register.
    windows={'Y0':(104,981,{104,386,389,981}),'Y1':(105,980,{105,384,388,980}),
             'N2':(380,385,{380,384,385}),'N4':(381,387,{381,386,387}),
             'N33':(382,388,{382,388}),'N34':(383,389,{383,389})}
    for role,(start,end,allowed) in windows.items():
        seen={i for i in range(start,end+1) if role in operands(program[i])}
        need(seen==allowed,'undeclared star access')
    for index in (104,105,380,381,382,383):changes[index]=[]
    for index in (384,386,388,389):
        event=copy.deepcopy(program[index]);event[4]=[];changes[index]=[event]
    for index in (385,387,980,981):
        event=copy.deepcopy(program[index]);event[2]=[];event[4]=len(event[3]);changes[index]=[event]
    for index,role,q in ((388,'N33',391),(389,'N34',386)):
        changes[index].append(['transport',role,[],[q],1])
    result=copy.deepcopy(source)
    result['program']=[e for i,event in enumerate(program) for e in changes.get(i,[event])]
    edges=[{'source_event':i,'role':program[i][1],'old':[],'new':program[i][3],'rank':len(program[i][3])} for i in (385,387,980,981)]
    return result,edges

def replay(word):
    frames={r:canonical(f) for r,f in word['initial_frames'].items()}
    initial=sorted(frames);rows={r:{r:Fraction(1)} for r in initial}
    profile=Counter();counts=Counter();erased=0
    for event in word['program']:
        tag=event[0];counts[tag]+=1
        if tag=='transport':
            _,r,a,b,k=event;a,b=canonical(a),canonical(b)
            need(frames[r]==a,'transport source frame')
            need(contains(a,b) or contains(b,a),'nested transport')
            need(type(k) is int and k==abs(len(a)-len(b))>0,'transport rank')
            frames[r]=b;profile[k]+=1
        elif tag=='add':
            _,t,s,c,f=event;f=canonical(f)
            need(t!=s and frames[t]==frames[s]==f,'ADD common frame')
            c=Fraction(c)
            for r,v in rows[s].items():rows[t][r]=rows[t].get(r,Fraction(0))+c*v
            rows[t]={r:v for r,v in rows[t].items() if v}
        elif tag=='sign':
            _,r,c,f=event;need(frames[r]==canonical(f),'sign frame')
            need(Fraction(c) in (-1,1),'scalar sign')
            rows[r]={s:Fraction(c)*v for s,v in rows[r].items()}
        elif tag=='zero':
            _,r,f=event;need(r not in rows,'fresh owned zero')
            rows[r]={};frames[r]=canonical(f)
        elif tag=='erase':
            _,r,f=event;need(frames[r]==canonical(f) and not rows[r],'exact zero erase')
            del rows[r];del frames[r];erased+=1
        else:raise ValueError('unknown event')
    need(frames=={r:canonical(f) for r,f in word['final_frames'].items()},'final frames')
    need(set(rows)==set(initial),'public output inventory')
    helpers=[r for r in initial if not r.startswith(('X','Y'))]
    need(len(helpers)==150 and all(rows[r]=={r:Fraction(1)} for r in helpers),'arbitrary helper restoration')
    packed=[[r,[[s,str(v)] for s,v in sorted(rows[r].items())]] for r in initial]
    return {'events':len(word['program']),'counts':dict(sorted(counts.items())),'profile':dict(sorted(profile.items())),
            'rank_mass':sum(r*n for r,n in profile.items()),'public_inputs':len(initial),'public_outputs':len(rows),
            'boundary_coefficients':len(initial)*len(rows),'boundary_sha256':hashlib.sha256(json.dumps(packed,separators=(',',':')).encode()).hexdigest(),
            'dirty_helpers_restored':len(helpers),'zero_erasures':erased},rows

def conjugate(gates):
    out=[]
    for gate in gates:
        tag=gate[0]
        if tag=='C':out.append((tag,gate[1],-gate[2]))
        elif tag=='D':out.append((tag,gate[1],tuple(-v%4 for v in gate[2])))
        elif tag=='phase':out.append((tag,-gate[1]%4))
        else:need(tag in ('P','X'),'known monomial gate');out.append(gate)
    return tuple(out)
def native_recipe(frame,interpreter):
    """Explicit one-positive-child formula; no Clifford compiler is used.

    If Gamma=M F_r M^-1, then conjugate(Gamma)=
    conjugate(M) F_r X_(2^r-1) conjugate(M)^-1, since C^-1=X C.
    Gate lists are in chronological execution order.
    """
    r=len(frame);need(0<r<9,'proper new frame')
    matrix=interpreter.transpose(interpreter.extend(tuple(frame),9))
    columns=interpreter.transpose(interpreter.inverse(matrix))
    quadratic=tuple((1<<i)^sum(((a&b).bit_count()%2)<<j for j,b in enumerate(columns)) for i,a in enumerate(columns))
    linear=tuple((row>>i)&1 for i,row in enumerate(quadratic))
    chart=(('P',matrix),('D',quadratic,linear))
    before=conjugate(interpreter.adjoint(chart))+(('X',(1<<r)-1),)
    after=conjugate(chart)
    return {'rank':r,'before':before,'after':after}
def freeze(value):return tuple(freeze(x) for x in value) if isinstance(value,list) else value
def recipe_gates(record,interpreter):
    need(type(record['rank']) is int and 0<record['rank']<9,'native child rank')
    before,after=freeze(record['before']),freeze(record['after'])
    need(all(g[0] in ('P','D','X','phase') for g in before+after),'native monomial wrappers')
    return before+interpreter.fourier(record['rank'])+after
def native_payload(edges,interpreter):
    records=[]
    for frame in sorted({tuple(e['new']) for e in edges}):
        records.append({'new':frame,'source_events':[e['source_event'] for e in edges if tuple(e['new'])==frame],
                        'recipe':native_recipe(frame,interpreter)})
    return {'schema_version':1,'transports':records}
