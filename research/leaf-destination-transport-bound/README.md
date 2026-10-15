# Leaf-destination transport: the exact maximum is max(1, floor(log2 n))

**A scoped written proof, checked by its author with exact computation. It has not been
independently reviewed. It makes no kappa, precision-invoice or rounding claim.**

## Theorem

In PR628's balanced reserved-depth dirty word with n free, noncommuting, contractive factors
(both orientations), a unit error injected at the destination of a completed leaf has, at any
later cut and in any register, free-algebra mass at most max(1, floor(log2 n)), and this value
is attained for every n:

  **E(n) = max(1, floor(log2 n)) for all n >= 1.**

The proof is in [`PROOF.md`](PROOF.md): Lemmas S, L2, L1 (prefix and exit monomiality), Lemma I
(the sign − call is the leaf-by-leaf inverse), Lemma X (an exit column has at most
floor(log2 k) + 1 nonzero registers) and Lemma P (an explicit readout) give the upper bound by a
case table over the lowest common call and an explicit attaining family.

This answers two open questions recorded on main:
- `research/leaf-destination-transport`: "Does `max(1,floor(log2 n))` hold for every n?" Yes.
- PR1416 `research/single-register-interval-transport`: "Determine the exact maximum between
  h−1 and h+2." For destination-supported single errors it is floor(log2 n): h for powers of two,
  h−1 otherwise (h = ceil(log2 n)).

## Scope

One unit error at a completed-leaf destination; every later cut and register; both
orientations; all n. Not covered: internal leaf intermediates, multiple or accumulated errors,
arbitrary joint errors, rounding, aliasing, a precision invoice and kappa. Card
`uniform-transfer-audit`, scope `refined` (see `TASK.json` and the session record
`TASK-CARD.md`).

## Checks

```sh
python3 scripts/research_package.py --package research/leaf-destination-transport-bound --check-only
python3.12 scripts/research_package.py --package research/leaf-destination-transport-bound
```

The registered `verify.py` (standard library, about 20 s) prints
`PASS_LEAF_DESTINATION_EXACT_MAXIMUM`. It checks that the word generators equal PR628's literal
`compose` for n <= 40, runs `check2.py` (Lemmas I, L1, X, P, the case table and E(n)) for
n = 1..40 and the family for n <= 128, `fam_closed.py` for n = 2..200, `lemmas.py` for n <= 32 and
the independent `census.py` for n <= 24, and requires two mutation controls (unreversed inverse,
ceil-half split) to fail.

| Script | Purpose |
|---|---|
| `check2.py MODE LO HI [famHI]` | All lemma, case-table, E(n) and family checks; modes `ok`, `unrev`, `swap`, `drop` |
| `fam_closed.py LO HI` | Family row equals the closed form of Theorem 2; Lemma P formula |
| `lemmas.py N` | Lemmas L1, L2, S for n <= N, both signs |
| `census.py N...` | Independent envelope census (E(n) = floor(log2 n) for n = 1..128 in author runs) |
| `controls.py` | Lemma mutation controls (unreversed inverse, dropped restoration) |
| `chainform.py`, `lcabound.py`, `lcacase.py`, `patterns.py` | Second census method; Lemma S necessity; per-case LCA values |

Longer author runs are in `logs/` (`check2.py ok` for n = 1..80, family and closed form to
n = 512, census n = 71..128, controls).

## Follow-up: attainment in every case, and multiple errors (`PROOF3.md`)

**Attainment in every source-dirty case.** Lemma P only applies when the readout phase has sign +. The remaining cases are (U,V′)+, (U′,V′)+ and (U,V′)−. For these, the readout is the scratch register z_{V′} instead of y.
- Lemma E gives the exit column along the y-keeping chain.
- Lemma Q gives the z_{V′} row inside a sign − call.
- Together they produce H = floor(log2 n) distinct monomials, so all four source-dirty cases are now proved.
- `fam3.py LO HI` checks this exactly for n ≤ 128; the logs are in `logs/`.

**k destination errors** (PR2067's model, one symbol per error):
- Proved: E_k ≤ k·max(1, floor(log2 n)).
- Proved: E_2 = 2·max(1, floor(log2 n)).
- Proved, sharper: only 2F(⌊n/2⌋) channels can reach the maximum, which gives E_k ≤ k·fl(n) − max(0, k − 2F).
- Exact census (`multi3.py`) for n ≤ 40: these bounds are attained. Interior cuts far exceed PR2067's endpoint counts; at n = 64 the all-errors total is 6173.
- Conjectured, not proved: the extremal cut and the all-errors total (11·4^h − 11·3^h + 1)/6 for n = 2^h.
- The ceil-half-split control fails.

`verify.py` runs `fam3` for n ≤ 64, `multi3` for n ≤ 16, and the swap control.

## Open next questions

Structured versions are in `TASK.json`.
- **Multiple or accumulated errors.** What is the exact transport of one error per leaf (or per
  phase)? Lemma L1's one-term argument fails for superposed injections; open PR2067 covers
  endpoint accumulation only.
- **Census-only cases of the lower bound.** The maximum is attained in all four source-dirty LCA
  cases for m <= 80, but only (U,V) with sign + is proved; Lemma P fails for sign −.

## Credit and AI assistance

Builds on woklerx (`leaf-destination-transport`), cbethin (PR1416), Arham Tahir (PR1374),
Hanson Sun (PR1085 prefix invariant) and Chafik Boukhalfa (PR628 `compose`). Prepared by
Philippe Van Velzen with substantial Claude (Anthropic) assistance: Claude sub-agents wrote the
proof, the census and the checking scripts; the main session re-ran the checks and controls.
No independent human review and no formal proof. Apache-2.0.
