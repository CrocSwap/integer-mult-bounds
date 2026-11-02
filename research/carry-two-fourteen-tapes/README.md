# Carry two on fourteen fixed tapes

This contribution was produced by Nick Petalas. Claim type: scoped all-size
construction and resource proof, with finite exact implementation evidence.

For every positive canonical binary-encoded `P,Q,G,S`, the two fixed programs
move every Boolean payload of volume `V=P Q² G S` by

```text
(p,x,g,y,z) -> (p,x,g,(y +/- (x+2)) mod Q,z).
```

Each direction has **598 local microinstructions, fourteen tapes and seven
symbols**. The complete costs are **at most 504V transitions and 41V visited
cells**. Source and descriptors are preserved with returned heads. Output is
separately owned. Every scratch cell and marker is erased and its head returns
to its original position. The contract includes `Q=1` and `Q=2`.

Charles Bethin's [PR2829](https://github.com/CrocSwap/integer-mult-bounds/pull/2829)
asks whether another fixed carry can use its fourteen-role budget. This answers
that question for carry two. JoyboyBrian's
[PR5019](https://github.com/CrocSwap/integer-mult-bounds/pull/5019) already supplies
arbitrary coefficients and offsets using nineteen tapes. The new result reduces
the role budget for this fixed carry. It makes no optimality claim about tapes,
instructions or runtime.

## Construction and proof

[controller.py](controller.py) compiles the two tables without runtime extents
or payload as arguments. After descriptor conversion, the binary workspace is
empty. It becomes a unary Q-position counter. Two cyclic unit advances prepare
the split. This separates termination of the x loop from wrapping of the split,
without adding a physical role. [PROOF.md](PROOF.md) gives the invariant, endpoint,
cleanup argument and exact path counts.

The assembler, unary converter, segment copier, reset and erasure macros are
David Arias's PR2776 components retained in PR2829. They are cited dependencies,
not independently audited results of this contribution. No predecessor verifier
is run. Its zero-carry table is used only as a deliberately wrong endpoint
control. Existing source files and credit lines are unchanged.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/carry-two-fourteen-tapes
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/carry-two-fourteen-tapes --check-source-history
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/carry-two-fourteen-tapes/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/carry-two-fourteen-tapes/verify.py
```

Expect `PASS_CARRY_TWO_FOURTEEN_TAPES` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Replay writes nothing. Its generated stdout
report binds the source files and both freshly compiled tables by SHA256.
No manually written receipt is used.

The exact finite evidence comprises 308 directional executions over 93 shapes
and 22,482 payload bits, 18 full-bank sparse/dense interpreter comparisons and
12 additional physical inverse round trips. Both directions execute 1,595,406
transitions in the primary fixtures. These totals exclude the additional round
trips and deliberate failure controls. Every four-bit Boolean payload at Q=2
and every basis column for two Q=3 shapes are included. Other fixtures exercise
independent origin shifts, nontrivial spectators, binary powers and adjacent
values. The independent coordinate oracle gathers preimages without split
logic. Exact costs, head returns, input contents and complete scratch erasure
are checked after every successful execution.

Thirteen controls reject wrong direction, a correct zero-carry endpoint, a
missing second carry transfer, nonlocal movement, changed payload, retained
scratch, noncanonical Q, four invalid compile-time direction values, changed
source bytes and endpoint-preserving unbilled movements. Finite executions
corroborate the written induction; they do not replace it.

## Scope and limitations

This changes the `uniform-transfer-audit` card to a standalone `precision_tape`
compiler component. It supplies no actual selected caller or discharged
framework assumption. Inputs must satisfy the full marked-string shape and
Boolean-payload contract, with distinct roles and initially blank output and
scratch tapes. Arbitrary dirty scratch, invalid-input cleanup, runtime carries,
arbitrary coefficients, in-place owner installation, native realization, full
supplier admission and a new kappa remain unproved here. There is no independent
human or proof-kernel review. The selected frontier is unchanged.

Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362286)
records the exact target. Entry overlap covered 387 open PRs, 6,317 Discussion
records and 8,917 local notes. Separate live PR, merged-PR and all-main README
searches included both general affine controllers and the fixed fourteen-tape
case. This metadata coverage does not prove novelty or cover unpublished work.

## Open next questions

1. Can a real caller allocate this fourteen-role kernel and install its owned
   output without exceeding its complete budget? Start with one named
   coefficient-one, carry-two site and its role lifetimes. No such site or
   installation is certified here.
2. Can the cyclic counter be reused for a general supplied affine offset with
   fewer than nineteen roles? Start with the complete descriptor lifetimes in
   PR5019. Coefficient/offset preparation and cleanup need a new resource proof;
   repeating this fixed-carry code does not supply it.

## Credit

Credit Charles Bethin / cbethin for PR2829's unit-carry interface and explicit
fourteen-role question; David Arias / DavidAriasC for PR2776's machine, counter,
split/merge, cleanup and separate dense interpreter; JoyboyBrian for PR5019's
general affine controller; Jose Manuel and the retained ordered-affine stream
lineage. New code, cyclic-counter construction and proof are produced by Nick
Petalas. Elementary cyclic rotation and split/merge are predecessor methods.
Apache-2.0.
