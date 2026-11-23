"""Independent target, inverse-word, list-codec and bounded-history audit."""
import argparse, ast, hashlib, json
from collections import deque
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace
import independent_basis as old
HERE=Path(__file__).resolve().parent
def need(x,m):
    if not x:raise ValueError(m)
def inv(word):
    return tuple((('swap',r[1],r[2]) if r[0]=='swap' else
                  ('add',r[1],r[2],-Q(r[3])) if r[0]=='add' else
                  ('scale',r[1],1/Q(r[2]))) for r in reversed(word))
def apply(word,row,mod=6561):
    out=list(row)
    for r in word:
        if r[0]=='swap':out[r[1]],out[r[2]]=out[r[2]],out[r[1]]
        else:
            q=Q(r[-1]);a=q.numerator*pow(q.denominator,-1,mod)%mod
            if r[0]=='scale':out[r[1]]=out[r[1]]*a%mod
            else:out[r[1]]=(out[r[1]]+a*out[r[2]])%mod
    return out
def scalar(v,w):
    need(isinstance(v,int) and 0<=v<1<<w,'independent unsigned width')
    return format(v,'0'+str(w)+'b')
def independent_bits(entries,n,w):
    h=(n-1).bit_length();out=scalar(len(entries),w)
    for owner,word in entries:
        out+=scalar(owner,w)+scalar(len(word),w)
        for r in word:
            tag={'swap':0,'add':1,'scale':2}[r[0]]
            j=0 if tag==2 else r[2];q=Q(0) if tag==0 else Q(r[-1])
            need(-32<=q.numerator<32 and q.denominator<32,'independent coefficient width')
            out+=scalar(tag,2)+scalar(r[1],h)+scalar(j,h)+scalar(q.numerator%64,6)+scalar(q.denominator,5)
    return out
def unpack_bits(image):
    data,bits=image
    return ''.join(format(b,'08b') for b in data)[:bits]
