# Independent fixed binary-caller endpoint audit

This checks the **actual 353-event, 34-field, 19-stage caller** retained from
PR6348. Two separately implemented engines compare every one of its 1,156
input-to-output Laurent polynomials with its advertised diagonal. The result
is a conditional formal identity, with arbitrary independent inputs.

The coefficient ring is
`Z[Q,Q^-1,D1,D1^-1,...,D19,D19^-1]`. All 19 stage symbols remain distinct.
Q is an indeterminate: no finite-order relation or sampled evaluation is used.
The frozen source stores 21 exponent slots, including an unused stage-zero
slot; the checkers require that slot to vanish and use the 20 actual variables.

## What is checked

The exact source `CONTROLLER.json` contains every instruction and every target.
Its SHA256 is
`6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f`,
Git blob `1f2e375b24aba5fb25580dfea7fab7a2049f3eb8`, retained at canonical
main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The archived PR6348 head is
`9894015d6f380206f990ad5fd14bc49bbd26b0d0`. Archival intake is not acceptance.

`verify.py` starts from each output coordinate and pulls its functional back
through the literal events in reverse order. `oracle.py` independently starts
from each input coordinate and propagates it through the chronological word.
Both use exact integer coefficients and sparse Laurent monomials. They import
neither the source generator/checkers nor one another. Every matrix cell is
compared, including all off-diagonal zero polynomials; a digest summarizes the
already checked matrix, rather than substituting for equality.

Reverse functional substitution is a formal transpose calculation. It is not
inverse execution and does not conjugate coefficients or negate exponents.
For LOCAL(s,src,dst), the forward semantics are

```
src' = D_s src
dst' = D_s (dst + Q^-1 src).
```

Thus the reverse weights are
`w_src,pre = D_s w_src,post + D_s Q^-1 w_dst,post` and
`w_dst,pre = D_s w_dst,post`, using the old weights simultaneously.
ADD, signed SCALE, SWAP, QUERY, Q_POWER and IDLE
retain their explicit source semantics. [PROOF.md](PROOF.md) states the full
inductive justification and conditional specialization to commuting units.

The common normalized matrix SHA256 is
`8263cc6b643ee815427d7d8a08e1080e920b9de070bac26a49383424f9d20fd2`.
There are 34 nonzero endpoint monomials and 1,122 zero off-diagonal cells.
The primary independently checks the event determinant against the diagonal:
`(D1...D5)^6 (D6...D19)^8`, with positive sign and Q exponent zero. This is
a unit in the declared Laurent ring. Both methods observe at most seven
terms per propagated row/column and one term per cell on the baseline word.

The retained receipts include actual coefficient witnesses for changed literal
words, such as removing a whole idle, translation or query, and changing an
orientation, scalar sign or stage label. These are formal-word controls under
the same semantics, not physical no-go theorems. Source-corruption and typed
receipt controls are separate transport checks. Complete source bindings and
final verification are in `SOURCE-PINS.json` and `VALIDATION.md`.
The primary has seven semantic controls; the forward oracle has eight. Its
additional Q_POWER sign flip changes a Q exponent by four and has a formal
coefficient witness, which can disappear under an extra relation Q^4=I. It
must not be presented as a physical error.

## Reproduce

With Python3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/balanced-caller-endpoint-audit --check-only
python3.12 -B scripts/research_package.py --package research/balanced-caller-endpoint-audit
```

The manifest runs both engines normally and optimized. They strictly compare
typed canonical JSON with `RESULT.json` or `ORACLE.json`. `--emit` prints a fresh
candidate without writing files or comparing a retained receipt. Package-local
byte-exact copies make replay independent of foreign Git history and network
access. The five retained source files authenticate before calculation; Python
sources and upstream proof are data, never imports. `SOURCES.json` separately
binds the base catalogue and selected record as provenance.

## Exact scope and prior work

The source author already checks the complete forward Laurent identity and
provides a four-field extension/tree-induction proof. This result is independent
execution evidence for that exact caller, not a newly discovered generic
identity or a flaw in the predecessor proof. The selected6030 audit covers a
different 18-call caller. Earlier5550/5717 callers, the5442 all-width lifting
work and its older5413 controller,4457's older p17/p16 words and3937's integer
shear obstruction retain their distinct scopes and credit.

PR6359 independently recounts the finite invoice while assuming this caller's
advertised diagonal. This package checks that **formal endpoint premise**. It
does not verify that actual native stages, physical contacts, phases or fresh
axes realize the assumed LOCAL/QUERY/IDLE operations. All34 inputs are arbitrary;
this is not permission to initialize productive helpers to zero or erase them.
Formal identity specializes through a ring homomorphism whenever the declared
operators are commuting units; injectivity is unnecessary. Proving those
physical hypotheses remains a separate source-specific obligation.

No native all-width implementation, physical caller admission, owned erasure,
complete funding, uniform compiler, precision tape, analytic recovery, new kappa
or integer multiplication theorem is established. All five framework assumptions
remain and the selected frontier is unchanged. No other package is modified.

## Coordination and credit

Changed `joint-query-controller` card: this audits one fixed endpoint premise
instead of searching for a new demand. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19344535)
takes [handoff19344470](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19344470).
Live overlap was bounded, not proof of novelty. The exact refreshed base,
coverage, stop rule and open next questions are in `TASK.json`.

Construction and four-field/tree proof credit stays with Ali Romman, with
substantial OpenAI Codex assistance, Cinna Davis and the P104 local/query
interface authors, PR6167/5544 and the complete retained
[NOTICE](sources/NOTICE). Retain prior independent caller, all-width and selected
reviewers' credit. The new source-specific reverse/forward audit and controls
are ToikY's contribution with substantial OpenAI Codex assistance and three
bounded agents for separate engines, overlap and proof review. Same-session
agent review is author-side evidence, not independent human or formal acceptance.
Apache-2.0.

## Open next questions

`TASK.json` gives relevance, first steps and blockers. The smallest useful next
work binds an exact changed native-stage/contact to the declared formal LOCAL
matrix, including absolute phase and arbitrary input. Complete source-specific
ordinary/compiler/outer funding remains separately necessary. Stop on one exact
failed contact, omitted charge or bound; do not transfer this formal result into
supplier admission.
