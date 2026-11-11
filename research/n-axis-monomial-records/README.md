# An n-axis monomial elimination uses at most (3n^2+9n+2)/2 records

**Proof, with an exhaustive census for n <= 4. No new κ.** The selected
conditional value stays `363005817/100000000000`.

## Result

Fix the monomial normal form used for nine axes in the `#4610`
specialization, and let the axis count be any positive integer `n`.
Eliminate the invertible binary address matrix by the pivot rule below,
replace each row swap by three `F_2` row additions, and emit one record
for each translation bit, each unit of a mod-4 linear phase, each
off-diagonal controlled sign, and each global factor of `i`.

**Theorem.** This synthesis emits at most

```text
R(n) = (3n^2 + 9n + 2)/2
```

elementary records, and there is a monomial for which it emits exactly
`R(n)`. The argument is in [PROOF.md](PROOF.md).

The column charge is the new step. On column `k`, if `a_k` is the number
of eliminations and `s_k` is 1 when a swap occurs, then `a_k + s_k <= n-1`.
Summing and replacing each swap by three additions gives the address
length `(n+2)(n-1)`. Charging at most `n(n-1)` additions and `n-1` swaps
separately gives the longer address length `(n+3)(n-1)`.

At `n = 9` the separate-maxima count is the published

```text
96 + 9 + 27 + 36 + 3 = 171,
```

while `R(9) = 163`. The value 171 remains a correct sufficient count. It
does not use the column charge. The operation list in section 6 of the
`#7000` application review sums to `R(n) + n + 2`, which is 174 at
`n = 9`, and the review then uses `4(n+1)^2`. At `n = 153` that square is
`94864` and `R(153) = 35803`. With the review's own map count `311304`,
the square product `29531542656` is below `2^35`, and the sharp product
`11145617112` is below `2^34`. The review's comparison `< 2^40` remains
true. None of these integers changes the admitted κ.

Assumption `precision_tape` is the interface being bounded: the record
list is the fixed finite template that the retained tape tariff multiplies.
The assumption is not discharged. The caller is this elimination, which is
the grammar specialized at `n = 9` and invoked for general `n` by that
application review. `frontier7000-verify` was not run.

## Evidence classes

The column charge, the closed form, the witness family, and the comparison
with 171 and with `4(n+1)^2` are a proof for every positive integer `n`.
The witness check through `n = 64` in the verifier is finite corroboration
of that one family, not the proof.

Separately, for every matrix in `M_n(F_2)` with `n <= 4`, the algorithm
accepts a matrix if and only if it lies in `GL(n, F_2)`, never swaps the
last column, obeys the column charge, attains `n(n-1)` additions on some
matrix, attains `n-1` swaps on some matrix, and attains the address bound
on exactly one matrix. That statement is an exhaustive finite census.
Its domain is finite, the enumeration runs through every bit mask, and the
acceptance count is checked against the product formula for `|GL(n, F_2)|`.
It is not a proof for `n > 4`. A failed search is not used anywhere in
this package.

`R(n)` is exact for this synthesis. It is not proved to be a lower bound
on every other recipe built from the same primitives.

## Scope and evidence

Catalogue card `formal-interface-lemma`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**.
The card asks for a formalized interface lemma. This package does not
start a proof-assistant development. It answers the all-size request for
one assumption id, one caller, and one proved proposition: the record
count above, under `precision_tape`.

Ordered eligible list for this session, after dropping every unpaidmoon
pull request and fork `cursor/*` branch named in the session brief. The
revision-8 next-decision table comes first. Catalogue cards that the table
does not name by id follow, in catalogue order.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. BIT helper contract (`bit-helper-contract`).
3. New decoders and interfaces.
4. Supplier audit.
5. All-size audit and formalization.
6. Verification tooling.
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

Item 5 is this package. It is not a register-model, paired-star, G20, or
conditional-κ continuation. The original card is copied in
[TASK.json](TASK.json). Pins are in [SOURCES.json](SOURCES.json).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/n-axis-monomial-records/verify.py
python3 -O -B research/n-axis-monomial-records/verify.py
python3 -B scripts/research_package.py --package research/n-axis-monomial-records --check-only
python3 -B scripts/research_package.py --package research/n-axis-monomial-records
```

The verifier prints `PASS_N_AXIS_MONOMIAL_RECORDS`. Checks raise
`SystemExit`, so optimized mode does not drop them. Not run: Lean, Docker,
a physical caller, and `make frontier7000-verify`.
`scripts/research_selected_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` and is not a scientific replay.

## Open next questions

- Is `R(n)` a lower bound on every selected-primitive recipe of some
  monomial, or only the exact length of this elimination? The tariff uses
  a sufficient count. A matching lower bound would show that this alphabet
  cannot price that monomial more cheaply. The first step is the `n = 2`
  witness, whose sharp recipe has 16 records. The selected rewrite system
  is not a finite search here.
- Does replacing the review's per-map `94864` by `R(153) = 35803` lower a
  cutoff integer in section 6 without changing the admitted κ? The review
  already says those finite constants leave the rank and exponent
  inequalities unchanged. No isolated cutoff checker is included, and the
  full admission replay was not run.

## Credit

The nine-axis normal form and the count 171 are Cao Yifan / intqwq,
PR `#4610`, as recorded in
`research/final4610-independent-admission/SPECIALIZATION.md`. The loose
general list and the map count `311304` are the `#7000` application
review, section 6. The package scaffold is Douglas Colkitt's. Prepared by
unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. No independent human or formal-kernel review is claimed.
