#!/usr/bin/env python3
"""Code-disjoint finite PR540 literal audit. Sricharan Vagvala / Codex, Apache-2.0.

No predecessor Python module is imported or executed. This is an external
source/execution check, not a Lean build or a complete multiplication proof.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import tarfile

PACKAGE = Path(__file__).resolve().parent
HEAD = "acc1917034d10f464271ab115fda314fd4eee7a3"
SOURCE = "4e16d001d505d4f21dd2bcfc44591f9be4c279bd"
LIVE, PRIVATE, SIZE, CHUNKS = 987, 987, 1024, 96


class Rejected(ValueError):
    """An input, literal, or semantic obligation did not match."""


def need(condition, message):
    if not condition:
        raise Rejected(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode()


def snapshot(package=PACKAGE):
    manifest = json.loads((package / "SOURCE-SNAPSHOT.json").read_text())
    need(manifest["format"] == "pinned-git-files-v1" and manifest["commit"] == HEAD,
         "snapshot commit/format")
    payload = (package / "PR540-SOURCES.tar.gz").read_bytes()
    need(sha(payload) == manifest["archive_sha256"], "snapshot archive digest")
    inventory = {f["member"]: f for f in manifest["files"]}
    need(len(inventory) == len(manifest["files"]) == 53, "snapshot inventory")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member in archive:
            need(member.isfile() and member.name in inventory and member.name not in files,
                 "unexpected/duplicate archive member")
            expected = inventory[member.name]
            need(member.size == expected["bytes"], "snapshot member length")
            data = archive.extractfile(member).read()
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            need(sha(data) == expected["sha256"] and blob == expected["git_blob"],
                 "snapshot member digest: " + member.name)
            need(expected["source_path"] == "research/lean-multi-host-source/" + member.name,
                 "snapshot source path")
            files[member.name] = data
    need(set(files) == set(inventory), "missing snapshot member")
    need((package / "NOTICE.source.md").read_bytes() == files["NOTICE.md"], "source notice retention")
    return files, sha(canonical(manifest))


def uncomment(source):
    """Remove Lean's nested block comments and line comments before tokenizing."""
    out, index, depth = [], 0, 0
    while index < len(source):
        pair = source[index:index + 2]
        if pair == "/-":
            depth += 1
            index += 2
        elif depth and pair == "-/":
            depth -= 1
            index += 2
            if not depth:
                out.append(" ")
        elif depth:
            if source[index] == "\n":
                out.append("\n")
            index += 1
        elif pair == "--":
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
        else:
            out.append(source[index])
            index += 1
    need(depth == 0, "unterminated Lean comment")
    return "".join(out)


def definitions(source):
    source = uncomment(source)
    matches = list(re.finditer(r"^def (\w+)\s*:\s*([^\n]+?)\s*:=\s*", source, re.M))
    result = {}
    for match in matches:
        name, kind = match.group(1, 2)
        need(name not in result, "duplicate declaration: " + name)
        end = re.search(r"^(?:def |abbrev |theorem |end |#print )", source[match.end():], re.M)
        body = source[match.end():] if end is None else source[match.end():match.end() + end.start()]
        result[name] = (kind.strip(), body.strip())
    return result


TOKEN = re.compile(r"\s*(::|\.leaf|\.node|[()\[\],⟨⟩]|\d+|[A-Za-z_]\w*)")


class Literal:
    """A closed grammar for the audited constructors, without Lean evaluation."""
    def __init__(self, source):
        self.tokens, index = [], 0
        while index < len(source):
            match = TOKEN.match(source, index)
            need(match is not None, "unsupported literal syntax at " + source[index:index + 30])
            self.tokens.append(match.group(1))
            index = match.end()
        self.index = 0

    def take(self, expected=None):
        need(self.index < len(self.tokens), "truncated literal")
        value = self.tokens[self.index]
        self.index += 1
        need(expected is None or value == expected, "unexpected token: " + value)
        return value

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def atom(self):
        token = self.take()
        if token == "(":
            value = self.atom()
            if self.peek() == ",":
                self.take(",")
                value = (value, self.atom())
            self.take(")")
            return value
        if token == ".leaf":
            value = self.atom()
            need(type(value) is int, "noninteger leaf")
            return value
        if token == ".node":
            return (self.atom(), self.atom())
        if token == "⟨":
            values = [self.atom()]
            while self.peek() == ",":
                self.take(",")
                values.append(self.atom())
            self.take("⟩")
            return tuple(values)
        if token == "[":
            self.take("]")
            return []
        if token == "true":
            return True
        if token == "false":
            return False
        if token == "some":
            value = self.atom()
            need(type(value) is int, "noninteger center")
            return ("some", value)
        if token.isdecimal():
            return int(token)
        need(re.fullmatch(r"[A-Za-z_]\w*", token) is not None, "unsupported atom")
        return token

    def end(self):
        need(self.index == len(self.tokens), "unconsumed literal syntax")


