#!/usr/bin/env python3
"""Independent literal/profile and rational-witness audit; does not rerun Lean."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analytic", required=True, type=Path)
    parser.add_argument("--selected", required=True, type=Path, action="append")
    parser.add_argument("--profile-source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    path = args.analytic
    source = (path / "SelectedProfileCertificate.lean").read_text()
    witnesses = json.loads((path / "selected-witnesses.json").read_text())
    manifest = json.loads((path / "theorem-manifest.json").read_text())

    def literal(name, domain):
        expression = re.findall(rf"^def {name} : {domain} := (.+)$", source, re.M)
        require(len(expression) == 1, "Missing or repeated literal " + name)
        if domain == "ℕ":
            require(expression[0].isdigit(), "Nonliteral natural " + name)
            return int(expression[0])
        match = re.fullmatch(r"\((\d+) / (\d+) : ℚ\)", expression[0])
        require(match is not None, "Nonliteral rational " + name)
        return Q(int(match[1]), int(match[2]))

    m, W = literal("m", "ℕ"), literal("W", "ℕ")
    saving, log_two = literal("saving", "ℚ"), literal("logTwoUpper", "ℚ")
    regions = re.findall(r"def rows : List Row := \[(.*?)\]", source, re.S)
    require(len(regions) == 1, "Missing or repeated row list")
    constructor = re.compile(r"⟨(\d+), (\d+), (\d+), \((\d+) / (\d+) : ℚ\), \((\d+) / (\d+) : ℚ\)⟩")
    matches = list(constructor.finditer(regions[0]))
    require(re.fullmatch(r"[\s,]*", constructor.sub("", regions[0])) is not None,
            "Unparsed syntax in literal row list")
    rows = [dict(width=int(t), multiplicity=int(n), scale=int(k),
                 logSmall=str(Q(int(ln), int(ld))), expUpper=str(Q(int(un), int(ud))))
            for t, n, k, ln, ld, un, ud in (match.groups() for match in matches)]
    require(len(rows) == 27 and rows == witnesses["rows"], "Literal/witness row mismatch")
    require(m == witnesses["m"] and W == witnesses["W"] and saving == Q(witnesses["saving"])
            and log_two == Q(witnesses["log_two_upper"]), "Literal/witness parameter mismatch")
    profile = {str(row["width"]): row["multiplicity"] for row in rows}
    require(len(profile) == len(rows), "Duplicate width")
    require(0 < saving < 1 and m > 1 and W > 0, "Invalid parameters")
    mass = sum(row["width"] * row["multiplicity"] for row in rows)
    bindings = []
    for certificate in args.selected:
        data = json.loads(certificate.read_text())
        require(data["bit"]["child_multiplicities"] == profile, "Selected multiplicity mismatch")
        require(data["bit"]["m"] == data["finite_bridge"]["bit"]["m"] == m, "Selected m mismatch")
        require(data["bit"]["W"] == data["finite_bridge"]["bit"]["W"] == W, "Selected W mismatch")
        require(Q(data["bit_saving"]) == Q(data["assembly"]["parameters"]["a_bit"]) == saving,
                "Selected saving mismatch")
        require(data["bit"]["total_rank"] == mass and data["bit"]["deficit"] == m * W - mass,
                "Selected mass/deficit mismatch")
        require(data["bit"]["maxchild"] == max(row["width"] for row in rows), "Selected maxchild mismatch")
        bindings.append(dict(path=str(certificate), sha256=sha256(certificate.read_bytes()).hexdigest(), exact=True))

    def polynomial(x, terms):
        return sum((x ** j / factorial(j) for j in range(terms)), Q())

    require(log_two >= 0 and 2 <= polynomial(log_two, 24), "Log-two witness fails")
    moment = Q()
    for row in rows:
        t, n, k = row["width"], row["multiplicity"], row["scale"]
        L, U = Q(row["logSmall"]), Q(row["expUpper"])
        ratio = Q(m, t * 2 ** k)
        x = saving * (k * log_two + L)
        require(0 < t < m and n > 0 and L >= 0, "Invalid literal row")
        require(ratio <= polynomial(L, 24), "Lower-exponential log witness fails")
        require(0 <= x <= 1, "Exponential argument domain fails")
        require(polynomial(x, 8) + x ** 8 * 9 / (factorial(8) * 8) <= U,
                "Upper-exponential witness fails")
        moment += Q(n * t, m * W) * U
    require(moment < 1 and moment == Q(witnesses["rational_moment_upper"])
            and 1 - moment == Q(witnesses["rational_gap"]), "Rational moment/gap mismatch")
    gap = re.findall(r"^theorem rational_gap_exact : 1 - rationalUpper = \((\d+) / (\d+) : ℚ\)", source, re.M)
    require(len(gap) == 1 and Q(*map(int, gap[0])) == 1 - moment, "Lean gap literal mismatch")
    source_binding = None
    if args.profile_source:
        digest = sha256(args.profile_source.read_bytes()).hexdigest()
        require(digest == witnesses["source_sha256"], "Witness provenance file hash mismatch")
        require(json.loads(args.profile_source.read_text())["bit"]["child_multiplicities"] == profile,
                "Witness provenance profile mismatch")
        source_binding = dict(path=str(args.profile_source), sha256=digest)
    for name, record in manifest["files"].items():
        require(sha256((path / name).read_bytes()).hexdigest() == record["sha256"], "Analytic source hash mismatch")
    report = dict(status="PASS", m=m, W=W, saving=str(saving), rows=len(rows),
                  rank_mass=mass, deficit=m * W - mass, profile=profile,
                  selected_bindings=bindings, profile_provenance=source_binding,
                  literal_witnesses_equal=True, independently_rechecked_rational_inequalities=True,
                  rational_upper=str(moment), rational_gap=str(1 - moment),
                  analytic_source_sha256={name:record["sha256"] for name,record in manifest["files"].items()},
                  scope="Independent source/literal/rational audit, not a new Lean build. The real-analytic proof and its standard-axiom logs were reviewed separately. Physical graph-to-profile and machine transfer remain separate.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: 27 literal rows, both selected certificates, all rational witnesses, exact real-power normalization reviewed")


if __name__ == "__main__":
    main()
