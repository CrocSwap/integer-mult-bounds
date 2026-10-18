# Fixed-bank scratch cannot reuse the zero-retention decoder's outputs

For the unchanged PR2707 zero-retention QQ16 word, **sixteen additional
owner-local payload arrays are necessary and sufficient in the fixed binding
model below**. None of its 224 output banks can hold a private scratch field
for that field's complete charged lifetime. This closes one allocation question;
it is not a universal memory lower bound or a complete physical caller invoice.

PR2651's retained decoder has a different answer. The existing
[output-slice refinement](../qq16-output-slice-scratch/PROOF.md) reuses unproduced
W output slices because both scalar bodies finish before W construction.
PR2707 initializes W earlier, and some later output rebuilds precede scratch
cleanup. Matching the final logical outputs does not transfer that allocation.

## Exact allocation contract

Fix one owner and its payload extent. The caller keeps 224 named Z/W output
banks at fixed, mutually disjoint slices, and 224 borrowed X/Y banks are
unavailable for scratch. All final outputs survive until delivery after the
word. Owned entry dirt is disposable. The caller grants the same writable,
correctly ordered owner-slice access required by the predecessor refinement;
providing that access is a separate physical obligation.

Each F/G field receives one constant slice binding for each private scope,
from its first initializing CLEAR through its final cleanup CLEAR, inclusive.
Bindings may change between scopes. A scratch field can occupy an output
slice only if that output has no intervening access and its old value is
already dead: the next output access must be a destructive CLEAR strictly
after the complete scratch lifetime. Distinct overlapping private lifetimes
require disjoint slices. Scalar values, zero values and frame labels do not
permit coalescing simultaneous logical fields in this model.

The word, including cleanup, stays in its literal order. This result excludes
migration, spilling/copying, moved CLEARs, recomputation, different output
bindings, early consumption, compressed/encoded states and value-dependent
aliasing. These are possible changed hypotheses, not excluded architectures.
There is no claim that the original decoder or the retained refinement promised
zero extra scratch for this different word.

## Source-bound obstruction and proof

