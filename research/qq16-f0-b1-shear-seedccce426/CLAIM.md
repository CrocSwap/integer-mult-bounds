CLAIM — QQ16 F0-to-B1 selected A/T shear using existing query width (Cycle 38; recursive-interfaces, priority revision 4)

**Assignment pins:** selector seed `ccce426f938ce02908e39f554d0187b2`; task `joint-query-controller`, key `0e34adbc1dd119161c3a`; exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

**Object / question:** Insert the reversible selected-state shear immediately after F0 and before B1: `X_T <- X_T + X_A`, `Y_T <- Y_T - X_A`, with all other fields fixed. Does this make the actual post-B1 selected output injective on the eight-dimensional selected-input defect from the fixed QQ16 witness, while using the existing query and recursive-child counts?

**Changed assumption and bounded method:** Permit one A-to-T shear on the already-produced selected fields, with identity coordinate map only. I will derive the exact 8-by-8 transfer on the pinned witness span using the actual QQ16 selected sections and ordered B1 maps, then compare identity shear, zero shear, and a sign-corrupted control. The experiment covers this witness span and this one shear; it does not claim a full controller or all-size supplier.

**Optimistic full local charge:** 16 scalar additions per owner (eight to X_T and eight to Y_T), eight copied values hosted in existing selected fields, zero new helpers, zero added recursive children, and no new coefficient precision for C=I. The B1 and F0 children stay as before. Frame/address transitions and restoration are provisionally granted free for the initial screen; any exact map or hosting cost found in the route calculation will be added. The local source/F0/B1 invoice remains 211210/214986 scalar primitives with 8/24 added rank-one children before the shear. The favorable selected profile has only two rank-one-equivalent operations of slack after an ideal rank-eight output charge, so any added child is a stop condition. No supplier or κ gain is presumed.

**Nearest work / distinct contribution:** PR #2086 treats arbitrary changes to the first A logger with the old T output fixed and names changed T records as open. PR #2093 and the completed B2-read work add ordinary-source observations. PR #2174 recovers pair 0 only with privileged post-B1 selected-cut values. PR #2189 gives a read-only transcript-width bound. This scope instead changes the selected state between the two calls by an invertible sum-preserving shear; no extra observation is added. The live exact-term scan at 23:47Z covered 445 open PRs and 892 Discussion records with complete pagination and no warnings, and returned no matches.

**Expected result / stop:** an exact rank-eight transfer or a counterexample on the witness span, with a source-bound reproducible check and charged local operations. Stop if the map is not injective or if implementation needs any extra recursive child. Claim expires 2026-10-15T01:50Z.

**Predecessor credit:** Ali Romman and the retained joint-query lineage (PR #1969) supply the local maps and witness; Cinna Davis (PR #2079) and Adam Gall (PR #2093) supply adjacent observation analyses. Substantial AI assistance from OpenAI Codex.

## FINDING — exact witness repaired at the B1 cut

The all-route group-algebra replay passes for all eight pinned `h_k`
directions. It verifies `B1 h_k=0`, the `2112 I` identity coefficient of
`B2 h_k`, rank eight in the post-F0 A field, rank zero in the zero-shear B1
T output, and rank eight in the sheared B1 T output. An exact eight-row
minor has determinant `-1/4096`; its group-map keys and rational
coefficients are in `RESULT.json`.

The shear costs 16 scalar additions per owner at the common `completed(0)`
frame, uses existing A/T fields, preserves selected sums, and adds no
helper, cover map, precision, or recursive child. This is a fixed-witness
interface mechanism, not a full controller, supplier, or kappa result.
Package and source pins pass; the final verifier passed locally on Python
3.14.7. The registered package replay targets Python 3.12 and remains for
hosted CI.
