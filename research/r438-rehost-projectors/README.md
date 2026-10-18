# PR2423 R438 rehosting: exact pending-projector binding

**Finite geometric certificate. No new bit endpoint or κ.** The concrete
rehosting selection in [PR2423](https://github.com/CrocSwap/integer-mult-bounds/pull/2423)
has compatible source-bound pending projectors at all **71,040 physical idle
deadlines**, covering **126,144 helper occurrences**. Its new rank-34 remainder
is the exact complement of its hosted width-eight slice. No geometric defect
was found.

This discharges the projector-compatibility item explicitly left unchecked in
PR2423's “Scope and limits.” It applies this account's
[PR1307 geometry](../selected-bit-hosting-audit/README.md) to a changed R438
allocation and word; it does not claim the original projector argument,
window feasibility, slot optimum, numerical owner formula, or moment root as
new. PR2423 already checks numerical owner maps in `verify_rehost.py`, despite
its broader README caveat about cross-replica maps. The added check binds those
owners to the actual subspaces and exact address operators.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Exact object and result

Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The pending predecessor is PR2423 at
`13cd273dc13c98244b1f9bcf588b6e828cbc0347`, using Ali Romman's PR1043 R438
word at `e309e17f83f5759b1ea1fa24a76f24838784cb4d`. The two consumed PR2423
files are retained byte-for-byte under [sources/](sources/); original paths,
Git blobs and SHA256 hashes are in [SOURCES.json](SOURCES.json).

PR589's selected nine-stage bit moment is
`c = 0.001733427039589844234749`, with width 64 and 28,416 roles. PR2423 proposes
`c = 0.001734846264120199151475` for its transported R438 word and new layout.
The latter number remains the predecessor's claim: **this package does not
recertify its root or admit its supplier**. The selected combined result at
the base is complex-bound. The geometric evidence remains useful independently
of later exponent records.

| Checked quantity | Result |
| --- | ---: |
| Source events / idle children, including the zero child | 29 / 10 |
| Helper slots per replica / replicas | 3,942 / 32 |
| Physical helper occurrences | 126,144 |
| Physical child-family deadlines, including zero rank | 71,040 |
| Occupied physical families | 28,096 |
| Families hosting factors from multiple idle children | 14,208 |
| Helper occurrences containing all of q-perp | 21,312 |
| Source port projectors / distinct factorization patterns | 111 / 12 |
| Exact basis columns represented in the operator check | 170,496 |
| Paid children / paid rank mass / deficit | 904,320 / 1,808,352 / 10,272 |

The per-replica nonzero idle profile is
`{2:433, 4:444, 6:444, 7:666, 34:1, 42:10}`; another 222 zero-rank
remainders are retained in the census. The changed word's independently
recounted local profile is
`{1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:18}`.
Using the inherited equal forward/reflected gap accounting, 288 local profiles
plus 32 idle profiles give

```text
{1:380736, 2:400352, 3:22752, 4:26880, 5:29376,
 6:17376, 7:26496, 34:32, 42:320}.
```

Every remainder remains charged. This agrees with the predecessor's proposed
accounting; it is not an additional saving. The selected R439 allocation is a
positive control, reproducing its 126,432 helper occurrences.

## Why the factors have the right physical operator

Use the source level convention from the pinned nine-stage geometry. For a
live root `q` with `q^T q = 4`, let `K_q = I_8 - q q^T / 4`. In a chart with
`q/2` first, seven q-perp axes next, and eight exterior seven-dimensional blocks,
the pending axes for a level change `a -> b` are

```text
[1, 8+7b)       if a = -1,
[8+7a, 8+7b)    otherwise.
```

Intervals are half-open. The checker reconstructs all ten intervals from the
source controller and compares their levels with the geometry producer's
literal idle table. It checks disjointness across children of a physical pair,
not just within each child.

The fixed selection expands to contiguous width-eight slices at offsets
`0,8,16,...` within each pending interval. When a pending interval starts at
axis 1, its first slice contains **all** seven q-perp axes and one exterior
axis. Every later slice is entirely exterior. Empty hosts leave the entire
q-perp block in the remainder. Intervals starting at axis 8 or later are
entirely exterior. Consequently neither a host nor its remainder splits
q-perp. This also follows directly from the checked condition
`mask & 255 in {0,254}` for every factor.

Thus each physical factor has a uniquely determined projector: either `K_q`
plus exterior coordinate projectors, or only exterior coordinate projectors.
It does not depend on which orthonormal completion of `q/2` the inherited
source uses. In particular the new partial child-6 family has hosted axes
`[22,30)` and remainder `[30,64)`, of ranks 8 and 34.

For an orthogonal projector `P`, the source bit address map on arbitrary head
and tail vectors is

```text
D(P) = [[I-P, P], [P, I-P]].
```

For orthogonal `P_i`, block multiplication gives
`D(P_1)...D(P_t) = D(sum_i P_i)`. At every deadline the hosted projectors and
remainder are disjoint and sum to the source pending projector. This proves
the complete endpoint identity for arbitrary input vectors. Reflected factors
have the same involutive endpoint, and reversing a nested frame path while
taking complements preserves each positive dimension gap.

The physical owner formula is
`replica*888 + (2*pair+side)*111 + port`.
The checker enumerates every helper occurrence at every replica, binds it to
its source pair, side, port and ambient support, and rules out aliases and
cross-child overlaps. It checks the no-touch borrowing windows directly from
the intervening source events. **Moving a hosted factor to its deadline still
uses the inherited whole-call/correlated-helper realization contract**; the
projector identity alone is not a proof of that realization.

## Reproduction and failure controls

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/r438-rehost-projectors/verify.py
python3 -I -O -B research/r438-rehost-projectors/verify.py
python3 -I -B research/r438-rehost-projectors/test_verify.py
python3 -B scripts/research_package.py --package research/r438-rehost-projectors --check-only
python3 -B scripts/research_package.py --package research/r438-rehost-projectors
```

Expected verifier line:

```text
PASS_R438_REHOST_PROJECTORS helpers=126144 deadlines=71040 ports=111 factorizations=12 controls=10 no_new_kappa
```

[RESULT.json](RESULT.json) is checked read-only. `--write NEW_PATH` exclusively
creates a new receipt for intentional regeneration. Checks remain enabled
under `-O`. The verifier reads pinned data and extracts only the source
`recipe`, literal geometry table and comparison `expand` function. It imports
no predecessor checker, optimizer or moment engine. The allocator, frame-rank
recount and rational address action are implemented here; the geometric
reasoning and source conventions remain explicitly credited to PR1307.

The matrix check applies the rational 16-coordinate local block directly to
all its basis vectors. It separately checks both head/tail basis columns of
each of the 56 exterior coordinates by their literal swap parity. These are
exact block-matrix checks, not sampled Boolean inputs. All 111 ports and 12
factorization patterns are checked, representing 170,496 columns; the physical
census then binds every actual deadline to one of them. Five focused tests
include a separately assembled dense rational matrix. An optimized Git-free
export replay also passed; actual source-byte and receipt-rank mutations in
that temporary export were rejected by the command-line verifier.

Eight rejection controls cover changed source bytes, missing/duplicate helpers,
a slice splitting q-perp, an illegal stage, omitted/duplicate rank-34
remainders, and an equal-rank wrong-exterior-axis operator. Two additional
exact witnesses distinguish a wrong port projector of the same rank and the
same exterior swap applied to the wrong independently dirty replica. For the
new remainder, replacing axis 30 by axis 8 keeps its rank 34 and changes the
address action. A dirty head coordinate at `(family=888, axis=22)` also
separates the intended replica from an aliased replica-0 call.

## Limits

This is a finite source-binding certificate with the scoped projector proof
above. It does not establish local scalar semantics/H1-H5, a native emitted
hosted template, the whole-call correlated-helper realization, an injective
cover compiler, all-size recursion, packet/tape/precision implementation, or
analytic transfer. Those obligations are inherited, not discharged by the
slot counts or basis checks. No complete cold replay, new moment endpoint,
full multiplication theorem, formal proof or independent human review is
claimed. The 22 alternative slack splits and later hypothetical helper
deletions are outside this fixed-selection audit.

## Open next questions

1. **Does native hosted emission preserve these exact owner/projector bindings?**
   This is the next admission boundary for PR2423. Start by exporting the
   source selection and matching the emitted owner routes and remainder
   factors against this receipt, then run the native hosted audit. The missing
   changed-layout emitter and inherited realization contract are blockers.
PR1736's mixed-width placements are a distinct, concurrently investigated
object. Width alone does not prove that q-perp is split: inspect the actual
slice positions. This fixed R438 certificate neither audits nor excludes that
family, and does not duplicate its open projector question.

The structured task and next questions are in [TASK.json](TASK.json). The
related canonical geometry discussion is
[#1289](https://github.com/CrocSwap/integer-mult-bounds/discussions/1289).

## Credit

Sagar Thakrar supplies PR2423's changed word, layout, slot optimum and invoice;
Ali Romman supplies PR1043's helper470 deletion. This account's PR1307 supplies
the selected-layout geometric audit and projector argument. DreamingOfClouds
and eumemic supply the PR589/555/545/543 bit lineage; DaysSky, Zhihao Chen,
chafreaky and the retained PR442/386/replica contributors supply the hosting,
port geometry and owner conventions. PR1023 and the seed72/seed14 packages
supply the earlier packing and window work. Their results are not claimed as
new. See [NOTICE.md](NOTICE.md) and the exact source pins.

New material is Apache-2.0. OpenAI Codex supplied substantial assistance in the
derivation, implementation, checking and writing. No independent human review
is claimed.
