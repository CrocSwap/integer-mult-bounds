"""Actual one-table natural-root/field-port composition checks."""
from hashlib import sha256
import producer as p
import join
from check import expected_prefix, prefix_bytes, need


def fixture(width=2,depth=2,slabs=1,body=1,prefix=7,mutant=None):
    program,meta,old=join.build(); R=join.source.R
    if mutant is not None:
        rows=list(program.instructions)
        if mutant=='skip_service':
            at=meta['events']['leaf'];rows[at]=old.instructions[at]
        elif mutant=='skip_code_pop':
            at=meta['events']['pop_end'];rows[at]=old.instructions[at]
        elif mutant=='zero_call_label':
            begin=meta['hooks']['push']
            at=next(i for i in range(begin,len(rows)) if rows[i][0]=='branch' and rows[i][1]==meta['phase'])
            op,tape,pairs,default=rows[at];targets=dict(pairs);targets[p.O]=targets[p.Z]
            rows[at]=(op,tape,tuple(sorted(targets.items())),default)
        else: raise ValueError('known literal joined mutant')
        program=p.m.Program(tuple(rows),program.tapes,program.entry)
    high=3**(width-1); a=slabs*(4*high)**depth; block=high*body; volume=4*a*block
    tapes=[]
    for role in range(program.tapes):
        if role<old.tapes:
            marker=R.LEFT if role<meta['payloads'] else R.BASE
            cells={i:(p.Z if i%2 else p.O) for i in range(prefix)};cells[prefix]=marker
            tapes.append(p.m.Tape(cells,prefix+1))
        else: tapes.append(p.m.Tape())
    def put(role,logical):
        tape=tapes[role];start=tape.head
        for i,value in enumerate(bit for s in logical for bit in (p.O if s>>2&1 else p.Z,
                                                                 p.O if s>>1&1 else p.Z,
                                                                 p.O if s&1 else p.Z)):
            tape.cells[start+i]=value
        tape.head=start+3
    bits=[int(((i*73+19) ^ (i//7))&1) for i in range(volume)]
    put(meta['ports']['source'],[p.LEFT,*[p.O if x else p.Z for x in bits],p.RIGHT])
    for role,value in ((meta['T_input'],slabs),(meta['R_body_input'],body),(meta['width'],width)):
        put(role,[p.LEFT,*[p.O if value>>i&1 else p.Z for i in range(value.bit_length())],p.RIGHT])
    for i in range(depth): tapes[meta['depth']].cells[prefix+1+i]=p.O
    baseline_tapes=[p.m.Tape(t.cells,t.head) for t in tapes[:old.tapes]]
    baseline=p.m.Machine(old,baseline_tapes).run(50_000_000)
    machine=p.m.Machine(program,tapes);path=[];ordinal=0;total=0;leaves=0;digest=sha256();leaf_counts=[]
    while not machine.halted:
        if machine.pc==meta['events']['push_begin']:
            phase=tapes[meta['phase']].read();need(phase in (p.Z,p.O),'actual static call phase')
            path.append(int(phase==p.O))
        if machine.pc==meta['events']['pop_end']:
            need(path,'matched source return');path.pop()
        if machine.pc==meta['events']['leaf']:
            need(len(path)==depth,'all-depth source field age');ordinal=0;leaves+=1
        if machine.pc==meta['hooks']['ready']:
            raw=prefix_bytes(tapes[meta['service_ports'][p.PREFIX]])
            need(raw==bytes(expected_prefix(3,1,2,path+[0],width,ordinal)),
                 'literal root-produced fibre receives chronological generated fields')
            digest.update(raw);ordinal+=1;total+=1
        if machine.pc==meta['hooks']['service_cleanup']:
            need(ordinal==slabs*high**(depth+1),'complete actual leaf fibre coverage')
            leaf_counts.append(ordinal)
        if machine.steps>50_000_000: raise RuntimeError('external joined check budget')
        machine.step()
    need(not path and leaves==2**depth,'exact source call forest')
    need(len(leaf_counts)==leaves and total==leaves*slabs*high**(depth+1),'no missing physical field-service calls')
    for actual,expected in zip(tapes[:old.tapes],baseline_tapes):
        need(actual.cells==expected.cells and actual.head==expected.head,
             'all source tapes exactly equal original completed root execution')
    for tape in tapes[old.tapes:]: need(not tape.cells and tape.head==0,'fixed added roles retired')
    return {'w':width,'depth':depth,'slabs':slabs,'body':body,'volume':volume,'leaf_entries':leaves,
            'leaf_prefixes':leaf_counts,'prefixes':total,'prefix_sha256':digest.hexdigest(),
            'source_steps':baseline.steps,'joined_steps':machine.steps,'added_steps':machine.steps-baseline.steps,
            'source_visited':sum(map(len,baseline.visits)),
            'source_tapes':old.tapes,'joined_tapes':program.tapes,'source_instructions':len(old.instructions),
            'joined_instructions':len(program.instructions),'visited':sum(map(len,machine.visits)),
            'added_role_visits':sum(map(len,machine.visits[old.tapes:]))}


if __name__=='__main__':
    import json
    print(json.dumps(fixture(),sort_keys=True))
