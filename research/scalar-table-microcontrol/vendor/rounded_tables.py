"""Literal finite-table total rounded scalars on the unchanged lifecycle ABI.

Only construction computes residues/quotients in Python. Runtime tables
contain branch/write/unit-move/goto/halt/reject, with no payload callbacks.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from source_binding import need, vendor

_old = vendor("rounded_frozen_scalar_builder", "vendor/exact_scalar_tables.py")
Builder = _old.Builder


def compile_rounded(op, coefficient):
    """Fixed a/b; all finite nonempty fields of signed complete components.

    SCALE ports: target, output-work, guide-work.
    ADD ports: target, source, output-work, guide-work; distinct public tapes.
    Same grid/shape is a premise. Every component is staged before public
    installation. Correctly shaped inputs reject only on signed output overflow.
    """
    need(op in ("SCALE", "ADD"), "rounded scalar operation")
    q = Fraction(coefficient)
    a, denominator = q.numerator, q.denominator
    d, odd = 0, denominator
    while odd % 2 == 0:
        odd //= 2; d += 1
    offset = denominator // 2
    p, r = (denominator, a) if op == "ADD" else (a, 0)
    count = 2 if op == "ADD" else 1
    output, guide = count, count + 1
    bound = abs(p) + abs(r) + odd + offset
    b = Builder(); b.request(("entry",))
    carry_states, residue_states = set(), set()

    def advance_inputs(step=1):
        for port in range(count):
            b.emit("move", port, step)

    def guide_one():
        b.emit("write", guide, 1); b.emit("move", guide, 1)

    def digit(k, carry, x, y):
        need(0 <= k <= d and abs(carry) <= bound, "finite carry invariant")
        carry_states.add(carry)
        value = p * x + r * y + carry
        bit = value & 1
        following = (value - odd * bit) // 2
        need(abs(following) <= bound, "closed signed carry interval")
        if k < d:
            return k + 1, following, bit
        b.emit("write", output, bit); b.emit("move", output, 1)
        return d, following, bit

    while b.pending:
        key = b.pending.popleft(); b.mark(key); tag = key[0]
        if tag == "entry":
            b.branch(output, {4:("guide-entry",)}, ("reject", "nonblank output work"))
        elif tag == "guide-entry":
            b.branch(guide, {4:("begin",)}, ("reject", "nonblank guide work"))
        elif tag == "begin":
            b.emit("write", guide, 5); b.emit("move", guide, 1)
            b.goto(("start", 0, False))
        elif tag == "start":
            _, parity, seen = key
            ending = ("finish-source",) if parity == 0 and seen else ("reject", "complete nonempty complex field")
            b.branch(0, {0:("first", parity, 0), 1:("first", parity, 1), 4:ending},
                     ("reject", "positive component width"))
        elif tag == "first":
            _, parity, x = key
            if odd == 1:
                b.goto(("read-source", 0, offset, 2, parity, x))
            elif count == 1:
                b.goto(("pre-digit", offset % odd, 1, parity, x, 0, True))
            else:
                b.branch(1, {y:("pre-digit", offset % odd, 1, parity, x, y, True) for y in (0,1)},
                         ("reject", "same complete component shape"))
        elif tag == "pre-digit":
            _, rho, power, parity, x, y, first = key
            z = y if count == 2 else x
            rho1, power1 = (rho + a * z * power) % odd, (2 * power) % odd
            residue_states.add((rho1, power1, z))
            b.emit("write", guide, 6 if first else 1); b.emit("move", guide, 1)
            advance_inputs()
            b.goto(("pre-scan", rho1, power1, z, parity))
        elif tag == "pre-scan":
            _, rho, power, sign, parity = key
            b.branch(0, {0:("pre-source",rho,power,parity,0),
                         1:("pre-source",rho,power,parity,1),
                         2:("pre-end",rho,power,sign,parity)},
                     ("reject", "unterminated residue component"))
        elif tag == "pre-source":
            _, rho, power, parity, x = key
            if count == 1:
                b.goto(("pre-digit",rho,power,parity,x,0,False))
            else:
                b.branch(1, {y:("pre-digit",rho,power,parity,x,y,False) for y in (0,1)},
                         ("reject", "same complete component shape"))
        elif tag == "pre-end":
            _, rho, power, sign, parity = key
            residue = (rho - a * sign * power) % odd
            initial = offset - residue
            need(abs(initial) <= bound, "signed corrected initial carry")
            following = ("pre-rewind-step", initial, parity)
            if count == 2:
                b.branch(1, {2:following}, ("reject", "same complete component shape"))
            else:
                b.goto(following)
        elif tag == "pre-rewind-step":
            _, initial, parity = key
            b.emit("move", guide, -1)
            b.goto(("pre-rewind-read", initial, parity))
        elif tag == "pre-rewind-read":
            _, initial, parity = key
            b.branch(guide, {1:("pre-back",initial,parity,False),
                             6:("pre-back",initial,parity,True)},
                     ("reject", "complete residue rewind guide"))
        elif tag == "pre-back":
            _, initial, parity, first = key
            advance_inputs(-1)
            b.goto(("arith-first",initial,parity) if first else ("pre-rewind-step",initial,parity))
        elif tag == "arith-first":
            _, initial, parity = key
            b.branch(0, {x:("read-source",0,initial,2,parity,x) for x in (0,1)},
                     ("reject", "unchanged residue input"))
        elif tag == "scan":
            _, k, carry, sx, sy, sq, parity = key
            b.branch(0, {0:("read-source",k,carry,sq,parity,0),
                         1:("read-source",k,carry,sq,parity,1),
                         2:("component-end",k,carry,sx,sy,sq,parity)},
                     ("reject", "unterminated signed component"))
        elif tag == "read-source":
            _, k, carry, sq, parity, x = key
            if count == 2:
                b.branch(1, {y:("digit",k,carry,sq,parity,x,y) for y in (0,1)},
                         ("reject", "same complete component shape"))
            else:
                b.goto(("digit",k,carry,sq,parity,x,0))
        elif tag == "digit":
            _, k, carry, sq, parity, x, y = key
            k1, c1, q1 = digit(k,carry,x,y)
            guide_one(); advance_inputs()
            b.goto(("scan",k1,c1,x,y,q1,parity))
        elif tag == "component-end":
            _, k, carry, sx, sy, sq, parity = key
            following = ("extend",d,k,carry,sx,sy,sq,parity)
            if count == 2:
                b.branch(1, {2:following}, ("reject", "same complete component shape"))
            else:
                b.goto(following)
        elif tag == "extend":
            _, remaining, k, carry, sx, sy, sq, parity = key
            if remaining:
                k1, c1, q1 = digit(k,carry,sx,sy)
                b.goto(("extend",remaining-1,k1,c1,sx,sy,q1,parity))
            elif sq not in (0,1) or carry != p*sx+r*sy-odd*sq:
                b.goto(("reject", "rounded signed output overflow"))
            else:
                b.emit("write",output,2); b.emit("move",output,1)
                guide_one(); advance_inputs()
                b.goto(("start",parity^1,True))
        elif tag == "finish-source":
            if count == 2:
                b.branch(1,{4:("finish-output",)},("reject","same complete field frontier"))
            else:
                b.goto(("finish-output",))
        elif tag == "finish-output":
            b.branch(output,{4:("rewind-step",)},("reject","exact staged output frontier"))
        elif tag == "rewind-step":
            b.emit("move",guide,-1); b.goto(("rewind-read",))
        elif tag == "rewind-read":
            b.branch(guide,{1:("rewind-inputs",),5:("install-start",)},("reject","complete unary rewind guide"))
        elif tag == "rewind-inputs":
            for port in tuple(range(count))+(output,):
                b.emit("move",port,-1)
            b.goto(("rewind-step",))
        elif tag == "install-start":
            b.emit("move",guide,1); b.goto(("install-guide",))
        elif tag == "install-guide":
            b.branch(guide,{1:("install-read",),4:("installed-target-end",)},("reject","install guide format"))
        elif tag == "install-read":
            b.branch(output,{s:("install-symbol",s) for s in (0,1,2)},("reject","complete protected rounded output"))
        elif tag == "install-symbol":
            b.emit("write",0,key[1])
            for port in (0,output,guide):
                b.emit("move",port,1)
            b.goto(("install-guide",))
        elif tag == "installed-target-end":
            b.branch(0,{4:("installed-output-end",)},("reject","exact installed target frontier"))
        elif tag == "installed-output-end":
            b.branch(output,{4:("halt",)},("reject","exact protected output consumption"))
        elif tag == "halt":
            b.emit("halt")
        elif tag == "reject":
            b.emit("reject",key[1])
        else:
            raise ValueError("unknown rounded compiler state")
    return b.finish(), dict(operation=op, coefficient=str(q), denominator_twos=d,
                            odd_denominator=odd, rounding_offset=offset,
                            carry_bound=bound, carry_states=len(carry_states),
                            residue_states=len(residue_states), rows=len(b.rows), states=len(b.labels),
                            public_ports=count, work_ports=2, residue_prepass=odd>1)
