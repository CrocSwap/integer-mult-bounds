"""Finite local row programs for a fixed compiled template.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The source Builder/positive-binary decoder is retained byte for byte. Every
runtime decision is a local-symbol branch in an emitted finite table.
Numerical Python values occur only in template compilation or observers.
"""
from pathlib import Path
import importlib.util
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_source(relative, name):
    path = Path(__file__).resolve().parent / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


retained = load_source("vendor/row_padding.py", "row_dispatch_retained_padding")
geometry = load_source("vendor/occurrence_geometry.py", "row_dispatch_retained_geometry")
BLANK, LEFT, ZERO, ONE = "_", "|", "0", "1"

# Inherited unary decoder uses TEMP=10. Roles are supplied, preallocated ports.
SOURCE, OUTPUT, OUTER, ROWS, STOCK, ROWBITS = range(6)
QUOT_ROWS, QUOT_STOCK, GUIDE_C, GUIDE_R, TEMP, GUIDE_J, GUIDE_S = range(6, 13)
HEADER, CHILD_HEADER, LENGTH = 13, 14, 15
SCHEMA = (
    ("outer", OUTER), ("rows", ROWS), ("stock", STOCK), ("row_bits", ROWBITS),
    ("within_bits", 16), ("record_bits", 17), ("p", 18), ("d", 19),
    ("K", 20), ("G", 21), ("H", 22), ("q0", 23), ("qF", 24),
    ("qB", 25), ("D", 26), ("f", 27), ("rho", 28),
    ("active_start", 29), ("back_start", 30), ("selected_axes", 31),
    ("entry_start", 32), ("remainder", 33), ("cutoff", 34),
)
OFFSET, CONSTANT = 35, 36
FIRST_ROLE = 40
ROW_CHILD = "single_owner_row_child"
MATCHED = "matched_fields_occurrence"


