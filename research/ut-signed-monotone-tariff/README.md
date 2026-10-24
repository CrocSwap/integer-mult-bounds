# Exact signed monotone unitriangular call prices

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration; no new kappa.**
In the full formal algebra `F2[UT_d(Z)]`, signed simple-root calls cannot
share their cost across diagonal outputs that admit sign-consistent words.
The theorem holds for every `d >= 2`, every finite number of targets and
every finite number of restored arbitrary dirty workspace roles. Free scalar
mixing is allowed. The exact minimum at arbitrary positive sign-dependent
prices is the sum of the individual positive and negative root counts below.

For example, put `h = g1^m g2^-n`, with `m,n > 0` and `d >= 3`. The endpoint
`diag([h],[h^-1],1,...)` costs exactly `2(m+n)` unit-price calls. Every
first-superdiagonal determinant character of this endpoint is one, yet both
opposite signs have separate unavoidable bills. The price is
`m(alpha1+ + alpha1-) + n(alpha2+ + alpha2-)`. This inverse-pair family is
a new test case, not a recheck of either predecessor UT5 endpoint.

## Model and theorem

Let `G = UT_d(Z)` and `g_i = I + E_(i,i+1)`, for `1 <= i < d`. There are
`R >= W` roles. Paid calls are exactly

```text
D_N(g_i^epsilon) = I_R + ([g_i^epsilon] + [1]) N,
epsilon in {+1,-1}, N = x y^T over F2, y^T x = 1.
```

Thus `N` is any binary rank-one idempotent. Its price is `alpha_i^epsilon > 0`.
Arbitrary `GL_R(F2)` transformations may be interleaved at zero cost in this
optimistic relaxation. No other address operation, erasure or clean workspace
is supplied. The endpoint must equal

```text
T = diag([h_1],...,[h_W],[1],...,[1]) in Mat_R(F2[G]).
```

All target and workspace data start arbitrary. Formal equality requires every
workspace input to return unchanged, with no residual target coupling. The
integer address matrices are not reduced modulo two.

Write `a_ji = (h_j)_(i,i+1)`. For **every** endpoint, every realizing program
has the separate bounds

```text
n_i+ >= P_i = sum_j max(a_ji,0),
n_i- >= M_i = sum_j max(-a_ji,0).
```

Call a supplied simple-root word sign-consistent when each root `g_i` occurs
with at most one sign within that word. Signs may differ between targets.
If each `h_j` has such a word, both bounds are attained simultaneously.
Consequently its exact optimal price is

```text
sum_i (alpha_i+ P_i + alpha_i- M_i).
```

The theorem permits arbitrary interleavings of root letters within each
supplied word, including noncommuting letters. Ordered products
`g_1^a1 ... g_(d-1)^a(d-1)` are one explicit subfamily. The existence of a
sign-consistent word is a hypothesis, not a decision procedure supplied here.

## Written proof

**1. Character projections.** For each `i`, the map
`chi_i(h) = h_(i,i+1)` is a group homomorphism from `UT_d(Z)` to `Z`.
Indeed the first-superdiagonal entry of a product is the sum of those entries;
there is no intermediate integer index strictly between `i` and `i+1`.
It sends `g_i^epsilon` to `epsilon` and every other simple-root letter to zero.
Therefore `[h] -> t^chi_i(h)` induces a ring homomorphism to
`L = F2[t,t^-1]`. Formal equality implies projected equality. No converse is
needed or asserted.

**2. The inherited all-minor degree.** For a square Laurent matrix `A`, let
`delta(A)` be the largest degree of any nonzero square minor, over all sizes,
including the empty minor one. It is nonnegative. Cauchy--Binet gives
`delta(AB) <= delta(A) + delta(B)`: each minor is a sum of products of
equal-sized minors, and cancellation cannot increase degree. Every invertible
constant matrix and its inverse have degree zero. Applying this inequality
in both directions shows that constant invertible left or right factors
preserve `delta`. This is Adam Gall's #1911 method, also used and extended
by ywz65 in #2716; the invariant and this argument are not claimed as new.

**3. Separate sign bills.** Since `N` is an idempotent of rank one,
`F2^R = im(N) direct-sum ker(N)`. A constant change of scalar basis puts `N`
in the form `diag(1,0,...)`. Under the `i`-th projection a call of root `i`
is therefore constant-similar to `diag(t^epsilon,1,...)`. Its `delta` is one
for `epsilon=+1` and zero for `epsilon=-1`. Calls of all other roots project
to the identity. Every free scalar transformation has `delta=0`.
Subadditivity through the entire actual word consequently bounds the endpoint
degree by `n_i+`. Replacing `t` by `t^-1` gives the separate bound by `n_i-`.
This includes every paid restoration call and every free mixing operation.

**4. Endpoint evaluation.** The projected endpoint is diagonal with entries
`t^a_ji` and spectator entries one. Each nonzero minor of a diagonal matrix
selects a subset of its diagonal entries. Selecting precisely the positive
exponents proves `delta(T_i) = P_i`. The inverted-variable projection gives
`delta(T_i(t^-1)) = M_i`. Spectator entries contribute zero for every `R-W`.
Steps 3 and 4 prove all the separate lower bounds, without a workspace bound
and without any assumption that a target word is sign-consistent.

