# PR2530 source-partner cuts and recovery movement windows

**Independent finite audit and scoped retiming certificate; no new supplier or
κ.** Both frozen PR2530 words pass an independently implemented check of their
eight new dirty-lender handoffs. The seven recovery blocks have **1,161 legal
single-block placements per provider** in the precise adjacent-movement model
below. These are individual placements, not 1,161 jointly feasible schedules.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

The claim is in [discussion #2606](https://github.com/CrocSwap/integer-mult-bounds/discussions/2606).

## What is checked

[PR2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530), at
`b4012098048e12500b2d33d2e84be281915a27ac`, restores source partners before using
them as dirty helper storage. Its author checks the complete endpoint. This
package adds explicit intermediate source-row certificates, a reverse
substitution check, and bounded recovery-movement certificates. It does not
import or execute the predecessor's verifier, generator or frame utilities.
Those files were inspected to identify the contract and existing coverage;
this is a separate implementation, not a blind review or independent human
review.

The two original compressed word files are retained byte-for-byte. Their PR
head, original Git blob IDs, source paths and SHA-256 digests are in
[INPUTS.json](INPUTS.json). They come from PR2530's PR2462 supplier
(`ef34071fee6dfb0286e9850a5cec4e36d9eb126d`). Main base is
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

For each word, all **646 live initial roles are independent formal inputs**.
The checker executes precondition, compensation, A, the logical centre cut,
and B, interleaving each B warp at its recorded cut and in table order. Each
warp is a distinct formal invertible operator. Exact rational coefficients
and cancellation of adjacent inverse symbols suffice; there are no floating
point tests, sampled inputs or unverified operator simplifications.

At every new handoff, the lender row is exactly its own original input:

| Removed helper | Lender | Handoff, before B gate | Operator |
| --- | ---: | ---: | ---: |
| 656 | 49 | 1082 | 51 |
| 657 | 83 | 1083 | 52 |
| 658 | 98 | 1084 | 53 |
| 660 | 101 | 1087 | 54 |
| 632 | 68 | 1014 | 55 |
| 648 | 80 | 1062 | 56 |
| 649 | 88 | 1063 | 57 |
| 633 | 31 | 1015 | 58 |

Indices are zero-based. A second interpreter substitutes backward from each
of these eight observations to the initial inputs. It appends operator symbols,
where the forward interpreter prepends them. Both agree on all 16 observations
across the two providers. The complete before/after rows of all nine recovery
gates, six older partner handoffs per provider, frame obstructions and local
commutator witnesses are in [CERTIFICATE.json](CERTIFICATE.json).

## The recovery identities

Write `x_r` for role r's original arbitrary input. The certificate establishes
these actual incoming rows, not just two-coordinate test vectors:

* For `(r,p) = (49,33), (83,74), (98,85), (101,55)`, immediately after the
  inherited recovery of p, the rows are `r=x_p+x_r`, `p=x_p`. Thus `r-=p`
  restores r before p's handoff.
* Before B687, `80=x_80+x_88` and `88=(-x_80+x_88)/2`. B687 performs
  `88+=80/2`, then B688 performs `80-=88`. These give `88=x_88`, `80=x_80`.
  Reversing these two operations fails; the stored control includes the exact
  wrong row at lender 80's handoff.
* Before B971, `68=x_4+x_68` and `4=(x_4-x_68)/2`. The block
  `68/=2; 68-=4` gives `68=x_68` before role 4's handoff.
* Before B973, `31=(-x_12+x_31)/2` and `12=x_12+x_31`. The operation
  `31+=12/2` gives `31=x_31` before role 12's handoff.

The older lenders **4 and 12 are not restored to their own original inputs**
at their handoffs: they retain the mixtures displayed above. This is not a
defect in PR2530. The eight-new-lender invariant must not be imposed on every
older borrowed role. Their inherited compensation contracts are separate.

The formal-row proof is immediate by induction over the instruction stream:
ADD forms the indicated rational row combination, SCALE multiplies the row,
and WARP left-multiplies each term. Equality to the original basis row proves
the observation for arbitrary dirty inputs and every interpretation of the
formal invertible operators. This does not certify a native implementation of
those operators.

## Exact scope of the movement certificate

Fix one of the seven displayed recovery blocks, keeping its internal order,
coefficients and frame annotations. Remove it from the flattened B stream,
which contains both ordinary gates and individual warp events. Keep every
other event fixed. A permitted step swaps this block with one adjacent event,
subject to both conditions:

1. The two linear maps commute, checked by exact free-operator row substitution
   on their union of registers.
2. At the new insertion cut, every incident register already has precisely the
   block's specified frame. A recovery must introduce **no frame climb**.

All nine original recovery gates satisfy this zero-climb condition. Frames
are independently reconstructed as explicit subsets of `F_2^9`, not by the
predecessor's echelon-basis routine. Every relevant chart map is checked for
invertibility and for its exact action on its input subspace.

The result is the maximal connected interval reachable by such adjacent steps
from the original placement. This is not a census of arbitrary jumps across
several noncommuting events, simultaneous moves of several blocks, altered
frames, or resynthesized recovery circuits.

| Recovery block | Earliest cut, after event | Latest cut, before event | Placements |
| --- | --- | --- | ---: |
| `49-=33` | B1034 | warp 47 at B1042 | 11 |
| `83-=74` | B1038 | warp 49 at B1042 | 9 |
| `98-=85` | B1040 | warp 50 at B1042 | 8 |
| `101-=55` | B1036 | warp 48 at B1042 | 10 |
| `68/=2; 68-=4` | B712 | warp 44 at B974 | 272 |
| `88+=80/2; 80-=88` | B686 | warp 56 at B1062 | 406 |
| `31+=12/2` | B542 | warp 46 at B974 | 445 |

Both providers give this same table. Positions between successive warps at
one B index count separately; the certificate records unambiguous event labels
and skeleton-cut indices.

For each interval, the certificate verifies every adjacent crossing and
records the first obstruction on each side. A legal crossing preserves the
entire B map by commutation. Induction proves this for every placement in the
interval. Since no moved recovery changes a frame, the unchanged remaining
events keep their frames and the original transitions. At each endpoint, the
next crossing either has an explicit nonzero **scalar** commutator or lacks
the exact required frame. No nonzero free-operator expression is used alone
to infer a concrete native obstruction. These witnesses prove maximality in
the declared connected-movement model.

There is a useful distinction at the left edge of the source-68 interval.
B712 reads role 4 and commutes algebraically with the recovery of 68. Before
B712, however, role 4 has dimension 3 rather than the required dimension 4.
Moving the block across that boundary adds a climb. The later right boundaries
usually have **equal-dimensional but different** four-dimensional frames;
checking dimension alone would miss them.

These movements preserve the scalar B map, the recovery gate count and the
declared frame trajectory under the stated model. No new physical schedule,
native cleanup program, complete bill or κ gain is claimed.

## Reproduction and controls

Python 3.12, standard library only, normally about 15 seconds for both commands
combined:

```sh
python3 -I -B research/t74-source-partner-cut-audit/verify.py
python3 -I -B research/t74-source-partner-cut-audit/test_verify.py
python3 scripts/research_package.py --package research/t74-source-partner-cut-audit
```

The direct checker prints:

```text
PASS_T74_SOURCE_PARTNER_CUT_AUDIT providers=2 handoffs=16 recovery_gates=18 reverse_cuts=16 movement_windows=14 semantic_rejections=24 no_new_kappa
```

Normal replay reads the certificate and inputs without rewriting them. The
optional `--write-certificate PATH` writes exclusively to a new path.

* Twelve rejecting semantic controls per provider: each of the nine recovery
  operations replaced by the identity, reversed 80/88 order, wrong sign for
  source 31, and premature handoff of source 80.
* Explicit positive noncommuting-operator/inverse and shared-read fixtures,
  including a backward-substitution key-collision fixture.
* Full B-map replay on all 646 inputs for the earliest and latest placement of
  each block: **28 positive relocated streams** across the two providers.
* The immediately adjacent outside placements: **28 rejections** of map-plus-
  zero-climb preservation. Two preserve the algebraic map but fail the frame
  condition, as described above.
* A deliberate coverage control corrupts a target-only prelude ADD. Lender-cut
  checks still pass, while the complete B endpoint changes. This demonstrates
  why the result is not a complete word or supplier verification.

## Limits and relation to other work

Only the **forward logical words of both providers** are audited. The native
inverse-transpose implementations, exact Gaussian phases, cleanup-buffer use,
final restoration, target endpoint, copied paths, local rank ledger, physical
owners, native/global/outer admission, precision and all-size/compiler
obligations are not recertified. The selected result is unchanged.

[PR2571](https://github.com/CrocSwap/integer-mult-bounds/pull/2571) and
[PR2575](https://github.com/CrocSwap/integer-mult-bounds/pull/2575) change owner
packing on these words. [PR2588](https://github.com/CrocSwap/integer-mult-bounds/pull/2588)
changes helper labels and packing; its changed frame bill is a different
obligation. [PR2573](https://github.com/CrocSwap/integer-mult-bounds/pull/2573)
excludes source-partner recovery from its retired-lender exhaustion model.
[PR2315](https://github.com/CrocSwap/integer-mult-bounds/pull/2315) audits the
older borrow43 record and buffer accounting. This package does not duplicate
their root, owner, exhaustion or storage claims. The concurrent
[discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612)
searches new source-partner assignments; this audit keeps the PR2530 words fixed.

## Open next questions

* **More general lender contracts.** Can the same cut checker verify prescribed
  invertible mixtures, such as the actual older roles 4 and 12, against their
  compensation terms? Start with those two explicit rows and derive the
  required target correction symbolically. The missing piece is a complete
  correction/cleanup contract, not the input-row reconstruction.
* **Larger jointly recoverable source spaces.** The pair certificates identify
  precisely which reads and frames constrain recovery. For one proposed
  three-source replacement, first supply its exact inverse rows and candidate
  cut, then check availability and price every changed frame. A complete
  changed word and native/global admission remain necessary before claiming
  fewer helpers or a better supplier.

Structured scope, stop rule and follow-ups are in [TASK.json](TASK.json).

## Credit

The source construction and original checks belong to zxv / PR2530, with
substantial OpenAI Codex assistance. Jeremy Kothe / PR2462 supplies the combined
T74 words and inherited pipeline; Tekalign (@tekuuu) / PR2436 supplies lifted
target borrowing and transport; Vlado Vojdanovski / PR2322 supplies coherent
handoffs; Cinna Davis (@1337isnot1337) / PR2226 supplies anticipatory dirty
borrowing. The PR1297/PR1319 and earlier provider lineage retains its credit.
The immutable input words remain Apache-2.0. New independent implementation,
cut certificates, movement proof, tests and writing were prepared for
commdata2338 with substantial OpenAI Codex assistance. No independent human
review or formal proof-assistant verification is claimed.
