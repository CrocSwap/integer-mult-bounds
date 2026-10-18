"""Finite PR589 nine-stage cancellation-free precision audit.

Prepared for @woklerx with substantial OpenAI Codex assistance, Apache-2.0.
Source word and global recipe are credited in NOTICE.md.
"""
import argparse
import ast
import copy
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
WORD='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
EXPECTED='research/e8-bit-p111-tuned/tune/EXPECTED.json'
GLOBAL='research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'
ADAPT='research/e8-bit-p111-tuned/code/adapt9p.py'
EXPORT='research/e8-bit-carrier-skeleton/code/bit/export_records.py'
REQUIRED={WORD,EXPECTED,GLOBAL,ADAPT,EXPORT}

def need(value,reason):
    if not value:raise ValueError(reason)

def digest(path):
    raw=path.read_bytes()
    return hashlib.sha256(raw if path.suffix=='.gz' else raw.replace(b'\r\n',b'\n')).hexdigest()

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def check_sources(pins):
    need(pins['base_commit']==BASE and set(pins['files'])==REQUIRED,'exact source inventory')
    for p,h in pins['files'].items():need(digest(ROOT/p)==h,'source digest: '+p)

def stream(w):
    n=2*w['v']+w['R'];out=[]
    for phase in ('D','A'):
        out += [(1,d,s) for f,d,ss in w[phase] for s in ss]
    for k,q in enumerate(w['ret']):
        out.append((2,n,q))
        out += [(1,w['v']+t,n) for t,ss in enumerate(w['scatter']) if k in ss]
        out.append((3,n,q))
    for phase in ('B','C'):
        out += [(1,d,s) for f,d,ss in w[phase] for s in ss]
    return out

def reverse(events):return [(5-op if op!=1 else op,d,s) for op,d,s in reversed(events)]

def recipe():
    out=[]
    # Direct stage table, independently organized from source recipe(K).
    pairs=(0,0,0,1,1,2,2,3,3)
    for stage,pair in enumerate(pairs):
        out.append({'kind':'local','stage':stage,'pair':pair,'reverse':bool(stage%2)})
        if stage in (1,3,5):out.append({'kind':'bridge','dst':pair,'src':pair+1,'coefficient':1})
        if stage in (2,4,6):out.append({'kind':'bridge','dst':pair,'src':pair+1,'coefficient':-1})
    for pair in (2,1,0):out.append({'kind':'bridge','dst':pair+1,'src':pair,'coefficient':1})
    out.append({'kind':'exchange'})
    return out

def source_recipe():
    tree=ast.parse((ROOT/GLOBAL).read_text(encoding='utf-8'))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='recipe')
    namespace={};exec(compile(ast.Module(body=[node],type_ignores=[]),GLOBAL,'exec'),namespace)
    return namespace['recipe'](4)

def source_bound(f,b):
    tree=ast.parse((ROOT/GLOBAL).read_text(encoding='utf-8'))
    nodes=[node.value for node in ast.walk(tree) if isinstance(node,ast.Assign)
           and any(isinstance(t,ast.Name) and t.id=='prefix' for t in node.targets)]
    need(len(nodes)==1,'unique consumed prefix expression')
    return eval(compile(ast.Expression(nodes[0]),GLOBAL,'eval'),{'__builtins__':{}},
                {'nb':18,'cf':f,'cb':b,'K':4})

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))

def local_model(events,v,r):
    n=2*v+r;rows=[(1,0,0)]*v+[(0,1,0)]*v+[(0,0,1)]*r+[(0,0,0)]
    peaks=set(rows);prefix=[];center=None
    for op,d,s in events:
        if op==1:
            need(d<n and d!=s and (s<n or center is not None),'local ADD shape')
            need(d!=center,'copied center immutable')
            rows[d]=add(rows[d],rows[s])
        elif op==2:
            need(center is None and d==n and rows[n]==(0,0,0),'fresh COPY')
            rows[d]=rows[s];center=s
        else:
            need(op==3 and d==n and center==s and rows[d]==rows[s],'literal ERASE binding')
            rows[d]=(0,0,0);center=None
        prefix.append(rows[d]);peaks.add(rows[d])
    need(center is None,'closed copies')
    return {'rows':rows,'prefix':prefix,'peaks':sorted(peaks),'bound':max(map(sum,peaks))}