**5. Attainment.** For a coordinate projector `E_j`, multiplication in the
full group algebra gives `D_Ej(g) D_Ej(h) = D_Ej(gh)`. Distinct coordinate
projectors act independently. Put the supplied word for `h_j` on role `j`.
Its signed root counts are exactly `max(a_ji,0)` and `max(-a_ji,0)` because
sign consistency forbids cancellation in `chi_i`. This realizes the complete
formal endpoint with the two bounds attained together. It uses no workspace
or scalar mixing. With left matrix actions, execute a displayed product's
letters from right to left. Positive prices now give the exact price formula.

For the inverse-pair example, the two words are `g1^m g2^-n` and
`g2^n g1^-m`. Each is sign-consistent. Their aggregate characters cancel,
while the theorem requires `m` calls of each sign of root 1 and `n` of each
sign of root 2. This completes the example and the theorem.

## What changes for the next search

Cinna Davis's [#2103](https://github.com/CrocSwap/integer-mult-bounds/pull/2103)
and [#3316](https://github.com/CrocSwap/integer-mult-bounds/pull/3316) ask about
sharing calls among other diagonal UT5 targets and give target-specific
formal obstructions. The new theorem closes the sign-consistent family at
every dimension and workspace size, with heterogeneous positive prices.
A search for a saving in this alphabet must leave that family, for example
by using targets with genuine root-sign reversals. We do not replay either
predecessor census or claim their target-specific conclusions as new.

The scalar-idempotent formal model retains the predecessor lineage of eumemic
#288 and Ali Romman #468. The proof method is credited to Adam Gall's
[#1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911) and ywz65's
[#2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716). Their
dihedral representations and tariffs are different from these integer
unitriangular character projections. Exact source bytes are pinned as
provenance in `SOURCES.json`; no predecessor executable is imported or run.
No claim of priority outside the repository is made.

## Reproduce and evidence

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ut-signed-monotone-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ut-signed-monotone-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ut-signed-monotone-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ut-signed-monotone-tariff --check-source-history
```

The absolute interpreter path is the original environment's CPython 3.12.15;
another CPython 3.12 installation can replace that path. Only the standard
library is needed. Expected final lines are `PASS_UT_SIGNED_MONOTONE_TARIFF`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and the committed-byte/source-history pass.
The registered normal and optimized commands are separately time-bounded.

The verifier constructs integer unitriangular products and full formal binary
coefficient matrices. It computes Laurent minors by Leibniz expansion,
separately from the written Cauchy--Binet proof. The generated report enumerates
all replay counts. It also compares formal products to a separately implemented
literal action on vectors modulo three, including every arbitrary-dirty basis
input of each sampled three-role word. That finite action corroborates the
implementation; quotient equality does not prove a formal lower bound.
The universal conclusion rests on the written proof, not finite sampling.

Default replay writes nothing. The JSON report binds all five package files
by SHA256. Optional `--receipt /absolute/path/outside/checkout.json` creates a
fresh report and refuses an occupied path or an output inside the checkout.
There is no hand-written or committed execution receipt.

## Limits and remaining obligations

This is an exact paid-call result in a formal model, not a finite certificate
for a supplier or a complete multiplication theorem. The lower bounds hold
for arbitrary targets, but sharpness requires sign-consistent supplied words.
A nonidentity central commutator has every `P_i=M_i=0`, so the character
bounds do not determine arbitrary-target costs. The verifier retains that
boundary control, a noncommuting-order control, a determinant-cancellation
control, and single-call omissions of the inverse-pair constructions.

The signed simple-root alphabet and full formal equality are essential.
Direct higher-root calls, arbitrary address maps, clean state, finite cyclic
quotient shortcuts and changed coupling alphabets are outside the theorem.
The formal attaining word has `W` dirty targets, no scratch, no free mixing
and exactly the stated paid counts. Native frames, physical XOR cost,
hosting, precision, tape movement, recursive pricing and supplier admission
are unknown. No selected construction, selected record or frozen source is
changed. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Which diagonal integer-unitriangular targets with genuine root-sign
   reversals admit a saving beyond the character lower bound? This is the
   first family this theorem does not exclude. Start with one explicitly
   nonmonotone endpoint and a bounded exact alphabet. Higher-root information
   is the missing ingredient; a zero character bill is not a construction.
2. Can one signed simple-root formal call be assigned an actual native
   supplier interface and complete price? Start with its dirty-state and frame
   contract and charge every scalar conversion and physical traversal.
   No such bridge is supplied here, so this result alone gives no kappa gain.

## Replay engineering

The verifier has no recursion, dynamic code execution, subprocesses or imported
predecessor code. Group dimensions are at most six, role dimensions at most
four, the exhaustive mixed-word length is three, and literal actions use
exactly 27 addresses and three roles. The remaining fixtures have fixed loop
bounds and deterministic seeds. All functions are below 60 physical lines.
Admission checks use explicit exceptions and remain enabled under `-O`.

Power-of-Ten rule 3 deviation: CPython allocates integers, tuples and sparse
dictionaries during arithmetic. Fixed replay dimensions, word lengths and
formal-support guards bound live data; the program is a terminating check,
not a steady service. Verification includes the complete bounded replay.
A fixed-storage implementation is a follow-up only if these bounds expand.
Rule 10 deviation: there is no compiler or configured static type checker for
this standalone standard-library package. Every registered command enables
warning errors; normal and optimized execution and explicit AST inspection
check the actual artifact. Add repository-standard static analysis if one is
adopted for these packages. These deviations make no real-time guarantee.
