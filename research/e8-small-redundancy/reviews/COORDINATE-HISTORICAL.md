# Independent review of the coordinate-total rigidity result

Reviewer: `/root/math_audit/center_lower_bound/rigidity_review`.

Reviewed files: `coordinate_totals_rigidity.md` and `coordinate_totals_rigidity.py` in this directory. The reviewer found no mathematical gap or counterexample within the stated scope. It checked the full-support lemma, quotient normalization, pairwise-difference argument, common scalar, binary support span, scatter identity, and rowspace bridge.

The reviewer independently reconstructed all 120 certificate ports. It also built a separate system with 72 variables: nine coordinates for each of eight difference vectors, eight explicit zero-sum constraints, and every pairwise equality at each forbidden port. The main checker instead uses 64 variables in a basis of the zero-sum space and only star-shaped equality constraints at each port.

The independent system gave these ranks over F_107:

| Extra normal weight | Rows | Rank | Nullity |
|---|---:|---:|---:|
| 0 | 1016 | 71 | 1 |
| 1 | 1128 | 72 | 0 |
| 3 | 1144 | 72 | 0 |
| 5 | 1112 | 72 | 0 |
| 7 | 1128 | 72 | 0 |

The reviewer saved `rigidity_review_72vars.py` and ran this command from the task directory:

```
python3 -I -B coordinate-totals/rigidity_review_72vars.py ../e8-coupled-retiming/research/e8-coupled-retiming/data/original.json.gz
```

The command returned exit code zero. The certificate SHA-256 was `4b92f00fc7454b9b15e6d71a3b05062792eacca0a0ca4efee46f87827d57c8aa`. The independent script imports no repository module.

The reviewer confirmed that the four nondegenerate subframe orbits have sizes 8, 56, 56, and 8. It also checked that elimination of the common coefficient function loses no constraints: every port has at least one forbidden coordinate.

The result concerns exactly nine totals assigned to the nine coordinate hyperplanes, with their span containing the fixed canonical E8 coefficient space. It does not establish a global copy-cost floor for other frame sets, other fitting matrices, or more totals. This review did not run Lean or verify the complete circuit.
