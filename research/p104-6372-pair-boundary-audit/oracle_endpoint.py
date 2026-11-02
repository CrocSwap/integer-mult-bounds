"""Independent full public scalar endpoint via reverse coordinate functionals.

Literal MOVE is identity in this projection. INIT supplies an owned zero;
COPY overwrites; CLEAR removes a coordinate without assuming its value was
zero. Source, author, local-audit and peer modules are never imported.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED = 770, 29
PINS = {
    "sources/INPUT-WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "sources/OUTPUT-WORD.json.gz": ("e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491", "0af79e58172f85c302c35b193205c0b185b09393"),
    "sources/BASIS.json": ("28d01a60c1780dc61373a13ac70654c140fa20519abdac0dd78f24c8343a002f", "efa2be3e34cab2d15ceaf33ff43eab70ff4c12e6"),
    "sources/constructor-source.py": ("e18f0221827628e38674dc71198a95ccebc401476328e3db7569b84e4b7be969", "d92f1f92e705eafdda770ec19b958084584420a8"),
    "sources/upstream-PROOF.md": ("4d02ec61147085ed88c11340b369729c943b954a0cc41a9995ffc07d24f1a285", "3a670ce4c0ae727b4d3cd3604d67d45b189da3c7"),
    "sources/NOTICE": ("f13f42a39d4614b26d9871f5bc8fcb76e60cb44b4df8762cd51e505b43723e46", "9af7effd3a0ff5218d94331567022fd179a1e8fa"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def rational(value):
    require(type(value) is str, "Rational coefficient string")
    result = F(value)
    require(str(result) == value and result != 0, "Canonical nonzero rational coefficient")
    require(result.denominator & (result.denominator - 1) == 0, "Dyadic coefficient")
    return result


def authenticate():
    manifest = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    require(type(manifest) is list and len(manifest) == len(PINS), "Six frozen input files")
    require({r["file"]: (r["sha256"], r["git_blob"]) for r in manifest} == PINS,
            "Independent hardcoded source pins")
    data = {}
    for name, (digest, blob) in PINS.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, "Exact source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Exact source Git blob: " + name)
        if name.endswith(".json.gz"):
            data[Path(name).name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            data[Path(name).name] = json.loads(raw)
    return data


def compile_word(word):
    require(type(word) is dict and type(word["public"]) is int and word["public"] == PUBLIC
            and type(word["owned_fields"]) is int and word["owned_fields"] == OWNED,
            "770 public inputs and29 owned labels")
    require(type(word["frames"]) is list, "Frame-label inventory")
    frames = len(word["frames"])
    for key in ("initial", "final"):
        require(type(word[key]) is list and len(word[key]) == PUBLIC, "Complete public frame boundary")
        for frame in word[key]:
            integer(frame, 0, frames, "Public frame label")
    require(type(word["live"]) is list and len(word["live"]) == 104, "104 live main pairs")
    for role in word["live"]:
        integer(role, 0, PUBLIC - 112, "Main role")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    require(len(main) == 208, "Distinct main pair roles")
    require(type(word["program"]) is list and len(word["program"]) < 26000, "Bounded complete program")
    current = dict(enumerate(word["initial"]))
    open_lifetimes, lifetimes, tape, copies = {}, [], [], []
    peak, serial = 0, 0
    for index, event in enumerate(word["program"]):
        require(type(event) is list and event, "Literal event list")
        op = event[0]
        require(op in ("MOVE", "INIT", "CLEAR", "ADD", "COPY", "SCALE"), "Known literal opcode")
        require(len(event) == {"MOVE": 5, "INIT": 3, "CLEAR": 3,
                               "ADD": 5, "COPY": 5, "SCALE": 4}[op], "Literal opcode arity")
        r = integer(event[1], 0, PUBLIC + OWNED, "Literal role")
        if op == "INIT":
            frame = integer(event[2], 0, frames, "INIT frame")
            require(r >= PUBLIC and r not in current, "INIT starts inactive owned storage")
            current[r] = frame
            open_lifetimes[r] = (index, serial)
            serial += 1
            peak = max(peak, len(open_lifetimes))
            tape.append((op, r))
        elif op == "CLEAR":
            frame = integer(event[2], 0, frames, "CLEAR frame")
            require(r >= PUBLIC and current.get(r) == frame and r in open_lifetimes,
                    "CLEAR ends an active lifetime in its declared frame")
            start, ordinal = open_lifetimes.pop(r)
            lifetimes.append({"ordinal": ordinal, "role": r, "init_index": start,
                              "clear_index": index, "clear_frame": frame})
            del current[r]
            tape.append((op, r))
        elif op == "MOVE":
            start = integer(event[2], 0, frames, "MOVE source label")
            end = integer(event[3], 0, frames, "MOVE target label")
            require(r in current and current[r] == start and type(event[4]) is bool
                    and event[4] == (r >= PUBLIC), "MOVE chronology and ownership")
            current[r] = end
            tape.append((op, r))
        else:
            frame = integer(event[-1], 0, frames, "Scalar frame label")
            require(r in current and current[r] == frame, "Active scalar destination and common frame")
            coefficient = rational(event[-2])
            if op == "SCALE":
                tape.append((op, r, coefficient))
            else:
                s = integer(event[2], 0, PUBLIC + OWNED, "Scalar source role")
                require(s != r and s in current and current[s] == frame,
                        "Active distinct scalar source in the common frame")
                if op == "COPY":
                    require(r >= PUBLIC, "COPY has owned destination")
                    copies.append((index, r))
                tape.append((op, r, s, coefficient))
    require(not open_lifetimes and current == dict(enumerate(word["final"])),
            "All owned lifetimes end and all final public labels agree")
    return tape, sorted(lifetimes, key=lambda r: r["clear_index"]), peak, copies


def bump(weights, role, value):
    result = weights.get(role, F(0)) + value
    if result:
        weights[role] = result
    else:
        weights.pop(role, None)


def pullback(tape, output, end=None):
    """Pull a real rational coordinate functional through literal chronology."""
    weights = {output: F(1)}
    stop = len(tape) if end is None else end
    for index in range(stop - 1, -1, -1):
        event = tape[index]
        op, target = event[:2]
        value = weights.get(target)
        if op == "CLEAR":
            require(value is None, "No functional coefficient on an inactive post-CLEAR coordinate")
        elif op == "INIT":
            weights.pop(target, None)
        elif op in ("ADD", "COPY"):
            if value is not None:
                if op == "COPY":
                    weights.pop(target, None)
                bump(weights, event[2], event[3] * value)
        elif op == "SCALE" and value is not None:
            weights[target] = event[2] * value
        # MOVE retains the formal scalar value.
    require(all(type(r) is int and 0 <= r < PUBLIC for r in weights),
            "All surviving coefficients belong to original public inputs")
    return weights


def encoded(row):
    return [[r, str(q)] for r, q in sorted(row.items())]


def row_hash(row):
    return sha256((canonical(encoded(row)) + "\n").encode()).hexdigest()


def difference(actual, expected, output):
    for r in sorted(actual.keys() | expected.keys()):
        if actual.get(r, 0) != expected.get(r, 0):
            return {"output": output, "input": r, "actual": str(actual.get(r, 0)),
                    "expected": str(expected.get(r, 0))}
    return None


def clear_functionals(tape, lifetimes):
    records = []
    for lifetime in lifetimes:
        row = pullback(tape, lifetime["role"], lifetime["clear_index"])
        records.append({**lifetime, "public_support": len(row), "zero_functional": not row,
                        "row_sha256": row_hash(row), "row": encoded(row)})
    return records


def controls(candidate, source_rows, basis):
    controls = []
    # These are actual scalar instructions in the complete forward word.
    choices = [("omit_first_output_correction", 0, "omit"),
               ("wrong_first_output_correction_sign", 0, "sign"),
               ("omit_output_basis_instruction", basis["control_indices"]["output_basis"], "omit"),
               ("omit_response_instruction", basis["control_indices"]["response"], "omit")]
    for label, index, action in choices:
        changed = deepcopy(candidate)
        original = deepcopy(changed["program"][index])
        require(original[0] in ("ADD", "SCALE"), "Full-word scalar mutation site")
        if action == "omit":
            changed["program"].pop(index)
            replacement = None
        else:
            changed["program"][index][-2] = str(-rational(original[-2]))
            replacement = changed["program"][index]
        tape, _, _, _ = compile_word(changed)
        witness = None
        probes = tuple(dict.fromkeys((224, 227, 169, 193, 204) + tuple(range(PUBLIC))))
        for output in probes:
            witness = difference(pullback(tape, output), source_rows[output], output)
            if witness is not None:
                break
        require(witness is not None, "Full-word fault must change an actual public endpoint coefficient: " + label)
        controls.append({"control": label, "event_index": index, "original_event": original,
                         "replacement_event": replacement, "literal_frames_and_lifetimes_valid": True,
                         "public_coefficient_witness": witness})
    return controls


def run():
    data = authenticate()
    source, candidate = data["INPUT-WORD.json.gz"], data["OUTPUT-WORD.json.gz"]
    require(set(source) == set(candidate), "Same source/candidate metadata keys")
    for key in source:
        if key not in ("program", "final"):
            require(canonical(source[key]) == canonical(candidate[key]), "Unchanged source metadata: " + key)
    changed_frames = {str(r): [source["final"][r], candidate["final"][r]]
                      for r in range(PUBLIC) if source["final"][r] != candidate["final"][r]}
    require(changed_frames == {"224": [127, 245], "227": [127, 245]},
            "Only the two intentional helper final labels change")
    left, source_lifetimes, source_peak, source_copies = compile_word(source)
    right, candidate_lifetimes, candidate_peak, candidate_copies = compile_word(candidate)
    for tape, copies in ((left, source_copies), (right, candidate_copies)):
        for index, role in copies:
            require(not pullback(tape, role, index), "Actual COPY destination is zero before overwrite")
    source_rows, candidate_rows = [], []
    mains = set(source["live"])
    for output in range(PUBLIC):
        old, new = pullback(left, output), pullback(right, output)
        require(difference(new, old, output) is None,
                "Candidate/source public endpoint coefficients differ at output" + str(output))
        expected = {output: F(1)}
        if output - 112 in mains:
            expected[output - 112] = F(1)
        require(old == expected and new == expected, "Required arbitrary-input identity and main shear")
        source_rows.append(old)
        candidate_rows.append(new)
    source_clear_rows = clear_functionals(left, source_lifetimes)
    candidate_clear_rows = clear_functionals(right, candidate_lifetimes)
    tail = candidate["program"][-2:]
    require(tail == [["CLEAR", 780, 127], ["CLEAR", 779, 127]], "Actual added forward tail CLEAR bindings")
    added = [r for r in candidate_clear_rows if r["clear_index"] >= len(right) - 2]
    require([r["role"] for r in added] == [780, 779], "Added forward lifetimes identified by chronological CLEARs")
    matrix_sha = sha256((canonical([encoded(row) for row in candidate_rows]) + "\n").encode()).hexdigest()
    return {"schema_version": 1, "status": "PASS_SCALAR_ENDPOINT_ONLY",
            "method": "independent reverse coordinate functionals on the complete literal words",
            "public_outputs": PUBLIC, "independent_public_inputs": PUBLIC,
            "coefficient_positions_compared": PUBLIC * PUBLIC,
            "nonzero_public_coefficients": sum(map(len, candidate_rows)), "matrix_sha256": matrix_sha,
            "changed_helper_final_labels": changed_frames,
            "source": {"events": len(left), "owned_lifetimes": len(source_lifetimes), "peak_owned": source_peak,
                       "COPY_zero_destination_checks": len(source_copies),
                       "nonzero_forward_CLEAR_rows": sum(not r["zero_functional"] for r in source_clear_rows),
                       "forward_CLEAR_functionals": source_clear_rows},
            "candidate": {"events": len(right), "owned_lifetimes": len(candidate_lifetimes), "peak_owned": candidate_peak,
                          "COPY_zero_destination_checks": len(candidate_copies),
                          "nonzero_forward_CLEAR_rows": sum(not r["zero_functional"] for r in candidate_clear_rows),
                          "forward_CLEAR_functionals": candidate_clear_rows},
            "added_forward_tail_lifetimes": added,
            "semantic_full_word_controls": controls(candidate, source_rows, data["BASIS.json"]),
            "limits": ["770 public inputs are arbitrary; owned fields are zero at INIT and have no independent initial input.",
                       "Forward CLEAR removes a live coordinate even when its scalar functional is nonzero; no erasure permission is inferred.",
                       "Equal scalar matrices do not equate the native helper operators: the two final native labels intentionally differ.",
                       "MOVE is identity only in this scalar projection; native phase, all-width realization, physical caller, price and kappa are not admitted."]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: oracle_endpoint.py [--emit]")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    else:
        retained = json.loads((HERE / "ENDPOINT-ORACLE.json").read_bytes())
        require(canonical(result) == canonical(retained), "Exact typed retained ENDPOINT-ORACLE.json receipt")
        print("PASS complete reverse public endpoint and retained receipt")
