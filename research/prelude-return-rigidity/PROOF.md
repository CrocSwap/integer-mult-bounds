# The retained round-three prelude cannot widen at its inverse return

This is a scoped obstruction for the exact round-three native word of
Cao Yifan / PR4610, payload SHA256
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
It is not a new kappa, a fixed-model moment ceiling, or an exclusion of changed
scalar words, added warps, nonmonotone paid routes or changed main interfaces.

## Additional theorem beyond PR5096

Retain the chronological persistent scalar operands, one common subspace per
scalar contact, and ascending subspace transports on every persistent-owner segment with no
native warp. This includes the main entrance to its first contact or warp input,
consecutive scalar contacts, the last contact to a warp input, and the last
contact to its fixed main-Y exit. Keep only the actual main-X entrance lines
and main-Y exit hyperplanes fixed. All helper and owned
boundaries may be released, every other native map may change, and all native
warp incidences are cut from the containment graph.

For each j=47,...,58, consider its early positive prelude on main X owner r_j,
four scalar contacts, and inverse occurrence on that same owner. Let a_j be
the fixed main X entrance vector. Require only that those two occurrences
still use one invertible G_j and its inverse as rank-zero transported native
maps: their exact output subspaces are G_j(U) and G_j^-1(V), respectively.
This is the retained native-map contract, not merely a shared operator label.
Additional Gaussian factors inside an alleged warp are outside this theorem.
Then all four prelude scalar
contact spaces are one-dimensional, the inverse input/output spaces are
one-dimensional, and the positive prelude input/output spaces are
one-dimensional. Combining this theorem with PR5096's first-image certificate
forces the actual original pair `<a_j> -> <45>` throughout that prelude.

The exact-map relation is inherited from the transported-warp source grammar
(`research/transported-warp-frames/PROOF.md`); no source phase theorem is
re-proved by this certificate. Graph generation cuts even these two incidences;
the written closed-return proof then separately restores their exact shared-map
relation.

The new ingredient is a reverse bound after the inverse. It is not obtained
by treating two occurrences of G as independent or by reusing a floating
solver's fixed line constraint.

## Fresh source certificate

Ignore emitted climbs, retaining every scalar, warp and physical owner. At each
warp sever the containment graph. Link consecutive scalar contacts of each
persistent owner only when no warp intervenes. Link the last contact on every
main Y owner (112..223) to its actual fixed exit. Paths imply containment.

For each of the twelve inverse preludes, the next persistent event on its
main X owner is a scalar. CERTIFICATE.json provides eight literal paths from
that next scalar to fixed main Y exits. The eight independently checked normal
vectors have rank eight and common kernel `{0,a_j}`. Thus its common space N_j
satisfies

    N_j <= <a_j>.

There are 96 paths and 993 literal consecutive-contact links per orientation.
Forward and inverse-transpose source streams are checked separately. A direct
512-vector evaluation cross-checks every kernel. No path traverses a warp;
no helper boundary, owned boundary, paid rank, late native map or solver result
is used. An independently written owner-timeline audit finds all 52 reachable
main Y exits for each of the 24 direction/operator cases; their full
intersection is the same line, and it separately checks all 1,986 submitted
path links.

The operator/source-role/prelude/inverse/next-scalar records are:

| G | Owner | Positive | Inverse | Next scalar | a |
|---|---:|---:|---:|---:|---:|
|47|33|6323|6328|9067|138|
|48|55|6287|6292|8758|324|
|49|74|6293|6298|9376|352|
|50|85|6299|6304|8912|505|
|51|49|6329|6334|9061|148|
|52|83|6275|6280|9370|382|
|53|98|6281|6286|8906|487|
|54|101|6305|6310|8752|375|
|55|68|6341|6346|9678|176|
|56|80|6311|6316|9524|494|
|57|88|6335|6340|9530|477|
|58|31|6317|6322|8604|26|

Event indices are zero-based after emitted climbs are removed, matching the
PR5096 skeleton convention.

## Proof of complete prelude forcing

Write U for the positive prelude input, F_1,...,F_4 for its four successive
common contact subspaces, V for the inverse-prelude input, and W=G_j^{-1}V for
its output. The fixed main input and no earlier warp imply `<a_j> <= U`.
Monotonicity and the absence of an intervening warp give

    G_j U <= F_1 <= F_2 <= F_3 <= F_4 <= V,
    W <= N_j <= <a_j>.

Apply G_j^{-1} to the first chain. Since `<a_j> <= U <= G_j^{-1}V=W`,
all inequalities close to

    <a_j> <= U <= W <= <a_j>.

Hence U=W=<a_j> and V=G_j<a_j>. Every F_i is between the same nonzero line
G_j<a_j> and itself, and therefore every F_i equals that line. This argument
already excludes rank widening without invoking PR5096's first-image bound.
PR5096 additionally gives F_1=<45>, fixing the actual vector image and the
original inverse return pair.

Thus releasing only the later scalar contacts and inverse-prelude frame pair
cannot enlarge the retained graph's native-map feasible set. The public
PR4610 next question must change another premise to escape this obstruction.
This does not dispute PR5096's proof: that earlier certificate bounded the
first positive prelude and explicitly left later contacts outside its theorem.
This certificate supplies the previously unused post-inverse bound.

## A graph-change positive control

The scope restriction is material. In each orientation delete the single
consecutive-scalar edge `(9067 -> 9068, owner 33)`. Every other native warp is
still cut. Exact reverse intersections now permit the next scalar at 9067 to
have the three-space `span(75,138,288)` instead of `<138>`. The fourth prelude
contact at 6327 permits `span(5,40,73)`.

The control assigns every scalar node the intersection of all its reachable
fixed exits, keeps every main X entrance fixed, and checks all 31,741 remaining
containment edges. All hold. The explicit invertible map with columns

    [1,2,8,16,128,256,22,63,329]

sends 138 to 45 and maps the first displayed three-space onto the second.
Both bijectivity and all 512 images are checked. Thus the reduced containment
model really permits a wider inverse return, rather than merely failing to
find eight paths. This is a positive control for the relaxed graph model,
not a priced changed native circuit or a complete shared-G construction.

## Reproduction and credit

`python3.12 -B research/prelude-return-rigidity/verify.py` checks the paths, exact
normals and six corrupted-certificate and one source-byte rejection controls.
`python3.12 -B research/prelude-return-rigidity/edge_control.py` checks the one-edge
positive control. The registered replay is read-only and verifies deterministic frozen receipts.
The explicit `--write` flags are authoring commands, not registered replay shortcuts. No shared checkout or upstream source was modified.

Credit Cao Yifan / intqwq for the exact PR4610 native word; Cinna Davis /
1337isnot1337 for PR5096's first-image forcing, the joint-helper/controller
construction and retained lineage; Dugongue for transported frames; zxv for
native/compiler work; Jacob Alan Sussman for mixed-target recursion; and the
retained source authors. New inverse-return certificate and proof prepared
for thu-nmrc with OpenAI Codex assistance. The separate owner-timeline audit
was written by another Codex research agent. No independent human or formal
proof-assistant acceptance is claimed. Apache-2.0.
