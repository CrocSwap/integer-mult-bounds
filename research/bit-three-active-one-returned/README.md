# Three active targets and one returned register

Three invertible lower-triangular rational 3 by 3 target frames need at
least nine paid calls in the formal binary scalar-register model below.
Nine calls suffice. The targets can differ. The fourth input is arbitrary
and must return unchanged. This is a scoped negative result. It gives no
new integer-multiplication exponent or kappa value.

Each paid factor is `I + ([A]-1)N` in `F_2[M_3(Q)]`. The address frame
`A` is nonzero and has rational rank one. The scalar matrix `N` is a
binary rank-one idempotent on four registers. The endpoint is
`diag([C_1],[C_2],[C_3],1)`. The proof has no bound on rational entries.
It does not cover an input that starts at zero and has a discarded output.

Read [PROOF.txt](PROOF.txt) and [AUDIT.txt](AUDIT.txt). The finite reduction
has a complete scalar catalogue. Two arithmetic engines check every
retained word. The original independent audit checks the catalogue and
the order coverage through different algorithms. This is a written and
computer-assisted proof, not a proof-assistant result or a human review.

The material predecessor is [PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468).
Its [three-register proof](https://github.com/CrocSwap/integer-mult-bounds/blob/07a78bf335b0b5039a1fecd7cd74a0fe1d1605ea/research/bit-three-register-lower-bound/README.md)
supplies the span-four and three-register bounds. The present proof states
the extension to an unchanged fourth register. That predecessor credits
the register model and the dimension-two flag bound to
[PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288), at
[its recorded source](https://github.com/eumemic/integer-mult-bounds/blob/475a088b5862f75f0b10596cfd6842d19531a5ec/research/negative-results-paradigm-search/README.md).
The pinned PR #468 proof also credits @huxint's
[PR #203](https://github.com/CrocSwap/integer-mult-bounds/pull/203) for the
related common triangular-frame obstruction, at
[its recorded commit](https://github.com/huxint/integer-mult-bounds/commit/d2873e20750d0949d2ad75cbc4cd82b5b1a74e84).
OpenAI Codex and research agents prepared the local proof and checks under
the user's direction. No independent human review is claimed.

From this package directory, with Python 3.10 or later and a C++17 compiler:

```sh
python3 -B verify.py --build /tmp/three-active-one-returned-replay
```

The build path must not exist. The script uses only the standard library.
It writes all generated files to that path. Set `CXX` to a compiler path
if needed. Allow about 200 MB for generated files. The wrapper checks the
saved source hashes and rejects optimized Python because the original
generator uses assertions. Python child processes ignore Python environment
options, so their assertions remain enabled.

The final result must contain:

```text
Exact checks: 2 27156 0 0
Exact checks: 3 1901600 538 0
Receipt: <build folder>/receipt.json
```

The original source bytes and receipts are retained. `SOURCE-MANIFEST.json`
maps each one to its local origin and SHA256. `receipt.json` is the original
full replay. `replayed-receipt.json` and `replay.log` record the cleanup
audit replay. The primary replay repeats the full primary generation and
both arithmetic engines. `replayed-independent-receipt.json` and
`independent-replay.log` record a separate complete replay of the
independent front end and its seven formal-polynomial controls.

The independent generator sources are in `independent-sources/`. After
the primary replay, run the complete independent front end with:

```sh
python3 -B verify_independent.py --primary-build /tmp/three-active-one-returned-replay --build /tmp/three-active-one-returned-independent
```

The second build path must not exist. This command reconstructs the
catalogue, checks both multiset censuses and all rank-two and rank-three
orders, and binds those results to the primary binary streams. It also
runs seven formal-polynomial controls. Those controls are not paid-call
circuit constructions. Large generated inputs remain outside the package.
The unchanged historical control script requires `clang++` on `PATH`;
the other compile steps use `CXX` when it is set.

The independent review also checked all 538 terminal words with exact
`Fraction` arithmetic. The saved historical terminal receipt is included
in `independent-sources/work/four-register/independent/`. The fresh result
is `replayed-fraction-terminals.json`. To repeat that check after the
primary replay, run:

```sh
python3 -E -B verify_fraction_terminals.py . /tmp/three-active-one-returned-replay /tmp/three-active-one-returned-fraction.json
```

The original cleanup replay receipts predate the final addition of the
historical Fraction receipt to `SOURCE-MANIFEST.json`. They record the
sources and checks present at that run. The final independent review
binds the complete package, including the added receipt.

The current [mixed-target compression result](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/bit-mixed-target-register-compression/README.md)
bounds the number of extra roles for a possible eight-call word but does
not rule that word out. The [parity-uniform target result](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/bit-parity-uniform-targets/README.md)
permits arbitrary dirty workspace when all target classes agree modulo
two in the generated address lattice. This package imposes no such parity
condition and uses exactly one returned role.

## Open next questions

Can the same lower bound cover three distinct target frames with more
than one arbitrary returned register? The first step is to compare the
scalar compression and invariant-subspace reductions with the current
mixed-target results. The four-register catalogue does not cover the
larger scalar alphabets. This package also supplies no physical compiler
or price for an alternative circuit.
