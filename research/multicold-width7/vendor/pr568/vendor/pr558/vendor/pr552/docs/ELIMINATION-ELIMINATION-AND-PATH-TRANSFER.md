# Exact circuit reductions from elimination and path algebra

These are sufficient constructive transformations. No new global originality claim or Lean certificate is made. Sources actually read and hashed are in SOURCES.json. The electrical analogy is exact Schur elimination of an internal linear variable; no positivity, passive-network or electrical complexity bound is imported into the circuit model.

## A. Eliminate a cold internal register while retaining reversible semantics

Let a linear straight-line program over a field use background registers z, targets y and one designated cold internal register h. No target feeds a background register. The raw program may interleave background and target updates. Its compensated endpoint is (z,h,y)->(z,h,y+Jz) after literal inverse cleanup of its background updates. Initial h is arbitrary dirt and its target contribution is cancelled by the explicit input preconditioner.

The following algorithm is a sufficient elimination procedure, provided every emitted nonzero coefficient and inverse is allowed and every emitted frame passes the ordinary incidence checks. Simulate the old program with initial h=0. Maintain an exact expression h=sum_j g_j z_j in the CURRENT surviving registers, rather than in stale inputs.

* At h+=a*z_s set g_s+=a. At h*=a multiply all g by a. Emit neither old update.
* At a surviving z_t+=a*z_s not reading h, emit the update and change g_s to g_s-a*g_t. At z_t*=a, divide g_t by a.
* At a read z_t+=a*h, put lambda=1+a*g_t. Require lambda!=0. Emit z_t*=lambda followed by z_t+=a*g_s*z_s for every s!=t with nonzero g_s. Then divide every g coefficient by lambda. These formulas are precisely one-coordinate Schur elimination and its reconstruction map. When t is a target, g_t=0 by the no-feedback assumption, hence lambda=1.

Proof of the invariant: after an ordinary surviving addition, substitute old z_t=new z_t-a*z_s into the maintained expression. For a read of h, new z_t=lambda*old z_t+a*sum_(s!=t)g_s*z_s. Solving this equation and substituting into h divides every coefficient by lambda. The required nonzero pivot is explicitly checked; it is not an assumed oracle. Induction now proves equality with the old h=0 execution on every surviving input column. Restrict the old initial dirt preconditioner by removing its h term, or recompute the exact response preconditioner. Regenerate inverse cleanup from the actually emitted background sequence. Every emitted update is invertible by its checked lambda or elementary transvection, so surviving background dirt is restored. The target map is the same J on all surviving inputs. The deleted register has no physical initial value to restore.

For the framed compiler, each added read/write must climb monotonically to its actual gate frame. Every fill-in addition, scale, inverse scale, cleanup gate, copy and normalization wrapper is charged. Deleting a helper does not itself establish a kappa gain: it changes local rank mass and the required residual inventory together; the new complete global assignment and invoice are compulsory. For dyadic circuits, exact denominator/pivot checks are additional sufficient hypotheses, tested on a constructed witness rather than replaced by arbitrary-field division.

A one-variable example is h=a*x+b*z, y+=c*h with h initially zero. Eliminating h emits y+=ca*x and y+=cb*z. For arbitrary initial h, the old preconditioner contributes -c*h_initial; the new program has no such coordinate. This example demonstrates correctness, not an uncharged saving: the two products and both cleanup implications must be billed.

## B. Whole-region path transfer and triangular factorization

Time-expand every linear assignment: each register version becomes a vertex, carry edges have weight1, and an addition creates an edge with its actual scalar coefficient. The resulting graph is acyclic in time. The coefficient from a boundary input to a boundary output equals the sum of products of weights over directed paths. Proof is induction on the destination time: updating a coordinate adds exactly the paths whose final edge is that update. Thus two finite regions with equal exact boundary path matrices can replace each other on arbitrary input/dirt columns.

A useful special case is a unitriangular region. Its strict-upper matrix N is nilpotent, so (I-N)^-1=I+N+...+N^(d-1). Every entry of N^k is the sum of k-edge path weights. Schur elimination removes an internal vertex by adding each incoming-weight times outgoing-weight to the corresponding boundary edge. Repeated elimination therefore computes the same finite path sum, including all length-three and longer cross terms. The construction terminates after the finite vertex set is eliminated; it never assumes an unknown circuit synthesis oracle.

For three ordered vertices, the exact source theorem gives

  U = T12(U12) T13(U13-U12*U23) T23(U23).

The correction U13-U12*U23 subtracts the length-two path already created by the outer factors. In larger regions one may eliminate coordinates in a fixed order, reading the residual coefficients after each step. Equality follows inductively from elementary row identities, not from matching an approximate objective. This is a region-level procedure, rather than the last round's fixed seven three-gate cells.

A replacement becomes a sufficient compiler optimization only after: exact boundary matrix equality; legal actual frame labels for every new gate; unchanged or explicitly reconstructed retained-copy interfaces; regenerated background inverse; full paid profile and coefficient-prefix recount; and any changed whole-owner inventory allocation. No equality of unframed transfer matrices alone makes an illegal physical frame move admissible.

## Bounded application record

Current target was the tn24 complex syndrome word, the binding supplier after public PR543/545 improved the bit side. Native C++ gates tested284 cold helper eliminations with explicit current-expression substitution: all were rejected by the prescribed fixed-frame incidence gate. Another screen multiplied1,669 maximal equal-frame regions and found no coordinate whose boundary row AND column both became identity, so that narrow coordinate-removal resynthesis had no nominee. Exact signed critical-pair comparisons found235 legal candidates with no paid improvement. The same bounded screens were rerun on root's avalanche8 frame rewrite, with the same counts and outcomes.

The helper-elimination nominator uses a prime-field support image only; no successful exact characteristic-zero witness or impossibility statement is claimed from it. Likewise, the equal-frame gate is merely a cheap nomination filter for one restricted reduction. These are not barriers to other Schur decompositions, alternate frames, new source words or larger path regions. The universal sufficient transformations above remain applicable when their explicit checks pass.

A preliminary old-bit screen also found seven further rank1+rank1->rank2 merges unlocked by the preceding Steinberg word. That smaller bit route became nonbinding when PR543/545 arrived and was not represented as a new numerical contribution. No native or final kappa claim is attached to these two routes in this round. Root's independently constructed frame avalanche, if fully admitted, is the numerical candidate.
