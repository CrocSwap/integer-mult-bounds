"""Finite one-head tape machines for S008. Builders run before any input is seen.

An instruction branches on the symbol beneath one head. A transition can copy
or xor scanned bits, write a fixed letter, and move each head one cell or stay.
Only the separate simulator sees head coordinates.
"""
from dataclasses import dataclass, field

BLANK, HOME, MARK, HALT = ".", "^", "*", -1

@dataclass(frozen=True)
class Action:
    target: int
    writes: tuple = ()
    moves: tuple = ()

@dataclass
class Rule:
    tape: str | None = None
    cases: dict = field(default_factory=dict)
    default: Action | None = None
    name: str = ""

class Builder:
    def __init__(self):
        self.rules = []

    def label(self, name=""):
        pos = len(self.rules)
        self.rules.append(Rule(name=name))
        return pos

    def put(self, pos, target, writes=(), moves=()):
        self.rules[pos].default = Action(target, writes, moves)
        return pos

    def sel(self, pos, tape, cases, default=None):
        self.rules[pos].tape = tape
        self.rules[pos].cases = cases
        self.rules[pos].default = default
        return pos

    def op(self, target, writes=(), moves=(), name="control"):
        return self.put(self.label(name), target, writes, moves)

    def test(self, tape, cases, name="test"):
        return self.sel(self.label(name), tape,
                        {a: Action(nxt) for a, nxt in cases.items()})

    def rewind(self, tape, target):
        p = self.label("rewind")
        return self.sel(p, tape, {HOME: Action(target, moves=((tape, 1),))},
                        Action(p, moves=((tape, -1),)))

    def erase(self, tape, target):
        p = self.label("erase")
        return self.sel(p, tape, {BLANK: Action(self.rewind(tape, target))},
                        Action(p, ((tape, BLANK),), ((tape, 1),)))

    def transfer(self, src, dst, target, *, keep=False):
        p = self.label("transfer marks")
        writes = ((dst, MARK),) if keep else ((src, BLANK), (dst, MARK))
        return self.sel(p, src, {BLANK: Action(target), MARK:
            Action(p, writes, ((src, 1), (dst, 1)))})

    def scale_unary(self, src, temp, factor, extra, target):
        target = self.rewind(src, self.rewind(temp, target))
        target = self.transfer(temp, src, target)
        target = self.rewind(src, self.rewind(temp, target))
        if extra:
            target = self.op(target, ((temp, MARK),), ((temp, 1),), "extra")
        p = self.label("unary scale")
        more = p
        for _ in range(factor - 1):
            more = self.op(more, ((temp, MARK),), ((temp, 1),), "scale emit")
        return self.sel(p, src, {BLANK: Action(target), MARK:
            Action(more, ((src, BLANK), (temp, MARK)), ((src, 1), (temp, 1)))})

    def unary_from_binary(self, desc, out, temp, target):
        p = self.label("binary digit")
        cases = {BLANK: Action(self.rewind(desc, target))}
        for bit in (0, 1):
            cases[str(bit)] = Action(self.scale_unary(out, temp, 2, bit, p),
                                     moves=((desc, 1),))
        return self.sel(p, desc, cases)

    def divide3(self, src, temp, target):
        target = self.rewind(src, self.rewind(temp, target))
        target = self.transfer(temp, src, target)
        target = self.rewind(src, self.rewind(temp, target))
        a, b, c = [self.label("divide3") for _ in range(3)]
        for state, nxt in ((a, b), (b, c)):
            self.sel(state, src, {MARK: Action(nxt, ((src, BLANK),), ((src, 1),))})
        self.rules[a].cases[BLANK] = Action(target)
        self.sel(c, src, {MARK: Action(a, ((src, BLANK), (temp, MARK)),
                                       ((src, 1), (temp, 1)))})
        return a

    def unary_loop(self, tape, body, target):
        check = self.label("unary loop")
        advance = self.op(check, moves=((tape, 1),), name="unary advance")
        return self.sel(check, tape, {MARK: Action(body(advance)),
                              BLANK: Action(self.rewind(tape, target))})

    def run(self, tape, target, writes=(), moves=(), name="payload"):
        p = self.label(name)
        return self.sel(p, tape, {BLANK: Action(self.rewind(tape, target)),
                                 MARK: Action(p, writes, moves + ((tape, 1),))})

    def reset_group(self, tapes, target):
        for tape in reversed(tapes):
            target = self.rewind(tape, target)
        return target

LANES = tuple(f"lane{a}{c}" for a in range(3) for c in range(3))

