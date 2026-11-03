# Exact full-guard law for k corank-one requests with orthogonal kernels

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped counting proof with finite corroboration.** Let
U_1, ..., U_k be pairwise orthogonal rank-one idempotents on F_q^m, and
P_t = I - U_t. A complete header G passes a request when all leading
principal minors of G P_t G^-1 through its rank are nonzero. All k requests
use the same G. This answers open question 2 of
[#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261), which
proves the case k = 2.

[PROOF.md](PROOF.md) proves:

1. **Transfer law, every finite field.** The joint fraction is
   C(q,m,k)/D(q,m,k), computed by a walk on k by k partial Gram matrices with
   diagonal entries different from 1, with
   D = q^(k(m-k)) prod_(i<k)(q^m - q^i).
2. **Binary character law, every k.** With n = m - 1,
   C(2,m,k) = 2^(-k(k-1)) sum_c (-1)^|c| Z(c)^n, where c ranges over
   zero-diagonal binary matrices and Z(c) is a three-state sum over
   {0,1,2}^k.
3. **Binary threshold, every k >= 2.** A common passing header exists over
   F_2 exactly when m >= k + 1. The proof is a rank and idempotence argument
   on J - I.
4. **Three requests over F_2.**

   ```text
   C(2,m,3) = (27^n - 6*21^n + 6*19^n - 6*17^n + 16*15^n - 18*13^n
               + 9*11^n - 2*9^n) / 64,
   Pr(all three pass) = C(2,m,3) / ((2^m-1)(2^m-2)(2^m-4) 2^(3m-9)).
   ```

   At m = 4 this is 1/1680, against (9/40)^3 for independent marginals. The
   three passing events are strictly negatively correlated for every m >= 2.

Over F_3 the threshold differs: 480 of 11,232 headers (5/117) pass three
requests at m = 3.

## Reproduction and evidence

From the repository root, with any CPython 3.12 replacing this local path:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corankone-triple-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/corankone-triple-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-triple-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-triple-header-law --check-source-history
```

The scientific marker is `PASS_CORANKONE_TRIPLE_HEADER_LAW`. Its generated
JSON holds every transfer count, the binary spectra, the census counts and
SHA-256 hashes of every package file. Nothing is written to disk and no
receipt is stored. Each verifier run takes about 20 seconds locally.

The finite corroboration:

- **Literal census of 31,614 complete GL headers**: F_2 at m = 2, 3, 4 and
  F_3 at m = 2, 3, with k up to min(m, 4). Each header is inverted, each
  conjugated request is formed as a full matrix, and no-pivot elimination
  checks its guards. Every joint count equals the transfer count times
  |GL_(m-k)|. At F_2, m = 4 the k = 3 count is 12 headers.
- **Transfer counts**: F_2 for k = 1..4 (m up to 40, 40, 30, 12) and F_3
  for k = 1..3 (m up to 10, 8, 5). The rank-one weights are enumerated from
  all (y, x) pairs, not taken from the formula.
- **Character law**: the binary spectra for k <= 4 are computed from Z(c)
  over all characters and match the transfer at every listed m. The k = 3
  closed form matches for m <= 30.
- **Threshold**: zero counts for m <= k and positive counts for m > k,
  k = 2, 3, 4. At m = k + 1 the counts are 2, 12, 48.
- **Correlation**: the k = 3 joint fraction is checked exactly against the
  cube of the marginal for 4 <= m <= 400; PROOF.md covers larger m.
- **Boundaries**: k = 1 reproduces #4227's marginal (3^n over F_2,
  2*7^n over F_3); binary k = 2 reproduces #4261's closed form for m <= 40;
  F_3 at k = m = 2 reproduces #4239's 1/6.
- **Controls**: omitting the zero-step multiplicity, assuming independence,
  dropping the negative characters, and admitting on first guards only
  (4,536 versus 12 headers at F_2, m = 4, k = 3) each change a checked value.

## Scope and remaining obligations

The transfer theorem covers every finite field; the replay implements F_2
and F_3 only. The closed form is for k = 3 over F_2. The count 2 k! at the
threshold is observed for k = 3, 4 and is not proved. Fixed idempotents with
pairwise orthogonal rank-one kernels and a complete, equally weighted GL
header domain are assumed. No density is asserted for restricted header
subsets.

No request producer, header selection or emission, dispatch, dirty return,
stock, precision or physical invoice is supplied. Those costs remain
unknown, not zero. No new kappa, selected-frontier change, supplier
admission or complete multiplication theorem is claimed. Independent human
and formal proof-kernel review are unclaimed. Selected cold replay, Lean and
Docker were not run.

The verifier is standard-library Python with bounded loops and no
recursion. The largest transfer has 5,832 states (F_3, k = 3). CPython
allocates integers and tuples dynamically; the declared finite domains
bound that allocation.

## Related work and credit

- [#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261) proves
  the k = 2 transfer and binary law; this package generalizes its partial
  Gram argument. Its binary closed form agrees numerically for m <= 40.
- [#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227)
  supplies the corank-one determinant identity and marginal law, used as a
  cited step and checked numerically at k = 1.
- [#4239](https://github.com/CrocSwap/integer-mult-bounds/pull/4239) gives
  the orthogonal rank-one law; its q = 3, m = 2 value 1/6 agrees.
- [#4246](https://github.com/CrocSwap/integer-mult-bounds/pull/4246) and
  [#4259](https://github.com/CrocSwap/integer-mult-bounds/pull/4259) cover
  orthogonal and laminar families. The requests here are neither when
  m > 2 and k >= 2.

These preceding counting packages were produced by Nick Petalas. Cinna
Davis supplied the #4100 BIT.md request context; the retained normalizer
lineage is due to source527, commdata2338 and Jose Manuel. No unmerged
predecessor code is imported.

## Open next questions

1. Is the binary count at the threshold m = k + 1 equal to 2 k! for every
   k >= 3, so that only the row and column rectangle decompositions of
   J - I occur? Checked for k = 3, 4; k = 5 needs a vectorized walk.
2. Is the binary joint fraction strictly below the product of marginals for
   every k >= 4? The single-entry characters give the second eigenvalue
   7*3^(k-2) with sign -1 and multiplicity k(k-1); the rest of the negative
   spectrum is not bounded here.
3. Can the odd-q transfer be reduced, for example by the symmetric group
   acting on the k requests, to a closed form?
4. Does an actual producer admit a fully charged shared-header caller for
   such a family? A joint density is not a physical saving.
