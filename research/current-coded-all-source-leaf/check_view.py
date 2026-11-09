"""Independent header oracle and sparse physical tape observations.

Syntax tests do not admit global producer/numerical premises. Prepared for
@CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hashlib import sha256
import json
from all_leaf_sources import need
from leaf_view import LeafView, R, RELEASE, S


class Tape:
    def __init__(self, origin=3):
        self.origin = self.head = origin
        self.data = {j:j % 2 for j in range(origin-1)}
        self.data[origin-1] = 2
        self.visited = set(range(origin+1))
        self.actions = 0

    def read(self):
        self.actions += 1; self.visited.add(self.head)
        return self.data.get(self.head, 6)

    def write(self, value):
        need(type(value) is int and 0 <= value <= 6, "physical alphabet")
        self.actions += 1; self.visited.add(self.head)
        if value == 6:
            self.data.pop(self.head, None)
        else:
            self.data[self.head] = value

    def move(self, direction):
        need(direction in (-1, 1), "literal unit move")
        self.actions += 1; self.head += direction
        need(self.head >= 0, "physical boundary")
        self.visited.add(self.head)


def encode(values):
    result = []
    for name, _ in R.SCHEMA:
        value = values[name]
        need(type(value) is int and value >= 0, "reference natural descriptor")
        digits = [(value >> j) & 1 for j in range(max(1, value.bit_length()))]
        result += [1]*len(digits)+[0]+digits
    return result


def decode(bits):
    values, at = {}, 0
    for name, _ in R.SCHEMA:
        start = at
        while at < len(bits) and bits[at] == 1:
            at += 1
        length = at-start
        need(length > 0 and at < len(bits) and bits[at] == 0, "positive canonical header length")
        at += 1; digits = bits[at:at+length]
        need(len(digits) == length and all(x in (0, 1) for x in digits)
             and (length == 1 or digits[-1] == 1), "canonical binary value")
        values[name] = sum(bit << j for j, bit in enumerate(digits)); at += length
    need(at == len(bits), "exact 23-field frontier")
    return values


def put(tape, bits):
    need(tape.head == tape.origin, "input origin")
    for j in list(tape.data):
        if j >= tape.origin:
            del tape.data[j]
    tape.data.update((tape.origin+j, bit) for j, bit in enumerate(bits))
    tape.visited.update(range(tape.origin, tape.origin+len(bits)+1))


def body(tape):
    at, bits = tape.origin, []
    while tape.data.get(at, 6) != 6:
        bits.append(tape.data[at]); at += 1
    need(all(j < at for j in tape.data if j >= tape.origin), "no hidden nonblank tail")
    return bits


def descriptor(f, large_unused=0):
    H, K = max(1, f-1), 2
    u = 2*H+1; z = u+9*f*K+2; a = z+H+1
    return dict(outer=2, rows=3, stock=6, row_bits=(1 << a)*18,
                within_bits=a, record_bits=18, p=9*f+1, d=9*f,
                K=K, G=1, H=H, q0=3, qF=0, qB=large_unused, D=9,
                f=f, rho=1, active_start=u, back_start=z,
                selected_axes=9*f, entry_start=u, remainder=0, cutoff=8*f)


def one(rank, parent, reusable=None):
    if reusable is None:
        view = LeafView(rank)
        work = [Tape(3+j % 5) for j in range(view.port_count)]
        source = Tape(11)
        view.bind(work, S.common.abi.BinaryContextPort(source))
    else:
        view, work, source = reusable
        need(view.rank == rank, "fixed table in history")
    bits = encode(parent); put(source, bits)
    tapes = (*work, source)
    ancestors = [{i:x for i,x in t.data.items() if i < t.origin} for t in tapes]
    before = sum(t.actions for t in tapes)
    steps = view.prepare(); actual = body(view.context.tape)
    wanted = dict(parent, f=rank*parent["f"])
    need(actual == encode(wanted) and decode(actual) == wanted, "complete exact leaf-only descriptor")
    need(len(actual) <= len(bits)+6, "rank at most eight adds at most six header bits")
    need(body(source) == bits and all(t.head == t.origin for t in tapes), "parent and prepared origins")
    steps += view.release()
    need(not view.active and all(not any(i >= t.origin for i in t.data) for t in work)
         and all(t.head == t.origin for t in tapes), "complete physical header retirement")
    need(all({i:x for i,x in t.data.items() if i < t.origin} == old
             for t,old in zip(tapes,ancestors)), "protected ancestors")
    actions = sum(t.actions for t in tapes)-before
    need(actions <= steps <= 1000*len(bits)+10000, "conservative local-instruction bill")
    return dict(rank=rank, parent_f=parent["f"], child_f=wanted["f"], parent_bits=len(bits),
                child_bits=len(actual), instructions=steps, physical_actions=actions,
                exact_header_sha256=sha256(bytes(actual)).hexdigest(),
                retained_private_visited_cells=sum(len(t.visited) for t in work)), (view,work,source)


def check():
    tables = {}
    for rank in range(1, 9):
        view = LeafView(rank)
        for table in (view.table, RELEASE):
            for row in table:
                need(row[0] in ("read", "write", "move", "goto", "done", "reject", "quarantine"), "literal table vocabulary")
                if row[0] in ("read", "write", "move"):
                    need(type(row[1]) is int and 0 <= row[1] < R.FIRST_ROLE, "fixed physical role")
                if row[0] == "write":
                    need(row[1] != R.HEADER and row[2] in (R.ZERO, R.ONE, R.BLANK), "read-only parent and markers")
                if row[0] == "move":
                    need(row[2] in (-1, 1), "literal unit movement")
        tables[rank] = dict(prepare=len(view.table), release=len(RELEASE),
                            sha256=sha256(json.dumps(view.table, separators=(",", ":")).encode()).hexdigest())
    cases = [one(rank, descriptor(f))[0] for rank in range(1, 9) for f in (1, 2, 3, 5, 17)]
    long_case, bank = one(8, descriptor(2, (1 << 1024)+3))
    reused, _ = one(8, descriptor(1), bank)
    fresh, _ = one(8, descriptor(1))
    need(reused["physical_actions"] == fresh["physical_actions"]
         and reused["instructions"] == fresh["instructions"]
         and reused["retained_private_visited_cells"] > fresh["retained_private_visited_cells"],
         "shrinking reuse retains old space without scanning blank tails")
    long_f = descriptor(1)
    long_f["f"] = (1 << 257)-1
    long_f["cutoff"] = 8*long_f["f"]
    long_f_case, _ = one(7, long_f)
    # This last header is canonical syntax only: its unchanged row geometry
    # does not admit the huge numerical child. No payload run is implied.
    invalid_ranks = (0, 9, True, 1.0, -1)
    for rank in invalid_ranks:
        try:
            LeafView(rank)
        except ValueError:
            pass
        else:
            raise ValueError("invalid source rank accepted")
    view, work, source = bank
    bad = descriptor(1); bad["f"] = 0
    put(source, encode(bad))
    try:
        view.prepare()
    except ValueError:
        need(not view.active and body(source) == encode(bad)
             and all(t.head == t.origin for t in (*work, source))
             and all(not any(i >= t.origin for i in t.data) for t in work), "zero-f rejection cleans and returns")
    else:
        raise ValueError("zero f accepted")
    recovered, _ = one(8, descriptor(1), bank)
    mutant, work, source = fresh_bank(2)
    mutant.table = LeafView(1).table
    try:
        one(2, descriptor(3), (mutant, work, source))
    except ValueError as error:
        need(str(error) == "complete exact leaf-only descriptor", "unscaled-f mutant caught by the numerical header oracle")
    else:
        raise ValueError("unscaled positive child width accepted")
    finally:
        if mutant.active:
            mutant.release()
    return dict(cases=cases, tables=tables, long_unused_metadata=long_case,
                long_f_syntax_only=long_f_case, history_reused=reused,
                history_fresh=fresh, recovery=recovered,
                rejected_source_ranks=len(invalid_ranks),
                zero_f_rejected_and_recovered=True, unscaled_f_mutant_rejected=True,
                full_global_header_admission_claim=False)


def fresh_bank(rank):
    view = LeafView(rank)
    work = [Tape(3+j % 5) for j in range(view.port_count)]
    source = Tape(11)
    view.bind(work, S.common.abi.BinaryContextPort(source))
    return view, work, source


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
