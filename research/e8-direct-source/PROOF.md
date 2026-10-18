# Remove root copies by reading the sources at their actual frames

This changes only the depth-one paid-copy provider of PR647, pinned at
`956bb581e7f97328e1b53baa5aca3d2490f2f607`. Its root labels, E8 coefficients,
positive Gaussian charts, three-stage cover and RAM model are retained.
This is an alternative supplier improvement, not a multiplication frontier.

## Construction and the removed expense

Use the predecessor's 120 ports p_t in F2^9, rank-eight factorization
K+BA=I, source charts P_t=p_t p_t^T, and target caps I-P_t. The real
coefficients A, B and K are rebuilt from the root formulas. The old core
allocated 120 dirty root input helpers, moved them from zero to P_t and
added source x_t. Those helpers supplied all pair and gather reads; each
source separately moved from P_t to FULL after its last use.

In the new word the source register itself supplies those reads. For each
pair K_ts != 0, while source s is still at P_s:

1. Move its pair helper from zero to P_s and add source s.
2. Move the pair helper to I-P_t, add K_ts times it to output helper t,
   then finish it at FULL.

K_ts != 0 implies p_t dot p_s=0, so the intermediate move is legal. After
**all** pair reads, grow source s from P_s to FULL and perform its eight
possible A_js gather updates at FULL. No earlier source read remains.
The output helpers stay at their caps; gathers and all consumed helpers
finish at FULL. No source-access oracle or uncharged source descent is used.

There are 120 output helpers, 6720 pair helpers and eight gathers:
R=6848, down from 6968. Every target is still at zero when the copied centers
are decoded; it then grows to its cap, receives its output helper, and that
helper finishes at FULL. Sources are already FULL at cleanup.

## Arbitrary dirt and the two orientations

Disregarding charts, let the complete core act on sources and helpers as

    x -> x,    H -> L H + V x.

Here L is the helper-only word consisting of the 6720 pair-to-output adds.
The other 7456 adds read the actual sources: 6720 pair loads and 736 gathers.
Let J read the outputs plus the B combination of the eight centers. Since
K+BA=I, JV=I. L is an explicit invertible shear word; no inverse oracle is used.

Before the core, at frame zero, copy the R helpers to an initialized private
tableau, execute L there, and subtract JL H from the targets. Decode B with
120 initialized private intermediates and 456 adds. Clear the tableau and
intermediates. Neither sources nor source copies are read by this macro.

After the core, copy each of the eight FULL centers to its own private array,
pay its FULL-to-zero child, and apply the B decoder to the zero-frame targets.
Clear the intermediates and center bank. Then perform the cap/output reads.
The net logical target change is J(LH+Vx)-JLH=x. At FULL, execute the entire
core ADD list in reverse order with negated coefficients, including the source
reads. This restores H exactly and leaves x unchanged. Thus

    F: (x,y,H) -> (x,y+x,H).

For the backward orientation apply inverse adjoint to the **complete live
macros**, preserving chronological order. A scalar `t += c*s` becomes
`s -= c*t`; unitary frame transitions remain unchanged. The old-response
macro becomes H += L^T J^T y, implemented by a private tableau seeded with
J^T y, the reversed transpose helper-only list, and R additions into H.
The center macro computes B^T y at zero, pays eight zero-to-FULL children,
subtracts into the live centers, and clears the private bank. It is not the
transpose of a CLEAR instruction. Cleanup is the transposed original core
list in reverse order. The same endpoint charts give

    B: (x,y,H) -> (x-y,y,H).

The local charts may all carry a common orthogonal background Q in a cover
invocation. Scalar gates commute with T_Q, private copies retain that background,
and an initialized zero private array may be assigned its chart. Center children
change only the local window. Thus this rewrite preserves the source
background/whole-helper interface as well as the zero-background calculation.

Sources can be targets of backward ADDs. Each transposed ADD has equal
operand frames, so this does not require a free frame change. All helper
off-diagonal and helper/data residuals vanish. `verify.py` checks these two
identities symbolically on every one of the 7088 independent live columns.
It also checks every chronological move/ADD frame and every endpoint.

For a transition projector P, the source's pinned exact basis/phase checker
checks a positive C_rank child with two address permutations and its binary
translation, on a determining set for the quadratic phase. Downward transport
includes the additional diag(P) translation. The pinned utilities are reused
and attributed, not described as independently reimplemented. Optimized
Python is rejected because those utilities use assertions.

## Complete finite price

| Quantity | PR647 depth one | Direct source |
| --- | ---: | ---: |
| Live helpers R | 6968 | 6848 |
| Live columns W=R+240 | 7208 | 7088 |
| Core ADDs | 14176 | 14176 |
| Helper-only old-response ADDs | 14176 | 6720 |
| Local forward ADDs | 44160 | 36464 |
| Local backward ADDs | 51136 | 43320 |
| Local forward COPYs | 6976 | 6856 |
| Local backward COPYs | 0 | 0 |
| CLEARs per orientation | 7216 | 7096 |
| Private tableau/decoder/center arrays | 7096 | 6976 |
| Local recursive children | 20896 | 20656 |
| Global recursive children | 62928 | 62208 |

