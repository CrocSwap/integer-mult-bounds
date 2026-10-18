# Exact positive certificates for the 47 outer inequalities

**Independent arithmetic verification; no new κ.** This supplies explicit
nonnegative-coefficient certificates for every one of the selected outer
engine's 47 strict inequalities on its retained parameter domain. It also
reproduces all 94 recorded slacks in the native and conservative PR626
witnesses, including their seven-step bootstrap and strict grid rounding.

The closed-form ceiling and the written reduction of the 47 rows belong to
[Romain Hedouin's PR183](https://github.com/CrocSwap/integer-mult-bounds/pull/183).
This corroborates that arithmetic with a different, complete algebraic
certificate: **57 polynomial records, 2,586 rational Bernstein coefficients,
1,268 positive coefficients**, and exact zero identities. No new ceiling,
supplier, multiplication exponent or practical speedup is claimed.

## Reproduce

Python 3.11+ and its standard library suffice, offline:

```sh
python3 -B -I research/outer-bernstein-certificate/verify.py
python3 -B -I research/outer-bernstein-certificate/test_verify.py
```

Expected primary line, followed by 12 passing tests:

```text
PASS_OUTER_BERNSTEIN_CERTIFICATE slacks=47 witnesses=2 coefficient_rows=57 weights=2586 controls=24 kappa=unchanged
```

The primary verifier reads the committed [EXPECTED.json](EXPECTED.json),
expands its positive basis with integer binomial arithmetic, and compares every
power coefficient with the expressions extracted from the pinned source. It
also regenerates the certificate independently by a power-to-Bernstein
transform. Source code is parsed as arithmetic syntax; no predecessor Python
is imported, compiled or executed. Checks remain active under `-O`.

An optional third-party algebra implementation checks all 57 polynomial
identities separately. It needs SymPy; SymPy 1.14.0 was used in validation:

```sh
python3 -B -I research/outer-bernstein-certificate/crosscheck_sympy.py
```

Expected: `PASS_SYMPY_OUTER_CERTIFICATE rows=57 weights=2586 identities=4 sympy=1.14.0`.
It imports none of the primary polynomial arithmetic, source interpreter or
verifier. The primary command and tests do not require SymPy.
`verify.py --write /new/path.json` creates a new certificate and refuses an
existing destination. [VALIDATION.md](VALIDATION.md) records observed checks.

## Statement and parameter map

Let `a` be the effective ordinary bit saving after bootstrap, `b` the complex
saving, `beta` the leaf backoff, `eta` the outer backoff, and `L,R` the two
literal/row bridge gaps. Assume

```text
0 < beta < 1,       0 < eta < 1/2,
0 < b < 1/32,       0 < a < (1-beta)b,
L > 0,             R > 0,
q = a(1-2eta),      D = 1+q,
G = (1-eta)q/D,     0 < kappa < G.
```

Then all 47 slacks of the pinned selected `outer.py` are strictly positive,
its two `min`/`max` choices have the prescribed order, the minimum of its seven
margins is exactly `G`, and its three further prefix identities hold. This is
a statement about the displayed arithmetic under its stated assumptions.
In particular, positive bridge gaps are hypotheses, not a construction of
physical networks or a re-audit of the finite invoice.

Introduce five independent open-unit coordinates:

```text
u = beta, v = 32b, w = a/((1-beta)b), z = 2eta, t = kappa/G.
a = (1-u)vw/32, b = v/32, eta = z/2, kappa = tG.
```

Every point of the stated domain has these coordinates in `(0,1)^5`.
Conversely every such coordinate tuple, together with arbitrary positive
`L,R`, gives a point of that domain. Here `q=(1-u)vw(1-z)/32 > 0`, so `D>1`.
The bridge variables are **not** restricted to the unit interval.

The source's `max(sigma-tau,0)` chooses zero because `b-a>0`. Its Gaussian
`min(1-epsilon-delta,r-delta)` chooses the second argument because
`1-epsilon-r=eta/2>0`. Both differences receive their own strict positivity
certificates. Thus branch choices do not depend on numerical sampling or an
uncertified symbolic simplification.

## Certificate proof

For `0<x<1`, each Bernstein basis element

```text
B[k,n](x) = binomial(n,k) x^k (1-x)^(n-k)
```

is strictly positive for `0<=k<=n`. Multiplying a source slack `S` by the
positive denominator `D` gives a rational polynomial. Each record supplies
an exact identity of the form

```text
D S = (1/C) sum_k W[k] product_{i=1..5} B[k_i,n_i](x_i) L^k_6 R^k_7,
```

where `C` is a positive integer, every integer weight `W[k]` is nonnegative,
and at least one weight is positive. Every term with a positive weight is
strictly positive on the stated domain. Therefore `D S>0`, hence `S>0`.
Zero coefficients are allowed; the domain is open, so no endpoint positivity
is asserted. The same argument handles the two unrestricted positive bridge
variables through ordinary monomials.

The power-to-Bernstein transform uses the exact identity

```text
x^j = sum_{k=j..n} binomial(k,j)/binomial(n,j) B[k,n](x).
```

The checking direction instead expands each `(1-x)^(n-k)` with integer
binomial coefficients and compares the resulting power map. It does not call
the nomination transform or the primary polynomial multiplication. The
optional SymPy checker expands both sides again with separate algebra.

The 57 records consist of the denominator, 47 slacks, two branch-order
differences, and seven margin differences `margin-G`. Six margin differences
have strict certificates; the compact-phase difference is the identically
zero polynomial. This proves both the lower bound on every margin and an
attaining margin, so the source's minimum assertion is justified. Three
additional source equalities reduce to zero coefficient maps. The receipt's
four identity entries include the minimum assertion.

This finite coefficient evidence, together with the positive-basis argument,
establishes the arithmetic statement for the whole parameter domain. The
tests of particular parameter points are supplementary. There is no Lean or
other proof-assistant formalization; correctness of the Python checker and
its arithmetic libraries is part of the executable trust boundary.

## Binding to the selected construction

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) pins six consumed files. The selected record binds
the full assembly receipt and review. The selected source inventory binds the
outer engine and its caller, and the receipt independently names the consumed
outer-engine hash `c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c`.
The AST interpreter accepts the fixed source grammar and complete row inventory;
it is not a general Python execution engine.

