"""Exact corroboration of the new full-batch threshold; standard library only."""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
LIMIT = 64
SHARP = Fraction(9702312163, 8589934592)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bill(p, ell, h):
    if not (type(p) is type(ell) is type(h) is int):
        raise ValueError("integer parameters required")
    if not (2 <= p <= LIMIT and 1 <= h <= ell <= p):
        raise ValueError("fixture outside bounded checker domain")
    q, n, w = p + 2, 2**h, 4 * (p + 2)
    accesses = n*n + 2*n*h*h + 24*n*h + 3*n
    records = n * (h*h + 3*h + 1)
    tape = accesses * (26*w*records + 25*w) + 30*w*records
    tape += 3*n*h + 6*(2*h-1)*n + 3
    crt = 65536*q**3 + 1024*q*ell**3 + 1024*q*q
    axis = crt + 4*(9*(ell+2)**2*n + (1+8*w*w)*tape)
    return 8*q*axis, 2**(4*ell)*q**16


def expanded_batch(p, ell, h):
    """A separate q-polynomial expansion of the full batch numerator."""
    q, n = p+2, 2**h
    a = n*(n + 2*h*h + 24*h + 3)
    j = n*(h*h + 3*h + 1)
    linear = 4*(a*(26*j+25)+30*j)
    constant = n*(15*h-6)+3
    return ((524288+4096*linear)*q**4 + (8192+4096*constant)*q**3
            + (32*linear+8192*ell**3)*q**2
            + (32*constant+288*(ell+2)**2*n)*q)


def sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            require(digest == row["sha256"], "source SHA256 mismatch")
            header = f"blob {len(data)}\0".encode()
            blob = hashlib.sha1(header+data).hexdigest()
            require(blob == row["git_blob"], "source Git blob mismatch")


def proof_checks():
    checks = 0
    for h in range(2, LIMIT+1):
        q, n = max(5, h+2), 2**h
        require(419328 < n**4*q**11, "first third")
        require(864 < n**3*q**13, "second third")
        require(146626560*h*h < n*q**12, "third third")
        if h >= 4:
            require(2*h*h*25 >= 32*(h+1)**2, "induction multiplier")
        checks += 1
    require(297353184 < 16*5**12, "height-one base")
    for ell in range(1, LIMIT+1):
        require((ell+1)**3-16*ell**3 <= -8*ell**3, "cubic step")
        require((ell+3)**2 < 16*(ell+2)**2, "quadratic step")
    return checks, LIMIT


def grid():
    failures, total, maximum = [], 0, Fraction(0)
    for p in range(2, LIMIT+1):
        for ell in range(1, p+1):
            for h in range(1, ell+1):
                batch, allowance = bill(p, ell, h)
                require(batch == expanded_batch(p, ell, h), "expanded bill")
                ratio = Fraction(batch, allowance)
                require(ratio <= SHARP, "sharp uniform bound")
                if batch >= allowance:
                    failures.append([p, ell, h])
                maximum = max(maximum, ratio)
                total += 1
    require(failures == [[2, 1, 1], [2, 2, 2]], "exception classification")
    require(maximum == SHARP, "attained constant")
    return total, failures


def controls():
    invalid = [(True, 1, 1), (2, 0, 1), (2, 1, 2), (1, 1, 1),
               (2, 3, 1), (LIMIT+1, 1, 1)]
    for args in invalid:
        try:
            bill(*args)
        except ValueError:
            continue
        raise ValueError("invalid fixture accepted")
    batch, allowance = bill(2, 2, 2)
    require(batch > allowance, "constant-one overclaim must reject")
    require(batch*SHARP.denominator == allowance*SHARP.numerator,
            "any strictly smaller constant must reject at the witness")
    return len(invalid)+2


def result():
    sources()
    proof = proof_checks()
    total, failures = grid()
    rejection_count = controls()
    names = ["PROOF.md", "verify.py", "SOURCES.json", "TASK.json", "VERIFY.json"]
    hashes = {name: hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()
              for name in names}
    witnesses = []
    for ell, h in [(1, 1), (2, 1), (2, 2)]:
        batch, allowance = bill(2, ell, h)
        witnesses.append({"p": 2, "ell": ell, "h": h, "batch": batch,
                          "allowance": allowance,
                          "ratio": str(Fraction(batch, allowance))})
    return {"status": "PASS_CRT_ARENA_BATCH_THRESHOLD",
            "claim_type": "scoped proof with finite corroboration",
            "grid_p_max": LIMIT, "grid_triples": total,
            "exceptions": failures, "sharp_constant": str(SHARP),
            "height_checks": proof[0], "extension_checks": proof[1],
            "rejection_controls": rejection_count,
            "p2_exhaustion": witnesses, "source_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    actual = result()
    path = PACKAGE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(actual, indent=2)+"\n")
    expected = json.loads(path.read_text())
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt differs from exact replay")
    print(json.dumps(actual, indent=2))


if __name__ == "__main__":
    main()
