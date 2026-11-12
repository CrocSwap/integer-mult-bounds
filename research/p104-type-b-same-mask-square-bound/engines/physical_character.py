"""Certify a physical −1-character obstruction from exact interval evidence."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS = {
    "price": "57687d0cdb758cacaff681497c6d4834ec071749156c05b1d74d326cda9c958d",
    "caller": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "interval": "36109749b5b86a32c2e85ee10898bb52ebeeb56112059d7958169cd85d25d3a9",
}


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def checked(args):
    raw = {}
    for key, pin in PINS.items():
        raw[key] = getattr(args,key).read_bytes()
        if sha256(raw[key]).hexdigest() != pin:
            raise ValueError(f"changed dependency {key}")
    return {k:loads(v,object_pairs_hook=unique) for k,v in raw.items()}


def body_mask(e):
    if e[0] == "J":
        assert len(e) == 4 and 1 <= e[1] <= 17
        return (e[1],)
    if e[0] == "A":
        return ()
    assert e[0] == "B"
    if e[1] in ("IDLE_ONE","IDLE_ODD"):
        assert e[3] and len(e[3]) == len(set(e[3]))
        assert e[4:] == ([-1] if e[1] == "IDLE_ODD" else [])
        return e[3]
    assert e[1] in ("ADD","QUERY","SWAP","SCALE","LAMBDA")
    return ()


def c_eigenvalues():
    # Each entry is represented by its integer real/imaginary numerator over 2.
    kernel = [[(1,1),(1,-1)],[(1,-1),(1,1)]]
    for sign, eigen_numerator in ((1,(2,0)),(-1,(0,2))):
        vector = [1,sign]
        for i, row in enumerate(kernel):
            for j in range(2):
                assert sum(a[j]*x for a,x in zip(row,vector,strict=True)) == eigen_numerator[j]*vector[i]
    return {"plus_line_eigenvalue":"1","minus_line_eigenvalue":"i",
            "minus_lines_in_target_body":2,"target_body_eigenvalue":"-1",
            "other_body_eigenvalues":"1","central_eigenvalue":"1"}


def main(args):
    assert __debug__
    d = checked(args)
    price, caller, witness = [d[key] for key in ("price","caller","interval")]
    assert price["head"] == witness["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert witness["phase"] == "q=+1, all body variables one"
    assert witness["old_arbitrary_input_endpoint_columns"] == 36
    cases = price["cases"]
    assert len(cases) == 9 and not witness["unvisited"] and not witness["survivors"]
    result = []
    for case, obs in zip(cases,witness["results"],strict=True):
        a,b,r,s = (case[k] for k in ("earlier","later","role","stage"))
        assert obs["key"] == case and obs["status"] == "excluded"
        tapes = caller["events"]
        offset = caller["types"]["B"]["offset"]
        assert tapes[a] == tapes[b] == ["B","IDLE_ONE",r+offset,[s]]
        matching = [[clock,tapes[clock]] for clock in range(a+1,b) if s in body_mask(tapes[clock])]
        assert not matching and obs["literal_interior_events"] == b-a-1
        i, raw = obs["column_off_axis"][0]
        coeff = Fraction(raw)
        assert i != r and coeff
        result.append({
            "key":case, "interior_matching_body_events":matching,
            "target_body_degree":0, "target_inverse_body_degree":0,
            "matrix_coordinate":[i,r], "retained_square_interval_entry":str(coeff),
            "two_original_idles_interval_entry":str(-coeff),
            "original_minus_square":str(-2*coeff),
        })
    assert len(result) == 9
    print(dumps({"head":price["head"],"input_sha256":PINS,"character":c_eigenvalues(),
                 "proof":"Every interior interval is independent of its target body. The -1 sign conjugates each nonzero off-axis coordinate while the same-role square is identity.",
                 "cases":result},sort_keys=True,indent=2))


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    for key in PINS:
        p.add_argument("--"+key, type=Path, required=True)
    main(p.parse_args())
