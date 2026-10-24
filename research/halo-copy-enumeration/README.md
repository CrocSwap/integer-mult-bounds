# Gaussian halo input-copy enumeration

**Scoped all-size combinatorial implication, independent finite verifier, and an
explicit physical-cost boundary. No new κ.** The selected conditional record
remains κ = 0.00302015. On 2026-10-22 the orchestrator replayed the final
algorithm-seam controls and six-input closure under CPython 3.12.13: metadata,
normal and optimized registered runs passed. Finite audit evidence is not
scientific acceptance, a full-tape proof, or selected-result replay.

This answers Nick Petalas's [#4217 open question](../halo-locality-witness-audit/README.md#open-next-questions),
not his polynomial-locality argument. Its caller is Cinna Davis's
[GAUSSIAN.md lines 177–226](../unconditional-batched-crt/GAUSSIAN.md) and
[HALO.md lines 36–94](../unconditional-batched-crt/HALO.md), retained from #4100.
The new result is the explicit prefix/DFS enumeration, exact copy-volume
identity, independent destination oracle, and separation of non-output setup
from output-sensitive work. It neither repeats the locality factor-two note
nor substitutes exponent arithmetic for a universal algorithm.

## Definition and quantified result

Let g >= 1, integer A > 0, L > 4A, 0 <= b < A, and axis periods S_i = n_i L
with n_i >= 2. Coordinates are canonical integers modulo S_i. Here b is a
sufficient input-dependency radius, not a Gaussian conditioning parameter.
For core c, write local coordinates in [0,L). The kept interior is
I = [A,L-A); the lower and upper boundary intervals are B_0 = [0,A) and
B_1 = [L-A,L). All intervals are half-open integer intervals.

For first boundary axis f and side s, the **output rectangle** is

    R(c,f,s) = I^f × B_s × [0,L)^(g-f-1), translated by cL.

Its **input rectangle** E(c,f,s) expands every interval by b on both sides,
then reduces coordinates periodically. A canonical source is copied once for
each E containing it, even if it belongs to several destinations. Its full key
is `(destination core tuple, f, s, lifted local tuple, canonical source tuple)`.
The signed local tuple records wrap without losing the destination chart.
Input-copy keys are unique as full keys; source addresses alone need not be.
Returned output keys are canonical global output coordinates, without f or s.

HALO uses the conservative expansion A. Using b < A is a sufficient tighter
input set for a tensor whose per-axis dependency bandwidth is at most b; it
is contained in the source's A-expanded allocation. Thus the volume upper
bound below also bounds the tighter scheme. This does not silently identify
A and b: a literal A-expanded implementation can use the same interval proof
with b=A (half-open expanded interiors then tile rather than have gaps), but
that variant is outside this verifier's explicitly strict-bandwidth domain.
No polynomial row locality is proved here. The call-site facts bandwidth
<p^45 and A=ceil(p^48) are the inherited reason a strict b can be chosen.

**Proposition.** On this domain the source-first prefix/DFS algorithm below
emits exactly the destination-membership multiset, without duplicate full
keys. Its admitted face forest has at most g times its number of leaves in
internal nodes, including roots. There is also O(g) setup per source even
when there are no leaves. The output rectangles return each discarded output
exactly once. These are all-size combinatorial statements, proved next;
the small fixtures do not establish them by induction or extrapolation.

## Proof: choices, prefix AND, and the face forest

Write source x_i=q_i L+r_i, 0 <= r_i < L. Its candidate later-axis cores are
q_i, also q_i-1 modulo n_i when r_i<b, and also q_i+1 modulo n_i when
r_i>=L-b. Because 2b<L and n_i>=2, the list has one or two distinct choices.
These are exactly the cores whose expanded full interval contains x_i.
An earlier-axis expanded interior contains x_i exactly when
A-b <= r_i < L-A+b, and its core must be q_i: the expanded interiors are
strictly separated by a positive gap. Precompute these memberships and the
expanded lower/upper face memberships from the same at-most-two candidates.
Every face interval is contained in its expanded full interval, so no face
choice is missed.

Let prefix[f] be the AND of the interior-membership flags for i<f, with
prefix[0]=true. Face (f,s) is permitted exactly when prefix[f] and its face
choice list is nonempty. All suffix full-interval lists are already nonempty.
Consequently a permitted face defines a Cartesian product with no dead
branches: the face core choices, then all later-axis core choices. Earlier
core choices are unique and fixed. Traverse this product by a depth-first
odometer (a stack of depth/next-choice counters); emit a leaf key using the
unique periodic lift into its destination interval. Interval widths are
less than S_i, so there cannot be two such lifts.

