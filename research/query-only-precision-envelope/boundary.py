"""Source-cut countermodel and literal retained exact-table boundary controls.

The one-grid child defect is permitted by an abstract error contract. This
module does not claim an actual retained MOVE implementation produces it.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
from source_binding import need, sources, load_vendor


class Tape:
    def __init__(self, machine, bits=(), origin=17):
        self.machine = machine
        self.origin = self.pos = origin
        self.cells = {origin - 1: machine.LEFT, origin - 2: 91}
        self.cells.update({origin + i: s for i, s in enumerate(bits)})
        self.actions = 0

    def tick(self):
        need(self.pos >= self.origin - 1, "no ancestor access")
        self.actions += 1

    def read(self):
        self.tick()
        return self.cells.get(self.pos, self.machine.BLANK)

    def write(self, symbol):
        self.tick()
        need(self.pos >= self.origin and 0 <= symbol < 7, "protected marker/alphabet")
        self.cells[self.pos] = symbol

    def move(self, step):
        self.tick()
        need(step in (-1, 1), "unit physical head move")
        self.pos += step
        need(self.pos >= self.origin - 1, "no ancestor crossing")

    def body(self):
        end = self.origin
        while self.cells.get(end, self.machine.BLANK) != self.machine.BLANK:
            end += 1
        return tuple(self.cells.get(k, self.machine.BLANK) for k in range(self.origin, end))

    def sentinel_ok(self):
        return self.cells[self.origin - 1] == self.machine.LEFT and self.cells[self.origin - 2] == 91


def encode(values, width):
    symbols = []
    for value in values:
        need(-(1 << (width - 1)) <= value < (1 << (width - 1)), "signed fixture input")
        symbols.extend((value >> j) & 1 for j in range(width))
        symbols.append(2)
    return tuple((s >> k) & 1 for s in symbols for k in (2, 1, 0))


def decode(bits, width):
    need(len(bits) % 3 == 0, "complete physical codewords")
    symbols = [4 * bits[i] + 2 * bits[i + 1] + bits[i + 2] for i in range(0, len(bits), 3)]
    need(len(symbols) % (width + 1) == 0, "complete numeric records")
    out = []
    for i in range(0, len(symbols), width + 1):
        b = symbols[i:i + width]
        need(all(z in (0, 1) for z in b) and symbols[i + width] == 2, "signed fixture encoding")
        out.append(sum(z << j for j, z in enumerate(b)) - (b[-1] << width))
    return tuple(out)


def run():
    _, word = sources()
    expected = [["MOVE", 697, 1042, 591, False],
                ["MOVE", 1334, 1042, 1046, False],
                ["MOVE", 901, 565, 591, False],
                ["SCALE", 1334, "1/2", 1046],
                ["SCALE", 697, "-2/3", 591]]
    need(word["program"][37476:37481] == expected, "exact five-event obstruction cut")
    need(all(697 not in e[1:3] for e in expected[1:4]), "no intervening access to the defect field")
    q = F(-2, 3)
    need(q.denominator != 1 and F(q.numerator, q.denominator).denominator == 3,
         "one-grid numerator remains nonintegral for every F")
    # Scalar reference: total nearest RDiv is a DIFFERENT operation.
    rounded = (q.numerator + q.denominator // 2) // q.denominator
    need(rounded == -1 and abs(F(rounded) - q) <= F(1, 2), "RDiv alternative and residual")
    machine = load_vendor("precision_boundary_machine", "vendor/machine.py")
    tables = load_vendor("precision_boundary_tables", "vendor/exact_scalar_tables.py")
    table, receipt = tables.compile_scalar("SCALE", q)
    cases = []
    # Distinct origins and initially dirty contiguous private work. Exact failed
    # runs are deliberately not advertised as restored/erased.
    for width in range(3, 10):
        for values in ((1, 0), (3, 1), (0, 0), (3, 0), (-3, 0)):
            target = Tape(machine, encode(values, width), 17)
            work = [Tape(machine, (1, 0, 1, 1), 41), Tape(machine, (0, 1), 63)]
            before = target.body()
            failure = None
            try:
                for t in work:
                    machine.retire(t)
                machine.execute_table(table, (target, *work))
                for t in work:
                    machine.retire(t)
            except ValueError as exc:
                failure = str(exc)
            ideal = tuple(q * v for v in values)
            admissible = all(v.denominator == 1 and -(1 << (width - 1)) <= v < (1 << (width - 1)) for v in ideal)
            need((failure is None) == admissible, "independent divisibility/range oracle")
            if admissible:
                need(decode(target.body(), width) == tuple(map(int, ideal)), "exact physical quotient")
                need(all(t.pos == t.origin for t in (target, *work)), "success heads reset")
                need(all(not t.body() for t in work), "success work erased")
            else:
                need(target.body() == before, "rejection before any public component commit")
            need(all(t.sentinel_ok() for t in (target, *work)), "ancestor sentinels")
            cases.append(dict(width=width, input=list(values), accepted=admissible,
                              actions=sum(t.actions for t in (target, *work))))
    need(len(cases) == 35 and sum(c["accepted"] for c in cases) == 21, "complete bounded physical coverage")
    return dict(source_move=37476, source_odd_scale=37480, register=697,
                coefficient="-2/3", intervening_events=3,
                universal_countermodel="one admitted quantum after MOVE; all other residuals zero",
                caveat="contract countermodel, not an observed error of a retained MOVE implementation",
                rounded_alternative=dict(output_numerator=rounded, residual_in_quanta=str(F(rounded) - q)),
                physical=dict(cases=cases, accepted=21, rejected=14, table_instructions=len(table),
                              table_receipt=receipt,
                              scope="unchanged generic exact SCALE table/executor; no new source-token binder",
                              failure_contract="public unchanged; private work and heads may be unrestored"))
