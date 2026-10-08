Complete ambient finite schedule correspondence, PR64 and PR71/73
================================================================

This bundle checks the actual two-direction copied-center schedule, including
its ambient tensor backgrounds, auxiliary exteriors, both data fronts, and the
final paid rank-one correction. The two enormous stages are represented by
exact indexed replication of local words, not by eagerly expanding billions
of duplicate XOR instructions. It is a finite schedule/profile correspondence
check, not a complete Lean Trace or a fixed-tape running-time theorem.

Results are separated by immutable source:

  PR64 selected words, source graph pin ad0f25ff7b23cff7f08ad237c2254e6ecf74257e
    verification/full-ambient.json
    W = 137151806; total charged rank = 78860441550.

  PR71 network 1bef94fd40a746452548c84a4a8f8834670a3113,
  read at PR73 pin 253ecc88faeed55a950c76026d1fe67a7f690123
    frontier/full-ambient-pr71-73.json
    W = 135075665; total charged rank = 77666660475.

Both use m=575, N=4073300 and deficit 1846900. The latest report directly
matches m,N,W,total_rank,parts,all child multiplicities and maximum child to
PR73's public research/round6-pr71/parameter-certificate.json and records its
hash. This bundle does not recompute an exponent saving or silently retarget
the older analytic theorem; each analytic bundle has its own literal input.

New versus reused evidence
--------------------------
NEW: concrete reverse-chronological, inverse-and-bank-renamed gate schedule,
with all current gauges checked and complete input/dirty basis replay. The
h25 reverse check covers 41186 basis directions for PR64, or 40615 for PR71.
It includes actual clearing gates and all center-copy/side dispatch. It is
not the reverse-transposed scalar replay used by the inherited word checker.

NEW: exact ambient boundary and endpoint operator calculation, actual rational
triple-line projectors and their fixed I+J coordinates, and universal controlled
corner entry-index identities. These identities hold for an arbitrary local
matrix, not randomly sampled matrix entries. Both local profiles are linked
to precisely the charged ambient tensor residuals, including complementary
reverse paths whose residual matrix is exactly unchanged.

NEW: TensorStageFrames.lean proves 21 declarations (19 theorem declarations
and 2 helper lemmas) about the ACTUAL matrix tensor embeddings over any
commutative ring. No numerical rank is substituted for a matrix. Each has a
printed axiom audit; only propext, Quot.sound and Classical.choice occur.
The module proves identities/idempotence/absorption, not rank preservation.
The separate localization bundle transports these rationally checked identities
to every eligible ZMod(q^f), with one finite denominator localization.

REUSED: complete scalar forward dirty-basis and fixed-basis CRT local-profile
certificates, already bound to exact serialized word hashes. PR64 uses the
prior independent ranked audit; PR71 uses the freshly completed independent
PR71/73 audit and exported deterministic profiler inputs. No new CRT run is
performed. The complete reverse charge lists equal those binary inputs byte
for byte, not just in total mass. PR73's inherited geometry files are compared
byte-for-byte with the pinned PR62 files.

REUSED: exact fixed-basis exterior profiles (h,m-2h); local data growth profiles
(1,h-2); and the full data-corner profile (nine singletons,21,17,481) for every
actual triple pair. The latter is charged 2N times, hence 18N singleton calls.
The pinned data-corners source and exact recovery code are recorded. Their
existing all-pair pivot certificates are not independently rederived here.
The new work establishes the physical residual/class correspondence and exact
complete profile summation using those inherited certified widths.

Exact two-stage construction
----------------------------
Let a=23,b=25. P is the actual a-triple orthogonal projector and Q the actual
b-triple orthogonal projector, in metrics I-J/9. Their normalized rank-one
form is t*(t^T G/2). For every actual triple the checker verifies that formula,
normalization and its exact fixed I+J conjugate:
  primal t+3*1; dual t/2-5*1/(3(h+1)).
All coordinates are nonzero. It checks all 1771+2300 actual lines.

Define tensor frame embeddings
  first_Q(U) = U tensor Q,
  second_P(U) = (I-P) tensor I + P tensor U.
The first is multiplicative when Q^2=Q. The second is multiplicative when
P^2=P, with second_P(0)=(I-P) tensor I and second_P(I)=I. Both preserve local
projector idempotence and absorption. In a transition U->V the residual is
  (V-U) tensor Q, or P tensor (V-U).
