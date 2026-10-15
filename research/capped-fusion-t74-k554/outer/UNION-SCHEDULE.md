# Radix-distributed sparse-union schedule (new in this package)

**Status.** This schedule is a new contribution of this package. It is not part of PR1673 (Vlado Vojdanovski, whose capped phase-cell fusion
construction and PHASE-LAYOUT-AUDIT.md this document modifies and relies on), nor of PR1699 (Chafik Boukhalfa, Le Gall's exponent). It replaces
one step of PR1673's sparse-union window, the per-axis scan of U, and is conditional on every other hypothesis of PR1673. Its executable finite
check is `outer/sched_test.py`; the arithmetic consequence is `outer/check_ledger.py`. An independent review is required before release.

## 0. Model and what is replaced

Machine model: PR1673's fixed-tape model, i.e. a multitape Turing machine with a fixed number of tapes; the cost of an operation is the total head
travel; a record is a p-bit coefficient record with a header of O(g log L) bits (g=p^beta, L=poly(p) the microbox side, beta<1, so the header is o(p)
and moving it multiplies the cost by 1+o(1)). V is the number of records of the microbox (including spectators). All notation (E_i, J_i, T_i, mu,
W, B, d, g, L, the windows) is that of PHASE-LAYOUT-AUDIT.md and the capped interiors of CAPPED-INTERIORS.md; mu = max_i |E_i|/L = O((W/B) polylog p).

A sparse window applies the Kronecker product `Theta = (x)_{i=1..g} T_i` to the microbox tensor, where `T_i = I_{E_i^c} (+) T_i|E_i` (for the window
containing the C and S^-1 stages, T_i is the product of the two sparse factors of axis i; each is block diagonal in the same way).
The audit's implementation scans the union U = {x : some x_i in E_i} once per axis to copy U_i = E_i x [L]^(g-1): cost O(|U|) per axis, hence
`O(V [g^2 mu + g mu polylog p])` per window and the union row `eps + beta + 1/2 - xi`. Here the g-fold scan of U is removed.

## 1. Flag sets and class decomposition

For a record x put `F(x) = {i : x_i in E_i}` (the g membership flags the audit already computes in the single scan that forms U; stored as a g-bit vector
in the header).

**(F1) invariance.** `T_i` changes a coordinate x_i only inside E_i and fixes E_i^c, and maps E_i to E_i. Hence `F(Theta x) = F(x)`: every T_j preserves every class
`C_F = {x : F(x) = F}`.

**(F2) commutation.** Each T_i depends only on the axis-i coordinate (and on axis i's own coarse label/page, fixed per microbox), so T_i acts on tensor factor i alone; the T_i act on different tensor factors, hence commute, and on class C_F the operator Theta equals `(x)_{i in F} T_i|E_i` on the coordinates in F
(range E_i) tensored with the identity on the coordinates not in F (the T_j, j not in F, are the identity on E_j^c).

**(F3) complete lines.** Fix F, f in F and the other coordinates z (all coordinates except x_f). The *E_f-line* of z is {x : x_f in E_f, other coordinates z}. Every point
of it has the flag set `F(z) union {f}` (flags of z-coordinates plus f), so the whole E_f-line lies in one class, and contains exactly |E_f| points.

## 2. The schedule

Let `f_r(F)` be the r-th smallest element of F. Define `S_r = {x : |F(x)| >= r}`, kept as a stream in lexicographic order of x (S_1 = U; S_{r+1} is S_r with
the records |F|=r deleted, so lexicographic order is inherited).

Round r (r = 1,2,...,R, where R = max |F| <= g) applies to every record x of S_r the operator T_{f_r(F(x))} along axis f_r(F(x)), to complete E_f-lines (F3).
After the rounds, every record of class C_F has received T_i exactly once for each i in F (the f_r(F) enumerate F), in increasing axis order;
by (F2) this equals the action of Theta. Since lines of the same round and class are disjoint and independent (F2), applying T_f to each line separately equals
the action of `T_f|E_f (x) identity` on the class. Rounds use the values written by earlier rounds because records carry their current values in the stream.

### 2.1 One round (cost accounting per step; N = |S_r|)

1. **Tag.** For each record compute `t = f_r(F(x))` from its header bits: O(g) bit operations (scan for the r-th set bit). Worst case a record has |F| = g and takes g rounds,
   so tag work per record is at most O(g^2) bit operations in total over the schedule, which is o(p) because 2*beta < 1 (ledger check `union_tag_work_fits_record`).
2. **Stable binary LSD radix distribution by tag.** For k = 0..ceil(log2 g)-1: scan the stream; records whose bit k of the tag is 0 go to output tape Z, bits 1 to tape O
   (one input tape, two output tapes), then Z is copied followed by O back onto the work tape. Each pass costs <= 2N record moves; the bits of the pass are written (N bits)
   to a bit tape together with the count n0 of zeros. *Stability* by induction on k: after pass k the stream is ordered by (bits k..0 of tag) with ties in the original order.
   After all passes: ordered by tag, ties in lexicographic order; the stream splits into contiguous axis substreams, one per tag value f.
   Inversion (used in step 5): replay the passes in reverse: copy the stream onto Z/O at the stored split point n0 (one pass), then read the bit tape and take the next record from Z or O accordingly.
   Cost 3N per pass. Total O(N log g) = O(N log p).
3. **Structure of an axis substream (the key lemma).** Axis f substream = {x in S_r : f_r(F(x)) = f}. Membership depends on F(x) only, and F(x) = F(z) union {f} for x with x_f in E_f (all substream records
   have x_f in E_f, because f is in F(x)); so it depends on z only, not on x_f. Therefore for each fixed prefix x_<f the substream restricted to that prefix is
   `E_f x Z'(prefix)` where the suffix set Z'(prefix) = {x_>f} is the same for every x_f in E_f. In the stream (lexicographic order of (prefix, x_f, suffix)) the prefix block is the concatenation of
   a = |E_f| rows (one per x_f in E_f, in increasing order), each row listing the same b = |Z'(prefix)| suffixes in the same order. No coordinate is invented: every needed point is present.
   Block boundaries are detected by comparing the prefix fields of consecutive records (O(g log L) bits per comparison, o(p)); rows by the ordinal of x_f in E_f stored in the header
   (computed with the flags: the rank of x_f in E_f costs O(polylog p) with the carving description) -- no counter of unknown length is needed.
4. **Variable-length lockstep transpose of every prefix block** (brings x_f to the line suffix). Let `a = |E_f| <= L = poly(p)`. All rows of a prefix block have the same length b within a tag (point 3), b unknown to the routine. Recursively halve the row index range into the upper part of ceil(a/2) rows and the lower part of floor(a/2) rows (the implementation uses chunk sizes h = floor(a/2) for the first child and a-h = ceil(a/2) for the second; either order works, the tree must be the same for every block and its inverse).
   Level structure: a balanced binary tree of row ranges of depth ceil(log2 a) = O(log p), the same tree for every block. *Merge of a node*: its children's outputs `TA` (rows 0..h-1 in suffix-major order,
   i.e. for each suffix the h records of A's rows) and `TB` (the a-h rows of B) are read in lockstep from two tapes, taking h records from TA, then a-h records from TB, alternately, until both end markers
   coincide; the output is the node's suffix-major order `[row_0[j], ..., row_{a-1}[j]]_j`. The routine never needs the row length b: the chunk sizes h and a-h depend on a alone, and the end of the node's data is
   the end marker (prefix-block boundary, or the stream end). A level is realised by two passes over the whole substream. Every record carries in its header the ordinal k of its source row x_f. The data of a node (a range [lo, lo+n) of ordinals) is a contiguous run of records of one prefix block whose ordinals lie in the range; its child A (ordinals [lo, lo+h)) comes first, immediately followed by child B (ordinals [lo+h, lo+n)), so the junction is the first record whose ordinal is >= lo+h, and the end of the node is the first following record whose ordinal is >= lo+n or whose prefix field differs (both read from headers; the tree is the same for every block and nodes appear in row order). Pass 1 copies the A-parts to tape M1 and the B-parts to tape M2, node by node. Pass 2 reads M1 and M2 in lockstep, h records from M1 then n-h from M2, node by node (a node's A- and B-parts end at the same node marker), writing the parent level. So a level costs O(N) record moves and the whole transpose O(N log a). After the transpose, each line (fixed prefix and suffix) occupies a consecutive group of a records with increasing x_f ordinal.
5. **Apply T_f on lines and batch.** Each consecutive group of a records is a complete E_f-line; T_f|E_f is applied exactly as in the audit's step 4: consecutive lines form right-hand sides, batched in dyadic width between W and 2W,
   factor pages (regenerated once per microbox and axis from its coarse origins, polynomial in p, amortised by the superpolynomial payload) scanned once per batch, only the polynomial-width row field moved
   (O(log p) times the boundary volume). This arithmetic is the *boundary-algebra row*, unchanged and not part of the union movement.
6. **Undo** the transpose (unzip levels), then undo the radix distribution (step 2 inverse): the processed records are back in lexicographic order of S_r.
7. **Split.** One scan: records with |F| = r are final for this window; push them (with the |S_r|-bit indicator keep_r = [|F| > r]) on the LIFO tape; the rest, S_{r+1}, is written to the alternate work tape.

### 2.2 Wrap-up

After the last round, pop the LIFO tape: for r = R,...,1 interleave `rest_r` with the already final stream S_{r+1} by keep_r (the audit's merge by indicator), producing the final S_1.
Finally merge S_1 into the microbox using the indicator bits of the single scan that formed U; identity records (F = empty) are never moved.
The two dense-stage scatters/regathers, the one scan forming U and the final merge are the audit's group scans: O(V polylog p) per window, in the group-scan row.

### 2.3 Tape-head accounting (per round, and why rounds do not multiply the cost)

Tapes: W1, W2 (alternating work tapes carrying S_r), Z, O (radix outputs), Tb (bit tape), STACK (LIFO), M1, M2 (merge/zip tapes), small header/counter tapes: a fixed number.
* W1 holds S_r written from cell 0; before round r the head is at cell 0 (rewind over the written length |S_r| only; cells beyond are stale and never read).
* S_{r+1} is written to W2 from cell 0, then the roles swap. Rewinding costs the written length, at most |S_r|.
* STACK is only appended to at its end and, in the wrap-up, read backwards from its end; the rest_r are consecutive, so popping costs the sum of |rest_r| <= sum |S_r|. No head ever travels over the whole of
  the stack or of U per round.
* Z, O, Tb, M1, M2 are written from cell 0 and rewound over their written length (<= |S_r| records or bits).
Hence the head travel of round r is O(|S_r| p (log g + log a + 1)) and the total is O(p (log g + log L + 1) * sum_r |S_r|). The rounds are sequential, but their *number* does not multiply the cost: |S_r| shrinks and
nothing in round r touches data outside S_r.

### 2.4 Volume identity

`sum_r |S_r| = sum_x |F(x)| = sum_i |U_i| = sum_i |E_i| L^(g-1) * (spectators) <= g mu V.` (Each record is counted once per flag; the first equality is exchanging the order of summation.)

## 3. New cost and row

Per window: `O(V g mu polylog p)`; no factor g^2 and no per-axis scan of U. Per group, then over d/g groups:

`O(V (d/g) g mu polylog p) = O(V d W polylog p / B)`,

i.e. union-movement exponent `eps + 1/2 - xi` (saving `xi + 1/2 - eps`). Old audit row: `eps + beta + 1/2 - xi`.
The identity `sum|F| <= g|U|` shows the new cost is never larger than the old one.

*Sparsity is not used.* In the regime of this package the expected number of flags g*mu = p^(beta+1/2-xi) is larger than 1 (xi - beta - 1/2 < 0), so U is essentially the whole microbox, and the audit's ledger check
`sparse_union_fraction_decays` is not used. The cost is the total number of record-flag incidences, not |U|.
Header and tag work: the flag header has g bits and g log L bits of coordinates (o(p) since beta < 1); tag work is at most O(g) per visit and a record is visited at most |F| <= g times: total <= O(g^2) bit operations per record, o(p) since 2 beta < 1.

## 4. Consequence for the ledger

Rows: main `eps q`; fused Gaussian `1 - eps + q beta`; boundary `c + xi - eps` with `c = (3 - tau)/2`, `tau_eff = 2.2500351` (rectangular batching, outer/RECT-BOUNDARY.md; this document's schedule is independent of the boundary exponent);
union `xi + 1/2 - eps`; guard `beta = 1 - xi - r - zeta`; `xi > 1/2`. Balance set: main = fused Gaussian = boundary - slack, which gives
`eps = (1 + q + q (c - s - r - zeta))/(1 + q)^2`, `xi = eps (1 + q) - c + s`. The union row is far above kappa at this point (saving about 0.127 here).
Rejecting controls in the ledger: reinstating the old row `1 - eps - beta - 1/2 + xi` at the new point fails (it is about -0.125); the full-key sort row fails; the four inherited controls fail.

## 5. Executable check (`outer/sched_test.py`, and the independently coded `outer/sched_review.py` by LeverRank)

The script runs the schedule above on exact integer tensors (g = 3..6 axes, L = 5..8, random E_i and random integer T_i|E_i): tagging, the stable LSD radix distribution with its inversion, per-prefix-block variable-length lockstep zip
transposes with a check that every extracted group of a records is a complete E_f-line with consecutive ordinals and one common z, application of T_f, unzip, undo, the keep/rest split, the LIFO pop and the merge by indicator bits,
and compares with the full tensor product `(x) T_i` computed by tensor contraction: exact equality. It also checks the volume identity `streamed = sum|F| = sum_i |U_i|`, `sum|F| <= g|U|` (),
that the number of record moves is within `3 * sum|F| * (ceil(log2 g) + 2 ceil(log2 a) + 4)`, and a tamper control (skipping the second round) fails.

## 5b. Rows that depend on beta, re-verified at the balance of this package

At the balance with tau_eff = 2.2500351 (outer/RECT-BOUNDARY.md): epsilon = 0.99895, xi = 0.6256, beta = 0.3744; every row is regenerated exactly by `check_ledger.py` and re-derived by `independent_check.py` (all strictly above kappa or strictly positive):
group scans 1-eps+beta = 0.375; union xi+1/2-eps = 0.127 (the old row 1-eps-beta-1/2+xi = -0.248 fails: rejecting control); boundary c+xi-eps = kappa+slack;
cap xi-1/2 = 0.126 > 0 and eps-xi > 0; group positive and below dimension (eps-beta > 0); support router span 1-beta = 0.626 (the supplier's total moved support O(g polylog p) = o(p));
gauge/guard 1-xi-r-beta = zeta; group key fits the record (1-(beta+1-eps) = 0.625); membership arithmetic 1-beta-2(1-eps) = 0.624; union tag work 1-2beta = 0.251; union header 1-beta; core-face corrections eps+beta-3 < 0.
The ledger row `sparse_union_fraction_decays` (xi-beta-1/2 > 0) is deleted: it is false at this point (xi-beta-1/2 = -0.249, g mu = p^0.249 > 1) and the schedule does not use it. No other place in this package assumes that U is a small fraction of the microbox; the only uses of the union are the one scan that forms the flags and the identity pass-through.

## 6. What this does and does not establish

Established here: the data-movement schedule, its correctness (class invariance, commutation, complete lines, stability of the radix passes, the lockstep transpose, LIFO interleave) and its tape-head cost O(V g mu polylog p) per window, assuming
the audit's carving (|E_i| and mu), the retained polynomial-width row-field movement for batched boundary arithmetic, and the retained dense/gauge/precision lemmas of PR1673.
Not established: nothing in this document changes the arithmetic, the Gaussian conditioning, the supplier, the boundary matrix exponent or the all-size hypotheses of PR1673; those remain inherited assumptions.
The step "variable block length" of the transpose (item 4) and the head accounting (2.3) are the places that most need an independent review.
