"""Compare independent labeled and free-orbit distance distributions."""
from pathlib import Path
import json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from flat_oracle import collect as flat
from state_oracle import collect as raw
from orbit_oracle import collect as quotient


def main():
    labeled, pencils, orbits=raw(),flat(),quotient()
    for name,value in [("RAW-STATES.json",labeled),("FULL-PENCILS.json",pencils),("TERNARY-ORBITS.json",orbits)]:
        if json.loads(json.dumps(value))!=json.loads((HERE/name).read_text(encoding="utf8")):
            raise ValueError("frozen graph domain: "+name)
    by_m={r["m"]:r for r in orbits}
    for r in pencils:
        if r["q"]==3:
            if r["distances"]!=by_m[r["m"]]["weighted_costs"]:
                raise ValueError("raw and quotient distance histograms")
    for row in orbits:
        if (row["m"]<5) != (len(row["weighted_bound_gap"])==1):
            raise ValueError("first ternary dimension with a gap")
    print(json.dumps(dict(status="PASS_MONOMIAL_GUARD_GRAPHS",raw_states=sum(r["states"] for r in labeled),
                          pencil_states=sum(r["states"] for r in pencils),ternary_orbits=sum(r["orbits"] for r in orbits),
                          covered_at_m8=orbits[-1]["raw_states"])))


if __name__=="__main__":
    main()
