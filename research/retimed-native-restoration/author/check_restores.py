#!/usr/bin/env python3
"""Source-bound restoration census, codec and complete native-return replay."""
import argparse
import ast
from collections import deque
from fractions import Fraction
from hashlib import sha256
from itertools import chain
import json
from pathlib import Path
import sys
PARSER=argparse.ArgumentParser();PARSER.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);PARSER.add_argument('--output',type=Path)
ARGS=PARSER.parse_args() if __name__=='__main__' else PARSER.parse_args([])
PACKAGE=ARGS.package.resolve()
sys.path.insert(0,str(PACKAGE));sys.path.insert(0,str(PACKAGE/'inputs/decoder'))
from source_loader import authenticate,extract,library,load,need,SRC
from codec import Writer
from codec_restores import RestoreCodec


def fingerprint(codec,word):
    data,bits=codec.word_image(word)
    return sha256(bits.to_bytes(8,'big')+data).hexdigest()


def target_census():
    ns=load();raw=ns['raw_word'];g=ns['graph']();root=ns['caller']();words=library()[0]
    differences,joints=ns['fixed_binary_charts']();requests={}
    for port in raw.targets:
        kind,role,index=port.tag
        if kind=='root':key=(kind,index,tuple(root['diagonal'][role]['stages']));base=joints[index]
        else:
            need(kind=='helper','target role')
            first,last=g['start'][index],g['final'][index]
            if g['frames'][str(first)]['dim']>g['frames'][str(last)]['dim']:first,last=last,first
            key=(kind,first,last);base=differences[first,last][0]
        need(tuple(base) in words,'target basis belongs to complete library')
        previous=requests.setdefault(key,(port,tuple(base)))
        need(previous[0].rank==port.rank and previous[1]==tuple(base),'target request rank agreement')
    checks=0;largest=0
    for columns in (1,2,5):
        c=ns['ActiveCatalogue'](134*columns,columns);keys=set(vars(c))
        need(keys=={'dimension','columns','graph','root','ports','body','ambient'},'actual ActiveCatalogue fields')
        for port,base in requests.values():
            target=c.target(port.tag)
            need(len(target.word)==len(base)*columns<=61*columns,'target literal lift size')
            need(len(target.mask)==port.rank*columns,'target literal rank')
            need(len(set(target.mask))==len(target.mask) and all(0<=i<c.dimension for i in target.mask),'target ordered mask')
            largest=max(largest,len(base));checks+=1
        need(set(vars(c))==keys,'no growing per-instance cache')
    tree=ast.parse((SRC/'strong_binary.py').read_text())
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ActiveCatalogue')
    init=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__')
    for call in [x for x in ast.walk(init) if isinstance(x,ast.Call)]:
        need(not(isinstance(call.func,ast.Name) and call.func.id in ('super','cache','setattr')),'no inherited cache initializer')
        need(not(isinstance(call.func,ast.Attribute) and call.func.attr=='__init__'),'no parent initializer')
    coefficients=[Fraction(item[-1]) for word in chain(words,(tuple(ns['inverse_word'](word)) for word in words)) for item in word if item[0] in ('add','scale')]
    numerator=max(abs(q.numerator).bit_length()+1 for q in coefficients);denominator=max(q.denominator.bit_length() for q in coefficients)
    need(numerator<=6 and denominator<=5,'complete inverse coefficient bound')
    witness=next(q for q in coefficients if not(-16<=q.numerator<16))
    need(-32<=witness.numerator<32,'actual six-bit signed coefficient witness')
    paid_witness=next(port for port in raw.paid if port.tag==('move',4,830,869))
    need(paid_witness.rank==5 and differences[45,388][0][39]==('scale',2,Fraction(7,20)),'actual paid-family inverse witness')
    return dict(targets=len(raw.targets),distinct_requests=len(requests),lift_checks=checks,maximum_base=largest,
                signed_numerator_bits=numerator,denominator_bits=denominator,
                signed_six_bit_witness=[witness.numerator,witness.denominator],
                paid_inverse_witness={'tag':['move',4,830,869],'rank':5,'pair':[45,388],'operation_index':39,'scale':[7,20]},no_instance_cache=True)


