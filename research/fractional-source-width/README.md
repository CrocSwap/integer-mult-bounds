# A fractional-moment bound for selected nested widths

This package was produced by Nick Petalas. Apache-2.0.

**Scoped mathematical proof, with exact finite corroboration.** For the unchanged
selected #4470 invoice, product power 1024, completion floor and paid split rule,
the #4436 nested compiler satisfies `K/N < 3.0694`.

This improves JoyboyBrian's [#5067](https://github.com/CrocSwap/integer-mult-bounds/pull/5067)
bound `K/N < 3.070`. More precisely, its uniform source logarithm bound
`197115103572543` decreases to `197100824008381`, a reduction of
`14279564162`. The new step is a fractional source-rank moment, including
completion and splitting. The selected kappa remains `60403/20000000`.
This is a mathematical width bound under the retained compiler assumptions;
physical stock, routing, native realization and supplier admission remain open.

## Premise and new uniform inequality

Use the source-labelled root/nonroot census and strict source-rank interval
proved in #5067 as cited premises. They are not independently audited here.
Write `M` for ambient rank, `L>=2` for the completed productive floor,
`x=n/M`, and `G=max{g:M L^g<=n}`. Let `T_k` and `P_r` be the fully completed
and split productive and paid inventories. The cited census includes every
nonroot absent-parent demand, with distinct chronological labels, and each
source rank `s` obeys `x<s<=n`.

For any real `p>0`, define `T_p=sum T_k k^p` and `P_p=sum P_r r^p`.
Each source contributes `1<(s/x)^p`. Sum this weight over the cited exact
census, then enlarge the eligible sets to full ordered words. Multiplicativity
of `(ab)^p` gives root weight `T_p^(G+1)` and depth-d weight
`P_p^d T_p^(G-d+1)`. Thus the new inequality is

```text
S_n < x^(-p) T_p sum_(d=0..G) P_p^d T_p^(G-d).       (1)
```

If a common `U` bounds both `T_p` and `P_p`, then

```text
S_n < (G+1) U^(G+1)/x^p
    <= (G+1) U (U/L^p)^G.                           (2)
```

This does not assume `P_p<=T_p`. Rank-mass ordering at p=1 alone does not
imply that ordering at a fractional p.

## Charging the actual completion and splitting

Let `t_p=sum T0_k k^p` and `q_p=sum P0_r r^p` be moments of the pinned raw
invoice, `W0=sum T0_k`, and `q_1=sum P0_r r`. The chronological product power
is `v=1024`, the completion floor is `L=21^v`, and split cutoff is `J=20^v`.
The product has `W0^v` productive slots. Completion adds at most `L` to
each slot on disjoint coordinates, so

```text
T_p <= t_p^v + W0^v L^p.
```

For a paid rank `a`, write `a=bJ+c`, `0<=c<J`. Its actual split p-moment is
`b J^p+c^p`, with the zero remainder omitted. Since
`b J^p <= a J^(p-1)` and `c^p<=a^p`, it is at most
`a J^(p-1)+a^p`. Applying this to every raw product call and every completion
call gives

```text
P_p <= q_p^v + q_1^v J^(p-1)
       + W0^v (L^p + L J^(p-1)).                  (3)
```

Every term in (3) is retained. Small unsplit calls enter `q_p^v`; rank mass
alone cannot bound a concave split moment. The proof permits arbitrary
completion deficits within the actual floor, without materializing their
histogram or declaring their costs zero.

Choose `p=511/512`. Then `L^p=21^1022` and `J^(p-1)=1/400` exactly.
The verifier encloses each raw rank power on a dyadic grid of mesh `2^-24`.
For the upper numerator `b_k`, it checks the integer inequality

```text
(b_k-1)^512 <= k^511 * 2^(24*512) <= b_k^512.
```

It sums the upper rational endpoints with the literal raw multiplicities,
raises them to power 1024, and compares the complete bounds above with
`U=2^18291`. Both are strictly smaller than U. No floating-point evaluation,
external numerical library or predecessor executable supplies these comparisons.

## Accumulating the width

