#!/usr/bin/env python3
"""Independent original-method lifetime oracle. No author lifetime code imports.

Pending owners are registered before consuming list inputs. Scalar arithmetic
is abstracted; this is ownership evidence, not numerical verification.
Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
from math import prod
import weakref

PINS={'product.py':'29ab6c60f937b7cce58666f5ddd7a921c3197cf72abf91ecca0ff7ad9486850e',
      'tensor_word.py':'36c5a9a0082c9aa3c6cb2d04a9196af8debce0d551a0525975b710018ea02cac'}

def require(ok,message):
    if not ok:raise ValueError(message)

class Census:
    def __init__(self):
        self.live=weakref.WeakSet();self.serial=0;self.peak=0;self.events=[];self.native=[]
    def record(self,kind,owner=None):
        ids=sorted(x.ident for x in self.live)
        self.peak=max(self.peak,len(ids));self.events.append((kind,owner,ids))
    def allocate(self,values=(),label='explicit-list'):
        census=self
        class Field(list):
            __hash__=object.__hash__
            def __init__(self):
                super().__init__();self.ident=census.serial;census.serial+=1
                census.live.add(self);census.record('allocate:'+label,self.ident)
            def __del__(self):
                census.live.discard(self);census.record('retire',self.ident)
        out=Field();out.extend(values);return out
    def h(self,data,target):
        require(data in self.live,'native active owner missing')
        self.native.append((len(self.live),data.ident,tuple(target)))
        for i,(a,b) in enumerate(data):data[i]=(a+b,a-b)

class TrackAllocations(ast.NodeTransformer):
    def __init__(self,label):self.label=label;self.sites=[]
    def visit_ListComp(self,node):
        self.generic_visit(node);label=self.label+':'+str(node.lineno);self.sites.append(label)
        generator=ast.GeneratorExp(elt=node.elt,generators=node.generators)
        return ast.copy_location(ast.Call(func=ast.Name(id='allocate',ctx=ast.Load()),
                  args=[generator,ast.Constant(label)],keywords=[]),node)
    def visit_Call(self,node):
        self.generic_visit(node)
        if isinstance(node.func,ast.Name) and node.func.id=='list':
            label=self.label+':'+str(node.lineno);self.sites.append(label)
            node.func=ast.Name(id='allocate',ctx=ast.Load());node.args.append(ast.Constant(label))
        return node

def method(path,owner,name,census):
    raw=path.read_bytes();require(sha256(raw).hexdigest()==PINS[path.name],'source hash '+path.name)
    cls=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef) and n.name==owner)
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    tracker=TrackAllocations(owner+'.'+name);fn=tracker.visit(fn);ast.fix_missing_locations(fn)
    namespace={'allocate':census.allocate,'hadamard':census.h,'prod':prod,
               'product_diagonal':lambda data,tables,grid:None}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path),'exec'),namespace)
    return namespace[name],tracker.sites

def experiment(source,size,stages,retain_roots=True,alias_inputs=False):
    c=Census();apply,sites1=method(source/'tensor_word.py','TensorWord','apply',c)
    convolution,sites2=method(source/'product.py','Multiplier','convolution_grid',c)
    Word=type('Word',(),{'apply':apply});word=Word()
    word.sides=(size,);word.entrance=word.exit=();word.grid=None
    word.jobs=[[([], (1,)),([], ())] for _ in range(stages)]
    Machine=type('Machine',(),{'convolution_grid':convolution,
          'public':lambda self,x:x,'public_product':lambda self,x,y:(x[0]*y[0],x[1]*y[1])})
    machine=Machine();machine.transform=word
    a=c.allocate(((i+1,-i) for i in range(size)),'root-a')
    b=a if alias_inputs else c.allocate(((2*i,1) for i in range(size)),'root-b')
    before_a,before_b=tuple(a),tuple(b)
    if retain_roots:
        result=machine.convolution_grid(a,b)
        require(tuple(a)==before_a and tuple(b)==before_b,'root operand mutated')
    else:
        del a,b
        result=machine.convolution_grid(c.allocate(before_a,'ephemeral-a'),c.allocate(before_b,'ephemeral-b'))
    require(len(result)==size,'complete output length')
    native_counts=[row[0] for row in c.native];per_transform=2*stages
    if retain_roots and not alias_inputs:
        require(c.peak==7,'source convolution peak is not seven')
        require(native_counts==[3]*per_transform+[4]*per_transform+[6]*per_transform,
                'native-cut owner counts')
        require(len(c.live)==3,'expected two roots and returned field')
    return {'size':size,'stages':stages,'peak':c.peak,'native':native_counts,
            'allocation_sites':sorted(sites1+sites2),'owner_allocations':c.serial}

def run(source):
    cases=[experiment(source,n,stages) for n in (2,4,8) for stages in (0,1,2,7,16)]
    missing=experiment(source,4,2,retain_roots=False);alias=experiment(source,4,2,alias_inputs=True)
    require(missing['native']!=[3]*4+[4]*4+[6]*4,'unretained-root control invisible')
    require(alias['peak']<7,'aliasing contract control invisible')
    return {'status':'PASS_INDEPENDENT_SOURCE_FIELD_LIFETIMES','cases':cases,
            'controls':{'missing_caller_roots':missing,'aliased_inputs':alias},
            'scope':'Full-field owners during convolution/native calls only; scalar arithmetic, coefficient tables, native internals and later integer recovery excluded.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path)
    print(json.dumps(run(p.parse_args().source),indent=2,sort_keys=True))
