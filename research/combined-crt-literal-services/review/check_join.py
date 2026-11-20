"""Root review: global relocation and a separate raw-cell interpreter.

No author Program, Audit, hardware Tape, WordPort or numerical oracle is used.
The only imported execution artifact is the fixed union generator.
"""
from pathlib import Path
from hashlib import sha256
import json
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import join


def require(value, message):
    if not value:
        raise ValueError(message)


code, meta = join.compile_union()
cut, total = 1304162, 1435098
require(len(code) == total and meta["arithmetic_locations"] == cut,
        "fixed graph segment lengths")
inverse = {**{i: i for i in range(64)}, 68: 64, 69: 65, 64: 66, 65: 67}


def segment_digest(start, stop, undo):
    h = sha256(b"[")
    for pc in range(start, stop):
        row = code[pc]
        op = row[0]
        if op == "R":
            require(all(start <= target < stop for target in row[2].values()),
                    "read crosses fixed state segment")
            cooked = (op, inverse[row[1]], {s: q-cut for s, q in row[2].items()}) if undo else row
        elif op == "J":
            require(start <= row[1] < stop, "jump crosses fixed state segment")
            cooked = (op, row[1]-cut) if undo else row
        elif op in ("W", "M"):
            require(pc+1 < stop, "fallthrough crosses fixed state segment")
            cooked = (op, inverse[row[1]], row[2]) if undo else row
        else:
            require(op == "H", "unexpected primitive")
            cooked = row
        if op in ("R", "W", "M"):
            require(type(row[1]) is int and 0 <= row[1] < 70, "fixed physical role")
            if not undo:
                require(row[1] < 68, "arithmetic prefix changed role inventory")
        if pc != start:
            h.update(b",")
        h.update(json.dumps(cooked, separators=(",", ":"), sort_keys=True).encode())
    h.update(b"]")
    return h.hexdigest()


require(segment_digest(0, cut, False)
        == "8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045",
        "arithmetic prefix differs from immutable predecessor")
require(segment_digest(cut, total, True)
        == "48863284a4af10cdbb4d16cbecba07dfbadabc57ee8d21f635181acc7e0d0d73",
        "inverse relocation differs from immutable lifecycle predecessor")


class Raw:
    def __init__(self, p, x, y, corrupt_template=False):
        self.p = p
        self.cells = []
        for slot in range(64):
            history = (slot*7+3) % 29
            body = ["0"]*p+["R"] if slot < 8 else ["_"]*(p+1)
            self.cells.append(["L"]+body+["_"]*history)
        self.cells[2][1:p+1] = list(format(x, "0%db" % p)[::-1])
        self.cells[3][1:p+1] = list(format(y, "0%db" % p)[::-1])
        self.cells += [["_"]*8 for _ in range(4)]
        self.cells += [["L"]+["0"]*p+["R"]+["_"]*31, ["_"]*338]
        self.heads = [1]*64+[0]*4+[1, 0]
        self.heads[6] = p  # A genuinely suspended, unselected numerical scan.
        self.calls = self.steps = 0
        self.corrupt_template = corrupt_template
        self.first_template_read = None

    def run(self, entry):
        pc = meta["entries"][entry]
        original_heads = self.heads[:]
        caps = list(map(len, self.cells))
        require(len({id(row) for row in self.cells}) == 70, "raw owner identity")
        cost = 0
        while True:
            row = code[pc]
            op = row[0]
            cost += 1
            require(cost <= 2000000, "raw replay watchdog")
            if op == "R":
                role = row[1]
                if role == 68 and self.first_template_read is None:
                    self.first_template_read = pc
                if self.corrupt_template and role == 68:
                    role = 64  # Deliberately omit the required template role relocation.
                symbol = self.cells[role][self.heads[role]]
                require(symbol in row[2], "raw inadmissible read")
                pc = row[2][symbol]
            elif op == "W":
                self.cells[row[1]][self.heads[row[1]]] = row[2]
                pc += 1
            elif op == "M":
                role, direction = row[1:]
                require(direction in (-1, 1), "unit movement")
                position = self.heads[role]+direction
                require(0 <= position < len(self.cells[role]), "no implicit backing grant")
                self.heads[role] = position
                pc += 1
            elif op == "J":
                pc = row[1]
            else:
                require(op == "H", "raw unknown opcode")
                require(self.heads == original_heads, "active and suspended head return")
                require(list(map(len, self.cells)) == caps, "no capacity change")
                self.calls += 1
                self.steps += cost
                return row[1], cost

    def bind(self, slot):
        require(self.run("L:SET_"+str(slot)) == ("BOUND", 31), "literal selector")

    def release(self, slot):
        self.bind(slot)
        require(self.run("L:FREE")[0] == "FREED", "literal release")

    def integer(self, slot):
        row = self.cells[slot]
        require(row[0] == "L" and row[self.p+1] == "R", "complete output frame")
        return int("".join(reversed(row[1:self.p+1])), 2)