Membership in the rectangle is a conjunction of these independent axis
conditions. This proves both directions of the emitted/oracle correspondence.
Each candidate list has no repeats, each Cartesian tuple is visited once,
and distinct face labels or core tuples give distinct destination keys.
Therefore the **full multisets**, not merely sets or counts, agree.
For output rectangles, each discarded coordinate has exactly one first
non-interior axis and exactly one side there. Earlier coordinates are
interior and later ones unrestricted. This proves unique returned keys.

For one permitted face, the product tree has height h=g-f <= g and at least
one leaf. At every non-leaf depth each node has a descendant leaf, and
nodes at that depth have disjoint descendant sets. There are at most C_f
nodes at each of its h non-leaf depths, hence at most h C_f <= g C_f
internal nodes, **including the root**, even for unary branches. Summing
over permitted faces gives N <= g C. There is no hidden 2g root term because
empty faces are rejected before a root is allocated. Testing those faces is
not free: scans, prefix ANDs and face tests total O(g) per source.

**Necessary additive term.** A source at the center of every core, farther
than b from all boundary slabs, emits zero copies but still requires its
coordinate scan and prefix/face setup. A literal all-work <= g times leaves
claim is therefore false. The correct operation account is

    O(g V) setup + O(g C) forest traversal + full-key/value emission,

where V is the number of dense records in the group and C the total copies.
The pinned GAUSSIAN text separately includes its initial scan; this is a
clarification and exact accounting witness, not a counterexample to its
already-separated dense-scan row. At a periodic core corner x=(0,...,0)
with b>0, the first-axis face has two neighboring face destinations in total
and every later axis has two choices: **2^g copies from that one address**.
The bound charges them as actual leaves, not by assuming constant fanout.

## Exact volume and the claimed cost boundary

Let K=product n_i, V=K L^g. Summing rectangle volumes with multiplicity gives

    C = K sum_(f=0)^(g-1) 2 (L-2A+2b)^f (A+2b) (L+2b)^(g-f-1).

This is a copied-input volume, not a union volume. With b<=A it is at most

    6 V (gA/L) (1+2A/L)^(g-1).

Thus C=O(VgA/L) if gA/L remains bounded (in particular the source's o(1)
hypothesis). The number of returned outputs is exactly
K[L^g-(L-2A)^g]. No bounded-multiplicity claim about individual sources is
needed. Empty centers and exponentially many-copy corners coexist.

The following implication is **conditional on a physical implementation**,
not a measured cost theorem for this Python program:

1. GAUSSIAN 194–207 supplies g=p^beta, local L with log L=O(log p), and
   beta+2(1-epsilon)<1. The absolute coordinate width ell and epsilon are
   defined in [CRT.md lines 20–28](../unconditional-batched-crt/CRT.md) and
   [PROOF.md lines 19–26](../unconditional-batched-crt/PROOF.md); both are
   pinned live inputs. With the caller's ell=O(p^(1-epsilon)), the quoted coordinate arithmetic
   O(g ell^2 polylog p)=o(p) and O(g log L)=o(p) absorb the O(g) setup into
   one p-bit-record scan. A mere g<=p would not justify this absorption.
   HALO's g log p=o(p) is also needed for short-field movement.
2. A destination/core/source key needs O(g ell + g log L + log g) bits,
   including signed local fields and face labels. This is O(p) under those
   hypotheses; spectator labels may be retained once, with the inherited
   complete-record O(p) width. Re-encoding a full key is not O(1) bits.
   A short-field stack implementation costing O(log L+log g) per traversed
   edge yields O(g polylog p) control work per leaf, absorbed by O(p) up to
   polylogs under the same strict beta<1 condition. Copying the p-bit value
   and complete key still costs O(p) bits per leaf. The node-count proof
   alone does not establish this stack/head-movement implementation.
3. Full-key binary radix sorting uses O(p) stable passes, not O(1). Each
   pass must scan/move O(p)-bit records and preserve all key fields, costing
   O(C p^2) bit movement (a generous upper bound also in normalized record
   work). Return sorting has at most C records. Sorting dense V records
   separately for each face would instead introduce the forbidden gV term.
   A fixed-tape stable distribution and rewind schedule is still an explicit
   physical premise, not Python Counter/dict behavior.
4. Conditional on sequential enumeration and sorting as above, the source's
   direct per-axis row application costs O(g A^2) record operations per copied
   record, giving per-group O(V + C[gA^2+p^2]) polylog p. Substituting the
   copied-volume bound and multiplying by O(d/g) balanced groups gives

       O(V [d/g + d g A^3/L + d A p^2/L] polylog p).

   Local coefficient setup remains an additive S_setup until the HALO 68–74
   hypotheses apply: fixed polynomial-in-p setup per rectangle/core,
   g tending to infinity, and at least g-1 long L-O(A) axes. Fixed g fixtures
   cannot demonstrate that absorption. The costs of actual row generation,
   arithmetic, exposure, and setup are not certified here.

