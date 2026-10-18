# Finite substitution and exact accounting

Let `W` be the immutable R480 word pinned in `SOURCES.json`. Its A[2409:2460] gates all act at frame 487 on the twelve registers
`(19,24,35,40,54,56,65,74,84,95,100,111)`. Their ordered Boolean row masks are
`(3327,2390,4083,4,3935,4015,4092,16,207,256,1023,1)`.

Each candidate gate is the elementary shear `r_d <- r_d XOR r_s` at that same frame. The verifier evaluates the original and replacement on every one of the 4,096 Boolean inputs and requires every **ordered** output to agree. Since all later gates have unchanged ordered operands and are linear over F2, replacing this subword preserves its subsequent Boolean action on every source, target and dirty-helper column. The finite complete-word replay independently checks this implication rather than relying on it alone.

The search uses `L M R = P`, where L is a product of row shears, R a product of right shears, and P an explicitly recovered permutation matrix. Its emitted chronological operations are the recorded right shears, the XOR-swap realization of P, then the reversed left shears. Every swap costs three ADDs. The verifier imports no search code and checks the resulting transfer directly; this description is not used as a certificate acceptance shortcut.

All operands remain source registers in the same rank-four frame. The verifier reconstructs the complete frame chronology and requires every one of the 720 individual frame paths to equal the frozen word's path. It checks strict frame nesting and independently computes exact rational frame ranks. Thus the multiset of paid MOVE ranks remains unchanged. The COPY ranks are nine eights, and all copied-source lifetimes and external-work closures are checked. No helper is allocated, relocated, omitted or silently restored.

C is rebuilt as the literal reverse of all source/helper-destination gates in A followed by B, at the rank-eight full frame. The block saves ten A ADDs and ten C ADDs. D, B, retained totals and scatter remain unchanged. The new invoice explicitly counts all scatter ADDs and cleanup ADDs and yields **33,938**, from **33,958**. The unchanged exporter produces exactly the same six-int raw records as the new independent reconstruction. The paid histogram is `{1:1200,2:1440,4:180,6:120,8:9}`, of rank mass 5,592.

An old C circuit may remain a Boolean inverse of the new block, but fails the required literal-cleanup predicate and has a different invoice. Accordingly, the stale-cleanup control first passes the complete Boolean endpoint and is then rejected by the literal contract. This separates endpoint correctness from this source-bound implementation contract.

For the integer lift, elementary ADDs in the signed inverse have coefficient -1. Reversing the candidate's signed shears restores its twelve inputs exactly over Z; the verifier checks its integer matrix against the identity. This does **not** imply that the original and new integer forward matrices agree, or that the complete signed multiplication construction is proved.

Following the pinned `columns_h.cpp`/`columns_k.cpp` rule, initialize every persistent row-norm bound to one. An ADD updates `u_d <- u_d + |c| u_s`; COPY initializes external work from its unchanged original center; ERASE closes it to zero. Reverse traversal interchanges COPY and ERASE and negates ADD coefficients, leaving their absolute values one. Compute the maximum row bound in both orientations. Exact results are:

- Original: `F=176135`, `B=3751204`, `64 F^3 B^2=4921056267806722187755121024000`.
- Candidate: `F=176135`, `B=3714396`, `64 F^3 B^2=4824956153877587673775933824000`.

Both payloads are strictly below `2^104` and have bit length 102. No unpriced precision increase is required. A separate endpoint-valid 1,000-gate neutral insertion demonstrates that Boolean equality alone cannot admit a circuit: it passes the endpoint, but its chronological positive invoice exceeds the cap and is rejected.

The new set-valued local engine covers all 720 formal columns, including arbitrary helper dirt. A separate integer-bitset implementation executes the literal PR363 bridged schedules with 2, 4 and 5 bank pairs on both words, covering 960, 1,440 and 1,680 formal columns respectively. Every bridge omission is rejected on the candidate. The unchanged inherited `xcheck_p.py` checks labels, all 672 closed frames, endpoint, H1-H5 and their U/J/K/restoration conclusions; the PR425 interface checker independently checks its more specialized hypotheses. These are finite checks and source-bound accounting, not a formal proof of a uniform compiler or of the full multiplication theorem.

The selected PR589 R439 supplier is a different word. The new witness is not composed with it, PR1003's Q-node2 or PR1027's quad12. Neither an improved moment nor a new kappa follows from these twenty finite scalar ADDs. Inherited physical, hosting, precision/tape, all-size/compiler and analytic obligations remain as listed in the README.
