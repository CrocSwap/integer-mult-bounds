# R439: four retained contacts obstruct staged helper465 isolation

**Scoped all-length interface obstruction; no new supplier or kappa.**
PR1271 leaves a legal width-seven suffix for helper465 at B cut10 open. A
four-ADD, two-frame isolation block does pass that cut's full dirty boundary.
Nevertheless, **every exact isolation block with the same boundary**, of any
length and using any rational frames or restored dirty workspace, must change
at least one of four later original contacts to admit the original target
endpoints. Merely reframing or adding scalar gates cannot repair them.

This is stronger than failure of one proposed schedule. It is **not** an
impossibility theorem for arbitrary helper465 retirement: changed scalar
boundaries, contact removal/reordering, changed physical roles or new transport
are material escape routes.

## Exact contract and four-contact theorem

The input is the selected PR589 word on PR555, SHA256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
Keep its D, A, nine retained COPY/scatter/ERASE lifecycles and first ten B records
unchanged. **Cut10 is after B[9]**, with zero-based record indices. All copies
have been erased. Let `u` be the 661 independent original register inputs and
`w=M u` the current scalar state. No incoming helper is assumed clean.

This is checked against the **actual pinned selected exporter**, not inferred
from a 661-column flattening. `literal_copies.py` runs it, decodes all27,234
records, and replays the complete original scalar/frame-ID stream. The exporter
reuses physical temporary661 at frame0: each COPY is followed by its scatter
reads and ERASE before the next COPY. The nine retained sources472–480 are at
frames510–518, each of rank seven. COPY records are
`21816,21881,21938,21995,22052,22117,22182,22239,22296`; the corresponding ERASE
records are `21880,21937,21994,22051,22116,22181,22238,22295,22360`. Cut10 is after
record22380. **There are no live correlated temporary roles at this cut.**

Only the earlier snapshot of source474 has coefficient one on original dirt
`u_465`; its lifetime is21938–21994. Each snapshot equals its retained ordinary
source's cut coordinate `w_472,...,w_480`, so each has coefficient zero on the
independent cut coordinate `w_465`. The ordinary retained sources remain in M;
they are not discarded or treated as clean. [COPY-LIFECYCLE.json](COPY-LIFECYCLE.json)
records both notions of coefficient, all source/temporary frames and lifetimes.

An **exact isolation block** has this complete boundary:

- helper465 becomes its original dirty input `u_465`;
- every other row loses precisely its coefficient of `u_465`, and every other
  original-input coefficient is unchanged;
- any auxiliary roles start independently dirty and are restored, without
  contaminating these outputs.

Allow arbitrary finite reversible linear scalar circuits, arbitrary rational
common gate frames in Q^8 and monotone frame enlargement. Scalar XORs require
a common frame for both operands. There is no new COPY/ERASE, frame descent,
reset, clean allocation, free address map or free physical-role permutation.
Physical register identities and original target output frames are retained.
The intended helper endpoint is frame512 of rank seven; the obstruction below
does not even need to assume that successful endpoint.

After this block, suppose the suffix retains these **contacts in this order**:

| Original record | Actual ADD | Frame information propagates |
|---|---|---|
| B[48] | `163 ^= 48` | 163 to48 |
| B[117] | `48 ^= 5` | 48 to5 |
| B[493] | `5 ^= 243` | 5 to243 |
| B[601] | `111 ^= 243` | 243 to111 |

Their frame assignments need not remain original. Any number of additional
scalar gates and frame enlargements may be interspersed. Other original
contacts may be changed or omitted. There can be no legal completion with
original target111's final frame525.

### Proof

Direct replay of the pinned prefix gives

```
w_0 = u_0,       w_465 = u_465 + u_0,
dirty-column465 support = {163,381,465,474},
current frame465 =507,       current frame163 =0.
```

The required isolation row for physical target163 is therefore uniquely

```
w'_163 = w_163 + u_465 = w_163 + w_465 + w_0.
```

Uniqueness is in **independent cut coordinates**: the scalar prefix is an
invertible product of transvections after substituting its consumed snapshots.
In particular, the coefficient of cut-coordinate465 in this output is one.
Independent auxiliary dirt cannot remove that required coefficient.

