"""Check exact scalar source spans for the actual line and plane queries."""

from hashlib import sha256
from pathlib import Path
import json


import argparse

ANNEX = Path(__file__).resolve().parents[1]
PARENT = ANNEX.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", required=True)
OUT = Path(parser.parse_args().out).resolve()
OUT.mkdir(parents=True, exist_ok=True)
HERE = ANNEX / "frozen" / 'lanes/schur-selection/plane-repair'
ROOT = HERE.parents[4]
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
PLANE_PIN = "f55bd0e7b81a15b6526ca3056ef3bf1bbf57b13137699e71a374f4cf8f55f794"
ARCHIVE_PIN = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PHASE_PIN = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


def need(value, message):
    if not value:
        raise ValueError(message)


def dot(x,y):
    return (x & y).bit_count() & 1


def main():
    raw = (PARENT / "payload/lanes/circuit-interface/INTERFACE.json").read_bytes()
    need(sha256(raw).hexdigest() == INTERFACE_PIN, "Actual eight centre rows")
    interface = json.loads(raw)
    rows = [[int(row.get(str(p),0)) for p in range(112)] for row in interface["R"]]
    need(len(rows) == 8, "Eight required centre outputs")
    need([[sum(rows[i][p]*rows[j][p] for p in range(112)) for j in range(8)] for i in range(8)]
         == [[56*int(i == j) for j in range(8)] for i in range(8)], "Actual row Gram")
    archive_record = json.loads((ANNEX / "ARCHIVE-CHECK.json").read_bytes())
    need(archive_record["archive_sha256"] == ARCHIVE_PIN, "Historical archive binding")
    phase = (PARENT / "payload/upstream/DATA-PHASES.json").read_bytes()
    need(sha256(phase).hexdigest() == PHASE_PIN, "Actual line labels")
    labels = [r["q"] for r in sorted(json.loads(phase)["recipes"],key=lambda r:r["port"])]
    need(len(labels) == len(set(labels)) == 112 and all(labels), "Distinct nonzero actual line labels")
    line_pivots = []
    for p,q in enumerate(labels):
        i = next(i for i in range(8) if rows[i][p])
        line_pivots.append({"port":p,"q":q,"centre_row":i,"pivot":rows[i][p]})
    need(all(abs(x["pivot"]) == 1 for x in line_pivots), "Explicit nonzero diagonal stacked minor")
    raw_plane = (HERE / "PLANE-INVOLUTION.json").read_bytes()
    need(sha256(raw_plane).hexdigest() == PLANE_PIN, "Frozen actual plane operators")
    planes = json.loads(raw_plane)["planes"]
    plane_pivots = []
    character_checks = 0
    determinant = 1
    for k,plane in enumerate(planes):
        q,r = plane["q"],plane["r"]
        w = q ^ r
        need(w != 0, "A nonzero plane swap direction")
        for j,other in enumerate(planes):
            if other["q"] ^ other["r"] == w:
                numerator = sum((-1) ** dot(q ^ other["q"],y) for y in range(512) if dot(w,y))
                need(numerator == 256*int(k == j), "Exact plane-separating functional")
                character_checks += 256
        p,s = plane["ports"]
        need([labels[p],labels[s]] == [q,r], "Matching uses actual line labels")
        gram = [[sum(rows[i][a]*rows[i][b] for i in range(8)) for b in (p,s)] for a in (p,s)]
        need(gram[0][0]*gram[1][1]-gram[0][1]*gram[1][0] == 12,
             "Each matched pair has two independent scalar input columns")
        i,j,d = next((i,j,rows[i][p]*rows[j][s]-rows[i][s]*rows[j][p])
                     for i in range(8) for j in range(i+1,8)
                     if rows[i][p]*rows[j][s]-rows[i][s]*rows[j][p])
        determinant *= d
        plane_pivots.append({"plane":k,"ports":[p,s],"centre_rows":[i,j],"determinant":d})
        need(sum(not dot(w,y) for y in range(512)) == 256, "Plane trace in the Fourier basis")
    need(determinant != 0, "Explicit nonsingular 112-column plane stacked minor")
    result = {"status":"PASS_EXACT_QUERY_SOURCE_SPANS", "interface_sha256":INTERFACE_PIN,
              "archive_sha256":ARCHIVE_PIN,"phase_sha256":PHASE_PIN,"plane_receipt_sha256":PLANE_PIN,
              "output_fields":8,"input_fields":112,"line_scalar_input_rank":112,
              "line_pivot_functionals":line_pivots,"plane_scalar_input_rank":112,
              "plane_pivot_functionals":plane_pivots,"plane_minor_determinant_in_matching_order":determinant,
              "plane_character_sum_checks":character_checks,
              "plane_endpoint_functional":"normalized trace minus constant-character expectation",
              "plane_endpoint_value_at_tensor_depth_lambda":"2^(-lambda)-1",
              "scope":"Exact scalar input spans for plain-input operator matrices, plus proof-based all-depth extension. This is a payload-query count bound under scalar free gates, not a native-child or rank-zero-map lower bound for the full supplier."}
    (OUT / "QUERY-SPAN.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"])
    print(json.dumps({k:result[k] for k in ("line_scalar_input_rank","plane_scalar_input_rank","plane_minor_determinant_in_matching_order","plane_character_sum_checks")},sort_keys=True))


if __name__ == "__main__":
    main()
