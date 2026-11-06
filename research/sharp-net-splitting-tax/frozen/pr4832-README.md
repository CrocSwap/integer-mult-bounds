# Sharp integer job-splitting charge

For every real `0<t<1`, the least universal constant in

```
q J^t + r^t <= K_t R J^(t-1),
R=qJ+r>J,   J,R positive integers,   0<=r<J,
```

is

```
K_t = (1+s_t^t)/(1+s_t) = t s_t^(t-1),
t s_t^(t-1) - (1-t)s_t^t = 1,   0<s_t<1.
```

The defining equation has exactly one solution. In particular,
`1<K_t<2` and `K_(1/2)=(1+sqrt(2))/2`. This replaces the coefficient 2 in
one oversized-paid-job estimate of zxv's
[higher-moment strictification, PR #4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433).
The new result is a scoped analytic proof with exact finite corroboration.
No new supplier or kappa is claimed. The elementary calculus is not claimed as
a literature discovery; the contribution is the sharp split charge and its
application to the retained compiler estimate.

## Proof and integer sharpness

Set `s=r/J`. Dividing the split charge by `R J^(t-1)` gives

```
F_q(s) = (q+s^t)/(q+s) = 1+(s^t-s)/(q+s).
```

Because `s^t>=s` on `[0,1]`, every `q>=1` satisfies `F_q(s)<=F_1(s)`.
Thus all multi-block quotients reduce to a single full block and a remainder.
The sign of the derivative of `F_1` on `(0,1)` is the sign of

```
n_t(s) = t s^(t-1) - (1-t)s^t - 1.
n_t'(s) = -t(1-t)s^(t-2)(1+s) < 0.
```

As `s` tends to zero, `n_t(s)` tends to positive infinity, while
`n_t(1)=-2(1-t)<0`. Hence its unique zero `s_t` is the unique maximizer.
The stationary equation gives the two displayed formulas for `K_t`.
The value is strictly larger than one because `s_t^t>s_t`, and strictly
smaller than two because `1+s_t^t<2<2(1+s_t)`.

For integer sharpness, take `J` tending to infinity, `r=floor(s_t J)` and
`R=J+r`. Eventually `0<r<J`, so `R>J`. Continuity gives
`F_1(r/J) -> F_1(s_t)=K_t`. Every smaller coefficient fails on one of these
integer splits. Thus the supremum over integer jobs equals the continuous
maximum, even though the maximizing fraction need not itself be rational.

At `t=1/2`, the stationary equation gives
`s_t=(sqrt(2)-1)^2=3-2sqrt(2)`, and consequently
`K_t=(1+sqrt(2))/2`. Already `J=6,R=7` has normalized charge
`(6+sqrt(6))/7>6/5`, so rounding the coefficient down to 1.2 is invalid.
At `t=1/3`, the solution is `s_t=1/8`, giving `K_t=4/3`, attained by
the integer split `J=8,R=9`. The supremum can therefore be attained.

## Consequence for the higher-moment paid tail

Retain the notation and all native hypotheses of PR #4433, section 2.
Let `C=1-t`, `u>=C`, `sigma=t+u>=1`, integer cutoff `J=c^v`, and
completion threshold `L=b^v`, with `1<c<b<m`. Let `T_x` and `P_x` be
productive and paid rank moments of the raw unit, and `B` its productive
field count. For each oversized rank `R>J`,

```
split_t(R,J) <= K_t R J^(-C)
              <= K_t R^(t+u) J^(-u).
```

The second inequality is exactly `(R/J)^(sigma-1)>=1`; the restriction
`sigma>=1` is retained. Summing over chronological tensor-product paid jobs
uses the predecessor's moment multiplication. Overcounting unsplit jobs by
`P_t^v` as before gives

```
original_paid_t <= P_t^v + K_t P_(t+u)^v / J^u.
```

Keep the predecessor's separate completion bound `2 B^v L J^(-C)` and its
lower bound `T_t^v` for the completed productive moment. The complete
normalized charge therefore obeys the improved sufficient bound

```
alpha^v + K_t gamma_u^v + 2 delta^v,
alpha   = P_t/T_t,
gamma_u = P_(t+u)/(c^u T_t),
delta   = B b/(c^C T_t).
```

Only the coefficient of the oversized original-paid term changes. Completion
is still paid, and the unsplit overcount remains. This proof does not replay
or certify the raw p7 invoice, a particular tensor power, the native programs,
integer batching or any physical supplier. A lower sufficient bound need not
reduce an actual construction's least tensor power. No selected record changes.

zxv's merged [PR #4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483)
gives a different direct compiler that removes tensor padding and splitting
for three profiles satisfying its gates. The present theorem tightens the
retained splitting estimate; it does not improve on that direct compiler's
sufficient rank or assert that every current profile needs strictification.

## Reproduction and evidence

From the repository root, with the available CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-integer-split-charge
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/sharp-integer-split-charge/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B research/sharp-integer-split-charge/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-integer-split-charge --check-source-history
```

The first command runs both registered modes. Standard library only. The
checker enumerates every `1<=J<=48`, `1<=q<=8`, `0<=r<J` at each of
`t=1/4,1/3,1/2,2/3,3/4,7/8`, including the harmless `R=J` boundary.
There are 56,448 enumerated split cases in total.
It uses rational intervals from bounded integer-root searches, never binary
floating point. Seven integer sharpness sequences, including `t=127/128`,
reach `J=10^6` within `10^-10` of the certified optimum. The half-exponent
closed form has an independent integer-square-root enclosure.

For rational `t=a/b`, the critical-point check uses `y=s_t^(1/b)` and the
strictly decreasing polynomial `a-(b-a)y^b-b y^(b-a)`. The analytic argument
covers all real `0<t<1`; the finite checker limits denominators to 128.
Its eleven rejection controls cover invalid exponents/domains, coefficients
1 and 6/5, a reciprocal-coefficient error, and the invalid `sigma<1` extension.
[RESULT.json](RESULT.json) is generated by `verify.py --write PATH`, binds the
five package sources by SHA256, and is compared without writes during replay.
It is finite corroboration, not a formal proof or independent human review.

## Scope, provenance and overlap

The `independent-moment` card is changed from audit to a new compiler inequality.
The required historical first command `scripts/research_baseline.py` fails on
the selected schema with `KeyError: 'bit_lower'`; the current documented
`scripts/research_selected_baseline.py` passes source-binding orientation.
Neither is this result's scientific evidence. The source version is canonical
main `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

The live overlap snapshot reports 348 open PRs and 3,786 Discussion records,
with complete remote pagination. Sparse local helper coverage was only 100
of 6,319 HEAD note paths and is not treated as complete. Separate `git grep`
searches of all main package READMEs and merged-PR searches covered split
charge, sharp splitting, remainder charge and higher-moment terms. They
identified the retained factor-2 estimate and its checks, not this optimal
coefficient. Search coverage does not prove novelty outside those sources.
The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132788)
records the question before the work.

