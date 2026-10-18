# One E4 call fills four T37 gaps

This construction changes one of the 333 local invocations in PR942's T37
construction. It reverses one four-helper entrance-promotion group, then
moves the four enlarged helpers into four existing unit gaps. The nominated
outer exponent is

\[
\kappa=0.001661961039655941,
\]

an increase of `0.000000000491941994` over PR942's
`0.001661960547713947`. Both figures use the repository's retained conditional
integer-multiplication framework, whose running-time claim is
\(T(n)=O(n(\log n)^{1-\kappa})\). The complete local finite replay passed on
2026-10-13. The inherited assumptions listed below remain open.

The reference checkout is
`407d52ff15b2217b6e22bce44728b4c3907b6515`.
[SOURCES.json](SOURCES.json) pins the dependencies. This package supplies a new
local supplier and its complete owner assignment; it does not change the
selected-result pointer.

## The local change

Start with the U8 word admitted by PR869/870 and used by PR942. For registers
635, 637, 638 and 639, replace the entrance frame
`[272,144,96,6,1]` with `[272,144,96,6]`. Make the same replacement in B-section
gates 456 through 467. These are the twelve gates of the corresponding
group in BlockInvert's `p6n-k4` promotion recipe. Every scalar gate, coefficient, endpoint and other
frame stays fixed. The exact before/after records are in
[LOCAL-EDIT.json](LOCAL-EDIT.json).

The four helpers have indices 411, 413, 414 and 415 after subtracting the
224 data registers. Each helper's residual width changes from four to five.
The residual width is the final dimension minus the entrance dimension.
The resulting local paid profile is

| Rank | U8 | Modified call |
|---:|---:|---:|
| 1 | 2548 | 2540 |
| 2 | 338 | 346 |
| 3 | 446 | 450 |
| 4 | 162 | 158 |
| 5 | 72 | 72 |
| 8 | 8 | 8 |

The helper-width inventory changes from
`{4:80, 5:32, 7:54, 8:122, 9:216}` to
`{4:76, 5:36, 7:54, 8:122, 9:216}`. The local paid rank mass increases by
four. The unchanged native checkers must verify the new frames, both scalar
orientations, all 728 columns, restoration of arbitrary dirty helpers,
normalized residual wrappers, coefficient prefix and all phase recipes.
An unchanged scalar word by itself would not establish those obligations.

## The four owner exchanges

Only call `(stage 0, replica 0)` uses the modified supplier. Exchange its
helpers with helper 454 in calls `(1,3)`, `(1,11)`, `(1,24)` and `(1,32)`,
respectively. The latter four helpers previously occupied width-four slices
in rank-32 children with total occupancy 31. The enlarged width-five helpers
fill these four children completely. The displaced width-four helpers fit
the original width-four positions.

| Enlarged helper | New owner replica | Idle child | Port | Former holder's call |
|---:|---:|---:|---:|:---|
| 411 | 4 | 6 | 0 | `(1,3)` |
| 413 | 12 | 6 | 0 | `(1,11)` |
| 414 | 25 | 6 | 0 | `(1,24)` |
| 415 | 33 | 6 | 0 | `(1,32)` |

Offsets in the affected children are repacked as contiguous prefixes.
[OWNER-EDITS.json](OWNER-EDITS.json) specifies all 20 changed role records,
including these offset changes. All 167,832 roles remain whole helpers.
The invocation order and the 37-replica bank envelope are inherited from
PR942. Actual bridge-aware idle windows, distinct families within each
invocation, disjoint slices, and residual/spectator charts must be checked
for the emitted mixed construction. Bin capacities alone do not prove the
schedule legal.

The remaining idle profile is `{1:2, 48:11086}`. Thus the global paid profile
is

```
{1:848478, 2:112562, 3:148522, 4:53942,
 5:23976, 8:2664, 48:11086}
```

It has rank mass 2,408,256 on 33,152 live families, retaining deficit 11,840.
The physical stock is 33,666 families. Relative to PR942, the exact global
change is `{-12 at rank 1, +8 at rank 2, +4 at rank 3, -4 at rank 4}`.
The four additional locally paid dimensions are exactly balanced by the
four consumed idle dimensions.

## Exact pricing and the dependency argument

For a global profile \(H\), the retained native complex moment is

\[
M_H(z)=\frac{1}{73\cdot33152}
       \sum_r H_r\,r(73/r)^z.
\]

Writing \(\phi_r(z)=r(73/r)^z\), the change is exactly

\[
\Delta M(z)=\frac{-12\phi_1(z)+8\phi_2(z)+4\phi_3(z)-4\phi_4(z)}
                       {73\cdot33152}.
\]

At zero it vanishes, as required by conservation of rank mass. Its derivative
there has numerator \(16\log2-12\log3=4\log(16/27)<0\).
This explains the direction of the search; the exact interval checks below
establish the finite improvement at the actual exponent.

The claimed adjacent root bracket is

\[
0.001664727752321934979327 < z_* <
0.001664727752321934979328.
\]

The lower endpoint must have moment strictly below one; the next
\(10^{-24}\) endpoint must have moment strictly above one. The production
replay checks both signs using the inherited Mercator and base-two engines.
[price.py](price.py) checks them separately using the positive-binomial
engine from the merged PR960 audit. That third path imports no production
logarithm or exponential code. It also certifies the signed profile change
at the nominated exponent. These are separately computed checks by the same
AI-assisted contributor, not independent human review.

