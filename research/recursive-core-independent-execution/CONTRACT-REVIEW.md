# Finite recursive-core interpreter contract review

Status: **conditional PASS for the frozen finite contract; no correction requested**. The initial source review preceded the contract's creation. I subsequently read the actual CONTRACT.json, CASES.json, SOURCE-PINS.json and COMMON-SEAL.json at 13:54–13:56 UTC, before reading either new engine or any result. This is review of the prospective experiment, not a completed run or validation of an unexecuted implementation.

Exact metadata SHA256: CONTRACT.json `3290f65dcdb7f7eae7d4ec741ec128d67822512a20b4977b30c84c7ce1f35035`; CASES.json `03d89ab4df0a679f3cbde69143a80ec65c07eb0186db6027d16344fef4b4e3d0`; SOURCE-PINS.json `46ef2331b7a636e025978d5fd9f5e638b375d28f1b1438699c8fbb8ed43b12dc`. These equal COMMON-SEAL.json. The new source manifest explicitly distinguishes five shared constructor modules from inert prose/checker provenance and the complete original TABLE.json.gz data object: fourteen objects, 140,678 raw bytes. I did not read the full source checker or any original expected/result receipt.

This is static review of the exact PR6719 constructor closure and instruction/entry semantics, using S4's retained text. The source is thu-nmrc PR6719 head `e4e52d6ba2c805fa78bb57778c3b7bbc064edba5`. I read the five module texts and the initializer excerpt, not the full source checker/observer, its expected outputs, old result receipts, or either new interpreter. No constructor, source program, scientific engine, interpreter, import, compilation, test, simulation or proof kernel was executed. Text reads and metadata hashes are the only tool activity supporting this review.

## Exact source closure

| Source module, relative to recursion/core | SHA256 |
|---|---|
| recursive.py | `0db666747ebcb6633102c7dbfbb51ec9d975aa82bf479668add7c9e4d1a2d5ad` |
| inputs/shape/producer.py | `dbd58802087ce10e39a72202960dbb5d4aa5ce50dc1b99b7ec98e07273c292b6` |
| inputs/shape/inputs/PR6719/router.py | `ccfb60465cacd3d0f458f96a505c43f5ccda6bb8eacd6ca67f8177f5fb1796a3` |
| inputs/shape/inputs/PR6719/counters.py | `2b51181a3efd403be14111ed2d556ba10e63a8939756e69d488d12344d5a7ad1` |
| inputs/shape/inputs/PR6719/machine.py | `04b7b76b9f06653d94d2158196cdd1bed7883dd1f59fcbc81a486e3ffb248681` |

The entry excerpt SHA256 is `fa8da01ed7073ff052c781cb31de3518cf6f7c7f233d8a18dfa943abbfc3daed`. It specifies fixture construction, not runtime observation or expected answers. The shared constructor closure is finite and consists of these five source modules plus their Python standard-library imports. Authenticate every source before loading it. Loading a source module that defines Machine/Tape is distinct from using those original classes to execute the resulting table.

Both new interpreters may share the authenticated `recursive.build(L,q,N)` construction. They must disclose that common dependency: two different literal machine models are not independent end-to-end construction, and agreement cannot independently validate the shared constructor or a shared observer bug. The actual returned table, tape count, entry and metadata must be canonically bound. Source nominal instruction counts are not substitutes for that binding.

## Literal instruction and observer authority

The retained machine charges one transition for each branch, write, unit move, goto and final HALT. Branch reads exactly one current symbol and chooses an explicit arm or default; write and move fall through to PC+1; goto supplies its literal target. Rejection is a dedicated outcome, not any arbitrary exception. In source statistics, branch/write visit the scanned head and move visits both departure and arrival. A new audit may state a stricter retained-space convention, but must distinguish initial support from accesses and keep visited positions after erasure.

The outer physical LEFT/BASE markers and the seven-cell prefixes are entry fixtures. Logical symbols are encoded by three nonblank Z/O digits; logical BLANK000 is not physical absence. Source/A/R/width packet body heads start three physical digits after their origin; depth is a raw unary run starting at its origin. Compiler execution does not prepare those markers or root descriptors. Their preparation time remains external, and initial backing remains charged. Malformed-store recognition/rollback is not part of the healthy contract.