**Dependency/frame lemma.** In a finite common-frame scalar circuit, a nonzero
coefficient of input coordinate i at output j implies a chronological dependency
path from i to j. Every gate frame on that path contains its predecessor's
current frame. Without descent or uncharged transport, the output frame thus
contains the input frame. This follows by induction on scalar gates; cancellation
can remove paths, but a nonzero coefficient leaves at least one path. Extra
independent dirty inputs do not alter it.

Apply this lemma to the isolation row: target163's frame contains frame507.
Frame507 contains the rational direction `e0=(1,0,0,0,0,0,0,0)` (its pinned
line0 is `2e0`). Each contact in the table forces both operands to a common
frame. Monotonicity therefore carries e0 through

```
163 --B48--> 48 --B117--> 5 --B493--> 243 --B601--> 111.
```

Frame525 is exactly the rank-seven hyperplane `x0=0`: every source basis vector
has first coordinate zero, and exact integer elimination gives rank seven.
It cannot contain e0. Consequently target111 cannot reach its required endpoint.
This proves the all-length statement, without enumerating possible isolation
blocks, auxiliary counts or rational gate frames. The argument concerns frames,
not whether scalar coefficients cancel later.

The proof is written, not proof-assistant checked. Its general dependency lemma
is the standard information-access principle used by the credited boundary
predecessors; the new contribution is this staged-isolation implication and
source-bound four-contact obstruction, not a new general rank principle.

## Scalar-positive construction and all-frame negative control

The following block realizes the exact isolation boundary:

```
frame507: 465 ^= 0
frame507: 163 ^= 465
frame512: 381 ^= 465
frame512: 474 ^= 465
```

Among all six orders of the last three clears, precisely the two that clear
163 first are geometrically legal. Their purpose is a positive control: unlike
the earlier single-common-frame block, this staged boundary itself is feasible.
It does not certify its continuation.

For a complete scalar control, algebraically track the removed helper's
non-dirty signal in the current active coordinates. This **ghost expression is
not a free physical register**: its actual reads are emitted and counted. Delete
13 later helper-writing ADDs. Replace the two helper reads by these scalar sums:

- B[653], target163: registers `0,11,63,72,247,323,345,373,432`;
- C[583], donor offset5 into381: register `0`.

The original prefix, four isolation ADDs and this fully emitted suffix use
**24,304 ADDs versus24,305**. Both forward and inverse scalar replays pass all
661 independent columns. All source/helper dirt is restored and every target
has the required increment. This is deliberately **not** called an improvement:
its geometry fails.

A separate least-join calculation permits **every rational monotone reframing**
of that scalar suffix, ignoring even its original gate frames. It also grants
the entire isolation block for free except for target163's proved mandatory
frame507. The first forced endpoint violation is B[601]: target111 requires
rank eight, with cap rank seven. The four-edge path is a shortest chronological
contact path from163 to111 through that prefix. Later ghost donor permutations
cannot affect this earlier failure. Neither legality of a finite frame catalogue
nor a search over selected frame IDs is being mistaken for all-rational coverage.

As a positive geometric countercontrol, allowing **all111 target endpoints to
be full rank eight** makes the complete emitted scalar word monotone-frame
legal. The resulting local bill is **3,085 paid children, rank mass5,239**,
including all nine rank-seven COPYs. The original bill is **2,920 children,
rank mass5,129**. This changed-endpoint control is not a supplier proposal;
relaxing only target111 is not claimed to repair every later obstruction.

## Favorable paid screen, not an achieved profile

The original helper465 frame dimensions are `0,1,4,6,7,8`; the isolated helper's
local path can be `0,1,4,7`. Granting all additional scalar, source-access,
restoration, transport and realization work for free gives local delta
`+H3-H2-2H1`. This optimistic grant is solely an impossibility screen.

For the predecessor's two-slot planning model, consume an idle rank-seven slot,
return all eight coordinates of the old slot to its remainder `r in {2,4,6}`,
and retain every other paid child, including the nine COPY/ERASE lifecycles:

```
Delta H = H3-H2-2H1-H7+H_(r+8)-H_r.
```

Rank mass is unchanged and child count decreases by three. For `p=1-a` with
`0<p<1`, concavity gives

```
Delta moment = (3^p-2^p-1) + ((r+8)^p-r^p-7^p-1) < 0.
```

The first bracket is negative; the second is at most `8^p-7^p-1<0`. The verifier
also supplies certified rational square-root intervals at `p=1/2` as arithmetic
controls. This favorable full two-slot relaxation explains why the question was
worth screening. It supplies no actual owner/window placement, changed H4
admission, precision allocation or new exponent. The geometric contradiction
holds even under that optimistic pricing, so no construction bill is silently
substituted for it.

