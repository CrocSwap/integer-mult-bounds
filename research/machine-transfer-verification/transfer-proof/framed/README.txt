Concrete address gauges and selected PR64 local forward phase verification
=======================================================================

Result and scope
----------------
AddressGauges.lean proves 19 new address-transport theorems, with only the
standard Lean axioms propext, Quot.sound and (in the matrix interface)
Classical.choice. A clean isolated Lean 4.21.0 build also recompiles the
unchanged DirtyWrapper and FramedXor dependencies. This package does not
assert a complete formal proof of the multiplication theorem.

full_forward_phase.py checks a concrete full FORWARD LOCAL invocation of
each selected PR64 XOR mixer, including its actual clearing gates. It is
not another scalar Boolean replay. Every literal XOR incidence is assigned
matching current address gauges. Every paid auxiliary transport is rebuilt
from that full phase schedule. The resulting binary CRT profiler input is
byte-for-byte equal to the existing independently verified input.

The local h=23/h=25 words are PR62's pair graph and PR57's joint compiler,
with PR60's descending-current-frame-rank reclamation priority. Their source
pins and credit are preserved in ../../finite-frames/source-word-manifest.json.
They are the words selected and published in PR64; this package does NOT
relabel them as newer PR67/68 constructions. The existing analytic and floor
recurrence formalizations also refer to the selected PR64 literal profile.

Source word SHA-256 (decompressed JSON):
  h23 640696dd7cd893add9d6e12d0d587956fecf113b2eff8c29547b82e5a6f3c0ad
  h25 7a827318eff45db1183d66e80d38ddbd4ce321bbc033d2effb7afa438d6b63a9
Original graph/compiler source pin:
  ad0f25ff7b23cff7f08ad237c2254e6ecf74257e (PR62).
Rank-order source: PR60 e7a492dd8bee4e6f574ced784a62af2ce735edc4,
  Chafik Boukhalfa; pair graph: Avi Eisenberg; joint compiler: eumemic.
Published package checkout used for comparison:
  PR64 790a14e28e935398072b9a9a68694ce7fba8940f.

The phase assignment, including all four traversals
-------------------------------------------------
Write D_U for the partial swap associated to the orthogonal projector onto U;
D_0 and D_1 are its identity/full-space endpoints. These are LOCAL labels.
A surrounding tensor construction can replace these by appropriate ambient
backgrounds; that replacement is an explicitly remaining obligation below.

The chronological wrapper is L,J,L^-1,V,L,J,L^-1,V. Starting frames are:
  auxiliary: D_0; target data: D_0; source T: D_<t_T>.
1. L uses D_0 on every auxiliary.
2. J reads D_0 auxiliary values into D_0 target values.
3. L^-1 remains at D_0.
4. Raise each injected auxiliary to its source triple line; apply V.
5. Execute the actual recorded L, raising BOTH incident auxiliary roles to
   each recorded frame before its XOR, including paid clearing operations.
   Raise retained output slots to their exact terminal frames.
6. Execute J with all center reads first, then sides grouped by target.
   For a center at U_i, allocate a new blank complete role stream, clone it
   once, move the copy from D_U_i to D_0, perform all its literal fanout
   reads, then erase only that temporary. Raise the original to D_1.
   Original auxiliary values may be arbitrary; no original role is cleared
   destructively. Each target then rises to its triple-perpendicular frame.
   Each of its three side roles follows the explicit three rank-one steps
   below, and is read exactly at that same target-perpendicular frame.
7. Raise every remaining auxiliary to D_1; run L^-1 entirely at D_1.
8. Raise source data from its triple line to D_1; perform the final V there.
Ending frames are auxiliary/source D_1 and target D_(t_T perpendicular).

Only traversal 5 varies auxiliary frames. Traversals 1,3,7 are common-frame
XOR circuits. Thus the scalar word has four L traversals, but the auxiliary
transport list has one varying L trajectory. No factor four is missing
from this local transport comparison. Reordered late scatter preserves the
complete literal incidence multiset, not merely its parity. FramedXor's
scatter_permutation and copied_fanout_correct justify these two macros.

Actual side flags
-----------------
For T={i,a,b}, the recorded side envelope is E({i}, [h]\{a,b}), rank h-3.
Its basis is b_j=e_i+2e_j for j outside T. With G=I-J/9:
  <b_j,b_k>=4 delta_jk; <b_j,t_T>=0.
Put w=e_a-e_b. Then <w,w>=2, <w,b_j>=<w,t_T>=0, and <t_T,t_T>=2.
The checker forms these actual sparse integer vectors and checks every
identity after multiplication by 9, as well as support/envelope membership.
Their Gram matrix proves independence and nondegeneracy; the envelope's
one linear equation proves the basis spans it. Hence the actual flag
  E < E+<w> < t_T perpendicular < Q^h
has three successive rank-one differences of nondegenerate orthogonal
projectors. This is stronger than assigning three abstract rank labels.
The ambient metric is nondegenerate because h is 23 or 25, not 9.

