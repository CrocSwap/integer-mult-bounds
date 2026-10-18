# A scale-dependent seed average can misprice the recurrence

**Scoped mathematical counterexample and corrected comparison theorem; no new
kappa.** A log-scale average of individual seed roots does not in general
give the exponent of the complete recursive cost. The missing condition is
control of the cumulative scale-oscillation error.

This directly tests the changed fixed-seed restriction proposed in
[Discussion 2278's single-letter lane](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278#discussioncomment-18964674),
within the mechanism scope of [Discussion 1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167).
The exact inspected predecessor is Philippe Van Velzen's
`ed21d6245f8ce1a62e21205be7bedc24271dd772`; source paths, Git blob IDs and
SHA256 hashes are in [SOURCES.json](SOURCES.json). No predecessor code is
imported or vendored. Replay checks the new mathematical witness locally;
it does not reauthenticate those remote source bytes.

## Result

In the source model `T(x)=sum_r (n_r/W)T(rx/m)+h(x)`, use m=256, W=1,
with complete child profiles A=`{16:1,1:2}` and B=`{16:4,1:32}`. Their
exact scalar roots are 1/4 and 3/4. Alternate A and B on equal log-length
scale intervals, and initially set all glue/adapters to zero. The averaged
root is 1/2, but the actual exponent is

    p_eff = log(19+3 sqrt(33))/log(256),    5/8 < p_eff < 2/3.

Both child ranks and all multiplicities are retained. The two-step transfer
is `[[36,8],[1,2]]`. The positive, phase-indexed moment has spectral radius
17/8 at the proposed averaged root, so it fails the contraction test there.
The discrepancy persists with a unit additive toll at every node.

[PROOF.md](PROOF.md) proves the result for every input scale. It also proves
by power comparison that arbitrary per-node switching in a finite positive
catalogue cannot beat its best fixed seed under explicit zero-glue,
bounded-ratio and terminal-cost hypotheses. Thus that limited extremal
conclusion survives, independently of the invalid unconditional averaging.

This counterexample **does not refute** the predecessor's error-qualified
Theorem 1: its retained oscillation allowance is order log x here. A claimed
Cesaro exponent needs that error, and the normalized glue contribution, to be
o(log x). No verdict is made on the other lanes, Problem X, or amplification
comparisons. These profiles are abstract positive recurrences; no native
supplier, physical hosting, precision/storage budget or outer multiplication
transfer is constructed or admitted.

## Reproduce

From the repository root, using only Python's standard library:

```sh
python3.12 -B scripts/research_package.py --package research/scale-dependent-seed-moment-audit
```

The registered commands run with `-I -O -B` and use explicit checks that remain
active under optimization. They write no package files. Direct portable replay:

```sh
python3 -I -O -B research/scale-dependent-seed-moment-audit/verify.py
python3 -I -O -B research/scale-dependent-seed-moment-audit/independent.py
```

Primary coverage: 240 grid prefixes, 120 exact quadratic-field block powers,
homogeneous controls, node-wise extremal bounds and eight semantic defect
controls. The separate checker traverses all rank histories for the displayed
periodic schedule through index 20, all 1,023 index schedules of length at most
nine, matrix recurrences through 120 and three semantic controls.
[REVIEW.md](REVIEW.md) gives its derivation and limits. Finite checks support
the separate written all-scale proof; they are not a formal-kernel proof.

## Open next questions

For an actual proposed growing-seed family, retain its full child ranks and
reached scale phases, then bound cumulative oscillation, terminal normalization
and all glue/adapter costs before assigning an exponent. The first useful
step is one paid caller and an explicit o(log x) error estimate. This audit
does not provide that family or justify another seed search. The structured
question and blocker are in [TASK.json](TASK.json).

## Credit and scope

Philippe Van Velzen's proposed interface and explicit error term motivate the
audit; the positive-recurrence and companion-matrix comparison arguments are
standard. Prepared by Ross Richardson with substantial OpenAI Codex GPT-6.1
Sol assistance. A separate mathematical worker wrote `independent.py` and
`REVIEW.md` without importing the primary verifier or predecessor implementation.
This is independent AI derivation, not independent human review. Apache-2.0.
Selected frontier, frozen inputs and personal configuration are unchanged.