def digit_pass(b, target):
    """[p][a=3][g][c=3][s] -> [p][c][g][a][s], in place on A."""
    def traversal(gather, after):
        top = b.label("prefix")
        continuation = top
        for outer in reversed(range(3)):
            def role(nxt, outer=outer):
                for inner in reversed(range(3)):
                    a, c = (outer, inner) if gather else (inner, outer)
                    lane = f"lane{a}{c}"
                    src, dst = ("A", lane) if gather else (lane, "A")
                    writes = ((dst, ("copy", src)),)
                    if not gather:
                        writes += ((src, BLANK),)
                    nxt = b.run("s", nxt, writes, ((src, 1), (dst, 1)))
                return nxt
            continuation = b.unary_loop("g", role, continuation)
        return b.sel(top, "A" if gather else "lane00", {BLANK: Action(after)},
                     Action(continuation))
    target = b.reset_group(("A",) + LANES, target)
    target = traversal(False, target)
    target = b.reset_group(("A",) + LANES, target)
    return traversal(True, target)

def boundaries(b, tapes, target, *, close):
    if close:
        clear = b.op(target, tuple((t, BLANK) for t in tapes),
                     tuple((t, 1) for t in tapes), "remove boundaries")
        return b.op(clear, moves=tuple((t, -1) for t in tapes), name="close")
    write = b.op(target, tuple((t, HOME) for t in tapes),
                 tuple((t, 1) for t in tapes), "write boundaries")
    return b.op(write, moves=tuple((t, -1) for t in tapes), name="open")

def build_direct():
    b = Builder()
    tapes = ("A", "E", "G", "S", "e", "g", "s", "work") + LANES
    finish = boundaries(b, tapes, HALT, close=True)
    clean = finish
    for t in ("e", "s", "g"):
        clean = b.erase(t, clean)
    clean = b.rewind("e", clean)
    after_digit = b.label("next trit")
    part = digit_pass(b, b.op(after_digit, moves=(("e", 1),)))
    b.sel(after_digit, "e", {BLANK: Action(clean), MARK:
          Action(b.divide3("s", "work", part))})
    scale = b.label("higher trits")
    scale_both = b.scale_unary("g", "work", 3, 0,
                  b.scale_unary("s", "work", 3, 0,
                                b.op(scale, moves=(("e", 1),))))
    b.sel(scale, "e", {MARK: Action(scale_both),
                       BLANK: Action(b.rewind("e", part))})
    setup = b.unary_from_binary("E", "e", "work", b.op(scale, moves=(("e", 1),)))
    setup = b.unary_from_binary("G", "g", "work", setup)
    setup = b.unary_from_binary("S", "s", "work", setup)
    first = b.test("E", {"0": finish, "1": setup}, "identity or exchange")
    return b, tapes, boundaries(b, tapes, first, close=False)

class Simulation:
    """Execute one transition per step. The rule sees only scanned symbols."""
    def __init__(self, prog, initial):
        self.builder, self.tapes, self.pc = prog
        self.tape = {t: dict(enumerate(initial.get(t, ""))) for t in self.tapes}
        self.head = dict.fromkeys(self.tapes, 0)
        self.lo, self.hi = self.head.copy(), self.head.copy()
        self.steps = 0

    def char(self, tape):
        return self.tape[tape].get(self.head[tape], BLANK)

    def step(self):
        rule = self.builder.rules[self.pc]
        act = rule.cases.get(self.char(rule.tape), rule.default) if rule.tape else rule.default
        if act is None:
            raise AssertionError((self.pc, rule.name, rule.tape, self.char(rule.tape)))
        values = []
        for tape, v in act.writes:
            if isinstance(v, tuple):
                op, *args = v
                if op == "copy":
                    v = self.char(args[0])
                elif op == "xor":
                    x, y = [self.char(t) for t in args]
                    assert x in ("0","1") and y in ("0","1")
                    v = str(int(x) ^ int(y))
                else:
                    raise AssertionError(op)
            values.append((tape,v))
        for tape, v in values:
            if v == BLANK:
                self.tape[tape].pop(self.head[tape], None)
            else:
                self.tape[tape][self.head[tape]] = v
        for tape, diff in act.moves:
            assert diff in (-1, 1)
            pos = self.head[tape] + diff
            self.head[tape] = pos
            self.lo[tape] = min(pos, self.lo[tape])
            self.hi[tape] = max(pos, self.hi[tape])
        self.pc = act.target
        self.steps += 1

    def execute(self, clock):
        while self.pc != HALT:
            if self.steps >= clock:
                raise AssertionError(f"clock {clock} expired")
            self.step()
        return self

    def contents(self, tape):
        cells = self.tape[tape]
        if not cells:
            return ""
        if min(cells) != 0 or len(cells) != max(cells) + 1:
            raise AssertionError(("noncontiguous", tape))
        return "".join(cells[i] for i in range(len(cells)))

    @property
    def visited(self):
        return sum(self.hi[t]-self.lo[t]+1 for t in self.tapes)

