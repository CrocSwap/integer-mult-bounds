"""Reconstruct all P5 spectral polynomials by the affine radical recursion."""
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECTION_PIN = "d7a8465e81f7e20cb87f6bc7b0d7fb7a059e88691fd06df2ec502ee65be62f54"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def as_counter(rows):
    return Counter({tuple(p): n for p,n in rows})


def lift(m, p, orbit):
    c = 2**(2*m-2)
    require(all((c*v) % (2**i) == 0 for i,v in enumerate(p)), "scaling")
    scaled = [c*v//2**i for i,v in enumerate(p)]
    prefactor = (0,-1,1) if orbit.startswith("O") else (-2,1,1)
    out = [0]*(2*m+1)
    for i,v in enumerate(scaled):
        for j,w in enumerate(prefactor):
            out[i+j] += v*w
    if orbit == "Sp":
        for i,v in enumerate(p):
            out[i] += 2*c*v
    require(out[-1] == 1, "leading coefficient")
    return tuple(out)


def main():
    data = json.loads((ROOT / "CORNERS.json").read_text())
    projection = (ROOT / "sources/five-qubit-projection.json").read_bytes()
    require(sha256(projection).hexdigest() == PROJECTION_PIN, "source pin")
    for name, key in [("Sp10","S10(2)"),("O10+","O10+(2).2"),("O10-","O10-(2).2")]:
        rows = json.loads(projection)[key]["rows"]
        prior = Counter(tuple(v//degree for v in p) for degree,*p in rows)
        native = data["corners"][name]
        require(prior == as_counter(zip(native["polys"],native["counts"],strict=True)), "prior census")
    current = Counter({(0,-1,1):1, (0,1,1):1})
    for m, family in enumerate(data["lower"], 2):
        sources = {name: as_counter(rows) for name,rows in family.items()}
        sources["P"] = current
        current = Counter()
        for orbit, census in sources.items():
            for p,n in census.items():
                current[lift(m,p,orbit)] += n
        print(f"P{m}: {sum(current.values())} ordinary irreducibles, {len(current)} distinct polynomials")
    native = data["corners"]["P5"]
    require(current == as_counter(zip(native["polys"],native["counts"],strict=True)),
            "rank-five stabilizer recursion vs independent permutation table")
    print("PASS every rank-five parabolic scalar and multiplicity, and #7806's three prior group projections")


if __name__ == "__main__":
    main()
