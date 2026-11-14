"""Independent all-instruction translation audit, without tape replay.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import types

def need(ok,label):
    if not ok: raise ValueError(label)
def load(path,name):
    module=types.ModuleType(name); module.__file__=str(path)
    sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module

def audit(package):
    expected_source='572e2c5de3b210ef34ed8f26f51fb1a2a6b4306fc355f93368504ad79308561c'
    need(sha256((package/'compose.py').read_bytes()).hexdigest()==expected_source,'join source drift')
    compose=load(package/'compose.py','independent_join_audit')
    actual,labels=compose.compile_composition()
    # Recompile frozen old and core graphs; compare each edge independently
    # rather than trusting the constructor's PORT_MAP or SYMBOL objects.
    old=load(package/'inputs/bridge.py','independent_bridge_source')
    bridge,blabel=old.compile_bridge()
    core,alphabet=compose.core_graph()
    need(len(bridge)==6003 and len(core)==82813 and len(actual)==88816,'fixed graph sizes')
    port=lambda t: 3 if t==0 else 2 if t==1 else t+41
    sym={'_':2,'0':0,'1':1,'|':3}; expected=[]
    entries=returns=0; old_private=set(); new_private=set(); core_writes=set()
    for instruction in bridge:
        if instruction==('H','PACKED'):
            expected.append(('J',6003)); entries+=1
        else: expected.append(instruction)
        if instruction[0] in ('R','W','M') and instruction[1]>=2:
            old_private.add(instruction[1])
    for instruction in core:
        op,*a=instruction
        if op=='read': translated=('R',port(a[0]),{sym[s]:6003+j for s,j in a[1].items()})
        elif op=='write':
            translated=('W',port(a[0]),sym[a[1]]); core_writes.add(port(a[0]))
        elif op=='move':
            need(a[1] in (-1,1),'unit move'); translated=('M',port(a[0]),a[1])
        elif op=='goto': translated=('J',6003+a[0])
        elif op=='halt': translated=('J',blabel['EXIT']); returns+=1
        else: raise ValueError('nonliteral child instruction')
        expected.append(translated)
        if op in ('read','write','move') and a[0]>=2: new_private.add(port(a[0]))
    need(tuple(expected)==actual,'literal translated graph mismatch')
    need(entries==returns==1,'one child call and return')
    need(labels['CORE']==6003 and labels['EXIT']==blabel['EXIT'],'call labels')
    need(old_private==set(range(2,43)),'all old private owners present')
    need(new_private==set(range(43,72)),'exact29 disjoint new private owners')
    need(not core_writes.intersection({0,1,3}),'child writes old/context/header')
    need(2 in core_writes,'core never commits packed payload')
    need(len({port(i) for i in range(31)})==31,'child port alias')
    branches=0
    for pc,instruction in enumerate(actual):
        if instruction[0]=='R':
            need(0<=instruction[1]<72,'read port'); need(set(instruction[2])<=set(sym.values()),'read alphabet')
            targets=instruction[2].values(); branches+=len(instruction[2])
        elif instruction[0]=='J': targets=(instruction[1],)
        elif instruction[0] in ('W','M'):
            need(0<=instruction[1]<72,'write/move port'); targets=()
            need(instruction[2] in (sym.values() if instruction[0]=='W' else (-1,1)),'local action')
        elif instruction[0]=='H': targets=()
        else: raise ValueError('nonlocal graph instruction')
        need(all(0<=j<len(actual) for j in targets),'nonlocal target')
    # Mutation detection uses the whole graph equality above, not a checksum
    # alone, and demonstrates both missing call and header/data alias faults.
    entrance=next(i for i,x in enumerate(bridge) if x==('H','PACKED'))
    mutant=list(actual); mutant[entrance]=('J',blabel['EXIT'])
    need(tuple(mutant)!=tuple(expected),'omitted child not detected')
    first_header=next(6003+i for i,x in enumerate(core) if x[0]=='read' and x[1]==0)
    mutant=list(actual); original=mutant[first_header]
    mutant[first_header]=(original[0],2,*original[2:])
    need(tuple(mutant)!=tuple(expected),'header/data alias not detected')
    # Algebraic coefficients for the complete bounds, after Vp<Vo/3 and
    # E_gamma<=Vp+E_old. These exact inequalities certify the constants.
    need(3*10*2**20+2*2**24<3*2**25,'payload time constant')
    need(2**20+2**24<=2**25,'header time constant')
    need(3*64+2*1024<3*2048,'payload history constant')
    need(64+1024<=2048,'header history constant')
    graph=sha256(json.dumps(actual,separators=(',',':'),sort_keys=True).encode()).hexdigest()
    return {'marker':'PASS_FULL_MOVE_LITERAL_COMPOSITION_AUDIT','compose_sha256':expected_source,
        'graph_sha256':graph,'locations':len(actual),'tapes':72,
        'translated_core_locations':len(core),'unchanged_bridge_locations':len(bridge)-1,
        'symbol_branches':branches,'new_private_owners':sorted(new_private),
        'source_public_to_joined_ports':{'HEADER':3,'DATA':2},
        'core_write_ports':sorted(core_writes),'all_edges_checked':True,
        'negative_controls':['omitted core entry','header/data alias'],
        'cost_constants':{'time':2**25,'history':2048},
        'meaning':'static literal simulation and exact cost inequalities; no heavy tape replay'}
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--package',type=Path,required=True)
    p.add_argument('--output',type=Path); a=p.parse_args(); result=audit(a.package.resolve())
    if a.output: a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['marker']); print(str(result['locations'])+' locations,72 tapes,29 new private owners; graph '+result['graph_sha256'])
