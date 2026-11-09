"""Metered fixtures execute unchanged Controller.primitive and execute_table.

Only fixture construction and post-run oracles inspect integer values/storage.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from types import SimpleNamespace
from fractions import Fraction
from source_binding import need, vendor

M = vendor("rounded_retained_lifecycle", "vendor/machine.py")


class RowCounter:
    """Observer-only table lookup counter; returns the unchanged immutable row.

    It never receives a tape, input value or coefficient, and never changes
    the instruction stream. Ordinary fixtures use the tuple directly.
    """
    def __init__(self, rows):
        self.rows, self.steps = rows, 0

    def __getitem__(self, pc):
        self.steps += 1
        return self.rows[pc]


class Tape:
    def __init__(self, bits=(), origin=17, readonly=False):
        self.origin = self.pos = origin
        self.cells = {origin-1:M.LEFT, origin-2:91}
        self.cells.update({origin+i:s for i,s in enumerate(bits)})
        self.readonly = readonly
        self.actions = self.reads = self.writes = self.moves = 0
        self.highwater = origin+len(bits)

    def tick(self):
        need(self.pos >= self.origin-1, "no ancestor access")
        self.actions += 1; self.highwater = max(self.highwater,self.pos)

    def read(self):
        self.tick(); self.reads += 1
        return self.cells.get(self.pos,M.BLANK)

    def write(self,s):
        self.tick(); self.writes += 1
        need(not self.readonly and self.pos >= self.origin, "protected source/marker")
        need(s in range(7), "physical alphabet")
        self.cells[self.pos]=s

    def move(self,step):
        self.tick(); self.moves += 1
        need(step in (-1,1), "unit physical movement")
        self.pos += step
        need(self.pos >= self.origin-1, "no ancestor crossing")
        self.highwater=max(self.highwater,self.pos)

    def body(self):
        end=self.origin
        while self.cells.get(end,M.BLANK)!=M.BLANK:
            end+=1
        return tuple(self.cells.get(k,M.BLANK) for k in range(self.origin,end))

    def blank(self):
        return all(v==M.BLANK for k,v in self.cells.items() if k>=self.origin)

    def protected(self):
        return self.cells[self.origin-1]==M.LEFT and self.cells[self.origin-2]==91


def encode_symbols(symbols):
    return tuple((s>>k)&1 for s in symbols for k in (2,1,0))


def symbols(values,width):
    need(width>=1,"positive signed width")
    out=[]
    for n in values:
        need(-(1<<(width-1))<=n<(1<<(width-1)),"signed fixture input")
        out.extend((n>>k)&1 for k in range(width));out.append(2)
    return tuple(out)


def decode(bits,width):
    need(len(bits)%3==0,"whole physical codes")
    syms=[4*bits[i]+2*bits[i+1]+bits[i+2] for i in range(0,len(bits),3)]
    need(len(syms)%(width+1)==0,"whole components")
    out=[]
    for i in range(0,len(syms),width+1):
        b=syms[i:i+width]
        need(all(z in (0,1) for z in b) and syms[i+width]==2,"numeric result grammar")
        out.append(sum(z<<k for k,z in enumerate(b))-(b[-1]<<width))
    return tuple(out)


def execute(table,op,target,source,width,work=None,target_symbols=None,source_symbols=None,contexts=(),count_rows=False):
    public=[Tape(encode_symbols(symbols(target,width) if target_symbols is None else target_symbols),17)]
    if op=="ADD":
        public.append(Tape(encode_symbols(symbols(source,width) if source_symbols is None else source_symbols),29,True))
    if work is None:
        work=[Tape((1,0,1,1,0),41),Tape((0,1,0),63)]
        work[0].pos+=2;work[1].pos+=3
    before=[t.body() for t in public]
    context_before=[t.body() for t in contexts]
    old_backing=sum(len(t.body()) for t in work)
    all_ports=public+work+list(contexts)
    before_actions=sum(t.actions for t in all_ports)
    # Exactly the attributes read by the unchanged method; no full recursive
    # Controller constructor/run/stack claim is made by this primitive fixture.
    measured=RowCounter(table) if count_rows else table
    controller=SimpleNamespace(payloads=tuple(all_ports),primitive_work=(len(public),len(public)+1),
                               primitive_context=tuple(range(len(public)+2,len(all_ports))),services={("fixture",):measured})
    failure=None
    try:
        M.Controller.primitive(controller,("fixture",),tuple(range(len(public))))
    except ValueError as exc:
        failure=str(exc)
    actions=sum(t.actions for t in all_ports)-before_actions
    need(all(t.protected() for t in all_ports),"protected local markers/ancestors")
    need([t.body() for t in contexts]==context_before,"borrowed binary contexts preserved")
    if op=="ADD":need(public[1].body()==before[1],"borrowed source preserved")
    if failure is not None:
        need(public[0].body()==before[0],"rejected whole field before any public write")
    else:
        need(all(t.pos==t.origin for t in all_ports),"all success heads restored")
        need(all(t.blank() for t in work),"entire historical scratch erased")
    return dict(error=failure,output=None if failure else decode(public[0].body(),width),
                table_rows=measured.steps if count_rows else None,
                actions=actions,old_backing=old_backing,public=public,work=work,before=before)


def rounded(q,m):
    """Independent integer oracle, not a finite-state transition replay."""
    q=Fraction(q)
    return (q.numerator*m+q.denominator//2)//q.denominator


def check_case(table,receipt,op,q,target,source,width,work=None):
    out=execute(table,op,target,source,width,work)
    expected=tuple(rounded(q,y)+(x if op=="ADD" else 0)
                   for x,y in zip(target,source if op=="ADD" else target))
    admitted=all(-(1<<(width-1))<=n<(1<<(width-1)) for n in expected)
    need((out["error"] is None)==admitted,"exact final-range iff")
    if admitted:need(out["output"]==expected,"integer nearest-up oracle")
    records=len(target);extent=records*(width+1)
    bound=512*(extent+1)+64*receipt['denominator_twos']*records+7*out['old_backing']
    need(out['actions']<=bound,"full positive tape-action bound")
    return admitted,out,bound