## Verification design

All new loops have finite code bounds; the largest census has 48 cutoffs,
at most 48 remainders and eight quotients for each of six exponents. Integer
root bisection is bounded by the initial integer's bit length, and critical
bisection has 88 rounds. Functions are below 60 lines; checks remain enabled
under `-O`. There are no native resources, imports from predecessor packages,
background children or generated replay files. Normal replay reads this package
only. Power of Ten managed-runtime deviation: Python allocates integers,
Fractions and receipt strings dynamically. Fixed domains and denominator/bit
limits bound the scientific computation; the small package files are trusted
reviewed inputs. The eleven synchronous control callbacks have explicit local
targets and no retained lifetime. A lower-level fixed-memory implementation
would be needed for a strict allocation-free replay; none is claimed here.

## Open next questions

1. Does the sharper coefficient reduce a sufficient tensor power for a current
   fully charged supplier? Start with one pinned inventory and its already
   certified alpha, gamma and delta intervals. Native/completion hypotheses and
   the selected outer bill must be preserved. No such numerical claim is made.
2. For fixed `sigma>1`, what is the least coefficient directly in
   `split_t(R,J)<=K_(t,sigma) R^sigma J^(t-sigma)`? Start with the same
   normalized quotient and a single-remainder calculus problem. The present
   constant is optimal for the linear-rank comparison only.

## Credit

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

zxv's PR #4433 supplies the higher-moment splitting/completion framework and
the factor-2 estimate improved here. Cinna Davis's PR #4412/#4414/#4416 supplies
the retained chronological tensor product and padding construction. Jacob Alan
Sussman supplies the mixed-target integer compiler. Their native, helper,
controller and outer predecessors retain their existing attribution. No
predecessor implementation or result was re-verified as the deliverable.
