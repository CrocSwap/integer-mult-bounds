"""Fixture construction and observations are outside the executed program."""
from pathlib import Path
from fractions import Fraction
from hashlib import sha256,sha1
import argparse
import gzip
import importlib.util
import json
import sys
import time

HERE=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:raise ValueError(why)


def authenticate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['sources']:
        raw=(HERE/pin['copy']).read_bytes()
        need(sha256(raw).hexdigest()==pin['sha256'] and len(raw)==pin['bytes'],'exact source SHA')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'exact source blob')


authenticate()
spec=importlib.util.spec_from_file_location('recursive_program',HERE/'recursive.py')
R=importlib.util.module_from_spec(spec);sys.modules[spec.name]=R;spec.loader.exec_module(R)
m=R.m


def encoded(logical):
    return [R.O if s>>shift&1 else R.Z for s in logical for shift in (2,1,0)]


def descriptor(value):
    need(type(value)is int and value>0,'positive fixture descriptor')
    return [m.LEFT]+[m.ONE if value>>i&1 else m.ZERO for i in range(value.bit_length())]+[m.RIGHT]


def put(tape,logical):
    start=tape.head
    for i,v in enumerate(encoded(logical)):tape.cells[start+i]=v
    tape.head=start+3


def packet(tape,start):
    raw=[];i=start
    while tape.cells.get(i,R.BL)!=R.BL:raw.append(tape.cells[i]);i+=1
    need(len(raw)%3==0 and all(x in(R.Z,R.O)for x in raw),'complete physical encoded packet')
    return [sum((x==R.O)<<(2-j) for j,x in enumerate(raw[k:k+3]))for k in range(0,len(raw),3)]


def binary_packet(tape,start):
    p=packet(tape,start);need(p[0]==m.LEFT and p[-1]==m.RIGHT and p[-2]==m.ONE,'canonical complete binary packet')
    return sum((v==m.ONE)<<i for i,v in enumerate(p[1:-1]))


