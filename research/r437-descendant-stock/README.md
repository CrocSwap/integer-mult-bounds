# R437 descendant stock: retain the 9475 factor once

**Scoped stock theorem and arithmetic path certificate; no new kappa.** For the
row quotient and stock guard used by the pinned R437 physical caller, sufficient
root stock is

\[
 R=t\,9475\,A^{D(n)},\qquad
 A=28416\,|\mathrm{GL}_{64}(\mathbb F_q)|\,q^{4096(w-1)},\quad t\geq1,
\]

when `n >= 64`; any positive row count suffices for this internal-node condition
when `n < 64`. Here `D(n)=0` below 64 and
`D(n)=1+D(42 floor(n/64))` otherwise. The original root's `q,w` stay fixed.

PR4176's `NUMERICAL.md` section 5 uses the stronger sufficient stock `t K^D`,
where `K=lcm(28416,28425)|GL64|q^(4096(w-1))=9475 A`.
Thus at positive depth `D` this component's least sufficient divisor is smaller
by exactly **9475^(D-1)**. This does not identify a defect in that conservative
bound. Its `check_stock_rows` intentionally rejects our smaller stock for `D>1`;
the frozen numerical wrapper is unchanged and does not admit it.

The new divisor is necessary and sufficient for **all paths allowed by this
rank-ceiling row-guard model**. Necessity is not a claim that every maximal path
is produced by the actual compiler, or that this is the least stock for every
other construction obligation. The universal result is the written argument
below; finite checks support its source binding and implementation.

## Actual source boundary

