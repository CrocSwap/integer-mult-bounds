# Admit fixed Gaussian-rational scalars in an all-column C-word runtime

The all-column C-word grammar in
[CrocSwap/integer-mult-bounds#7834](https://github.com/CrocSwap/integer-mult-bounds/pull/7834)
has dyadic scalar instructions. The selected complex construction and
[#7828's alternative compiler](https://github.com/CrocSwap/integer-mult-bounds/pull/7828)
also use fixed odd rational scalars. This package proves and checks a local
grammar/grid extension that removes that particular mismatch.

**No new kappa.** The selected bound remains conditional on all five
selected assumptions. The package neither materializes a funded word nor
admits an entire compiler, primitive service or multiplier.

## Exact result

Admit `SCALE(a,b,q)`, meaning multiplication of a complete row by
`(a+i b)/q`, for fixed integers `a,b` and positive integer `q`.
The coefficient acts once; a column phase still acts by `i^f` at
column multiplicity `f`. An exact matrix-key dictionary over Gaussian
rational coefficients decides the all-positive-column identity, by the
same finite Vandermonde argument as #7834. Absolute phases stay in keys.
Private registers start and finish zero and receive no productive credit.

For a fixed accepted word with base rank `N>=2`, productive width `W>=2`
and `J` instructions, define

```
D = lcm of all odd denominator parts,
d = floor(log_N h),
S = D^(Jd),
G = 8 (N + J(m+2) + 1) (h+1),
```

where `m>=2` strictly bounds every scalar numerator sum and denominator
by `2^m`. One root lift by `2^G S` makes every intermediate operation
exactly integral. Completed C children return dyadic endpoints relative
to their entrances; only unfinished scalar contexts contribute odd debt.
Addition takes the maximum denominator debt, not its sum.

For p-bit integer input components, reserve

```
p + 2G + Jd bitlength(D) + 4
```

signed bits, including full numerator temporaries. Retire the odd scale
and the surplus binary guard at the root, checking exact remainders.
The output is exactly `2^h C^(tensor h)` on the original input numerators.
No extra paid C instruction is introduced.

Under the retained complete-row scalar, placement, parking and disjoint-XOR
contracts, each new local scalar costs `O_word(V)` and root odd scaling
and retirement cost `O_word(V log(h+2))`, with linear backing. The width
is `O_word(p+h+log(h+1))`, hence `O_word(p)` in the source geometry.
The complete positive-power recurrence absorbs these bills. Genuine
productive row stock and zero padding remain charged source conditions.

Unary coefficient fields retain an effective `2^O(L) poly(L)` validation
bound at code length L. Their shared length budget gives
`D <= product q_i <= 3^(L/3)`. The implementation uses binary divisor
descriptors. This startup statement is conditional on a qualifying fixed
word existing; the test fixtures are deliberately unfunded.

## Evidence and implementation boundary

[PROOF.md](PROOF.md) supplies the universal invariants and full additional
bills. `word.py` implements exact semantic checking and a signed unary
codec. `execute.py` is a logical integer-grid model using Python arrays;
its indexed access is not presented as a tape implementation.

The primary checks compare with a dense closed tensor formula, including
three recursion depths, nonreal scalars, odd and even denominators,
nonzero private paid work, complete nonzero spectators, interleaved axes,
padding and retirement. Controls catch the scalar/column phase confusion,
missing odd lift or retirement, nonzero private endpoints, insufficient
row stock and malformed syntax. Funding alone is explicitly shown
insufficient for semantic correctness.

An independently written recursive Fraction reference and grid engine
are retained in `review/`. Their standalone derivation preceded the root
implementation; final-code review and additional adversarial controls are
recorded separately. All checks are exact. Finite executions corroborate
the induction; they do not prove the retained physical services.

## Reproduce

From the repository root:

```sh
python3 -I -B -W error research/rational-all-column-c-word/verify.py
python3 -I -B -W error research/rational-all-column-c-word/review/check_rational_grid.py
python3 -B scripts/research_package.py --package research/rational-all-column-c-word
```

The arithmetic checks are self-contained. The registered provenance check
also needs the two exact source histories. If they are absent, use these
bounded read-only fetches:

```sh
git fetch --depth=1 --filter=blob:none https://github.com/aliromman/integer-mult-bounds.git 4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02
git fetch --depth=1 --filter=blob:none https://github.com/aliromman/integer-mult-bounds.git 03b572b3b9ab72c6ba67762e85e1630cda1daad5
```

These pending source heads are dependencies, not asserted ancestors of
this branch. Source bytes and the exact canonical base are recorded in
SOURCES.json. Normal and optimized registered checks use Python 3.12
and the standard library.

## Open next questions

1. Bind a particular #7828 complex output word to the expanded grammar,
   including every adapter, phase, owner and paid count. A scalar-alphabet
   bridge does not establish that complete translation.
2. Implement the new fixed rational scans and root passes in a literal
   fixed-tape service at a named physical caller. Preserve both input limbs,
   all head returns, histories, private cleanup and source permissions.
3. Supply the complete disjoint-XOR and higher-controller contracts needed
   by an accelerated actual multiplier. The present grid argument cannot
   replace those movement and analytic premises.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Ali Romman for #7834's all-column dictionary, Vandermonde test,
startup and row recursion, and #7828's source compiler context; the
selected #7000 common-grid audit and all credited native/tape predecessors
remain effective. Common denominators and exact binary arithmetic are
classical. No human peer review or formal-kernel acceptance is claimed.
Apache-2.0.