Thus the second stage's nonzero background cancels in every internal residual;
it is not omitted from the current gauge. These are Lean-proved equations.

Stage 1 holds the b-triple fixed, executes the actual h23 forward local word,
and has data boundaries
  X: P tensor Q -> I tensor Q,
  Y: 0 -> (I-P) tensor Q.
Auxiliary roles begin at gauge zero and end at I tensor Q, then receive the
charged exterior I tensor (I-Q), ending at gauge I.

Both data fronts are the same ACTUAL residual
  (I-P) tensor (I-Q).
They take X to (I-P) tensor I + P tensor Q, and Y to (I-P) tensor I.

Stage 2 holds the a-triple fixed and executes the PHYSICAL inverse word with
X and Y bank names exchanged. Its local starting gauges are X's triple line,
Y's zero, and auxiliary zero, under the second_P embedding. The reverse
phase details below give final local gauges X=I,Y=Q-perpendicular,auxiliary=I.
Hence ambient data endpoints are X=I,Y=I-P tensor Q.
The auxiliary input gauge is D0=(I-P) tensor I, not zero. After the local end I,
the charged descending exterior I->P tensor I has involutive residual D0.
The ORIGINAL auxiliary endpoints D0 and I-D0 are complementary; their product
is full interchange. The exterior is charged, not a free gauge reset.

The two scalar shears give (x,y)->(y,x+y), restoring every original auxiliary.
Accounting for the initial data frames (D_(P tensor Q), identity), the physical
outputs are A=D_I y and B=D_I x+D_(I-P tensor Q)y. Make ONE new blank complete
stream, clone A at gauge I, transport that copy to gauge I-P tensor Q using
the rank-one residual P tensor Q, and XOR into B at that matching gauge.
Only the temporary is erased. This cancels the second term of B. The physical
outputs are (D_I y,D_I x). Undoing the data bank exchange at merge yields full
interchange on every original role, including arbitrary dirty auxiliaries.

Reverse invocation (the previously missing phase check)
-------------------------------------------------------
The forward chronological wrapper is L,J,L^-1,V,L,J,L^-1,V. Inverting the word
reverses chronology but DOES NOT transpose each XOR gate. Renaming source X
and target Y then gives the opposite shear. The local reverse phases are:
  1. Initial V from Y into auxiliary, all at D0.
  2. Early L, all at D0.
  3. Early J into X: sides first, then centers.
     A side follows 0<t_T<(E+<e_a-e_b>)^perp<E^perp, reading X exactly at t_T;
     X then grows to full space before any center read into it.
     Each center original grows directly 0->U_i^perp (rank one); a new copy
     goes U_i^perp->full (rank h-1), supplies all center reads, and is erased.
  4. Reverse the remaining forward cleanup, then execute L^-1 in reverse
     chronology at complementary recorded frames. Gate target/source stays
     unchanged. Every incident role has exactly the required current frame.
  5. Raise Y to its triple perpendicular and perform the cancelling V.
  6. Raise remaining auxiliary roles to D1, then late L at D1.
  7. Late J into X at D1.
  8. Late L^-1 at D1.

The explicit side flags are complements/reversals of actual rational flags
checked on all selected terminal indices. Their residual projectors, and all
other internal reverse residuals, equal the original forward residuals.
This explains the exact binary charge equality. Early J preserves every
literal scatter incidence; no read or clearing operation is removed.

Compact replication and original role layout
---------------------------------------------
For 0<=s<v_a,0<=t<v_b, use X(s,t)=s*v_b+t and Y(s,t)=N+s*v_b+t.
Stage1 auxiliary(t,r)=2N+t*R_a+r; stage2 auxiliary(s,r)=2N+v_b*R_a+s*R_b+r.
These disjoint consecutive product ranges cover exactly W original roles.
Stage1 runs once per t (2300 invocations); stage2 once per s (1771 invocations).
Both preserve their entire distinct auxiliary banks. The only sharing between
invocations is the explicitly indexed data bank; stage1 and stage2 run in order.
One local common-frame identity lifts for EVERY fixed factor projector by the
Lean tensor identities. Thus exact indexed replication is sufficient; expanding
roughly three billion XOR events would add no independent mathematical check.