Forward ADDs are 6720+2*14176+2*456+4*120=36464: the helper-only old
response, main and cleanup, both decoders, and their/root-output target reads.
Backward adds R+8 because the inverse adjoints of the forward copies add into
live arrays. COPYs are R+8; CLEARs are R+2*120+8. The private namespaces are
disjoint, initialized, and cleared. A single additional permutation work array
is explicitly owned. Each permutation is a scatter/copy-back/clear, charged
linearly in its array length. Pointwise ADDs pay coefficient multiplication,
addition, source/target reads and target writes; COPY/CLEAR pay their accesses.

The whole cover uses forward/backward/forward. Per owner it therefore has
116248 ADDs, 13712 COPYs and 21288 CLEARs, plus at most twice the child count
in address permutations, one translation per child, 120 final translations
and 120 signed exchanges. Workspace initialization is bounded by 6977 zero
writes per entry per cover owner (a conservative bound: the bank is cleared
and reused between complete invocations). Address-table construction, role
routing and loop/index work are charged as in the fixed-depth predecessor.
No private buffer is a borrowed zero input. During a center child the other
nonzero center buffers remain in the caller's protected segment, disjoint from
the child's fresh workspace; the tableau and decoder buffers are zero.

The old local histogram loses 120 rank-one loads and 120 rank-eight moves.
The latter cancellation compares the old input-helper climb plus late source
climb to the new single source climb. Multiplying by three gives

    H = {1:40680, 2:240, 7:20160, 8:1080, 9:48},
    m=27, W=7088, sum s H(s)=191352=27*7088-24.

The center-copy bill remains 24 rank-nine global children; none is removed.
Both source and target endpoints, all cleanup, and 240 final rank-two children
are included. The positive deficit stays 24. The improvement is a smaller paid
profile and live width, not a larger deficit.

## Exact moment and full cost recurrence

At eta=1/14100, exact rational log/exponential bounds give

    27W - sum_s s H(s) (27/s)^eta > 11/100.

For the old histogram and W=7208, a rational **lower** bound on its moment
gives negative slack at the same eta. Thus the larger admitted value is a
consequence of this new word, not finer rounding of the old profile's exponent.
The source's earlier explicit certified eta was 1/15000. Eta here is a
Gaussian-RAM provider saving; it is not integer-multiplication kappa.

The endpoint maps F/B and all data charts are unchanged. Drop precisely the
120 input-helper role types from each owner in the source's three-stage cover;
the remaining helpers use its same block-swap routing. Each still undergoes
one independently restored full-window transform in each of the three blocks.
The source's explicit route identities and signed final exchange therefore
continue to give C_27 on every live input. No helper-sharing hypothesis changes.
This proof reuses the pinned all-owner argument; it does not enumerate O(27,2).

For completeness the inherited padding/recursion price can be restated with
the new numbers. Set a=27^2+ceil(log2 W)=742, L=2^a, and G=|O(27,2)|. Enumerate
matrix labels directly, with orthogonality tests; no group-ranking oracle is
needed. All L-GW unused matrix/role slots contain actual input and each pays
an ordinary full-window transform. If

    B_s = G H(s) + (L-GW) * 1_(s=27),

then the normalized moment is strictly below one by more than

    11 / (100 * 27 * 2^742),

because G>=1. For input exponent ell=a+27k+b, 0<=b<27, first pay ordinary
butterflies on the a+b role/remainder bits. Dilate the explicit finite word.
For t(ell)=T(ell)/2^ell its complete recursive cost satisfies

    t(ell) <= A + sum_s (B_s/L) t(sk).

A is a finite architecture constant paying every scalar, copy, clear, adapter,
source access, allocation, address table and routing operation listed above.
All child exponents sk<=ell-a-b<ell, including ordinary padding children.
Strong induction using the strict normalized moment yields
T(ell)=O(2^ell (ell+1)^(1-1/14100)). Fresh recursive workspaces are disjoint;
child array sizes shrink by at least 2^-a, giving linear workspace by a geometric
series. These are the predecessor's exact complex RAM and integer-word model,
with fixed depth one. No finite-precision, tape, compiler-to-multiplication,
or supplied-root Fourier extension is newly established here.

## Scope and evidence

The construction is explicit and can be regenerated from source; the receipt
binds the two chronological words by SHA256. Arbitrary-dirt symbolic checks,
frame/phase checks, scalar invoices and exact moments support the proof. Seven
negative controls remove old response, misroute/drop seed-selected source 26,
climb it early, omit cleanup, reverse a center direction, or remove center cost.
Separate tests execute 48 modular physical character instances across two
fields, both directions and 12 characters. Those tests include actual Gaussian
phase factors and private-center descent/ascent; they are finite corroboration,
not a formal proof or a giant end-to-end transform implementation.
