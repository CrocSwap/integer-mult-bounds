"""Source-bound execution of the concrete PR2250 repair stage and Lean model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok: raise ValueError(message)


def pins():
    for name,root,key in [('SOURCES.json',ROOT,'path'),('VENDOR.json',HERE,'local_path')]:
        for item in json.loads((HERE/name).read_text(encoding='utf-8'))['files']:
            if name=='SOURCES.json' and item.get('usage')!='input':continue
            raw=(root/item[key]).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==item['sha256'],'source hash: '+item[key])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'source blob: '+item[key])


def load():
    pins()
    modules=[]
    for name in ('streams','compact'):
        spec=importlib.util.spec_from_file_location(name,HERE/'vendor/pr2250'/f'{name}.py')
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        modules.append(module)
    return modules


def extract(qs,bad,key,raw):
    return [(key(q),raw[q]) for q in qs if bad[q]]


def radix(records,width):
    for i in range(width):
        records=[r for r in records if not ((r[0]>>i)&1)]+[r for r in records if (r[0]>>i)&1]
    return records


def fill(qs,bad,records,good):
    out=[];bi=gi=0
    for q in qs:
        if bad[q]:
            if bi==len(records) or records[bi][0]!=q:return None
            out.append(records[bi][1]);bi+=1
        else:
            if gi==len(good):return None
            out.append(good[gi]);gi+=1
    return out if bi==len(records) and gi==len(good) else None


def run():
    streams,compact=load()
    fixtures=[];controls=[]
    for label,K,constant in [('earlier-source',2,False),('constant-mixed-guard',5,True)]:
        fields=(() if constant else (('x',2*K),))+(('u',1),('t',1),('y',2*K),('b',1))
        width=sum(w for _,w in fields)
        layout=compact.Layout(fields,width)
        word=compact.Compact(1,K,1,0,None if constant else 'x','y',False)
        word.validate(layout)
        qs=list(range(layout.records))
        S=[layout.encode(word.execute(layout.decode(q),layout)) for q in qs]
        Sinv=[layout.encode(word.execute(layout.decode(q),layout,True)) for q in qs]
        T=[layout.encode(word.ideal(layout.decode(q))) for q in qs]
        fullT=[layout.encode(word.ideal(layout.decode(q),highest=True)) for q in qs]
        bad=[word.bad(layout.decode(q)) for q in qs]
        for q in qs:
            need(S[Sinv[q]]==Sinv[S[q]]==q,'actual raw inverse')
            need(T[T[q]]==q,'actual ideal inverse')
            need(bad[S[q]]==bad[q],'actual bad-set invariance')
            need(bad[q] or S[q]==T[q],'actual good-set agreement')
        initial=[bytes((q>>i)&1 for i in range(width)) for q in qs]
        raw=[initial[Sinv[q]] for q in qs]
        records=extract(qs,bad,lambda q:T[Sinv[q]],raw)
        sorted_records=radix(records,width)
        good=[raw[q] for q in qs if not bad[q]]
        output=fill(qs,bad,sorted_records,good)
        expected=[initial[T[q]] for q in qs]
        need(output==expected,'Lean-model guarded endpoint')
        meter=streams.Meter(); tape=streams.Tape(meter,b''.join(raw))
        actual=compact.repair(tape,layout,word)
        need(bytes(actual.data)==b''.join(expected),'original physical repair stage')
        need(actual.head==0 and tape.head==0 and not tape.data,'source consumption and output origin')
        full=compact.execute(streams.Tape(streams.Meter(),b''.join(initial)),layout,word)
        need(bytes(full.data)==b''.join(initial[fullT[q]] for q in qs),'complete primitive plus highest bit')
        inverse=compact.execute(full,layout,word)
        need(bytes(inverse.data)==b''.join(initial),'complete primitive second invocation')
        wrong=compact.repair(streams.Tape(streams.Meter(),b''.join(raw)),layout,word,wrong_inverse=True)
        need(bytes(wrong.data)!=b''.join(expected),'wrong inverse accepted-but-wrong witness')
        controls.append(label+':inverse-key-necessary')
        # Keep every key and record count, but break key/payload pairing.
        rotated=[(kv[0],sorted_records[(i+1)%len(sorted_records)][1]) for i,kv in enumerate(sorted_records)]
        need(fill(qs,bad,rotated,good) is not None and fill(qs,bad,rotated,good)!=expected,'whole record preservation necessary')
        controls.append(label+':pair-preservation-necessary')
        corrupted=list(sorted_records);corrupted[0]=(layout.records,corrupted[0][1])
        need(fill(qs,bad,corrupted,good) is None,'wrong destination rejects')
        controls.append(label+':destination-guard')
        need(fill(qs,bad,sorted_records+[(0,b'')],good) is None,'leftover bad records reject')
        need(fill(qs,bad,sorted_records,good+[b'']) is None,'leftover good records reject')
        controls.append(label+':complete-consumption')
        fixtures.append({'label':label,'records':layout.records,'record_bits':width,'bad':sum(bad),'good':len(qs)-sum(bad),'repair_meter':meter.__dict__,'endpoint_sha256':hashlib.sha256(b''.join(expected)).hexdigest()})
    need(fill([0,1],[False,False],[],[1,0])==[1,0],'missing good law countermodel')
    controls.append('good-agreement-necessary')
    need(fill([],[],[],[])==[],'empty completion boundary')
    controls.append('empty-completion')
    return {'fixtures':fixtures,'controls':controls,'kernel_checked_by_this_command':False,
            'scope':'Successful-completion repair refinement only; raw laws and guard success remain premises in the all-size theorem.'}
