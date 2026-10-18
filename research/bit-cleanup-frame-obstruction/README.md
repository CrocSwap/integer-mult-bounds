# Full-frame cleanup bound for R420 and the selected R439 bit word

**Status: scoped negative result, with an exact certificate and a written proof.**
For the unchanged PR543 R420 prefix and the PR589 punctured R439 prefix,
all helpers must reach the full eight-dimensional frame during any admissible
post-phase-B restoration. This covers every resynthesized cleanup circuit in
the model below, including nonlinear common-frame operations. With the native
source endpoints retained, the original cleanup attains the exact minimum local
rank moment for every `0<p<1`:

| Prefix | Helpers forced full | Minimum cleanup moment | Positive climbs | Rank mass |
|---|---:|---|---:|---:|
| PR543 R420 | 420 | `360 + 91*2^p` | 451 | 542 |
| PR589 R439 | 439 | `361 + 180*2^p + 8*4^p + 7^p` | 550 | 760 |

The result excludes early helper endpoints and cheaper cleanup frame paths
**after these fixed prefixes**. It does not exclude fewer scalar XORs, changed
prefixes, earlier restoration, a new COPY interface, or a different supplier.
There is no new kappa or changed selected construction.

Main advanced during this run to PR741 with the PR589 bit supplier. Both pinned
bit source trees remain byte-identical to the starting base. R420 is historical;
R439 is the selected bit word at that refresh. The result checks both explicitly.

## Fixed objects and permitted changes

PR543 is pinned to `2065fe4f72a914d907f1046603f5a36f17018535`.
PR589 is pinned to `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
The starting base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The submission base is `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
`SOURCES.json` pins both consumed words and their owning documentation/checkers.
No pending PR supplies code here.

Keep D, A, the nine retained-total copies and scatter, and B unchanged. Start
the replacement immediately after B. Keep the physical identities of the
original registers, including the full-frame source endpoints. Leave the final
helper frames unconstrained. Restore every source and helper to its arbitrary incoming
bit, as required by the native word interface. The result allows any finite
fixed straight-line cleanup circuit satisfying these conditions:

1. Each register has a rational subspace of Q^8 as its frame. Frames only grow
   by inclusion along that physical register.
2. Each local operation reads and writes registers at one common frame that
   contains their previous frames. Any deterministic Boolean function is
   allowed there; the result does not require linear gates or reversibility.
3. Fresh constant or independently initialized scratch and target registers may
   participate under the same rules. Their work is not assigned negative cost.
4. The circuit has no additional retained-total COPY, label reset, frame
   descent, uncharged external read, or data-dependent nonlocal control.

Rule 4 distinguishes common-frame scalar copying by XOR from the special
retained-total COPY/ERASE interface. That interface transfers scalar information
across labels and is outside this lower bound. Scalar inputs in the native
contract are independent. Exploiting physical owner correlations through a
different value contract is also outside the claim.

The lower bound concerns local native frame ranks. It does not assert optimal
global hosting, a whole-supplier bound, or an unconditional multiplication theorem.
All inherited all-size/compiler, common-label/mutable-basis, pooled hosting,
residual, precision/tape and analytic assumptions remain.

## Proof

### 1. Information cannot move down a frame

Consider any circuit satisfying the four rules. Its input coordinates at the
cleanup boundary are independent. If output r depends on boundary input s,
there is a directed path from s to that output in the circuit's information
flow graph: absent such a path, induction over operations shows that changing
s cannot change the output. This argument applies to nonlinear functions too.

Along a register edge the frame grows by inclusion. Across an operation edge,
the common operation frame contains the input register's preceding frame and
becomes a frame of the output register. Therefore every path from s to r
forces the initial frame F_s to lie in the final frame E_r. Independently,
monotonicity on the destination register forces F_r to lie in E_r. Consequently,

\[
 E_r\supseteq F_r+\sum_{s:\,\text{output }r\text{ depends on }s}F_s.
\tag{1}
\]

Extra independent scratch and arbitrary initial target values do not remove
this implication. A dependence cannot disappear from the required output
function just because the circuit uses another register along its path.

### 2. The required dependence comes from the inverse, not the forward map

Write z=(x,s) for the source/helper values: 540 in R420 and 550 in R439. The fixed A/B non-target gates
give z'=Uz over F2. Each gate is an invertible transvection. None reads a target,
so U is invertible and is independent of the incoming target values. D and the
scatter only write targets. Each target starts independently and its raw
coefficient on its own initial value remains one; no raw target feeds z.
Thus all z' coordinates and the target coordinates are independent at the
cleanup boundary. This also follows directly from invertibility of the complete
scalar prefix.

Restoration requires

\[
                z_r=\sum_s (U^{-1})_{rs}z'_s.
\tag{2}
\]

Whenever `(U^-1)[r,s]=1`, changing only z'_s flips the required output.
Reading targets or adding fresh scratch does not change that required function.
Equations (1) and (2) therefore give the necessary frame

\[
 L_r=F_r+\sum_{s:(U^{-1})_{rs}=1}F_s\subseteq E_r.
\tag{3}
\]

This uses semantic dependence. Syntactic paths that cancel in F2 are not
automatically dependencies. It also uses inverse support, which can exceed
the support of the corresponding forward row.

### 3. Exact specialization to both words

`CERTIFICATE-r420.json` and `CERTIFICATE-r439.json` supply the complete inverse
support and independent frame vectors for every source/helper output. Every
helper has eight pairs `[origin register, root-line index]`. Each origin is the
destination itself or has inverse coefficient one. Each root line belongs to
that origin's boundary frame. The eight integer vectors have nonzero determinant.
They lie in L_r and span Q^8, so equation (3) forces E_r=Q^8 for every helper.

