# Exact bill for the literal child-grant producer

This external audit derives an exact transition ledger and a safe **60(S+K)** transition envelope for the nine-tape descriptor producer in [thu-nmrc's PR6719](https://github.com/CrocSwap/integer-mult-bounds/pull/6719), pinned at `3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`. It also checks the complete source-emitted producer using separately authored sparse and dense interpreters. The source program, arithmetic construction and classical counter formulas are credited predecessors.

Fix L>=2 before runtime. The inputs are positive canonical binary A,H,R on three distinct tapes, with LH dividing A. Put q=A/(LH), K=HR and S=A+H+R. Four additional work tapes and two output tapes have supplied owned blank backing. The producer returns canonical q,K with their heads at one, preserves all original input bytes and heads, and erases all four work tapes and returns their heads to zero. Its finite table depends only on L; A,H,R are runtime header data.

With the credited converter and from-zero counter formulas

```
c(x) = 24x - 7 popcount(x) + 15 bit_length(x) + 12
C(x) = 13x - 7 popcount(x) + 5 bit_length(x),
```

the literal successful producer has exact cost

```
T = c(A)+c(H)+c(R)+C(q)+C(K)
    +12A+11H+R+6K+(4L+2)q+46.
```

[PROOF.md](PROOF.md) accounts for setup, first and subsequent rewinds, every quotient/product increment, scratch retirement and the **actual success HALT**. It proves T<=60(S+K) and total distinct visited local cells <=10(S+K) for all promised inputs and every fixed L>=2. The constants are safe envelopes, with no sharpness claim. For L=2,A=2,H=R=1, the exact cost is 291 transitions and 30 visited cells. The earlier [increment audit, PR6725](https://github.com/CrocSwap/integer-mult-bounds/pull/6725), supplies the sharp from-zero C(x)<=15x bound; this is not a per-call bound at arbitrary counter state.

The counted object is the producer through its success HALT. Input encoding/backing, compiling the table, delivered-grant lifetimes and retirement, routing, child payloads and consumers have separate obligations. Source bounds for a linked producer/router/consumer cannot be replaced by this producer-only bill.

## Evidence and replay

The authenticated shared emitter imports the pinned producer/machine/counter/router closure and calls only producer.build(L), at L=2,3,4,7. Neither checker calls the source Machine/Tape interpreter, router builder, linked caller or original checker. Candidate construction is shared; the sparse and dense execution engines are separately authored. This is not independence of end-to-end construction.

Both blind first runs passed before reading peer certificates. Their complete 92,290-byte certificates were identical, with SHA256 `4ea1cffdc2d4a3b8e443daec4d397e7adbedddae896d18c1e51171c0fa6a5800`. Each contains all 261 case rows: a 256-case grid and five boundary cases, with actual outputs, heads, visited extents/counts, complete endpoint digests and ten controls. Endpoints bind all nine nonblank tape maps, including untouched guards. Every positive case checks input preservation, canonical outputs, full scratch erasure and measured 60/10 envelopes. Full HALT costs one.

Four actual-table mutations expose wrong quotient/product values, residual work and wrong input-head return. Three raw malformed fixtures must reach dedicated source REJECT instructions; three parser controls reject duplicate keys, float tokens and Boolean integers. Rejected execution has no rollback promise. [STRICT-MODES.json](STRICT-MODES.json) records four passing normal/optimized retained-certificate checks. First receipts record 0.122 seconds/31,997,952 bytes RSS for the primary and 0.619 seconds/32,768,000 bytes for the oracle on managed Python 3.12.14. These are finite local observations, not performance guarantees.

Default checker execution is read only and recomputes the whole retained certificate. `--certificate PATH` checks an alternate actual certificate; only `--emit PATH` writes one. The exact metadata, thirteen core/input paths, source bytes and complete emitted tables are authenticated. [VERIFY.json](VERIFY.json) specifies the registered commands; [VALIDATION.md](VALIDATION.md) records subsequent verification and transport status. Finite case agreement supports the source binding; the written invariants and ledger establish the all-size implication under the named model.

## Open next questions

1. Can the exact ledger be carried through the actual linked child router and delivered-copy consumer? First bind its tape reuse, HALT replacement and complete consumer events to the existing source table. This would connect the smaller local bill to a larger caller invoice; that binding is outside the audited producer.
2. Can the real production path generate H and the parent A/R headers at every depth? First audit one actual descriptor-production edge with its retained backing and lifetime charges. The present ABI receives those headers, so its theorem does not supply that preprocessing.
3. Can the full codec/stack/consumer composition preserve these bounds and all required returns? First bind one exact emitted composition and a complete ledger, then prove the recursion invariant. The source's physical continuation evidence and coarse 1000V/100V bounds remain separate predecessors, not re-admitted here.

No full supplier, all-five-assumptions admission, productive credit, paid profile, kappa improvement, selected-frontier change or scientific adoption follows. The remaining physical, precision, traversal, payload, consumer and storage obligations stay explicit.

## Credit

thu-nmrc/PR6719 supplies the producer, descriptor ABI, source functional proof and earlier coarse bills; David Arias/PR2776 supplies the unchanged machine, assembler and converter. Ali Romman/PR5829 supplies whole-high geometry and address lineage. Jose Manuel/JoyboyBrian binary-control/divisor work and the retained segment, codec, stack and output-return authors retain their source credit. ToikY's PR6725 supplies the external sharp increment audit. This package adds the source-bound exact full-producer ledger, safe envelope proof and separate execution audit, with substantial OpenAI Codex assistance. Original notices are retained under Apache-2.0; see [NOTICE](NOTICE) and [SOURCE-PINS.json](SOURCE-PINS.json).

External rejection validation:20 cases/40 actual CLI rejections pass in revised v2. The first harness stopped after the primary correctly rejected the coherent false table with the stronger one-success-HALT diagnostic, rather than the harness expected whole-certificate diagnostic; exact failure retained. No engine/core/certificate changed. The inherited v2 first_suite label is qualified in REJECTION-HARNESS-REFINEMENT.md. Exact visited-space formula is a written-proof result; finite engines record all visits and check the envelope, without a separate symbolic F equality guard.
