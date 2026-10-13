#!/usr/bin/env python3
"""Audit the complete, pinned PR612 data expressions against PR543's payload.

This recognizes a deliberately closed subset of these three Lean data modules.
It neither executes Lean nor validates proof terms or general Lean expressions.
No supplier, generator, predecessor checker, or other repository code is imported.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys


class AuditError(ValueError):
    pass


CURRENT = "research/lean-current-r420-boundary-interfaces/CurrentR420BoundaryData.lean"
BOUNDARY = "research/community-cold617-audit/pr612/lean/SelectedBitCarrierBoundaryData.lean"
PHASE = "research/community-cold617-audit/pr612/lean/SelectedBitCarrierPhaseBData.lean"
WORD_PATH = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
EXPECTED_PATHS = {CURRENT, BOUNDARY, PHASE, WORD_PATH,
    "research/community-cold617-audit/im-cold617-formal-binding.py",
    "research/community-cold617-audit/pr612/lean/SOURCE-CORRESPONDENCE.json",
    "research/lean-current-r420-boundary-interfaces/CurrentR420PhaseBXor.lean",
    "research/lean-current-r420-boundary-interfaces/DEPENDENCIES.json",
    "research/lean-current-r420-boundary-interfaces/SOURCE_BINDING.json"}


def require(ok, message):
    if not ok:
        raise AuditError(message)


def tokens(text):
    """Tokenize without searching inside strings or nested Lean comments."""
    result, i = [], 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith("--", i):
            end = text.find("\n", i + 2)
            i = len(text) if end < 0 else end + 1
        elif text.startswith("/-", i):
            i, depth = i + 2, 1
            while i < len(text) and depth:
                if text.startswith("/-", i):
                    depth, i = depth + 1, i + 2
                elif text.startswith("-/", i):
                    depth, i = depth - 1, i + 2
                else:
                    i += 1
            require(depth == 0, "unterminated Lean comment")
        elif c == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                require(text[j] not in "\\\r\n", "unsupported Lean string escape/newline")
                j += 1
            require(j < len(text), "unterminated Lean string")
            result.append(text[i:j + 1])
            i = j + 1
        elif c.isascii() and (c.isalpha() or c == "_"):
            j = i + 1
            while j < len(text) and text[j].isascii() and (text[j].isalnum() or text[j] in "_.'"):
                j += 1
            result.append(text[i:j])
            i = j
        elif c in "0123456789":
            j = i + 1
            while j < len(text) and text[j] in "0123456789":
                j += 1
            require(j == i + 1 or c != "0", "noncanonical numeral")
            result.append(text[i:j])
            i = j
        elif text[i:i + 2] in (":=", "++", "=>"):
            result.append(text[i:i + 2])
            i += 2
        elif c in "[](),.:+*-×⟨⟩'":
            result.append(c)
            i += 1
        else:
            raise AuditError(f"unsupported Lean character at offset {i}: {c!r}")
    return result


def module(text, prefix, suffix, names):
    ts, pre, post = tokens(text), tokens(prefix), tokens(suffix)
    require(ts[:len(pre)] == pre and ts[-len(post):] == post, "module wrapper differs")
    ts = ts[len(pre):-len(post)]
    out, i = {}, 0
    while i < len(ts):
        require(ts[i] in ("def", "abbrev") and i + 2 < len(ts), "expected data declaration")
        kind, name = ts[i:i + 2]
        require(name not in out, f"duplicate declaration: {name}")
        i += 2
        header = []
        while i < len(ts) and ts[i] != ":=":
            header.append(ts[i])
            i += 1
        require(i < len(ts), f"missing definition body: {name}")
        i += 1
        start = i
        while i < len(ts) and ts[i] not in ("def", "abbrev"):
            i += 1
        require(i > start, f"empty definition body: {name}")
        out[name] = (kind, header, ts[start:i])
    require(list(out) == names.split(), "declaration names/order differ")
    return out


def rhs(decls, name, header, kind="def"):
    actual_kind, actual_header, body = decls[name]
    require(actual_kind == kind and actual_header == tokens(header), f"declaration type differs: {name}")
    return body


def fixed(decls, name, header, expression, kind="def"):
    require(rhs(decls, name, header, kind) == tokens(expression), f"unsupported expression: {name}")


def literal(ts, allow_fin=False):
    """Recursively consume one entire numeric/string/list/tuple/Fin literal."""
    i = 0

    def take(expected):
        nonlocal i
        require(i < len(ts) and ts[i] == expected, f"expected literal token {expected!r}")
        i += 1

    def value():
        nonlocal i
        require(i < len(ts), "truncated literal")
        t = ts[i]
        i += 1
        if t in ("[", "("):
            end = "]" if t == "[" else ")"
            items = []
            if i < len(ts) and ts[i] != end:
                items.append(value())
                while i < len(ts) and ts[i] == ",":
                    i += 1
                    items.append(value())
            take(end)
            require(t == "[" or len(items) == 3, "only triple tuples are supported")
            return items if t == "[" else tuple(items)
        if t == "⟨":
            require(allow_fin, "Fin constructor outside frameOrder")
            n = value()
            require(type(n) is int and 0 <= n < 672, "Fin literal out of bounds")
            for expected in (",", "by", "decide", "⟩"):
                take(expected)
            return ("Fin", n)
        if t == "-":
            require(i < len(ts) and ts[i].isascii() and ts[i].isdigit(), "bad negative literal")
            n = -int(ts[i])
            i += 1
            return n
        if t.startswith('"'):
            return t[1:-1]
        require(t.isascii() and t.isdigit(), f"not a supported literal: {t}")
        return int(t)

    result = value()
    require(i == len(ts), "trailing expression after literal")
    return result


def gates(ts):
    value = literal(ts)
    require(type(value) is list and all(type(g) is tuple and len(g) == 3 for g in value), "expected list of gate tuples")
    return [list(g) for g in value]


def extract_projection(current_text, boundary_text, phase_text):
    old = module(boundary_text, "import Init namespace CurrentMain.SelectedBitCarrierBoundary.Data",
                 "end CurrentMain.SelectedBitCarrierBoundary.Data", "h v R format form lines frames start final ret registers")
    prior = module(phase_text, "import SelectedBitCarrierBoundaryCheck namespace CurrentMain.SelectedBitCarrierPhaseB.Data",
                   "end CurrentMain.SelectedBitCarrierPhaseB.Data", "phaseB scatter")
    cur = module(current_text, "import SelectedBitCarrierPhaseBData namespace CurrentMain.CurrentR420Boundary.Data set_option Elab.async false",
                 "end CurrentMain.CurrentR420Boundary.Data", "h v R registers format form coords lines frameOrder frameAt frames start final ret scatter firstTargets sourceMiddle lastTargets phaseB Reg ExtendedReg embed temporary")
    old_types = {"h": "Nat", "v": "Nat", "R": "Nat", "format": "String", "form": "String", "lines": "List (List Int)", "frames": "List (List Nat)", "start": "List Nat", "final": "List Nat", "ret": "List Nat"}
    data = {name: literal(rhs(old, name, ": " + typ)) for name, typ in old_types.items()}
    fixed(old, "registers", ": Nat", "2*v+R")
    gates(rhs(prior, "phaseB", ": List (Nat × Nat × List Nat)"))  # Not reused as current B.
    scatter = literal(rhs(prior, "scatter", ": List (List Nat)"))
    for name in ("h", "v", "format", "form", "lines"):
        fixed(cur, name, "", "SelectedBitCarrierBoundary.Data." + name, "abbrev")
    fixed(cur, "scatter", "", "SelectedBitCarrierPhaseB.Data.scatter", "abbrev")
    r = literal(rhs(cur, "R", ": Nat"))
    coords = literal(rhs(cur, "coords", ": String"))
    fixed(cur, "registers", ": Nat", "2*v+R")
    order = literal(rhs(cur, "frameOrder", ": List (Fin 672)"), allow_fin=True)
    require(type(order) is list and all(type(i) is tuple and len(i) == 2 and i[0] == "Fin" for i in order), "expected explicit Fin constructors in frameOrder")
    order = [i[1] for i in order]
    require(sorted(order) == list(range(672)), "frameOrder is not the required permutation")
    fixed(cur, "frameAt", "(i : Fin 672) : List Nat", "SelectedBitCarrierBoundary.Data.frames[i.val]'(by rw [SelectedBitCarrierBoundary.frame_domain.1] exact i.isLt)")
    fixed(cur, "frames", ": List (List Nat)", "frameOrder.map frameAt")
    fixed(cur, "start", ": List Nat", "(List.range 120).map (fun r => r+2) ++ List.replicate 540 0")
    fixed(cur, "final", ": List Nat", "SelectedBitCarrierBoundary.Data.final.take 660")
    ret = literal(rhs(cur, "ret", ": List Nat"))
    bands = [gates(rhs(cur, name, ": List (Nat × Nat × List Nat)")) for name in ("firstTargets", "sourceMiddle", "lastTargets")]
    fixed(cur, "phaseB", "", "firstTargets ++ sourceMiddle ++ lastTargets")
    fixed(cur, "Reg", "", "Fin 660", "abbrev")
    fixed(cur, "ExtendedReg", "", "Fin 661", "abbrev")
    fixed(cur, "embed", "(r : Reg) : ExtendedReg", "⟨r.val, Nat.lt_trans r.isLt (by decide)⟩")
    fixed(cur, "temporary", ": ExtendedReg", "⟨660, by decide⟩")
    require(data["h"] == 8 and data["v"] == 120 and type(r) is int and r == 420, "current dimensions differ")
    require(len(data["frames"]) == 672 and len(data["final"]) >= 660, "historical table dimensions differ")
    require([len(b) for b in bands] == [120, 597, 120], "B band lengths differ")
    projection = {k: data[k] for k in ("h", "v", "format", "form", "lines")}
    projection.update(R=r, coords=coords, frames=[data["frames"][i] for i in order],
                      start=list(range(2, 122)) + [0] * 540, final=data["final"][:660],
                      ret=ret, scatter=scatter, B=bands[0] + bands[1] + bands[2])
    validate_projection(projection)
    return projection


def validate_projection(p):
    def nat(n, bound):
        return type(n) is int and 0 <= n < bound

    def rows(value, count, entry):
        return type(value) is list and len(value) == count and all(type(row) is list and all(entry(x) for x in row) for row in value)

    require(p["h"] == 8 and p["v"] == 120 and p["R"] == 420, "wrong dimensions")
    require(rows(p["lines"], 120, lambda n: type(n) is int) and all(len(row) == 8 for row in p["lines"]), "invalid line coordinates")
    require(rows(p["frames"], 672, lambda n: nat(n, 120)), "invalid frames")
    for field in ("start", "final"):
        require(type(p[field]) is list and len(p[field]) == 660 and all(nat(n, 672) for n in p[field]), f"invalid {field}")
    require(type(p["ret"]) is list and len(p["ret"]) == 9 and all(nat(n, 660) and n >= 240 for n in p["ret"]), "invalid retained helpers")
    require(rows(p["scatter"], 120, lambda n: nat(n, 9)), "invalid scatter")
    require(type(p["B"]) is list and len(p["B"]) == 837, "invalid B length")
    for gate in p["B"]:
        require(type(gate) is list and len(gate) == 3 and nat(gate[0], 672) and nat(gate[1], 660) and type(gate[2]) is list and all(nat(n, 660) for n in gate[2]), "invalid B gate")
    for key in ("coords", "form", "format"):
        require(type(p[key]) is str, f"invalid {key}")


def compare_projection(projection, word):
    def equal(a, b, path):
        require(type(a) is type(b), f"type mismatch at {path}")
        if type(a) is list:
            require(len(a) == len(b), f"length mismatch at {path}")
            for i, (x, y) in enumerate(zip(a, b)):
                equal(x, y, f"{path}[{i}]")
        else:
            require(a == b, f"value mismatch at {path}")

    validate_projection(projection)
    require(type(word) is dict, "supplier must be a JSON object")
    for key, value in projection.items():
        require(key in word, f"missing supplier field: {key}")
        equal(value, word[key], key)


def load_word(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise AuditError(f"non-finite JSON constant: {value}")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def audit(root, word_path=None):
    manifest_raw = Path(__file__).with_name("SOURCES.json").read_bytes()
    manifest = load_word(manifest_raw)
    require(manifest.get("format") == "r420-lean-source-binding-v1", "wrong source manifest format")
    pins = manifest.get("files")
    require(type(pins) is dict and set(pins) == EXPECTED_PATHS, "source manifest paths differ")
    require(type(manifest.get("git_blobs_at_base")) is dict and set(manifest["git_blobs_at_base"]) == EXPECTED_PATHS, "source git-blob paths differ")
    texts = {}
    for relative, expected in pins.items():
        raw = (Path(root) / relative).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, f"source hash mismatch: {relative}")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        require(blob == manifest["git_blobs_at_base"][relative], f"source git blob mismatch: {relative}")
        if relative in (CURRENT, BOUNDARY, PHASE):
            texts[relative] = raw.decode("utf-8")
    source_binding = load_word((Path(root) / "research/lean-current-r420-boundary-interfaces/SOURCE_BINDING.json").read_bytes())
    payload_hash = manifest.get("decoded_word_sha256")
    require(source_binding["input"]["decoded_sha256"] == payload_hash and source_binding["input"]["compressed_sha256"] == pins[WORD_PATH], "source context and manifest disagree")
    raw = (Path(word_path) if word_path is not None else Path(root) / WORD_PATH).read_bytes()
    compressed_hash = hashlib.sha256(raw).hexdigest()
    require(len(raw) <= 1024 * 1024, "compressed payload exceeds bound")
    if word_path is None:
        require(compressed_hash == pins[WORD_PATH], "committed gzip hash mismatch")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        decoded = stream.read(1024 * 1024 + 1)
    require(len(decoded) <= 1024 * 1024, "decoded payload exceeds bound")
    require(hashlib.sha256(decoded).hexdigest() == payload_hash, "decoded payload hash mismatch")
    projection = extract_projection(texts[CURRENT], texts[BOUNDARY], texts[PHASE])
    compare_projection(projection, load_word(decoded))
    canonical = json.dumps(projection, sort_keys=True, separators=(",", ":")).encode()
    return {"status": "PASS_R420_LEAN_SOURCE_EXPRESSIONS", "fields": sorted(projection),
            "source_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "source_sha256": pins, "decoded_sha256": payload_hash,
            "committed_compressed_sha256": pins[WORD_PATH], "projection_sha256": hashlib.sha256(canonical).hexdigest(),
            "B_gates": len(projection["B"]), "B_operands": sum(len(g[2]) for g in projection["B"]),
            "frames": len(projection["frames"]), "scatter_terms": sum(map(len, projection["scatter"]))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--word", type=Path, help="Alternate gzip encoding; decoded bytes must match the pinned payload.")
    parser.add_argument("--json", action="store_true", help="Print the deterministic full report.")
    args = parser.parse_args()
    try:
        report = audit(args.root, args.word)
        expected = load_word(Path(__file__).with_name("EXPECTED.json").read_bytes())
        require(report == expected, "report differs from EXPECTED.json")
    except (AuditError, OSError, ValueError, EOFError) as exc:
        print(f"FAIL_R420_LEAN_SOURCE_EXPRESSIONS: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"{report['status']} fields={len(report['fields'])} frames={report['frames']} gates={report['B_gates']} operands={report['B_operands']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
