#!/usr/bin/env python3
"""Fixed-F4 first-slice backend port with complete raw matrix evidence.

Ali Romman's Field is the sole executed predecessor dependency. The old
ToikY6543 algorithm and Petalas6451 threshold retain credit. Apache-2.0.
Substantial OpenAI Codex assistance.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parent
PIN = "4ddc2862bf5e8f3a718ec60a9b2c8ed12b97bda679a719c5b4f5db0bd77b15b9"
INPUTS_PIN = "ce46d3e6f89e261e4cb9e4f5260e27c9ab498b619b4bd812f4b00b0d50ad4db8"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_load(raw):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def bad(value):
        raise ValueError("nonfinite JSON " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticate(root=ROOT):
    raw = (root / "SOURCE-PINS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN, "source manifest")
    data = strict_load(raw)
    need(data["schema_version"] == 1 and len(data["files"]) == 6, "source schema")
    bodies = {}
    for item in data["files"]:
        path = root / item["local_path"]
        need(not path.is_symlink(), "source symlink")
        body = path.read_bytes()
        need(len(body) == item["bytes"], "source length")
        need(hashlib.sha256(body).hexdigest() == item["sha256"], "source digest")
        blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body)
        need(blob.hexdigest() == item["git_blob"], "source git blob")
        bodies[path.name] = body
    return bodies


def frozen_inputs():
    raw = (ROOT / "PENCILS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == INPUTS_PIN, "frozen pencils")
    data = strict_load(raw)
    need(data["schema_version"] == 1 and len(data["fixtures"]) == 10, "pencil schema")
    return data["fixtures"]


def load_module(name, body, file):
    module = types.ModuleType(name)
    module.__dict__["__file__"] = str(file)
    exec(compile(body, str(file), "exec"), module.__dict__)
    return module


def setup():
    bodies = authenticate()
    inputs = frozen_inputs()
    backend = load_module("credited_field_5664", bodies["5664-field.py"], ROOT / "inputs/5664-field.py")
    f = backend.Field(2, (1, 1, 1))
    body = (ROOT / "constructor.py").read_bytes()
    constructor = load_module("new_f4_constructor", body, ROOT / "constructor.py")
    constructor.backend_check(f)
    return f, constructor, inputs


def encode(row):
    return (json.dumps(row, separators=(",", ":")) + "\n").encode()


def backend_gate(f, c):
    for a in range(4):
        need(f.add[a][0] == a and f.mul[a][1] == a, "field identity")
        if a:
            need(f.mul[a][f.inv[a]] == 1, "field inverse")
        for b in range(4):
            for d in range(4):
                need(f.add[f.add[a][b]][d] == f.add[a][f.add[b][d]], "field additive associativity")
                need(f.mul[a][f.add[b][d]] == f.add[f.mul[a][b]][f.mul[a][d]], "field distributivity")
    a, b = [[0, 0], [0, 0]], [[2, 0], [0, 3]]
    answer = c.construct(a, b, f)
    need(answer["e"] == 1 and answer["alpha"] == [0], "actual nonprime base slice")
    need(answer["slice"] == [[[2], [0]], [[0], [3]]] and
         answer["inverse"] == [[[3], [0]], [[0], [2]]], "actual nonprime inverse")
    return {"A": a, "B": b, "answer": answer,
            "z_squared": f.mul[2][2], "z_times_z_plus_one": f.mul[2][3]}


def matrix_from_code(code):
    entries = []
    for _ in range(4):
        entries.append(code % 4)
        code //= 4
    need(code == 0, "matrix code overflow")
    return [entries[:2], entries[2:]]


def base_matrix(matrix):
    need(all(len(x) == 1 for row in matrix for x in row), "base matrix projection")
    return [[x[0] for x in row] for row in matrix]


def census(f, c, stream=None):
    hasher, counts, points, size = hashlib.sha256(), {"regular": 0, "singular": 0}, {}, 0
    for acode in range(256):
        a = matrix_from_code(acode)
        for bcode in range(256):
            b = matrix_from_code(bcode)
            polynomial = c.bareiss(a, b, f, c.trace_new())
            try:
                answer = c.construct(a, b, f)
            except ValueError as exc:
                need(str(exc) == "nonregular pencil", "unexpected census failure: " + str(exc))
                need(polynomial == (0,), "singular polynomial")
                row = [acode, bcode, list(polynomial), "singular", None, None, None, None]
                counts["singular"] += 1
            else:
                need(answer["e"] == 1, "2x2 first degree")
                point = "infinity" if answer["infinity"] else "affine"
                alpha = None if answer["infinity"] else answer["alpha"][0]
                row = [acode, bcode, list(polynomial), "regular", point, alpha,
                       base_matrix(answer["slice"]), base_matrix(answer["inverse"])]
                counts["regular"] += 1
                points[point] = points.get(point, 0) + 1
            raw = encode(row)
            hasher.update(raw)
            size += len(raw)
            if stream is not None:
                stream.write(raw)
    return {"cases": 65536, "regular": counts["regular"], "singular": counts["singular"],
            "stream_sha256": hasher.hexdigest(), "stream_bytes": size,
            "point_kind_counts": dict(sorted(points.items()))}


def named(f, c, inputs):
    out = []
    for item in inputs:
        a, b = item["A"], item["B"]
        try:
            answer = c.construct(a, b, f)
        except ValueError as exc:
            need(str(exc) == "nonregular pencil" and item["expected_degree"] is None,
                 "unexpected named rejection: " + str(exc))
            answer, status = None, "singular"
        else:
            need(answer["e"] == item["expected_degree"], "named first degree")
            status = "regular"
        out.append({"name": item["name"], "A": a, "B": b, "status": status, "answer": answer})
    return out


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return True
    raise ValueError("negative control accepted")


def require_base_fixed(exponent, h, f, c):
    need(all(c.modpow((a,), exponent, h, f) == (a,) for a in range(4)),
         "Frobenius not base linear")


def controls(f, c, fixtures):
    by_name = {item["name"]: item for item in fixtures}
    good = by_name["first-degree-2"]
    out = {}
    for name, key in (("wrong_inverse", "inverse"), ("wrong_literal_slice", "slice")):
        answer = copy.deepcopy(good["answer"])
        answer[key][0][0] = [1] if answer[key][0][0] == [0] else [0]
        out[name] = rejects(c.validate_answer, good["A"], good["B"], answer, f)
    answer = copy.deepcopy(good["answer"])
    answer["field_modulus"] = [0, 0, 1]
    out["reducible_modulus"] = rejects(c.validate_answer, good["A"], good["B"], answer, f)
    answer = copy.deepcopy(good["answer"])
    answer["alpha"] = [4]
    out["noncanonical_embedding"] = rejects(c.validate_answer, good["A"], good["B"], answer, f)
    bad = copy.deepcopy(f)
    bad.mul = [[(a*b) % 4 for b in range(4)] for a in range(4)]
    out["z4_backend_rejected"] = rejects(c.construct, [[0]], [[2]], bad)
    require_base_fixed(4, tuple(good["answer"]["field_modulus"]), f, c)
    out["p_frobenius_not_base_linear"] = rejects(require_base_fixed, 2,
        tuple(good["answer"]["field_modulus"]), f, c)
    out["boolean_entry"] = rejects(c.construct, [[True]], [[0]], f)
    out["out_of_range_entry"] = rejects(c.construct, [[4]], [[0]], f)
    out["nonregular"] = rejects(c.construct, [[0]], [[0]], f)
    out["nonsquare"] = rejects(c.construct, [[0, 1]], [[0]], f)
    out["duplicate_json"] = rejects(strict_load, '{"x":1,"x":2}')
    out["nonfinite_json"] = rejects(strict_load, '{"x":NaN}')
    need(by_name["polynomial-row-pivot"]["answer"]["trace"]["polynomial_row_swaps"] > 0,
         "unexercised polynomial pivot")
    out["actual_polynomial_row_pivot"] = True
    return out


def source_control():
    with tempfile.TemporaryDirectory(prefix="f4-source-control-") as name:
        root = Path(name)
        raw = (ROOT / "SOURCE-PINS.json").read_bytes()
        (root / "SOURCE-PINS.json").write_bytes(raw)
        manifest = strict_load(raw)
        for item in manifest["files"]:
            path = root / item["local_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / item["local_path"]).read_bytes())
        path = root / manifest["files"][0]["local_path"]
        body = bytearray(path.read_bytes())
        body[0] ^= 1
        path.write_bytes(body)
        return rejects(authenticate, root)


def receipt(first_small=False, stream=None):
    f, c, inputs = setup()
    gate = backend_gate(f, c)
    if first_small:
        selected = [item for item in inputs if item["name"] == "first-degree-2"]
        return {"schema_version": 1, "source_manifest_sha256": PIN,
                "inputs_sha256": INPUTS_PIN, "backend_gate": gate,
                "fixtures": named(f, c, selected), "scope": "first-small"}
    counted = census(f, c, stream)
    fixtures = named(f, c, inputs)
    checks = controls(f, c, fixtures)
    checks["actual_backend_source_corruption"] = source_control()
    return {"schema_version": 1, "source_manifest_sha256": PIN,
            "inputs_sha256": INPUTS_PIN, "backend_gate": gate, "census": counted,
            "fixtures": fixtures, "controls": checks,
            "code_sha256": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                            for name in ("constructor.py", "verify.py")}}


def same_type_tree(actual, expected):
    need(type(actual) is type(expected), "receipt value type")
    if type(expected) is dict:
        need(actual.keys() == expected.keys(), "receipt keys")
        for key in expected:
            same_type_tree(actual[key], expected[key])
    elif type(expected) is list:
        need(len(actual) == len(expected), "receipt list length")
        for a, b in zip(actual, expected):
            same_type_tree(a, b)
    else:
        need(actual == expected, "receipt value")


def stream_path(args):
    if len(args) == 3 and args[0:2] == ["--emit", "--stream-file"]:
        path = Path(args[2])
        need(path.is_absolute(), "absolute external stream path")
        need(ROOT not in path.resolve().parents and path.resolve() != ROOT, "external stream path")
        need(not path.exists() and not path.is_symlink(), "new stream file")
        return path
    return None


def main():
    args = sys.argv[1:]
    path = stream_path(args)
    need(args in ([], ["--emit"], ["--first-small"]) or path is not None, "unsupported arguments")
    if path is not None:
        with path.open("xb") as output:
            result = receipt(stream=output)
    else:
        result = receipt(args == ["--first-small"])
    if args:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        same_type_tree(strict_load((ROOT/"RESULT.json").read_bytes()), result)
        print("PASS_F4_FIRST_SLICE_CONSTRUCTOR")


if __name__ == "__main__":
    main()