The input is [ywz65's PR2707](https://github.com/CrocSwap/integer-mult-bounds/pull/2707)
at `efa51a6c7ffec6edd556a98deedfe9deeba65809`. [WORD.json](WORD.json) is its
byte-exact 3,823-event word, SHA-256
`5623b9cd62635d47f84e78135d817cfddec7ae31c154c565bf6e16cf5ed75475`.
Indices below are zero-based. The checker authenticates this snapshot before
parsing its instructions and imports no predecessor executable.

For each fixed output bank, a disposable gap lies strictly after its last
touch and strictly before its next CLEAR. Initial disposable dirt gives a gap
before its first CLEAR. There is no gap after its final touch, since delivery
reads the final output. Enumerating consecutive touches and subsequent CLEARs
therefore gives every gap allowed by the stated allocation contract.

A scratch binding is legal exactly when its complete closed interval fits
strictly inside one such gap, and it does not collide with another scratch
binding. Both directions follow directly from preservation of the old output
until its last access, absence of output accesses during the scratch interval,
and the later CLEAR discarding the scratch value before output use resumes.
The contract requires these exclusive intervals even when a particular input
would make one of the values zero.

[RESULT.json](RESULT.json) lists every gap and all 32 scratch lifetimes. For
`0 <= i < 8`, the latter have these exact endpoints:

| Private scope | Scratch interval, inclusive | Latest next-CLEAR among output gaps |
| --- | --- | --- |
| B1 current query, markers 696/1593 | F_i: [697+57i, 1585+i] | Eight noninitial W gaps end by 1579. |
| Future logger inverse, markers 1938/2403 | F_i: [1939+53i, 2395+i] | No noninitial gap intersects this scope. |
| F0 inverse, markers 2853/3806 | F_i: [2854+10i, 3790+i]; G_i: [2855+10i, 3798+i] | Sixteen noninitial Z gaps end by 3785. |

All initial gaps end before the first scope starts. Checking every lifetime
against every output gap gives **zero legal scratch/output pairs**. Thus all
scratch lifetimes require additional private slots in this model. In the final
scope all sixteen intervals contain event 2925, so at least sixteen slots are
required. Sixteen suffice: bind F_i to P_i and G_i to P_(8+i), reuse P0..P7 in
the earlier disjoint scopes, and retain all literal initialization/cleanup.
This is an explicit allocation upper bound and a matching interference lower
bound, not an information-theoretic dimension argument.

Two concrete failures explain why checking only data reads is insufficient:

- Directly transplanting F0 -> W0 fails at event 697, `CLEAR F0`. It erases
  live W0, and event 698, `F0 += W0`, becomes a self-ADD on the cleared bank.
- F4 -> Z76 in the final scope passes a last-data-read test. F4's first
  CLEAR is at 2894 and its last data use is at 3746, inside Z76's gap
  [2887,3765). But Z76 is rebuilt at 3765..3769, and F4's literal cleanup
  CLEAR at 3794 would erase the completed output. Moving that CLEAR changes
  the hypothesis and needs a new allocation proof.

The existing [PR2807 finite-format bound](../qq16-finite-dyadic-format/README.md)
already supplies `2*464*N*D*W` data bits for 224 borrowed arrays, 224 outputs
and sixteen private arrays, with W its sufficient signed component width.
This contribution does **not** improve that count. It proves why the sixteen
extra slices cannot be removed by this particular fixed-binding reuse method.
Arithmetic scratch, permutations, addressing, movement, entry encoding and
output consumption are additional obligations. Local owner scratch can be
reused sequentially across owners when the caller supplies that schedule;
this proof neither requires nor proves sixteen additional full-cover banks.

## Reproduce and evidence

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-fixed-scratch-allocation
```

The registered replay runs normal and optimized verification and five test
groups. The direct check also works in a Git-free export:

```sh
python3.12 -Werror -I -O -B research/qq16-fixed-scratch-allocation/verify.py
```

Expected output is
`PASS_QQ16_FIXED_SCRATCH_ALLOCATION lifetimes=32 alias_edges=0 minimum_extra=16 no_new_kappa`.
Default verification is read-only. `--write` creates an absent RESULT.json
and refuses overwrite. Exact main source bindings are in [SOURCES.json](SOURCES.json).

The accepting fixture uses sixteen private slots. Six rejecting allocation
controls cover the two illegal output aliases, a borrowed bank, overlapping
private slots, fifteen slots and an omitted binding. A separate forward-access
oracle checks all 32 x 224 candidate bindings without constructing gaps; an
initial-dirt toy word supplies its positive alias control. Tests also exercise
missing initialization/cleanup, scope/schema errors, source drift, changed and
Boolean receipt values, duplicate keys, missing/oversized receipts, read-only
Git-free replay and exclusive deterministic regeneration. The scalar examples
illustrate alias corruption; they are not a replay of the complete native
operator or the multiplication theorem.

Power of Ten scope: verification traverses the fixed 3,823 events, 464 names,
32 lifetimes and at most 312 gaps. No recursion, solver or network is used.
Each JSON read is capped at 200,000 bytes. Rule 3 has a managed-runtime
deviation because Python allocates integers and collections during checking;
the fixed input and traversal limits bound live work. Peak memory is measured
in the verification record below. Rule 9 has one test-only dynamic import
with the single explicit local verify.py target. Rule 10 uses warning-as-error
normal/optimized replay and compilation; no static type checker or physical
integer build is claimed. A larger word requires a successor capacity review.

## Open next questions

Can a changed cleanup schedule or an explicit paid migration reuse a Z dead
window in PR2707? Start with F4/Z76 above, move its cleanup before event 3765
and prove every alias, frame and ownership obligation before pricing physical
access. The current fixed binding theorem does not decide that changed model.
A new implementation round still needs a pinned caller and complete favorable
budget; this result does not authorize an unpriced optimization campaign.

Can an actual caller supply those writable owner slices while paying native
and map movement, arithmetic workspace, entry precision and final consumption?
Start with its physical layout and full boundary ledger. Those unpriced
obligations block supplier admission. The family decision is narrow and stop
at this allocation result. No selected-frontier or kappa claim is made.

## Credit and verification record

New source-bound allocation proof and checker by Nick Petalas, Apache-2.0.
Credit ywz65/PR2707, Arham Tahir/PR2681, commdata2338/PR2651 and ywz65's
output-slice scratch refinement for the different retained word. Nick
Petalas/PR2807 supplies the existing finite-format count. Ali Romman,
starship-s, Sagar Thakrar, Ross Richardson and the retained QQ16/native lineage
retain their predecessor credit. No predecessor mathematics or native identity
is claimed as new. Frozen sources and the selected record remain unchanged.

Local verification on macOS arm64, CPython 3.12.15: registered normal and
optimized replay plus all five artifact/behavior groups pass. The same tests
pass under optimized CPython 3.14.8. Warning-as-error compilation and Ruff
E4/E7/E9/F/B/I/UP/SIM checks pass. A fresh tracemalloc measurement of the primary
verification call peaks at 1,347,353 bytes; this is a local measurement, not a
cross-runtime memory guarantee. Separate internal source and artifact reviews
check the result; no independent human, formal-kernel, full native-semantic
or selected cold replay is claimed.
