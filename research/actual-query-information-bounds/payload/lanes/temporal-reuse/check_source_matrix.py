"""Rebuild the source matrix with the reviewed reverse propagation."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parent

ARCHIVE_PIN = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"

INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"

MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": (
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
        "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"),
    "slots/local/LOCAL-PROGRAMS.json.gz": (
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
        "9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3"),
}

A = [0, 7, 20, 27, 36, 46, 57, 111]

T = [21, 37, 47, 76, 81, 87, 92, 110]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def pinned(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, "Changed input: " + str(path))
    return raw

def source_matrix():
    inputs = {}
    for name, (compressed_pin, payload_pin) in MEMBERS.items():
        compressed = (LANES.parent / "upstream" / name.rsplit("/", 1)[-1]).read_bytes()
        need(sha256(compressed).hexdigest() == compressed_pin, "Member pin differs")
        payload = gzip.decompress(compressed)
        need(sha256(payload).hexdigest() == payload_pin, "Payload pin differs")
        inputs[name.rsplit("/", 1)[-1]] = json.loads(payload)
    word = inputs["CANONICAL-WORD.json.gz"]
    events = inputs["LOCAL-PROGRAMS.json.gz"]["forward"]
    cut = events.index(["phase", "centers"])
    gradient = [{} for _ in range(712)]
    for k, center in enumerate(word["centers"]):
        gradient[center][k] = Q(1)

    def register(token):
        need(token[0] in ("L", "C"), "Unknown field namespace")
        value = token[1] + 704 * (token[0] == "C")
        need(0 <= value < 712, "Invalid field")
        return value

    for event in reversed(events[:cut]):
        if event[0] != "scalar":
            continue
        op = event[1]
        target = register(op[1])
        if op[0] == "clear":
            gradient[target] = {}
        elif op[0] == "scale":
            scale = Q(op[2], op[3])
            gradient[target] = {k: x * scale for k, x in gradient[target].items()}
        else:
            need(op[0] in ("add", "copy"), "Unknown scalar operation")
            source = register(op[2])
            need(source != target, "Unexpected aliased scalar operation")
            scale = Q(1) if op[0] == "copy" else Q(op[3], op[4])
            for k, x in gradient[target].items():
                gradient[source][k] = gradient[source].get(k, 0) + scale*x
            if op[0] == "copy":
                gradient[target] = {}
    R = [[gradient[p].get(k, Q(0)) for p in range(112)] for k in range(8)]
    interface = json.loads(pinned(LANES / "circuit-interface/INTERFACE.json", INTERFACE_PIN))
    need(R == [[Q(row.get(str(p), 0)) for p in range(112)] for row in interface["R"]],
         "Reverse source reconstruction differs from R")
    need(all(x.denominator == 1 for row in R for x in row), "R is not integral")
    R = [[int(x) for x in row] for row in R]
    gram = lambda ports: [[sum(R[i][p]*R[j][p] for p in ports)
                           for j in range(8)] for i in range(8)]
    need(gram(range(112)) == [[56*(i == j) for j in range(8)] for i in range(8)],
         "Full source Gram differs")
    need(not set(A) & set(T), "Fixed minors overlap")
    for ports in (A, T):
        need(gram(ports) == [[4*(i == j) for j in range(8)] for i in range(8)],
             "A fixed minor differs")
    columns = list(zip(*R))
    need(all(sum(x*x for x in col) == 4 for col in columns), "A root norm differs")
    dots = Counter(sum(x*y for x, y in zip(columns[i], columns[j]))
                   for i in range(112) for j in range(i))
    need(dots == {0: 3304, 2: 1960, -2: 952}, "Root products differ")
    return {"archive_sha256": ARCHIVE_PIN, "members": MEMBERS,
            "reverse_output_forms": 8, "source_columns": 112, "source_cut": cut,
            "pair_products": dict(sorted(dots.items())), "full_gram": "56 I8",
            "fixed_minor_grams": "4 I8"}

if __name__ == "__main__":
    result = source_matrix()
    result["status"] = "PASS_REVERSE_SOURCE_MATRIX_BINDING"
    (HERE / "SOURCE-MATRIX-BINDING.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
