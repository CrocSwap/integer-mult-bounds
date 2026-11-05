"""Independent transition-table audit of the source-bound delayed-cover router.

Imports only the finite assembler/producer. The source Machine/Tape interpreter
is not executed: SparseRun below implements its own unit-step semantics.
The all-size result is written in REVIEW.md, not inferred from this grid.
OpenAI Codex assistance. Apache-2.0. Internal author-side review.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys
from types import SimpleNamespace

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/'inputs'/(name+'.py'))
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


class Invalid(ValueError):pass


class SparseRun:
    """Test instrument, never available to an executed instruction."""
    def __init__(self,program,cells,heads):
        self.program=program.instructions;self.cells=[dict(x) for x in cells];self.heads=list(heads)
        self.pc=program.entry;self.steps=0;self.visits=[set() for _ in cells];self.written=[set() for _ in cells]
    def run(self,cap):
        while True:
            need(self.steps<cap,'External test cap')
            instruction=self.program[self.pc];tag=instruction[0];self.steps+=1
            if tag=='halt':return self
            if tag=='reject':raise Invalid(instruction[1])
            if tag=='goto':self.pc=instruction[1];continue
            t=instruction[1];position=self.heads[t];self.visits[t].add(position)
            if tag=='branch':
                value=self.cells[t].get(position,0)
                self.pc=dict(instruction[2]).get(value,instruction[3]);continue
            if tag=='write':
                value=instruction[2];self.written[t].add(position)
                if value:self.cells[t][position]=value
                else:self.cells[t].pop(position,None)
            elif tag=='move':
                need(instruction[2] in (-1,1),'Actual unit move')
                self.heads[t]+=instruction[2];self.visits[t].add(self.heads[t])
            else:raise ValueError('Unsupported finite instruction')
            self.pc+=1


GUARD={-7:6,-3:4,-1:3}


def marked(symbols):
    values=list(symbols)
    return {**GUARD,0:1,**{i+1:v for i,v in enumerate(values)},len(values)+1:2}


def binary(n):return marked(4 if n>>i&1 else 3 for i in range(n.bit_length()))


def c(n):return 24*n-7*n.bit_count()+15*n.bit_length()+12


def ledger(L,A,R,merge):
    V=L*A*R;d=1 if merge else L
    return c(A)+c(R)+18*V+4*A*L+7*A+R+4*L+3*d+33


def space(L,A,R):
    V=L*A*R;a=A.bit_length();r=R.bit_length()
    return 2*V+A+R+a+r+max(a,r)+2*L+12


def sha(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def run():
    snapshot=json.loads((HERE/'SOURCE-SNAPSHOT.json').read_bytes())
    for item in snapshot['files']:
        raw=(HERE/'inputs'/item['path']).read_bytes()
        need(len(raw)==item['bytes'] and sha256(raw).hexdigest()==item['sha256'],'Pinned producer/source bytes')
    machine,counters,router=load('machine'),load('counters'),load('router')
    tables=json.loads((HERE/'inputs/TABLES.json').read_bytes())
    # Source interpreter methods are never called; only Assembler and Program
    # construction are imported. The actual numeric ports remain compile-time.
    shapes=[(1,1),(1,64),(64,1),(2,31),(31,2),(7,9),(9,7),(16,16),(3,4),(4,3)]
    cases=[];compiled={};max_time=(0,1);max_space=(0,1)
    for L in (2,3,5,96):
        for merge in (False,True):
            generated=router.build(L,merge)
            recorded=tables[str(L)]['merge' if merge else 'split']
            need(json.loads(json.dumps(generated.instructions))==recorded,'Full sealed table equals actual build serialization')
            program=SimpleNamespace(instructions=recorded,tapes=generated.tapes,entry=generated.entry)
            compiled[str((L,merge))]=dict(instructions=len(program.instructions),tapes=program.tapes,sha256=sha(program.instructions))
            need(program.tapes==L+7,'Fixed port count')
            for A,R in (shapes if L<96 else [(1,1),(2,3),(1,81)]):
                V=L*A*R;p=router.ports(L)
                for pattern in (0,1,2):
                    bits=[pattern if pattern<2 else (((i*97+i*i+13)^(i>>2)^(i>>5))&1) for i in range(V)]
                    bank_bits=[[bits[(a*L+l)*R+r] for a in range(A) for r in range(R)] for l in range(L)]
                    cells=[dict(GUARD) for _ in range(p['count'])];heads=[0]*p['count']
                    cells[p['repeats_input']]=binary(A);cells[p['block_input']]=binary(R)
                    heads[p['repeats_input']]=heads[p['block_input']]=1
                    source_indices=p['banks'] if merge else (p['source'],)
                    destination_indices=(p['output'],) if merge else p['banks']
                    for l,t in enumerate(source_indices):
                        values=bank_bits[l] if merge else bits
                        cells[t]=marked(3+x for x in values);heads[t]=1
                    old=[dict(x) for x in cells]
                    out=SparseRun(program,cells,heads).run(94*V)
                    need(out.steps==ledger(L,A,R,merge),'Every instruction in exact all-input ledger')
                    need(sum(len(x) for x in out.visits)==space(L,A,R),'Every physical visited cell in exact ledger')
                    need(out.steps<=94*V and sum(len(x) for x in out.visits)<=13*V,'Uniform resource ceilings')
                    for t in source_indices+(p['repeats_input'],p['block_input']):
                        need(out.cells[t]==old[t] and out.heads[t]==1,'Borrowed source/descriptor bytes and heads unchanged')
                    for l,t in enumerate(destination_indices):
                        expected=bits if merge else bank_bits[l]
                        need(out.cells[t]==marked(3+x for x in expected) and out.heads[t]==1,'Exact new output value/order/head')
                    for t in (p['repeats'],p['block'],p['binary_work']):
                        need(out.cells[t]==GUARD and out.heads[t]==0,'Workspace including marker physically erased to origin')
                    unused=p['source'] if merge else p['output']
                    need(out.cells[unused]==old[unused] and out.heads[unused]==heads[unused],'Unused physical port untouched')
                    need(all(not vs or min(vs)>=0 for vs in out.visits),'No primitive reads or writes protected ancestor prefix')
                    need(all(all(k>=0 for k in positions) for positions in out.written),'No protected ancestor prefix write')
                    if out.steps*max_time[1]>max_time[0]*V:max_time=(out.steps,V)
                    used=sum(len(x) for x in out.visits)
                    if used*max_space[1]>max_space[0]*V:max_space=(used,V)
                    cases.append((L,A,R,merge,pattern,out.steps,used))
    # Independent binary-converter table walk including every shrink at powers2.
    converter=machine.Assembler(3)
    counters.emit_binary_to_unary(converter,0,1,2,'independent_conversion')
    converter.halt();program=converter.finish()
    converter_cases=[]
    for N in range(1,257):
        cells=[binary(N),{**GUARD,0:1},{**GUARD,0:1}]
        out=SparseRun(program,cells,[1,1,1]).run(c(N)+1)
        need(out.steps==c(N)+1,'Exact binary conversion ledger')
        need(out.cells==[binary(N),{**GUARD,0:1},marked([5]*N)],'Converter output/source/scratch bytes')
        need(out.heads==[1,1,1] and all(min(x)>=0 for x in out.visits),'Converter full head restoration/confinement')
        converter_cases.append((N,out.steps))
    controls=[]
    L,A,R=2,2,3;p=router.ports(L);program=router.build(L)
    base=[dict(GUARD) for _ in range(p['count'])];heads=[0]*p['count']
    base[p['source']]=marked([3,4]*6);heads[p['source']]=1
    base[p['repeats_input']]=binary(A);base[p['block_input']]=binary(R)
    heads[p['repeats_input']]=heads[p['block_input']]=1
    for label in ('zero_descriptor','redundant_high_zero','occupied_target','bad_source_symbol','missing_source_end'):
        cells=[dict(x) for x in base]
        if label=='zero_descriptor':cells[p['repeats_input']]=marked([3])
        elif label=='redundant_high_zero':cells[p['repeats_input']]=marked([3,4,3])
        elif label=='occupied_target':cells[p['banks'][0]][1]=4
        elif label=='bad_source_symbol':cells[p['source']][1]=5
        elif label=='missing_source_end':cells[p['source']].pop(13)
        try:SparseRun(program,cells,heads).run(94*L*A*R)
        except Invalid:controls.append(label)
        else:raise ValueError('Malformed local input accepted: '+label)
    return dict(status='PASS_INDEPENDENT_PHYSICAL_COVER_ROUTER_AUDIT',snapshot=snapshot['files'],
                interpreter='Independent local transition walker executes sealed TABLES; source Machine/Tape interpreter never executed. Actual build serialization compared separately.',
                physical_cases=len(cases),case_digest=sha(cases),converter_cases=len(converter_cases),
                converter_digest=sha(converter_cases),compiled_tables=compiled,
                exact_time_formula='c(A)+c(R)+18V+4AL+7A+R+4L+3d+33; d=L split,1 merge',
                exact_space_formula='2V+A+R+ellA+ellR+maxell+2L+12',
                time_bound='94V',visited_bound='13V',max_observed_time_ratio=list(max_time),max_observed_space_ratio=list(max_space),
                controls=controls,protected_prefix_preserved=True,
                scope='All-size static invariant/resource proof plus independent finite table execution. Source-bound physical low-type router only; no full variable-cover dispatcher/admission/precision theorem, kappa or external acceptance.')


if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run();raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:(HERE/'INDEPENDENT.json').write_text(raw)
    else:need((HERE/'INDEPENDENT.json').read_text()==raw,'Frozen exact independent audit')
    print(result['status'])
