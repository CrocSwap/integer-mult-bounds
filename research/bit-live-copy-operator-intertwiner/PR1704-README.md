# Two live copies reduce the fixed PR1062 scatter by 120 ADDs

**Finite scalar construction and a replacement copied-workspace contract; no
new kappa or admitted supplier.** On Sagar Thakrar's pinned PR1062 word, four
disjoint pairs of retained copies reduce scatter work from **527 to 407 ADDs**,
including preparation and restoration. The complete word falls from **11,500
to 11,380 ADDs**. The maximum saving is exactly 120 in the explicitly defined
pair/singleton block class: all 2,620 partitions were checked, with 105 optima.
This is not an optimum over arbitrary two-temporary circuits.

The change needs **two simultaneously live copied temporaries instead of one**.
It preserves all nine rank-seven COPYs and every persistent register's frame
path. Its local recursive profile is unchanged, and its reverse positive bound
increases. Thus it supplies an interface construction and scalar saving, not a
structural improvement to the selected recursive budget.

## Boundary contract and proof

The inherited exporter sends each retained total from its current frame to a
fresh temporary at **ZERO**, performs target ADDs at ZERO, then erases the copy.
Its native legality checker requires a single live temporary and forbids writing
that temporary while it is live. The proposed extension allows two disjoint
fresh copied slots and temporary writes at ZERO, with these obligations:

1. Original centers, their frames, and all other persistent registers except
   the specified targets remain unchanged during the scatter block. Snapshot
   creation depends only on its unchanged center and preserves other live state.
2. Both copied values and the affected targets are in the same ZERO-frame
   module. There are no new frame moves, source reads, resets, or hidden roles.
3. Every ERASE sees **exactly the value that its own immutable original COPY
   produced**. Both slots are closed at the block boundary. Eventual restoration
   after an ERASE is insufficient.
4. Two simultaneously live COPY outputs are available without aliasing either
   each other or the implementation's private workspace. This is an explicit
   physical-admission obligation, not a consequence of the scalar proof.

Let the original two snapshots be arbitrary values `a,b` in an F2 module and
their target sets be `A,B`. All target values are arbitrary. Create `p=a,q=b`;
add `p` to targets in `A\B` and `q` to targets in `B\A`; perform

```text
p += q
for t in A intersect B: y[t] += p
p -= q
ERASE p against its original center
ERASE q against its original center
```

The two signs coincide over F2. The signed form also proves this local block
over every module over a commutative ring: after the second shear `p=a,q=b`;
each target receives exactly its old increment, and neither original center
changes. It follows pointwise for arbitrary compatible streams, not just finite
scalar test inputs. The argument treats `a,b` as the *outputs* of their snapshot
operators; it does not equate different frame operators.

Different blocks only add to targets and restore their workspace, so their
order is immaterial at this boundary. The unchanged B/C continuation receives
the same persistent state and frames as before. This is a local substitution
lemma conditional on the stated COPY implementation contract. It does not
establish the availability, tape layout, or precision of two physical copies.

The old native checker is preserved. Its single-copy state and explicit
`copied source or temporary mutated inside COPY window` rule exclude the new
stream. We inspect and pin that code; no native acceptance or executed native
rejection is claimed. The PR1062 D prefix is also unchanged: its known H2/K
syntax failures remain, with the separate semantic bridge credited to PR1194.

## Exact restricted optimum

For one pair, the complete scalar bill is

`|A| + |B| - |A intersect B| + 2`,

so its saving is `|A intersect B| - 2`. A singleton uses the original schedule.
The class permits every partition of the nine labeled totals into disjoint
singletons and pairs, using exactly this block for each pair and one COPY/ERASE
per total. It permits no reuse of a total between pairs, retained sum between
blocks, target basis changes, or extra COPYs.

The chosen lexicographically first optimum (no precision-based tie search) is
`(0,3), (1), (2,4), (5,7), (6,8)`. Index `i` denotes register `472+i`.
All four intersections have size 32, giving `4*(32-2)=120`. The receipt contains
the complete intersection matrix and saving distribution. A separate subset
dynamic program reproduces that distribution without enumerating partitions.
The exhaustive checker also verifies the full dirty scatter boundary for
**every one of the 2,620 partitions**, not only the best witness.

## Complete local accounting and its boundary

| Quantity | Pinned PR1062 | Two-copy candidate |
| --- | ---: | ---: |
| Persistent registers / independent dirty input columns | 661 | 661 |
| Peak live copied temporary slots | 1 | 2 |
| Peak sum of live COPY ranks | 7 | 14 |
| COPY / ERASE events | 9 / 9 | 9 / 9 |
| COPY rank sum | 63 | 63 |
| Scalar scatter ADDs, including prepare/restore | 527 | 407 |
| Complete scalar ADDs | 11,500 | 11,380 |
| Persistent nested MOVEs | 2,911 | 2,911 |
| Local recursive child rank mass | 5,129 | 5,129 |
| Forward positive bound F | 25,717 | 25,717 |
| Reverse positive bound B | 5,911,840 | 6,248,884 |
| Bits in `64 F^3 B^2` | 95 | 96 |
| Bits in `2^18 F^5 B^4` | 182 | 182 |

