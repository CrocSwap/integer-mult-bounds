# Independent audit of the all-even attaining word

**PR6717 section 7 checks out within its algebraic contract.** The independent
written derivation confirms ranks `(2q,3q,2q)` and the full formal endpoint
`S diag(ABC,AB,B,C,I_(n-4)) tensor I_q`, for every even `n>=4`, `q>=1`, over
fields of characteristic different from two. Every input remains independent.
This is a construction audit, not an independent proof of the `7q` lower bound.

The source is thu-nmrc's [PR6717](https://github.com/CrocSwap/integer-mult-bounds/pull/6717),
head `3c9072b8738323dda9f9c7dfb421d578ed3fc17a`, section 7 of its `PROOF.md`.
[PR6721](https://github.com/CrocSwap/integer-mult-bounds/pull/6721) separately
reviewed section 6 and released the attaining-word obligation in the
[handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19405518).
This audit's canonical coordination is [Discussion 6730](https://github.com/CrocSwap/integer-mult-bounds/discussions/6730).

## What was checked

- [PROOF.md](PROOF.md) independently derives unimodularity, all six selected
  query factors including extra coordinates, the full query endpoint, actual
  prefix conditions, exact stage chronology, and the all-width extension.
- [verify.py](verify.py) rebuilds the printed construction without importing
  predecessor code. It multiplies every input column of the literal word in
  `Z[S,A,B,C]/(S^2-1)`, retaining three independent stage variables.
- Eighteen finite cases cover integer coefficients at `n=4,6,8,10,12` with
  `q=1`, plus `(n,q)=(4,2),(6,2),(4,3)`, and coefficient reductions modulo
  3 and 5 for the five scalar dimensions. Modular cases are convention
  checks; exact integer identities already imply their reductions.
- Four controls reject a last-column sign error, a lost extra input, swapped
  query chronology, and an endpoint-preserving incompatible final query.

The last control is the useful coverage distinction: at `n=6`, omit the last
column's extra alternating correction. The altered basis remains unimodular
and the **entire formal endpoint still passes**, but the final stage fails
`Pn Rn=Rn`. Section 8 derives the explicit nonzero defect. Endpoint checking
alone cannot certify this construction's local compatibility contract.

## Reproduce

Python 3.12, standard library only. The standalone checker is Git-free and
read-only, including authentication of the three exact copied source texts:

```sh
python3.12 -I -B research/p104-attainment-independent-audit/verify.py
python3.12 -I -B -O research/p104-attainment-independent-audit/verify.py
```

Or use the registered hook from a Git checkout containing the pinned main:

```sh
python3.12 -B scripts/research_package.py --package research/p104-attainment-independent-audit
```

[SOURCES.json](SOURCES.json) separates main provenance from inert copied
predecessor text. The pending PR commit is not a Git-history dependency;
`verify.py` authenticates its copied proof, notice and license against exact
SHA256 and Git-blob pins. No network fetch or predecessor program is needed.
[VALIDATION.md](VALIDATION.md) records actual runs, environment and limitations.

## Scope and remaining work

This supplies independent AI-assisted derivation and executable finite checks,
not independent human review or proof-kernel verification. The finite grid
supports conventions; the written proof supplies unbounded `n,q` and field
scope. Tensoring this explicit construction does not classify arbitrary
coupled projectors. Sections 2-6's universal lower bound, native/physical
realization, complete paid invoice, precision, ownership, compiler and outer
framework obligations remain outside. No new kappa or selected-frontier change.

The `formal-interface-lemma` card is explicitly changed to this written and
executable audit. It does not satisfy a proof-assistant formalization gate.
No scientific predecessor replay was run, and no selected assumption is
claimed discharged. Main source-binding orientation passed for selected #6030.

## Open next questions

Independently review a remaining lower-bound implication in PR6717 sections
2-5. This matters because attainment alone does not establish minimality.
First refresh the source head and live overlap, then choose one exact
normal-form or odd-projector implication with its field/coupled hypotheses.
This needs a separately scoped audit; no work is reserved. The structured
question is retained in [TASK.json](TASK.json).

## Credit and license

The construction, attaining family and original theorem are thu-nmrc's work
with substantial OpenAI Codex assistance. Ali Romman's normal-form/closure
work, Cinna Davis's query/controller lineage and all retained contributors
keep their original credit. Exact source notice and Apache-2.0 license are
preserved in `inputs/`; no predecessor file is modified.

Independent audit, symbolic checker and failure controls prepared for
**ferdy252 with substantial OpenAI Codex assistance**, including separate AI
written derivation, adversarial proof review and static checker review.
New work is Apache-2.0. No world-priority or maintainer-admission claim.