All sources are exact bytes at canonical main
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`; `SOURCES.json` binds their blobs and
SHA256 digests. No predecessor source is edited.

1. `r437-pooled-native-interface/replica_catalogue.py`, `ReplicaTopology`, has
   28,416 families. `selected-bit-physical-caller/macro_binding.py`,
   `SelectedBinding`, sets cutoff 64 and `stock_multiple=9475`.
2. `fresh_rows.quotient` divides positive rows successively by the family count,
   `context.codes.size=|GL64(F_q)|`, then by `q` exactly `4096(w-1)` times.
   Its `radix_power` source yields once per division of `q^w` by `q` until 1;
   the first of those `w` iterations is skipped for each of 4096 matrix entries.
   Every remainder must be zero, and the quotient must be positive.
3. `Machine.node` stores that quotient as `unused` and immediately requires
   divisibility by 9475. Its `prepare_child` handoff passes `unused` as the
   child's `rows` port through the fixed `CAPSULE` ordering. It does not divide
   the child's inherited row count by 9475.
4. `r437-carrier-integration/numerical.py` supplies the declared maximum paid
   rank 42 and the depth recurrence. The separate native/compiler claim that
   every child width is at most `42 floor(n/64)` is retained as a premise.

These facts identify the recurrence `R_child=R_parent/A` and the local
condition `9475 | R_child`. They do not price `Count` arithmetic, prove the
complete request inventory, or execute a recursive payload. The source's
`SelectedBinding.check_stock` placeholder is not presented as an installed
descendant validator.

## Proof and exact scope

Put `S=9475`. First fix any positive integers `A,S` and a path with exactly `d`
internal transitions. At transition `j`, starting with `j=1`, the unchanged
guards require a positive exact quotient `R/A^j` divisible by `S`.
The final condition implies `S A^d | R`. Conversely, if `R=t S A^d`, every
quotient is the positive integer `t S A^(d-j)`, so all guards pass. Consequently
the least positive stock on a path of length `d` is **S A^d**, without any
coprimality assumption about `A` and `S`. With zero transitions no guard is run.

For the width model, let `g(n)=42 floor(n/64)`. On internal widths, `g` is
nondecreasing and strictly smaller than `n`. Iterating it shows that `D` is
nondecreasing. Every permitted child `1 <= c <= g(n)` therefore satisfies
`D(c) <= D(n)-1`. Along a path at depth `j`, `D(n_j) <= D(n_0)-j`.
Starting with `R_0=t S A^D`, exact row inheritance gives

\[
 R_j=t S A^{D-j}.
\]

If node `j` is internal, `D-j >= 1`, so its quotient remains divisible by `S`.
Moreover its inherited rows are divisible by the new sufficient divisor for
its entire remaining subtree: for `D(n_j)>0`, the multiplier is
`t A^(D-j-D(n_j))`. At a leaf the divisor is 1. This proves all bounded paths
are covered, including early leaf termination and paths stopping internally.

The maximal path `n,g(n),g(g(n)),...` has exactly `D(n)` transitions in the
declared model. Applying the first paragraph to that path proves necessity
within the model. A compiler that forbids that path might permit less stock;
we make no such reachability claim. Additional stock predicates outside the
two identified guards are also outside this minimum claim.

`stock.py` implements a separate arithmetic certificate. It anchors the first
node to a supplied root, preserves its field and precision, checks the rank
ceiling, and requires **exact** parent-to-child row equality. Local divisibility
alone is insufficient: at widths `128 -> 84`, twice the correct child stock
passes its local divisibility test but is not the parent's quotient. The
checker rejects that forged path. The supplied root still needs external
prime, precision, source and Program authentication. This component does not
replace PR4176's complete `checked_entry` or remove its root-only restriction.

## Reproduction and evidence

Python 3.12, standard library only:

```sh
python -B scripts/research_package.py --package research/r437-descendant-stock
```

Direct replay, including in a Git-free export containing the declared inputs:

```sh
python -B research/r437-descendant-stock/verify.py
python -O -B research/r437-descendant-stock/verify.py
```

Ordinary verification is read-only and compares the complete deterministic
`RESULT.json`. Explicit `--write` is reserved for receipt regeneration.
The receipt reports:

- 1,024 width comparisons with the pinned depth function and **323,232** child
  transitions checking the depth inequality.
- **25,620** exhaustive abstract `(A,S,d,R)` cases comparing the formula with
  repeated local guards (`A=1..5`, `S=1..4`, `d=0..4`, `1 <= R <= 2 S A^d+1`,
  with leaf divisor 1). These include non-coprime factors.
- **14** internal nodes through the unchanged AST of `fresh_rows.quotient` and
  the four-statement quotient/stock block in `Machine.node`, using an explicitly
  substituted **integer Count/Word adapter**, including the source's radix loop.
  This checks control-flow arithmetic,
  not binary tape operations, acquisition, cleanup or timing.
- Four full maximal paths with `(q,w,n)=(3,1,64),(3,2,128),(5,2,512),(3,2,2048)`.
  At width 512, depth 4, the old/new stock factor is **850,624,046,875**. At
  width 2048, depth 7, it is **723,561,269,122,002,197,265,625**. These are row
  cardinality ratios, not time savings or practical materialized datasets.
- **17** rejecting controls, including locally divisible but unrelated rows,
  lost high-lift/family/9475 factors, one missing recursive factor, precision
  and field changes, wrong widths, missing roots, and continuation below cutoff.
  Three controls confirm that the predecessor's stronger wrapper rejects the
  new smaller stock; this is expected, not a failed predecessor test.

The q=3/q=5 fixtures are semantic arithmetic checks, not the q>2^80 numerical
admission. No full selected cold replay, compiler catalogue, Lean, Docker,
native payload, source preparation or physical tape simulation was run. The
orientation command `research_selected_baseline.py` stopped on an omitted
`certificates/checkpoints/frontier4359.json` in this sparse checkout; no baseline
pass is claimed. The selected record remains conditional kappa 0.00302015.

## Coordination and attribution

Task `r437-carrier-integration`, revision 7, refined from the bit-mechanisms
draw `5b8bdff3d61d78a94ac212b844fcd944` to this exact stock implication.
[Discussion #4682](https://github.com/CrocSwap/integer-mult-bounds/discussions/4682)
is the canonical claim/result. Overlap checks covered R437, descendant/path
certificates, 9475 and stock-divisor terms. The initial remote snapshot had
448 open PRs and 3,606 Discussion records with complete pagination; local
coverage was sparse and closed PR bodies/code diffs were not fully searched.
The central ledger was consulted. PR4584 audits the separate pivot implication;
PR4612 concerns selected BIT row stock, with different atom and call boundaries.

Chris R / Clear1nsight's PR4067 and PR4176 supply the changed carrier, complete
source interface, conservative K^D bound and explicit descendant-certificate
gap. unpaidmoon / PR4147 supplies the earlier coefficient audit, not recomputed
here. The literal caller and stock interfaces retain Jose Manuel /
jmbarrancoml, David Arias, Nick Petalas, ywz65 and the PR2753/2769 lineage.
The R437/hosting/source predecessors retain ai-nanachi, Ali Romman, Sagar Thakrar,
Rohan Arun, zxv, Ross Richardson and all notices in the pinned packages.
New proof, arithmetic certificate and checks: Mihir Srivastava (mihir-s-05),
with substantial OpenAI Codex assistance. Apache-2.0. This is author-checked
work with separately written arithmetic, not independent human review or
formal proof-kernel verification.

## Open next questions

1. **Bind an arithmetic path to actual produced Program events.** This is
   necessary before extending the numerical entry to descendants. Start with
   one authenticated `checked_entry` root, its `Machine.prepare_child` handoff
   and decoded chronological STEP. The blocker is proving actual request,
   width, source identity and inherited `rows` correspondence; a list of valid
   integers does not establish that correspondence.
2. **Price or implement the guard on the physical Count tapes.** The theorem
   removes a repeated stock factor but gives no physical cost reduction. Start
   by running the unchanged quotient and stock check with real tape Count
   objects and the same fixed root precision. Complete source-table, payload,
   visited-backing and blank-return costs remain separate obligations.