**Result boundary:** the written combinatorial implication and exact
conditional accounting are supplied. The complete quoted physical tariff
is **not independently discharged**: it requires a fixed-number-of-tapes
encoding and paid stack/candidate-list access, stable radix distribution,
full-key movement, and the inherited coefficient/application/setup budgets.
This is a precise implementation obligation, not a claim that the source's
bound is false. No random-access dictionary operation in the verifier is
used as evidence for that tariff.

## Finite executable contract and observed evidence

`verify.py` uses integer arithmetic and standard-library Python 3.12. It
streams canonical addresses; it does not allocate a global value/matrix
array. Counters retain only small fixture copy keys and output keys. It uses
no project imports, search, census, huge p, numerical Gaussian coefficients,
or generated external files. The independent oracle loops destinations
first and tests absolute lifted half-open intervals directly; it does not
reuse the source candidate lists, prefix code, DFS, or lift computation.

Three fixed positive fixtures cover `(core counts; L,A,b)`:

- `(2,3; 12,2,1)`: 2D, unequal periodic sides, several destinations and wrap.
- `(2,2,2; 10,2,1)`: 3D corner with eight copies from one source, unary/deeper
  branches, several faces, interior zero-copy sources, and wrap.
- `(2,2; 10,2,0)`: zero bandwidth, genuinely empty emitted lists for interior
  sources, and no wrap halo.

Every fixture compares the full emitted key **Counters**, requires count one
for every full key and returned key, and checks exact copied-input and
discarded-output volume identities. Each admitted forest is checked for
nonempty leaves and the internal-node bound; the aggregate bound is also
checked. Direct destination membership is independent of source construction.
The center check establishes zero emitted copies; the corner requires exactly
2^g copies for b>0. The written algorithm, rather than a redundant inequality
g>g*0, explains why zero-copy sources still need additive setup.

Coordinate scans, prefix steps, face tests and candidate tests are **diagnostic
loop counts** with internal consistency checks. Printed oracle membership-test
counts are diagnostic too. These counters are not independent evidence of
physical cost: they do not price tape movement, arithmetic, stack access,
key rewrites or sorting. Exact membership, volume, output uniqueness and
forest bounds must not be conflated with those diagnostic counters.

The prior replay passed fourteen comparison/validation controls: omitted first
lower face, duplicated input key, lost periodic wrap, and dropped inclusive
lower endpoint on both positive-bandwidth fixtures; duplicate returned output
on all three fixtures; negative, equal-to-A, and larger-than-A bandwidth.
These retained controls mutate completed results or validate input domains;
they do not by themselves exercise an erroneous source algorithm.

The revised harness additionally runs three **algorithm-seam mutants** on each
positive-bandwidth fixture, using the same source implementation rather than
a duplicate algorithm:

- omit the preceding neighbor-core choice when r<b;
- use the unexpanded interior for earlier-axis membership, corrupting the
  memberships consumed by prefix AND;
- exclude the inclusive lower endpoint of an expanded upper face.

Each mutant must complete, then its **full emitted multiset** is compared with
the unchanged destination oracle. Internal exceptions are outside the rejection
wrapper and cannot masquerade as successful oracle detection. All rejection
checks use explicit exceptions and remain active with `-O`. Both modes rejected
all six algorithm mutants and fourteen comparison/validation controls.
They detect enumeration errors, not Gaussian-operator defects or physical costs.

The final replay reproduced these exact fixture counts:

| Fixture | Sources | Copies | Returned outputs | Maximum source fanout |
|---|---:|---:|---:|---:|
| `two_dimensional_wrap` | 864 | 1,152 | 480 | 4 |
| `three_dimensional_corner` | 8,000 | 19,456 | 6,272 | 8 |
| `zero_bandwidth` | 400 | 256 | 256 | 1 |

Both final runs reported `PASS_HALO_COPY_ENUMERATION`, twenty passed
rejecting controls, and six live source pins. The refreshed canonical launcher
at `624de9dc66858af0945e5f8a0942488d62280d43` also replayed both modes successfully.
An independent read-only agent reviewer re-derived the interval, forest, volume
and conditional cost algebra and reported no blocking mathematics defect. This
is scoped agent review, not human acceptance or formal proof-kernel verification.

## Reproduce