Use the unchanged selected `H=64215200000000`, `N=2^H`, `M=145^1024` and
`B_n=B_(n-1) S_n`, with base width one. Exact integer bit lengths give

```text
G(n) <= h = 14279564152       for M<=n<=N,
floor(log2 L^p) = 4488,
U/L^p > 1.
```

Taking logarithms in (2) and bounding by integer bit lengths yields

```text
log2 S_n < bit_length(h+1) + 18291 + h*(18291-4488)
         = X = 197100824008381.
```

Therefore `log2 B_N<NX`. The integer `NX` bounds `ceil(log2 B_N)`, so
`K/N<=X/H`. The exact integer comparison `10000 X < 30694 H` proves the
stated `3.0694` bound. This argument uses a uniform envelope; it assumes no
monotonicity of the exact source count. The permitted nested widths and
complements remain as in the cited compiler, with no changed physical tariff.

## Reproduction and evidence

From the repository root, CPython 3.12 and standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/fractional-source-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/fractional-source-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fractional-source-width
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fractional-source-width --check-source-history
```

Any CPython 3.12 installation can replace that interpreter path. Expected
marker: `PASS_FRACTIONAL_SOURCE_WIDTH K/N<3.0694 no_new_kappa`.
The verifier prints exact root intervals, the new integer X, finite fixture
counts and a generated SHA256 receipt for all package files. No receipt is
hand-written or committed. The 458 new tiny ordered-word fixtures corroborate (1)-(2)
at p=1/2, and 32 actual split-moment fixtures corroborate (3). Discriminating examples
show why omitting split mass, assuming paid/productive moment ordering or
rounding a rank power downward is unsafe. They do not rerun predecessor
source-count fixtures or certify its census independently. Checks use explicit
exceptions and remain enabled under `-O`.

The written proof establishes the uniform claim. Finite tests corroborate it.
Independent human and formal proof-kernel review are unclaimed. The selected
source-binding orientation passed and was metadata orientation only. No Lean,
Docker, selected operator replay or physical implementation was run. All
registered package checks ran locally; hosted CI is reported in the PR.

The verifier has no recursion, subprocesses or configurable search bounds.
Its fixed domains have rank at most 145 and at most 33 bisection steps per
rank; the toy paths have depth at most four. Functions have fewer than 60
lines. Python allocation during exact arithmetic is a managed-runtime
deviation from fixed allocation, bounded by these finite inventories and
fixed exponents. No library allocation audit is claimed. Warning-strict normal
and optimized execution provide the available diagnostics; repository-wide
static-analysis configuration is unchanged.

## Open next questions

1. Can a boundary-sensitive moment or a different fixed exponent tighten the
   mathematical width further? Start with (1) and preserve every term in (3).
   Optimal exponent and optimal width remain unknown. No optimization campaign
   is performed here because the first improvement meets the stop rule.
2. Can the permitted width be realized by the actual fixed-program
   stock/ownership/routing interface at its full tariff? Choose one caller
   before extending arithmetic bounds. Native/all-column, whole-job, precision,
   tape and analytic/recovery assumptions remain separate obligations.

## Credit and scope

Produced by Nick Petalas. This answers Open next question 1 of JoyboyBrian's
#5067 by extending its first-moment argument. Credit Sagar Thakrar #5026,
James Reed/jwr404 #4972/#4970, Mark/Matarener #4612, zxv #4436, Cinna Davis
and zxv #4440/#4470, Jacob Alan Sussman's Theorem 1G, Ryanson Jonathan and
mihir-s-05, together with the lineage retained in #5067. Predecessor credit
lines and files are unchanged. No claim of literature priority is made for
the elementary moment method or the splitting inequality.

The selected-stock-envelope card is changed to a scoped mathematical compiler
width result, following a concrete other-contributor handoff. This does not
discharge the card's physical stock question. SOURCES.json pins the census
statement and raw invoice at main `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`.
Live and merged overlap checks, recent account work and local reservations were
consulted before the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142685).
Unpublished work and arbitrary code diffs remain outside that coverage.
