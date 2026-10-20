"""Uniform sequential-arena Beneš component: cell/head model and scoped proof.

Block tape methods batch repeated ONE-CELL operations, charging each cell.
They never perform an indexed arena lookup. Bounded scalar control is mirrored
by Python integers; its bit lowering is proved separately in PROOF.md.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
P, INV, COLOR, OUT, STACK = range(5)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def word(value, width):
    need(isinstance(value, int) and 0 <= value < (1 << width), "encoded word range")
    return format(value, "0%db" % width).encode()


class Tape:
    """Alphabet {0,1,blank}, implicit left marker, one sequential head."""

    def __init__(self, data=b"", expanded=False):
        self.data = bytearray(data)
        self.head = self.actions = 0
        self.expanded = expanded

    def read(self, count):
        need(0 <= count and self.head + count <= len(self.data), "tape read bounds")
        if self.expanded:
            result = bytearray()
            for _ in range(count):
                result.append(self.data[self.head])
                self.head += 1
                self.actions += 2
            return bytes(result)
        result = bytes(self.data[self.head:self.head + count])
        self.head += count
        self.actions += 2 * count  # count repetitions of READ; RIGHT.
        return result

    def write(self, data):
        if self.expanded:
            for cell in data:
                if self.head == len(self.data):
                    self.data.append(cell)
                else:
                    self.data[self.head] = cell
                self.head += 1
                self.actions += 2
            return
        stop = self.head + len(data)
        self.data[self.head:stop] = data
        self.head = stop
        self.actions += 2 * len(data)

    def skip(self, count):
        need(0 <= count and self.head + count <= len(self.data), "tape move bounds")
        if self.expanded:
            for _ in range(count):
                self.head += 1
                self.actions += 1
        else:
            self.head += count
            self.actions += count  # count one-cell RIGHT operations.

    def rewind(self):
        if self.expanded:
            while self.head:
                self.head -= 1
                self.actions += 1
        else:
            self.actions += self.head
            self.head = 0

    def clear(self):
        need(self.head == 0, "clear starts at left marker")
        self.write(bytes(len(self.data)))  # NUL encodes blank, distinct from ASCII 0/1.
        self.rewind()


def descriptors(h):
    n = 1 << h
    for depth in range(h):
        size = n >> depth
        height = h - depth
        for node in range(1 << depth, 1 << (depth + 1)):
            for kind in (P, INV, COLOR):
                for index in range(size):
                    yield (node, kind, 0, index), n if kind == COLOR else 0
            for layer in range(2 * height - 1):
                for index in range(size):
                    yield (node, OUT, layer, index), 0
    for index in range(n):
        yield (0, STACK, 0, index), n


class Arena:
    """Fixed-width tagged records; EVERY get/put scans all records and returns."""

    def __init__(self, h, p, expanded=False):
        self.h, self.p, self.width = h, p, 4 * p + 8
        self.tape = Tape(expanded=expanded)
        self.key_tape = Tape(expanded=expanded)
        self.calls = self.records_scanned = self.scan_actions = 0
        self.key_actions = 0
        self.kinds = {"get": 0, "put": 0}
        self.count = 0
        for key, initial in descriptors(h):
            self.tape.write(b"".join(word(v, self.width) for v in key) + word(initial, self.width))
            self.count += 1
        self.tape.rewind()
        n = 1 << h
        need(self.count == n * (h * h + 3 * h + 1), "exact flattened arena census")
        self.length = len(self.tape.data)
        need(self.length == 5 * self.width * self.count, "fixed-width arena size")

    def access(self, key, value=None, omit_return=False):
        need(self.tape.head == 0, "arena operation must start at left marker")
        encoded = b"".join(word(v, self.width) for v in key)
        key_tape = self.key_tape  # One reused physical scratch tape, never a tape per call.
        key_start = key_tape.actions
        key_tape.write(encoded)
        key_tape.rewind()
        start = self.tape.actions
        answer = None
        found = 0
        for _ in range(self.count):
            candidate = self.tape.read(4 * self.width)
            supplied = key_tape.read(4 * self.width)
            key_tape.rewind()
            if candidate == supplied:
                found += 1
                if value is None:
                    answer = int(self.tape.read(self.width), 2)
                else:
                    self.tape.write(word(value, self.width))
            else:
                self.tape.skip(self.width)
            self.records_scanned += 1
        if not omit_return:
            self.tape.rewind()
        key_tape.clear()
        need(found == 1, "tagged record must exist exactly once")
        self.calls += 1
        self.kinds["get" if value is None else "put"] += 1
        self.scan_actions += self.tape.actions - start
        self.key_actions += key_tape.actions - key_start
        need(all(cell == 0 for cell in key_tape.data) and key_tape.head == 0,
             "key scratch must be cleared/returned")
        return answer

    def get(self, node, kind, index, layer=0):
        return self.access((node, kind, layer, index))

    def put(self, node, kind, index, value, layer=0):
        self.access((node, kind, layer, index), value)

    def finish(self):
        need(self.tape.head == 0, "arena final head return")
        self.tape.clear()
        need(all(cell == 0 for cell in self.tape.data), "private arena must be erased")
        need(self.records_scanned == self.calls * self.count, "every logical access is a full scan")
        # One matching value read/write adds w beyond the unmatched skip.
        # The key tape is written, returned, reread/returned N times, erased/returned.
        expected = self.calls * (26 * self.width * self.count + 25 * self.width)
        need(self.scan_actions + self.key_actions == expected, "complete scan/key/head-return invoice")
        return {"record_width_bits": 5 * self.width,
                "word_width_bits": self.width, "arena_records": self.count,
                "arena_cells": self.length, "logical_accesses": self.calls,
                "get_calls": self.kinds["get"], "put_calls": self.kinds["put"],
                "records_scanned": self.records_scanned,
                "arena_and_key_scan_actions": self.scan_actions + self.key_actions,
                "arena_initialization_cleanup_actions": 6 * self.length,
                "arena_and_key_tape_actions": self.tape.actions + self.key_actions,
                "private_arena_erased": True, "private_heads_returned": True}


def compile_stream(input_bits, h, p, expanded=False, wrong_neighbor=False):
    """Uniform valid-input compiler; no host recursion, no indexed arena accesses.

    Input is the protected h-bit encoding of N permutation entries. Output is
    the owned concatenation of the 2h-1 root switch tables, N bits per layer.
    """
    need(isinstance(h, int) and isinstance(p, int) and 1 <= h <= p, "1<=h<=p")
    n = 1 << h
    need(len(input_bits) == n * h and all(cell in (48, 49) for cell in input_bits),
         "complete binary permutation encoding")
    incoming = Tape(input_bits, expanded=expanded)
    arena = Arena(h, p, expanded)
    for index in range(n):
        arena.put(1, P, index, int(incoming.read(h), 2))
    incoming.rewind()
    pushes = pops = max_stack = validation_pairs = 0

    # Top-down recursion-tree schedule, not Python recursive calls.
    for depth in range(h):
        size = n >> depth
        height = h - depth
        for node in range(1 << depth, 1 << (depth + 1)):
            # Explicit quadratic validation replaces the source's sorted call.
            for x in range(size):
                px = arena.get(node, P, x)
                need(px < size, "permutation range")
                for y in range(x):
                    need(arena.get(node, P, y) != px, "permutation distinctness")
                    validation_pairs += 1
            if size == 2:
                bit = arena.get(node, P, 0)
                arena.put(node, OUT, 0, bit)
                arena.put(node, OUT, 1, bit)
                continue
            for x in range(size):
                arena.put(node, INV, arena.get(node, P, x), x)
            for initial in range(size):
                if arena.get(node, COLOR, initial) != n:
                    continue
                arena.put(node, COLOR, initial, 0)
                top = 0
                arena.put(0, STACK, top, initial)
                top += 1
                pushes += 1
                while top:
                    max_stack = max(max_stack, top)
                    top -= 1
                    x = arena.get(0, STACK, top)
                    arena.put(0, STACK, top, n)
                    pops += 1
                    for edge in (0, 1):
                        other = (x ^ 1 if edge == 0 else
                                 arena.get(node, INV, arena.get(node, P, x) ^ (0 if wrong_neighbor else 1)))
                        opposite = arena.get(node, COLOR, x) ^ 1
                        color = arena.get(node, COLOR, other)
                        if color == n:
                            arena.put(node, COLOR, other, opposite)
                            need(top < n, "encoded DFS capacity")
                            arena.put(0, STACK, top, other)
                            top += 1
                            pushes += 1
                        else:
                            need(color == opposite, "two perfect matching color constraints")
            for x in range(size):
                color = arena.get(node, COLOR, x)
                arena.put(node, OUT, x, color ^ (x & 1), layer=0)
                inverse = arena.get(node, INV, x)
                last = arena.get(node, COLOR, inverse) ^ (x & 1)
                arena.put(node, OUT, x, last, layer=2 * height - 2)
                # Each input pair has exactly one representative of each color.
                arena.put(2 * node + color, P, x // 2, arena.get(node, P, x) // 2)

    # Bottom-up assembly of complete child tables.
    for depth in reversed(range(h - 1)):
        size = n >> depth
        height = h - depth
        for node in range(1 << depth, 1 << (depth + 1)):
            for layer in range(2 * height - 3):
                for x in range(size):
                    value = arena.get(2 * node + (x & 1), OUT, x // 2, layer=layer)
                    arena.put(node, OUT, x, value, layer=layer + 1)
    need(pushes == pops and max_stack <= n, "encoded DFS stack balanced")
    # Serialize the OWNED root output before erasing every private arena cell.
    output = Tape(expanded=expanded)
    for layer in range(2 * h - 1):
        for x in range(n):
            output.write(word(arena.get(1, OUT, x, layer), 1))
    output.rewind()
    # Observer gate: independently derived from validation/tree/DFS/merge sums.
    expected_accesses = n * n + 2 * n * h * h + (37 * n * h - 35 * n) // 2
    need(arena.calls == expected_accesses, "derived exact logical-access census")
    invoice = arena.finish()
    invoice.update({"h": h, "p": p, "wires": n,
                    "input_bits": len(input_bits), "input_tape_actions": incoming.actions,
                    "owned_output_bits": len(output.data), "owned_output_tape_actions": output.actions,
                    "validation_pairs": validation_pairs,
                    "dfs_pushes": pushes, "dfs_pops": pops, "maximum_dfs_entries": max_stack})
    need(incoming.head == output.head == 0 and bytes(incoming.data) == input_bits,
         "protected source/owned output return contract")
    return output, invoice


def query_stream(network, h, layer, address, omit_return=False):
    """Read one queried bit by a complete sequential scan, protecting network."""
    n = 1 << h
    need(0 <= layer < 2 * h - 1 and 0 <= address < n, "query domain")
    need(network.head == 0 and len(network.data) == n * (2 * h - 1), "complete network input")
    selected = layer * n + address  # bounded scalar multiplication; proof charges it.
    before = network.actions
    answer = Tape(expanded=network.expanded)
    for index in range(len(network.data)):
        value = network.read(1)
        need(value in (b"0", b"1"), "binary network entry")
        if index == selected:
            answer.write(value)
    if not omit_return:
        network.rewind()
    answer.rewind()
    need(len(answer.data) == 1 and answer.data[0] in (48, 49), "owned query bit exists")
    return answer, network.actions - before + answer.actions


def unpack(network, h):
    """Observer only: compare owned encoded output to the retained source API."""
    n = 1 << h
    schedule = list(range(h)) + list(reversed(range(h - 1)))
    return [(bit, tuple(int(chr(v)) for v in network.data[layer * n:(layer + 1) * n]))
            for layer, bit in enumerate(schedule)]


def run_case(permutation, p, source, expanded=False):
    n = len(permutation)
    h = n.bit_length() - 1
    incoming = b"".join(word(x, h) for x in permutation)
    output, invoice = compile_stream(incoming, h, p, expanded)
    expected = source.benes(permutation)
    need(unpack(output, h) == expected, "byte-exact retained compiler output")
    before = bytes(output.data)
    queries = steps = 0
    for layer, (bit, table) in enumerate(expected):
        for address in range(n):
            encoded_value, actions = query_stream(output, h, layer, address)
            value = int(bytes(encoded_value.data), 2)  # Observer of the owned one-bit output.
            need(value == table[address] == table[address ^ (1 << bit)], "exact queried target-independent bit")
            need(actions == 3 * len(output.data) + 3, "complete query scan, owned bit and return")
            queries += 1
            steps += actions
    need(bytes(output.data) == before and output.head == 0, "query protects encoded network")
    for address in range(n):
        need(source.run_network(unpack(output, h), address) == permutation[address], "permutation endpoint")
    invoice.update({"queries": queries, "query_tape_actions": steps,
                    "owned_output_sha256": hashlib.sha256(before).hexdigest()})
    return invoice


def rejected(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def finite(source):
    cases = []
    for n in (2, 4):
        cases.extend(("all_permutations", tuple(p), n.bit_length() - 1)
                     for p in itertools.permutations(range(n)))
    for n, moduli in ((4, (2, 3)), (8, (5, 7)), (16, (11,))):
        for modulus in moduli:
            offsets = range(modulus) if n <= 8 else (0, 1, 10)
            cases.extend(("modular_rotation", source.rotation(n, modulus, c), n.bit_length() - 1)
                         for c in offsets)
    cases.extend(("arbitrary", p, 3) for p in
                 ((7, 0, 6, 1, 5, 2, 4, 3), (1, 4, 7, 2, 5, 0, 3, 6)))
    cases.append(("wider_parameter", (3, 2, 0, 1), 7))
    receipts = []
    digest = hashlib.sha256()
    categories = {}
    for category, permutation, p in cases:
        invoice = run_case(permutation, p, source)
        categories[category] = categories.get(category, 0) + 1
        digest.update(json.dumps([list(permutation), invoice], sort_keys=True).encode() + b"\n")
        receipts.append(invoice)
    # Compare expanded one-cell execution with batched sequential macros.
    example = (2, 0, 3, 1)
    fast = run_case(example, 2, source)
    expanded = run_case(example, 2, source, expanded=True)
    need(fast == expanded, "expanded cell execution matches batched macro trace")
    return {"cases": len(cases), "categories": categories,
            "permutation_endpoints": sum(r["wires"] for r in receipts),
            "queried_control_bits": sum(r["queries"] for r in receipts),
            "logical_accesses": sum(r["logical_accesses"] for r in receipts),
            "records_scanned": sum(r["records_scanned"] for r in receipts),
            "arena_and_key_tape_actions": sum(r["arena_and_key_tape_actions"] for r in receipts),
            "maximum_arena_cells": max(r["arena_cells"] for r in receipts),
            "maximum_dfs_entries": max(r["maximum_dfs_entries"] for r in receipts),
            "expanded_one_cell_case": list(example), "receipt_sha256": digest.hexdigest(),
            "largest_case": max(receipts, key=lambda row: row["wires"]),
            "wider_parameter_case": receipts[-1]}


def mutations(source):
    failures = []
    failures.append(rejected(lambda: compile_stream(word(0, 2) * 4, 2, 2), "duplicate input permutation"))
    failures.append(rejected(lambda: compile_stream(b"001", 2, 2), "incomplete input encoding"))
    failures.append(rejected(lambda: compile_stream(b"0110", 2, 1), "h exceeds p"))
    failures.append(rejected(lambda: compile_stream(b"00100111", 2, 2, wrong_neighbor=True),
                             "wrong inverse-permutation matching edge"))
    arena = Arena(1, 1)
    arena.access((1, P, 0, 0), omit_return=True)
    need(arena.tape.head != 0, "missing arena return mutant detected")
    failures.append("missing arena head return")
    network, _ = compile_stream(b"01", 1, 1)
    _, actions = query_stream(network, 1, 0, 0, omit_return=True)
    need(network.head != 0 and actions != 3 * len(network.data) + 3, "missing query return tariff detected")
    failures.append("missing query return and tariff")
    network, _ = compile_stream(b"01", 1, 1)
    network.data[1] = 50  # A nonselected entry is not a binary bit.
    failures.append(rejected(lambda: query_stream(network, 1, 0, 0), "nonselected nonbinary network entry"))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    authenticated = {}
    for row in pins:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        need(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == row["git_blob"],
             "source Git blob: " + row["path"])
        authenticated[row["path"]] = data
    path = "research/unconditional-batched-crt/check_batched_crt.py"
    module = types.ModuleType("_pinned_benes_scan_reference")
    module.__file__ = str(ROOT / path)
    sys.modules[module.__name__] = module
    exec(compile(authenticated[path], module.__file__, "exec"), module.__dict__)
    result = {"schema_version": 1, "result": "PASS_UNIFORM_BENES_SCAN_COMPONENT",
              "base_commit": "12fa8c5c844be21bfefb38a19503fbd867a11244",
              "source_inputs_checked": len(authenticated), "finite": finite(module),
              "negative_controls": mutations(module),
              "limitations": ["Executed model charges sequential tape cells/heads; bounded scalar lowering is the written proof.",
                              "Canonical header decoding and pre-admission format checks are written lowerings, not executed microcode.",
                              "No literal complete finite-state transition table or proof-assistant formalization.",
                              "Beneš component only; no full CRT arithmetic/control evaluator or production placement.",
                              "No ordinary interchange, precision/native/outer multiplication theorem or new kappa."]}
    output = PACKAGE / "RESULT.json"
    if args.write_result:
        output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(output.read_text()) == result, "stored receipt differs from replay")
    print(json.dumps({"result": result["result"], "cases": result["finite"]["cases"],
                      "logical_accesses": result["finite"]["logical_accesses"]}, sort_keys=True))


if __name__ == "__main__":
    main()
