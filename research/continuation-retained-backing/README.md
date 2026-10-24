# Retained backing across physical continuation histories

This package closes the modeled-tape backing calculation for the nineteen-tape
continuation of [#5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356)
and [#5368](https://github.com/CrocSwap/integer-mult-bounds/pull/5368).
[PROOF.md](PROOF.md) derives every payload coordinate from nested segment
origins, adds the exact unary control-frame frontier, and accounts for shared
descriptor and relay backing. It includes prefixes, markers, erased tails,
arbitrary blank entry history and outputs delivered into resumed parents.

The complete capacity is a **sum of coordinatewise historical maxima**.
Sixteen 64-cell child temporaries, each placed in a different role, use 142
cells per fresh owner but **1102 cells in one reused bank**. A child returning
one bit after writing and erasing 4096 cells retains 4175 versus 80 cells for
the same boundary sizes and a one-cell interior. Neither a fixed number of
tapes nor a local linear time bill supplies a recursive space bound.

For k payload roles, K0 total entry backing, historical path payload envelope V,
maximum depth h, parked descriptor path sum P, descriptor maximum dmax and
maximum delivered output Lmax, a sufficient complete grant is

```text
K0 + (k+1)V + (3k+3)h + P + dmax + Lmax.
```

For k=16 this is `K0+17V+51h+P+dmax+Lmax`. The exact vector formula in the proof
is tighter. A conditional `K0+19B` corollary states the path-summability premise
needed to prove an O(root volume) reserve, including descriptor and marker terms.
That production premise is left open, rather than inferred from proper nesting.

The unchanged compact-source routines supply a useful local input: a complete
rectangle with R records, b address bits and w payload bits per record has at
most **R(w+b)** binary symbols in any one lexical payload Role, including
repair keys and radix buffers. This is a source-derived local bound, not a
proof of sixteen-slot allocation success or complete recursive caller stock.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/continuation-retained-backing --check-only
python3.12 -B scripts/research_package.py --package research/continuation-retained-backing
python3.12 -B scripts/check_research_commit.py --package research/continuation-retained-backing
```

The registered normal and optimized commands authenticate package-local source
exports before execution and compare the full typed deterministic RESULT.json.
`verify.py --emit` prints a fresh receipt without editing the committed receipt.
Prospective per-tape guards check capacity before each source write; declared
trees predict exact final lengths. Source calibration checks the complete
independent compact permutation and preserved parent state, not only lengths.
See [EVIDENCE.md](EVIDENCE.md) for environment and coverage.

Only this package is added; frozen inputs and the selected frontier are unchanged.
The result counts all nineteen modeled Tape.cells arrays. It excludes Python
heap/list allocator capacity, source bulk arrays, the weak-reference allocation
facade, logical counter compilation, descriptor production, full recursive C,
stock/precision admission and the full multiplication theorem.

## Attribution

[@aliromman](https://github.com/aliromman) supplied the unchanged physical stack
and output return in [#5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356)
and [#5368](https://github.com/CrocSwap/integer-mult-bounds/pull/5368).
[@JoyboyBrian](https://github.com/JoyboyBrian)'s
[#5329](https://github.com/CrocSwap/integer-mult-bounds/pull/5329) supplies the
segment/source boundary; [#5041](https://github.com/CrocSwap/integer-mult-bounds/pull/5041)
supplies locality context. [#5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286)
by [@kumagi](https://github.com/kumagi) supplies earlier coordinatewise history
accounting for a different bank, retaining the prior numerical/packet-backing
work's credit for that accounting principle.
[@jmbarrancoml](https://github.com/jmbarrancoml) supplied sequential compact
primitives through [#2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250).
Douglas Colkitt, Cinna Davis, [@Matarener](https://github.com/Matarener), the
guard/repair/carry/native lineage and original source notices retain their credit.
The alternative stack [#5364](https://github.com/CrocSwap/integer-mult-bounds/pull/5364)
by [@mihir-s-05](https://github.com/mihir-s-05) is a distinct encoding, not
audited or replaced here. New work by [@zxv](https://github.com/zxv), with
substantial OpenAI Codex assistance in proof, implementation and assisted review.
Review shares source context; no independent human or formal-kernel acceptance
is claimed. Apache-2.0; see vendor/NOTICE.md and retained module notices.

## Open next questions

1. Prove a production path envelope for actual parked payloads and generated
   descriptors. Start at one literal recursive call and derive G(v), including
   erased interiors and markers. The production recursive-C/descriptor compiler
   and common-cut bounds remain blockers; a local time tariff is insufficient.
2. Compile lexical allocation and logical counters physically. Start with
   repair/stable_radix and its erased-but-retained owners. The per-Role length
   bound does not prove slot reuse or allocation success.
3. Integrate the complete vector grant into a caller reserve. First bind each
   actual role's local peak and inherited K_j. External caller banks, source
   bulk-array lowering, numeric stock and placement remain separate obligations.
