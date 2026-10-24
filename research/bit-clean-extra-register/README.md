# Restrictions for three active targets and one clean extra register

This package proves restrictions on an eight-call formal binary circuit.
There are three active targets and one extra input that starts at zero.
The extra output is discarded. The required upper-left block is
`diag([C_1],[C_2],[C_3])`, where the targets are invertible lower-triangular
rational 3 by 3 frames. Paid factors are `I + ([A]-1)N`: `A` is nonzero
and has rational rank one, and `N` is a binary rank-one idempotent on
four registers. The coefficient ring is `F_2[M_3(Q)]`.
The endpoint is the product of these listed paid factors. No additional
free scalar map is applied at the end. The clean active-block condition
alone does not justify removing such a map from a broader circuit model.

The [final report](sources/four-register/FINAL-CLEAN-REPORT.txt) states
the scope and proof dependencies. The results are:

- Paid-frame span at most four needs at least nine calls. This bound
  permits any number of clean extra registers.
- Span eight is impossible. Span seven forces zero active off-diagonal
  entries in every scalar projector.
- For one clean extra register, the complete 24-projector class with
  zero active off-diagonal entries is impossible in eight calls.
- Eight calls are also impossible over the union of the coordinate-basis
  projectors and one arbitrary binary-basis set of projectors.

The remaining arbitrary four-register problem has frame span five or six,
a nonzero active off-diagonal pattern, and an alphabet outside the last
class. It remains open here. Fixing one basis to the coordinate basis is
a restriction; it is not a normalization of every pair of bases. These
results give no construction, complete clean-register lower bound, or
new kappa value.

The [span proof](sources/four-register/CLEAN-SPAN-FOUR.txt) extends the
method in [PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468),
at its [recorded source](https://github.com/CrocSwap/integer-mult-bounds/blob/07a78bf335b0b5039a1fecd7cd74a0fe1d1605ea/research/bit-three-register-lower-bound/README.md).
The [one-relation proof](sources/four-register/CLEAN-ONE-RELATION.txt),
[zero-pattern proof](sources/four-register/independent/clean-zero/PROOF.txt),
and [independent scope audit](sources/doubling-architecture/rank-independent/clean-audit/PROOF-AUDIT.txt)
give the other arguments. The predecessor credits the scalar model to
[PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288), at
[its recorded source](https://github.com/eumemic/integer-mult-bounds/blob/475a088b5862f75f0b10596cfd6842d19531a5ec/research/negative-results-paradigm-search/README.md).
The pinned PR #468 proof also credits @huxint's
[PR #203](https://github.com/CrocSwap/integer-mult-bounds/pull/203) for the
related common triangular-frame obstruction, at
[its recorded commit](https://github.com/huxint/integer-mult-bounds/commit/d2873e20750d0949d2ad75cbc4cd82b5b1a74e84).
OpenAI Codex and research agents prepared the proof and checks under the
user's direction. No independent human review is claimed.

From this package directory, with Python 3.10 or later and a C++17 compiler:

```sh
python3 -B verify.py --build /tmp/clean-extra-register-replay
```

The build path must not exist. `CXX` can select the compiler. The runner
copies the saved source files there before any generated output is written.
It rejects optimized Python because some historical sources use assertions.
No repository source or third-party Python module is required.

The final line must be:

```text
PASS_CLEAN_RESTRICTED_CLASSES 314666 7406643
```

The replay checks all 314,666 zero-pattern words with primitive-integer and
finite-field engines and compares every output record. A separate generator
checks all 3,674,160 raw orders by dependence signatures. It also checks
all 166 basis alphabets, with 7,406,643 words, in the finite-field engine.
The basis catalogue is reconstructed through dual-vector tests. A separate
rational engine checks 48 fixed words from the saved independent receipt.
The full basis search does not have a second complete arithmetic replay.

`SOURCE-MANIFEST.json` records the original paths and hashes. Source bytes
are unchanged. The new runner only makes the existing checks portable and
compares their outcomes. `expected/` contains historical receipts. The
new `replayed-receipt.json` and `replay.log` record the cleanup audit run.
Historical prose can name receipts at their old paths; `expected/`
contains the receipts used by this replay. The earlier layer-only audits
and returned-register controls are historical evidence. They are not
replay dependencies. The current runner executes the 166 basis checks
in sequence; the preserved historical scheduler used three workers.
Python child processes ignore Python environment options so their
assertions remain enabled.

## Open next questions

Does an eight-call clean circuit exist in frame span five or six outside
the two excluded scalar classes? A first step is an exact completeness
reduction for the remaining nonzero active off-diagonal patterns. The
present reductions do not bound that full scalar search. A positive word
would still need an all-size compiler and a full cost calculation before
it could affect kappa.
