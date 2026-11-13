# Exact finite Gaussian outward slack

This package proves exact finite optima for injective integer-output
rounding of \(U=H_4/2\) with Euclidean error at most one. For
\(S_R=\{x\in\mathbb Z^4:\|x\|_2\le R\}\), the verified optima are:

| Radius | Inputs | Optimal outward slack | Strict Hall witness size |
|---:|---:|---|---:|
| 5 | 3,121 | \(\sqrt{21}-\sqrt{19}\) | 1,809 / 1,777 |
| 6 | 6,577 | \(\sqrt{31}-\sqrt{28}\) | 3,569 / 3,537 |
| 7 | 11,833 | \(\sqrt{31}-\sqrt{28}\) | 3,569 / 3,537 |
| 9 | 32,633 | \(\sqrt{78}-\sqrt{73}\) | 23,561 / 23,497 |
| 11 | 72,465 | \(\sqrt{78}-\sqrt{73}\) | 23,561 / 23,497 |

The same value at radii 9 and 11 implies the radius-10 optimum by set
inclusion; radius 10 was not separately computed. A signed-permutation
identity transfers these finite results and the necessary global lower
bound to #6509's ideal Gaussian pair and its conjugate.

The global outward-slack infimum at error cap one is consequently in
\([\sqrt{78}-\sqrt{73},1]\), using the inherited #6509 construction for
the upper endpoint. No global map attaining the lower endpoint is supplied.
All five selected multiplication assumptions remain; no new kappa is claimed.

## Proof and verification modules

`PROOF.md`, `R5-OPTIMUM.json.gz`, `verify.py` and `compact-hall/` retain the
original radius-five result and compact two-exclusion Hall proof. The
original proof, draft and review discuss that module's earlier lower bound.
Their scientific inputs and code are unchanged by the extension.

`orbit-extension/` contains the four later, explicitly bounded radius checks,
full positive quotient-flow certificates and strict Hall orbit predicates.
Its proof shows why flow between paired signed-coordinate orbits lifts to
an actual finite injection: each orbit-pair edge relation is biregular, so
uniformly distributed flow supplies a fractional matching, hence Hall's
inequality. No complete-bipartite assumption is made for an orbit pair.

`review/extension/` contains an independent full-point certificate checker
that imports no author generator or comparator, and an independent full
radius-nine matching. Both methods agree with the extension. The standalone
radius-five compact check does not read the original matching certificate.

## Read-only reproduction

Python 3.10+ and the standard library suffice. From this directory:

```sh
python3 -I -B verify.py
python3 -I -B compact-hall/check.py
python3 -I -B orbit-extension/verify.py
python3 -I -O -B orbit-extension/verify.py
python3 -I -B review/extension/check_full_certificates.py
python3 -I -B review/extension/check_full_r9.py
```

The four-radius search is reproducible with
`python3 -I -B orbit-extension/sweep.py`; redirect its output to a temporary
file to compare against `orbit-extension/RESULT.json`. Default checks do not
write files. Exact source pins, search coverage, controls, limitations and
AI/predecessor credit are retained. `PR-DESCRIPTION.md` is the current full
proposed description; `PR-DRAFT.md` is the original R5-only draft.
