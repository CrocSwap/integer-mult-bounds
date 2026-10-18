# R439 B508: moving the left boundary does not remove the eleven-wire floor

**Scoped proof and exact finite certificate; no new supplier or kappa.**
In the retained PR1062 word, enlarge the interval from the isolated B508 block
to **A[1991:2075], the nine COPY/scatter/ERASE observations, and B[0:195]**.
The left cut precedes helper 466's rank-one-to-rank-four promotion. Nevertheless,
all eleven B508 wires must contain the complete rational frame F508 by the
right cut. Their exact minimum contribution **inside this interval** is

\[
8\,2^q+3\,3^q,\qquad 0<q=1-a<1.
\]

The baseline attains this contribution with eleven single climbs, of total
rank mass 25. This answers the donor-466 enlarged-boundary subproblem in
[Discussion #1795](https://github.com/CrocSwap/integer-mult-bounds/discussions/1795).
It does **not** establish an optimum for the other wires or the complete interval.

The stronger finite statement is that the same eleven wires are forced to
contain F508 for **every left cut immediately before A[k], 0 <= k <= 1991**,
with the same post-B[194] endpoint: 1,992 cuts and 21,912 wire/cut checks.
The displayed sharp invoice belongs only to k=1991. At earlier cuts, multiple
baseline climbs may still have coalescing headroom.

Evidence is author-checked by two separately implemented exact engines written
in the same assisted session. No independent human review is claimed. The
claim is in discussion #1795; these files are LOCAL-ONLY until publicly linked.

## Changed interface and exact model

The source is [PR1062's word](../r439-bsection-stars-seed01/candidate.json.gz),
SHA-256 `b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee`.
All indices are zero-based. B508 itself is B[174:195]. The enlarged interval
has 279 stored A/B operations, 308 elementary A/B ADDs, 527 scatter ADDs,
nine COPY/ERASE pairs and 661 original scalar registers.

The reversible subsystem consists of 111 sources and 439 helpers. Targets
111..221 may receive the prescribed observations, but **neither a target nor a
returned COPY value may feed back into this subsystem**. This retains the
no-target-feedback part of the original interface. COPY is a special interface,
not an ordinary common-frame gate, so omitting this restriction would invalidate
the proof. Its original observation rows and target effects are checked exactly.

A replacement may change all intermediate arithmetic and frames, including
helper 466's frame at the original B508 entrance. It may write sources
temporarily, use any finite independent dirty workspace, and use nonlinear
reversible Boolean gates. Each gate's operands share a rational frame containing
their previous frames; frames grow by inclusion. Initial values range over the
full Cartesian product. No erasure, reset, frame descent, external read or new
information-transfer interface is allowed in the reversible subsystem.

At the right cut every original source/helper coordinate must have the same
value as the pinned interval, for every input and auxiliary value. Original
wire identities remain fixed. Auxiliary outputs may be arbitrary, provided the
subsystem remains reversible; this relaxes the usual restoration requirement.
The eleven exit frames are **not prescribed to be F508**: containing F508 is
the conclusion. They may be larger, with all resulting costs still payable.

## Proof and the source-only witness

Use the semantic forward/inverse frame invariant credited to PR1511 and its
dirty-workspace/nonlinear extension in PR1810. If a reversible subsystem has
the exact original endpoint z -> U z, then each original output wire i must
contain every initial frame S_j for which either U[i,j]=1 or U^-1[j,i]=1,
as well as its own initial frame. This remains true with independent dirty
auxiliaries: the original coordinates of the inverse of
`(z,b) -> (Uz,G(z,b))` are exactly `U^-1 y`, independently of auxiliary outputs.

For completeness, the invariant follows by induction on local bijections.
Forward dependence can spread only among the gate's operands. Composing the
inverse with that gate's inverse can likewise spread inverse dependence only
among these operands. Their common containing frame contains the union of the
previous obligations. Monotone promotion preserves all obligations. This
argument uses semantic dependence on independent coordinates, so it covers
arbitrary reversible nonlinear gates, not just XOR resynthesis. The special
COPY observations are harmless only because they have no return channel.

The new observation is that **original source lines suffice**, without assuming
any helper already has rank four. For source 19 at the enlarged cut, its forward
source support is just `[19]`, whereas its inverse-column source support is

```
[19, 35, 66, 89, 97].
```

The four root vectors with indices `[19,35,66,89]` are rationally independent
and span F508. Each source j always retains its original root line j. Thus
source 19 must contain F508 even after removing helper 466's old entry-frame
assumption. A hypothetical rank-three exit, and its proposed replacement of
the original rank-two climb by a rank-one climb, is impossible in this model.

Why does the inverse source support survive earlier cuts? Write the subsystem
map as U_k = B A_k, where A_k is the suffix A[k:2075] and B is the non-target
part of B[0:195]. Every A operation writes a helper, so A_k fixes each source
coordinate. Hence the source rows of

\[
U_k^{-1}=A_k^{-1}B^{-1}
\]

equal those of B^-1 for every k. The baseline prefix's source-preserving
property proves this endpoint identity; the replacement itself need not
preserve sources at intermediate times.

For the other ten wires, forward source support together with inverse source
support and the wire's own source line gives rank four as well. The certificate
contains exact supports and four-root witnesses at k=1991. The following
table gives the complete minimum component bill at that cut:

| Wires | Entry rank | Forced rank | Minimum contribution |
|---|---:|---:|---:|
| 19, 27, 35, 43, 57, 74, 89, 97 | 2 | 4 | 8 H2 |
| 65, 66, 466 | 1 | 4 | 3 H3 |

Here Hr denotes r^q. On one wire with positive increments d_t and forced
dimension increase at least d, concavity/subadditivity gives
`sum d_t^q >= (sum d_t)^q >= d^q`. The original interval reaches F508 in
one jump on each listed wire, proving sharpness of their **aggregate component**.
This is an attainable component minimum, not an assertion that independently
minimized components compose into a globally optimal circuit.

The cut atlas repeats the exact source-support test for every k=0..1991.
One engine updates endpoint rows by right multiplication when moving the cut;
the other replays every suffix from scratch. Both establish that the union of
the named source lines spans exactly F508, rather than merely some rank-four
space. These finite checks instantiate the written arbitrary-circuit lemma.

## Complete baseline ledger and remaining headroom

No unpriced scalar saving is counted. The source-bound baseline partition is:

| Component | Paid profile | Rank mass |
|---|---|---:|
| Eleven B508 wires inside enlarged interval | 8H2 + 3H3 | 25 |
| Other wires inside enlarged interval | 38H1 + 144H2 + 13H3 + 36H4 + 10H5 + H6 | 565 |
| Nine retained-total COPY calls | 9H7 | 63 |
| Other baseline frame work | remainder of complete profile | 4476 |
| Complete baseline word | 1323H1 + 1342H2 + 79H3 + 44H4 + 102H5 + 11H6 + 19H7 | 5129 |

Only the first row is proved sharp for the enlarged interval. The old isolated
B508 invoice, 6H2+2H3, omitted the newly included A promotions of wires 43, 57
and 466; using it here undercharges by 2H2+H3. The complete matrix replay
includes the COPY/scatter effects on all targets, not just the 550-wire
restriction used in the proof.

A replacement could still change the other-wire component or promote these
wires beyond F508 to merge later climbs. It must recompute every affected
continuation charge, COPY/restoration obligation, caller width, normalization,
hosting and precision cost. The last two rows of the table are baseline
accounting, **not** a claim that those costs remain constant under changed exits.
The selected complex side still binds; no scalar count or partial profile here
changes the selected moment or exponent.

## Reproduce and controls

From the repository root, Python 3.12 and its standard library:

```sh
python3 -I -B scripts/research_package.py --package research/r439-donor466-enlarged-seam --check-only
python3 -I -B scripts/research_package.py --package research/r439-donor466-enlarged-seam
```

The registered replay runs both engines and the ten test groups with `-I -O -B`.
Expected primary and separate-checker markers:

```text
PASS_R439_ENLARGED_SEAM cuts=1992 wire_cut_checks=21912 minimum=8H2+3H3 mass=25 no_new_kappa
PASS_R439_ENLARGED_SEAM_ORACLE direct_cut_replays=1992 rational_rank_checks=21912 full_matrix=661 COPY=9 minimum=8H2+3H3 no_new_kappa
```

The primary engine uses packed binary rows, reverse-gate inversion and rational
elimination. The separate checker uses sets, Gauss-Jordan inversion of the
forward matrix, literal COPY/ERASE replay and fraction-free integer elimination.
Neither imports predecessor verification code. Source pins bind the exact
compressed input; regenerated evidence is compared as structured JSON.

Controls reject source-byte corruption, a rank-preserving wrong inverse support,
a dependent root witness, the underpriced old block invoice, an incomplete cut
atlas, an omitted scatter ADD, source-writing A input and target feedback.
The scatter mutation preserves the eleven source/helper witness records but
changes the full endpoint, demonstrating why that larger boundary is checked.
An exhaustive 65,536-state fixture checks nonlinear source-preserving preparation
with arbitrary dirty auxiliary output; a source-writing prefix breaks the
corresponding inverse-row identity. Forward-only geometry sees rank one for
source 19 and misses the rank-four inverse obligation.

No native multistage replay, physical hosting/precision admission, all-size
compiler or transfer proof, Lean formalization, selected cold replay, complete
interval optimum or multiplication theorem is claimed. Package checks and two
same-session implementations are not independent scientific review.

## Open next questions

Can the **other-wire component** of this exact interval be reduced while keeping
the nine observation rows and complete endpoint? It matters because the eleven
B508 wires cannot provide the hoped-for lower exits. A feasible first step is
to isolate one helper outside this set, retain its surrounding fixed visits,
and derive its complete replacement/continuation bill before synthesis. The
blocker is an actual common-frame circuit with a favorable full invoice.
[The direct-source substitution census](../bit-source-substitution-seed11/README.md)
already excludes the simple helper467-to-source27 replacement at A[1991]; that
covered experiment should not be repeated.

Alternatively, can moving the **right** cut change the inverse source recovery
relation, while paying for every intervening operation? First choose one later
source-changing cut and recompute the same supports and complete invoice. The
present atlas moves only the left cut. A new scalar endpoint, return channel or
frame-descent interface needs its own correctness and cost proof. Structured
questions are in [TASK.json](TASK.json).

## Provenance and credit

Base main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The exact pins and historical selected-record binding are in [SOURCES.json](SOURCES.json).
No pending implementation is a dependency. This is the `scalar-to-moment` card,
refined to the released #1795 handoff; the original chooser and scope are in
[TASK.json](TASK.json).

Credit Sagar Thakrar's PR1062 (`cd016e5dcd5ba28dafa3f3b4eeef003a38e6a11b`)
for the composed word; Arham Tahir's PR1368
(`6ae784908c57f3aa5a2165d382b21a40accdf7a6`) for the B-block interfaces;
Andrey Mas's PR1511 (`f247c4e17b19e55c0db0ec8a1b660fd118adf014`)
for the inverse-column invariant; and Ross Richardson's PR1810
(`aed73d574ff6145f056d3723ce87c61b06e631f8`) for the dirty-workspace/nonlinear
extension and explicit enlarged-boundary handoff. The general invariant is
used and credited, not claimed anew. Those results fix the isolated block
entrances; the present source-only certificates cover a different interval
and 1,992 left boundaries. The fixed post-B cleanup bound concerns a different
right boundary. The source-substitution census and its authors retain credit
for the separate restricted helper-deletion obstruction.

Credit DreamingOfClouds/PR589, eumemic/PR555/PR543, Sricharan Vagvala/PR967,
Aaron Wang/PR1015, and the retained frame/compiler lineage. Existing packages,
archives and the selected result are unchanged.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. No independent human review is claimed.
