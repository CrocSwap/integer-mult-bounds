"""External exact oracles and fixtures; never imported by emitted programs."""
from hashlib import sha256
import json
import producer as p


def need(ok, message):
    if not ok: raise ValueError(message)


def encoded(symbols, origin=0):
    logical = [p.LEFT, *symbols, p.RIGHT]
    body = [p.O if s >> bit & 1 else p.Z for s in logical for bit in (2,1,0)]
    return p.m.Tape({origin:p.LEFT, **{origin+1+i:s for i,s in enumerate(body)}}, origin+4)


def binary(n, origin=0):
    need(n > 0, 'positive fixture integer')
    return encoded([p.O if n >> i & 1 else p.Z for i in range(n.bit_length())], origin)


def expected_prefix(q, dimension, code_bits, codes, width, ordinal):
    cap=q**(width-1); high=cap**(dimension*dimension); length=(q**width).bit_length()+1
    out=[]
    for code in codes:
        out.extend(p.O if code >> bit & 1 else p.Z for bit in range(code_bits)); out.append(p.WE)
        h=ordinal % high; ordinal //=high
        digits=[]
        for _ in range(dimension*dimension): digits.append(h % cap); h //=cap
        for digit in reversed(digits):
            out.extend(p.O if digit >> bit & 1 else p.Z for bit in range(length)); out.append(p.WE)
        out.append(p.FE)
    return out


def prefix_bytes(tape, origin=0):
    need(tape.head==origin+1 and tape.cells.get(origin)==p.LEFT, 'prefix local origin')
    stop=origin+1
    while tape.cells.get(stop,p.BL)!=p.BL: stop+=1
    return bytes(tape.cells[x] for x in range(origin+1,stop))


def fixture(q=3, dimension=2, code_bits=2, codes=(0,1), width=2, fibre=1, repeats=1,
            oldest_first=True, partial_prefixes=None, origins=None, program_override=None):
    program,meta=p.build(q,dimension,code_bits,oldest_first=oldest_first)
    if program_override is not None: program=program_override(program,meta)
    total=q**((width-1)*dimension*dimension*len(codes))*repeats
    allocated=total if partial_prefixes is None else partial_prefixes
    origins=[0]*p.TAPES if origins is None else origins
    tapes=[p.m.Tape(head=origin) for origin in origins]
    tapes[p.WIDTH]=binary(width,origins[p.WIDTH]); tapes[p.FIBRE]=binary(fibre,origins[p.FIBRE])
    words=[]
    for code in codes:
        words.extend(p.O if code >> bit & 1 else p.Z for bit in range(code_bits)); words.append(p.WE)
    oc=origins[p.CODES]
    tapes[p.CODES]=p.m.Tape({oc:p.LEFT,**{oc+1+i:s for i,s in enumerate(words)},oc+1+len(words):p.RIGHT},oc+1)
    payload=[p.O if ((i*73+19) ^ (i//7)) & 1 else p.Z for i in range(allocated*fibre)]
    tapes[p.PAYLOAD]=encoded(payload,origins[p.PAYLOAD])
    # Buried nonzero records test translation and local origins. No live head
    # is permitted to read/write these protected predecessor cells.
    for t,origin in zip(tapes,origins):
        t.cells.update({origin-3:p.O,origin-2:p.Z})
    protected=[(dict(t.cells),t.head) for t in tapes[:4]]
    machine=p.m.Machine(program,tapes); digest=sha256(); observed=[]; count=0
    while not machine.halted:
        if machine.pc==meta['events']['ready']:
            value=prefix_bytes(machine.tapes[p.PREFIX],origins[p.PREFIX])
            if oldest_first:
                want=bytes(expected_prefix(q,dimension,code_bits,codes,width,count))
                need(value==want, 'complete chronological field record matches body fibre')
            digest.update(value)
            if count<3: observed.append(value)
            count+=1
            if partial_prefixes is not None and count==partial_prefixes: break
        if machine.steps>=100_000_000: raise RuntimeError('external finite simulation budget')
        machine.step()
    if partial_prefixes is None:
        need(count==total, 'all complete high fibres including repeated slabs')
        for tape,(cells,head) in zip(machine.tapes[:4],protected):
            need(tape.cells==cells and tape.head==head,'borrowed bytes and heads restored')
        for tape,origin in zip(machine.tapes[4:],origins[4:]):
            need(tape.cells=={origin-3:p.O,origin-2:p.Z} and tape.head==origin,'owned role erased at reused origin')
    for i,origin in enumerate(origins):
        need(not machine.visits[i] or min(machine.visits[i])>=origin,'never visit buried callers')
    return {'q':q,'N':dimension,'Q':code_bits,'codes':list(codes),'w':width,'fibre':fibre,'repeats':repeats,
            'complete':partial_prefixes is None,'prefixes':count,'prefix_sha256':digest.hexdigest(),
            'instructions':len(program.instructions),'steps':machine.steps,'reads':machine.reads,
            'writes':machine.writes,'moves':machine.moves,'visited':sum(map(len,machine.visits))}, observed, machine, meta


if __name__=='__main__':
    print(json.dumps(fixture(dimension=1,codes=(0,1),width=2,fibre=3)[0],sort_keys=True))
