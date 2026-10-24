# Literal old-low to carry-descriptor frontend

**Partial result: helper462/frame506 now has a five-tape finite-alphabet frontend from the actual old-low cache to a new-low word and the exact binary carry descriptor C+1. The complete payload low-type permutation and full route lowering remain unfinished.**

The new source-specific lemma is that every carry in both directions is `k/4 mod q^(w-1)` for one fixed integer `-7<=k<=12`, independent of width, q and tensor multiplicity. The emitted runtime program uses only scanned-symbol branches, unit moves, writes, jumps, halt and reject. It physically dispatches the quarter code, generates the modular binary descriptor, clears that code and restores both inputs and all heads. There is no runtime host arithmetic or free type-table lookup. [PROOF.md](PROOF.md) gives the all-width proof, explicit N,q compiler costs and complete frontend transition/visited-space bounds.

The assigned q5,w4 fixture produces cell5 `(new_low,carry)=(4,124)`. Another invertible low matrix admitted by the actual source, `I+3e05`, produces cell0 `(1,1)`. PR5019's existing later-target shear cannot directly update the first high coordinate. Two paid completed OLD swaps would repair this interface; that is a conditional added bill, not a bug in PR4989 or a fixed-tape impossibility result.

The bounded checks run 148 linked frontend cases against the independent source modular-M oracle, including both directions, q3/5/7, w2/4/9 and actual strided f2 cache positions; 240 offset cases include 40-bit Q. The unchanged source interpreter also runs a full route round trip on the admitted cell0 input. Negative controls cover old-cache lifetime, inverse direction, missing dispatch, malformed encodings and descriptor residue semantics. The full GL payload is not materialized. [RESULT.json](RESULT.json) records the precise coverage and false closure flags.

## Reproduce

From the repository root, using CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/bit-low-carry-lowering
```

The registered normal and `-O` commands run the new bounded verifier only. All necessary predecessor bytes are retained under `vendor/`, authenticated against [RETAINED.json](RETAINED.json); replay needs no pending Git objects. The source heads are PR4989 `fe886dc0431d33e9df856b47d0510f1ec66ef750` and PR5019 `39f3cf9fb4f2e495a716c7b501ea3bceb6b2a748`. The base and priority card remain pinned through [SOURCES.json](SOURCES.json). Their scientific claims are not independently recertified by byte authentication.

## Open next questions

Implement the full finite low-type block permutation, old-cache retirement and source/output installation at the actual payload layout, then combine the descriptor frontend with the complete high-coordinate route and the paid first-coordinate repair. This is the precise remaining implication; it is blocked by an unimplemented full-fiber controller, not by descriptor width or a claimed universal obstruction. The next experiment should execute one tiny complete invertible-low domain with arbitrary payload/spectator tags and derive its all-size tariff before binding N=8f. [TASK.json](TASK.json) preserves the original assignment and narrowed outcome.

## Credit and limits

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0. Preserve JoyboyBrian PR4989/5019, Chris R/Clear1nsight PR4957, ai-nanachi PR4760/4814/4326, David Arias PR2776, Charles Bethin's unit-carry work, rohanarun PR185/199, Maxime Fleury PR204, Cinna Davis, zxv, Jacob Alan Sussman, Mark/Matarener and the retained native/ordinary/ROW/tape lineage. Their bytes are unchanged. This is an author-checked algorithmic frontend proof with bounded tests, not a formal proof, complete supplier admission or a new kappa.
