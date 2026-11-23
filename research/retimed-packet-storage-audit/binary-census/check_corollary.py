#!/usr/bin/env python3
"""Source-bound exact arithmetic for the separate binary capacity corollary."""
import ast
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
def require(ok,message):
    if not ok: raise AssertionError(message)
bindings=json.loads((ROOT/'COROLLARY-BINDINGS.json').read_text())
for path,row in bindings['files'].items():
    require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==row['sha256'],'dependency hash '+path)
source_bindings=json.loads((ROOT/'SOURCE-BINDINGS.json').read_text())
for path,row in source_bindings['files'].items():
    require(hashlib.sha256((ROOT/'sources'/path).read_bytes()).hexdigest()==row['sha256'],'source hash '+path)
def definitions(path,names,ns):
    tree=ast.parse((ROOT/path).read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
    require({n.name for n in nodes}==set(names),'definition selection')
    for n in nodes:
        n.decorator_list=[d for d in n.decorator_list if not(isinstance(d,ast.Name) and d.id=='cache')]
    exec(compile(ast.Module(nodes,type_ignores=[]),path,'exec'),ns)

ns={'dataclass':dataclass}
definitions('dependencies/powered.py',['Port','PoweredWord','bit_word'],ns)
definitions('sources/tagged_sources.py',['binary_ports'],ns)
graph=json.loads((ROOT/'sources/graph.json').read_text())
caller=json.loads((ROOT/'sources/caller.json').read_text())
word=ns['binary_ports'](graph,caller)
q=len(word.paid)
require((word.ambient,len(word.targets),q,max(x.rank for x in word.targets),min(x.rank for x in word.paid))==(134,18906,104904,127,1),'production grades')
constant_tree=ast.parse((ROOT/'dependencies/installations.py').read_text())
constant=next(n for n in constant_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BINARY_C' for t in n.targets))
constant_ns={'Q':F}
exec(compile(ast.Module([constant],type_ignores=[]),'installations.py','exec'),constant_ns)
trial=constant_ns['BINARY_C']; t=1-trial
require(t==F(1148436507037532395,1152921504606846976) and t>F(3,4),'binary exponent')
mass_binding=json.loads((ROOT/'dependencies/mass-PRODUCTION-BINDING.json').read_text())['binary']
require(mass_binding=={'ambient':134,'target_max':127,'paid_min':'1','targets':18906,'paid':104904,'d':60,'t':str(t)},'accepted mass geometry binding')

def capture_plan(*args,**kwargs): return args,kwargs
transport_ns={'F':F,'Plan':capture_plan}
definitions('sources/transport.py',['Recipe'],transport_ns)
Recipe=transport_ns['Recipe']
stage_ns={'Recipe':Recipe,'BINARY_C':trial,'binary_word':lambda:SimpleNamespace(tagged=word,targets=tuple(x.rank for x in word.targets),paid=tuple(x.rank for x in word.paid),cells={})}
definitions('sources/raw_binary_stage.py',['binary_recipe'],stage_ns)
captured=[]
for h in (1024,3000,5610,9100):
    recipe=stage_ns['binary_recipe'](h)
    args,kwargs=recipe.open()
    n,targets,paid,cells,exponent,lower,upper,volume,ticks,rounds=args
    require(n==1<<h and exponent==t and lower==32768,'actual Recipe arguments')
    require(upper==2*(n//(2048*134)) and lower<upper<n,'actual upper endpoint')
    require(volume==n**6 and ticks==n**82 and rounds==n**2,'actual production powers')
    require(kwargs['width']==n**92 and kwargs['delay_base']==1<<19,'actual width/delay base')
    require(q+1<n and 2*n<=n**6 and 16<9*h,'production slack')
    captured.append({'height':h,'lower':lower,'ambient':word.ambient,'delay_base':kwargs['delay_base'],'q_plus_one_below_n':True,'capacity_exponent_slack':9*h-16})

# Extract the exact loop defining delay and count from Plan.__init__.
tree=ast.parse((ROOT/'sources/transport.py').read_text())
plan=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Plan')
init=next(n for n in plan.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
level_assign=next(n for n in init.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Tuple) and [a.id for a in n.targets[0].elts if isinstance(a,ast.Name)]==['level','limit'])
level_loop=next(n for n in init.body if isinstance(n,ast.For) and isinstance(n.body[0],ast.While))
code=compile(ast.Module([level_assign,level_loop],type_ignores=[]),'transport-level-loop','exec')
class ToyMeasure:
    def mass(self,left,right): return F(0),F(3*left+1,7)
loop_cases=0
for lower,upper in ((10,100),(16,256),(32768,65540)):
    holder=SimpleNamespace(bands=range(lower,upper,2),delay={},count={})
    scope={'F':F,'lower':lower,'self':holder,'scale_step':F(6,5),'delay_base':1<<19,
           'measure':ToyMeasure(),'ceil':lambda x:-(-x.numerator//x.denominator)}
    exec(code,scope)
    for e,delay in holder.delay.items():
        exponent=(delay.bit_length()-1)//19
        require(delay==1<<(19*exponent),'delay exact power')
        require(F(lower)*F(6,5)**exponent<=e<F(lower)*F(6,5)**(exponent+1),'source level brackets band')
        require(F(delay)<=F(e,lower)**76,'delay envelope')
        require(holder.count[e]==(3*e+7)//7,'actual count uses upper ceiling')
        loop_cases+=1

require(6**76>2**19*5**76,'delay exponent integer certificate')
require(22339<2**15,'owner coefficient certificate')
require(32768>=16 and t>F(1,2),'mass coefficient below one')
controls=[]
def reject(name,fn):
    try: fn()
    except (AssertionError,ValueError): controls.append(name)
    else: raise AssertionError('accepted control '+name)
reject('insufficient delay exponent72',lambda:require(6**72>2**19*5**72,'delay exponent'))
reject('reversed delay inequality',lambda:require(6**76<2**19*5**76,'reversed bound'))
reject('tiny height has no q slack',lambda:require(q+1<2**16,'q slack'))
reject('Recipe rejects height below1024',lambda:stage_ns['binary_recipe'](1023))
result={'status':'PASS','source_commit':bindings['scientific_source_commit'],
        'mass_publication':bindings['publication_commit'],'dependency_files':len(bindings['files']),
        'binary_exponent':str(t),'captured_production_arguments':captured,
        'literal_level_count_cases':loop_cases,'negative_controls':controls,
        'exact_delay_margin':str(6**76-2**19*5**76),
        'capacity_statement':'capacity <= B+22339*C_* < 2B; N=2^h,h>=3000; fresh local binary allocator',
        'scope':'Analytic inequalities with exact accepted mass dependency. No production calendar execution, supplier admission or selected-premise discharge.'}
print(json.dumps(result,indent=2,sort_keys=True))
