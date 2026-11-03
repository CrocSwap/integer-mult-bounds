# Two nonnested capacities for one prescribed linear map

A prescribed injective map h:U→W extends to an isomorphism g:V→W satisfying
both g(A)⊆C and g(B)⊆D exactly when seven stated compatibility/capacity tests
hold. V and W may be any equal finite dimension over any field. A,B,C,D are
arbitrary subspaces; target nesting is not required.

This answers the first open question of Nick Petalas's PR6489, whose theorem
covers nested target flags. The additional condition measures a coupled
quotient map, not merely the dimensions of the two capacities separately.
The all-field result rests on [PROOF.md](PROOF.md); exact finite checks provide
corroboration. No general literature-priority claim or new kappa is made.

## The missing condition

Put E=h(U), UA=U∩A, UB=U∩B, U0=U∩(A+B), and Z=(E∩C)+(E∩D).
First require h(UA)⊆C, h(UB)⊆D, h(U0)⊆C+D and the three natural individual/
sum quotient-dimension capacities. Then the additional necessary and
sufficient inequality is

    dim(A∩B)+dim(h(U0)∩Z)−dim UA−dim UB
        ≤ dim(C∩D)−dim(E∩C∩D).

The left side is the kernel dimension of the coupled map
J=((A+U)/U)∩((B+U)/U) → (E∩(C+D))/Z,
a+U=b+U ↦ h(a−b)+Z. The right side is dim π(C∩D) in W/E.
An injective common lift exists exactly when this kernel fits that space.
The proof extends the lift across the remaining quotient and ambient bases.
The software checks the criterion; it is not a general-field constructor.
No formula counting every nonnested completion is supplied.

## A genuine oblique obstruction

In F³ fix U=<e1,e2> pointwise and request

    A=<e1+e3>  → C=<e1,e3>,
    B=<e3>     → D=<e1,e2+e3>.

The ordinary individual, sum, intersection and common-quotient capacity tests
all pass, as do the prescribed-image compatibilities. Yet any joint map would
send e3 into C∩D=<e1>, collapsing it into the already prescribed image. The
coupled map has a one-dimensional kernel and no target kernel space.

The reverse calibration has F², U=<e1−e2> fixed, A=C=<e1>, B=D=<e2>.
The identity works although J has dimension 1 and π(C∩D)=0: the coupled map is
injective. Requiring all of J, rather than its kernel, to fit would be wrong.

## Exact finite evidence and reproduction

Use CPython 3.12 and the standard library:

```sh
python3.12 -I -W error -B research/two-capacity-prescribed-completion/verify.py
python3.12 -I -W error -B research/two-capacity-prescribed-completion/oracle.py
```

Repeat with `-O`. Strict defaults require retained receipts; `--emit` prints
candidates without overwriting files. Both programs authenticate the two inert
predecessor documents before reading them, and execute no predecessor program.
The primary uses row reduction, annihilator intersections and quotient ranks;
the separate checker constructs literal vector sets and enumerates all GL
matrices in the declared finite domains. No primary code is imported by it.

For each rank r, normalize h to the identity on the first r coordinates and
vary all four subspaces. Independent domain/codomain basis changes put every
partial injection into such a frame. The census therefore covers every
instance in the stated finite domains up to those changes; it does not count
every differently labelled h. Domains are F2 dimensions 0–3 and F3/F5 dimension 2.
Membership-mask ordering and one raw0/1 byte per decision are documented in the
receipts. Counts/digests identify complete finite transcripts, not an all-field
proof or formal-kernel acceptance.

## Retained finite census

The two different engines agree on 280228 normalized capacity decisions, of
which 62153 are feasible, including every per-rank raw decision transcript.

| Field | Dimension | Subspaces | Cases across prescribed ranks |
| --- | ---: | ---: | ---: |
| F2 | 0 | 1 | 1 |
| F2 | 1 | 2 | 32 |
| F2 | 2 | 5 | 1875 |
| F2 | 3 | 16 | 262144 |
| F3 | 2 | 6 | 3888 |
| F5 | 2 | 8 | 12288 |

Seven actual omission controls each delete one of the seven tests, produce a
false positive, and are rejected by literal GL enumeration. The oblique 3D
fixture has 2/6/20 individual completions over F2/F3/F5 but zero joint
completions; the prescribed extension pools have 4/18/100 members. The
nonzero-coupled-map calibration has exactly one joint completion (the identity).
Those are named finite counts, not a general nonnested count formula.

## Source, task and credit

Canonical base 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority 8, selected PR6030.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19365420).
PR6489 head fdb7b8808ce89cd1738ea49dcd65c19ae1dddedd and its README/PROOF are
byte-pinned. The 478-open-PR cache, current1166claims and bounded all-state
prescribed-map/nonnested searches were checked. The separate6471 flag-defect
and binary symplectic rank-two claims concern different contracts. Hidden/
unpublished work, arbitrary diffs and sparse historical notes remain unknown.
The submission refresh found Ali Romman's [PR6533](https://github.com/CrocSwap/integer-mult-bounds/pull/6533),
head efa89adc2c71f1ef57228111639e1c8fc48393e3. Its earlier claim and
finite-field theorem already cover arbitrary simultaneous targets, all matrix
ranks and fixed images through exponential affine/kernel-lattice counting.
Its documented next question asks for a faster restricted nonnested criterion.
This result supplies a closed seven-test criterion for TWO targets over EVERY
field, including infinite fields, with a direct quotient-lifting proof. It does
not claim the first nonnested completion result or a new general count. The
finite existence checks overlap the general finite-field scope of PR6533; no
PR6533 program or receipt is imported, executed or used as expected output.
The original 478-body snapshot and then-current Hub view missed this adjacent
advance claim; the prepublication refresh caught it. The scientific inputs,
code and receipts remain frozen; this is a documentation/credit correction.
The formal-interface card is explicitly changed to this algebraic side lemma;
no Lean or selected-assumption discharge is claimed.

ToikY with substantial OpenAI Codex assistance, Apache-2.0. Credit Nick Petalas/
6489 for the nested theorem and explicit next question; Brian/JoyboyBrian/5020
for the one-capacity contract; Cao Yifan/intqwq/4610 for native-map caller
context; Nick Petalas/4919, codyw912/4735, Cinna Davis, Dugongue, zxv,
Jacob Alan Sussman and the retained native/compiler lineage. Quotient spaces,
linear lifting and basis extension are classical. Exact original notices remain.
Ali Romman/PR6533 retains the earlier general finite-field counting and
fixed-image compression result. Separate AI implementation/review is not independent human acceptance.

## Open next questions

- Derive a two-target count formula avoiding the general kernel-lattice census.
  PR6533 already counts every finite-field completion by a general exponential
  method. Fix the coupled map and lifting freedoms to seek a simpler formula.
- Determine what additional compatibility is needed for three nonnested targets.
  PR6533 covers finite-field counting, but no closed all-field criterion is
  supplied here. A third target can couple choices left free here. Begin with one explicit
  arrangement and a discriminating obstruction; this theorem does not cover it.
- Bind one actual shared native operator and all its source/image conditions.
  Symplectic constraints, absolute phases, causal access, dirty restoration,
  basis preparation, delivery, productive debits and the complete paid/native/
  precision/stock/tape/compiler/outer invoice remain open. All five selected
  assumptions and the selected frontier retain their status.