packets = []
for p, x, y in ((5, 31, 7), (5, 0, 1), (9, 500, 127), (9, 17, 7),
                (17, 131071, 65535), (17, 90001, 12345)):
    raw = Raw(p, x, y)
    originals = [r[:] for r in raw.cells]
    require(raw.run("A:ACQUIRE") == ("READY", 89), "selector acquisition")
    require(raw.run("L:INIT") == ("READY", 2744), "ordered stack initialization")
    require(raw.run("L:ZERO")[0] == "ALLOC_8", "first LIFO zero")
    raw.bind(2)
    require(raw.run("L:COPY")[0] == "ALLOC_9" and raw.integer(9) == x,
            "cross-segment copy")
    acquired = [8, 9]
    for kind, left, right in (("COMPARE", 2, 3), ("ADD", 2, 3),
                               ("SUBTRACT", 2, 2), ("DIVIDE", 2, 3)):
        m = 56-len(acquired)
        start = raw.steps
        for operand in (left, right):
            raw.bind(operand)
            require(raw.run("L:IS_LIVE")[0] == "LIVE", "literal operand membership")
        nout = {"COMPARE": 0, "ADD": 1, "SUBTRACT": 1, "DIVIDE": 2}[kind]
        outputs = []
        for _ in range(nout):
            status, _ = raw.run("L:TAKE")
            output = int(status.removeprefix("ALLOC_"))
            require(output == 8+len(acquired), "ordered reservation")
            acquired.append(output)
            outputs.append(output)
        selected = [left, right] + (outputs if nout == 2 else
                                  [outputs[0]]*2 if nout == 1 else [left, right])
        for selector, slot in enumerate(selected):
            require(raw.run("A:SET_%d_%d" % (selector, slot)) == ("BOUND", 31),
                    "arithmetic selector binding")
        status, _ = raw.run("A:"+kind)
        if kind == "COMPARE":
            expected = "CMP_"+({-1:"NEG", 0:"EQ", 1:"POS"}[(x>y)-(x<y)])
            price = 247*p+122*m+968
        elif kind == "ADD":
            expected = "ADD_C"+str(int(x+y >= 1<<p))
            require(raw.integer(outputs[0]) == (x+y) % (1<<p), "integer sum")
            price = 401*p+158*m+1470
        elif kind == "SUBTRACT":
            expected = "SUB_B0"
            require(raw.integer(outputs[0]) == 0, "aliased difference")
            price = 279*p+158*m+1256
        else:
            expected = "DONE"
            q, r = divmod(x, y)
            require([raw.integer(s) for s in outputs] == [q, r], "integer quotient and remainder")
            price = 402*p*p+923*p+194*m+1986+(278*p+245)*q.bit_count()
        require(status == expected and raw.steps-start == price, "value/flag and complete path price")
        require(all(set(raw.cells[s]) == {"_"} for s in range(64, 68)), "shared selector retirement")
        require(raw.cells[:8] == originals[:8], "protected and suspended numerical fields")
    for slot in reversed(acquired):
        raw.release(slot)
    require(raw.run("L:CLOSE") == ("RETIRED", 1395), "terminal metadata")
    require(raw.cells[:64] == originals[:64] and raw.cells[68] == originals[68],
            "complete same-owner historical contents restored")
    require(all(set(raw.cells[s]) == {"_"} for s in (*range(64, 68), 69)), "all metadata blank")
    packets.append({"p": p, "n": x, "d": y, "calls": raw.calls, "instructions": raw.steps})

bad = Raw(5, 31, 7, corrupt_template=True)
bad.run("A:ACQUIRE"); bad.run("L:INIT")
try:
    bad.run("L:ZERO")
except ValueError:
    pass
else:
    raise ValueError("unrelocated template role escaped independent interpreter")

result = {"status": "PASS_INDEPENDENT_LITERAL_UNION",
          "globally_checked_locations": total,
          "predecessor_graphs_recovered_exactly": True,
          "packets": packets,
          "negative_controls": ["unrelocated_template_role"],
          "scope": "Global fixed-state relocation plus a separate raw-cell interpreter; no full higher-controller tariff."}
if "--record" not in sys.argv:
    require(result == json.loads((HERE/"review/RESULT.json").read_text()), "review receipt")
print(json.dumps(result, indent=2, sort_keys=True))