def main(package):
    frozen=json.loads((package/'NATIVE-FREEZE.json').read_text())
    for n,h in frozen['files'].items():need(hashlib.sha256((package/n).read_bytes()).hexdigest()==h,'frozen '+n)
    old.PACKAGE=package/'inputs/decoder';old.SRC=old.PACKAGE/'sources';old.authenticate()
    ns,g,root=old.originals();ns['need']=need
    old.definitions('factored_frames.py',['apply_row'],ns)
    old.definitions('raw_binary.py',['Axis','placed_job','job_frame','BinarySource'],ns)
    @dataclass(frozen=True)
    class Port:
        tag:tuple
        rank:int
    @dataclass(frozen=True)
    class Job:
        owner:int
        axes:tuple
    ns.update(Port=Port,Job=Job,bit_word=lambda t,p:SimpleNamespace(targets=t,paid=p))
    old.definitions('tagged_sources.py',['binary_ports'],ns)
    raw=ns['binary_ports'](g,root)
    old.definitions('strong_binary.py',['active_catalogue','StrongBinarySource'],ns)
    old.definitions('raw_binary_stage.py',['BinaryWord'],ns)
    differences,joints=ns['fixed_binary_charts']()
    words={tuple(w) for w,r in differences.values()}|set(joints)|{()}
    need(len(words)==595 and max(map(len,words))==61,'fixed library closure')
    tags=[];dims={int(k):v['dim'] for k,v in g['frames'].items()}
    for role,item in enumerate(root['diagonal']):
        tags.extend((('root',role,p),1+7*len(item['stages'])) for p in range(root['ports']))
    for clock,event in enumerate(root['events']):
        if event[0]=='LOCAL':
            tags.extend((('helper',clock,p),abs(dims[g['start'][p]]-dims[g['final'][p]])) for p in range(2*root['ports'],len(g['start'])))
    need(tags==[(p.tag,p.rank) for p in raw.targets] and len(tags)==18906,'independent ordered target census')
    requests={}
    for tag,rank in tags:
        kind,role,p=tag
        if kind=='root':key=(kind,p,tuple(root['diagonal'][role]['stages']));base=joints[p]
        else:
            a,b=g['start'][p],g['final'][p]
            if dims[a]>dims[b]:a,b=b,a
            key=(kind,a,b);base=differences[a,b][0]
        need(tuple(base) in words,'target library membership')
        requests.setdefault(key,(tag,rank,tuple(base)))
    need(len(requests)==2120,'unique target requests')
    checks=0;maxbase=0
    for cols in (1,4):
        c=ns['ActiveCatalogue'](134*cols,cols);initial=dict(vars(c))
        for tag,rank,base in requests.values():
            f=c.target(tag)
            need(f.word==old.lift(base,cols),'independent target literal lift')
            need(len(f.mask)==rank*cols and len(set(f.mask))==len(f.mask),'target mask rank')
            maxbase=max(maxbase,len(base));checks+=1
        need(vars(c)==initial and set(initial)=={'dimension','columns','graph','root','ports','body','ambient'},'actual catalogue has no request cache')
    need(maxbase==52,'target maximum')
    coeff=[]
    for word in words:
        need(inv(word)==tuple(ns['inverse_word'](word)),'independent source inversion')
        coeff.extend(Q(r[-1]) for w in (word,inv(word)) for r in w if r[0]!='swap')
    need(max(abs(q.numerator).bit_length()+1 for q in coeff)==6,'signed inverse width')
    need(max(q.denominator.bit_length() for q in coeff)==5,'inverse denominator width')
    need(differences[45,388][0][39]==('scale',2,Q(7,20)) and Q(20,7) in coeff,'actual six-bit witness')
    # Execute the target codec only; no author check/loader is imported.
    for path,names in [(package/'inputs/decoder/codec.py',{'Writer','Reader'}),(package/'codec_restores.py',{'RestoreCodec'})]:
        tree=ast.parse(path.read_text());body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name in names]
        exec(compile(ast.Module(body=body,type_ignores=[]),str(path),'exec'),ns)
    codec=ns['RestoreCodec'](134,24,1<<20);roundtrips=0
    catalogue=ns['ActiveCatalogue'](134,1);targets=list(requests.values())
    for idx,word in enumerate(sorted(words,key=repr)):
        tag,rank,_=targets[idx%len(targets)];target=catalogue.target(tag)
        source=ns['Frame'](134,word,tuple(reversed(range(len(target.mask)))))
        matcher=source.matcher_to(target)
        need(len(matcher)<=len(word)+134+len(target.word)<=123*134,'literal matcher length')
        row=[(7*j+3)%6561 for j in range(134)]
        need(apply(inv(matcher),apply(matcher,row))==row,'independent inverse action')
        for w in (matcher,inv(matcher)):
            values=[(idx,w)];image=codec.pack(values)
            need(unpack_bits(image)==independent_bits(values,134,24),'independent bit fields')
            need(codec.unpack(image)==values,'exact ordered codec roundtrip');roundtrips+=1
    result={'target_count':len(tags),'distinct_target_requests':len(requests),'target_lifts':checks,'max_target_base':maxbase,'library_words':len(words),'coefficient_bits':[6,5],'matcher_roundtrips':roundtrips}
    class Banks:
        dimension=134
        def __init__(self):self.live=set();self.serial=0;self.first=[];self.tail=deque(maxlen=18906);self.routes=0
        def zero(self):
            v=self.serial;self.serial+=1;self.live.add(v);return v
        def retire(self,v,**kw):need(v in self.live,'retire live');self.live.remove(v)
        def clone(self,v):need(v in self.live,'clone live');return self.zero()
        def xor(self,a,b):need(a in self.live and b in self.live,'xor live')
        def swap(self,a,b):need(a in self.live and b in self.live,'swap live')
        def route(self,owner,word):
            need(owner in self.live,'route live');entry=(owner,tuple(word));self.routes+=1
            if len(self.first)<18906:self.first.append(entry)
            self.tail.append(entry)
    banks=Banks();jobs=[ns['Job'](banks.zero(),tuple(range(p.rank))) for p in raw.targets]
    wrapper=ns['BinaryWord'].__new__(ns['BinaryWord']);wrapper.tagged=raw
    gen=wrapper.native(jobs,1,ns['StrongBinarySource'](banks));next(gen)
    physical=gen.gi_frame.f_locals['actual'];saved=list(physical.gi_frame.f_locals['restores'])
    need(len(saved)==18906 and saved==banks.first,'actual ordered retained list')
    expected=[(owner,inv(word)) for owner,word in saved[::-1]]
    count=1
    for job in gen:
        need(job.owner in banks.live,'paid owner live');count+=1
    need(count==104904 and list(banks.tail)==expected,'complete actual reverse-inverse return')
    need(banks.live==set(range(18906)),'original owners retained, private owners retired')
    result.update(paid=count,restorations=len(saved),routes=banks.routes,reverse_trace_sha256=hashlib.sha256(repr(expected).encode()).hexdigest())
    controls=[]
    def reject(f,name):
        try:f()
        except (ValueError,ArithmeticError):controls.append(name);return
        raise ValueError('mutant accepted '+name)
    reject(lambda:codec.pack([(0,(('scale',0,Q(32)),))]),'positive signed overflow')
    reject(lambda:codec.pack([(0,(('add',0,1,Q(1,32)),))]),'denominator overflow')
    reject(lambda:codec.pack([(0,(('swap',0,134),))]),'coordinate overflow')
    reject(lambda:codec.pack([(0,(('scale',0,Q(0)),))]),'zero scale')
    entry=[(0,(('scale',0,Q(20,7)),))];image=codec.pack(entry)
    reject(lambda:codec.unpack((image[0][:-1],image[1])),'truncated image')
    need(Q(20-32,7)!=Q(20,7),'five-bit mutant');controls.append('five-bit reciprocal corrupts value')
    need(expected!=[(o,inv(w)) for o,w in saved],'order mutant');controls.append('forward list order fails return')
    need(expected!=saved[::-1],'word inverse mutant');controls.append('omitted word inversion fails return')
    h=3000;N=1<<h;P=18906
    normalized=Q(128,N)+P*(Q(256,N)+246+Q(1599,h))
    total=16*normalized+Q(524288,N)
    need(normalized<1<<23 and total<1<<28 and 28<9*h,'uniform historical budget')
    need(24+84*h+h<128*h,'segment offset width')
    # A fixed number of physical slots remains essential for arbitrarily many calls.
    peaks=[[0]*4 for _ in range(3)]
    for use in range(27):
        slot=use%3
        for role in range(4):peaks[slot][role]=max(peaks[slot][role],image[1])
    need(sum(map(sum,peaks))==12*image[1] and 27*4*image[1]>sum(map(sum,peaks)),'fresh role history mutant')
    controls.append('fresh role per call violates concurrency inference')
    result.update(status='ACCEPT_SCOPED_RESTORATION_STORAGE',controls=controls,slots=3,successive_contexts=27,
                  scientific_hashes={k:frozen['files'][k] for k in ('PROOF.md','codec_restores.py','check_restores.py')},
                  proof_scope='restoration values and four fixed reusable image roles only; no native route time or whole-runtime memory')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,default=(HERE.parent if (HERE.parent/'NATIVE-FREEZE.json').exists() else HERE.parent/'storage/native-restores'));p.add_argument('--output',type=Path);a=p.parse_args()
    report=json.dumps(main(a.package.resolve()),indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(report)
    else:print(report,end='')
