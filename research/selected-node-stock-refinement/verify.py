"""Independent NODE/stock/return audit of the pinned physical caller.

The runtime is retained source. The mixed-radix oracle, provenance observer,
and stock controls are new. No predecessor expected-output checker is used.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, ExitStack
from hashlib import sha256
import json
from math import gcd, prod
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/selected-bit-physical-caller"


def require(value, message):
    if not value:
        raise ValueError(message)


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    checked = 0
    for row in manifest["files"]:
        if row.get("usage") == "input":
            path = root / row["path"]
            require(path.is_file() and sha256(path.read_bytes()).hexdigest() == row["sha256"],
                    "source pin: " + row["path"])
            checked += 1
    return checked


def runtime():
    authenticate()
    sys.path.insert(0, str(SOURCE))
    import loader
    loader.activate()
    import macro_machine
    import records
    import words
    import cardinal_counts
    import low_codes
    from check_support import no_decode
    return SimpleNamespace(Machine=macro_machine.Machine, Tape=records.Tape,
                           Arena=words.Arena, Unsigned=words.Unsigned,
                           Count=cardinal_counts.Count, LowCodes=low_codes.LowCodes,
                           BLANK=words.BLANK, LEFT=words.LEFT, no_decode=no_decode)


class TaggedBit(int):
    """Observation only: one original Boolean coordinate, with its actual bit."""
    def __new__(cls, value, origin):
        result = int.__new__(cls, value)
        result.origin = origin
        return result


class Provenance:
    """Track literal copies through Tape.read/write, never select runtime work."""
    def __init__(self, tape_class):
        self.tape_class = tape_class
        self.labels = {}

    @contextmanager
    def observe(self):
        original_read, original_write = self.tape_class.read, self.tape_class.write
        labels = self.labels
        def read(tape):
            value = original_read(tape)
            origin = labels.get(tape, {}).get(tape.head)
            return TaggedBit(value, origin) if origin is not None else value
        def write(tape, value):
            original_write(tape, value)
            cells = labels.setdefault(tape, {})
            if isinstance(value, TaggedBit):
                require(value in (0, 1), "provenance only labels Boolean data")
                cells[tape.head] = value.origin
            else:
                cells.pop(tape.head, None)
        with patch.object(self.tape_class, "read", read), patch.object(self.tape_class, "write", write):
            yield

    def seed(self, tape, length):
        self.labels[tape] = {i + 1: i for i in range(length)}

    def vector(self, tape, length):
        return [self.labels.get(tape, {}).get(i + 1, -1) for i in range(length)]


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([4]))


def count_value(value):
    """Checker-only conversion outside the production no-decode path."""
    result = 0
    # Cardinal Counts use little-endian dense Boolean bodies, including zero.
    encoded = body(value.tape)
    require(encoded[-1] == 3, "count RIGHT delimiter")
    for bit, digit in enumerate(encoded[:-1]):
        require(digit in (0, 1), "count binary body")
        result += digit << bit
    return result


def shape(q, w, n, families, old, unused, before, gap, suffix):
    modulus = q ** w
    low = prod(q ** 2 - q ** i for i in range(2))
    high = q ** (4 * (w - 1))
    rows = families * low * high * unused
    fibre = unused * before * gap * suffix * modulus ** (2 * n)
    volume = old * families * low * high * fibre
    return dict(modulus=modulus, low=low, high=high, rows=rows,
                fibre=fibre, volume=volume, family_volume=volume // families)


def peel_destination(address, *, n, modulus, gap, suffix, weights, dimension=2):
    """Independent Cartesian-coordinate action, not a source event replay."""
    rest, s = divmod(address, suffix)
    rest, tail = divmod(rest, modulus ** n)
    rest, g = divmod(rest, gap)
    outer, head = divmod(rest, modulus ** n)
    x, y = [], []
    for _ in range(n):
        head, digit = divmod(head, modulus); x.append(digit)
        tail, digit = divmod(tail, modulus); y.append(digit)
    x.reverse(); y.reverse()
    for i in range(dimension * (n // dimension), n):
        j = n - 1 - i
        x[i], y[j] = weights[i] * y[j] % modulus, pow(weights[i], -1, modulus) * x[i] % modulus
    head = tail = 0
    for a, b in zip(x, y):
        head = head * modulus + a; tail = tail * modulus + b
    return ((((outer * modulus ** n + head) * gap + g) * modulus ** n + tail) * suffix + s)


def expected_vectors(case, dims):
    length = dims["volume"]
    peeled = [-1] * length
    for origin in range(length):
        weights = case["weights"]
        if case.get("history"):
            old = origin // (length // case["old"])
            weights = case["prefix_weights"][case["old_codes"][old]]
        target = peel_destination(origin, n=case["n"], modulus=dims["modulus"],
                                  gap=case["gap"], suffix=case["suffix"], weights=weights)
        require(peeled[target] == -1, "oracle is a permutation")
        peeled[target] = origin
    families = [[] for _ in range(case["families"])]
    block = dims["low"] * dims["high"] * dims["fibre"]
    for c in range(case["old"]):
        for f in range(case["families"]):
            start = (c * case["families"] + f) * block
            families[f].extend(peeled[start:start + block])
    return peeled, families


class Binding:
    """Explicit finite root-weight fixture; no selected coefficient claim."""
    cutoff, child_mode = 2, 0
    def __init__(self, rt, q, weights, stock_multiple, history=0, prefix_weights=None):
        self.codes = (SimpleNamespace(q=2, dimension=2, size=6, bits=4, limit=12)
                      if q == 2 else rt.LowCodes(q, 2, 1))
        self.weights, self.stock_multiple = tuple(weights), stock_multiple
        self.history, self.prefix_weights = history, prefix_weights

    def incoming(self, machine):
        def coefficient(prefix, request):
            require(request.kind == "incoming", "incoming request")
            weights = self.weights
            if self.history:
                from records import read_finite, read_word, RECORD_END
                code = read_finite(prefix, self.codes.bits)
                require(code in (0, 1), "finite history fixture source code")
                for _ in range(4):
                    high = read_word(prefix, machine.arena)
                    require(high.zero(), "zero high field in width-one fixture")
                    machine.arena.free(high)
                require(prefix.read() == RECORD_END, "complete old field")
                prefix.step(1)
                weights = self.prefix_weights[code]
            require(prefix.read() == 4, "complete frozen-only prefix")
            prefix.rewind()
            # Each fixture's finite alphabet is fixed before execution. No Word
            # inspect(), numerical decoding, or payload decision is used here.
            for i, value in enumerate(weights):
                key = machine.indices.literal(i)
                from words import Unsigned
                equal = Unsigned(machine.indices).compare(request.coordinate, key) == 0
                machine.indices.free(key)
                if equal:
                    result = machine.arena.literal(value)
                    if request.negative_inverse:
                        inverse = (machine.arena.copy(result) if getattr(self,"omit_inverse",False)
                                   else machine.context.ring.inverse(result))
                        require(inverse is not None, "unit fixture coefficient")
                        negative = machine.context.ring.negate(inverse)
                        machine.arena.free_many(result, inverse)
                        result = negative
                    return result
            raise ValueError("fixture coordinate outside fixed grammar")
        return SimpleNamespace(coefficient=coefficient)


CASES = (
    dict(name="two_old_rows_two_families", q=2, w=1, n=2, families=2, old=2,
         unused=2, before=2, gap=3, suffix=2, weights=(1,1)),
    dict(name="odd_peel_all_spectators", q=2, w=1, n=3, families=2, old=2,
         unused=2, before=2, gap=2, suffix=2, weights=(1,1,1)),
    dict(name="nonbinary_weighted_peel", q=3, w=1, n=3, families=1, old=1,
         unused=1, before=1, gap=2, suffix=1, weights=(2,1,2)),
    dict(name="nontrivial_high_fibres", q=2, w=2, n=2, families=1, old=1,
         unused=1, before=1, gap=1, suffix=1, weights=(1,3)),
    dict(name="nonempty_old_prefix_weights", q=3, w=1, n=3, families=1, old=2,
         unused=1, before=1, gap=1, suffix=1, weights=(1,1,2), history=1,
         old_codes=(0,1), prefix_weights=((1,1,2),(2,2,1))),
)


def run_case(case, rt=None, mutant=None):
    rt = runtime() if rt is None else rt
    dims = shape(**{k: case[k] for k in ("q","w","n","families","old","unused","before","gap","suffix")})
    require(dims["volume"] <= 70000, "bounded complete payload fixture")
    expected, expected_family = expected_vectors(case, dims)
    binding = Binding(rt, case["q"], case["weights"], case["unused"],
                      case.get("history",0), case.get("prefix_weights"))
    if mutant == "wrong_prefix_weight":
        binding.prefix_weights = (binding.prefix_weights[0], binding.prefix_weights[0])
    topology = SimpleNamespace(families=case["families"])
    program = SimpleNamespace(staged_roles=0, operations=(("node",), ("return",)))
    bits = dims["modulus"].bit_length() + 1
    machine = rt.Machine(binding, topology, (program,), rt.Arena(bits, 512), rt.Arena(10, 512))
    source_arena, source_indices = rt.Arena(bits, 512), rt.Arena(10, 512)
    modulus, size, depth = source_arena.input(dims["modulus"]), source_indices.input(case["n"]), source_indices.input(case.get("history",0))
    source, directory, encoded = rt.Tape(), rt.Tape(), rt.Tape()
    if case.get("history"):
        from records import append_finite, append_word, RECORD_END
        for code in case["old_codes"]:
            append_finite(directory,code,binding.codes.bits)
            for _ in range(4):
                zero=source_arena.zero();append_word(directory,zero);source_arena.free(zero)
            directory.append(RECORD_END)
        directory.rewind()
    for i in range(dims["volume"]):
        source.append(((i * 13) ^ (i >> 3) ^ (i >> 7) ^ 0x53) & 1)
    source.rewind()
    rows = dims["rows"] // dims["high"] if mutant == "missing_high_stock" else dims["rows"]
    counts = [rt.Count.literal(v) for v in (case["old"], rows, case["before"], case["gap"], case["suffix"])]
    borrowed = (source, directory, encoded, *(v.tape for v in counts))
    saved = tuple((bytes(t.cells), t.head) for t in borrowed)
    borrowed_words = (modulus,size,depth)
    saved_words = tuple((bytes(t.cells),t.head) for t in borrowed_words)
    original = body(source)
    provenance = Provenance(rt.Tape); provenance.seed(source, dims["volume"])
    with ExitStack() as changes, provenance.observe(), machine.pool.install(), rt.no_decode():
        if mutant == "lost_peel":
            import macro_machine
            changes.enter_context(patch.object(macro_machine.peel, "run", lambda first,*a,**k: first))
        if mutant == "lost_high_fibres":
            import macro_machine
            changes.enter_context(patch.object(macro_machine.fresh_rows, "family_rows",
                                                lambda ctx: rt.Count.literal(ctx.codes.size)))
        machine.load_root(source, directory, encoded, modulus, size, depth, *counts)
        machine.dispatch(("node",))
        machine.boundary()
        if mutant == "spectator_as_stock":
            machine.commit(machine.tape("leading"),"unused")
        require(count_value(machine.count("unused")) == case["unused"], "fresh U is separate from spectators")
        require(count_value(machine.count("leading")) == case["unused"] * case["before"], "leading U times B")
        require(count_value(machine.count("fibre")) == dims["fibre"], "complete fibre")
        require(count_value(machine.count("family_rows")) == dims["low"] * dims["high"], "all low and high rows")
        if mutant == "family_order":
            a,b = machine.tape(("family",0)),machine.tape(("family",1))
            a.cells,b.cells = b.cells,a.cells
            provenance.labels[a],provenance.labels[b] = provenance.labels[b],provenance.labels[a]
        for f, wanted in enumerate(expected_family):
            tape=machine.tape(("family", f))
            require(len(body(tape)) == len(wanted) and provenance.vector(tape,len(wanted)) == wanted,
                    "complete NODE family coordinates")
            require(body(tape) == bytes(original[o] for o in wanted), "complete NODE Boolean data")
        if mutant == "return_alias":
            machine.output=source
        require(machine.dispatch(("return",)) == "done", "root complete return")
        actual=provenance.vector(machine.output,dims["volume"])
        require(actual == expected, "complete MERGE coordinate output")
        require(body(machine.output) == bytes(original[o] for o in expected), "complete MERGE Boolean data")
        require(machine.output not in borrowed, "distinct owned return")
        require(tuple((bytes(t.cells),t.head) for t in borrowed) == saved, "borrowed input bytes and heads")
        require(tuple((bytes(t.cells),t.head) for t in borrowed_words) == saved_words,
                "borrowed numerical input bytes and heads")
        require(provenance.vector(source,dims["volume"]) == list(range(dims["volume"])), "borrowed provenance")
        require(not machine.arena.live and not machine.indices.live and not machine.pool.live, "closed numerical and scratch state")
        require(all(not body(t) and t.head == 1 for t in machine.roles.values()), "cleared node roles")
        machine.erase_work()
        work=(*machine.roles.values(),*machine.handoff.values(),*machine.pool.tapes)
        require(all(all(v == rt.BLANK for v in t.cells) for t in work), "erased permanent work markers")
        require(all(all(v == rt.BLANK for v in word.cells)
                    for bank in (machine.arena,machine.indices) for word in (*bank.words,bank.template)),
                "erased numerical words and templates")
        require(machine.numerical.machine.tapes == [{},{}], "erased physical parking tapes")
        require(machine.output.head == 1 and machine.output.cells[0] == rt.LEFT, "owned output survives erasure")
    record=dict(name=case["name"],volume=dims["volume"],family_volume=dims["family_volume"],
                old=case["old"],families=case["families"],low=dims["low"],high=dims["high"],unused=case["unused"],
                remainder=case["n"]%2,history=case.get("history",0),peak_scratch=machine.pool.peak,
                permutation_sha256=sha256(b"".join(x.to_bytes(4,"big") for x in actual)).hexdigest(),
                payload_sha256=sha256(body(machine.output)).hexdigest())
    for t in (source,directory,encoded,machine.output): t.clear()
    for c in counts:c.close()
    source_arena.free(modulus);source_indices.free_many(size,depth)
    return record


def typed_equal(first, second):
    return json.dumps(first,sort_keys=True,separators=(",",":")) == json.dumps(second,sort_keys=True,separators=(",",":"))


def noninvolutory_unit_peel(rt=None, wrong_inverse=False):
    """A complete q=5 peel-only packet distinguishes a=2 from a^-1=3.

    It deliberately has one row; no selected full-cover stock claim is made.
    """
    rt=runtime() if rt is None else rt
    from directory import Context
    from scratch_pool import ScratchPool
    from words import Ring
    import peel
    arena,indices=rt.Arena(4,512),rt.Arena(8,512)
    modulus=arena.input(5);ring=Ring(modulus)
    binding=Binding(rt,5,(1,1,2),1);binding.omit_inverse=wrong_inverse
    context=Context(ring,binding.codes)
    size,depth=indices.input(3),indices.zero()
    incoming=binding.incoming(SimpleNamespace(context=context,arena=arena,indices=indices))
    source,directory=rt.Tape(),rt.Tape();length=5**6
    for i in range(length):source.append(((i*7)^(i>>3)^0x57)&1)
    source.rewind();original=body(source)
    counts=[rt.Count.literal(1) for _ in range(5)]
    pool=ScratchPool(153)
    provenance=Provenance(rt.Tape);provenance.seed(source,length)
    expected=[-1]*length
    for i in range(length):
        j=peel_destination(i,n=3,modulus=5,gap=1,suffix=1,weights=(1,1,2))
        expected[j]=i
    with provenance.observe(),pool.install(),rt.no_decode():
        output=peel.run(source,context,indices,size,depth,object(),directory,*counts,incoming)
        actual=provenance.vector(output.physical,length)
        require(actual==expected,"noninvolutory inverse peel coordinates")
        require(body(output.physical)==bytes(original[i] for i in expected),"noninvolutory inverse Boolean values")
        require(body(source)==original and source.head==directory.head==1,"peel-only borrowed state")
        output.clear();pool.empty()
    result=dict(q=5,modulus=5,weight=2,inverse=3,coordinates=length,
                permutation_sha256=sha256(b"".join(i.to_bytes(4,"big") for i in actual)).hexdigest())
    source.clear();directory.clear()
    for count in counts:count.close()
    context.close();ring.close();arena.free(modulus);indices.free_many(size,depth)
    require(not arena.live and not indices.live,"peel-only numerical restoration")
    return result


def stock_arithmetic():
    live, physical, multiple = 28416, 28425, 9475
    require(live*physical//gcd(live,physical) == 269241600 == live*multiple,
            "selected compatible LCM coefficient")
    require(gcd(live,physical) == 3 and multiple % live != 0, "one-level guard is not recursive stock")
    cases=0
    for q in (2,3,5):
        for w in (1,2,3):
            nlow=prod(q**2-q**i for i in range(2)); high=q**(4*(w-1))
            for W,P in ((2,3),(4,6),(live,physical)):
                K=(W*P//gcd(W,P))*nlow*high
                factor=P//gcd(W,P)
                for d in (1,2,3):
                    for t in (1,2,7):
                        U=t*K**d//(W*nlow*high)
                        require(U == t*factor*K**(d-1), "exact fresh-row quotient recurrence")
                        require(U % K**(d-1) == 0 and U%factor==0, "next compatible stock")
                        cases+=1
    require(42*(128//64)==84 >=64, "internal maximum-rank child at width 128")
    return dict(live=live,physical=physical,lcm=269241600,stock_multiple=multiple,
                quotient_cases=cases,local_only_control=dict(parent_n=128,child_n=84,root_stock="K",child_rows=9475,
                child_first_divisor=28416,remainder=9475))


def stock_guard(kind, rt=None):
    """Reach the actual selected-size NODE guard, stopping before payload work.

    q=3 is only a small arithmetic fixture. Complete GL64 cardinality is used,
    but no GL64 low list or Boolean payload is materialized.
    """
    rt = runtime() if rt is None else rt
    from macro_binding import SelectedBinding
    from topology import SelectedTopology
    import macro_machine
    W, factor = SelectedTopology.families, SelectedBinding.stock_multiple
    require((W, factor) == (28416, 9475), "source selected stock constants")
    q, dimension, modulus_value = 3, 64, 3
    N = prod(q ** dimension - q ** i for i in range(dimension))
    K = W * factor * N
    rows = {"one_packet": K, "two_packets": K*K,
            "missing_compatible_factor": W*N*(factor-1),
            "missing_family": K-1, "missing_low": W,
            "child_of_one_packet": factor}[kind]
    binding = Binding(rt, q, (1,), factor)
    binding.codes = SimpleNamespace(q=q, dimension=dimension, size=N, bits=1, limit=1)
    program = SimpleNamespace(staged_roles=0, operations=(("node",),("return",)))
    machine = rt.Machine(binding, SimpleNamespace(families=W), (program,), rt.Arena(3,512), rt.Arena(10,512))
    source_arena, source_indices = rt.Arena(3,512), rt.Arena(10,512)
    modulus=source_arena.input(modulus_value)
    size=source_indices.input(84 if kind=="child_of_one_packet" else 128)
    depth=source_indices.zero()
    source,directory,encoded=rt.Tape(),rt.Tape(),rt.Tape()
    counts=[rt.Count.literal(x) for x in (1,rows,1,1,1)]
    class StopAtPeel(Exception):
        pass
    def stop(*args,**kwargs):
        raise StopAtPeel()
    outcome = None
    with machine.pool.install(),rt.no_decode(),patch.object(macro_machine.peel,"run",stop):
        machine.load_root(source,directory,encoded,modulus,size,depth,*counts)
        try:
            machine.node()
        except StopAtPeel:
            outcome="accepted_local_stock"
        except ValueError as error:
            outcome=str(error)
    # These deliberately stopped/rejected executions assert only the guard's
    # decision. General exception cleanup is not a contract under this audit.
    return dict(kind=kind,outcome=outcome,dimension=dimension,q=q,
                families=W,stock_multiple=factor,rows_bits=rows.bit_length())


def guard_records(rt):
    expected={"one_packet":"accepted_local_stock", "two_packets":"accepted_local_stock",
              "missing_compatible_factor":"compatible fresh stock factor",
              "missing_family":"complete fresh family factor",
              "missing_low":"complete fresh GL low factor",
              "child_of_one_packet":"complete fresh family factor"}
    records=[]
    for kind, message in expected.items():
        record=stock_guard(kind,rt)
        require(record["outcome"]==message,"literal selected NODE stock guard: "+kind)
        records.append(record)
    return records


def run():
    rt=runtime()
    records=[run_case(case,rt) for case in CASES]
    return dict(schema=1,kind="conditional source refinement and finite independent audit",
                stock=stock_arithmetic(),guards=guard_records(rt),cases=records,
                noninvolutory_peel=noninvolutory_unit_peel(rt),
                total_coordinates=sum(r["volume"] for r in records),new_kappa=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write-result",type=Path)
    parser.add_argument("--case",choices=[c["name"] for c in CASES])
    args=parser.parse_args()
    result=run_case(next(c for c in CASES if c["name"]==args.case)) if args.case else run()
    if args.case:
        print(json.dumps(result,sort_keys=True));return
    if args.write_result:
        with args.write_result.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    else:
        stored=json.loads((HERE/"RESULT.json").read_text())
        require(typed_equal(stored,result), "typed deterministic receipt")
    print("PASS_SELECTED_NODE_STOCK_REFINEMENT cases="+str(len(result["cases"]))+" coordinates="+str(result["total_coordinates"])+" no_new_kappa")


if __name__ == "__main__":
    main()
