# Exact signed two-source connector over odd prime fields

For every odd prime p, the signed dirty connector with two immutable sources
and all p^2 - 1 nonzero coefficient rows over F_p has exact unit-call optimum

```text
OPT_signed(p, 2) = 2p^2 + 2p - 4.
```

In particular, the optimum is **56 calls over F5**. The construction uses
eight source calls and two readouts for each of the 24 nonzero rows. The
lower bound permits arbitrary extra readouts, so it is an all-word optimum
within the specified alphabet.

This is a **scoped proof with finite corroboration**, produced by Nick
Petalas. The new step is an exact full-coefficient signed optimum and a
short-path deficit argument. The prefix/difference method is predecessor
work. No new kappa or complete multiplication theorem is claimed.

## Interface

There are two read-only sources x_0,x_1, one borrowed dirty connector z and
distinct dirty outputs y_v indexed by every nonzero v in F_p^2. For arbitrary
compatible F_p-linear maps, the required action is

```text
y_v += v_0 A_v B_0 x_0 + v_1 A_v B_1 x_1;
x_0, x_1 and z unchanged.
```

Maps may be singular and need not commute. The only operations are signed
complete calls, each with unit price:

```text
+B_j: z += B_j x_j       -B_j: z -= B_j x_j
+A_v: y_v += A_v z       -A_v: y_v -= A_v z
```

The negative letters subtract a map application; they do not invert its
matrix. Calls preserve every other row and restore their own private scratch
and entry heads. The word is independent of data and map entries. Outputs
are observed only after completion and cannot serve as workspace. There is
no scalar-multiple source letter beyond the two signs, no source mutation,
extra connector, free copy, direct A_v B_j call or frame change.

This retains Ross Richardson's #943/#934 complete-call boundary and uses
signed letters as in conorholds's #2208. Full coefficient demand differs from
binary-mask demand. The GF4 scalar-source alphabet of #2266 permits nonunit
coefficients in a source call and is a different model.

## Prefix identity

Project any legal word onto its b source calls. Let q_t in F_p^2 be their
signed prefix-count vector at boundary t, with q_0=q_b=0. At that boundary,

```text
z = z_initial + (q_t)_0 B_0 x_0 + (q_t)_1 B_1 x_1.
```

Readouts of A_v with signs epsilon_s at boundaries t_s add

```text
(sum_s epsilon_s) A_v z_initial
  + sum_j (sum_s epsilon_s (q_t_s)_j) A_v B_j x_j.
```

Thus correctness is equivalent to cancellation of connector dirt and the
required two coefficients, together with q_b=0. Sufficiency uses linearity
only and keeps A_v on the left. Necessity follows by specializing all maps
to scalar identities and independently varying x_0,x_1,z_initial.

Every nonzero output needs at least two readouts. A single signed readout
cannot cancel arbitrary incoming dirt in odd characteristic. With exactly
two readouts the signs must be opposite, since p is odd. Such an output is
therefore available exactly when v is a difference q_s-q_t of two prefixes.

## Attaining construction

Put h=(p-1)/2 and use the integer-restoring source word

```text
(+B_0)^h (+B_1)^h (-B_0)^h (-B_1)^h.
```

Its 4h=2(p-1) events visit every integer boundary point of the square
[0,h]^2. Every row v has a unique representative (a,b) in [-h,h]^2. It is a
difference P-Q of two square-perimeter points:

- For a>=0,b>=0, take P=(a,h), Q=(0,h-b).
- For a>=0,b<0, take P=(a,0), Q=(0,-b).
- For a<0, apply one of these rules to (-a,-b) and swap P,Q.

Read +A_v at P and -A_v at Q. Both points occur on the path; their
chronological order is irrelevant because readouts preserve z. The two
calls cancel A_v z_initial and give exactly the required row. All output
pairs can be interleaved in boundary order in one word.

There are p-1 source calls per source and two readouts per nonzero row, so
the full count is

```text
2(p-1) + 2(p^2-1) = 2p^2 + 2p - 4.
```

## Lower bound allowing extra readouts

Let M=p^2-1 and let b_j count source j's occurrences, regardless of sign.
Every legal word costs at least b+2M, where b=b_0+b_1. If b>=2(p-1), this
already proves the proposed bound.

Suppose b<2(p-1). One coordinate j has b_j<=p-2. Its signed displacement
is zero modulo p, and its absolute value is at most b_j<p, so it is zero
as an integer. Consequently b_j is even. Since p is odd, b_j<=p-3.

Lift this coordinate of the source prefixes to an integer closed walk.
If its range has width w, a closed walk must make at least w positive and
w negative steps. Hence 2w<=b_j<=p-3. All its prefix differences lie in
[-w,w], which has at most 2w+1<=p-2 residue classes. At least two residues
in coordinate j are unavailable to paired readout. Zero is available, so
these missing residues are nonzero.

Each missing residue, paired with any of the p other-coordinate values,
gives a distinct requested nonzero row. At least 2p outputs cannot use two
readouts. Each of them therefore needs at least one additional readout,
without any upper bound on how many it may buy. The total cost is at least

```text
2M + b + 2p > 2M + 2(p-1).
```