A complete endpoint check must include every one of the actual 25 tapes, all nonblank cells and heads: unchanged borrowed source/A/R/width/depth, all prefix and delimiter bytes, the exact changed owned root output, and physical blankness/head restoration for every other owned role. Decoding only the output bits is insufficient. Space must retain at least initial occupied positions union all accessed positions; final sparse nonblank support is insufficient. Live-frame A/R/H/grants and source/output data may be observed externally at named event PCs; the finite program itself receives none of these host observations.

The expected semantic observer can independently implement the credited split/address/recurse/merge bit grammar: for parent bank l, index `(a*L+l)*R+r`; child descriptors `A/(L*H), H*R`; at a leaf complement bank0; otherwise recurse banks0 and1. Complete stream/index correspondence is stronger than a volume match. The observer must not call the source expected-output checker or use program outcomes to define the expected values.

## Planned cases, discrimination and resources

For L=4,q=3,N=1,T=R_body=1, the proposed `(w,d)` cases `(1,0),(2,1),(2,2),(3,1)` have root `(H,A,R,V)` respectively `(1,1,1,4)`, `(3,12,3,144)`, `(3,144,3,1728)`, `(9,36,9,1296)`. They satisfy the full global divisibility domain, not just the first edge. Their two-site occurrence-volume sums are 4,216,3024,1944. They exercise 14 node entries and ten nonroot CALL/RETURN edges altogether. This is a small finite domain, not arbitrary payloads or all depths; retain the exact bit words/pattern and all source/case pins.

The frozen control contract has five ordered rows: four negative semantic cases and one positive wrong-H one-edge control. They are suitable if they run the actual changed table and fail a semantic endpoint/trace gate rather than merely a table-hash comparison:

- Skip output protection before child retirement/pop: empty or wrong returned output must be detected.
- Omit RETURN's depth-left move: wrong subsequent remaining depth or its dedicated contract rejection must be detected.
- Wire grant H to current R **only inside grant construction**: with R_body=1 the initial R0 equals H, so depth-one can still pass. At depth two with H=3, the true child has A=12,R=9; the wrong next divisor is 4*9, so the next grant is invalid. The retained converter processes and restores each input sequentially, so sharing the current R source in this deliberate mutant does not itself force a root failure. A broad mutation that also rewires H generation would not test this claim.
- Swap restored phase continuations: bank placement and/or the second call must differ on a nondegenerate retained bit word. A dedicated rejection is allowed; an unrelated interpreter exception is not evidence of the intended control.

The maximum source packet is 1728 logical bits, with 25 fixed tapes and bounded active depth two. These sizes support attempting a bounded run without extra dependencies. No measured runtime or memory estimate follows from this review. The actual frozen limits are 180 seconds/process, five million transitions/case, 8MiB expanded table, visited addresses -8 through40,000 and a 128MiB peak-memory forecast. Far spectator cells at50,000/50,001 remain initial retained support and must stay unchanged, outside the permitted visited range. The memory value is a forecast, not an observed maximum or a proof. Preserve every timeout, construction or observer failure and do not silently reduce the case domain. Source theorem constants are deliberately loose and are not an execution-time forecast.

The actual contract incorporates the important observer gates: before-event read-only observation; whole constructed program/metadata comparison with the original authenticated table; all K parked payload maps/heads plus control/phase before push and after pop, compared as actual objects before hashing; depth restored separately; capture and compare the real changed output before destructive retirement; complete expected root endpoint; exact unchanged prefix/spectator cells; and retained backing as initial support union persistent visits. The primary recursive bit-vector observer and oracle original-index-mask observer are explicitly different methods. I have reviewed their stated contracts only, not either implementation. No source Machine/Tape runtime or original expected-output function is authorized by this contract.

## What this can contribute

Successful separate literal runs can fill S4's released emitted-table/runtime corroboration gap for these exact cases, with whole endpoints, physical backing and semantic controls. S4's conditional all-depth source proof remains predecessor evidence, not a conclusion newly established by four runs. Likewise, source primitive prices, real cover eligibility, natural-root generation, BIT/Gaussian leaves, numerical weights, stock/routes/precision/compiler/outer invoices and all five selected assumptions remain open. No new exponent, kappa, frontier, supplier adoption or merge is implied.

Credit thu-nmrc for the current constructor/core proof and author tests; Ali Romman/PR5829 for whole-high geometry and allocator; David Arias/PR2776 for machine/assembler/counter; retained stack/codec/output-before-pop/binary-control lineage and S4's scoped written external review. Substantial OpenAI Codex assistance; this is neither independent human nor kernel acceptance.