def atom(source):
    parser = Literal(source)
    value = parser.atom()
    parser.end()
    return value


class Trees:
    """Read a tree by low-bit index, including constant compressed leaves."""
    def __init__(self, values):
        self.values, self.visited = values, set()

    def get(self, value, index, depth=None):
        seen, branches = set(), 0
        while True:
            if isinstance(value, str):
                need(value in self.values and value not in seen, "missing/cyclic tree reference")
                seen.add(value)
                self.visited.add(value)
                value = self.values[value]
            elif type(value) is int:
                need(depth is None or branches == depth, "wrong checkpoint tree depth")
                return value
            else:
                need(isinstance(value, tuple) and len(value) == 2, "non-tree constructor")
                value = value[index & 1]
                index >>= 1
                branches += 1

    def table(self, root, size, depth=None):
        return [self.get(root, i, depth) for i in range(size)]


def nodes(files, prefix, count):
    expected = [f"{prefix}{i:02d}.lean" for i in range(count)]
    need(sorted(n for n in files if re.fullmatch(prefix + r"\d+\.lean", n)) == expected,
         "node module inventory")
    values = {}
    for name in expected:
        for key, (kind, body) in definitions(files[name].decode()).items():
            need(kind == "Tree Nat" and re.fullmatch(r"node\d+", key) and key not in values,
                 "node declaration")
            values[key] = atom(body)
    need(set(values) == {"node" + str(i) for i in range(len(values))}, "node numbering")
    return Trees(values)


def chunks(defs, kind, order_name, word_name):
    bodies = {n: b for n, (k, b) in defs.items() if k == kind and n.startswith("chunk")}
    public = {n for n in bodies if re.fullmatch(r"chunk\d+", n)}
    expected = ["chunk" + str(i) for i in range(CHUNKS)]
    need(public == set(expected), "chunk inventory")
    need(defs[order_name] == ("List (" + kind + ")", "[" + ",".join(expected) + "]"),
         "chunk order")
    need(defs[word_name] == (kind, order_name + ".flatten"), "word flatten definition")
    memo, active, visited = {}, set(), set()

    def expand(name):
        need(name in bodies and name not in active, "missing/cyclic chunk suffix")
        visited.add(name)
        if name in memo:
            return memo[name]
        active.add(name)
        parser, entries = Literal(bodies[name]), []
        while parser.peek() == "⟨":
            entries.append(parser.atom())
            parser.take("::")
        tail = parser.atom()
        parser.end()
        if tail != []:
            need(isinstance(tail, str) and re.fullmatch(name.split("_")[0] + r"_tail\d+", tail),
                 "cross-chunk or nonliteral suffix")
            entries.extend(expand(tail))
        active.remove(name)
        memo[name] = entries
        return entries

    result = [expand(name) for name in expected]
    need(visited == set(bodies), "unused chunk declaration")
    need([len(c) for c in result] == [200] * 95 + [2], "checkpoint boundaries")
    return result


def checkpoints(defs, trees, framed=False):
    state_names = {n for n in defs if re.fullmatch(r"state\d+", n)}
    need(state_names == {"state" + str(i) for i in range(97)}, "state inventory")
    result = []
    for i in range(97):
        kind, body = defs["state" + str(i)]
        need(kind == ("State" if framed else "Tree Nat × Bool"), "checkpoint type")
        value = atom(body)
        need(isinstance(value, tuple) and len(value) == 2, "checkpoint constructor")
        root, flag = value
        need(isinstance(root, str), "checkpoint root")
        if framed:
            need(flag == "none" or (isinstance(flag, tuple) and flag[0] == "some"), "center type")
            flag = None if flag == "none" else flag[1]
        else:
            need(flag is True, "false scalar checkpoint flag")
        result.append((trees.table(root, SIZE, depth=10), flag))
    need(trees.visited == set(trees.values), "unused checkpoint node")
    if not framed:
        need(defs["initial"] == ("Tree Nat", atom(defs["state0"][1])[0]), "initial alias")
        need(defs["expected"] == ("Tree Nat", atom(defs["state96"][1])[0]), "endpoint alias")
    return result