def matcher_roundtrips():
    ns=load();words=library()[0];raw=ns['raw_word'];count=0;maximum_ratio=[0,1]
    for columns in (1,2,5):
        n=134*columns;catalogue=ns['ActiveCatalogue'](n,columns);codec=RestoreCodec(n,20,2**20-1)
        for index,base in enumerate(words):
            port=raw.targets[index%len(raw.targets)];target=catalogue.target(port.tag)
            source_word=tuple(op for item in base for j in range(2*columns)
                              for op in ns['coordinate_word']((item,),lambda k,j=j:k*(2*columns)+j))
            source=ns['Frame'](n,source_word,tuple(reversed(range(len(target.mask)))))
            matcher=source.matcher_to(target)
            need(len(matcher)<=len(source.word)+n+len(target.word)<=123*n,'literal matcher length')
            inverse=tuple(ns['inverse_word'](matcher));image=codec.pack([(index,matcher)])
            need(codec.unpack(image)==[(index,matcher)],'ordered matcher roundtrip')
            need(codec.unpack(codec.pack([(index,inverse)]))==[(index,inverse)],'inverse matcher roundtrip')
            if len(matcher)*maximum_ratio[1]>maximum_ratio[0]*n:maximum_ratio=[len(matcher),n]
            count+=2
    return dict(roundtrips=count,maximum_observed_length_over_n=maximum_ratio)


def actual_native_replay():
    ns=load();raw=ns['raw_word'];n=134;P=len(raw.targets);codec=RestoreCodec(n,24,2**24-1)
    class Banks:
        dimension=n
        def __init__(self):self.live=set();self.next=0;self.routes=0;self.first=[];self.last=deque(maxlen=P)
        def zero(self):
            owner=self.next;self.next+=1;self.live.add(owner);return owner
        def retire(self,owner,**kwargs):need(owner in self.live,'retire owner');self.live.remove(owner)
        def clone(self,owner):need(owner in self.live,'clone owner');return self.zero()
        def route(self,owner,word):
            need(owner in self.live,'route owner');record=(owner,fingerprint(codec,word));self.routes+=1
            if len(self.first)<P:self.first.append(record)
            self.last.append(record)
        def xor(self,left,right):need(left in self.live and right in self.live,'xor owners')
        def swap(self,left,right):need(left in self.live and right in self.live,'swap owners')
    banks=Banks();jobs=[ns['Job'](banks.zero(),tuple(range(port.rank))) for port in raw.targets]
    extract('raw_binary_stage.py',['BinaryWord'],ns)
    wrapper=ns['BinaryWord'].__new__(ns['BinaryWord']);wrapper.tagged=raw
    native=wrapper.native(jobs,1,ns['StrongBinarySource'](banks));first=next(native)
    wrapper_locals=native.gi_frame.f_locals;physical=wrapper_locals['actual'];locals_=physical.gi_frame.f_locals
    restores=locals_['restores'];need(len(restores)==P,'actual P saved restorations')
    need(wrapper_locals['entries'] is locals_['inputs'],'actual wrapper passes same entry list')
    need(all(entry[1] is job for entry,job in zip(wrapper_locals['entries'],jobs,strict=True)),'wrapper preserves input Job references')
    need(len(locals_['active'])==P,'actual active target count')
    image=codec.pack(restores);restored=codec.unpack(image);need(restored==restores,'full retained native list roundtrip')
    need(banks.first==[(owner,fingerprint(codec,word)) for owner,word in restores],'initial ordered matcher routes')
    expected=[(owner,fingerprint(codec,tuple(ns['inverse_word'](word)))) for owner,word in reversed(restores)]
    max_length=max(len(word) for _,word in restores);need(max_length<=123*n,'actual retained word bound')
    count=0
    for job,port in zip(chain((first,),native),raw.paid,strict=True):
        need(len(job.axes)==port.rank and job.owner in banks.live,'actual wrapper paid extent/owner');count+=1
    need(count==104904 and banks.live==set(range(P)),'actual complete native return')
    need(list(banks.last)==expected,'actual reverse inverse restoration sequence')
    return dict(paid=count,restores=P,routes=banks.routes,restoration_bits=image[1],maximum_matcher_operations=max_length,
                reverse_return_sha256=sha256(json.dumps(expected,separators=(',',':')).encode()).hexdigest(),
                wrapper_entry_alias=True,input_job_alias=True,scope='Unchanged wrapper/raw/inner metadata; numerical bank payloads abstracted.')


