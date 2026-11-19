"""Check all spectral blocks for five qubits at widths 13, 14 and 15.
apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = "d7a8465e81f7e20cb87f6bc7b0d7fb7a059e88691fd06df2ec502ee65be62f54"
ORDER = 24815256521932800
NUM_COLUMNS = 1024 * ORDER


def require(condition, message):
    if not condition:
        raise ValueError(message)


def block_spectrum(group, t, width, orbit):
    order = group["order"]
    degrees = []
    records = []
    for i, (degree, *sums) in enumerate(group["rows"], start=1):
        require(len(sums) == 11 and sums[-1] == degree, "identity fixed space")
        require(sum(sums) == (order if i == 1 else 0), "row orthogonality to trivial")
        inner = sum(c * t**d for d, c in enumerate(sums))
        multiplicity, remainder = divmod(inner, order)
        require(remainder == 0 and multiplicity >= 0, "integral nonnegative multiplicity")
        dim = degree * orbit
        eigen = Fraction(NUM_COLUMNS * multiplicity, 32**width * dim)
        degrees.append(degree)
        records.append((i, degree, dim, multiplicity, eigen))
    require(sum(d*d for d in degrees) == order, "degree census")
    return records


def census(records, width):
    require(sum(d*d for _,_,d,_,_ in records) == NUM_COLUMNS, "all projective blocks")
    require(sum(d*m for _,_,d,m,_ in records) == 32**width, "full natural tensor dimension")
    require(sum(d*d*v for _,_,d,_,v in records) == NUM_COLUMNS, "normalized Gram trace")
    missing = [(i, degree) for i,degree,_,m,_ in records if m == 0]
    nullity = sum(d*d for _,_,d,m,_ in records if m == 0)
    return missing, nullity


def main():
    data = (ROOT / "PROJECTION.json").read_bytes()
    require(sha256(data).hexdigest() == SOURCE, "projection bytes")
    tables = json.loads(data)
    g = tables["S10(2)"]
    require(g["order"] == ORDER and len(g["rows"]) == 198, "Sp10")
    r13 = block_spectrum(g, -64, 13, 32)
    missing, nullity = census(r13, 13)
    require(missing == [(10,11935), (26,81158), (31,202895), (38,365211),
                        (41,405790), (73,1623160), (77,1826055)] and
            nullity == 6466626860503040, "width 13 missing blocks")
    results = []
    for name, orbit, count, index, degree in (("O10+(2).2",528,155,9,868),
                                               ("O10-(2).2",496,164,16,5236)):
        table = tables[name]
        require(table["order"] * orbit == ORDER and len(table["rows"]) == count,
                "Bell orbit and stabilizer order")
        group_rows = block_spectrum(table, -64, 14, orbit)
        require([(j,d) for j,d,_,m,_ in group_rows if m == 0] == [(index,degree)],
                "Bell missing row")
        # Dropping the phase in the trace would give positive multiplicity
        # for this missing block, invalidating the rank result.
        y = table["rows"][index-1][1:]
        require(sum(c * 64**d for d,c in enumerate(y)) > 0, "phase control")
        results.extend(group_rows)
    _, null14 = census(results, 14)
    require(null14 == 6954742423552, "width 14 exact nullity")
    r15 = block_spectrum(g, 128, 15, 32)
    require(census(r15, 15) == ([],0), "width 15 full rank")
    vals = [v for _,_,_,_,v in r15]
    lower = Fraction(394477183485, 2**43)
    upper = Fraction(7279231852517625, 2**45)
    require(min(vals) == lower and max(vals) == upper, "threshold endpoints")
    print(f"PASS f13 missing=7 nullity={nullity}")
    print(f"PASS f14 missing=2 nullity={null14} rank={NUM_COLUMNS-null14}")
    print(f"PASS f15 rank={NUM_COLUMNS} endpoints=[{lower},{upper}] T(5)=15")


if __name__ == "__main__":
    main()