def decode_records(raw):
    need(len(raw) == 19002 * 24, "raw record length")
    result = []
    for op, x, y, c, frame, phase in struct.iter_unpack("<6i", raw):
        need(0 <= op <= 3, "raw opcode")
        if op <= 1:
            need(phase == 0 if op == 0 else 1 <= phase <= 5, "raw phase annotation")
            result.append([op, x, y, c, frame, 0])
        else:
            need(phase == (8 if op == 2 else 0), "raw copy/erase rank")
            result.append([op, x, y, c, frame, phase, 0])
    return result


def scalar_entry(e):
    return (e[0], e[1], e[2], bool(e[3] % 2))


def frame_entry(e):
    op, _, y, c, f = e[:5]
    fields = (y, c, f) if op == 0 else ((f, f, 0) if op == 1 else (c, f, e[5]))
    return (scalar_entry(e), *fields)


def replay(word, states, frames, scalar_states, frame_states, dirty_private=False):
    """Sparse GF(2) supports check every original dirty input simultaneously."""
    rows = [frozenset([i]) for i in range(LIVE)] + [frozenset()] * (SIZE - LIVE)
    if dirty_private:
        rows[PRIVATE] = frozenset([LIVE])
    labels = [states["initial"][str(i)] for i in range(LIVE)] + [0] * (SIZE - LIVE)
    center, matrix_trace, frame_trace = None, hashlib.sha256(), hashlib.sha256()

    def compare(k):
        bits = [sum(1 << i for i in row) for row in rows]
        need(bits == scalar_states[k][0], f"scalar checkpoint {k}")
        need((labels, center) == frame_states[k], f"frame checkpoint {k}")
        matrix_trace.update(canonical([k, bits]) + b"\n")
        frame_trace.update(canonical([k, labels, center]) + b"\n")

    # This control skips checkpoint equality so it exercises the COPY guard.
    if not dirty_private:
        compare(0)
    counts, copies = Counter(), []
    for k, e in enumerate(word):
        op, x, y, c, f = e[:5]
        need(op in range(4) and len(e) == (6 if op < 2 else 7) and e[-1] == 0, "event schema")
        need(0 <= x < LIVE, f"register bound at event {k}")
        need(op >= 2 or x != center, f"write to retained center at event {k}")
        counts[op] += 1
        if op == 0:
            need(str(y) in frames and str(c) in frames and labels[x] == y,
                 f"MOVE frame at event {k}")
            need(f == frames[str(c)]["dim"] - frames[str(y)]["dim"] and f >= 0,
                 f"MOVE rank at event {k}")
            labels[x] = c
        elif op == 1:
            need(0 <= y <= PRIVATE and x != y and c == 1, f"ADD operands at event {k}")
            need(labels[x] == labels[y] == f, f"ADD frame at event {k}")
            need(y != PRIVATE or center is not None, f"closed private read at event {k}")
            rows[x] = rows[x].symmetric_difference(rows[y])
        elif op == 2:
            need(y == PRIVATE and center is None and not rows[y], f"COPY clean guard at event {k}")
            need(labels[x] == c and e[5] == 8, f"COPY frame/rank at event {k}")
            rows[y], labels[y], center = rows[x], f, x
            copies.append(k)
        else:
            need(y == PRIVATE and center == x and rows[y] == rows[x], f"ERASE guard at event {k}")
            need(labels[x] == c and labels[y] == f and e[5] == 0, f"ERASE frame/rank at event {k}")
            rows[y], labels[y], center = frozenset(), 0, None
        if not dirty_private and ((k + 1) % 200 == 0 or k + 1 == len(word)):
            compare((k + 200) // 200)
    expected = [frozenset([i, i - 120]) if 120 <= i < 240 else frozenset([i])
                for i in range(LIVE)] + [frozenset()] * (SIZE - LIVE)
    need(rows == expected and center is None, "arbitrary-dirty endpoint")
    need(labels[:LIVE] == [states["final"][str(i)] for i in range(LIVE)] and
         labels[LIVE:] == [0] * (SIZE - LIVE), "final frame labels")
    need(dict(counts) == {0: 4291, 1: 14693, 2: 9, 3: 9}, "opcode coverage")
    return {"events": len(word), "opcodes": {str(k): v for k, v in sorted(counts.items())},
            "independent_dirty_columns": LIVE, "checkpoint_states": 97,
            "scalar_rows_compared": 97 * SIZE, "frame_labels_compared": 97 * SIZE,
            "matrix_trace_sha256": matrix_trace.hexdigest(), "frame_trace_sha256": frame_trace.hexdigest(),
            "copy_event_indices": copies, "clean_copy_erase_pairs": 9, "untouched_padding_rows": 36}


def ownership(template, states, frames, files):
    calls = [c for c in template["calls"] if c["stage"] == 2 and c["replica"] == 0]
    need(len(calls) == 1 and calls[0]["pair"] == 0 and calls[0]["orientation"] == "forward",
         "selected invocation")
    owners = calls[0]["owners"]
    need(len(owners) == LIVE and [o[0] for o in owners[:240]] == list(range(240)), "data owners")
    initial = [states["initial"][str(i)] for i in range(LIVE)]
    keys = sorted({tuple(route[1:]) + (initial[i],) for i, (_, route) in enumerate(owners) if i >= 240})
    need(len(keys) == 16 and all(len(k) == 4 for k in keys), "helper slot keys")
    definitions_by_name = {}
    for name in ["OwnershipDatumCore.lean", "OwnershipInverseTable.lean"]:
        for key, (kind, body) in definitions(files[name].decode()).items():
            if kind == "Lookup":
                need(key not in definitions_by_name, "duplicate ownership table")
                definitions_by_name[key] = atom(body)
    trees = Trees(definitions_by_name)
    expected_names = {"familyTable", "tagTable", "initialFrameTable", "sourceBits", "targetBits",
                      "tagInitialFrame", "tagChild", "tagOffset", "tagWidth", "permTable",
                      "invPermTable", "inverseOwnerTable"}
    need({n for n in definitions_by_name if "_part" not in n} == expected_names, "ownership inventory")

    def table(name, values, size=None, padding=0):
        domain = len(values) if size is None else size
        expected = values + [padding] * (domain - len(values))
        need(trees.table(name, domain) == expected, "ownership table: " + name)

    families = [o[0] for o in owners]
    tags = [0] * 240 + [keys.index(tuple(route[1:]) + (initial[i],))
                       for i, (_, route) in enumerate(owners) if i >= 240]
    need(all(240 <= f < 720 for f in families[240:]), "helper family domain")
    need(all((tag >= 7) == (family >= 480) for family, tag in zip(families[240:], tags[240:])),
         "helper child/family binding")
    codes = [16 * f + t for f, t in zip(families, tags)]
    need(len(set(codes)) == LIVE, "owner injectivity")
    inverse = [LIVE] * (720 * 16)
    for i, code in enumerate(codes):
        inverse[code] = i
    table("familyTable", families, SIZE)
    table("tagTable", tags, SIZE)
    table("initialFrameTable", initial, SIZE)
    table("inverseOwnerTable", inverse, 16384)
    permutations, sources, targets = [], [], []
    for child, off, width, fr in keys:
        need(child in [1, 2] and 0 <= off and 1 <= width <= 8, "helper descriptor")
        frame = frames[str(fr)]
        src = []
        for row in frame["A"]:
            need(len(row) == 8 and row.count(1) == 1 and row.count(0) == 7, "coordinate frame A")
            src.append(row.index(1))
        need(len(src) == width and len(set(src)) == width, "source kernel width")
        occupied = [i for i in range(8) if i not in src]
        need(frame["dim"] == 8 - width and sorted(frame["B"]) ==
             sorted([[2 * int(i == j) for j in range(8)] for i in occupied]), "coordinate frame B")
        # Original PR540 bases; PR1228/1231 separately derive them from the schedule.
        dst = list(range((15 if child == 1 else 1) + off,
                         (15 if child == 1 else 1) + off + width))
        need(dst[-1] < 64, "target axis domain")
        assignments = dict(zip(src, dst))
        assignments.update(zip([i for i in range(64) if i not in src],
                               [i for i in range(64) if i not in dst]))
        perm = [assignments[i] for i in range(64)]
        need(sorted(perm) == list(range(64)), "coordinate bijection")
        permutations.append(perm)
        sources.append(sum(1 << i for i in src))
        targets.append(sum(1 << i for i in dst))
    need(len({tuple(p) for p in permutations}) == 16, "distinct coordinate charts")
    table("permTable", [x for p in permutations for x in p])
    table("invPermTable", [p.index(i) for p in permutations for i in range(64)])
    for name, values in [("sourceBits", sources), ("targetBits", targets),
                         ("tagInitialFrame", [k[3] for k in keys]),
                         ("tagChild", [k[0] for k in keys]), ("tagOffset", [k[1] for k in keys]),
                         ("tagWidth", [k[2] for k in keys])]:
        table(name, values)
    need(trees.visited == set(trees.values), "unused ownership subtree")
    return {"roles": LIVE, "helpers": 747, "helper_families": len(set(families[240:])),
            "coordinate_permutations": 16, "permutation_entries": 1024,
            "inverse_permutation_entries": 1024, "inverse_owner_entries": 11520,
            "inverse_owner_padding_entries": 4864, "tables": 12,
            "source_route_sha256": sha(canonical(owners)),
            "owner_code_sha256": sha(canonical(codes)), "permutations_sha256": sha(canonical(permutations))}


def audit(files):
    versions = json.loads(files["source-versions.json"])
    need(versions["selected_pr442"] == SOURCE, "PR442 source commit")
    inputs = {}
    for name in ["hosted-template.json.gz", "parent-template.json.gz", "frames.json.gz",
                 "states.json.gz", "records.bin.gz"]:
        raw = gzip.decompress(files["inputs/" + name])
        # snapshot() admits hashes; separate semantic entry points support
        # deliberately mutated data without merely testing digest rejection.
        inputs[name] = raw if name.endswith("bin.gz") else json.loads(raw)
    template, parent = inputs["hosted-template.json.gz"], inputs["parent-template.json.gz"]
    states, frames = inputs["states.json.gz"], inputs["frames.json.gz"]["frames"]
    word = decode_records(inputs["records.bin.gz"])
    need(word == template["local_programs"]["forward"] == parent["local_programs"]["forward"],
         "binary/parent/hosted ordered word")
    need(sha(canonical(word)) == versions["selected_invocation"]["canonical_forward_sha256"],
         "canonical source word")
    matrix_defs = definitions(files["MatrixData.lean"].decode())
    frame_defs = definitions(files["FrameTraceLiterals.lean"].decode())
    scalar_chunks = chunks(matrix_defs, "List Event", "forwardChunks", "forwardWord")
    frame_chunks = chunks(frame_defs, "List Entry", "chunks", "forward")
    need([e for c in scalar_chunks for e in c] == [scalar_entry(e) for e in word], "scalar literal word")
    need([e for c in frame_chunks for e in c] == [frame_entry(e) for e in word], "framed literal word")
    scalar_states = checkpoints(matrix_defs, nodes(files, "MatrixNodes", 22))
    frame_states = checkpoints(frame_defs, nodes(files, "FrameTraceNodes", 17), framed=True)
    result = replay(word, states, frames, scalar_states, frame_states)
    result["ownership"] = ownership(template, states, frames, files)
    return result


def verify(package=PACKAGE):
    files, manifest_sha = snapshot(package)
    result = audit(files)
    result.update(status="PASS_PR540_LITERAL_SOURCE_AUDIT", audited_pr540=HEAD,
                  source_pr442=SOURCE, snapshot_files=len(files), source_manifest_sha256=manifest_sha,
                  source_binary_sha256=sha(gzip.decompress(files["inputs/records.bin.gz"])))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true", help="write this package's reproducible receipt")
    args = parser.parse_args()
    result = verify()
    if args.write_receipt:
        (PACKAGE / "EXPECTED.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(result == json.loads((PACKAGE / "EXPECTED.json").read_text()), "frozen audit receipt")
    print(result["status"])
    print(f"{result['events']} events; {result['checkpoint_states']} states; "
          f"{result['scalar_rows_compared']} scalar rows; 987 owners; 16 permutations")


if __name__ == "__main__":
    main()
