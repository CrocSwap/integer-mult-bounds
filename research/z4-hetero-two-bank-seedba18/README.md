# Heterogeneous 3+7 echoes on two distinct source banks share one order-four boundary

**Scoped recursive-interface construction and exact finite law. No new κ, supplier
admission, or change to the selected result.** Agent: **Aaron Wang**, with help from
opencode (substantial AI assistance; no independent human review is claimed).

## Object

This package fills the one uncovered cell of the pinned PR1391 order-four typed
boundary interface. On that interface, two consecutive root echoes can share one
carried workspace phase instead of paying two independent boundary schedules:

- `research/z4-persistent-pair-seed57` and `research/z4-heterogeneous-pair-seed3x7`:
  two calls on **one shared source** (identical 5|5, then heterogeneous 3|7 with the
  canonical phase path);
- `research/z4-distinct-source-seed55`: two **identical** five-child calls on **two
  distinct source banks**, with the handoff at the 5|5 midpoint.

Missing until now: **heterogeneous reader schedules across two distinct source
banks**, where the source handoff sits at an asymmetric boundary. Here type A has
three children reading source octets `[0,1,2]` of bank `X`; type B has seven children
reading `[2,1,0,2,1,0,2]` of bank `Y`; one arbitrary dirty output octet `D` and one
24-coordinate arbitrary dirty workspace `W` must both be restored exactly.

## Construction

The child family is the pinned phase-indexed typed child
`C_(i,t): D += Q^(-t) R_i W; W += (P-I)W` of `research/z4-distinct-source-seed55`
(the identity `Q^(-t) R_i P^t = R_i` is re-checked here for all 12
phase/reader pairs over blocks `{0,1,2}`). The joint word is one ten-child typed
echo over the concatenated schedule `[0,1,2,2,1,0,2,1,0,2]`, with the charged
source handoff `W += P^t (Y-X)` placed after child 2 — the 3|7 boundary, at
workspace phase `t = 1` on the optimal path — instead of the midpoint. As in the
predecessor, the complete call copies `X` in, runs the typed body, applies the
handoff and the `Y` restore, and closes with the literal inverse body.

## Exact results

Child cost is the pinned leaf `(62,6)`, each single-source call pays a `2d = 48`
ADD copy/restore wrapper, and the two-source handoff costs 48 ADDs. The workspace
boundary charge `g(k)` comes from the exact recurrence
`F_0(t) = A(t)`, `F_(j+1)(s) = min_t F_j(t) + A((s-t-1) mod 4)`, terminal phase `0`,
with `A = [(0,0),(54,6),(36,12),(54,6)]`.

| Execution | ADD | NEG | Primitives | Reads | Prefix row-L1 peak | Map |
|---|---:|---:|---:|---:|---:|---|
| A then B, separate (3 and 7 children) | 1,552 | 144 | 1,696 | 3,248 | 18 | pass, 80 columns |
| Joint ten-child, asymmetric 3-to-7 handoff | 1,408 | 144 | **1,552** | **2,960** | 21 | pass, 80 columns |
| 5-to-5 predecessor control (reproduced) | 1,552 → 1,408 | 144 | 1,696 → 1,552 | 3,248 → 2,960 | 16 → 21 | pass, 80 columns |
| 2-to-8 even split (both words) | 1,408 | 144 | 1,552 | 2,960 | — | pass, 80 columns |

The joint 3|7 call **saves 144 primitives and 288 reads** against the two separate
calls, with both sources read-only, all four banks arbitrary dirty, and the exact
map `(D,X,Y,W) -> (D + sum_{b in [0,1,2]} R_b X + sum_{b in [2,1,0,2,1,0,2]} R_b Y, X, Y, W)`
checked on all 80 basis columns. The 5|5 row reproduces
`research/z4-distinct-source-seed55`'s published figures exactly (positive control).

## Boundary law (exact for this interface)

Because `A` has period 4 under the min-plus recurrence, `g(k) = g(k mod 4)`:
`g(0) = (0,0)`, `g(1) = g(3) = (54,6)`, `g(2) = (36,12)` (checked against exhaustive
coverage at `k = 3, 5, 7, 10`: 64 + 1,024 + 16,384 + 1,048,576 phase paths, and for
`k = 1..16` by the recurrence). The complete charged invoice of the two-bank pair
therefore obeys

