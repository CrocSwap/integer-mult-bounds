# PR6372 forward-CLEAR form gap

**No new κ.** The declared local rank margin of PR6372 does not discharge two
nonzero forward CLEAR functionals.

## Scope and evidence

Task `supplier-boundary-audit`, scope **refined**. The card asks whether one
changed supplier has complete admission coverage. This package answers one
gate on the frozen PR6372 word: the two added frame-127 CLEAR forms are
nonzero, agree off an explicit eight-term difference, and are absent from the
MOVE rank margin `2H_4 - 2H_5` paid and `2H_8 - 2H_9` productive.

The candidate word is PR6372 head `b556600ffe14be72406b03a47c661f3c7f1aff06`,
blob `0af79e58172f85c302c35b193205c0b185b09393`. The source word is that
package's PR6353 input, blob `03ea7690285d4cda72815f962d5710ab96e08490`.
Those commits are not ancestors of this branch. The copies under `inputs/`
are authenticated by SHA256 and Git blob id inside `verify.py`. Catalogue and
selected-record pins are provenance at base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

PR6376 already recorded that these two CLEAR rows have public support 97 and
that dual-preparation zeros do not grant forward erasure. The new statement
is the exact difference

```text
f - g = 2(e_27 - e_57 + e_87 - e_92 + e_228 + e_230 - e_232 - e_234)
```

and the separation of that pair from the MOVE-only margin. The argument and
the non-claims are in [PROOF.md](PROOF.md).

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 -B research/p104-6372-clear-form-gap/verify.py
python3 -O -B research/p104-6372-clear-form-gap/verify.py
python3 scripts/research_package.py --package research/p104-6372-clear-form-gap --check-only
```

Both verifier modes print

```text
PASS_P104_6372_CLEAR_FORM_GAP support=97 difference=8 paid=2H4-2H5 productive=2H8-2H9
```

The run is a full literal replay of the two pinned words and finishes in about
a second. It does not import PR6372 or PR6376 code. A one-coordinate mutation
of `f` is required to change the difference, and the source word is required
not to contain these CLEAR indices.

## Open next questions

1. **Does the retained owned-erasure contract allow these two discards?**
   The forms are nonzero public functionals on owned roles 779 and 780.
   Why it matters: PR6372's signed margin has no term that cancels them, so
   any claim that they are free still needs the contract, not the rank
   expression. First step: quote the allocation/erasure rule that applies to
   a frame-127 owned CLEAR and test these two rows against it. Blocker: the
   selected `owned_erasure` assumption names the contract without reproducing
   its permission predicate in this package.
2. **Does the same difference survive PR6375?**
   That successor keeps this word's bytes and then changes six other helper
   inputs. Why it matters: a transferred margin would reuse a false erasure
   reading. First step: replay the same CLEAR indices on the PR6375 word.
   Blocker: this certificate is pinned to head `b556600f` and does not load
   that later word.

## Credit

Ali Romman supplied PR6372 and the `2(H_8-H_9)-2(H_4-H_5)` margin. ToikY's
PR6376 recorded the support-97 forward rows and separated them from the
dual-preparation zeros. DreamingOfClouds's PR6375 is the successor this
certificate does not transfer to. Unpaidmoon's PR6353 ordinary-work and
stage-1 contact notes stay on that earlier supplier and are not this gate.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
