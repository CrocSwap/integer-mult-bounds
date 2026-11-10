"""Fixed scalar services compiled to the unchanged lifecycle table ABI.

All arithmetic here belongs to finite-template construction. The returned
runtime uses only branch/write/unit-move/goto/halt/reject instructions.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import deque
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Builder:
    def __init__(self):
        self.rows, self.labels = [], {}
        self.pending, self.claimed = deque(), set()

    def request(self, key):
        if key not in self.claimed:
            self.claimed.add(key)
            self.pending.append(key)
        return key

    def mark(self, key):
        need(key not in self.labels, "unique compiled state")
        self.labels[key] = len(self.rows)

    def emit(self, *row):
        self.rows.append(row)

    def goto(self, key):
        self.emit("goto", self.request(key))

    def branch(self, port, cases, default):
        self.emit("branch", port,
                  tuple((s, self.request(k)) for s,k in sorted(cases.items())),
                  self.request(default))

    def finish(self):
        need(not self.pending, "complete finite graph")
        out = []
        for row in self.rows:
            if row[0] == "goto":
                out.append(("goto", self.labels[row[1]]))
            elif row[0] == "branch":
                out.append(("branch", row[1], tuple((s,self.labels[k]) for s,k in row[2]),
                            self.labels[row[3]]))
            else:
                out.append(row)
        return tuple(out)


def compile_scalar(op, coefficient):
    """Build a table for all complete complex records on one common grid.

    SCALE ports: target, output-work, guide-work.
    ADD ports: target, source, output-work, guide-work.
    Additional supplied work/context ports are untouched. Work is physically
    retired by the unchanged Controller.primitive success wrapper.
    """
    need(op in ("ADD", "SCALE"), "scalar operation")
    q = Fraction(coefficient)
    need(q != 0, "nonzero selected scalar")
    a, denominator = q.numerator, q.denominator
    d, odd = 0, denominator
    while odd % 2 == 0:
        d += 1
        odd //= 2
    p, r = (denominator,a) if op == "ADD" else (a,0)
    count = 2 if op == "ADD" else 1
    output, guide = count, count+1
    bound = abs(p)+abs(r)+odd
    b, carry_states = Builder(), set()
    b.request(("entry",))

    def advance_inputs():
        for port in range(count):
            b.emit("move", port, 1)

    def guide_one():
        b.emit("write", guide, 1)
        b.emit("move", guide, 1)

    def digit(k, carry, last_q, x, y):
        need(0 <= k <= d and abs(carry) <= bound, "finite carry invariant")
        carry_states.add(carry)
        value = p*x+r*y+carry
        if k < d:
            if value % 2:
                return None
            return k+1, value//2, last_q
        bit = value & 1
        following = (value-odd*bit)//2
        need(abs(following) <= bound, "closed finite carry interval")
        b.emit("write", output, bit)
        b.emit("move", output, 1)
        return d, following, bit

    while b.pending:
        key = b.pending.popleft()
        b.mark(key)
        tag = key[0]
        if tag == "entry":
            b.branch(output, {4:("guide-entry",)}, ("reject","nonblank output work"))
        elif tag == "guide-entry":
            b.branch(guide, {4:("begin",)}, ("reject","nonblank guide work"))
        elif tag == "begin":
            b.emit("write", guide, 5)
            b.emit("move", guide, 1)
            b.goto(("start",0,False))
        elif tag == "start":
            _, parity, seen = key
            ending = ("finish-source",) if parity == 0 and seen else ("reject","complete nonempty complex field")
            b.branch(0, {0:("read-source",0,0,2,parity,0),
                         1:("read-source",0,0,2,parity,1), 4:ending},
                     ("reject","positive component width"))
        elif tag == "scan":
            _, k, carry, sx, sy, sq, parity = key
            b.branch(0, {0:("read-source",k,carry,sq,parity,0),
                         1:("read-source",k,carry,sq,parity,1),
                         2:("component-end",k,carry,sx,sy,sq,parity)},
                     ("reject","unterminated signed component"))
        elif tag == "read-source":
            _, k, carry, sq, parity, x = key
            if count == 2:
                b.branch(1, {y:("digit",k,carry,sq,parity,x,y) for y in (0,1)},
                         ("reject","same complete component shape"))
            else:
                b.goto(("digit",k,carry,sq,parity,x,0))
        elif tag == "digit":
            _, k, carry, sq, parity, x, y = key
            following = digit(k,carry,sq,x,y)
            if following is None:
                b.goto(("reject","inexact low numerator bits"))
            else:
                k1,c1,q1 = following
                guide_one()
                advance_inputs()
                b.goto(("scan",k1,c1,x,y,q1,parity))
        elif tag == "component-end":
            _, k, carry, sx, sy, sq, parity = key
            following = ("extend",d,k,carry,sx,sy,sq,parity)
            if count == 2:
                b.branch(1, {2:following}, ("reject","same complete component shape"))
            else:
                b.goto(following)
        elif tag == "extend":
            _, remaining, k, carry, sx, sy, sq, parity = key
            if remaining:
                following = digit(k,carry,sq,sx,sy)
                if following is None:
                    b.goto(("reject","inexact sign-extension numerator bits"))
                else:
                    k1,c1,q1 = following
                    b.goto(("extend",remaining-1,k1,c1,sx,sy,q1,parity))
            elif sq not in (0,1) or carry != p*sx+r*sy-odd*sq:
                b.goto(("reject","inexact quotient or signed output overflow"))
            else:
                b.emit("write", output, 2)
                b.emit("move", output, 1)
                guide_one()
                advance_inputs()
                b.goto(("start",parity^1,True))
        elif tag == "finish-source":
            if count == 2:
                b.branch(1, {4:("finish-output",)}, ("reject","same complete field frontier"))
            else:
                b.goto(("finish-output",))
        elif tag == "finish-output":
            b.branch(output, {4:("rewind-step",)}, ("reject","exact staged output frontier"))
        elif tag == "rewind-step":
            b.emit("move", guide, -1)
            b.goto(("rewind-read",))
        elif tag == "rewind-read":
            b.branch(guide, {1:("rewind-inputs",),5:("install-start",)},
                     ("reject","complete unary rewind guide"))
        elif tag == "rewind-inputs":
            for port in tuple(range(count))+(output,):
                b.emit("move", port, -1)
            b.goto(("rewind-step",))
        elif tag == "install-start":
            b.emit("move", guide, 1)
            b.goto(("install-guide",))
        elif tag == "install-guide":
            b.branch(guide, {1:("install-read",),4:("installed-target-end",)},
                     ("reject","install guide format"))
        elif tag == "install-read":
            b.branch(output, {s:("install-symbol",s) for s in (0,1,2)},
                     ("reject","complete protected numeric output"))
        elif tag == "install-symbol":
            b.emit("write", 0, key[1])
            for port in (0,output,guide):
                b.emit("move", port, 1)
            b.goto(("install-guide",))
        elif tag == "installed-target-end":
            b.branch(0, {4:("installed-output-end",)}, ("reject","exact installed target frontier"))
        elif tag == "installed-output-end":
            b.branch(output, {4:("halt",)}, ("reject","exact consumed protected output"))
        elif tag == "halt":
            b.emit("halt")
        elif tag == "reject":
            b.emit("reject", key[1])
        else:
            raise ValueError("unknown compiler state")
    return b.finish(), dict(operation=op,coefficient=str(q),denominator_twos=d,
                           odd_denominator=odd,numerator_target=p,numerator_source=r,
                           carry_bound=bound,carry_states=len(carry_states),
                           rows=len(b.rows),states=len(b.labels),public_ports=count,work_ports=2)


def source_literal(event, word, caller=None):
    """Authenticate a source scalar retained by source_ir's nested remappings.

    Fields stay the source lowerer's actual ordered binding. Whole-job native
    normalizers and two-output SWAP/SIGNED_SWAP services remain outside scope.
    """
    need(event.op == "SERVICE", "only original scalar SERVICE")
    token = event.token
    wrappers = {'caller-local':4, 'product-left':4,
                'product-right':5, 'unit-fragment':6}
    while isinstance(token,(tuple,list)) and token:
        if len(token) == 1 and isinstance(token[0],(tuple,list)):
            token = token[0]  # The source remap API's empty context.
            continue
        if isinstance(token[0],str) and token[0] in wrappers:
            need(len(token)==wrappers[token[0]],'source remap wrapper grammar')
            # product-right also retains an issuing PAID token as provenance.
            # Only the last member is the instruction currently being remapped.
            token = token[-1]
            continue
        break
    need(isinstance(token,(tuple,list)) and token and isinstance(token[0],str)
         and token[0] in ('local','boundary-right','boundary-left','outer','query-add'),
         'source scalar origin grammar')
    tag = token[0]
    if tag == 'local':
        need(len(token)==3,'local scalar token grammar')
        _,pc,raw = token
        need(type(pc) is int and 0 <= pc < len(word['program']), "actual current source event")
        need(tuple(raw) == tuple(word['program'][pc]), "exact current scalar source bytes")
        q, origin = Fraction(raw[-2]), ('local',pc)
    else:
        need(caller is not None,'outer scalar requires exact caller source')
        if tag in ('boundary-right','boundary-left'):
            need(len(token)==3,'boundary scalar token grammar')
            _,column,raw = token
            rows = caller['boundaries'][tag.split('-')[1]+'_program']
            need(tuple(raw) in tuple(tuple(x) for x in rows),'actual boundary scalar instruction')
            origin = (tag,column)
        elif tag == 'outer':
            need(len(token)==4,'outer scalar token grammar')
            _,site,column,raw = token
            need(type(site) is int and 0 <= site < len(caller['physical_events']),
                 'actual outer source site')
            need(tuple(raw)==tuple(caller['physical_events'][site]),'exact outer scalar instruction')
            origin = (tag,site,column)
        else:
            need(len(token)==5 and token[1]=='query','query scalar token grammar')
            _,_,site,stage,column = token
            need(type(site) is int and 0 <= site < len(caller['physical_events']),
                 'actual query source site')
            original = caller['physical_events'][site]
            need(original[0]=='QUERY_SHEAR' and original[1]==stage and original[3] is False,
                 'actual forward source query')
            raw = ('ADD',None,None,1)
            origin = (tag,site,column)
        need(type(column) is int and 0 <= column < 104,'actual source scalar column')
        need(raw[0] in ('ADD','SCALE'),'original source arithmetic scalar')
        q = Fraction(raw[-1])
    op = raw[0]
    need(op in ("ADD","SCALE"), "original scalar kind")
    arity = 2 if op == "ADD" else 1
    need(len(event.fields) == arity and len(set(event.fields)) == arity,
         "distinct actual scalar field ports")
    need(q != 0, "nonzero source coefficient")
    return op,q,origin


def bind_services(events, word, caller=None):
    """Bind precisely the supplied source scalar events to finite tables."""
    cache, services, receipt = {}, {}, []
    for event in events:
        op,q,origin = source_literal(event,word,caller)
        key = (op,q)
        if key not in cache:
            cache[key] = compile_scalar(op,q)
        table,_ = cache[key]
        token = event.token
        need(token not in services or services[token] == table, "unambiguous scalar service token")
        services[token] = table
        receipt.append((origin,op,str(q),tuple(event.fields)))
    return services, tuple(cache[key][1] for key in sorted(cache)), tuple(receipt)