The unchanged PR589 bit lower endpoint is
`0.001733427039589844234749`; its bad-residue charge and H1–H5 remain.
The outer construction takes `eta = beta = 1/10^24`,
`s = min(c,(1-beta)b)-1/10^27`, and seven bootstrap steps starting at
`384599/10^10`. Every bootstrap cutoff charges the full **1024-bit complex
payload**. The claimed prefix requirement is 779 bits and the physical
row coefficient is 17,495, below the retained limit 20,161. The separate
invoice must recompute these values from both actual suppliers, all 333
calls and all bridges. All nine finite-admission checks and all 47 outer
inequalities must pass before the nominated κ is accepted.

The dependency order is: complete cold PR942 ancestry; literal reconstruction
of the changed local word and owners; native admission of the new local
supplier; an independent event/owner/chart recount; exact pricing; emitted
mixed-provider controller audit; complete finite invoice; strict outer
assembly; payload and admission mutation controls; and final binding of
the actual artifacts. Discovery only records values derived from this fixed
construction. A separate strict run compares them with the frozen record.

PR942's all-replica upper bound holds for the unchanged U8 profile and helper
inventory. This construction changes that hypothesis in one invocation.
It therefore does not contradict the fixed-family upper bound. The earlier
local supplier's profile and widths cannot be substituted for the modified
call when applying that upper bound.

## Reproduce

Use Python 3.11 or later with the scientific/build dependencies required by
the selected cold replay. Assertions must stay enabled. Run from the
repository root, giving a new output directory outside the checkout:

```sh
python3 -B research/u8-e4-gap-fill/verify.py --work /absolute/path/to/new-e4-replay
```

To reuse a completed, source-bound `scripts/verify_frontier942.py` output:

```sh
python3 -B research/u8-e4-gap-fill/verify.py \
  --baseline942 /absolute/path/to/completed-frontier942-output \
  --work /absolute/path/to/new-e4-replay
```

The baseline directory is the one containing the wrapper's `RESULT.json`
and `replay/` directory. The verifier checks its full evidence closure before
reuse. Original source packages and `upstream/` remain read-only. Generated
gzip files are compared through their decompressed JSON or documented
semantic identity; exact hashes still bind immutable inputs and receipts to
their actual referenced files.

[VALIDATION.json](VALIDATION.json) records the completed local replay and its
limits. [ASSEMBLY.json](ASSEMBLY.json) is the unedited strict production
assembly, and [INDEPENDENT-PRICE.json](INDEPENDENT-PRICE.json) is the unedited
binomial/outer certificate. The executed checks cover a fresh complete cold
T37 baseline, the new native supplier, all 167,832 helper roles and 9,628
actual chart types, 28 separate owner mutations, 23 controller mutations,
114 strict admission mutations, 12 bit-supplier controls and 11 payload
mutations. The selected-source inventory and final artifact bindings pass.
The repository-wide `make verify`, hosted CI and formal verification of the
full multiplication theorem were not run for this package.

The replay uses PR942's runtime adaptations without changing verifier
predicates. Its single-provider freezer carries three fixed metadata fields.
[freeze_metadata.py](freeze_metadata.py) derives their two-provider values:
the actual dispatch counts, 23 controller mutations, and 114 admission
controls. The last count is 31 common cases, one bad owner-receipt hash,
and, for each of two providers, 17 literal cases, 20 distinct-width-pair
cases and four spot-width cases. The strict run must execute and reject
every control; changing the expected count does not relax an admission test.
The separate owner checker has explicit, source-bound edits to
select the width/profile of the provider actually used by each call and to
retain the 1024-bit reserve. It rejects the original unmodified owner map,
discarding the modified provider, and individually omitting each of the
20 owner edits, in addition to its inherited geometric controls. Payload
controls test strict prefix/row boundaries and eleven altered invoices.

## Scope and credit

The live selected record checked on 2026-10-13 still uses PR942. Newer pending
[PR987](https://github.com/CrocSwap/integer-mult-bounds/pull/987),
[PR1004](https://github.com/CrocSwap/integer-mult-bounds/pull/1004),
[PR1005](https://github.com/CrocSwap/integer-mult-bounds/pull/1005) and
[PR1018](https://github.com/CrocSwap/integer-mult-bounds/pull/1018) claim larger
gains through additional triangle slots and mutable-leaver circuits. This
package does not verify those claims or claim the largest pending κ. Its
contribution is the separate entrance-frame and gap-filling mechanism on the
pinned, fully replayed T37 baseline.

Prepared for David Breslauer with substantial OpenAI Codex assistance.
Apache-2.0 applies. Retained source notices and licenses remain in force.
The new work is the four-helper local reversal, its placement in the four
T37 unit gaps, the frozen mixed witness and its verification package.

BlockInvert supplied the PR664-style entrance promotions reversed here;
the [retained promotion proof](../gauge44-barch/PROOF-NOTE-PROMO.md) records
the exact `p6n-k4` recipe. Chafik Boukhalfa's PR685 supplied the earlier owner
certificate in this lineage. Jeremy Kothe's
PR799 X4 work and the PR869/870 U8 lineage supply the local word; the
retained notices credit NewBArch, ColdWitness/icekylinx, and the earlier
factory/gauge contributors. Jonathan Capalbo's PR942 supplies the T37
owners, its eight-role trade, and 1024-bit integration. Chafik Boukhalfa's
PR890 and Hao Yan's PR858 supply the preceding replica lifts, owner audits
and ancestry checks. The native/controller, bit, moment and outer suppliers
retain their attribution through [PR942's notice](../complex-t37-owners/NOTICE.md).

Finite certificate success does not prove the full integer-multiplication
theorem. The inherited all-size/compiler, common-label and mutable-source
realization, physical hosting, precision/tape, analytic transfer, and bit
H1–H5 assumptions remain. No claim of global optimality is made for this
new supplier family.