def exported_stream(wanted):
    with tempfile.TemporaryDirectory(prefix='s70-',dir=HERE) as temp:
        need(Path(temp).resolve().parent==HERE.resolve(),'owned temporary output before automatic cleanup')
        p=subprocess.run([sys.executable,'-I','-B',str(ROOT/EXPORT),str(ROOT/WORD),temp],capture_output=True,text=True)
        need(p.returncode==0,'source exporter: '+p.stderr)
        raw=Path(temp,'249-records.bin').read_bytes()
        events=[];counts={str(i):0 for i in range(4)}
        for op,a,b,c,f,z in struct.iter_unpack('<6i',raw):
            counts[str(op)]+=1
            if op==1:need(c==1,'source unit ADD');events.append((op,a,b))
            if op in (2,3):events.append((op,b,a))
        need(events==wanted,'entire scalar stream matches source exporter')
        return {'records':len(raw)//24,'operations':counts,'sha256':hashlib.sha256(raw).hexdigest()}

def replay(events,models,v,r,skip_bridge=-1,zero_helpers=False):
    n=8*v+9*r;temp=n
    vals=[1]*(8*v)+[0 if zero_helpers else 1]*(9*r)+[0]
    bank=[1]*8;coarse=1;exact_peak=1;envelope_peak=1;bridge_no=0;count=0
    stages=[];trace=hashlib.sha256();helper_sets=[];max_location=None
    for event in recipe():
        if event['kind']=='local':
            stage,p,rev=event['stage'],event['pair'],event['reverse']
            a,b=(2*p+1,2*p) if rev else (2*p,2*p+1)
            model=models[int(rev)];ops=reverse(events) if rev else events
            incoming=(bank[a],bank[b],0 if zero_helpers else 1)
            local_bound=max(dot(row,incoming) for row in model['peaks'])
            envelope_peak=max(envelope_peak,local_bound);coarse*=model['bound']
            helpers=list(range(8*v+stage*r,8*v+(stage+1)*r));helper_sets.append(helpers)
            mapping=list(range(a*v,(a+1)*v))+list(range(b*v,(b+1)*v))+helpers+[temp]
            need(len(set(mapping))==2*v+r+1,'injective stage mapping')
            peak=1
            for index,((op,d,s),row) in enumerate(zip(ops,model['prefix'])):
                d,s=mapping[d],mapping[s]
                if op==1:vals[d]+=vals[s]
                elif op==2:vals[d]=vals[s]
                else:vals[d]=0
                need(vals[d]<=dot(row,incoming)<=local_bound<=coarse,'every prefix bound')
                peak=max(peak,vals[d]);count+=1
                if vals[d]>exact_peak:exact_peak=vals[d];max_location=[stage,index,d]
                trace.update((str(vals[d])+'\n').encode())
            bank[a]=max(dot(row,incoming) for row in model['rows'][:v])
            bank[b]=max(dot(row,incoming) for row in model['rows'][v:2*v])
            need(all(vals[i]<=bank[i//v] for i in range(8*v)),'bank endpoint domination')
            stages.append({'stage':stage,'reverse':rev,'input_bank_bounds':list(incoming),'exact_stage_peak':str(peak),'envelope_stage_peak':str(local_bound),'source_coarse_bound':str(coarse)})
        elif event['kind']=='bridge':
            a,b=event['dst'],event['src']
            for d,s in ((2*a,2*b),(2*b+1,2*a+1)):
                if bridge_no!=skip_bridge:
                    for j in range(v):vals[d*v+j]+=vals[s*v+j];count+=1
                    bank[d]+=bank[s]
                bridge_no+=1;coarse*=2
                exact_peak=max(exact_peak,max(vals[d*v:(d+1)*v]))
                envelope_peak=max(envelope_peak,bank[d])
                need(max(vals[d*v:(d+1)*v])<=bank[d]<=coarse,'bridge prefix bound')
        else:
            for p in range(4):
                a,b=2*p,2*p+1
                vals[a*v:(a+1)*v],vals[b*v:(b+1)*v]=vals[b*v:(b+1)*v],vals[a*v:(a+1)*v]
                bank[a],bank[b]=bank[b],bank[a]
    need(len(set(x for hs in helper_sets for x in hs))==9*r,'stage-distinct arbitrary helper inputs')
    need(exact_peak<=envelope_peak<=coarse,'final precision sandwich')
    return {'exact_positive_prefix':str(exact_peak),'exact_bits':exact_peak.bit_length(),
            'bank_envelope_prefix':str(envelope_peak),'bank_envelope_bits':envelope_peak.bit_length(),
            'coarse_prefix':str(coarse),'coarse_bits':coarse.bit_length(),'stages':stages,
            'scalar_operations':count,'bridge_shears':bridge_no,'independent_input_columns':n,
            'helper_input_columns':9*r,'local_prefix_trace_sha256':trace.hexdigest(),'max_local_location':max_location}

def boolean_endpoint(events,v,r,skip=-1):
    n=8*v+9*r;values=[1<<i for i in range(n)]+[0];bridges=0
    for event in recipe():
        if event['kind']=='local':
            st,p,rev=event['stage'],event['pair'],event['reverse']
            a,b=(2*p+1,2*p) if rev else (2*p,2*p+1)
            mapping=list(range(a*v,(a+1)*v))+list(range(b*v,(b+1)*v))+list(range(8*v+st*r,8*v+(st+1)*r))+[n]
            for op,d,s in reverse(events) if rev else events:
                d,s=mapping[d],mapping[s]
                if op==1:values[d]^=values[s]
                elif op==2:need(values[d]==0,'Boolean fresh COPY');values[d]=values[s]
                else:need(values[d]==values[s],'Boolean exact ERASE');values[d]=0
        elif event['kind']=='bridge':
            a,b=event['dst'],event['src']
            for d,s in ((2*a,2*b),(2*b+1,2*a+1)):
                if bridges!=skip:
                    for j in range(v):values[d*v+j]^=values[s*v+j]
                bridges+=1
        else:
            for p in range(4):
                a,b=2*p*v,(2*p+1)*v
                values[a:a+v],values[b:b+v]=values[b:b+v],values[a:a+v]
    return values==[1<<i for i in range(n)]+[0]

def run():
    pins=read(HERE/'SOURCES.json');check_sources(pins)
    w=json.loads(gzip.decompress((ROOT/WORD).read_bytes()));v,r=w['v'],w['R']
    need((v,r)==(111,439),'selected local dimensions')
    events=stream(w);exported=exported_stream(events)
    need(recipe()==source_recipe(),'independent schedule equals consumed source recipe')
    # Adapter edits have no precision or recipe replacement.
    adapt=ast.parse((ROOT/ADAPT).read_text(encoding='utf-8'))
    edits=next(node.value for node in adapt.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EDITS' for t in node.targets))
    pairs=next(value for key,value in zip(edits.keys,edits.values) if isinstance(key,ast.Constant) and key.value=='global_k.py').elts[1].elts
    anchors=[pair.elts[0].value for pair in pairs]
    need(not any(any(token in anchor for token in ('prefix=','def recipe','cf=','cb=')) for anchor in anchors),'adapter preserves bound and recipe')
    models=[local_model(events,v,r),local_model(reverse(events),v,r)]
    f,b=[m['bound'] for m in models];need((f,b)==(49347,1113070),'selected local prefix bounds')
    receipt=replay(events,models,v,r)
    expected=read(ROOT/EXPECTED)
    need(int(receipt['coarse_prefix'])==source_bound(f,b)==(1<<18)*f**5*b**4,'exact consumed product formula')
    need(receipt['coarse_bits']==177 and expected['nine']['bit']['charged_prefix_bits']==192,'selected precision context')
    need(boolean_endpoint(events,v,r),'all arbitrary Boolean columns restored')
    controls=[]
    def reject(label,fn):
        try:fn()
        except ValueError:controls.append(label)
        else:raise ValueError('control was not rejected: '+label)
    reject('identity endpoint implies unit prefix',lambda:need(int(receipt['exact_positive_prefix'])<=1,'false precision shortcut'))
    reject('local maximum bounds entire schedule',lambda:need(int(receipt['exact_positive_prefix'])<=max(f,b),'missing composition'))
    dirtless=replay(events,models,v,r,zero_helpers=True)
    reject('zero helper inputs preserve arbitrary-dirt bound',lambda:need(dirtless['exact_positive_prefix']==receipt['exact_positive_prefix'],'helper dirt matters'))
    for omitted in range(18):reject('omit bridge '+str(omitted),lambda k=omitted:need(boolean_endpoint(events,v,r,k),'full formal columns'))
    bad=copy.deepcopy(pins);bad['files'].pop(EXPORT)
    reject('removed consumed source pin',lambda:check_sources(bad))
    bad=copy.deepcopy(pins);bad['files'][WORD]='0'*64
    reject('changed source digest',lambda:check_sources(bad))
    return {'status':'PASS_NINE_STAGE_PREFIX_AUDIT_S70','seed':70,'base_commit':BASE,'sources':pins,
            'exported_records':exported,'local_bounds':{'forward':f,'reverse':b},'schedule':recipe(),
            'audit':receipt,'zero_helpers':dirtless['exact_positive_prefix'],'negative_controls':controls,
            'selected_charged_bits':192,'scope':'Finite unbanked scalar schedule; physical cover/compiler/hosting and production precision remain inherited, not readmitted.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if args.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    else:need(canonical(result)==canonical(read(path)),'complete deterministic certificate comparison')
    a=result['audit']
    print('PASS_NINE_STAGE_PREFIX_AUDIT_S70 exact_bits=%s envelope_bits=%s coarse_bits=%s controls=%s'%(a['exact_bits'],a['bank_envelope_bits'],a['coarse_bits'],len(result['negative_controls'])))

if __name__=='__main__':main()
