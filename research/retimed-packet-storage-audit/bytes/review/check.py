#!/usr/bin/env python3
"""Independent finite stream/permutation checks of the source-local byte theorem.

Uses source-extracted functions with a separate in-memory endpoint interpreter.
It does not invoke the author's meters, checkers, or runtime restoration.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path
import inspect
import json
import random

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise AssertionError(why)


class Span:
    """Read/write semantics plus every visited endpoint, including zero tails."""
    def __init__(self, data=b"", key="external"):
        self.raw = BytesIO(data)
        self.key = key
        self.high = len(data)
        self.closed = False
        self.dirty_truncations = 0

    def tell(self):
        return self.raw.tell()

    def seek(self, offset, whence=0):
        answer = self.raw.seek(offset, whence)
        self.high = max(self.high, answer)
        return answer

    def read(self, n=-1):
        data = self.raw.read(n)
        self.high = max(self.high, self.tell())
        return data

    def write(self, data):
        answer = self.raw.write(data)
        self.high = max(self.high, self.tell())
        return answer

    def truncate(self, size=None):
        size = self.tell() if size is None else size
        if any(self.raw.getvalue()[size:]):
            self.dirty_truncations += 1
        return self.raw.truncate(size)

    def value(self):
        return self.raw.getvalue()

    def close(self):
        need(not any(self.value()), "dirty contents at closed stream " + self.key)
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def extracted(path, names, env, transform=None):
    tree = ast.parse(path.read_text(), filename=str(path))
    selected = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    need({n.name for n in selected} == set(names), "source function unavailable: " + str(path))
    unit = ast.Module(body=selected, type_ignores=[])
    if transform:
        unit = transform.visit(unit)
        ast.fix_missing_locations(unit)
    exec(compile(unit, str(path), "exec"), env)


class Harness:
    def __init__(self, sources):
        self.created = []
        self.env = {"CHUNK": 65536, "ZEROS": bytes(65536), "contextmanager": contextmanager}
        self.live = set()
        self.previous_calls = 0

        @contextmanager
        def work_tapes(count):
            caller = inspect.currentframe().f_back.f_back
            site = caller.f_code.co_qualname
            tapes = [Span(key=site + ":" + str(i)) for i in range(count)]
            need(not (set(t.key for t in tapes) & self.live), "same fixed work role reentered")
            self.live.update(t.key for t in tapes)
            self.created.extend(tapes)
            try:
                yield tapes
            finally:
                for tape in tapes:
                    self.env["erase"](tape)
                    tape.close()
                    self.live.remove(tape.key)

        self.env["work_tapes"] = work_tapes
        extracted(sources / "streaming_routes.py", ["read_exact", "copy_bytes", "write_zeros", "erase",
                  "ternary_extent", "join_buckets", "negate_field", "shift_field", "type_route"], self.env)
        extracted(sources / "limb_scale.py", ["unit_scale"], self.env)
        extracted(sources / "quotient_route.py", ["sort_packets"], self.env)

    def peaks(self):
        answer = {}
        for tape in self.created:
            answer[tape.key] = max(answer.get(tape.key, 0), tape.high)
            need(not tape.dirty_truncations, "dirty truncation in source execution")
        need(not self.live, "work role survived")
        return answer

    def previous_swap(self, source, target, digits, front, gap, piece):
        """Independent complete-index transpose, no source route implementation."""
        self.previous_calls += 1
        side = 3**digits
        data = source.read(front * side**2 * gap * piece)
        need(len(data) == front * side**2 * gap * piece, "short swap oracle input")
        for p, right, g, left in product(range(front), range(side), range(gap), range(side)):
            index = ((p * side + left) * gap + g) * side + right
            target.write(data[index * piece:(index + 1) * piece])


def token_data(count, width=4):
    return b"".join(i.to_bytes(width, "little") for i in range(count))


def type_checks(sources):
    count = 0
    witnessed_padding = False
    for rows, types, piece in product((1, 2, 5), range(2, 18), (1, 3)):
        data = bytes((31 * i + i // 251 + 7) % 256 for i in range(rows * types * piece))
        transposed = b"".join(data[(r * types + t) * piece:(r * types + t + 1) * piece]
                              for t in range(types) for r in range(rows))
        for inverse in (False, True):
            h = Harness(sources)
            source, target = Span(transposed if inverse else data), Span()
            h.env["type_route"](source, target, rows, types, piece, inverse=inverse)
            need(target.value() == (data if inverse else transposed), "opaque type transpose failed")
            _, extent = h.env["ternary_extent"](types)
            padded = rows * extent * piece
            peaks = h.peaks()
            need(len(peaks) == 5, "type tuple arity")
            for key, value in peaks.items():
                slot = int(key.rsplit(":", 1)[1])
                need(value <= (padded if slot < 2 else padded // 3), "type individual byte bound")
            need(sum(peaks.values()) <= 3 * padded < 9 * len(data), "type total byte bound")
            witnessed_padding |= sum(peaks.values()) > 3 * len(data)
            count += 1
    for rows, types, piece in ((0, 2, 3), (3, 2, 0), (3, 1, 4)):
        h = Harness(sources)
        data = b"x" * (rows * types * piece)
        out = Span()
        h.env["type_route"](Span(data), out, rows, types, piece)
        need(out.value() == data and not h.created, "zero/singleton route should have no scratch")
        count += 1
    need(witnessed_padding, "padding-omission negative control was not exercised")
    return {"cases": count, "padding_omission_rejected": witnessed_padding}


def scaler_checks(sources):
    count = 0
    visited = set()
    earlier = 0
    for digits, prefixes in product(range(8), (1, 2)):
        side = 3**digits
        for unit in (1, 2, 4, 5, 8, 17):
            h = Harness(sources)
            data = token_data(prefixes * side)
            out = Span()
            h.env["unit_scale"](Span(data), out, digits, prefixes, 4, unit, h.previous_swap)
            inverse = pow(unit, -1, side) if side > 1 else 0
            expected = b"".join(((p * side + (x * inverse % side))).to_bytes(4, "little")
                                for p in range(prefixes) for x in range(side))
            need(out.value() == expected, "unit scale disagrees with direct modular permutation")
            peaks = h.peaks()
            visited.update(key.rsplit(":", 1)[0] for key in peaks)
            size = len(data)
            for key, value in peaks.items():
                cap = size if "<locals>" not in key else Fraction(size, 3)
                need(value <= cap, "individual scaler role bound")
            need(sum(peaks.values()) <= Fraction(17 * size, 3), "all-site scaler historical bound")
            earlier += h.previous_calls
            count += 1
    need(any("odd_step" in x for x in visited) and any("carry_step" in x for x in visited),
         "both nonconcurrent auxiliary sites must be counted")
    return {"cases": count, "sites": sorted(visited), "external_swap_oracle_calls": earlier}


class DropBucketErase(ast.NodeTransformer):
    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == "erase" and len(node.value.args) == 1:
                if isinstance(node.value.args[0], ast.Name) and node.value.args[0].id == "tape":
                    return ast.copy_location(ast.Pass(), node)
        return self.generic_visit(node)


def sort_checks(sources):
    count = 0
    rng = random.Random(20261123)
    for width, slots, block, groups in ((4, 16, 7, 3), (9, 416, 2, 2), (1, 3, 11, 4)):
        h = Harness(sources)
        labels = list(product(range(3), repeat=width))[:slots]
        rng.shuffle(labels)
        blocks = [bytes((17 * j + k + 1) % 256 for k in range(block)) for j in range(slots)]
        expected = b"".join(data for _, data in sorted(zip(labels, blocks)))
        with h.env["work_tapes"](10) as tapes:
            for _ in range(groups):
                data, tags, *aux = tapes
                data.write(b"".join(blocks))
                tags.write(b"".join(bytes(x) for x in labels))
                out = Span()
                h.env["sort_packets"](data, tags, out, slots, block, width, aux)
                need(out.value() == expected, "radix sort differs from independent lexicographic oracle")
                need(all(t.value() == b"" for t in tapes), "group did not reset both ping-pong parities")
                count += 1
        peaks = h.peaks()
        P, T = slots * block, slots * width
        caps = [P, T, P, T, T, P, T, P, T, P]
        need(all(value <= caps[int(key.rsplit(":", 1)[1])] for key, value in peaks.items()),
             "individual radix position exceeded payload or tag extent")
        need(sum(peaks.values()) <= 5 * P + 5 * T, "radix historical sum bound")
    h = Harness(sources)
    extracted(sources / "quotient_route.py", ["sort_packets"], h.env, DropBucketErase())
    rejected = False
    try:
        with h.env["work_tapes"](10) as tapes:
            data, tags, *aux = tapes
            data.write(bytes(range(16)))
            tags.write(b"".join(bytes(x) for x in list(product(range(3), repeat=4))[:16]))
            h.env["sort_packets"](data, tags, Span(), 16, 1, 4, aux)
        rejected = any(t.high > (64 if i in (1,3,4,6,8) else 16)
                       for i,t in enumerate(h.created))
    except (EOFError, IndexError, AssertionError):
        rejected = True
    need(rejected, "erasure mutation escaped radix byte/output checks")
    return {"groups": count, "odd_and_even_pass_parity": True, "bucket_erase_mutation_rejected": rejected}


def repair_checks(sources):
    records = []
    for bits, suffix, component, pattern in ((0,0,1,"all"), (6,0,1,"all"), (7,1,1,"odd"),
                                             (9,2,2,"third"), (10,1,13,"all"), (5,0,1,"none")):
        created = []
        def factory():
            tape = Span(key="repair-file:" + str(len(created)))
            created.append(tape)
            return tape
        env = {"TemporaryFile": factory, "contextmanager": contextmanager}
        extracted(sources / "spool.py", ["transfer", "zero_bytes", "scratch", "Field"], env)
        extracted(sources / "compact_columns.py", ["Columns"], env)
        field = env["Field"](bits, component, Span())
        total = (1 << bits) * 2 * component
        payload = bytes((19 * i + i // 251 + 7) % 256 for i in range(total))
        field.stream.write(payload)
        M = 1 << (bits - suffix)
        a = (2 * component) << suffix
        t = max(1, (bits - suffix + 7) // 8)
        def good(address):
            i = address >> suffix
            return pattern == "none" or (pattern == "odd" and i % 2 == 0) or (pattern == "third" and i % 3 == 0)
        def key(address):
            return address ^ (1 << (bits - 1)) if pattern == "odd" else address
        expected = bytearray(total)
        E = 0
        for i in range(M):
            target = i if good(i << suffix) else key(i << suffix) >> suffix
            E += not good(i << suffix)
            expected[target * a:(target + 1) * a] = payload[i * a:(i + 1) * a]
        columns = env["Columns"](1,0,1,0,0,0,suffix,None)
        columns.repair(field, good, key)
        need(field.stream.value() == bytes(expected), "repair differs from independent destination-array oracle")
        need(len(created) == 5, "repair must have one replacement and four scratch streams")
        peaks = [x.high for x in created[1:]]
        need(all(x.closed and not x.value() for x in created[1:]), "repair did not scrub physical scratch")
        need(not any(x.dirty_truncations for x in created), "repair truncated a dirty tail")
        need(peaks[0] == E * (a+t), "exact tagged extent")
        need(all(peaks[i] <= E * (a+t) for i in range(3)) and peaks[3] <= (M-E)*a,
             "individual repair extent")
        need(sum(peaks) <= total + 2*E*a + 3*E*t, "four-role repair sum")
        need(sum(peaks) + 2*total <= 8*total, "tested production-shaped byte cover")
        records.append({"L":bits,"z":suffix,"component":component,"pattern":pattern,
                        "field_bytes":total,"bad_groups":E,"scratch_highs":peaks})
        field.retire()
    # For an all-bad identity repair every binary label occurs once. At each
    # nonempty bit pass exactly M/2 labels enter each bucket. Hence these are
    # exact symbolic historical extents, not a production-sized execution.
    boundaries = []
    for L in (17,33):
        M, a, t = 1 << L, 2, (L+7)//8
        V = M*a
        dirty = M*(a+t)
        bucket = M//2*(a+t)
        complete = dirty + 2*bucket + 2*V
        boundaries.append({"L":L,"V":V,"dirty":dirty,"each_binary_bucket":bucket,
                           "complete_with_input_and_replacement":complete,
                           "ratio":str(Fraction(complete,V)),"execution":"symbolic complete-label census"})
    need(boundaries[0]["ratio"] == "7" and boundaries[1]["ratio"] == "9", "generic boundary arithmetic")
    return {"cases":records,"symbolic_api_boundaries":boundaries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=HERE.parent)
    parser.add_argument("--output", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    sources = args.package / "sources"
    pins = json.loads((args.package / "SOURCE-BINDINGS.json").read_text())
    for item in pins["resolved_modules"].values():
        need(sha256((sources / item["file"]).read_bytes()).hexdigest() == item["sha256"], "source pin changed")
    for name,digest in pins["retained_files"].items():
        need(sha256((sources/name).read_bytes()).hexdigest() == digest, "retained source pin changed")
    coefficient = 1 + Fraction(5) + Fraction(20,81) + Fraction(47,48)
    need(coefficient < 8, "route envelope arithmetic")
    for N in range(2,65):
        need(Fraction(N*N,3**(2*N)) <= Fraction(4,81), "tag dominance")
        need(prod(3**j-1 for j in range(1,N+1)) >= 16, "low-count dominance")
    result = {"status":"PASS_INDEPENDENT_LOCAL_BYTE_REVIEW", "source_commit":pins["commit"],
              "proof_sha256":sha256((args.package/"PROOF.md").read_bytes()).hexdigest(),
              "route_envelope_upper_coefficient":str(coefficient),
              "type":type_checks(sources),"scaler":scaler_checks(sources),
              "sorter":sort_checks(sources),"repair":repair_checks(sources),
              "scope":"finite source-extracted stream checks plus exact symbolic boundaries; universal theorem remains source proof, with all declared external contracts"}
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