From the repository root, with full Git history and Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/halo-copy-enumeration --check-only
python3.12 -B scripts/research_package.py --package research/halo-copy-enumeration
python3.12 -B research/halo-copy-enumeration/verify.py
python3.12 -O -B research/halo-copy-enumeration/verify.py
```

The registered commands completed within their 30-second timeouts. The final
refreshed-launcher shell took 1.26 seconds including environment activation;
this is not a precise verifier benchmark. The observed terminal marker was
`PASS_HALO_COPY_ENUMERATION`, with twenty control names and six live inputs.
CPython 3.12.13 was used; no Python LSP was configured. Metadata validation
checked Git provenance and the exact copied card. Every live input is declared
in VERIFY and pinned by base Git blob and SHA256 in SOURCES. All pins resolve
at the package base, so no unmerged PR object is required. No selected-result
or full-tape proof replay was performed.

## Boundary and obligation ledger

| Boundary | Established here | Not established here |
|---|---|---|
| Source identity | Exact base/blob/SHA256 metadata and six-input replay passed | Selected-result replay |
| First-face geometry | All-size interval/partition proof; independent read-only agent re-derivation | Gaussian locality or conditioning; human/formal acceptance |
| Enumeration | Written all-size product-tree implication; final normal/`-O` replay and algorithm-seam controls passed | Human/formal acceptance of the all-size proof |
| Complexity | O(gV)+O(gC) short-operation account and conditional key/pass algebra; loop counters diagnostic only | Complete fixed-tape scheduling/cost theorem |
| Finite evidence | Three exact fixtures and twenty rejecting controls passed in both modes | Independent human or formal scientific acceptance |
| Multiplication | No frontier, ledger or supplier change | CRT repair, rounding, recovery, unconditional theorem |

## Open next questions

1. **Can a fixed-tape implementation realize the short-field stack and full-key
   radix schedule with the stated scan/leaf invoice?** It would close the
   remaining physical enumeration boundary. First implement a bounded symbolic
   tape trace for one face forest, explicitly charging candidate-list access,
   stack pushes/pops, key rewrites, distribution and rewinds; then prove its
   all-size schedule. Blocked by no additional mathematical input, but not
   supplied by Python's random-access containers.
2. **Can the local coefficient setup and g axis exposures be bound to that same
   copy layout without an extra dense scan per face?** This is required to
   promote the conditional invoice to the full HALO tariff. First specify the
   page generation, ownership and tape-order interface for one destination
   rectangle, retaining S_setup until g grows. Blocked by the unreviewed
   physical schedule and inherited row-generation/application hypotheses.

These questions are also structured in `TASK.json`; neither calls for another
finite locality replay or a parameter/exponent census.

## Provenance, overlap and credit

Base: `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
The original `uniform-transfer-audit` card is copied exactly; the assignment
refines it to one Gaussian copy-enumeration implication. The parent refreshed
upstream to `624de9dc66858af0945e5f8a0942488d62280d43` and reported an exact diff:
guidance, catalogue, selected record, and all scientific sources were unchanged;
only `scripts/research_package.py` changed among the inspected infrastructure.
The scientific base and source pins remain at `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.

The refreshed parent-provided overlap on 2026-10-22 covered 299 remote open-PR
records at 19:49:07Z, 3,721 Discussion records at 19:49:40Z with complete
pagination, and all 5,860 tracked local notes plus the two new package notes.
Exact terms `source-driven enumeration`, `halo-copy-enumeration`,
`f7-l22-receipt-domain`, and `f7-l22-deep-shard-census` matched predecessors
and the new notes only; no competing remote match was found. Arbitrary diffs
and closed-only unmerged PRs were not covered. This records a refresh, not a
novelty proof or an independent search by this agent. Local-only coordination
is retained; a parent posting attempt had unknown outcome and no matching
claim was found on its read-only follow-up. No successful public claim or
publication is asserted. No commit or publication was made here.

Cinna Davis authored #4100 (submitted head
`337d04939571a637aeab54a0f58f54fde811663a`), including the prefix/odometer
proposal, halo tariff and Gaussian caller. Nick Petalas authored #4217
(submitted head `d2479b3606beeb745c19210219acdd96967bf8eb`), explicitly
excluding enumeration from his locality audit and asking this question.
The present package is an independent implementation and accounting refinement
of their retained text, not an invention of the first-face idea. The #4100
[NOTICE](../unconditional-batched-crt/NOTICE.md) preserves the broader lineage,
including Douglas Colkitt/OpenAI's tape framework, Vlado Vojdanovski/PR1673's
Gaussian layout work, and Chafik Boukhalfa/PR1758/1786's constructions.
CRT.md and PROOF.md bind the ell/epsilon definitions used in the conditional
cost algebra, and NOTICE.md binds this lineage; their exact base blobs and
SHA256 digests join GAUSSIAN.md, HALO.md and the #4217 README in SOURCES.json.
All six are declared live inputs in VERIFY.json.
New artifacts prepared by the Astra research contribution agent with substantial
OpenAI assistance under the user-authorized parallel assignment. Apache-2.0.
No independent human review or formal proof-kernel certification is claimed.
