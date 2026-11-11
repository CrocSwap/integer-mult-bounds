# Independent review of the changing-node CRT state package

Reviewer: dispatcher research worker, separate from the analytic author worker.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
This is model-assisted mathematical and source review, not human or proof-kernel
acceptance. Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

## Outcome

**Pass for the stated source-relative composition after one proof correction.**
The exact source seam, protected-word entry, close-before-write ownership
boundary, balanced-tree induction, complete row invoice, and rolewise storage
bound support the scoped claim. The full binary evaluator, payload permutation,
uniform topology/source production, exceptional key composition, and selected
foundational assumptions remain outside it. No multiplication or kappa change
follows from this review.

I read the package proof, implementation and receipt, the actual #6100
workspace/query source and proof, the #5625 adapter and proof, the #5353 RowEntry,
the #5219 Port/Entry implementation, the numerical Word boundary, and the
retained explicit-width logical Caller and balanced CRT definitions. All pinned
scientific input bytes and the single declared geometry substitution passed separate
SHA256/Git-blob checks. The predecessor paths have no changes relative to the
base in the author worktree. The task-catalogue provenance row is historically
bound by package metadata and is not treated as a live scientific input.
The reader-facing author package is still being
finished; file hashes of the reviewed core are in RESULT.json.

## Defect found and corrected

The initial proof asserted

    sum_G (P_G+2)^2 < (4/3)(ell+3)^2 d^2.

This is false. For ell=20, d=16 and every width20, the left side is

    8*43^2 + 4*83^2 + 2*163^2 + 323^2 = 199815,

whereas the asserted upper bound is 541696/3. This width family admits
pairwise-coprime moduli, so it is not merely outside the theorem domain.

The author replaced it with the valid bound

    sum_G (P_G+2)^2 < 2(ell+2)^2 d^2 <= 32p^2.

For a size-n node, n>=2 and P_G+2<=n*ell+3<=n(ell+2).
There are d/n nodes at that level. Thus the relevant geometric series is
d(ell+2)^2 times sum(2^j), which is strictly below 2d^2(ell+2)^2.
Finally (ell+2)/(ell-1)<=4 and d(ell-1)<=p. The changed coefficient
fits the existing quadratic allowance; the final majorant is unaffected.
The author added this exact counterexample as a failure-detection control.

## Independent semantic argument

The #6100 workspace stores backing, owner identities and geometry; it stores
no width-dependent numerical object across rows. The exact new seam allows
level/start to change while preserving the width tuple and ell. The actual
#5353 RowEntry reconstructs the unary guide from the selected current source
records, appends one guide bit, and therefore supplies precisely
P_G=1+sum_(i in G) h_i. Numerical words/template, canonical and padded streams,
and ROM headers are rebuilt using that guide. The saved Python capacity does
not choose numerical branches. Its bounds check remains satisfied on the
inherited valid delimiter-driven execution.

The eight ProtectedZeros roles satisfy the missing width-sensitive premise:
at every active entry each is LEFT, exactly P_G zero bits, RIGHT, at head1.
They are distinct from the source, staging and 118 owned row roles. The
inherited numerical entry preserves their values/heads; the new caller then
physically retires them before any change of precision. A shorter next word
does not expose stale bits because the whole historical extent was already
blank. A larger next word grows through actual Port reads/writes/moves.

The #5625 consumer first copies the returned output into staging, then calls
the query's close. This retires all numerical/ROM roles and invokes
Workspace.end. Only after that release does the consumer write the supplied
source coordinate fields. It scans the actual source and restores its head1;
the staging tape is erased and returns to head0. The new caller preserves
this order. An all-idle node-row is explicitly skipped and uses no tape work.

At a fixed level, different aligned nodes are disjoint, and every operation
reads left-child coordinates while changing only right-child coordinates.
Serializing nodes within a row therefore equals the logical simultaneous
row. Left-child state is fixed throughout all rows of that level, so every
new query recomputes the same controls as the published level transform.
For padded states, each inherited row is still an involution; reversing the
entire chronological list (levels, rows and nodes) gives its inverse.

