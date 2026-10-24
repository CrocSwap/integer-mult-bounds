# Exact native-map cancellation on the fixed source word

## 1. Scope

The input is the final PR4610 word after the credited PR5350 constructor.
All 632 persistent inputs are arbitrary. C0 is owned and returns zero.
The output is a new scalar/native word with the same physical endpoints,
frame contacts and recursive invoice. This proof does not establish a higher
kappa, a practical speedup, or an optimum among linear circuits.

## 2. Normalize each field before comparing ADDs

Write the current value in field r as

    y_r = c_r G_r z_r,

where c_r is a nonzero rational scalar and G_r is a word in native maps and
their inverses. Initially c_r=1 and G_r is empty. A SCALE changes c_r. A warp
W changes G_r to W G_r. Adjacent inverse letters reduce in the free group.
Only this exact inverse rule is used; no finite-column coincidence is assumed.

An ADD y_r += a y_s acts on the normalized values as

    z_r += (a c_s/c_r) G_r^-1 G_s z_s.

For r distinct from s, two such ADDs on the same ordered pair commute and
combine by coefficient addition when their normalized native words agree.
Two ADDs on pairs (r,s) and (u,v) commute if r differs from v and u differs
from s. This follows by multiplying their elementary block matrices: both
cross terms vanish. It holds for noncommuting operator coefficients.

The constructor scans back only across this commuting relation. A source
write or target read stops the scan. A CLEAR or COPY stops it on each of its
operands. Thus it does not move an ADD through an overwrite or a dependent
operation. When it combines two coefficients at the later contact, it converts
the sum back to that contact's actual scalar factor. A zero sum deletes both
ADDs. A nonzero sum replaces the later scalar coefficient. Every intermediate
native map and SCALE remains in place at this step.

Consequently the changed logical word is an exact identity in the free
operator algebra. It holds for any representation of the native maps,
including their actual absolute phases and every allowed column multiplicity.
This algebraic statement does not discharge the inherited all-size native
implementation assumption.

## 3. Remove native maps with no remaining contact

For each field, the second pass tracks native maps between scalar contacts.
A scalar read, write, COPY or CLEAR ends that interval. SCALE commutes with a
native linear map. Within one interval, adjacent inverse letters cancel.
This includes letters separated by operations on other fields.

Climbs are coordinate changes in the logical frame representation. The
constructor keeps every paid climb record. After the logical simplification,
both retained native interpreters check the actual input frame of every
warp, the common frame of every scalar contact, each paid transition, every
persistent output, and the owned return. This is necessary: logical equality
alone would not prove that the changed record list has legal physical frames.

For a legal framed word, substitute the frame map at each contact. Each
internal frame map cancels its inverse at the next operation. The physical
endpoint is therefore the final frame map, followed by the logical word,
followed by the inverse initial frame map. Since the initial and final maps
and the logical operator are unchanged, the physical endpoint is unchanged.
All paid edges and all surviving warps have the original exact phase recipes.
No new edge or monomial operator is introduced. The historical recipe proofs
are reused; this replay does not run their full phase-lowering suite again.

## 4. Exact effect on the complete bill

The pass follows the PR5350 compressor. Per orientation, it removes 42 scalar
ADD records and 60 of its 240 warp records. The source scalar allowance uses
coefficient size; it is not a flat price per ADD. The extra allowance saving
is exactly 236. Including PR5350, the reduction from PR4610 is 193 scalar
records, 60 warps and 1452 scalar allowance units per call.

Both orientations retain every PR5350 paid record in its chronological order.
They also retain the original PR4610 role/frame/rank transition census. The
paid profile is

    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.

The main and helper endpoints and all helper inputs are unchanged. Hence all
productive jobs are unchanged. For every exponent t, both sums of r^t in the
complete controller invoice are identical to their previous values. The
recursive moment and kappa do not improve. If the same word is used in all
18 full calls of the retained p16 controller, the local count differences
multiply by 18; that statement is arithmetic, not a new whole-controller run.

## 5. Evidence and limits

The deterministic receipt contains both retained all-column interpreter
results, the generated program hashes and source-event patch. Dense rational
controls check dependency barriers and scalar normalization. An actual scalar
sign mutation fails both native interpreters in both orientations. The source
files are pinned by bytes and Git blob.

There is no new independent native interpreter, cold selected replay, uniform
compiler, BIT supplier, precision/tape implementation, analytic recovery,
formal-kernel proof or end-to-end integer-multiplication check. The five
selected framework assumptions remain. Independent human review is open.

Credit Cao Yifan, Cinna Davis, ahrazzle, Chrisbryan17, Dugongue, zxv, Jacob
Alan Sussman, and all retained source authors. Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0.