def complement(b, total, first, dest, target):
    """Write total-first-1 unary marks and reset the three heads."""
    target = b.reset_group((total, first, dest), target)
    target = b.transfer(total, dest, target, keep=True)
    p = b.label("count roles before selection")
    return b.sel(p, first, {MARK: Action(p, moves=((first,1),(total,1))),
              BLANK: Action(target, moves=((total,1),))})

def build_role(*, xor):
    """Copy/xor source role into destination role over every outer prefix."""
    b = Builder()
    tapes = ("A","Y","J","K","I","D","S","jb","kb","i","d","ja","ka","s","temp")
    finish = boundaries(b, tapes, HALT, close=True)
    for t in ("jb","kb","i","d","ja","ka","s"):
        finish = b.erase(t, finish)
    finish = b.reset_group(("A","Y"), finish)
    top = b.label("role prefix")
    def skip(nxt, dst, count):
        return b.unary_loop(count, lambda n: b.run("s", n, moves=((dst,1),)), nxt)
    nxt = skip(top, "Y", "ka")
    nxt = skip(nxt, "A", "ja")
    val = ("xor","A","Y") if xor else ("copy","A")
    nxt = b.run("s", nxt, (("Y",val),), (("A",1),("Y",1)))
    nxt = skip(nxt, "Y", "d")
    nxt = skip(nxt, "A", "i")
    b.sel(top,"A",{BLANK:Action(finish)},Action(nxt))
    first = complement(b,"jb","i","ja",complement(b,"kb","d","ka",top))
    for desc,out in reversed((("J","jb"),("K","kb"),("I","i"),("D","d"),("S","s"))):
        first = b.unary_from_binary(desc,out,"temp",first)
    return b,tapes,boundaries(b,tapes,first,close=False)

def shared_clean(b, tapes, unary, inputs, target=HALT):
    last = boundaries(b,tapes,target,close=True)
    for t in unary:
        last = b.erase(t,last)
    return b.reset_group(inputs,last)

def plain_copy(b, name, src, dst, target, *, clear=False):
    writes = ((dst, ("copy",src)),)
    if clear:
        writes += ((src,BLANK),)
    return b.run(name,target,writes,((src,1),(dst,1)))

def bit_move(b, target, *, inverse):
    lanes = ("zero","one")
    def sweep(run_length, gather, after):
        top = b.label("bit-lane prefix")
        nxt = top
        for lane in reversed(lanes):
            src,dst = ("A",lane) if gather else (lane,"A")
            nxt = plain_copy(b,run_length,src,dst,nxt,clear=not gather)
        return b.sel(top,"A" if gather else lanes[0],{BLANK:Action(after)},Action(nxt))
    first,last = ("d","z") if inverse else ("z","d")
    nxt = b.reset_group(("A",)+lanes,target)
    nxt = sweep(last,False,nxt)
    nxt = b.reset_group(("A",)+lanes,nxt)
    return sweep(first,True,nxt)

def divide2(b, src, temp, target):
    target=b.rewind(src,b.rewind(temp,target))
    target=b.transfer(temp,src,target)
    target=b.rewind(src,b.rewind(temp,target))
    a,c=b.label("divide2"),b.label("divide2")
    b.sel(a,src,{BLANK:Action(target),MARK:Action(c,((src,BLANK),),((src,1),))})
    b.sel(c,src,{MARK:Action(a,((src,BLANK),(temp,MARK)),((src,1),(temp,1)))})
    return a

def build_pack(*, inverse):
    b=Builder()
    tapes=("A","T","K","z","d","k","temp","zero","one")
    finish=boundaries(b,tapes,HALT,close=True)
    done=finish
    for t in ("k","d","z"):
        done=b.erase(t,done)
    done=b.rewind("k",done)
    after=b.label("packing digit")
    run=bit_move(b,b.op(after,moves=(("k",1),)),inverse=inverse)
    def double(nxt):
        return b.scale_unary("z","temp",2,0,b.scale_unary("d","temp",2,0,nxt))
    change = divide2(b,"z","temp",divide2(b,"d","temp",run)) if inverse else double(run)
    b.sel(after,"k",{BLANK:Action(done),MARK:Action(change)})
    start_run=run
    if inverse:
        grow=b.label("pack preparation")
        b.sel(grow,"k",{BLANK:Action(b.rewind("k",run)),MARK:
                    Action(double(b.op(grow,moves=(("k",1),))))})
        start_run=b.op(grow,moves=(("k",1),))
    # d initially measures one bit.
    start=b.op(start_run,(("d",MARK),))
    start=b.unary_from_binary("K","k","temp",start)
    start=b.unary_from_binary("T","z","temp",start)
    start=b.test("K",{"0":finish,"1":start},"identity or pack")
    return b,tapes,boundaries(b,tapes,start,close=False)

