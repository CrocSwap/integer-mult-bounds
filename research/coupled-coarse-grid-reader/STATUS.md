# Worker C status — 2026-11-06T04:15:09.572471+00:00

Proved candidate (root audit requested): for fixed A=[[1,2],[-2,1]], M=2^b, integer source box [-B,B]^2 and arbitrary dirty helpers, the GLOBAL minimum over every integer lift L of the worst squared Euclidean coarse-output error equals

min(ceil(3B/M)^2, 2*ceil(B/M)^2).

A is a concrete member of PR6666's complete [-2,2] 2x2 census. It is an algebraic retained cut, not a literal native P104 cut. Phase identity and matrix-residue method are explicitly credited to PR1135; scalar coarse-reader law to PR6685; exact dyadic-capacity context to PR5615 and approximate response to PR6666.

Proof: D=A L-MI obeys d11-2d21=-M mod5 and d12-2d22=2M mod5. If D has one nonzero row, its integer l1 norm is at least 3. If D has two nonzero rows, some z in {-1,0,1}^2 makes both row products nonzero, hence x=Bz makes each magnitude at least B. det(A)=5 is odd, so helper phases fill all M^2 residue vectors independently and attain both rounded coordinate extrema simultaneously. Zero D is impossible.

Attainment: balanced D cycles -I,J,I,-J as b mod4; it is a signed permutation. Concentrated D=[[u,v],[0,0]], centered residues u=-M mod5 and v=2M mod5, has |u|+|v|=3. L=adj(A)(MI+D)/5 is integral.

Exact precision thresholds: error <=1 coarse cell requires b>=ceil(log2(3B)); error <=sqrt(2) cells requires b>=ceil(log2 B). Same Smith form diag(1,5) has a different Euclidean minimax ceil(s_b B/M), s_b=1 for even b and 2 for odd b, showing geometry is not determined by Smith factors.

Six-register reversible lowering: each reader temporarily forms H1+2H2 in H1, adds M/2, translates Y1 by the non-mutating arithmetic-right-shift bit view, then undoes; similarly H2-2H1. Reader restores H itself. Full four-call word: 2P(L)+12 signed word ADDs and 8 constant translations for b>=1; zero constants omitted at b=0. No clean word, source scaling, destructive shift or runtime odd division. The full width/headroom proof is in PROOF.md §§7–8 and the literal word is in reader.py. Normal and optimized warning-strict exact checks pass with matching receipts; registered metadata and both replay modes pass. 17,050 execution/inverse fixtures, 250 complete histograms, 93 global finite optima, 14,091 residual candidates, 640 headroom corners 130 lift-commutation cases and 16 internal rejection controls. Two actual temporary-file corruptions also reject. Root independently checked the central mathematical case argument; formal/human acceptance is unclaimed. Mathematical work and logical implementation are complete; final amended-commit replay and export are being verified for handoff.

No kappa, physical gain or productive target credit. No selected cold replay or source-closure PASS.


Added physical restriction: if L must commute with quarter-turn J (Gaussian-linear lift), the sharp squared optimum is always 2*ceil(B/M)^2. Balanced lifts attain it; concentrated lifts do not commute with J. This does not assert full rounded-word covariance. Source-history check refused shallow checkout; byte/mode check, official export and empty-PATH permission-read-only direct replays passed. Final handoff will name the exact amended commit and matching receipt; no ancestry PASS.