## Reproduction and coverage

Python3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/r439-staged-retirement-boundary/verify.py
uv run --python 3.12 --no-project python -I -O -B research/r439-staged-retirement-boundary/independent.py
uv run --python 3.12 --no-project python -I -O -B research/r439-staged-retirement-boundary/literal_copies.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/r439-staged-retirement-boundary
```

Expected primary marker:

```
PASS_R439_STAGED_RETIREMENT columns=661 contacts=4 first_failure=B601 scalar_ADDs=24305->24304 controls=13 no_new_kappa
```

The primary engine uses packed F2 rows and rational RREF. The second uses sets,
independent ghost updates and fraction-free integer elimination; it imports no
primary or predecessor implementation. They agree on the complete emitted
scalar-word digest and endpoint, not just a target sample. Separate code paths
are not independent human review. The primary recomputes every certificate field;
`--emit` prints a new receipt without overwriting any file. Tests cover receipt
mutations, source corruption and source-only isolated optimized relocation.
[VALIDATION.json](VALIDATION.json) records actually exercised commands.

The13 semantic negatives omit each isolation ADD, corrupt a COPY snapshot,
omit a ghost donor or B601, remove each witness edge, change the separating
normal, or corrupt the pinned input. The copied-value lifecycle is checked as
an exact scalar snapshot contract; native COPY realization and reverse physical
routing are not claimed. The original source's notices and archives are unchanged.

The literal lifecycle audit also rejects an omitted ERASE and a second COPY
before ERASE. It runs Dylan Crow's pinned exporter as a subprocess; neither
independent scalar/geometry engine imports predecessor executable code.

## Scope, overlap and open next questions

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; independent OS-random chooser seed
`494d0ed24f025eea9e623e001763c7c4`, bit-mechanisms. The complete unrerolled output
is [SELECTION.json](SELECTION.json). The selected conditional kappa remains
`836330098538459/500000000000000000`, with the complex supplier binding.

The task is declared **changed** from the emitted H2/K card to the concrete
terminal-aware H4 handoff: PR1194 and successors already cover semantic D.
PR1256 proves first-single-frame exclusions and constructs helper470 retirement;
PR1271 supplies later-cut necessary windows but no helper465 completion. The
helper468 late-cut package concerns a different helper and explicitly leaves
staged mechanisms open. This result covers arbitrary multi-frame exact isolation
at the stated helper465 cut, but only continuations retaining the four contacts.
It does not close PR1271's unrestricted suffix question or repeat the earlier
round's two-writer helper absorption result. Exact heads, local/merged context
and overlap coverage are in SOURCES.json and OVERLAP.json.

## Open next questions

1. Can one of the four contacts be replaced or retimed while preserving all
   dirty columns and pricing every changed frame? Begin with B[48]'s source48
   read; it connects the isolated target to the frame506 source block. The
   blocker is a complete legal continuation, not another isolation-star search.
2. Can a coupled suffix delay isolation and thereby avoid the exact intermediate
   boundary? Begin with a specified alternative target163 row at cut10 and its
   target-output obligations. Its changed scalar interface, full paid profile,
   hosting and precision must be proved; the current theorem does not exclude it.

No native5/9/11-stage replay, hosted supplier, selected cold replay, all-size
compiler proof, precision/tape reduction, Lean theorem, CI success or new kappa
is asserted by this package.

## Credit and disclosure

Prepared for **Adam Gall (@adamgall)** with substantial **OpenAI Codex / GPT-6
Astra** assistance in mathematics, implementation, verification and writing.
New material is Apache-2.0; no independent human proof review is claimed.

Credit **Ali Romman** (PR1128 two-sided boundary and PR1043 earlier helper470
deletion), **Ross Richardson** (PR1256 first-restoration access and staged470
construction), **Philipp / @mightyOil** (PR1271 complete later-cut windows),
**Cinna Davis** (helper468 late-cut follow-up), **Sagar Thakrar** (PR1023 hosting
incentive and PR1062 working example), **DreamingOfClouds** (PR589), **eumemic**
(PR555/543), and the retained compiler/hosting lineage. No predecessor source
code is imported or modified; their general information-access methods and
fully specified source word are reused with attribution.