def build_padding(*, inverse):
    """Given W,U in binary, derive B=least 3^ell>=W and C=W*ceil(B/W)."""
    b=Builder()
    tapes=("A","Y","W","U","w","u","b","extra","temp")
    done=shared_clean(b,tapes,("w","u","b","extra"),("A","Y"))
    top=b.label("pad prefix")
    nxt=b.unary_loop("extra",lambda n: b.run("u",n,
             writes=() if inverse else (("Y","0"),),
             moves=(("A" if inverse else "Y",1),)),top)
    nxt=b.unary_loop("b",lambda n: plain_copy(b,"u","A","Y",n),nxt)
    b.sel(top,"A",{BLANK:Action(done)},Action(nxt))
    reset=b.reset_group(("w","b","extra"),top)
    add=b.transfer("w","extra",reset,keep=True)
    mod=b.label("batch remainder")
    use=b.label("batch step")
    b.sel(use,"w",{BLANK:Action(b.rewind("w",use)),
                    MARK:Action(mod,moves=(("w",1),("b",1)))})
    b.sel(mod,"b",{BLANK:Action(add),MARK:Action(use)})
    # At B end, w points to the first omitted slot, or to blank for a full W.
    bigger=b.label("compare W and ternary power")
    testb=b.label("is power exhausted")
    too_small=b.reset_group(("w","b"),b.scale_unary("b","temp",3,0,bigger))
    b.sel(testb,"b",{BLANK:Action(too_small),
                     MARK:Action(bigger,moves=(("w",1),("b",1)))})
    b.sel(bigger,"w",{BLANK:Action(b.reset_group(("w","b"),mod)),
                      MARK:Action(testb)})
    setup=b.op(bigger,(("b",MARK),))
    setup=b.unary_from_binary("U","u","temp",setup)
    setup=b.unary_from_binary("W","w","temp",setup)
    return b,tapes,boundaries(b,tapes,setup,close=False)

def build_tag(*, inverse):
    """Append comparison trits to [P][t][g][t][s] records of width H."""
    b=Builder()
    tapes=("A","Y","T","G","S","H","t","g","s","h","temp")
    finish=shared_clean(b,tapes,("t","g","s","h"),("A","Y"))
    prefix=b.label("tag prefix")
    per_x=b.label("earlier physical field")
    move_marker=b.label("advance threshold")
    after_marker=b.label("next threshold")
    reset_mark=b.rewind("t",b.op(prefix,(("t","@"),)))
    b.sel(after_marker,"t",{BLANK:Action(reset_mark),
               MARK:Action(b.rewind("t",per_x),(("t","@"),))})
    b.sel(move_marker,"t",{MARK:Action(move_marker,moves=(("t",1),)),
              "@":Action(after_marker,(("t",MARK),),(("t",1),))})
    def each_y(nxt):
        end=b.rewind("t",nxt)
        earlier,later=b.label("y before threshold"),b.label("y after threshold")
        def records(trit,target):
            if inverse:
                trit=(-trit)%3
            def emit(n):
                n=b.op(n,(("Y",str(trit%2)),),(("Y",1),))
                n=b.op(n,(("Y",str(trit//2)),),(("Y",1),))
                return plain_copy(b,"h","A","Y",n)
            return b.unary_loop("s",emit,b.op(target,moves=(("t",1),)))
        b.sel(earlier,"t",{MARK:Action(records(2,earlier)),
                           "@":Action(records(0,later))})
        b.sel(later,"t",{MARK:Action(records(1,later)),BLANK:Action(end)})
        return earlier
    gloop=b.unary_loop("g",each_y,move_marker)
    b.put(per_x,gloop)
    b.sel(prefix,"A",{BLANK:Action(finish)},Action(per_x))
    first=b.op(prefix,(("t","@"),))
    for desc,out in reversed((("T","t"),("G","g"),("S","s"),("H","h"))):
        first=b.unary_from_binary(desc,out,"temp",first)
    return b,tapes,boundaries(b,tapes,first,close=False)
