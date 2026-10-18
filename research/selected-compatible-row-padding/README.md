# Compatible-row padding for the logical BIT caller

This package implements one open boundary in David Arias's [PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753): turn sufficient fresh-row capacity into an exactly divisible row range, then remove the added rows after the completed caller returns. It uses fresh owned output, not arbitrary dirty borrowed padding. It does not implement the outer high-part borrowing/exchange wrapper or admit a supplier. The selected frontier is unchanged.

For positive integers `C,R,S,B`, with `R>=S`, the component takes a binary payload in order `[C prefixes][R fresh rows][B body positions]`. Here B is the complete ordered body volume, not PR2753's before-spectator extent. No internal body factor is reordered. It computes

```text
R' = ceil(R/S)*S,    a = R'-R,    R <= R' < 2R,
V = C*R*B,          V' = C*R'*B.
```

It inserts `a` zero rows after the genuine rows of **each** prefix, calls a completed row-pointwise permutation on all `R'` rows, checks every added output bit is zero, and restricts each prefix back to its original `R` rows. Every genuine row keeps its original ordinal. The all-size proof and exact source boundary are below.

The contribution is the executable padding/restriction and its lifetime/traffic argument. The stock formula, row-pointwise callee contract and earlier conditional padding arithmetic are predecessor results. In particular, [Sagar Thakrar's body-stock audit](../bit2234-body-stock-audit/README.md) already explains the conditional complete-row implication; this does not claim that argument as new.

## Quantified boundary and proof

Assume the callee borrows its padded input and row-count tape without changing them, restores their heads, returns a distinct owned output, and closes its work on failure. Its completed Boolean endpoint must be the pullback of a permutation that fixes each prefix and each fresh row pointwise. Within a row it applies the required body permutation. The body permutation may depend on the frozen prefix, but not on payload bits. These are semantic premises, not consequences of the wrapper's shape checks.

1. `plan_rows` consumes one original row on each main iteration and one position in the current stock group. It has completed at least one group exactly when `R>=S`; otherwise it rejects before reading payload. Finishing only the last incomplete group gives `R'=ceil(R/S)*S`. Thus `0<=a<S<=R` and `R'<2R`. Counts remain on sequential binary tapes; the runtime never decodes R, S or a body address into a host integer.
2. Padding maps genuine index `(c,r,b)` to the identical padded index for `r<R` and writes zero at every `r>=R`. It repeats this separately for every prefix. No original payload cell changes.
3. The completed callee fixes the row coordinate, so each added row contains only a permutation of its own zeros. Every genuine output row is the required permutation of that same genuine input row. Restriction therefore returns the desired endpoint and deletes only zeros. Pointwise row restoration is necessary; preserving merely the row multiset is insufficient. A shape-correct permutation of two genuine rows passes the runtime zero test, and the independent endpoint control detects it.
4. The padded input is cleared immediately after the callee returns. Restriction then copies genuine output and checks discarded output. Finally the complete callee output is cleared, both planning counts are erased, and the original source head is restored. A callee's internal failure cleanup remains its own obligation. This is ownership composition, not isolation from hostile callback code.

The proof holds for every finite positive extent in this interface, not only the replayed widths. An all-zero source is not assumed. Added storage must be fresh and owned. An in-place arbitrary-dirty substitute is outside this result, consistent with [PR2740](https://github.com/CrocSwap/integer-mult-bounds/pull/2740)'s different restricted-alphabet obstruction.

## Exact traffic and temporary contents

The following exact counts include all wrapper payload reads, writes and unit head moves, both clearing scans, and the retained Tape implementation's LEFT-marker rewinds. They exclude the callee and binary count tapes:

```text
reads  = 4V + 8V' + 12
writes =  V + 3V'
moves  = 4V + 8V' + 16.
```

For one padding or restriction scan, reads are `2V+2V'+3` and moves are `2V+2V'+4`; writes are respectively V' and V. Clearing an N-cell owned tape at its restored head takes `2N+3` reads, N writes and `2N+4` moves. The two cleared tapes each have V' cells. The checker compares these formulas with actual payload meters, subtracting the measured fixture callee traffic.

Binary control is also charged, though no exact coefficient is claimed for it. A countdown from N has O(N+bit_length(N)) total ripple and rewind work. In planning, stock-group restarts cost `O(ceil(R/S)*bit_length(S))=O(R)` because `bit_length(S)<=S` and `S<=R`. Building R' and a by binary increments costs O(R'). In a scan, constructing a body countdown per row costs `O(C*R'*bit_length(B))=O(V')`; row and prefix countdowns have the same absorption. Thus all wrapper count work is O(V'), and the complete wrapper adds O(V) charged logical tape work. No preparation coefficient is silently treated as zero.

During the callee retain the original V-cell input in addition to its space. Outside the callee, the maximum payload content is at most `V+2V'<5V`: original input, padded input, and callee output at return. After clearing padded input, restriction uses at most `2V+V'`. Repeated row counters are erased and their logical tape objects released; their cleared backing arrays are not a Python heap or physical placement bound.

A conservative extra metadata allowance is twelve binary tapes of at most `ell(V')+3` symbols each, where `ell(x)=bit_length(x)`. This includes the four borrowed extent tapes, two planning results, active prefix/row/body counters, literal-construction and replacement overlaps, delimiters and LEFT markers. All count values are at most V'. This bound is for successful traces of the stated routines, not arbitrary callback allocations.

## Application to the pending selected caller

The exact dependency is PR2753 at `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, by David Arias. Its PROOF sections 1, 4 and 7 give

```text
K = lcm(28416,28425) * |GL64(Fq)| * q^(4096*(w-1)),
D(n) = 0 below 64, otherwise 1+D(42 floor(n/64)),
S = K^D(n),    accepted root rows = t*S.
```

Its complete endpoint fixes each original fresh row. Its independent unused U coordinate remains genuine child stock. Applying this wrapper with `R>=S` supplies the exact accepted row multiple while preserving every original prefix, row and body coordinate at return. It does not construct S, select borrowed width k, or move the two high fields. The source's independent directory/program, root coupling, fresh-field, precision and completed-callee premises remain unchanged. Invoke this component at a whole completed F_I boundary, not at an intermediate cover. It can pad each F_I separately; it does not assign q-ary high-field values to added row ordinals.

As a **conditional corollary**, assume PR2753's pending `<11V'+F_q` logical reserve theorem with its stated source/root-coupling hypotheses. Keeping the original source costs V more. The callee phase is then below `23V+F_q`, while the outside payload phases cost less than 5V. Adding the conservative count allowance still gives `<24V+F_q` for V>=1024: `ell(V')<=ell(V)+1` and `12*(ell(V)+4)<V` on that domain. For `2^j<=V<2^(j+1)`, it suffices to check `12*(j+5)<2^j`; this holds at j=10 and remains true by induction. The selected internal body has at least `q^128` positions, so it meets this elementary size condition. This is an implication from the pending reserve theorem, not an independent verification or adoption of it. It is also not a new stock exponent or outer-wrapper theorem.

## Source pins and replay

`PREDECESSOR.json` records all 84 Git blobs, SHA256 digests and lengths of the exact PR2753 package. `predecessor.tar.gz` preserves those bytes, including every predecessor notice. Replay authenticates the full archive and every member before exporting to a fresh temporary directory and importing code. There are no archived bytecode caches. Preloaded source-module names reject rather than bypass the authenticated imports. The main-checkout evidence and historical task/selection provenance are pinned in `SOURCES.json`.

From repository root with standard-library Python 3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/selected-compatible-row-padding
```

The registered commands compare complete typed receipts, and do not rewrite them. Explicit `--emit-to NEW_EXTERNAL_FILE` creates a new receipt outside this package and refuses overwrite.

- Core replay checks 8,385 stock plans, 702 patterned complete wrappers, forty independent Boolean basis columns, exact traffic, eight runtime rejection controls and a semantic row-permutation control. It includes multiple prefixes, no padding, stock one, exact multiples, short/long output, nonzero padding, aborted callees and ownership/head errors.
- Integration runs the unchanged source Node/Driver and model normal-form consumer with a finite two-MOVE catalogue and the source's unchanged one-family topology. It pads 49 genuine rows to 96 with divisor 48, and covers all 48 GL2(F3) classes. Every one of 3,969 genuine Boolean columns is checked by separate weighted-reversal arithmetic; 3,807 added columns start at zero. The receipt records 96 MOVE residuals and 816 matched child entries/returns. This is a two-dimensional fixture, **not** execution of the selected GL64 payload, the four-family COPY/IDLE schedule or a new recursive source construction.
- Focused tests cover literal endpoints, capacity failure, binary planning, source corruption/omission, preloaded-module rejection, optimized Git-free replay, symlinked temporary directories and boolean/integer receipt corruption.

The finite evidence supports the written implication; it does not prove arbitrary widths by enumeration. No selected cold replay, physical tape compiler, stronger H2 saving, outer borrowing/exchange, proof-assistant check, independent human review or new kappa is claimed.

### Implementation and verification limits

Local verification uses CPython 3.12.15 on Linux x86_64 under WSL2. The ten focused tests and 74 repository research-workflow tests pass with warnings treated as errors. Scoped Ruff checks use `E,F,B,I,UP,SIM`. Normal and optimized core replay give identical receipts. An initial four-family integration was stopped after more than eight minutes without a receipt; the registered fixture uses the smaller one-family topology to leave headroom under the 600-second command cap. No endpoint conclusion is drawn from the stopped run.

New runtime loops have explicit encoded finite bounds, and no new routine recurses. Python allocates variable-width tapes and counter objects during execution, so this is a managed-runtime deviation from allocation-free execution. The payload bound and twelve-tape metadata allowance constrain live contents; physical allocation and erased backing capacity remain the second open question below. The completed-callee callback is a deliberate indirect-call boundary. Only the pinned source adapter and finite fixture callees are replayed, and any other callee must establish the same ownership and endpoint premises. Immutable source dependencies retain their original implementation and notices. Source exports are bounded to 84 files of at most 100,000 bytes each, with a compressed archive cap of 200,000 bytes.

## Open next questions

1. Can the remaining outer borrowing/high-part exchange use this fresh-output contract while returning the entire original high field? Start at PR2234's two-call wrapper, padding each completed F_I separately so the intervening high-field arithmetic never receives added row ordinals. Bind its actual high-field layout, residual digits, coefficients and lifetime ledger. The padding subroutine alone does not perform that exchange or establish its time/space constants.
2. Can the padding/count streams share the physical caller's fixed tape inventory? Start with their sequential scans and at most twelve metadata tapes, then serialize locations, heads and reuse. The logical model releases cleared tape objects; a physical blank-return and movement proof remains necessary. Coordinate with the existing Frame/bank investigation before implementing another allocator.

These are component handoffs, not a recommendation to expand a supplier search. Structured first steps and blockers are in `TASK.json`.

## Credit and scope

Nick Petalas. Apache-2.0. David Arias supplies PR2753's recursive caller and pending logical reserve. Jose Manuel/jmbarrancoml supplies PR2697, PR2234 and the retained selected word, packet, route and coefficient lineage. Sagar Thakrar supplies the earlier body-dependent stock/padding implication. The retained PR2753 archive preserves their complete source notices and the separate component credit to starship-s, ywz65 and Nick Petalas. No predecessor stock formula, caller, reserve theorem or conditional padding observation is claimed as new.

The task picker proposed adversarial audit with nonce `e976f9f32d2dc2ef8c3206127eecf944`. Scope is refined from `uniform-transfer-audit` to this quantified row-padding boundary, after checking the newer Discussion2319 handoff. The separate physical caller and all-width geometry claims are not taken. The canonical claim and freshness record are in `TASK.json`. Evidence is locally checked, not an independent human or formal review.