Thus shorter source paths are strictly more expensive even after buying
extra readouts. Combined with the construction, this proves the exact
optimum for every odd prime. No census is a premise of this proof.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/signed-prime-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/signed-prime-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-prime-connector
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-prime-connector --check-source-history
```

Any CPython 3.12 executable can replace the absolute interpreter path. The
verifier prints a generated JSON receipt bound to SHA256 hashes of all five
package files, then

```text
PASS_SIGNED_PRIME_CONNECTOR p5_calls=56 primes=5 dense_cases=10 controls=10
```

It checks the closed-form readout compiler, an independently enumerated
perimeter difference set and the full literal dirty coefficient action:

| p | Nonzero rows | Source calls | Full calls |
|---:|---:|---:|---:|
| 3 | 8 | 4 | 20 |
| 5 | 24 | 8 | 56 |
| 7 | 48 | 12 | 108 |
| 11 | 120 | 20 | 260 |
| 13 | 168 | 24 | 360 |

The lower-bound census visits every signed source word of length less than
four at p=3, and less than eight at p=5. It visits 85 and 21,845 words,
respectively. Among them 9 and 641 close modulo p, including the empty
word. Their smallest missing-row counts are 6 and 10, exactly 2p. Every
closed path is checked for the integer-range lemma and the final excess
inequality. No equivalence quotient or heuristic pruning is used.

Ten dense executions cover each listed prime in dimensions two and three,
with dirty connectors and outputs, singular source maps and explicit checks
that readout/source maps do not commute. Ten rejection controls cover
dropped and sign-flipped source/readout calls, an output misroute, a missing
output pair, the F5 word interpreted over F7, and three invalid moduli.
All contracts remain enabled under optimized Python.

The card's first working control passed with 945 pairings, maximum coverage
31, 74 queries and 182 leaves. The selected-source metadata baseline passed
separately. These are orientation checks, not new results or selected cold
replays. Predecessor results are cited rather than reverified here.

## Bounds and implementation limits

The written theorem is uniform in p and in compatible map dimensions. The
executable domain is bounded to odd primes at most 31, with registered
fixtures at the five listed primes and exhaustive short paths only at 3,5.
It has no recursion, subprocess, network access or file writes. The maximum
source path is 60 events, the maximum full word is 1,980 events, and package
hash reads are capped at 1 MiB per file. Every function is below 60 lines.

Python requires dynamic allocation during computation, a Power of Ten rule 3
deviation in this bounded offline verifier. Fixed prime, path, word and
matrix-dimension limits bound live storage; the registered timeout is 60
seconds. The verifier is run with warnings treated as errors. No separate
project Python linter or type checker is configured or available locally.
Reconsider fixed-capacity storage only if this code enters an online caller.

The unit call count is proved. For unequal complete prices, the same word
has the constructive bill

```text
h sum_(j=0,1) (c_(+B_j) + c_(-B_j))
  + sum_(v!=0) (c_(+A_v) + c_(-A_v)).
```

Its optimality for unequal prices is unknown. Admission, map preparation,
word storage, dispatch, physical routing, frames, stock, precision and tape
costs remain additional and unknown. There is no identified recursive
consumer for full F_p^2 demand and no complete supplier budget. The family
decision is to finish this local exact result and stop construction work.

No formal proof-kernel build, independent human review, selected cold
replay, physical supplier admission or outer multiplication proof is
supplied. The selected frontier and all frozen predecessors are unchanged.

## Open next questions

1. What is the exact cost with unequal complete source/readout prices?
   Start at p=5 with the short-path deficit and explicitly price a source
   saving against extra readouts. The unit-price proof does not compare
   those weighted trades.
2. What changes for composite characteristic or a field extension? Start
   by specifying the coefficient set and permitted scalar letters. The
   theorem here assumes prime-field coefficients and only two signs.
3. Does an actual recursive caller need all F_p^2 coefficient rows? Pin one
   before another construction round, then price admission, every signed
   primitive, dispatch and dirty return. No such caller is provided here.

## Credit and source scope

This contribution was produced by Nick Petalas. Ross Richardson's
[#943/#934 lineage](../universal-connector-boundary/README.md) supplies the
complete-call boundary and paired-prefix criterion. conorholds's
[#2208](../bidirectional-connector/README.md) supplies signed dirty-connector
context and all-word query-model methods. Riquelme Soares's
[#4189](https://github.com/CrocSwap/integer-mult-bounds/pull/4189) supplies the
unsigned F3 one-source predecessor. The distinct full GF4 two-source problem
and charged nonunit scalar letters are from 1337isnot1337's
[#2266](https://github.com/CrocSwap/integer-mult-bounds/pull/2266). Nick
Petalas's #4256 treats all coefficient rows with unsigned calls, a different
alphabet. No priority is claimed for elementary lattice differences or the
prefix identity.

[SOURCES.json](SOURCES.json) pins historical provenance at public base
624de9dc66858af0945e5f8a0942488d62280d43. There are no executable predecessor
dependencies. The catalogue scope is explicitly changed from a general
alphabet extension to this two-source full-coefficient exact side result.
The new step is the square construction together with an all-word lower
bound that rules out cheaper source/readout trades. Independent human and
formal proof-kernel review are unclaimed. Apache-2.0.
