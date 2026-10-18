# One root-linear factor makes the E8 mask rigid

**Research note / scoped negative result. No new supplier or kappa.**

On P112, all 112 additional single-line punctures P111, and all 1260
frame-pair P104 sets, requiring a complex decoder to be exact only on the
even-inner-product entries already forces exactness on **every** entry,
provided at least one factor is root-linear. The opposite factor is
unrestricted, and the number of terms can be arbitrary.

Precisely, let `R` contain the live norm-two E8 root representatives. If
`D = R A` **or** `T = R B`, and `D T^transpose = 2 R R^transpose` on the
orthogonal pairs and diagonals, then the same equality holds on all pairs.
Transpose is ordinary complex transpose. The proof also applies whenever
the deleted root lines can be covered by at most eight orthogonal sets;
only the stated 1373 live sets are enumerated.

## What this adds and what it costs

PR968 and PR1077 explicitly leave masked identities outside their
eight-term all-pairs theorems. This result rules out a particular route
through that opening: changing only the required entries while keeping
one root-linear factor. It uses elementary covariance identities and a
local spanning argument, without the predecessors' hyperplane-flat
classification premise. See [PROOF.md](PROOF.md).

For each fixed term count, the masked and all-pairs feasible factor pairs
in this class are identical. Therefore their minima under the same
support-pair copy-cost function are identical too. Even an optimistic
budget with free mask enforcement cannot save copied information **from
this relaxation alone**. This is the stopping criterion; there is no new
helper word to price or adopt. It does not exclude better scheduling or
better all-pairs factorizations.

For exactly eight terms, the inherited PR1077 floor consequently applies:
64 on P112, 63 on these P111 sets, and at least 56 on these P104 sets.
This is a transfer of the predecessors' scoped floor, not a new numerical
bound. No such eight-term floor is asserted for nine or more terms.
Concurrent [PR1180](https://github.com/CrocSwap/integer-mult-bounds/pull/1180)
by woklerx addresses arbitrary-term **all-pairs cost** with both factors
root-linear; it explicitly leaves masked identities open. Its new floor is
not a dependency of this package. The similar cancellation fixture is
credited as a shared scope control, not a new decoder mechanism.
To escape this mask rigidity on these live sets, **both** factors must
leave the root-coordinate column space. That is a necessary condition,
not a construction or a guarantee of a favorable completed budget.

## Reproduce

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -B research/complex-masked-rigidity-seed28/verify.py
```

Expected final line, exit status zero:

```text
PASS_ONE_SIDED_MASK_RIGIDITY_S28 sets=1373 local_spans=143584 controls=7
```

The command checks pinned proof/model sources, all 7744 covariance
entries, the semantic controls, and the independently implemented local
span certificate. It compares both deterministic receipts to their
committed JSON. `verify.py --write` regenerates only `CERTIFICATE.json`;
the independent oracle has its own regeneration command.

The two methods have different proof dependencies:

- `verify.py` checks integer covariance identities. The written Bessel
  inequality argument turns them into uniform spanning statements.
- `tensor_oracle.py` independently enumerates the roots and frames and
  supplies exact local basis witnesses for every one of the 143,584
  `(live set, target)` pairs. It does not rely on the covariance identity.

A nine-term positive fixture has a root-linear first factor and genuinely
non-root-linear cancelling columns in the second factor. Controls also
exhibit the failures caused by deleting diagonals or dropping both
root-linearity assumptions, detect a coefficient error and corrupted
geometry, and distinguish ordinary from conjugate transpose. These are
exact finite checks, not a formal proof of the full multiplication theorem.

## Scope, sources and attribution

The base is `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`, assignment seed
**28**, complex-supplier track. [CLAIM.md](CLAIM.md) records the three
candidates, bounded domain and refinement; [OVERLAP.md](OVERLAP.md)
records the inspected competing work; [SOURCES.json](SOURCES.json)
records exact predecessor heads, source hashes and selected context.

The selected result at that base is PR1094's conditional
`kappa = 836330098538459/500000000000000000`. It is orientation context,
not a result of this experiment. This package changes neither the
selected record nor any existing supplier, archive or `upstream/` file.
No native construction, hosting, source access, restoration, precision,
all-size compiler, analytic transfer or complete selected-frontier replay
is claimed or newly discharged.

Credit DreamingOfClouds (#717 and #595) for the decoder/copy model,
themilkman216 (#968) for the frame-pair construction/census and all-pairs
floor, woklerx (#1077) for its complex extension, Joel Pulikkan /
GamingPuzzled (#620) for prior decoder-floor work, and icekylinx for P112.
The selected packing context credits Rohan Arun (#1094), Jeremy Kothe,
Hao Yan and the retained supplier lineage. This scoped result does not
claim their constructions or cost floors as new.

Prepared for Philipp / `@mightyOil` with substantial OpenAI Codex
assistance in the research, proof, implementation and review. Separate
AI agents supplied the independent oracle and adversarial review; no
independent human review or proof-assistant verification is claimed.
New material is Apache-2.0; see [NOTICE.md](NOTICE.md).
