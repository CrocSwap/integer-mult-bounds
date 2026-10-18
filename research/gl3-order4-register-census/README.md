# Two order-four GL3 targets need eight coordinate-CNOT calls

**Finite minimum certificate; no new kappa.** On exactly two arbitrary-input
registers, the formal target `diag([h],[h])` requires exactly **eight** paid
coordinate-CNOT calls, where

```text
h = [[0,1,0], [0,0,1], [1,1,1]] in GL_3(F2).
```

All six directed coordinate CNOTs are allowed, and all scalar `GL_2(F2)`
register mixing is free. The address matrix has order four,
`rank(h-I)=2`, and direct coordinate-CNOT length four. Its coordinate dependency
graph contains the cycle `0 -> 1 -> 2 -> 0`; no address coordinate is a spectator.
This answers one concrete instance of [PR #1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414)'s
second open question. It does not establish a general direct-sum bound.

## Model and evidence

Work in the formal group algebra `R=F2[GL_3(F2)]`. A paid unit is
`I+([g]+1)N`, where `g=I+E_ij`, `i!=j`, and `N=uv^T` is a binary rank-one
idempotent (`v^T u=1`). There are six address labels and six scalar projectors,
hence 36 paid generators. Every occurrence, including an undo, costs one.
Free scalar basis changes normalize away by augmentation. No free address
maps, extra registers, clean allocations, copies or erasures are allowed.
Both role inputs are arbitrary and the complete formal output is prescribed.

The direct chronological address word is
`(1<-1+0), (0<-0+1), (2<-2+1), (1<-1+2)`.
Execute it first on scalar projector `E_00`, then on `E_11`: eight paid calls,
no additional roles, no scalar basis changes and no omitted restoration bill.
Its full formal coefficients and all **336 columns** of the faithful regular
representation agree with the target.

For the lower bound, map formal labels to their natural three-dimensional
matrices. This gives an **exclusion-only** six-dimensional matrix relaxation.
Two separately implemented exact traversals agree on every matrix in every
layer through radius four:

| Distance | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Distinct natural matrices | 1 | 36 | 816 | 14,694 | 225,528 |

The radius-three and radius-four balls contain 15,547 and 241,075 matrices.
There are **zero** target meets, excluding every word of length at most seven,
including odd lengths. Each traversal expands 559,692 directed transitions.
No sign/parity argument from the six-element `GL_2(F2)` group is reused.
The direct address census covers all 168 `GL_3(F2)` elements with distance
layers `1,6,24,51,60,24,2`.

[PROOF.md](PROOF.md) explains normalization, complete finite coverage,
the one-way use of the natural representation and the formal upper bound.
[EXPECTED.json](EXPECTED.json) records exact layer hashes, the witness and
15 semantic/scope controls. A four-term nonzero group-algebra perturbation
has zero natural image and zero augmentation; it demonstrates why a natural
*match* would not certify a formal identity.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3 -I -B research/gl3-order4-register-census/verify.py
python3 scripts/research_package.py --package research/gl3-order4-register-census --check-only
python3 scripts/research_package.py --package research/gl3-order4-register-census
```

Expected direct output:

```text
PASS_GL3_ORDER4_REGISTER_CENSUS minimum=8 registers=2 address_group=168 direct_length=4 natural_short_words=0 regular_columns=336 controls=15 no_new_kappa
```

The registered hook runs the certificate and seven focused tests. Those tests
check all 1,296 two-generator formal/natural comparisons, all scalar
conjugations, faithful regular rejection, source corruption and receipt
corruption, including the real CLI under optimized Python. `--emit` computes
a fresh receipt on stdout; normal replay reads and compares the entire committed
receipt. It does not regenerate artifacts. Layer hashes encode sorted packed
36-bit row matrices as five little-endian bytes each.

The independent engine enumerates all 512 candidate address matrices and all
16 scalar matrices, uses dense row tuples in register-major order and right
multiplication. The primary engine uses rank-one factorizations, packed
coordinate-major rows and left multiplication. Entire distance-layer sets
are compared after an explicit index conversion. Each engine also performs
its own target-intersection test, with independently obtained inverse data.
They were written in the same research session; this is implementation
cross-checking, not independent human review.

## Task, overlap and limitations

Base `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`; card
`bit-new-register-model`, scope key `7f5f4426ef796683c485`, priority revision 2,
nonce `b4841db8408c803fc7a3fb9693192ecf`. The claim is in
[discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18912727).
[TASK.json](TASK.json) records the scoped question and overlap check.

This account's PR #1414 (`9e1640094f649ba6db9742796825a8d6c238989b`) treats
order-two swaps in a two-coordinate alphabet. Gareth Davidson's PR #1333
(`7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`) permits all affine rank-one
address operations, giving a different rank-based bill. Concurrent work in
#1317 on a third address coordinate for order-two swaps, and on central
commutators in `UT_3(F2)`, has different targets and alphabets. No pending
implementation is imported or required for replay.

The result is confined to this target, six-label alphabet and **exactly two
scalar registers**. Additional arbitrary dirty registers are unexamined.
The changed formal nonabelian model does not reduce rational frames modulo two.
Physical/compiler/common-label/hosting, precision/tape and analytic admission
are unrun. There is no selected-supplier cold replay, Lean proof, full
multiplication theorem or exponent improvement. The selected record and
frozen sources are unchanged.

## Open next questions

1. **One extra restored dirty scalar register.** This tests whether the
   two-role obstruction survives a genuine workspace expansion. First build
   the 168-generator nine-dimensional natural relaxation for the same `h`
   and seek a short path; certify any positive path formally. Radius-four
   growth is the immediate resource blocker, and an empty smaller search
   would not settle the question.
2. **A structural lower bound for this target with arbitrary register count.**
   This would replace the finite role restriction. Start by identifying an
   invariant that assigns at least eight total charges to the two order-four
   outputs. The rank floor is only four and the sign-quotient argument
   of PR #1414 does not apply here; the present finite census supplies
   no universal proof.

## Credit and license

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit Gareth Davidson (@bitplane), PR #1333, for the restricted-alphabet
question and augmentation normalization; this account's PR #1414 for the
concrete higher-dimensional follow-up; eumemic (PR #288), Ali Romman
(PR #468) and David Govea (PR #720) for the surrounding register-model
lineage. No general rank-method or literature-priority claim is made.
New work is Apache-2.0; all predecessor files and notices remain unchanged.