class Builder(retained.Builder):
    def empty(self, tape):
        ok = self.fresh("empty")
        self.read(tape, {BLANK: ok})
        self.mark(ok)

    def seek_end(self, tape):
        loop, step, end = (self.fresh("seek") for _ in range(3))
        self.mark(loop)
        self.read(tape, {ZERO: step, ONE: step, BLANK: end})
        self.mark(step)
        self.move(tape, 1)
        self.go(loop)
        self.mark(end)

    def canonical(self, tape, positive=False):
        """Canonical LSF binary; exactly '0' is the sole zero representation."""
        first0, last0, last1, next0, next1, end = (self.fresh("canon") for _ in range(6))
        self.read(tape, {ZERO: first0, ONE: next1})
        self.mark(first0)
        self.move(tape, 1)
        branches = {ZERO: next0, ONE: next1}
        if not positive:
            branches[BLANK] = end
        self.read(tape, branches)
        self.mark(next0)
        self.move(tape, 1)
        self.go(last0)
        self.mark(next1)
        self.move(tape, 1)
        self.go(last1)
        self.mark(last0)
        self.read(tape, {ZERO: next0, ONE: next1})
        self.mark(last1)
        self.read(tape, {ZERO: next0, ONE: next1, BLANK: end})
        self.mark(end)
        self.rewind(tape)

    def copy(self, source, target):
        self.empty(target)
        loop, zero, one, end = (self.fresh("copy") for _ in range(4))
        self.mark(loop)
        self.read(source, {ZERO: zero, ONE: one, BLANK: end})
        for label, bit in ((zero, ZERO), (one, ONE)):
            self.mark(label)
            self.write(target, bit)
            self.move(source, 1)
            self.move(target, 1)
            self.go(loop)
        self.mark(end)
        self.rewind(source)
        self.rewind(target)

    def divide_constant(self, source, target, divisor, exact=True, remainder=None):
        """Positive quotient; optional floor/remainder, all remainders finite."""
        need(type(divisor) is int and divisor > 0, "fixed positive divisor")
        self.canonical(source, positive=True)
        self.copy(source, target)
        self.seek_end(source)
        self.seek_end(target)
        self.move(source, -1)
        self.move(target, -1)
        state = [self.fresh("remainder") for _ in range(divisor)]
        finishes = [self.fresh("division_done") for _ in range(divisor)]
        common = self.fresh("division_common")
        self.go(state[0])
        for rem in range(divisor):
            self.mark(state[rem])
            branch = {bit: state[rem] + bit for bit in (ZERO, ONE)}
            if rem == 0 or not exact:
                branch[LEFT] = finishes[rem]
            self.read(source, branch)
            for value, bit in enumerate((ZERO, ONE)):
                self.mark(state[rem] + bit)
                quotient, following = divmod(2 * rem + value, divisor)
                self.write(target, str(quotient))
                self.move(source, -1)
                self.move(target, -1)
                self.go(state[following])
        for rem in range(divisor):
            self.mark(finishes[rem])
            self.move(source, 1);self.move(target, 1)
            if remainder is not None:
                self.empty(remainder)
                for bit in bin(rem)[2:][::-1]:
                    self.write(remainder,bit);self.move(remainder,1)
                self.rewind(remainder)
            self.go(common)
        self.mark(common)
        self.seek_end(target)
        self.move(target, -1)
        trim, erase, done = (self.fresh("trim") for _ in range(3))
        self.mark(trim)
        self.read(target, {ZERO: erase, ONE: done})
        self.mark(erase)
        self.write(target, BLANK)
        self.move(target, -1)
        self.go(trim)
        self.mark(done)
        self.rewind(target)

    def unary_zero(self, descriptor, output):
        self.canonical(descriptor)
        maybe,positive,zero,finish=(self.fresh("unary_zero") for _ in range(4))
        self.read(descriptor,{ZERO:maybe,ONE:positive})
        self.mark(maybe);self.move(descriptor,1)
        self.read(descriptor,{BLANK:zero,ZERO:positive+"rewind",ONE:positive+"rewind"})
        self.mark(positive+"rewind");self.rewind(descriptor);self.go(positive)
        self.mark(zero);self.rewind(descriptor);self.go(finish)
        self.mark(positive);self.unary(descriptor,output)
        self.mark(finish)

    def double(self, tape):
        """Positive binary multiplication by two using one-bit pending control."""
        states=(self.fresh("shift_zero"),self.fresh("shift_one"))
        end=self.fresh("shift_done")
        self.go(states[0])
        for pending in (0,1):
            self.mark(states[pending])
            branches={bit:states[pending]+bit for bit in (ZERO,ONE)}
            if pending==1:branches[BLANK]=end
            self.read(tape,branches)
            for value,bit in enumerate((ZERO,ONE)):
                self.mark(states[pending]+bit)
                self.write(tape,str(pending));self.move(tape,1);self.go(states[value])
        self.mark(end);self.write(tape,ONE);self.rewind(tape)

    def multiply_constant(self, source, target, factor):
        need(type(factor) is int and factor>=0,"finite nonnegative multiplier")
        self.empty(target)
        if factor==0:
            self.write(target,ZERO)
            return
        self.canonical(source,positive=True)
        states=[self.fresh("multiply_carry") for _ in range(factor)]
        end=self.fresh("multiply_done")
        self.go(states[0])
        for carry in range(factor):
            self.mark(states[carry])
            self.read(source,{ZERO:states[carry]+ZERO,ONE:states[carry]+ONE,BLANK:states[carry]+"end"})
            for value,bit in enumerate((ZERO,ONE)):
                self.mark(states[carry]+bit)
                total=factor*value+carry
                self.write(target,str(total%2));self.move(target,1);self.move(source,1)
                self.go(states[total//2])
            self.mark(states[carry]+"end")
            if carry:
                for bit in bin(carry)[2:][::-1]:
                    self.write(target,bit);self.move(target,1)
            self.go(end)
        self.mark(end);self.rewind(source);self.rewind(target)

    def add(self, left, right, target):
        self.empty(target)
        states=(self.fresh("add_zero"),self.fresh("add_one"))
        end=self.fresh("add_done")
        self.go(states[0])
        for carry in (0,1):
            self.mark(states[carry])
            self.read(left,{a:states[carry]+"left"+a for a in (ZERO,ONE,BLANK)})
            for a in (ZERO,ONE,BLANK):
                base=states[carry]+"left"+a
                self.mark(base)
                self.read(right,{b:base+"right"+b for b in (ZERO,ONE,BLANK)})
                for bit in (ZERO,ONE,BLANK):
                    self.mark(base+"right"+bit)
                    if a==BLANK and bit==BLANK and carry==0:
                        self.go(end)
                        continue
                    total=int(a==ONE)+int(bit==ONE)+carry
                    self.write(target,str(total%2));self.move(target,1)
                    if a!=BLANK:self.move(left,1)
                    if bit!=BLANK:self.move(right,1)
                    self.go(states[total//2])
        self.mark(end);self.rewind(left);self.rewind(right);self.rewind(target)

    def compare(self, left, right, less, equal, greater):
        """LSF comparison remembers the most recent differing (higher) bit."""
        states={v:self.fresh("compare") for v in (-1,0,1)}
        ends={-1:less,0:equal,1:greater}
        self.go(states[0])
        for previous in (-1,0,1):
            self.mark(states[previous])
            self.read(left,{a:states[previous]+a for a in (ZERO,ONE,BLANK)})
            for a in (ZERO,ONE,BLANK):
                base=states[previous]+a
                self.mark(base)
                self.read(right,{b:base+b for b in (ZERO,ONE,BLANK)})
                for b in (ZERO,ONE,BLANK):
                    self.mark(base+b)
                    if a==BLANK or b==BLANK:
                        result=previous if a==b else (-1 if a==BLANK else 1)
                        self.rewind(left);self.rewind(right);self.go(ends[result])
                    else:
                        following=previous if a==b else (-1 if a<b else 1)
                        self.move(left,1);self.move(right,1);self.go(states[following])

    def row_extent(self):
        within=dict(SCHEMA)["within_bits"]
        record=dict(SCHEMA)["record_bits"]
        guide=QUOT_ROWS
        self.empty(guide);self.empty(TEMP)
        self.canonical(record,positive=True)
        self.clear(ROWBITS);self.copy(record,ROWBITS)
        self.unary_zero(within,guide)
        loop,more,end=(self.fresh("extent") for _ in range(3))
        self.mark(loop);self.read(guide,{ONE:more,BLANK:end})
        self.mark(more);self.double(ROWBITS);self.move(guide,1);self.go(loop)
        self.mark(end);self.clear(guide);self.clear(TEMP)

    def cutoff_guard(self, rank):
        self.empty(CONSTANT)
        for bit in bin(rank)[2:][::-1]:
            self.write(CONSTANT,bit);self.move(CONSTANT,1)
        self.rewind(CONSTANT)
        cutoff=dict(SCHEMA)["cutoff"]
        self.canonical(cutoff,positive=True)
        good=self.fresh("valid_global_cutoff")
        self.compare(cutoff,CONSTANT,"reject",good,good)
        self.mark(good);self.clear(CONSTANT)

    def derive_geometry(self, rank, child):
        """Rank-one child: e'=f, s'=program_start; then f',r',s'+r'K."""
        need(type(rank) is int and rank>=2,"fixed final-template rank")
        ports=dict(SCHEMA)
        f,e,entry,active,rem,k=(ports[name] for name in
                              ("f","selected_axes","entry_start","active_start","remainder","K"))
        if child:
            self.clear(e);self.copy(f,e)
            self.clear(entry);self.copy(active,entry)
        self.clear(f);self.clear(rem);self.clear(active)
        self.divide_constant(e,f,rank,exact=False,remainder=rem)
        self.empty(OFFSET);self.write(OFFSET,ZERO)
        self.empty(GUIDE_S);self.empty(TEMP);self.unary_zero(rem,GUIDE_S)
        loop,more,end=(self.fresh("remainder_offset") for _ in range(3))
        self.mark(loop);self.read(GUIDE_S,{ONE:more,BLANK:end})
        self.mark(more)
        self.add(OFFSET,k,CONSTANT)
        self.clear(OFFSET);self.copy(CONSTANT,OFFSET);self.clear(CONSTANT)
        self.move(GUIDE_S,1);self.go(loop)
        self.mark(end);self.clear(GUIDE_S)
        self.add(entry,OFFSET,active);self.clear(OFFSET)

    def encode(self, fields, target):
        """Fixed schema: length prefix 1^ell 0 followed by ell LSF digits."""
        self.empty(target)
        for field in fields:
            self.canonical(field)
            loop, unit, end = (self.fresh("length") for _ in range(3))
            self.mark(loop)
            self.read(field, {ZERO: unit, ONE: unit, BLANK: end})
            self.mark(unit)
            self.write(target, ONE)
            self.move(target, 1)
            self.move(field, 1)
            self.go(loop)
            self.mark(end)
            self.write(target, ZERO)
            self.move(target, 1)
            self.rewind(field)
            loop, zero, one, end = (self.fresh("digits") for _ in range(4))
            self.mark(loop)
            self.read(field, {ZERO: zero, ONE: one, BLANK: end})
            for label, bit in ((zero, ZERO), (one, ONE)):
                self.mark(label)
                self.write(target, bit)
                self.move(field, 1)
                self.move(target, 1)
                self.go(loop)
            self.mark(end)
            self.rewind(field)
        self.rewind(target)

    def decode(self, source, fields):
        self.empty(LENGTH)
        for field in fields:
            self.empty(field)
            first = self.fresh("positive_length")
            self.read(source, {ONE: first})
            self.mark(first)
            loop, unit, end = (self.fresh("read_length") for _ in range(3))
            self.mark(loop)
            self.read(source, {ONE: unit, ZERO: end})
            self.mark(unit)
            self.write(LENGTH, ONE)
            self.move(LENGTH, 1)
            self.move(source, 1)
            self.go(loop)
            self.mark(end)
            self.move(source, 1)
            self.rewind(LENGTH)
            loop, digit, zero, one, end = (self.fresh("read_digits") for _ in range(5))
            self.mark(loop)
            self.read(LENGTH, {ONE: digit, BLANK: end})
            self.mark(digit)
            self.read(source, {ZERO: zero, ONE: one})
            for label, bit in ((zero, ZERO), (one, ONE)):
                self.mark(label)
                self.write(field, bit)
                self.move(field, 1)
                self.move(source, 1)
                self.move(LENGTH, 1)
                self.go(loop)
            self.mark(end)
            self.rewind(field)
            self.canonical(field)
            self.clear(LENGTH)
        exact = self.fresh("exact_header")
        self.read(source, {BLANK: exact})
        self.mark(exact)
        self.rewind(source)

    def divisible_guides(self, rows, stock):
        loop, r_more, s_more, restart, end = (self.fresh("stock") for _ in range(5))
        self.mark(loop)
        self.read(rows, {ONE: r_more, BLANK: end})
        self.mark(r_more)
        self.read(stock, {ONE: s_more, BLANK: restart})
        self.mark(s_more)
        self.move(rows, 1)
        self.move(stock, 1)
        self.go(loop)
        self.mark(restart)
        self.rewind(stock)
        self.go(loop)
        self.mark(end)
        exact = self.fresh("complete_stock")
        self.read(stock, {BLANK: exact})
        self.mark(exact)
        self.rewind(rows)
        self.rewind(stock)

    def close(self):
        self.code.append(("done",))
        self.mark("reject")
        self.code.append(("reject",))
        self.mark("quarantine")
        self.code.append(("quarantine",))
        return self.finish()


def compile_prepare(divisor, kind=ROW_CHILD, rank=None, root=False):
    need(kind == ROW_CHILD, "matched-fields occurrence must not split rows")
    b = Builder()
    fields = tuple(port for _, port in SCHEMA)
    for port in (HEADER, CHILD_HEADER, LENGTH, QUOT_ROWS, QUOT_STOCK,
                 TEMP, GUIDE_S, OFFSET, CONSTANT, *fields):
        b.boundary(port)
    b.decode(HEADER, fields)
    if rank is not None:
        b.cutoff_guard(rank)
        fast=b.fresh("actual_fast_child")
        width=dict(SCHEMA)["selected_axes" if root else "f"]
        b.compare(width,dict(SCHEMA)["cutoff"],"reject","reject",fast)
        b.mark(fast)
        if root:
            b.row_extent()
        b.derive_geometry(rank,child=not root)
    b.divide_constant(ROWS, QUOT_ROWS, divisor)
    b.divide_constant(STOCK, QUOT_STOCK, divisor)
    replacements = {ROWS: QUOT_ROWS, STOCK: QUOT_STOCK}
    b.encode(tuple(replacements.get(port, port) for port in fields), CHILD_HEADER)
    for port in (*fields, QUOT_ROWS, QUOT_STOCK):
        b.clear(port)
    return b.close()


def compile_row_extent():
    b=Builder()
    for port in (16,17,ROWBITS,QUOT_ROWS,TEMP):b.boundary(port)
    b.row_extent()
    return b.close()


def compile_leaf(rank):
    """Actual requested-child test f<=t, t=max(N,floor(h^eta)) supplied globally."""
    need(type(rank) is int and rank>=2,"fixed final-template rank")
    b=Builder()
    fields=tuple(port for _,port in SCHEMA)
    for port in (HEADER,LENGTH,CONSTANT,*fields):b.boundary(port)
    b.decode(HEADER,fields);b.cutoff_guard(rank)
    f=dict(SCHEMA)["f"];cutoff=dict(SCHEMA)["cutoff"]
    b.canonical(f,positive=True)
    leaf,internal=b.fresh("elementary_child"),b.fresh("recursive_child")
    b.compare(f,cutoff,leaf,leaf,internal)
    for label,value in ((leaf,True),(internal,False)):
        b.mark(label)
        for port in fields:b.clear(port)
        b.code.append(("result",value))
    return b.close()


def compile_router(divisor, merge=False):
    """Uses CHILD header (rows=R/divisor); split and merge have inverse order."""
    need(type(divisor) is int and divisor > 0, "fixed positive divisor")
    b = Builder()
    roles = tuple(range(FIRST_ROLE, FIRST_ROLE + divisor))
    fields = tuple(port for _, port in SCHEMA)
    for port in (SOURCE, OUTPUT, HEADER, LENGTH, TEMP, GUIDE_C, GUIDE_R,
                 GUIDE_J, GUIDE_S, *fields, *roles):
        b.boundary(port)
    b.decode(HEADER, fields)
    for descriptor, guide in ((OUTER, GUIDE_C), (ROWS, GUIDE_R),
                              (ROWBITS, GUIDE_J), (STOCK, GUIDE_S)):
        b.empty(guide)
        b.unary(descriptor, guide)
    b.divisible_guides(GUIDE_R, GUIDE_S)
    if merge:
        b.empty(OUTPUT)
    else:
        for role in roles:
            b.empty(role)
    prefix, group, next_prefix, finish = (b.fresh("route") for _ in range(4))
    phases = tuple(b.fresh("role") for _ in roles)
    b.mark(prefix)
    b.read(GUIDE_C, {ONE: group, BLANK: finish})
    b.mark(group)
    b.read(GUIDE_R, {ONE: phases[0], BLANK: next_prefix})
    for index, role in enumerate(roles):
        b.mark(phases[index])
        source, target = (role, OUTPUT) if merge else (SOURCE, role)
        loop, bit, zero, one, row_done = (b.fresh("row") for _ in range(5))
        b.mark(loop)
        b.read(GUIDE_J, {ONE: bit, BLANK: row_done})
        b.mark(bit)
        b.read(source, {ZERO: zero, ONE: one})
        for label, value in ((zero, ZERO), (one, ONE)):
            b.mark(label)
            b.empty(target)
            b.write(target, value)
            if merge:
                b.write(source, BLANK)
            b.move(source, 1)
            b.move(target, 1)
            b.move(GUIDE_J, 1)
            b.go(loop)
        b.mark(row_done)
        b.rewind(GUIDE_J)
        if index + 1 == divisor:
            b.move(GUIDE_R, 1)
            b.go(group)
        else:
            b.go(phases[index + 1])
    b.mark(next_prefix)
    b.rewind(GUIDE_R)
    b.move(GUIDE_C, 1)
    b.go(prefix)
    b.mark(finish)
    for port in roles if merge else (SOURCE,):
        exact = b.fresh("exact_payload")
        b.read(port, {BLANK: exact})
        b.mark(exact)
    for port in (*roles, OUTPUT) if merge else (SOURCE, *roles):
        b.rewind(port)
    for port in (GUIDE_C, GUIDE_R, GUIDE_J, GUIDE_S, TEMP, *fields):
        b.clear(port)
    return b.close()


class PhysicalPort:
    """Raw physical binary adapter: bypasses virtual codewords/blanks."""
    def __init__(self, tape, marker=2):
        self.tape = tape
        self.marker = marker

    def read(self):
        symbol = self.tape.read()
        need(symbol in (0, 1, 6, self.marker), "raw physical row alphabet")
        return {0: ZERO, 1: ONE, 6: BLANK, self.marker: LEFT}[symbol]

    def write(self, symbol):
        self.tape.write({ZERO: 0, ONE: 1, BLANK: 6, LEFT: self.marker}[symbol])

    def move(self, direction):
        self.tape.move(direction)


def run_choice(program, ports, limit=None):
    """Return a fixed terminal label and observer count; no numeric decoding."""
    pc = steps = 0
    while True:
        if limit is not None and steps >= limit:
            raise ValueError("observer step limit")
        row = program[pc]
        op = row[0]
        steps += 1
        if op == "done":
            return None, steps
        if op == "result":
            return row[1], steps
        if op in ("reject", "quarantine"):
            raise ValueError("row program " + op)
        if op == "goto":
            pc = row[1]
            continue
        port = ports[row[1]]
        if op == "read":
            symbol = port.read()
            need(symbol in row[2], "foreign row symbol")
            pc = row[2][symbol]
            continue
        if op == "write":
            port.write(row[2])
        elif op == "move":
            port.move(row[2])
        else:
            raise ValueError("unknown local instruction")
        pc += 1


def run(program, ports, limit=None):
    """Returned step count is an observer, never a control register."""
    result, steps = run_choice(program, ports, limit)
    need(result is None, "ordinary local table has no decision terminal")
    return steps


def occurrence(ambient, active, child_ambient, kind=MATCHED):
    """Static #6878 constructor; neither payload nor numerical input is read."""
    need(kind == MATCHED, "coordinate occurrence is a matched-field event")
    order = geometry.stable_prefix(ambient, tuple(active))
    need(len(active) <= child_ambient <= ambient, "complete child ambient")
    swaps = tuple(geometry.swap_word(order))
    return {"kind": kind, "ambient": ambient, "active": tuple(active),
            "child_ambient": child_ambient, "order": order,
            "entry": swaps, "return": tuple(reversed(swaps)),
            "selected_xor_calls": 6 * len(swaps), "row_divisor": 1}


def compile_occurrence(bindings, ambient, requests, child_ambient):
    """Full-field #6878 conjugations surround ONE complete matched native word."""
    need(len(bindings)==len(requests)>0,"all native matched fields")
    need(len(set(bindings))==len(bindings),"distinct source matched bindings")
    layouts=tuple(occurrence(ambient,active,child_ambient) for active in requests)
    out=[]
    for field,layout in zip(bindings,layouts):
        for a,b in layout["entry"]:
            out.extend(("xor",field,x,y) for x,y in ((a,b),(b,a),(a,b)))
    out.append(("native",tuple(bindings)))
    for field,layout in reversed(tuple(zip(bindings,layouts))):
        for a,b in layout["return"]:
            out.extend(("xor",field,x,y) for x,y in ((a,b),(b,a),(a,b)))
    need(sum(row[0]=="xor" for row in out)==sum(x["selected_xor_calls"] for x in layouts),
         "complete occurrence address invoice")
    return tuple(out),layouts
