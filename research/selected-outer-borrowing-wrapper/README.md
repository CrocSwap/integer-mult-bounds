# Executable outer borrowing wrapper for the logical BIT caller

This package implements the outer-wrapper handoff in [PR2786](https://github.com/CrocSwap/integer-mult-bounds/pull/2786), using its unchanged binary-tape padding component. It interleaves three body shears with **two separately padded, completed unweighted reversed calls**, then exchanges the original high fields. It also exchanges residual digits when the body is not a whole number of atoms. The result preserves arbitrary Boolean payloads, all original spectators, and the complete genuine high-field ranges.

The ordinary-wrapper identity and conditional borrowing argument are predecessor results in [the retained row proof](../../notes/three-stage-cover-rows.tex) and [Sagar Thakrar's body-stock audit](../bit2234-body-stock-audit/README.md). The contribution here is executable composition, its ordered layout and ownership/cost ledger, and full-origin checks on the literal binary tapes. It is not a new stock coefficient, fit cutoff, physical fixed-tape compiler, supplier or kappa. The selected frontier is unchanged.

## Contract

Fix an integer radix q>=2, positive k,w,n, and 0<=ell<w. Put

```text
R=q^k, M=q^w, A=M^n, J=q^ell,
e=k+n*w+ell, and V=P*R^2*A^2*J^2*Z*T.
```

P,Z,T are positive complete spectator extents. The borrowed input has order

```text
[P][H_hi:R][H_body:A][H_rem:J][Z][D_hi:R][D_body:A][D_rem:J][T].
```

All numerical values and extents used by `outer.py` stay on binary Word/Count tapes. q is fixed finite control, not a decoded variable digit. `remainder_ring=None` represents ell=0. Encoded counts, word arenas and complete payloads must satisfy the retained primitives' canonical, capacity and head contracts. The source and every borrowed head enter at their local left boundary. The caller supplies S with 1<=S<=R. This routine does not compute S, choose k, or assert k<e/2. Those remain borrowing/fit obligations of its caller. Its endpoint identity itself needs no near-half or minimal-borrowing assumption.

The completed callee accepts `[P][R'][H_body][H_rem][Z][D_hi][D_body][D_rem][T]`, where

```text
R'=ceil(R/S)*S,  R<=R'<2R,  V'=V*R'/R.
```

It fixes P, every row ordinal, H_rem,Z,D_hi,D_rem,T pointwise. On the two atom vectors it has the **unweighted** endpoint `F_I(H,D)=(C D,C H)`, where C reverses the n atom coordinates. It borrows its input/counts without changing them, returns a distinct owned output, restores heads, and closes its work before returning or raising. Both calls use this same completed contract. An arbitrary weighted reversed call is not a substitute.

The q=2 integration below is a retained toy, outside the selected odd-prime supplier's domain. The elementary wrapper identity works at any radix; that fact does not relax the selected supplier's prime or implementation premises.

## Endpoint and ordered-layout proof

1. If ell>0, exchange H_rem and D_rem first, using the unchanged digit-swap routine with extents `before=P*R*A`, `middle=Z*R*A`, `suffix=T`. Both high fields and both atom bodies are complete spectators. This leaves `[P][H_hi][H_body][D_rem][Z][D_hi][D_body][H_rem][T]`.
2. For the atom bodies use `before=P*R`, `gap=J*Z*R`, `suffix=J*T`. At body coordinate i, the ADD extents are

   ```text
   before_i=P*R*M^i,
   middle_i=M^(n-1)*J*Z*R,
   suffix_i=M^(n-1-i)*J*T.
   ```

   Thus each vector ADD acts componentwise across the actual intervening remainder, spectator and D_hi fields. For target negation, `before_i` additionally contains `M^n*J*Z*R`. The runtime starts with encoded n-1 and advances these extents by exact radix multiplication/division. It does not assume the intervening factors are adjacent or commute them.
3. Execute `D-=H; F_I; D+=H; F_I; D=-D; D+=H`. Since C is additive and C^2=I, the body states are

   ```text
   (H,D-H), (C(D-H),CH), (C(D-H),CD), (D,D-H), (D,H-D), (D,H).
   ```

   Each F_I is independently padded and restricted through unchanged PR2786 `padding.complete`. At its completed endpoint each added row is still all zero, and every genuine row keeps its ordinal. Restrict immediately after each F_I. The intervening body arithmetic and later high-field exchange therefore see exactly R genuine rows, never R' fabricated q-ary high-field values. The two calls reuse stock rather than multiplying sequential reserves. No global generation-depth or coefficient-program reset occurs in this wrapper.
4. The order is now `[P][H_hi][D_body][D_rem][Z][D_hi][H_body][H_rem][T]`. Exchange H_hi and D_hi with `before=P`, `middle=A*J*Z`, `suffix=A*J*T`. The endpoint is `[P][D_hi][D_body][D_rem][Z][H_hi][H_body][H_rem][T]`, exactly the full original chunk interchange.
5. Every pass preserves its borrowed source and returns fresh owned output. `replace` clears only the previous owned output, never the original source. Scope cleanup erases wrapper-owned counts and intermediate payloads. If a callee raises after closing its own work, both padding and the enclosing wrapper release their own state. The tests inject failure at each callee entry; they do not independently certify every internal callee failure path.

These are quantified algebraic/layout arguments for the stated interface, not conclusions extrapolated from the finite fixtures. They retain the completed callee and elementary-stream implementation premises. No arbitrary-dirty in-place padding or complete multiplication theorem follows.

### Why an involutive weighted call is insufficient

The retained source also offers weighted endpoints `F_A(H,D)=(C_A D,C_A^-1 H)`. These are involutions, but the displayed ordinary wrapper additionally needs the same involutive C on both banks. Over F3 with n=2 and A=(2,1), C_A^2=2I. Starting at H=(0,0), D=(1,0), the weighted two-call word returns H=(2,0), D=(1,0), not the interchange. A control physically adds the corresponding sign passes, permits its correct weighted per-call endpoint, and still rejects its full ordinary endpoint. This is a contract-sensitivity example, not a claim that the predecessor misused weighted calls.

## Complete added bill

Let `ADD(V,M)` and `NEG(V,M)` include **all** work of one retained scalar ADD or sign pass, including arithmetic, binary counters, accesses and erasure. Let `DIGIT_q(V)` include all work of one fixed-radix digit swap, including its q^2 buckets. Each F_I costs its actual complete callee bill at volume V'. The implemented chronological invoice is

```text
3*n ADD(V,M) + n NEG(V,M)
+ (k+ell) DIGIT_q(V)
+ 2 F_I(V') + 2 PAD_RESTRICT(V,V')
+ cardinality setup and intermediate-output disposal.
```

The first three terms are added work, not saved children. Runtime call counters independently require 3n ADDs, n signs, one high-chunk swap and, when ell>0, one residual-chunk swap. The source digit-swap routine executes k and ell digit passes respectively. The two F_I calls have their complete source invoices; no recursive child has been deleted or repriced.

PR2786's exact payload-only charge for one PAD_RESTRICT is `4V+8V'+12` reads, `V+3V'` writes and `4V+8V'+16` unit moves, excluding the callee and separately charged binary control. Both calls therefore pay twice these amounts. The wrapper also clears five body-stage outputs before the next stage, an optional residual-stage output, the body result before high return, and all nonfinal outputs within the vector/digit passes. These clearing scans are charged; they are not included for free in the padding formula.

Cardinality setup costs polynomial binary work in the encoded lengths and n; it is not a unit-cost host exponentiation. For admitted minimal encodings, all new numerical/count lengths are O(log V). The inherited ADD implementation still has its actual numerical toll. This package does **not** turn that toll into the stronger selected H2 estimate, claim a new O(V*n) implementation, or treat an unknown callee cost as zero.

For payload contents, outside a callee a conservative bound is 8V. At most the original source, the pre-body source and the current body-stage source, each of volume V, coexist with callee-owned state. During a callee the bound is therefore `3V+L_F(V')`, where L_F includes its padded input, output and internal payload. Outside it, a vector primitive adds at most an input-sized split and an output, and a padding/restriction phase adds at most 2V'; V'<2V. New metadata uses a fixed number of variable-length tapes, charged separately from this payload bound. This is not a bound on cleared backing capacity, Python heap or total physical reserve, and does not independently adopt PR2753's pending logical reserve theorem.

## Evidence and replay

Exact dependencies are PR2786 `80df2062cef303c05ffe89bb54b87b6b371d1253`, by Nick Petalas, and its archived PR2753 `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, by David Arias. `VENDOR.json` binds five byte-identical PR2786 files by Git blob, SHA256 and size. The retained loader additionally authenticates its complete 84-file PR2753 export before any caller code imports. Original notices remain inside that unchanged archive. Undeclared outer bytecode and preloaded source modules reject. Root-note/task pins are in `SOURCES.json`.

```sh
python3.12 -Werror -B scripts/research_package.py \
  --package research/selected-outer-borrowing-wrapper
```

`RESULT.json` is read-only. Explicit `verify.py --emit-to NEW_EXTERNAL_FILE` refuses overwrite and writes outside the package. Normal and optimized replays compare complete typed JSON receipts, so replacing integer 1 by boolean true fails.

- Nine complete interface fixtures cover 38,925 independent Boolean input columns and 102,492 padded per-call columns. Domains include n=1,2,3; radices 2 and 3; atom widths 1 and 2; nonzero residual digits; multiple prefix/gap/suffix values; exact/no padding; and overborrowing k=2 with S=2 at q=3, where ceil(log_q S)=1. Each individual F and the final full-chunk endpoint are checked, not only the final two-call cancellation.
- The unchanged source Node/Driver and full good/fallback normal forms execute a one-family GL2(F2) two-MOVE toy with R=8, S=6, padded separately to 12 rows for each call. All 1,024 genuine columns and all 3,072 padded per-call columns agree. The literal source makes 24 MOVE residual calls and 240 matched child entries/returns. Frozen generation depth, the incoming-weight tape, the empty old directory and their heads are preserved. The toy program is an opaque identity token, not an executed serialized coefficient program. This is complete toy execution, **not** selected GL64 payload execution or a new recursive construction.
- Nine controls detect omitted/substituted shears, wrong initial sign, omitted remainder/high exchange, an incorrect F endpoint, unsafe weighted-F substitution, and failures at either callee entry with wrapper cleanup. CLI tests separately exercise optimized Git-free read-only replay, both source-authentication layers, bytecode/preload rejection, typed receipt corruption and emission boundaries.

Local environment and final freshness are recorded in `TASK.json`. Each registered command has a timeout of 300 seconds. No selected cold replay, hosted-CI success, proof-assistant acceptance or independent human review is claimed.

## Engineering limits

New runtime functions are at most 60 physical lines. No new function recurses. The vector loops consume one encoded atom each turn; radix-power loops decrease a positive power by q>=2; fixed operation lists have at most nine entries. Checker extents are explicitly capped at 60,000 genuine and 120,000 padded positions. Source authentication reads five bounded files, then the retained bounded archive.

Python's dynamic tapes and counter objects are a managed-runtime deviation from allocation-free execution. The payload bound above and finite fixture caps constrain live contents; fixed physical allocation remains open. The completed-callee callback and scope-cleanup callbacks are deliberate, finite indirect-call boundaries. The immutable predecessor's implementations remain unchanged, including their own dynamic-allocation and failure-path limits. New acceptance checks use explicit exceptions and remain active under optimization. The mutable checker instrumentation is scoped and restored; no concurrent artifact-writing replay is supported.

## Open next questions

1. Bind the actual selected odd-prime GL64 F_I interface, compatible stock construction and fitted k to this wrapper. Start with PR2753's complete caller and a source-bound unweighted incoming program. The completed semantic, root-coupling, numerical and physical contracts remain required; the q=2 fixture cannot admit them.
2. Lower the outer extents, disposal and padding/count streams to the physical caller's fixed tape inventory. Start from the active Frame/bank integration in [Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319). A live-content bound is not a placement/movement or erased-backing-capacity proof.
3. Price or improve the actual ADD/old-routine tolls before using stronger bootstrap H2. The displayed invoice identifies the exact new calls, but does not establish the desired all-width primitive time constants. No further supplier search is justified by this component alone.

## Credit

Nick Petalas. Apache-2.0. David Arias supplies PR2753's all-size logical caller and toy source. Jose Manuel/jmbarrancoml supplies PR2697/2234 and the retained source, coefficient, route, packet and selected-word lineage. Sagar Thakrar supplies the conditional body-stock, two-call reuse and padding argument. PR2786 supplies the unchanged padding implementation and exact traffic. The retained row-proof identity, selected supplier and original source notices keep their predecessor attribution. No predecessor theorem, stock formula, caller, normal form or finite source construction is claimed as new.