`separate(k1,k2) - joint(k1,k2) = 2 * (g(k1) + g(k2) - g(k1+k2))`.

For `k1 + k2 = 10` this saving is **144 primitives exactly when both child counts
are odd, and 0 when both are even**. The emitted-word checks confirm both sides:
the 3|7 pair realizes the full 144, while the 2|8 pair (same banks, same child
family, handoff after child 1) is a legal composition whose two invoices are
identical — it merges no boundary work. The heterogeneous invoice is also identical
to the 5|5 invoice: on this interface the saving depends on the parities of the
child counts, not on how the children are distributed between the calls.

## Controls and evidence

`verify.py` re-checks the pinned PR1391/PR1410 input blobs and the selected-record
hash at base `e112d71c8d7bb32435debcc54df932593dd8223a`, the 12 typed-child
identities and gate counts, recurrence-versus-exhaustive agreement at all four
sizes, and six negative controls on the 3|7 cell: switching at the midpoint
instead of the 3|7 boundary, a wrong handoff phase, a mutated A-side reader, an
omitted B call, a missing terminal `Y` restoration, and a missing literal inverse —
each rejected by the exact map. `RESULT.json` is the recomputed evidence and must
match byte-for-byte on a second run.

## Reproduce

```sh
python3 -I -B research/z4-hetero-two-bank-seedba18/verify.py
python3 -B scripts/research_package.py --package research/z4-hetero-two-bank-seedba18 --check-only
```

Expected marker:

```text
PASS_Z4_HETERO_TWO_BANK_3_7 g3=60 g7=60 g10=48 separate=1696 joint=1552 saved=144 reads_saved=288 law=odd_splits_only even28_saved=0 paths=64+1024+16384+1048576 basis=80 controls=6
```

The registered package replay is declared for Python 3.12 in `VERIFY.json`; the
local runs above used CPython 3.12 as well.

## Scope and limits

The result is exact for the declared order-four phase-indexed child alphabet and
these fixed reader schedules. It is not a lower bound for arbitrary ADD/NEG words.
Output-row reindexing is free in this word model (it is the typed ADD target);
address calculation, physical row routing, source hosting, tape travel,
fixed-precision admission, recursive assembly into a selected supplier and analytic
transfer are unproved. The joint word raises the prefix row-L1 peak from 18 to 21,
so precision remains a live obligation. No κ, selected moment, supplier or frontier
change is claimed.

## Open next questions

- **Can a named selected supplier realize the heterogeneous typed readers at the
  3|7 handoff?** This matters because the 144-primitive saving transfers to a
  recursive profile only through an admitted supplier. A feasible first step is to
  extract one retained #1094 child matrix and test `Q^(-t) R_b P^t = R_b` for the
  block schedules `[0,1,2]` and `[2,1,0,2,1,0,2]`, then price the handoff routing.
  Blocked by: no physical host, tape schedule or precision-admitted supplier for the
  paired order-four interface exists yet; both predecessor packages record the same
  blocker.
- **Is the parity law sharp beyond the fixed ten-child total?** The identity
  `separate - joint = 2(g(k1)+g(k2)-g(k1+k2))` is proved for this alphabet at the
  invoice level; whether any non-typed schedule beats `g` at odd/odd splits is open.
  A first step is an exhaustive search over non-typed boundary words at `k = 3`.
  Blocked by: the typed recurrence is optimal only within the typed alphabet; a
  different reader family needs its own model.

## Credit

The order-four child emitter, the typed reader identity and the two-bank handoff
mechanism are Cinna Davis's (1337isnot1337), from PR #1391, PR #1410 and the
packages `research/z4-paired-frame-restoration-seed56`,
`research/z4-persistent-pair-seed57`, `research/z4-distinct-source-seed55`; the
heterogeneous 3|7 reader schedule is from
`research/z4-heterogeneous-pair-seed3x7` (PR #1768). All are pinned byte-for-byte
in `inputs/` and `SOURCES.json`. The new material here is the heterogeneous
two-bank composition with the asymmetric handoff, the exact map and invoice checks
for it, the period-4 boundary law with its odd/even saving classification, and the
2|8 zero-saving control. Prepared by **Aaron Wang** with help from opencode.
New material is Apache-2.0; the repository license and all source attribution are
retained.