On globally valid inputs there is also a direct induction on a parent node.
If its children encode mixed-radix integers K_L and K_R in locally scaled CRT
form and S_L is the product of left moduli, the parent integer is
K_L+S_L*K_R. A right coordinate with right-local prefix Q changes from
K_R/Q modulo its modulus to

    K_R/Q + K_L/(S_L Q) = (K_L+S_L K_R)/(S_L Q).

This is precisely the current-left offset computed by the source. Left
coordinates already have their parent prefixes. The root therefore yields
the defining complete CRT formula. This endpoint proof uses the inherited
local arithmetic/ROM correctness; the review does not replace those contracts.

## Independent cost checks

Direct counting of the actual Port methods gives a first protected-word
prepare-and-retire cost of 10P+23 raw actions per word, and 10P+24 on reuse
(one extra reverse move to the blank origin). Consequently the eight-word
cost is strictly within the declared 4096(P+2). Initial eight blank cells
remain separately charged. The independent executable checks this exact
formula through nine growth/shrink transitions, including 256 down to4.

The independent invoice sums numerical entry, all per-axis ROM producers,
query work, staging/source update, the 370 stable-entry allowance, and the
protected-word allowance directly over node records. Its implementation
uses the independently simplified axis summand 3h*2^h+3h+5. It equals the
author's complete invoice in all 744 tested width domains; it is not a
rerun of the author verification implementation or the large ROM interpreter.

The corrected universal moment bounds are consistent. For n=2^j, there
are d/n nodes. Quartic, quadratic, cubic-with-target-count, and linear-pair
sums respectively reduce to the geometric series in 8^j, 2^j, 4^j and
2^j. They give 715p^4, 32p^2, 6p^3 and 15p^2 as used in the repair.
There are fewer than2p rows per node. The quartic contribution is below
2^31 p^5; the quadratic contribution is at most2^22 p^3. A direct coarse
bound puts all remaining non-ROM terms below2^20 p^3. The total ROM
coefficient before rounding is 46,875,000 times
2^(3ell) p^4 (ell+1)^4, hence the claimed48,000,000 bound with(p+1)^4
is safe. A second copy absorbs the axis-query summands. These estimates
fit below2^34*2^(3ell)*(p+2)^8. The p>=14 comparison follows from
2^ell*(p+2)^8>=4*16^8=2^34.

The role inventory is 58 fixed numerical word/template/guide roles, five
numerical streams, 52 ROM roles, three query roles, eight protected words,
and staging:127 owned roles. Adding the separate supplied source gives
exactly the proof's envelope. Bounding each of the52 roles by a complete
bank bound is loose but valid. Each role's maximum is taken separately, so
reuse does not hide blank historical capacity. No external topology or
source-generation allocation is folded into this inventory.

## Reproduction and limits

When installed under the reviewed package's independent-review directory,
run from the repository root:

    python3 -I -B research/crt-whole-tree-state/independent-review/independent.py

The separate working copy also accepts an explicit --package-root argument.
The script is read-only by default; --write-result explicitly regenerates the
receipt after the reviewer has inspected any changed core inputs.

Expected:

    PASS_INDEPENDENT_SCOPED_REVIEW 744 9 3

The test checks all declared input pins, the exact seam, invoice equality,
forward/inverse schedule, four corrected moments, the majorant, and the
actual protected-word lifecycle. Negative controls detect live resize,
stale historical data, and the original false geometric inequality.
The random width families use seed20261110; the full tested domain is
ell2..32, d in(2,4,8,16,32,64), and four declared families per pair.
These are finite corroborations; the quantified arguments are above.

The author's 500-million-instruction numerical/ROM suite was deliberately
not rerun by this reviewer. Its receipt was inspected, not independently
regenerated. Final author normal/optimized registered replay and a frozen
commit remain publication gates handled by the author and orchestrator.
