# Exact invariant lattices for rational rounded shears

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped mathematical proof with exact finite corroboration.
No new kappa or supplier admission is claimed.

For half-up nearest rounding R(t)=floor(t+1/2), consider

    U_a(x,y) = (x, y + R(a x)),
    V_b(x,y) = (x + R(b y), y).

If both rational slopes a,b are nonintegral, a proper full-rank additive
sublattice of Z^2 preserved by both maps exists **if and only if ab is an
integer**. Both updates are then exact linear shears on that lattice.
When a=p/q is reduced, the explicit lattice qZ x |p|Z attains the positive
direction. This is an all-rational theorem, not a bounded search conclusion.

The more general exact criterion covers every rational slope and every
full-rank lattice, including skew lattices. In Hermite coordinates

    L = { (hn, rn+km) : n,m in Z }, h,k>=1, 0<=r<k,
    g = gcd(r,k), ell = hk/g,

    U_a(L)=L iff k=1 or ah/k is an integer,
    V_b(L)=L iff ell=1 or bg/ell is an integer.

[PROOF.md](PROOF.md) proves the criterion by identifying the source
projections and the target fibers. The scalar step is that, for d>=2,
R(cn) can belong to dZ for every integer n only when c belongs to dZ.
No predecessor numerical result is needed in the proof.

For the lifting slopes a=1/2,b=-4/5 of the rational rotation with
cosine 3/5 and sine 4/5, the product is -2/5. Thus no proper additive
integer lattice survives both directions at every substep. A correlated
precision policy using one fixed proper lattice cannot pass that closure
gate. This does not exclude an interface whose domain changes between stages.

## Evidence and reproduction

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rounded-shear-lattice-closure/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/rounded-shear-lattice-closure/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-shear-lattice-closure
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rounded-shear-lattice-closure --check-source-history
```

Substitute another CPython 3.12 executable on another machine. Run the final
command after committing. The direct checker prints
`PASS_ROUNDED_SHEAR_LATTICE_CLOSURE` in a generated JSON stdout receipt
bound to the six package file hashes. It writes no files. The registered
runner executes both modes and reports `PASS_REGISTERED_RESEARCH_PACKAGE`.

The checker covers all 75 Hermite lattices with 1<=h,k<=5 and 0<=r<k,
and all 39 distinct reduced slopes p/q with -5<=p<=5, 1<=q<=5.
It compares 5,850 one-shear closure verdicts with 664,950 literal point
updates over complete residue periods. The periodic reduction has its own
proof and does not use the closure criterion to decide the oracle verdict.

It also checks all 784 ordered pairs of nonintegral slopes in that set.
The 56 integer-product pairs have literal constructive replays, comprising
40,800 additional point updates; the other 728 pairs have no proper
invariant lattice in the enumerated family. That bounded absence corroborates
the universal written theorem and does not replace it. Ten semantic controls
cover unit fibers, integral-slope exceptions, skew lattices, signed ties,
the positive construction, single-direction closure and completed-word
closure. Ten invalid-input cases reject explicitly, including under `-O`.

## Source, credit and scope

Credit woklerx's [PR1848](https://github.com/CrocSwap/integer-mult-bounds/pull/1848),
head `d975e19e7e931fc2b45792a4f7140ac13759a7da`, for its explicit
intervening-update lattice-closure question and affine-lattice precision
interface. Its cancellation theorem is a cited predecessor, not an audit
target. The new step is the classification for separately rounded planar
shears and its integer-product obstruction. Hermite normal form, floor
increments and rational lifting factorizations are classical; no general
literature-priority claim is intended. Gareth Davidson, Chafik Boukhalfa
and Ali Romman retain the mixed-precision and dirty-restoration lineage
credited by that predecessor.

Adam Gall's [PR1908](https://github.com/CrocSwap/integer-mult-bounds/pull/1908)
already supplies an actual rounded-leaf counterexample to transferring
ideal lattice closure. It is separate context, with no replay here. The
present result gives a quantified criterion for a different explicit
nonlinear update model. Linear Gaussian-module classifications and
equivariant frame rounders are different contracts as well.

[SOURCES.json](SOURCES.json) pins the source question, original catalogue
and selected record as historical provenance. No predecessor executable,
pending Git object, network service or external library is a runtime input.
[TASK.json](TASK.json) records the change from `formal-interface-lemma`
to this written precision-interface result. No proof-kernel formalization
or binding to an actual selected caller is supplied.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362381)
and overlap check used canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The cached scan covered 387 open PRs and 6,328 Discussion
records with complete pagination. Its local scan covered 108 of 8,917
note paths; all-main README searches and distinctive merged-PR searches
supplemented it. Arbitrary code diffs and unpublished work remain outside
that coverage. No novelty certificate is claimed.

## Limitations and verification design

The theorem requires a full-rank additive sublattice of the integer plane,
the same lattice at both substeps, rational fixed slopes, half-up rounding,
and separately rounded increments followed by exact integer updates.
Both nonintegrality hypotheses are essential for the product equivalence.
The closure criterion itself also handles integral slopes. Affine cosets,
lower-rank domains, changing stage domains, nonlinear entrance sets and
whole-word-only closure are excluded.

Actual caller reachability, physical native realization, restoration and
precision/movement/storage prices, the complete paid/productive invoice,
supplier admission and all five selected framework assumptions remain
open. No predecessor scientific replay, selected cold replay, Lean or
Docker run was performed. Independent human and formal proof-kernel
review are unclaimed.

The verifier has no recursion, subprocesses, external imports or writes.
Its fixed census bounds and validated Hermite/slope limits bound every
enumeration. Functions remain below 60 lines. Mathematical checks use
explicit exceptions and remain active under optimized Python. Python's
managed allocation and dataclass-generated methods are documented Power
of Ten deviations; the finite parameter sets bound live storage and
dispatch, with no fixed-memory or static-analyzer claim. Warning-strict
normal and optimized execution provide interpreter diagnostics.

## Open next questions

Can changing lattice domains support one actual rounded lifting caller?
First fix its literal update sequence and derive the exact image domain
at each substep. This matters because the present obstruction requires
one common invariant lattice. Actual source reachability, later inverse
compatibility and the complete precision/movement/storage bill remain
blockers. The structured question is retained in TASK.json. No further
construction search is part of this contribution.