Both native and conservative witnesses are reconstructed from the retained
complex and bit endpoints. For their common ordinary recursion parameter `s`,
the checker uses the closed form `a_j=s-s^j(s-a_0)`, with
`a_0=384599/10^10`, rather than the producer's update loop. All 14 exponents,
14 gap/cutoff records and 94 outer slacks match exactly. At the `10^-18` grid,
`kappa=(ceil(10^18 G)-1)/10^18`, so `kappa<G<=kappa+10^-18`.

| Witness | Reproduced κ |
| --- | --- |
| Selected native | `51110230636731/31250000000000000` |
| Conservative comparison | `1635527377506429/1000000000000000000` |

Both supplier endpoints and the physical meanings of the two bridge gaps are
inherited inputs. Their moment enclosures, supplier geometry, phase/wrapper
legality, hosting, invoice and all-size validity are not independently proved
by this package. The selected low-level engine has no separate positive-κ
guard; this statement deliberately concerns positive targets, as chosen by
the selected constructor. It does not assert equivalence with every possible
call of the historical balanced checker discussed in PR183.

## Failure detection

Twenty-four built-in controls reject altered signs/weights/scales, a missing
coefficient or row, surplus rows, incorrect branch choices, dropped target
charges, an altered Gaussian cap, changed witness/cutoff receipts, strict
boundary equalities, nonpositive bridge gaps and nonexact inputs. JSON numeric
types are retained: `0`, `0.0` and `false` are not interchangeable evidence.

Twelve additional tests include a separate de Casteljau evaluation of every
certificate, 64 explicit tensor basis checks, 864 ordinary-recursion checks,
source corruption and an isolated optimized replay from a minimal relocated
copy. A useful control changes the Gaussian cap from `1/4` to `1/8`: both
selected points still pass that row, but an interior-domain counterexample
and a negative Bernstein coefficient reject the universal claim. This is a
modified-model control, not a defect in the intact construction.

For that control, take `beta=1/4`, `b=1/64`, `a=3/512`, `eta=9/20`,
`kappa=G/10`, and positive bridge gaps. Then `r=46173/204920`:
the original Gaussian gap is `5057/204920>0`, while the altered gap is
`-10279/102460<0`.

## Attribution, overlap and limits

PR183 at `1f22094b12bdae7759124e6c51ab44d3ea2a10ab` is credited for the closed
form, the written 47-row reduction and its earlier point checks. No priority
for those mathematical statements is claimed. BigCactusLabs' PR701 at
`de07c015b38e5b157016db636f210c4f7f537058` gives a larger-domain Gaussian
envelope and separate factored finite comparisons; this stays inside the
retained `b<1/32` domain and adds a complete coefficient certificate for the
selected engine. PR294 and the existing domain audit provide related context.
No pending contribution's code is imported.

The initial queue check covered 611 open PRs through PR791. PR678/706 verify
supplier moments, PR771 finite invoice guards, and PR766 assembly mutation
sites; those are distinct from this universal outer-arithmetic certificate.
The packaging refresh inspected arrivals through PR810 and confirmed unchanged
main and predecessor heads, with no matching Bernstein certificate found.
[CLAIM.json](CLAIM.json) records seed **79**, the three candidate tasks and
`79 mod 3 = 1`. No pinned coordination issue existed, so the claim is local.

Credit also to eumemic / Anthropic Claude for the retained outer engine;
icekylinx, Zhihao Chen, James Chang and RaD / hipotures for its assembly
lineage; Rohan Arun for the ordinary bootstrap; Jeremy Kothe, Chafik Boukhalfa,
DreamingOfClouds and the retained selected-supplier contributors. Original
notices and files are unchanged.

Prepared for **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance** in algebra, code, verification and writing. Both implementations
were developed in one AI session; independent implementation does not mean
independent human review. New material is Apache-2.0 under the repository
[LICENSE](../../LICENSE).

No production file, frontier pointer or `upstream/` source changes. This does
not discharge the inherited compiler, common-label/mutable-basis realization,
whole-call hosting, normalized residual, precision/tape/exact-recovery or
analytic-transfer assumptions, and is not a formal multiplication theorem.

## Maintainer checkpoint binding

The integrated package reads `certificates/checkpoints/k492626.json` instead
of the moving selected-result pointer. The checkpoint bytes have the original
SHA-256; no source digest or mathematical witness was changed. This package
does not claim to replace the current selected construction.