Counts and cost boundary
------------------------
                                    h=23             h=25
  source/target roles v               1,771            2,300
  auxiliary roles R                 27,918           36,586
  literal gates in one L            149,172          205,915
  scalar wrapper XORs               621,482          855,860
  fresh complete-stream clones           23               25
  wrapper + clone XOR equivalents  621,505          855,885
  explicit side flags                5,313            6,900
  side rank-one transports          15,939           20,700
  auxiliary rank mass              642,620          915,250
  distinct paid transitions        138,003          190,879
  displayed extra data rank         77,924          110,400

The scalar wrapper XOR count excludes the fresh clone macros. Each clone
is one XOR-equivalent pass into a blank temporary; copying and erasing
also have separate O(stream volume) costs. Erasure is not a reversible XOR
on an arbitrary dirty role. These counts do not purport to count every
physical tape instruction. The JSON reports count every phase separately.

The auxiliary mass is hR+h(h-1). The two data transitions for each triple,
D_0 -> D_(t perpendicular) and D_<t> -> D_1, are exposed separately. Each
has inherited local profile (1,h-2); this new checker does not rederive that
profile. Auxiliary exterior blocks, ambient data fronts, the two-direction
assembly, and the paid final data endpoint correction are outside this
local profile comparison. The binary equality binds to the existing CRT
input; the CRT rank/profile proof is supplied by the earlier independent
finite verifier, not re-run by this phase checker.

New Lean content
----------------
shearGauge distinguishes address PUSHFORWARD new*old^-1 from payload
PULLBACK old*new^-1. The former has matrix new-old and the latter its inverse.
The three original ordered address updates are proved to produce interchange.
partialSwapGauge is an actual permutation over any additive commutative
group whenever the supplied endomorphism is idempotent. Nested orthogonal
projectors give D_Q D_P = D_(Q-P), with both absorption directions explicit.
Complementing and reversing a path preserves the exact residual, not merely
its rank. The selected endpoint theorem derives all-role physical interchange
from a typed trace, a scalar role permutation, and complementary endpoint
projectors. Matrix and ZMod(q^f) interfaces are provided.

The address module is not the Boolean payload. Eligibility of a common odd
prime must exclude 3 and every prime dividing the relevant finite rational
denominators, Gram determinants and certified nonzero pivots. Nothing here
infers the matrix equations or profiles for every q, or supplies a ring map
from all of Q to a finite ring. See field-and-transfer-assessment.txt.

What remains genuinely outside these checks
------------------------------------------
The Python schedule is not a generated Lean Trace term. Its concrete labels
have not yet been embedded into every ambient tensor background of the
complete two-direction construction. The complete reverse copied-center
schedule and the final paid endpoint correction have not been generated
and checked here. The existing reverse/transposed scalar replay alone is
not that full physical schedule. Rational frame reduction at one eligible
common prime and the fixed-basis residual compiler's tape realization/cost
remain separate interfaces. Fixed-tape movement, parking, copying, descriptor
costs and the resulting uniform physical recurrence are not proved by this
package. The Lean matrix/permutation semantics and this finite local schedule
reduce these obligations; they do not discharge them by renaming them.

Reproduce without writing tracked inputs
---------------------------------------
Use Python >=3.10; tested with Python 3.12. No third-party Python package.
From this workspace root (replace python3 if needed):

  python3 outputs/transfer-proof/framed/full_forward_phase.py \
    --word outputs/finite-frames/pair-ranked-word-23.json.gz \
    --manifest outputs/finite-frames/source-word-manifest.json \
    --receipt outputs/finite-frames/pair-ranked-23-receipt.json \
    --binary outputs/transfer-proof/framed/inputs/ranked-23.bin \
    --output work/full-phase-check/forward-23.json

Repeat with 25 in all three dimension-specific paths. The same command
accepts the word, manifest and receipt from a fresh PR64 checkout under
research/ranked-pair-verification/finite-frames; it has no hardcoded checkout.
The manifest's irrelevant historical files section is not consumed. Receipts
record the actual supplied manifest hash, so the two manifest variants will
produce different provenance hashes but identical mathematical checks.

  python3 outputs/transfer-proof/framed/test_phase_rejections.py \
    --word outputs/finite-frames/pair-ranked-word-23.json.gz \
    --manifest outputs/finite-frames/source-word-manifest.json \
    --receipt outputs/finite-frames/pair-ranked-23-receipt.json \
    --binary outputs/transfer-proof/framed/inputs/ranked-23.bin \
    --output work/full-phase-check/rejections.json

The seven controls modify only an in-memory checker copy: omitted incidence
transports, stale copied frame, unpaid copy, omitted late scatter incidence,
missing cleanup, and a false side flag. Every malformed schedule is rejected.
Selected source words and files are never rewritten.

With lean/lake 4.21.0 on PATH and an existing Mathlib project pinned to
308445d7985027f538e281e18df29ca16ede2ba3 (v4.21.0):

  python3 outputs/transfer-proof/framed/check_lean.py \
    --lake-project /path/to/pinned/lake/project \
    --output /absolute/path/to/new/build-directory

The script installs nothing, checks source and dependency pins, compiles all
three modules into its own olean directory, and audits 13+18+19 printed axiom
reports. Delivered build logs and verification.json came from that isolated
command. Prior proof bundles and the published PR were not modified.
