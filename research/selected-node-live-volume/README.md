# Complete first-node data-content peak

For the unchanged first-range caller in Jose Manuel's [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697), the following is a sharp bound on simultaneous nonblank payload and embedded route-key content, including the borrowed input:

```text
no remainder, n = 64:       3V
positive remainder:        max(4V, 3V + 3V/C) <= 6V
```

Here V is the entire caller input and C is the number of physical old prefixes. The bound assumes the source's successful complete-row/leaf contracts, the geometry below and route keys fitting one body fibre. It is not a total numerical reserve. Directory symbols, numerical/count/control tapes, LEFT markers, fixed compiled data and interpreter backing capacity remain excluded. No supplier, exponent, selected record or predecessor implementation changes.

The new step joins all caller data lifetimes, including the original-offset remainder peel. [Nick Petalas's PR2708](https://github.com/CrocSwap/integer-mult-bounds/pull/2708) covers routes and gather/return/scatter. [starship-s's PR2731](https://github.com/CrocSwap/integer-mult-bounds/pull/2731) proves the sharp residual bound `3v+3R`. Those component results are retained and credited. The peel uses the much larger fibre `V/C`, rather than the staged residual's R. Substituting R there would miss the possible 6V peak.

## Source and counted objects

The caller is pinned at `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The component audits are pinned at `2982489cc00a17bd1c7ee1e206e975eda9bcb64d` and `46c0c3554608a1096816ad668c755d3b5b7a8c0b`. [SNAPSHOTS.json](SNAPSHOTS.json) authenticates 39 unchanged caller/runtime/proof/notice files and the two component proofs by SHA256 and Git blob. Runtime imports occur only after authentication. No predecessor verifier executes.

Use the caller's notation, with F used for its family count:

```text
F = 28416                 live family streams
r = 661                   ordinary staged roles, at most one private role
N = |GL_64(F_q)|           low classes per family
H = q^(4096(w-1))          high matrices per low class
C >= 1                    physical old-prefix multiplicity
R = U B G S (q^w)^(2n)     one high-matrix body fibre
v = C H R                 one staged packet
V = F N v                 complete caller input
J = 4096(ell+1)            embedded route-key length
```

The actual residue arena word length is ell. Fix a source-admissible odd prime q and retain the source's encoding, row, successful-operation and completed-below64-leaf contracts. Require `64 <= n < 128`, positive complete multiplicities, fresh distinct tape factories, and **J <= R**. This last condition is an explicit word-size premise, not inferred from arbitrary padded encodings. It holds, for example, for minimal residue encodings with one margin bit. Indeed `ell <= q^w`, `J <= 8192 q^w <= (q^w)^128 <= R` for odd q and n>=64. Arbitrarily oversized supplied words require the unabsorbed key term instead.

Content counts physical tapes by identity, so the unpeeled source alias is counted once. Reading a symbol does not dispose of it. A cleared symbol stops contributing even when the backing bytearray retains capacity. The count includes route-key bits and WORD_END delimiters on route data tapes. It excludes directory copies of those fields and all numerical tapes. Caller/coefficients/observation callbacks must not allocate additional payload tapes beyond the pinned program.

## Lifetime proof

### Peel before row splitting

The original-offset `peel.run` uses `leading=fresh_rows*B`, gap G, suffix S and all 2n atom coordinates in its layout. Its directory loop has C old prefixes, without a fresh matrix field. Therefore its fibre is

```text
R0 = fresh_rows B G S (q^w)^(2n) = F N H R = V/C.
```

Apply PR2731's packet-engine lifetime proof to this actual layout, with volume V and fibre R0. Any primitive uses at most `3V+3R0`. If n=64 the trace is empty and returns the original source alias. If n>64 the trace has eight primitives per peeled pair. Its final sign follows earlier primitives. A sign retains its local source, complemented intermediate, buckets and output, totalling 4R0. At the last old prefix this coexists with the original V, distinct current V and `(C-1)R0` accumulated output. The sum is exactly `3V+3R0`. This argument also applies at w=1. It is independent of the bits and coefficients.

### Split and complete global caller

After a nonempty peel, the borrowed source and peeled output each have V content; after an empty peel these are one tape. Splitting creates F families with combined volume V. Thus the protected base during the global word is `3V` with a remainder, `2V` without one. The peeled tape stays live throughout `Driver.global_word`; it is cleared only in `Node.run`'s finally block.

All additional data above that base is bounded by

```text
E = max((r+1)v + max(Nv, 3H(R+J)), (r+3)v + 3R).
```

The first term is PR2708's gather/route/return/scatter bound. All r staged packets survive return routing. Scatter builds a new full Nv family before clearing the old family. Its extra returned packet is retained too. The second term is PR2731's complete MOVE/COPY residual bound with ordinary/private packets retained. COPY's cloned input is a distinct tape. An aligned XOR adds only one packet, so fits this bound. Clone creation itself fits as well.

For idle, the gathered input and its complete residual use at most `3v+3R`; during its commit the gathered input, changed output and new family need `2v+Nv`. A bridge adds only Nv, and terminal exchange allocates no payload. These all fit E for r>=1. Distinct common-low invocations, roles and global phases execute sequentially. Their extras are a maximum, not a sum.

Since J<=R, H>=1 and C>=1,

```text
3H(R+J) <= 6v,       3R <= 3v,
E <= max((r+1+N)v, (r+7)v).
```

For F=28416, r=661 and every N>=1, both coefficients are at most FN:
`(F-1)N >= 28415 >= 662 = r+1` and `FN >= 28416 >= 668 = r+7`.
Consequently E<=V. The complete global caller has at most 4V content with a remainder, 3V without one. This includes literal local words, COPY, ERASE, idle residuals, bridges and their primitive interiors.

### Merge, cleanup and sharpness

Merge retains all families while constructing a complete new V output. With a remainder, source, peeled, families and output coexist at the final append, attaining 4V. Without a remainder, source and peeled alias and the peak is 3V. Cleanup only removes counted content. Together with the attained peel peak, this proves the displayed exact formula and uniform 6V upper bound. For C=1 the peel attains 6V; for C=2 it attains 9V/2; for C>=3 merge attains 4V. There is no 4V uniform bound for this unchanged remainder path.

The same proof applies to the retained dimension-two model when its F,r,N satisfy the two coefficient inequalities and J<=R. This is a domain statement about the fixed ownership schedule, not a lower bound on other implementations. Earlier disposal of the peeled packet or a different primitive could change it.

## Replay and evidence

Use standard-library CPython 3.12 from the repository root:

```sh
uv run --python 3.12 --no-project python -I -B research/selected-node-live-volume/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/selected-node-live-volume
```

The verifier executes the unchanged complete model node, not a hand-written phase simulator. A temporary observer counts every write/erase at all payload/route allocation sites. It retains every uncleared counted tape, even if the program drops its Python reference. At a claimed peak a separate scan of all active cells checks the incremental census. Exit checks require precisely the borrowed source and returned output, source preservation, head return, numerical arena cleanup and the full independently computed weighted-swap bit endpoint. The direct census covers tracked tapes; completeness additionally relies on the source audit of every reachable data constructor.

The registered complete-node execution uses q=3, dimension two, w=1, the full 48 low classes, four families and no remainder. Four separate literal peel executions cover a positive remainder, one through three old prefixes and an independent external gap. Their measured `(V, peak)` pairs are `(729,4374)`, `(1458,6561)`, `(2187,8748)` and `(1458,8748)`. The complete node measures `(15552,46656)`. They do not execute the selected GL64 payload or a multi-digit complete node. The written proof supplies the quantified result; the finite executions and retained component proofs support the implementation binding. Failure controls reject a 4V peel budget and a budget one cell below 6V, source changes and wrong receipt types. An observer-bypass control must fail the direct census.

An additional complete positive-remainder model is available as `verify.py --case 1`. Its local attempt was stopped after about 20 minutes without a final result, and it is outside the registered evidence. This is neither a failure nor a correctness conclusion. `--case 0` likewise emits the complete core-node measurement without receipt comparison; default replay compares the full registered receipt. `--peel-only` is a quick component probe and does not print the complete-package PASS marker.

The registered CPython 3.12.15 replay passed locally on macOS 27.0.1 arm64, including exact receipt comparison and all six control groups. The repository research-workflow suite passed 70 tests with three skips. No hosted CI pass is claimed.

## Scope and expansion decision

Base canonical main `0374b3e6a532dac112813523d605288c416418c1`, priority revision 5. The isolated branch was refreshed to `7b39515117fe26e75d16c268877391f1bdaa5640`; guidance, selection and replay runner were unchanged. The original card is `selected-stock-envelope`; TASK.json records the change to the live complete-caller lifetime handoff in [Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18956316). The baseline binding command passed before this work. The initial complete overlap snapshot covered 754 open PRs and 1360 Discussion records, with no warnings, plus 1827 local records. Metadata coverage excludes arbitrary diffs and unpublished work.

Decision: finish this bounded composition, then stop. This is a successor proof about an existing node, not a new construction campaign. Proved data costs now include peel, staging, residuals, routes and merge. Total numerical/control/directory/marker costs, larger child returns and native admission remain unknown. The separate directory component in ywz65's PR2688 does not make them zero.

## Open next questions

1. What numerical/control/marker content coexists with these measured data peaks? Begin at the attained peel sign and final merge; include count copies, coefficient pages, directory production and disposal. These missing terms block a total caller reserve. Do not replace simultaneous lifetimes by an assumed historical parking allowance.
2. Can a source-preserving peel use less than the attained 6V data content? Begin with the sign's local source, complement, buckets and output, preserving arbitrary dirty payload and exact return. A changed primitive needs a separate endpoint and lifetime proof; the present result claims no optimality over algorithms.

## Credit and verification limits

Nick Petalas prepared this composite proof and replay. Jose Manuel/jmbarrancoml supplied the first-node caller and source-packet implementation; Nick Petalas supplied the route component; starship-s supplied the residual component; ywz65 supplied the separate directory and primitive/setup audits. The byte-exact retained NOTICE.md preserves the selected supplier, geometry, compiler and tape lineage. New work is Apache-2.0 under the repository license.

Build the Lever led to a per-write replay against retained source. Prove It Works led to a direct peak census and an independent returned-bit oracle. Test Behavior, Not Implementation led to executing the actual peel under invalid budgets. Local-only internal review checked the lifetime proof, all 41 source exports and reachable allocation sites, and repeated the four peel fixtures and six control groups. No human or formal-kernel review, full selected cold replay, selected GL64 Boolean execution, total reserve admission or new kappa is claimed.

Power of Ten inspection is scoped to the new verifier and controls. New functions stay under 60 physical lines; allocation-frame traversal is capped at four frames; fixture domains and subprocess timeouts are fixed. Explicit contracts remain active under optimized Python. Dynamic allocation and interpreter metadata enumeration are documented managed-runtime deviations: the registered data domains are one 15,552-bit complete node and four peels of at most 2,187 bits, with at most the proved data peaks live. Numerical/interpreter allocation is excluded from the measured theorem and is not presented as a fixed-capacity implementation. Source-bound dynamic imports and temporary Tape observers are checker-only deviations from static dispatch. The context manager restores every patched method on success and failure. Frozen source uses its inherited tape-terminated loops and dynamic allocation; it is preserved byte for byte. Extending the fixed domains requires a fresh capacity and runtime review.
