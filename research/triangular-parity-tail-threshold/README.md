# The sharp tail threshold for forward parity prefixes

For every fixed real `eta > 1`, the exact triangular Toeplitz parity compiler
has a family whose completed map has infinity norm `1+eta`, but whose first
proper macro-prefix has norm

```text
((eta+1)/2)^(N/2-1),       N = 4,8,16,... .
```

This is a **scoped algebraic proof with finite controls**. It rules out even a
polynomial-in-`N` forward-prefix bound based only on a fixed coefficient-tail
budget greater than one. Together with Brian's
[#4737](https://github.com/CrocSwap/integer-mult-bounds/pull/4737) theorem for
`eta <= 1`, it identifies one as the exact threshold for a dimension-independent
forward macro-prefix bound over the complete tail-budget class. The new part is
the exponential family for every `eta > 1`; the complementary theorem is cited,
not re-proved or replayed.

## Proposition and proof

Use the exact parity recursion in
[`SHALLOW-TOEPLITZ.md`, section 3](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md).
A macro is a completed Toeplitz shear. At every node the right shear runs first,
the two children run next, and the left shear runs last. The proof only needs
the root right shear, so it applies to every legal child interleaving.

Fix `eta > 1` and put

```text
a = (eta+1)/2 > 1,       b = (eta-1)/2 = a-1 > 0,
f(z) = 1 + b z + a z^2,  N = 2m >= 4.
```

Let `T_N(f)` denote multiplication by `f` modulo `z^N` in coefficient order.
Its tail coefficient l1 norm is `a+b=eta`. Every row has absolute sum at most
`1+a+b`, and every row with index at least two attains it. Thus

```text
||T_N(f)||_infinity = 1+eta = 2a,
```

independently of `N`. In even/odd order the root split has

```text
e(z) = 1+a z,       o(z) = b,
k(z) = o(z)/e(z) = b sum_(j=0)^(m-1) (-a)^j z^j mod z^m,
U = [ I T_m(z k) ; 0 I ].
```

All inverses here are finite triangular inverses, since `e(0)=1`. No analytic
convergence is assumed. The first macro-prefix is exactly `U`. Its upper block
row with within-block index `i` has absolute row sum

```text
1 + b sum_(j=0)^(i-1) a^j = a^i,       0 <= i < m.
```

For `i=0` the sum is empty. The largest row is `i=m-1`, so

```text
||U||_infinity = a^(m-1) = ((eta+1)/2)^(N/2-1).
```

The shear is a proper prefix because it precedes the children and the nonzero
root left shear. Coordinate permutation preserves this norm. Also
`U^(-1)=[I -T_m(zk);0 I]`, so the same exact norm holds for its inverse.
The norm is attained on a unit infinity-norm input: choose each input coordinate
to have the sign of its coefficient in the largest row, and zero when that
coefficient vanishes. Thus the growth is an actual amplification of bounded
data, not merely a loose product estimate.

For fixed `a>1`, the logarithm of the displayed norm is `(N/2-1) log(a)`.
It grows linearly in `N`, whereas the logarithm of any fixed polynomial grows
as `O(log N)`. Therefore no dimension-independent bound, or polynomial bound
with constants depending only on `eta`, can cover every symbol in this class.
This conclusion already holds with three nonzero coefficients and nonnegative
input-symbol coefficients. The proof is valid for every real `eta>1`; the
finite checker uses rational instances only.

For example, `eta=3` gives `f=1+z+2z^2`. At `N=16` the first prefix has norm
`128`, while the completed map has norm `4`. These are exact values checked
by the verifier.

## What this changes and what it does not establish

The completed map's bounded forward norm alone cannot justify increasing the
parity compiler's permitted tail budget beyond one. Any such extension needs
an additional restriction or a changed factorization. Brian's #4737 gives a
single `eta=2` violation of the `1+eta` cap; this result strengthens that domain
observation to exponential growth for every fixed superunit budget.

The retained triangular caller in `SHALLOW-TOEPLITZ.md` assumes `eta<1`.
Nothing here contradicts that theorem or changes the selected frontier.
This family is not asserted to have uniformly bounded inverse endpoint norm.
The obstruction is specific to the exact parity factorization and its macro
boundaries. It does not exclude other compilers, settle internal FFT or shear
gate accounting, provide a physical supplier, or prove a complete integer
multiplication theorem. No new kappa is claimed. Formal proof-kernel and
independent human review are unclaimed.

The original `uniform-transfer-audit` card changes to this algebraic domain
side result. The original card, scope reason and remaining obligations are in
[TASK.json](TASK.json). The current selected source-binding orientation passed
with `scripts/research_selected_baseline.py`; the card's older balanced-schema
control is historical. No predecessor executable was replayed.

## Reproduction and finite evidence

Run from the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/triangular-parity-tail-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/triangular-parity-tail-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/triangular-parity-tail-threshold/verify.py
```

Expected marker:

```text
PASS_PARITY_TAIL_THRESHOLD fixtures=25 controls=7 max_n=64 no_new_kappa
```

The 25 fixtures are the full Cartesian product of tail budgets
`17/16, 5/4, 3/2, 2, 3` and dimensions `4,8,16,32,64`. For every fixture the
checker independently divides the finite series, applies the root right,
diagonal and left factors to every input column, and compares the complete
product with the literal Toeplitz endpoint. It checks both inverse orders for
the first shear, its exact norm, an attaining signed input, the endpoint norm,
and the dyadic growth identity `p_(2N)=a p_N^2` on every adjacent size pair.
Seven controls cover the tail boundary, the finite upper tail limit,
non-dyadic size, size exhaustion, nonunit division, a missing shift and the
wrong Schur sign. These are controls of the new family, not rechecks of a
predecessor's claimed counts.

Each run prints a generated JSON receipt containing these results and SHA256
hashes of all five package files. No receipt is hand-authored or committed.
The all-size claim rests on the preceding proof, not these finite samples.
Lean, Docker, internal-gate compilation and the selected full operator replay
are outside scope and unrun.

The checker has no imports from predecessor code, network calls, subprocesses
or writes. Source documents are pinned as historical provenance in
[SOURCES.json](SOURCES.json). Its loops have fixed finite bounds, with matrices
of at most `64 x 64` and 25 fixed rational fixtures. Functions are under 60
lines, and explicit contracts remain active under optimization. Python's
managed allocation and arbitrary-precision arithmetic are a Power of Ten
deviation: live dimensions and coefficient inputs are bounded by this fixed
grid. The rejection helper's indirect calls have five explicit local targets.
Warning-strict normal and optimized execution are the available diagnostics.
No standalone linter or type checker is installed in this environment.

## Open next questions

- Can a changed factorization retain polynomial forward-prefix norms on a
  class with tail budget above one and a separately bounded inverse endpoint?
  This would distinguish a compiler limitation from unavoidable conditioning.
  Start with a concrete zero-free symbol whose even part has an interior zero,
  then price the replacement factorization. Such a class and its inverse bound
  have not been constructed here.
- Can a caller normalize a superunit-tail triangular symbol into near-identity
  factors without repaying the gain through coefficient generation, storage
  or additional shears? Start with one caller's literal symbol and complete
  invoice. Caller-specific spectra and implementation costs remain unknown.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.

Brian's #4737 supplies the complementary forward theorem and the prior
`eta=2` example; #4731 supplies the common four-cut envelope. James Reed's
#4699 and subsequent finite parity-prefix packages supply the one-level
budget and individual examples. The parity compiler is retained from Vlado
Vojdanovski's #1673 and Cinna Davis's #4100 caller. Credit also Ryanson Jonathan
and unpaidmoon #4371 for the preceding conditioning question. The new
contribution is the sparse exponential family and the universal superunit-tail
obstruction. All predecessor files and credit lines are unchanged.
