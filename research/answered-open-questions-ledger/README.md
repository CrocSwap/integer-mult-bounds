# Open next questions that merged packages already answer: a ten-row ledger

**Navigation record. No new mathematical claim and no κ.** Ten open questions
stored in merged research packages are tied to the later merged package whose
README answers them (5 rows), answers them by scope inclusion (2 rows) or
answers only part of them (3 rows). Each row gives the question exactly as
stored in the asking package's `TASK.json`, the answering package, and one to
four quoted README lines. All inputs are pinned to main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The asking packages are frozen, so
the missing cross-references live here instead of in their files.

| Row | Question stored in | Answered in | Status |
|---|---|---|---|
| L01 | `length9-four-vertex-gap`: arc {0,1,2,3,4}, common far-rim root? | `length9-five-vertex-gap` | answered |
| L02 | `length9-five-vertex-gap`: arc {0,1,2,3,4,5}, common far-rim root? | `length9-six-vertex-gap` | answered |
| L03 | `length9-six-vertex-gap`: arc {0,1,2,3,4,5,6}, common survivor root? | `length9-seven-vertex-gap` | answered |
| L04 | `gaussian-neumann-ten`: smallest integer c with U < c p^2 | `gaussian-neumann-nine` | answered |
| L05 | `precision-blind-composite-rigidity`: even lengths | `weighted-reversal-rescaling` | answered |
| L06 | `paired-plane-rematch-rank34`: minimum fitting rank over all matchings | `paired-plane-frame-packing`, `p112-frame-partition`, `paired-plane-frame-repair` | partial |
| L07 | `triangular-parity-n8`: every n=8 symbol, prefixes at most 3/2 | `triangular-parity-forward-bound` | answered by scope inclusion |
| L08 | `triangular-parity-prefix`: nested splits inside the product of one-level caps | `triangular-parity-forward-bound` | answered by scope inclusion |
| L09 | `diagonal-pair-five-call-collisions`: six-call floor in odd characteristic or F4 | `diagonal-pair-collision-audit` | partial |
| L10 | `connector-gray-growth`: sharp leading constant of N(c)/(c log2 c) | `connector-bounded-depth-cap` | partial |

[ledger.json](ledger.json) holds the rows. Each row has a `note` that says in
one or two sentences what the answering README settles and what it does not.

## Statuses

- `answered` means the answering README states a result for the object the
  question names, in its title or first sentences.
- `answered-by-scope-inclusion` means the answering README proves a quantified
  statement whose scope includes the asked case, without saying it answers that
  question. The inclusion is my reading. The `note` names the definitional step
  it relies on: L07 and L08 read the asking package's proper prefixes as the
  answering package's forward macro-prefixes, by inspecting the two definitions,
  and that step is not proved here.
- `partial` means part of the question, or only its stated first step, is
  settled. L06: the stated first step (is 12 the maximum number of disjoint
  orthonormal 8-frames?) is answered, but the cited READMEs give a matching with
  fitting rank 32 and say they do not claim the optimum over all matchings.
  L09: odd characteristic is addressed only for F3 at width two, and the
  answering README labels its length-five row local SAT evidence. L10: the
  leading constant is fixed at 1/2 only for concatenations of blocks of depth at
  most two, and the general constant stays open in [1/2, 1].

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/answered-open-questions-ledger/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/answered-open-questions-ledger/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/answered-open-questions-ledger
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/answered-open-questions-ledger --check-source-history
```

Any CPython 3.12 installation can replace the displayed interpreter path. Both
direct runs print one line that begins
`PASS_ANSWERED_OPEN_QUESTIONS_LEDGER rows=10 answered=5 scope_inclusion=2 partial=3`
and takes about 0.03 s. The check authenticates the SHA256 of 30 pinned inputs
(19 `TASK.json`, 11 `README.md`), requires each stored question to equal its
`TASK.json` entry and to be unique there, requires each quote to lie inside one
README line, requires that no answering README cites the asking package by a
`research/<name>` or `../<name>` path (that absence is what makes the
cross-reference missing), and rejects eleven mutated copies of a real row:
changed question text, a moved index, a quote absent from the README, a quote
spanning a newline, a quote that is too short, a package answering itself, an
unpinned answering package, an unknown status, an empty answer list, a quote
borrowed from another row, and an answering README that cites the asking
package by path. Checks raise explicit exceptions, so `-O` does not disable
them.

## What this does and does not establish

- It establishes that the quoted lines exist in the pinned READMEs and that the
  stored questions match the pinned `TASK.json` files.
- It does **not** re-verify any answering result, and it does not decide by
  program that a quote answers a question. That reading is mine and is recorded
  in each row's status and note.
- The ten rows are chains I met while looking for an open question to take. They
  are not a census, and they support no statement about how many other stored
  questions are already answered.
- In all ten rows, no answering README cites the asking package by a
  `research/<name>` or `../<name>` path; the verifier enforces this on the
  pinned READMEs. It does not look at the answering packages' other files, so
  a citation there is not excluded. A path-citation index built from READMEs
  would therefore not link these pairs.
- In the length-9 chain, the five-vertex package's stop rule says not to start
  the six-vertex arc, and its stored question points at that arc. Rows L01 to
  L03 record where each next step was taken. I did not check whether the other
  asking packages were meant to stop at their stated question.

## Scope

`scope-navigation` card, scope refined: the card asks for one navigation repair
or one related family index, and this ledger spans seven small question chains.
No frozen package is edited. The card's first working command,
`python3 -B scripts/research_selected_baseline.py`, printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` at the base commit; that command checks
source bindings only and is not a scientific replay.

## Open next questions

The structured list with relevance, first step and blocker is in
[TASK.json](TASK.json).

1. Which other merged packages store an open question that a later merged
   package already answers? First step: for packages whose questions no other
   package cites by path, search later PR titles and README first lines for the
   named objects, and add a row only when the answering README states the result
   in its own words. An automatic match is only a lead.
2. L06: what is the minimum exact fitting rank over all perfect matchings of the
   P112 plane ports? The cited READMEs give a rank-32 matching and a floor of 30
   that is stated only for the two-support even-group colouring construction.
3. L09: does the six-call diagonal-pair floor hold over F4, over F5 and at
   widths above two? The cited audit settles F3 at width two only.
4. L10: is the general leading constant of N(c)/(c log2 c) above 1/2? Check live
   PRs and discussions for a depth-three block construction before choosing it.

Questions 2 to 4 are pointers to questions other contributors stored. They are
not claimed here.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.

Every row depends on predecessor work that is cited, not re-verified:
jwr (James Reed) for `length9-four-vertex-gap`, `length9-five-vertex-gap`,
`length9-six-vertex-gap`, `length9-seven-vertex-gap`, `gaussian-neumann-ten`,
`gaussian-neumann-nine`, `triangular-parity-n8` and `triangular-parity-prefix`;
Wentao Li for `precision-blind-composite-rigidity`; Matarener (Mark) for
`paired-plane-rematch-rank34`; Tekalign (tekuuu) for `paired-plane-frame-repair`;
Brian (JoyboyBrian) for `triangular-parity-forward-bound`; JoyboyBrian for
`diagonal-pair-five-call-collisions`; Josie Elliston for
`diagonal-pair-collision-audit` and `connector-bounded-depth-cap`; apoursh for
`connector-gray-growth`; and Nick Petalas for `weighted-reversal-rescaling`,
`paired-plane-frame-packing` and `p112-frame-partition`. Each package's
`README.md` and `TASK.json` retain its own credit line.
