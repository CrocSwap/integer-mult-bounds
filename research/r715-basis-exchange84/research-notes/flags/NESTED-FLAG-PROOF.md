# Nested donor flags: a sufficient extension of the kernel interface

This construction replaces the old requirement that every use of a donor have exactly the same entrance frame. It permits an inclusion chain of frames, with every actual common-frame addition and frame transition charged. No residual is split across families, and no new oracle is assumed. The existing complete-call compiler, arbitrary-dirty-helper hosting and analytic interfaces remain conditional exactly as in the parent construction.

## Universal scheduling lemma

Let P be a set of pivot registers and D a disjoint set of donor registers. A correction is a shear donor(d) += pivot(p), with p in P and d in D. Its matrix is I + e_d e_p^T. For any two such corrections, the products of their off-diagonal matrices are zero because P and D are disjoint. Thus all these shears commute, over any coefficient ring, and their inverse product is obtained by negating the corrections. This is an exact statement, not a random-input argument.

For each physical frame F, write a register value as T_F v, where T_F is the invertible frame operator and v is its logical value. A climb F to G implements T_G T_F^{-1}; it leaves v unchanged. At a common frame G, physical addition induces the same logical shear v_d += v_p. Consequently any legal common-frame schedule of the corrections induces the same logical shear product. Equal donor frames are unnecessary: it suffices that each donor visits an increasing chain of frames, each pivot is available at the frames at which it is read, and the last frame on every register embeds in the first frame required by the unmodified remaining circuit.

The complete scalar transfer and dirty cancellation must still be established for the actual coefficient model. The new finite constructor checks all955 arbitrary-dirty binary columns, exact rational frame ranks and clean integer operand supports. The independent native signed/formal-column checks supply the separate bit-compiler evidence; an F2 response equation is not silently promoted to an integer equation. Under the retained complete-call interface, the changed helper endpoint is the full-frame operator times the inverse of its new entrance operator. Its exact residual dimension is charged by the new owner allocation.

This gives a sufficient substitution rule: retain the parent response relations, change selected entrances, schedule their corrections along the verified donor flags, replay the full changed program, then use the matching whole-residual isometries and allocation. No part of the proof relies on treating a necessary response condition alone as a complete construction.

## Frozen finite instance

The source word is the updated warm PR473 word with the14 target factors and the checked paired-source cancellation. Its canonical SHA-256 is e60a092a57e71c848380ee27f0096b68c5050b18b2b5b9644d47478d76dae26c. The final word has SHA-256 86ec5a244728e90714d545d0ecb8557346577f9e5c4a265b1cad844398ba4f02.

Ten pivots are promoted from a coordinate line to a coordinate plane:

| Pivot | Old frame | New frame |
|---|---:|---:|
|721|5|291|
|752|9|293|
|787|9|960|
|802|9|960|
|804|2|294|
|846|3|959|
|899|8|295|
|906|9|293|
|911|8|956|
|926|2|294|

There are110 pivots and102 distinct donor roles. The correction prefix grows from102 rows to120 frame/donor groups; the entrance rank becomes129. Every actual donor chain is tested by set inclusion of the closed frame catalogues, not merely by comparing dimensions. Incomparable frames are rejected. Pivots and donors remain disjoint, so the unchanged full-frame cleanup is the inverse of the same logical correction product. The constructor changes only A and the initial-frame table.

The ten promotions change the local charged histogram by {1:+34,2:-20,3:+4,4:-4} relative to their source word. The resulting local histogram is {1:2419,2:1014,3:260,4:275,5:113,6:62,7:1,8:9}. The residual inventory is605 whole width8 residuals,91 width7 residuals and19 width6 residuals per call. These numbers are derived from the actual entrances, not estimates.

## Complete physical accounting

Every entrance used here is spanned by coordinate roots2e_i. Put those axes first and the remaining axes afterward. This explicitly gives an orthogonal coordinate permutation, its inverse, and the complementary residual basis. All16 distinct entrance records include the actual permutation and an elementary swap decomposition of at most7 swaps. The independent isometry checker tests the Gram matrix, the entrance projector and the full complementary span.

A newly frozen whole-residual allocation uses the same eleven-stage, eight-replica controller. The allocation matches all62,920 helper occurrences exactly and never splits one residual across physical owners. Its global paid profile is

    {1:213480,2:92899,3:22880,4:27524,5:9944,
     6:7232,7:4248,8:792,34:1,56:684}.

The rank mass is745536; with ambient dimension78 and9600 live families the deficit remains3264. The floating discovery nomination is approximately0.0012982900659383454 for the bit supplier. The release must use the independent exact moment certificate and47-constraint assembly, and must freshly charge coefficient growth from the emitted word. This note does not substitute the floating nomination for that evidence.

## Why the library search mattered

The first structural idea was matroid basis exchange: change which member of a response circuit is the pivot. Every one of331 single exchanges was exactly profile-neutral. That finite screen was retired rather than relabelled as an improvement.

The useful generalization came from flags: preserve the scalar shear while allowing its donor to climb through a chain of subspaces. Mathlib Module.Basis.flag_succ and flag_mono give the exact growing-span structure; flag_le_ker_coord_iff identifies untouched complementary coordinates. Matroid closure_exchange and closure_insert_congr supply the response-span invariance perspective. Matroid disjointSum independence decomposition motivated separating old-entrance components before combining their choices. These are source-level mathematical analogues; no claim is made that the new compiler theorem was already formalized in those files.

The native search grouped candidate promotions by disjoint original-entrance components, rejected nonmonotone chains, and combined exact histogram differences by a finite dynamic program. The selected complete words were then replayed independently. Dynamic programming is discovery machinery only; portable verification uses the frozen selection and needs no optimizer.

All source hashes, declaration names and inspected line locations are in SOURCE-PROVENANCE.json. No new Lean theorem or fresh kernel replay is claimed in this campaign.
