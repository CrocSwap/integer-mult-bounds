# Sharp rounding radii for integer shear reflections

**Scoped proof with exact finite corroboration; no new kappa.** This answers
Open next question 1 of Nick Petalas's [PR #5079](https://github.com/CrocSwap/integer-mult-bounds/pull/5079),
head `43f558c1b8fc14fb0ed33a4512fbc976beea6b0f`: determine the least uniform
infinity-norm error of an integer-valued rounder commuting with the
nonorthogonal reflection `A_1(x,y)=(x+y,-y)`.

The exact optimum is `floor(2m/3)/m` on the complete grid `(1/m)Z^2`, m>=2,
and `2/3` on R^2. One compatible rule attains all these radii and fixes
integer inputs. The same proof covers every `A_k(x,y)=(x+k*y,-y)`, k integer:

| K=abs(k) | Grid optimum R_m(k) | Real optimum |
|---|---|---|
| 0 | `floor(m/2)/m` | `1/2` |
| 1 | `floor(2m/3)/m` | `2/3` |
| positive even | `(K/2+1)*floor(m/2)/m` | `(K+2)/4` |
| odd, at least 3 | `floor(((K+1)*m-e_m*max(K-m,0))/4)/m` | `(K+1)/4` |

Here e_m is one for odd m and zero otherwise. The correction is essential:
`R_3(7)=5/3`, `R_3(5)=4/3`, `R_5(5)=7/5`, while `R_2(5)=3/2`. Finite order
does not bound the necessary error by dimension and group order alone: the real radii are
unbounded in this order-two, dimension-two family.

[PROOF.md](PROOF.md) supplies the universal argument, including fixed-axis
constraints, tie-compatible orbit choices, and explicit attaining inputs.
This strengthens the predecessor's existence result with matching lower and
upper bounds; it does not replay that result or assert a new supplier.

Scientific base: canonical main `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`,
priority revision 7. [Coordination #5100](https://github.com/CrocSwap/integer-mult-bounds/discussions/5100).

## Evidence and reproduction

[verify.py](verify.py) implements the formula and the at-most-four-candidate
rounder. The separately implemented [lattice_oracle.py](lattice_oracle.py)
enumerates every integer output in a box derived from a feasible output's
literal two-point error, without the formula or two-row reduction. Any better
output must lie in that box. It checks every residue for `-10<=k<=10` and
`2<=m<=18`. The main verifier checks literal equivariance, error bounds,
larger attaining fixtures, and meaningful rejecting controls. The written
proof supplies the universal and real-input results; finite checks alone do not.

[VALIDATION.md](VALIDATION.md) records executed checks, counts and limits.
From the repository root with Python 3.12:

```sh
python3.12 -W error -B research/reflection-rounding-radius/verify.py
python3.12 -W error -I -O -B research/reflection-rounding-radius/verify.py
python3.12 -B scripts/research_package.py --package research/reflection-rounding-radius
python3.12 -B scripts/check_research_commit.py --package research/reflection-rounding-radius --check-source-history
```

Expected marker: `PASS_REFLECTION_ROUNDING_RADIUS no_new_kappa`. Default replay
writes no package files. Optional `--receipt /absolute/external/path.json`
creates a computed report bound to package source hashes. No predecessor
verifier is imported or replayed. SOURCES.json and VERIFY.json pin the
predecessor README as the sole live external input; catalogue and selected
record pins are historical provenance. Frozen sources and the selected record
are unchanged.

## Scope and limitations

This explicitly changes the `uniform-transfer-audit` card to a mathematical
side theorem requested by #5079. It does not discharge a #4100 caller
implication. The domain is the complete grid or R^2; no continuity, linearity
or translation equivariance is required. An actual reader may avoid the
maximizing orbits. Physical floor/comparison/arithmetic/tape costs, dirty echo
restoration, accumulated error, supplier and outer admission remain open.
No arbitrary finite-group optimum, nonlinear frame action, Lean proof,
selected cold replay, new kappa or selected-frontier change is supplied.
Evidence is author-checked with AI assistance; independent human and formal
proof-kernel acceptance are unclaimed.

## Open next questions

1. Does a concrete carried reader reach a maximizing orbit for one of these
   reflections? This would give an actual precision constraint. Start with
   the reader's exact dirty-input image and the explicit witnesses. Reachability
   and the complete paid implementation are missing, as in #5079 Q2.
2. Can exact stabilizer-compatible covering radii be computed for a finite
   integer frame group with more than two elements? Start with #5079's
   nonorthogonal dihedral example and its fixed sublattices. The two-point
   argument does not handle its simultaneous errors and nontrivial stabilizers.

No follow-up is reserved. TASK.json gives the same structured questions.

## Credit

Krzysztof Wojt with substantial OpenAI Codex assistance; Apache-2.0. The primary
agent derived and checked the proof and integrated the package. A Luna agent
inventoried claims/source scope and implemented the independent box oracle.

Nick Petalas supplies #5079's finite-group classification, invariant norm,
stabilizer-compatible construction and explicit radius question. Sricharan
Vagvala / #1631 supplies the infinite-shear obstruction; woklerx / #1892 the
orbit-window analysis and compatibility caveat; Sagar Thakrar / #1537 the
carried-reader setting; Ross Richardson / #1287 and retained #1227/#889/#1203
the output-frame/dirty-echo lineage. Their exact constructions are not alleged
to be defective. This contribution supplies the sharp family formula, attaining
rule and new exact checks; no broader literature-priority claim is made.
