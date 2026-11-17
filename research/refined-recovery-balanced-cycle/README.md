# Sharp balanced rank-one frames for refined recovery

Scoped written proof with exact finite corroboration. This package was produced
by Nick Petalas. Apache-2.0.

The new explicit cycle answers structured-construction question 2 of Armin
Pourshafeie / apoursh's [#6853](https://github.com/CrocSwap/integer-mult-bounds/pull/6853).
Within the affine frame family of #6851, at every positive depth t,

    S >= (2^104-2) 13^(-4t) + 13^(-8t).

Equality is attainable exactly when 2^100 divides t. The construction enumerates
kernel vectors in Gray order and uses only rank-one changes from the identity.
Every transition uses one signed retained integer lift. At positive complete
cycles the exact minimum maximum fiber within this family is

    [13^(8t) + (2^104-2) 13^(4t) + 1] / 2^104.

The fixed infinite sequence attains #6852's asymptotic exponent 4 log2(13)
explicitly. Its enormous period gives no practical improvement at depths 28–30.
The bound, construction, shortest equality depth and specialization are proved
in [PROOF.md](PROOF.md). The full 2^100-stage period is not enumerated.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/refined-recovery-balanced-cycle
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/refined-recovery-balanced-cycle/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/refined-recovery-balanced-cycle/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/refined-recovery-balanced-cycle/cycle.py --index 7
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/refined-recovery-balanced-cycle --check-source-history
```

The scientific marker is PASS_REFINED_RECOVERY_BALANCED_CYCLE. The constructor
prints sparse factors for W=I+v*lambda and U_to_next=I+delta*lambda, with zero-based
owner and cycle indices. It computes any index below 2^100 without expanding the
period. Sparse checkouts must first materialize this package and the declared
VERIFY.json inputs. Direct verification is Git-free once those files are present.

The generated stdout receipt binds every package file and live input by SHA256.
It reports eight reduced-dimension cycles, 8,152 nonzero cycle characters,
4,626 complete arbitrary-map sequences with 46 equality cases, 3,238 complete
Fourier occupancy multisets, 106 integer frame sample invocations, eight
omitted-vector spectrum controls and eight rejected API inputs. The arbitrary-map
census fixes the first map at zero and covers d=1, t=1..4 and d=2, t=1..2.
The occupancy census covers dimensions 1..3 and totals 1..6. The sample indices
include all 100 individual Gray basis vectors and the cyclic wrap. These are
finite corroborations; the universal proof is not a finite census.

## Premises, credit and scope

Credit apoursh #6853 for the question and finite-depth construction, #6851 for
the affine character model and #6852 for the existential optimal rate; Nick
Petalas #6660 for the integer frame family and retained lifts; CubeJerry #6327
and zxv #5444 for the rounded-native interface and literal matrix. The inherited
Poisson and small-error maximum-fiber implications are premises. Their exact
source bytes are pinned in SOURCES.json. No predecessor scientific executable
is imported or replayed. Their attribution and notices remain unchanged.

This changes uniform-transfer-audit to a local analytic-recovery construction.
It does not discharge a selected framework assumption. Optimality and the
2^100 divisibility obstruction apply only to the affine family. Nonmultiples
have a strict lower bound here, with no exact optimum supplied. The constructor
uses the unbounded integer model in the proof; its reference action API limits
operands to 4,096 bits. No full-cycle execution, codec, physical tag acquisition,
restoration cost, accepting caller, supplier admission, new kappa or selected
cold replay is claimed. Independent human and formal proof-kernel review are
unclaimed. Lean and Docker were not run.

## Implementation bounds

The two new Python files use bounded loops and no recursion, dynamic evaluation
or callback dispatch. A frame uses 100 lifts of 112 coordinates. The source
parser accepts 25 blocks of four lifts, each with at most 112 entries and
coefficients of magnitude at most 100. Functions are below 60 physical lines.
Checks raise exceptions and remain active under -O. The CLI rejects out-of-range
indices. Integer action, inverse, mode preservation and transition composition
are checked against the actual matrix.

Power-of-Ten rule 3 has a managed-runtime deviation in both files. Python and
its JSON and integer libraries allocate dynamically. The fixed source dimensions,
4,096-bit action limit, at most 256 stages and 4,096 characters in a toy case,
and explicitly bounded census domains bound live data. Source JSON is trusted
only after hash authentication in the verifier. No live service or retained
resource is introduced. Warning-strict normal and optimized replay, source
compilation and CLI checks are the available diagnostics; no static type checker
is configured for this isolated Python package. A physical implementation would
need fixed-capacity storage and its own resource proof.

## Open next questions

1. Can a much shorter explicit near-balanced sequence give a useful finite-depth
   bound? Start with a small-bias kernel multiset and prove every character
   imbalance bound. No short construction is supplied.
2. What bound replaces this one outside the affine family? First derive the
   character action of a frame that changes its fixed complement. This package
   gives no global frame classification.

The relevance and blockers are also recorded in TASK.json.