The controlled common basis uses physical index 25*alpha+beta. The checker
constructs all 25 permutation completions from the actual first47/last47 labels.
It verifies symbolic coefficient indices for every entry of the 23,25 and47
corners. A local residual's first-h/last-h corner is its entire local matrix
scaled by nonzero row/column factors. It contains the full residual rank and
has the same ordered pivot pattern. No separated pivot positions are gathered.
This derives preservation of the REUSED local profiles; it does not re-prove
the separate exterior/data-corner Schur and nonzero-pivot certificates.

Cost boundary and remaining proof work
--------------------------------------
complete_profile.parts reconstructs the two local internal lists, both exterior
classes, both pairs of local data growths, both data fronts, and every paid final
rank-one correction. The masses match the selected profile exactly. Counts also
expose fresh center and endpoint clones. Every clone is one XOR-equivalent pass
into blank storage; copying and erasing additionally have linear stream costs.
Every temporary has the existing complete role volume V/W, including spectators.
It adds a sequential fixed stream, not another original row-coordinate family.
Original dirty auxiliary values are never destructively cleared.

The finite schedule is checked in Python and its reusable algebra in Lean;
there is no mechanically generated complete Lean Trace term for all 137 million
(or 135 million) original roles. The profile linkage uses earlier exact pivot
certificates as stated above. This bundle does not compile the residual blocks,
ordered affine wrappers, splitting, movement, parking, descriptor updates and
copies into one fixed-tape program with a proved uniform O(V) node cost.
Those are the remaining physical recurrence/refinement obligations, alongside
the separate retained analytic multiplication interfaces.

Reproduction
------------
Python >=3.10, tested 3.12. No third-party Python package; git is needed only to
read immutable local object contents. Scripts do not fetch, reset or change a
checkout. An exact source-file change is rejected, while unrelated worktree
metadata is not reset. Choose fresh output directories as below.

From the workspace root, PR64:

  python3 -B outputs/full-transfer/framed/full_ambient.py \
    --upstream /path/to/checkout-containing-PR62 \
    --word-dir outputs/finite-frames \
    --profile-inputs outputs/transfer-proof/framed/inputs \
    --certificate outputs/selected-certificate.json \
    --prior-audit outputs/audit/ranked-candidate-adversarial.json \
    --output-dir work/recheck-ambient-pr64

Current public PR71/73 (independent audit completed first):

  python3 -B outputs/full-transfer/framed/verify_frontier.py \
    --frontier /path/to/PR73-checkout \
    --geometry-upstream /path/to/checkout-containing-PR62 \
    --audit-dir outputs/full-transfer/audit \
    --output-dir work/recheck-ambient-pr71-73

The frontier schema-views are explicitly labeled adapters of exact pinned
compiler/profile/transition JSON objects. They do not invent or replace any
counts. The independent assembly's rank_mass receives only a total_rank field
alias. Direct public parameter-certificate comparison supplies a second binding.

  python3 -B outputs/full-transfer/framed/test_rejections.py \
    --word-dir outputs/finite-frames \
    --profile-inputs outputs/transfer-proof/framed/inputs \
    --output work/recheck-ambient-rejections.json

Seven controls reject: transposed reverse mixer gates, omitted original center
transport, unpaid reverse copied transform, missing endpoint correction, wrong
copy residual, missing stage2 exterior, and a wrong data-front residual. Only
in-memory checker copies are mutated. Original certificates remain unchanged.

Lean/lake 4.21.0 must be on PATH; the existing Mathlib project must be pinned to
308445d7985027f538e281e18df29ca16ede2ba3. The command installs nothing:

  python3 -B outputs/full-transfer/framed/check_lean.py \
    --lake-project /path/to/pinned/lake/project \
    --output /absolute/path/to/new/tensor-build

Declarations and meanings are in proof-manifest.json. Clean delivered logs are
verification/TensorStageFrames.log and verification/verification.json.

Attribution: Paureel's paid endpoint correction and two-stage topology; icekylinx
copied centers and partial-swap construction; James Chang's reversed geometry;
Rohan Arun's fixed data-corner certificates; Avi Eisenberg's pair graph; eumemic's
joint compiler and later live/retired controls; Chafik Boukhalfa's ranked priority;
all further source notices remain with the immutable upstream files. The new
checker, reverse schedule audit and tensor-matrix formalization extend the
previous framed verification work without changing historical bundles or PRs.