def controls():
    ns=load();codec=RestoreCodec(8,20,100,ports=3);word=(('add',0,1,Fraction(1)),('add',1,0,Fraction(1)))
    values=[(3,word),(7,tuple(ns['inverse_word'](word)))];image=codec.pack(values);names=[]
    def reject(action,name):
        try:action()
        except (ValueError,ArithmeticError,AssertionError):names.append(name);return
        raise ValueError('negative control accepted: '+name)
    reject(lambda:codec.pack([(-1,word)]),'negative-owner')
    reject(lambda:codec.pack([(1,(('swap',0,8),))]),'coordinate-overflow')
    reject(lambda:codec.pack([(1,(('add',0,1,Fraction(32)),))]),'signed-numerator-overflow')
    reject(lambda:codec.pack([(1,(('add',0,1,Fraction(1,32)),))]),'denominator-overflow')
    reject(lambda:codec.pack([(1,(('scale',0,Fraction(0)),))]),'zero-scale')
    reject(lambda:codec.unpack((image[0][:-1],image[1])),'truncated-image')
    bad=Writer();bad.put(1,20);bad.put(1,20);bad.put(1,20);bad.put(1,2);bad.put(0,3);bad.put(1,3);bad.put(2,6);bad.put(4,5)
    reject(lambda:codec.unpack(bad.finish()),'noncanonical-rational')
    need(codec.pack(list(reversed(values)))!=image,'ordered restoration cannot be sorted/reversed away');names.append('reordered-restorations-change-trace')
    need(codec.pack(values[:-1])!=image,'omitted restoration');names.append('omitted-restoration-changes-return')
    inverse=tuple(ns['inverse_word'](word));row=[1,0,0,0,0,0,0,0]
    need(ns['apply_row'](word,row,3)!=ns['apply_row'](inverse,row,3),'forward route differs from inverse');names.append('forward-word-is-not-restoration')
    decoded_five=20-32
    need(Fraction(decoded_five,7)!=Fraction(20,7),'five-bit signed inverse corrupts exact coefficient')
    names.append('five-bit-source-inverse-changes-value')
    return names


def slot_history_checks():
    codec=RestoreCodec(8,20,100,ports=3);image=codec.pack([(3,(('add',0,1,Fraction(1)),))])
    peaks=[[0]*4 for _ in range(2)];live=set();opened=0
    for _ in range(4):
        for slot in range(2):
            need(slot not in live,'bounded slot admission');live.add(slot);opened+=1
            for role in range(4):peaks[slot][role]=max(peaks[slot][role],image[1])
        before=sum(map(sum,peaks))
        for slot in range(2):live.remove(slot)
        need(sum(map(sum,peaks))==before,'slot role peaks survive clearing')
    bounded=sum(map(sum,peaks));fresh=opened*4*image[1]
    need(bounded==2*4*image[1] and fresh>bounded,'fresh physical roles are not justified by concurrency')
    return dict(slots=2,successive_contexts=opened,roles=8,historical_bits=bounded,
                fresh_identifier_roles_bits=fresh,controls=['fresh-role-per-ident-overruns-concurrency-bound'])


def bounds():
    P=18906;need(370*P+1<2**23,'explicit per-list coefficient')
    h=3000;N=1<<h;B=N**92;w=128*h;C=2*N**83
    L=w+P*(2*w+123*N*(2*h+13));total=8*C*L+2048*C*w
    need(L<2**23*N*h and total<2**28*N**84*h<B*N*h,'inclusive historical list roles')
    need(28<9*h,'all-production ratio cutoff')
    return dict(production_h_min=3000,matcher_operations='<=123N',list_roles_per_context=4,
                historical_bits='<2^28 N^84 h < B N h',all_five_assumptions_retained=True)


def main():
    args=ARGS
    frozen=json.loads((PACKAGE/'NATIVE-FREEZE.json').read_text())
    for name,want in frozen['files'].items():
        need(sha256((PACKAGE/name).read_bytes()).hexdigest()==want,'native scientific hash: '+name)
    original=json.loads((PACKAGE/'inputs/decoder/SCIENTIFIC-FREEZE.json').read_text())
    for name,want in original.items():
        need(sha256((PACKAGE/'inputs/decoder'/name).read_bytes()).hexdigest()==want,'original decoder science: '+name)
    authenticate()
    result=dict(status='PASS_NATIVE_RESTORATION_LISTS',targets=target_census(),matchers=matcher_roundtrips(),
                native=actual_native_replay(),negative_controls=controls(),slot_history=slot_history_checks(),bounds=bounds())
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'targets':result['targets']['targets'],'paid':result['native']['paid'],
                      'matcher_roundtrips':result['matchers']['roundtrips'],'controls':len(result['negative_controls'])},sort_keys=True))

if __name__=='__main__':main()
