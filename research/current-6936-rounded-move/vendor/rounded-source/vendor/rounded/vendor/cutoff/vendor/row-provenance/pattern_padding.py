"""Retained row-pad planner with canonical encoded-zero row payloads.

Only the added-row writer/restrictor changes. The exact inherited binary
decoder, round-up, complete genuine-row scans and cleanup remain in use.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import importlib.util
import sys


def load_programs():
    path=Path(__file__).resolve().parent/"row_programs.py"
    spec=importlib.util.spec_from_file_location("pattern_row_programs",path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    exec(compile(path.read_bytes(),str(path),"exec"),module.__dict__)
    return module


r=load_programs()
source=r.retained
ZERO_ROW=15
TAPES=16


class PatternBuilder(source.Builder):
    def rows(self, incoming, output, count, mode):
        if mode=="copy":
            return super().rows(incoming,output,count,mode)
        source.need(mode in ("zero","discard"),"fixed padding mode")
        rows,row,body,bit,zero,one,endbody,end=(self.fresh("pattern") for _ in range(8))
        self.mark(rows)
        self.read(count,{"1":row,"_":end})
        self.mark(row)
        self.mark(body)
        self.read(source.B,{"1":bit,"_":endbody})
        self.mark(bit)
        self.read(ZERO_ROW,{"0":zero,"1":one})
        for label,value in ((zero,"0"),(one,"1")):
            self.mark(label)
            if mode=="zero":
                self.write(output,value)
                self.move(output,1)
            else:
                good=self.fresh("same_encoded_zero")
                self.read(incoming,{value:good})
                self.mark(good)
                self.move(incoming,1)
            self.move(ZERO_ROW,1)
            self.move(source.B,1)
            self.go(body)
        self.mark(endbody)
        exact=self.fresh("exact_zero_row")
        self.read(ZERO_ROW,{"_":exact})
        self.mark(exact)
        self.rewind(ZERO_ROW)
        self.rewind(source.B)
        self.move(count,1)
        self.go(rows)
        self.mark(end)
        self.rewind(count)


def program():
    b=PatternBuilder()
    for port in range(TAPES):
        b.boundary(port)
    for descriptor,output in ((source.PD,source.P),(source.RD,source.R),
                              (source.SD,source.S),(source.BD,source.B)):
        b.unary(descriptor,output)
    # Validate a complete pattern even when padding happens to be empty.
    loop,more,end=(b.fresh("validate_zero_row") for _ in range(3))
    b.mark(loop)
    b.read(source.B,{"1":more,"_":end})
    b.mark(more)
    good=b.fresh("pattern_digit")
    b.read(ZERO_ROW,{"0":good,"1":good})
    b.mark(good)
    b.move(source.B,1);b.move(ZERO_ROW,1);b.go(loop)
    b.mark(end)
    exact=b.fresh("pattern_exact")
    b.read(ZERO_ROW,{"_":exact});b.mark(exact)
    b.rewind(source.B);b.rewind(ZERO_ROW)
    b.plan()                         # retains the explicit stock <= rows test
    b.transform(source.SOURCE,source.PAD,False)
    b.code.append(("call",))
    for port in (source.SOURCE,source.PD,source.RD,source.SD,source.BD,
                 source.ROWS,source.PAD,source.RETURN,ZERO_ROW):
        b.boundary(port)
    b.transform(source.RETURN,source.OUTPUT,True)
    for port in (source.P,source.R,source.S,source.B,source.D,source.TEMP,
                 source.ROWS,source.PAD,source.RETURN):
        b.clear(port)
    b.code.append(("done",))
    b.mark("reject")
    b.rejection="quarantine"
    for port in (source.P,source.R,source.S,source.B,source.D,source.TEMP,
                 source.ROWS,source.PAD,source.RETURN,source.OUTPUT):
        b.clear(port)
    for port in (source.SOURCE,source.PD,source.RD,source.SD,source.BD,ZERO_ROW):
        b.rewind(port)
    b.code.append(("rejected",))
    b.mark("quarantine");b.code.append(("quarantined",))
    return b.finish()


PROGRAM=program()


class Machine:
    """The sole suspended PC is finite root-wrapper control, not a host stack."""
    def __init__(self,ports):
        source.need(len(ports)==TAPES,"sixteen fixed physical padding ports")
        self.ports=tuple(ports)
        self.pc=0
        self.steps=0

    def run(self,limit=None):
        while True:
            if limit is not None and self.steps>=limit:
                raise ValueError("observer limit")
            row=PROGRAM[self.pc]
            op=row[0]
            self.steps+=1
            if op in ("call","done"):
                self.pc+=1
                return op
            if op in ("rejected","quarantined"):
                raise ValueError("pattern padding "+op)
            if op=="goto":
                self.pc=row[1]
                continue
            port=self.ports[row[1]]
            if op=="read":
                symbol=port.read()
                source.need(symbol in row[2],"padding local alphabet")
                self.pc=row[2][symbol]
                continue
            if op=="write":port.write(row[2])
            elif op=="move":port.move(row[2])
            else:raise ValueError("unknown padding opcode")
            self.pc+=1
