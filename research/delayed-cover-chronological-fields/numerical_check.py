"""Exact unchanged 64D Callback.weight consumer of physically emitted records.

The legal rank-one source vocabulary is a bounded witness, not a selected
catalogue replay. The producer's complete huge cube is not materialized.
"""
from fractions import Fraction
from pathlib import Path
import sys
import producer as p
from check import fixture, need

sys.path.insert(0,str(Path(__file__).resolve().parent/'numerical'))
import words
import records
import controller
import sources


class ReadOnlyPort:
    """Fixed alphabet renaming only; no coordinate/word decoding."""
    alphabet={p.BL:words.BLANK,p.LEFT:words.LEFT,p.RIGHT:words.RIGHT,p.Z:words.ZERO,
              p.O:words.ONE,p.WE:records.WORD_END,p.FE:records.RECORD_END}

    def __init__(self,tape): self.tape=tape; self.meter=words.Meter()

    def read(self):
        self.meter.reads+=1
        return self.alphabet[self.tape.read()]

    def step(self,direction):
        need(direction in (-1,1),'unit source-record move')
        self.meter.moves+=1; self.tape.head+=direction

    def rewind(self):
        self.step(-1)
        while self.read()!=words.LEFT: self.step(-1)
        self.step(1)

    def write(self,_): raise ValueError('borrowed field records are readonly')


def specifications():
    identity=tuple(tuple(Fraction(i==j) for j in range(64)) for i in range(64))
    base=tuple(tuple(Fraction(i==j==0) for j in range(64)) for i in range(64))
    template=sources.Template(q=3,rank=1,record=('synthetic-order-witness',),
                              base=base,chart=identity,preparation=identity)
    out={}
    for code,block in enumerate((((1,1),(1,2)),((1,2),(1,1)))):
        low=[[int(i==j) for j in range(64)] for i in range(64)]
        for i,row in enumerate((0,63)):
            for j,column in enumerate((0,63)): low[row][column]=block[i][j]
        out[code]=sources.Specification(code=code,template=template,low=tuple(map(tuple,low)),good=True)
    out[2]=sources.Specification(code=2,template=template,low=out[1].low,good=True)
    return out


def actual_weight(tape):
    original=dict(tape.cells),tape.head
    residue=words.Arena(5); index=words.Arena(20,capacity=256)
    modulus=residue.input(9); ring=words.Ring(modulus)
    program=records.Program.fixture(index,residue,262144,1,[(0,0,1,0,False,False),(0,1,1,0,False,False)],2)
    fields=records.Fields(index,residue,2); fields.tape=ReadOnlyPort(tape)
    program_before=dict(enumerate(program.tape.cells)),program.tape.head
    pos=index.input(0)
    inspect=words.Word.inspect
    def forbidden(_): raise ValueError('no runtime numerical word inspection')
    words.Word.inspect=forbidden
    try:
        cb=controller.Callback(ring,index,program,fields,specifications(),2)
        result=cb.weight(pos); cb.close()
    finally:
        words.Word.inspect=inspect
    value=result.inspect(); residue.free(result); index.free(pos)
    need((tape.cells,tape.head)==original,'literal produced prefix bytes/head survive actual callback')
    need((dict(enumerate(program.tape.cells)),program.tape.head)==program_before,'borrowed program survives')
    need(not index.live,'index scratch retired')
    ring.close(); residue.free(modulus); need(not residue.live,'residue scratch retired')
    return {'value':value,'record_actions':fields.tape.meter.record(),
            'residue_actions':residue.meter.record(),'index_actions':index.meter.record()}


def witness():
    # Full 3^(12288) domain is infeasible. Both machines run only to the second
    # emitted prefix. The materialized payload prefix has a valid extension;
    # no terminal/cleanup/full-cube claim is made for these two executions.
    out=[]
    for oldest_first in (True,False):
        receipt,seen,machine,_=fixture(dimension=64,codes=(0,1,2),width=2,fibre=1,
                                     partial_prefixes=2,oldest_first=oldest_first)
        weight=actual_weight(machine.tapes[p.PREFIX])
        need(weight['value']==(1 if oldest_first else 7),'actual numerical ordering witness')
        out.append({'oldest_first':oldest_first,'producer':receipt,'consumer':weight})
    return out


if __name__=='__main__':
    import json
    print(json.dumps(witness(),sort_keys=True))