R420 also forces all 120 sources full without using their specified endpoints.
Its 540 determinants have absolute values
`16:54, 32:291, 64:57, 128:27, 256:111`. The boundary has 89 already-full
source/helper registers. Direct inverse dependence on those registers covers
339 outputs. The remaining 201 also require dimension eight through combined
proper frames and their own frames. The certificate checks every output.

R439 forces all 439 helpers and 108 sources full. Sources **6, 19 and 22** have
semantic support spans of dimension **four**. The proof does not force these
three full from information flow alone. Their specified full-frame source
endpoints supply that requirement for the rank-moment conclusion. Their witnesses
and complete support-span dimensions are checked explicitly. A model that also
changes source endpoints requires a separate analysis.

The primary calculation follows the literal inverse z-gates and uses rational
elimination to select witness vectors. A separate calculation ignores C,
constructs U by dense Boolean forward simulation, and inverts U by set-based
Gauss-Jordan elimination. It checks full-rank witnesses with integer Bareiss
elimination and every support-span dimension by integer elimination. Boundary
frames come from reverse last-use lookup. Scatter does not move the retained
registers: R420 totals have rank eight, while R439 totals have rank seven.
Both boundaries also match the unchanged owning native checkers. Independent
integer ranks check both profiles.
These are exact calculations; no numerical rank or solver tolerance is used.

### 4. The original cleanup attains the rank-moment lower bound

For R420, 360 boundary registers have dimension seven, 91 have dimension six,
and 89 have dimension eight. For R439, the respective counts at dimensions
seven, six, four and one are 361, 180, 8 and 1. Every helper must
finish full by (3); every source must finish full by (3) or its fixed endpoint.
For any nested frame path with positive rank increments d_1,...,d_k, their
sum is the endpoint dimension difference d. For `0<p<1`,

\[
 \sum_i d_i^p\ \geq\ d^p.
\]

Indeed, after division by d^p, each term `(d_i/d)^p` is at least `d_i/d`, and
the latter sum is one. Applying this to the boundary dimensions gives the two moments
in the table. Each original C uses only full-frame gates and moves each operand
there directly from its boundary frame. Both bounds are attained. No added common-frame circuit or nonnegative scratch
charge can reduce this component. The fixed prefix, copies, existing source
access and recursive children remain paid; the optimistic screen already gives
no reduction before any extra construction or hosting cost is charged. QED.

## Reproduce and verification scope

From repository root, with Python 3.10 or later and no third-party packages:

```sh
python3 -I -B research/bit-cleanup-frame-obstruction/verify.py
```

The final line is:

```text
PASS_BIT_CLEANUP_FRAME_OBSTRUCTION helpers=420+439 independent_inverse=540+550 proper_source_exceptions=3 controls=14
```

Five negative controls per word corrupt endpoint coverage, inverse support, determinant
independence, allowed origins, or boundary frames. Another control rejects an invented
full-frame climb at the R439 rank-seven COPY boundary. Three small scope controls
exercise restoration before a later climb, cancelled syntactic dependencies,
and the distinction between forward and inverse support. Exhaustive closure of
two-register XOR/MOVE circuits on the four-frame diamond checks the information
flow condition in 652 endpoint checks across every reachable state. These finite examples support the
argument; the written proof establishes its arbitrary-circuit scope.

The certificate generator is not independent evidence. Agreement between reverse
replay and forward inversion supplies an independent check of the crucial
matrix calculation. The information-flow proof is separate from both programs.
`VALIDATION.json` records actual execution and its limits. No external human
review, proof-assistant proof or full multiplication theorem verification is
claimed. No benchmark or practical runtime improvement is claimed.

## Prior work and contribution

Credit eumemic's PR543 for the R420 word, interleaved source/helper interface,
restoration and exact checker, building on PR493. Its cumulative lineage includes
Dylan Crow's E8 decoder and native format; Zhihao Chen's mutable-source and
common-label interface; DreamingOfClouds' bit accounting; DaysSky's whole-call
hosting; and Chafik Boukhalfa's physical routes and audits. DreamingOfClouds' PR589 supplies the selected transports on eumemic's PR555
punctured word, following the PR545 and PR510 interfaces. The selected PR741
complex construction and its contributors remain unchanged.

PR760 (`6872990...`, ishan-1729) already measures omitted-cleanup restoration
debt and shows why fewer cleanup XORs alone do not improve the recursive bill.
PR661 (`9ca7aa3...`, yuj1r0) proves fixed-order phase-B frame optimality.
PR673 (`0b4f514...`, androolloyd) prices owner completion when helper work is
removed. PR437 (`ba6c10b...`, eumemic) demonstrates earlier helper resets on
a different prefix. They are context and credited predecessors, not imported
code or validation of this result. Full pins are in `SOURCES.json`.

This contribution rules out **all post-B common-frame cleanup replacements** as
a way to lower the native cleanup frame moments on these two prefixes, even when final helper
frames are initially left unconstrained. Scalar cleanup optimization remains
compatible with this result. An early-return search must instead change when
restoration occurs, change the prefix's semantic dependencies, or pay for a
different information-transfer interface. The elementary information-flow lemma
is not claimed as a new general principle or a literature priority claim.

Prepared for Charles Bethin with substantial OpenAI Codex assistance, under the
repository's Apache-2.0 license. This is internal machine-assisted verification,
not independent human peer review.
