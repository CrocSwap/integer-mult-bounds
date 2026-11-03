"""Factor the actual PR6621 opening preparation, restoring owned slot 770.

Produced by Nick Petalas. Apache-2.0. The source expression and word are
DreamingOfClouds's PR6621, with the lineage retained in inputs/NOTICE.
"""
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
TARGETS = (119, 169, 191, 193, 204, 206)
SOURCES = ((471, "1"), (525, "1/2"), (704, "2"))
TEMPORARY = 770
FRAME = 3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def old_prefix():
    return [["ADD", target, source, coefficient, FRAME]
            for target in TARGETS for source, coefficient in SOURCES]


def new_prefix():
    compute = [["ADD", TEMPORARY, source, coefficient, FRAME]
               for source, coefficient in SOURCES]
    fanout = [["ADD", target, TEMPORARY, "1", FRAME] for target in TARGETS]
    uncompute = [["ADD", TEMPORARY, source, str(-Fraction(coefficient)), FRAME]
                 for source, coefficient in reversed(SOURCES)]
    return [["INIT", TEMPORARY, FRAME]] + compute + fanout + uncompute + [
        ["CLEAR", TEMPORARY, FRAME]]


def read_source():
    pins = json.loads((HERE / "NATIVE-SOURCE.json").read_bytes())
    require(pins["head"] == "c51a142bb94c6d46ebee9a48c3f71cde8022da91",
            "Exact construction source head")
    require(len(pins["files"]) == 2, "Two retained source members")
    for pin in pins["files"]:
        require(pin["path"] in ("inputs/WORD.json.gz", "inputs/NOTICE"),
                "Fixed retained member path")
        raw = (HERE / pin["path"]).read_bytes()
        require(len(raw) == pin["bytes"] <= 200000, "Retained member size")
        require(sha256(raw).hexdigest() == pin["sha256"], "Source SHA256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(sha1(blob).hexdigest() == pin["git_blob"], "Source Git blob")
    return json.loads(gzip.decompress((HERE / "inputs/WORD.json.gz").read_bytes()))


def construct(word):
    require(word["public"] == 770 and word["owned_fields"] == 29,
            "Declared source role ranges")
    require(word["frames"][FRAME] == [], "Empty native frame")
    require(word["program"][:18] == old_prefix(), "Exact opening preparation")
    require(18 <= len(word["program"]) <= 20000, "Bounded source program")
    for role in TARGETS + tuple(source for source, _ in SOURCES):
        require(word["initial"][role] == FRAME, "All public operands start in frame 3")
    uses = [(i, event) for i, event in enumerate(word["program"])
            if event[1] == TEMPORARY or
            (event[0] in ("ADD", "COPY") and event[2] == TEMPORARY)]
    require(uses[0] == (8448, ["INIT", TEMPORARY, 737]),
            "Slot 770 is inactive before its first source lifetime")
    result = dict(word)
    result["program"] = new_prefix() + word["program"][18:]
    return result


def evaluate(program, initial):
    """Exact local semantics; INIT/CLEAR require an inactive/zero owned slot."""
    require(len(program) <= 18 and len(initial) == 9, "Bounded local domain")
    values = dict(initial)
    temporary = None
    peak_temporary = Fraction(0)
    peak_public = max(abs(value) for value in initial.values())
    for event in program:
        op, target = event[:2]
        require(event[-1] == FRAME, "Local frame")
        if op == "INIT":
            require(target == TEMPORARY and temporary is None, "Inactive owned INIT")
            temporary = Fraction(0)
        elif op == "CLEAR":
            require(target == TEMPORARY and temporary == 0, "Zero owned CLEAR")
            temporary = None
        else:
            require(op == "ADD" and target != event[2], "Legal distinct-role ADD")
            source = event[2]
            value = temporary if source == TEMPORARY else values[source]
            require(value is not None, "Live ADD source")
            delta = Fraction(event[3]) * value
            if target == TEMPORARY:
                require(temporary is not None, "Live ADD target")
                temporary += delta
                peak_temporary = max(peak_temporary, abs(temporary))
            else:
                values[target] += delta
                peak_public = max(peak_public, abs(values[target]))
    require(temporary is None, "Owned slot inactive at exit")
    return values, peak_temporary, peak_public


def encoded(word):
    raw = (json.dumps(word, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return gzip.compress(raw, mtime=0)


def main():
    require(len(sys.argv) == 2, "Usage: rewrite.py /external/path/WORD.json.gz")
    destination = Path(sys.argv[1]).resolve()
    require(not destination.is_relative_to(HERE.parents[1]),
            "Emit generated words outside the checkout")
    require(not destination.exists(), "Refuse to overwrite an existing output")
    payload = encoded(construct(read_source()))
    with destination.open("xb") as output:
        require(output.write(payload) == len(payload), "Complete word output")
    print(json.dumps({"path": str(destination), "sha256": sha256(payload).hexdigest()}))


if __name__ == "__main__":
    main()
