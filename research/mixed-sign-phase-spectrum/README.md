# Exact phase defects for mixed-sign orthogonal charts

For every binary sign mask b and every width n>=1, the attainable defects of
orthogonal chart changes are exactly

    D_b = {e : wt(b+e) == wt(b) modulo 4}.

Each defect e has the explicit representative T_e=I+ee^T and the same number
of realizations. The exact-preserver subgroup has order

    |O(n,2)| / sum_{k==wt(b) modulo 4} binomial(n,k).

This is a scoped written algebraic proof with exact finite corroboration.
See [PROOF.md](PROOF.md) for the full gate contract and argument. No new
kappa, physical supplier or selected-frontier change is claimed.

The addition to Philipp / mightyOil's [PR1300](https://github.com/CrocSwap/integer-mult-bounds/pull/1300)
is an arbitrary fixed mixture of positive and negative residual gates. At
width five with one negative axis, a weight-two defect is attainable although
the equal-sign spectrum excludes it. At width six with one negative axis,
there are 12 defects and 1920 exact preservers, versus the credited equal-sign
values 16 and 1440. These exact counts are corroborated by the verifier's
explicit sign/defect enumeration and the inherited group-order recurrence.

This changes the `bit-helper-contract` card to a phase-boundary side result.
It specifies the algebraic admission criterion for mixed signs before anyone
prices an actual changed chart. It does not claim a cheaper complete caller.
The first source discriminator is the width-five one-negative-axis fixture.
The selected metadata positive control was run separately; no predecessor
scientific suite was replayed as this contribution.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/mixed-sign-phase-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/mixed-sign-phase-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-sign-phase-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mixed-sign-phase-spectrum --check-source-history
```

Substitute another CPython 3.12 path elsewhere. The verifier prints
`PASS_MIXED_SIGN_PHASE_SPECTRUM` inside a JSON receipt whose hashes bind every
package file. It reads no predecessor executable and writes no files.
`SOURCES.json` preserves predecessor proofs as historical provenance.

The bounded replay enumerates every orthogonal matrix through width five,
every sign mask at those widths and every kernel coefficient. It also checks
the matrix census by independent full binary-matrix enumeration through width
four; constructs every admissible sign/defect pair through width nine; tests
every width-four twisted-cocycle pair for every sign mask; and includes ten
semantic controls. The generated receipt reports 777 orthogonal matrices,
23,866 matrix/sign pairs, 749,988 literal coefficients, 66,066 full binary
matrices, 349,524 sign/defect candidates, 87,892 attaining representatives
and 36,864 cocycle pairs. These are finite checks of the new mixed-sign
statement, not a predecessor audit.

## Scope and provenance

The scientific base is canonical main `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`,
priority revision 7. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146049)
preceded implementation. The initial cache covered 340 open PRs and 4440
Discussion records with complete remote pagination. The sparse local search
was incomplete; targeted `git grep origin/main` and merged-PR searches covered
the distinctive phase object separately. Search coverage is not novelty proof.

Independent human and formal proof-kernel review are unclaimed. The all-width
claim rests on the written proof, not extrapolation from the finite checks.
Physical route/frame costs, native realization, source acquisition, restoration,
compiler, precision/tape, stock, complete supplier admission and the full
multiplication theorem remain outside scope. No Lean, Docker or selected
supplier cold replay was run.

The verifier uses bounded Python allocation, a managed-runtime deviation from
Power of Ten's fixed-allocation rule. Widths are fixed at 1..5 for group/kernel
checks, 1..4 for the full-matrix cross-check, and 1..9 for representatives. The
prefix list is capped at 32768 entries, each matrix has at most nine columns,
and convolution arrays have at most 32 entries. There is no recursion, child
process, network access, dynamic code or external dependency. Explicit errors
preserve all checks under `-O`. Every function has fewer than 60 lines. Warning
strict normal/optimized replay is the available diagnostic check. A larger
registered domain must first update these bounds and its measured runtime.

## Open next questions

1. Can a named mixed-sign native helper use the larger exact-preserver subgroup
   to reduce its complete physical bill? First bind its literal sign mask and
   compare an explicit phase-preserving chart with all transport/restoration
   costs. No priced caller is supplied here.
2. Which defects remain when the permitted orthogonal chart changes must fix
   a specified set of literal axes? First derive the restricted orbit of q_b
   on that stabilizer before proposing a synthesis search. The unrestricted
   representative T_e need not fix those axes.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
Philipp / mightyOil's PR1300 supplies the equal-sign defect spectrum, canonical
transvection and orthogonal-group order. Gareth Davidson's PR1255 supplies the
C-gate phase contract and row convention. yssite's PR1558 supplies the signed
Gauss-normalization context, following icekylinx's PR24. Credit Rohan Arun,
Jeremy Kothe, Hao Yan, Josie Elliston, Douglas Colkitt and the retained
Clifford/normalization lineage. Classical quadratic-refinement and Gauss-sum
facts retain their classical status. All predecessor notices stay unchanged.