The profile is exactly `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` for both.
All added scalar work is at ZERO and already included in the ADD total. The
two temporary slots are fresh COPY destinations; no arbitrary dirty initial
contents of those newly allocated slots are assumed to vanish for free.

The positive majorants use absolute ADD coefficients, including the negative
restoration shear, and literal reversed COPY/ERASE streams. The exact inherited
expressions are strictly below `2^104` and `2^192`. These are **algebraic guard
checks**, not a migrated native/physical precision invoice. Extra simultaneous
workspace, its hosting and routing, and any changed compiler constants still
need pricing. At the fixed incumbent normalization, even granting that workspace
and all scalar changes for free leaves the local recursive moment identical;
no gain follows from the 120-ADD reduction alone.

## Reproduce and evidence

Standard library, Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/bit-two-copy-scatter
```

The registered commands run the primary checker, separate implementation, and
nine test groups (including optimized Python). Expected markers:

```text
PASS_BIT_TWO_COPY_SCATTER ADDs=11500->11380 partitions=2620 optima=105 ... no_new_kappa
PASS_TWO_COPY_INDEPENDENT columns=661 directions=2 integer_lifts_equal ...
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-two-copy-scatter outcome=completed
```

`verify.py` uses packed binary rows and rational elimination. `independent.py`
imports no primary or predecessor executable code; it uses individual integer
input columns, subset dynamic programming, and fraction-free frame ranks. It
checks equality of the two full **signed integer lifts** in both directions,
then their desired F2 endpoints. It does not claim that either full integer
lift is itself the multiplication supplier's physical map. Both implementations
were written with the same AI assistance, not independent human review.

Controls reject all eight temporary-gate omissions, omitted target work,
restoration after ERASE, a mutated original center, wrong ERASE center, occupied
or inactive copied slots, non-ZERO operands, unpriced frame moves, a wrong
integer restoration sign, and undercounted preparation. Six receipt corruptions,
duplicate/nonfinite JSON, source corruption, and a read-only relocated export
are exercised. The ordinary verifier only compares its regenerated in-memory
receipt; `--emit NEW_PATH` explicitly creates a receipt and refuses overwrite.

No selected-construction cold replay, native two-copy compiler, hosted invoice,
outer assembly, all-size realization, tape/rounding, analytic transfer, Lean
theorem, or hosted CI pass is supplied. The selected record and frozen sources
are unchanged. This is a reviewable partial interface construction.

## Scope, overlap, and credit

Base: `5e554ff58d01921747d27177045c0061f31e1ad1`; selected conditional #1094,
κ `0.001672660197076918`. The helper's one OS-random nonce was
`ffd7509ee115bd599b3ebe2151ecdd39`. [TASK.json](TASK.json) explicitly records
the change from the assigned H2/K question to the copied-temporary contract.
[Discussion 1687](https://github.com/CrocSwap/integer-mult-bounds/discussions/1687)
contains the claim and final result. Exact Git/SHA256 inputs and predecessor
heads are in [SOURCES.json](SOURCES.json); overlap coverage is retained in the
[OVERLAP.json](OVERLAP.json) receipt. Search results are not proof of novelty.

Sagar Thakrar / thakrarsagar supplied the PR1062 B/star word at
`cd016e5dcd5ba28dafa3f3b4eeef003a38e6a11b`; its existing 11,500-ADD result is
not new here. Credit PR967 / theon199 helper stars; Gareth Davidson's PR926
pairs; Aaron Wang's PR1015 B blocks; Ross Richardson's PR923 block;
DreamingOfClouds' PR589 and eumemic's PR555 bit word/checkers; Dylan Crow's
exporter and native-checker adaptation; and the earlier restored-sharing
mechanism, including Sagar Thakrar's PR708.

woklerx's **live-COPY stabilizer** requires an unchanged snapshot at an ERASE
cut. We retain that equality and add reversible writes to the copied slots,
not unpaired original-helper mutation. His **late retained-total mixing**
raises original helper frames; those helpers are immutable here, and mixing
occurs on their ZERO-frame outputs instead. PR1194 supplies the separate
zero-frame D substitution. The pair-sum identity is standard; the contribution
is its precise copied-workspace contract, fixed-word application, complete local
accounting and restricted optimum. No claim of literature priority is made.

Prepared by Ross Richardson with substantial OpenAI Codex assistance in
reasoning, code, testing and prose. Apache-2.0; all source licenses and notices
are retained. No subagents or independent human review were used.

## Open next questions

Can a two-slot emitter and actual physical COPY implementation satisfy the
noninterference and restored-value contract? This matters because the finite
scalar word alone cannot be adopted. First implement the two temporary roles
in a separate native checker and price their concurrent workspace before a
full replay. The blocker is native lifecycle/workspace admission and inherited
physical/analytic obligations. Because the recursive profile is unchanged,
this is a compiler/scalar-efficiency question, not a pending kappa improvement.
The structured version is in [TASK.json](TASK.json).