def expected(bits,L,H,A,block,depth):
    """Separate integer oracle, never called by the machine."""
    banks=[[bits[(a*L+l)*block+r]for a in range(A)for r in range(block)]for l in range(L)]
    if depth:
        for l in (0,1):banks[l]=expected(banks[l],L,H,A//(L*H),H*block,depth-1)
    else:banks[0]=[1-x for x in banks[0]]
    return [banks[l][a*block+r]for a in range(A)for l in range(L)for r in range(block)]


def fixture(L=4,q=3,N=1,w=2,depth=2,slabs=1,body=1,prefix=7,mutant=None):
    program,meta=R.build(L,q,N);H=q**(N*N*(w-1));A=slabs*(L*H)**depth;block=H*body;volume=L*A*block
    if (L,q,N)==(4,3,1):
        table=json.loads(gzip.decompress((HERE/'TABLE.json.gz').read_bytes()))
        actual=json.loads(json.dumps({'instructions':program.instructions,'tapes':program.tapes,'entry':program.entry}))
        need(actual==table['program'] and json.loads(json.dumps(meta))==table['metadata'],'exact emitted literal table custody')
    if mutant is not None:
        rows=list(program.instructions);events=meta['events']
        if mutant=='pop_before_saving_output':
            rows[events['save_child_output']]=('goto',events['retire_child'])
        elif mutant=='omit_return_depth_restore':
            at=events['pop_end'];need(rows[at]==('move',meta['depth'],-1),'actual return depth instruction')
            rows[at]=('goto',at+1)
        elif mutant=='use_parent_R_instead_of_H':
            for lo,hi in ((events['grant_site_0'],events['grant_site_1']),
                          (events['grant_site_1'],events['push_begin'])):
                for i in range(lo,hi):
                    if rows[i][0]in('branch','write','move')and rows[i][1]==meta['high']:
                        rows[i]=(rows[i][0],meta['ports']['block_input'],*rows[i][2:])
        else:raise ValueError('unknown literal-program mutant')
        program=m.Program(tuple(rows),program.tapes,program.entry)
    tapes=[]
    for role in range(program.tapes):
        marker=R.LEFT if role<meta['payloads'] else R.BASE
        cells={i:(R.Z if i%2 else R.O)for i in range(prefix)};cells[prefix]=marker
        tapes.append(m.Tape(cells,prefix+1))
    origins=[t.head for t in tapes];p=meta['ports']
    bits=[int((i*i+3*i+1)%7<3)for i in range(volume)]
    put(tapes[p['source']],[m.LEFT]+[m.ONE if b else m.ZERO for b in bits]+[m.RIGHT])
    for role,value in ((p['repeats_input'],A),(p['block_input'],block),(meta['width'],w)):
        put(tapes[role],descriptor(value))
    for j in range(depth):tapes[meta['depth']].cells[origins[meta['depth']]+j]=R.O
    borrowed=[p['source'],p['repeats_input'],p['block_input'],meta['width'],meta['depth']]
    saved={i:(dict(tapes[i].cells),tapes[i].head)for i in borrowed}
    machine=m.Machine(program,tapes);trace=[];grants=[]
    # Only the external observer sees machine heads or program counters.
    events=meta['events'];frames=[];floors=[];pop_pending=None;returns=0
    previous=None
    while not machine.halted:
        pc=machine.pc
        if pc==events['node_entry']:
            j=tapes[meta['depth']].head-origins[meta['depth']]
            actualA=binary_packet(tapes[p['repeats_input']],tapes[p['repeats_input']].head-3)
            actualR=binary_packet(tapes[p['block_input']],tapes[p['block_input']].head-3)
            need(actualA==A//(L*H)**j and actualR==block*H**j,'on-path actual child headers at every entry')
            need(binary_packet(tapes[meta['high']],origins[meta['high']])==H,'physically produced immutable H')
            trace.append({'depth':j,'A':actualA,'R':actualR,'volume':L*actualA*actualR})
        if pc in (events['grant_ready_0'],events['grant_ready_1']):
            j=tapes[meta['depth']].head-origins[meta['depth']]
            ca=binary_packet(tapes[meta['grant_A']],tapes[meta['grant_A']].head-3)
            cr=binary_packet(tapes[meta['grant_R']],tapes[meta['grant_R']].head-3)
            need(ca==A//(L*H)**(j+1) and cr==block*H**(j+1),'actual live-frame generated child grants')
            grants.append({'parent_depth':j,'A_child':ca,'R_child':cr})
        if pc==events['push_begin']:
            snap=[]
            for t in tapes[:meta['payloads']]:
                lo=t.head-1
                while t.cells.get(lo,R.BL)!=R.LEFT:lo-=1
                end=lo+1
                while t.cells.get(end,R.BL)!=R.BL:end+=1
                snap.append((dict((i,t.cells.get(i,R.BL))for i in range(lo,end)),t.head,end))
            frames.append(snap)
        if pc==events['push_end']:
            floors.append([t.head-1 for t in tapes[:meta['payloads']]])
        if pc==events['pop_begin']:
            j=tapes[meta['depth']].head-origins[meta['depth']]
            protected=packet(tapes[meta['output_relay']],origins[meta['output_relay']])
            need(len(protected)==volume//L**j+2 and protected[0]==m.LEFT and protected[-1]==m.RIGHT,
                 'complete child output is protected before pop')
            floors.pop();pop_pending=frames.pop()
        if pc==events['pop_end']:
            need(pop_pending is not None,'matching real pop')
            for t,(old,head,end)in zip(tapes,pop_pending):
                need(t.head==head and all(t.cells.get(i,R.BL)==v for i,v in old.items()),'pop restores every parent byte and head')
            returns+=1;pop_pending=None
        row=program.instructions[pc]
        # A pop is the only declared operation allowed to reenter its parent.
        if floors and row[0]in('branch','write','move')and row[1]<meta['payloads']:
            t=row[1];need(tapes[t].head>=floors[-1][t],'child accesses no parked parent')
            if row[0]=='move':need(tapes[t].head+row[2]>=floors[-1][t],'child crosses no ancestor delimiter')
        machine.step()
        need(machine.steps<100000000,'external simulation cap')
    wanted=expected(bits,L,H,A,block,depth)
    need(packet(tapes[p['output']],origins[p['output']])==[m.LEFT]+[m.ONE if b else m.ZERO for b in wanted]+[m.RIGHT],
         'full all-depth split/child-return/merge endpoint')
    for role,(old,head)in saved.items():
        need(tapes[role].head==head and all(tapes[role].cells.get(i,R.BL)==v for i,v in old.items()),'root original input/header preserved')
        need(not set(old)&machine.write_positions[role],'original source/header bytes are never written')
    allowed={*borrowed,p['output']}
    for role,t in enumerate(tapes):
        if role not in allowed:
            need(not any(i>=origins[role]for i in t.cells),'all owned scratch/control/H/relays physically erased')
            need(t.head==origins[role],'all retired heads restored')
        need(all(t.cells.get(i,R.BL)==(R.Z if i%2 else R.O)for i in range(prefix)),'external ancestor prefix unchanged')
    need(not frames and not floors and returns==2**(depth+1)-2,'all nested child continuations returned')
    need(len(trace)==2**(depth+1)-1,'all recursive nodes entered through actual machine PC')
    need(len(grants)==returns,'every actual child call has a newly generated owned grant')
    ct=10**8*(meta['payloads']+(q**(N*N)).bit_length()+1)
    cs=1000*(meta['payloads']+(q**(N*N)).bit_length()+1)
    time_upper=ct*(sum(x['volume']for x in trace)+volume)
    space_upper=cs*sum(volume//L**j for j in range(depth+1))
    need(machine.steps<=time_upper,'proved complete occurrence-sum time envelope')
    need(sum(max(v)-min(v)+1 if v else 0 for v in machine.visits)<=space_upper,
         'proved active-chain backing envelope, prefix charged separately')
    return {'L':L,'q':q,'N':N,'w':w,'H':H,'remaining_depth':depth,'A':A,'R':block,'root_volume':volume,
            'fixed_tapes':program.tapes,'literal_instructions':len(program.instructions),
            'program_sha256':sha256(json.dumps(program.instructions,separators=(',',':')).encode()).hexdigest(),
            'nodes':trace,'generated_grants':grants,'actual_returns':returns,'microtransitions':machine.steps,
            'visited_cells':sum(len(v)for v in machine.visits),
            'local_retained_backing_upper':sum(max(v)-min(v)+1 if v else 0 for v in machine.visits),
            'external_ancestor_prefix_cells':program.tapes*prefix,
            'proved_time_upper':time_upper,'proved_local_space_upper':space_upper,
            'output_sha256':sha256(bytes(wanted)).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tiny',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    cases=[fixture(w=1,depth=0)]if a.tiny else[fixture(w=1,depth=0),fixture(w=2,depth=1),fixture(w=2,depth=2),fixture(w=3,depth=1)]
    controls={}
    if not a.tiny:
        # The wrong H wire agrees at root (R0=H) and therefore passes a one-edge
        # instance. Only real on-path grandchildren expose the stale premise.
        fixture(w=2,depth=1,mutant='use_parent_R_instead_of_H')
        controls['stale_H_wire_one_edge_positive_control']=True
        for mutant in ('pop_before_saving_output','omit_return_depth_restore','use_parent_R_instead_of_H'):
            try:fixture(w=2,depth=2,mutant=mutant)
            except ValueError as error:controls[mutant]=str(error)
            else:raise ValueError('literal-program semantic fault accepted '+mutant)
    r={'status':'PASS_LITERAL_ON_PATH_FIXED_WIDTH_RECURSIVE_PRODUCTION','cases':cases,'controls':controls}
    raw=json.dumps(r,sort_keys=True,indent=2)+'\n'
    if a.write:(HERE/'RESULT.json').write_text(raw)
    elif not a.tiny:need((HERE/'RESULT.json').read_text()==raw,'read-only stable receipt')
    print(r['status']+' cases='+str(len(cases))+' semantic_controls='+str(len(controls)))
