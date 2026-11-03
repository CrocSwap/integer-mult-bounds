# Repetition law for balanced depth-four chain schedules

This package answers Open next question 2 of SHIN09-git's
[PR6080](https://github.com/CrocSwap/integer-mult-bounds/pull/6080)
(`research/chain-cyclic-schedules`): at depth four, which exact repetition
conditions replace the depth-three parity gate and cubic shift?

**Answer.** A repeated block v^d, with v holding n copies of each letter and
m = dn, is correct for target c exactly when

```text
(d odd or n even)  and  (3 does not divide d, or 3 divides n)  and  d | c,
```

and v itself is correct modulo n for target c/d. The cubic shift C(d,3)n^3,
which survives at depth three, and the new quartic shift C(d,4)n^4 both vanish
modulo m once the two gates hold. A new **triple gate** takes the place of the
depth-three cubic target shift.

**Corollary.** If gcd(c,m) = 1, in particular for c = 1, no correct balanced
depth-four word has a nontrivial rotation symmetry. Every cyclic class then has
exactly 4m words, so 4m divides W4(m,c). At depth three a unit-target word can
repeat three times; at depth four it cannot repeat at all.

Claim type: **scoped proof with bounded finite corroboration**. No κ, supplier,
paid-profile saving or physical speedup is claimed. The alphabet is unchanged;
this is a counting side result.

## Contract

Work over a nonzero unital ring of exact characteristic m >= 2 with five roles
z0 = x, z1, z2, z3, z4 = y, arbitrary initial data, immutable x and arbitrary
compatible linear maps. Letter l is one complete call z_l += B_l z_{l-1}, for
l = 1..4. A balanced word has m copies of each letter. Let N_ij count the
scattered subwords i(i+1)...j. Appending letter j adds N_{i,j-1} to N_ij for
i < j and increments N_jj, so by induction

```text
z_j(final) = z_j(initial) + sum_{i<=j} N_ij B_j ... B_i z_{i-1}(initial).
```

This is the depth-four form of the interval identity in Nick Petalas's
chain-tariff proof (retained as `research/chain-cyclic-schedules/source/chain-tariff-PROOF.md`,
building on PR4249); the same induction and the same specialization argument
(identity maps, one initial register on at a time, exact characteristic) apply
unchanged. Hence a balanced word is correct for target c iff

```text
N12 = N23 = N34 = N13 = N24 = 0 (mod m)   and   N14 = c (mod m).
```

Write W4(n,c) for the number of balanced words with n copies of each letter
satisfying these congruences modulo n. The convention W4(1,0) = 24 counts all
permutations of 1234 (congruences modulo 1 are vacuous), as in PR6080.

## Proof

**Composition formula.** Let w = v^d. An occurrence of the subword for the
interval I = [i,j] picks its letters from copies of v with nondecreasing copy
index. Grouping letters by copy splits I into consecutive nonempty parts
I_1,...,I_r placed in r distinct copies in increasing order, so

```text
N_I(v^d) = sum over compositions (I_1,...,I_r) of I of  C(d,r) * prod_k N_{I_k}(v).
```

With N_ll(v) = n and a = N12(v), b = N23(v), e = N34(v), p = N13(v), q = N24(v),
t = N14(v), and C_r = C(d,r):

```text
N12(w) = d a + C_2 n^2                       (likewise b, e)
N13(w) = d p + C_2 n(a+b) + C_3 n^3          (likewise q with b, e)
N14(w) = d t + C_2 (n q + a e + p n) + C_3 n^2 (a + b + e) + C_4 n^4.
```

**Pair gate.** This is PR6080's argument unchanged: N12(w), N23(w), N34(w)
are 0 modulo dn iff (d odd or n even) and a, b, e are 0 modulo n. Write
a = n alpha, b = n beta, e = n epsilon. Then C_2 n^2 = dn (d-1)n/2 with
(d-1)n even, so every term C_2 n^2 X with integer X is 0 modulo dn.

**Triple gate.** Under the pair gate, N13(w) = d p + C_3 n^3 (mod dn).
This is 0 modulo dn iff d divides C_3 n^3 and p = -C_3 n^3/d (mod n).
Now C_3 n^3/d = (d-1)(d-2) n^3/6. The factor (d-1)(d-2) is always even, and
divisible by 3 unless 3 | d. So d | C_3 n^3 iff (3 does not divide d or 3 | n).
In that case C_3 n^3/(dn) = (d-1)(d-2) n^2/6 is also an integer, so the shift
is 0 modulo n and the condition is just p = 0 (mod n). The same holds for q.

**Target.** Under both gates write p = n pi, q = n kappa. The C_2 term of
N14(w) is C_2 n^2 (kappa + alpha epsilon + pi), which is 0 modulo dn. The C_3
term is C_3 n^3 (alpha + beta + epsilon), also 0 modulo dn. For the quartic
shift, C_4 n^4/(dn) = (d-1)(d-2)(d-3) n^3/24. If d is odd, (d-1)(d-3) is a
product of consecutive even numbers, so 8 divides it; if d is even then n is
even and 8 | n^3. One of d-1, d-2, d-3 is divisible by 3 unless 3 | d, and
then 3 | d-3. So the quartic shift is 0 modulo dn. Hence N14(w) = d t (mod dn),
which equals c modulo dn iff d | c and t = c/d (mod n). ∎

**Fixed points and classes.** As in PR6080, a word fixed by a rotation of
order d is v^d with v balanced of size n = m/d, and d must divide m. So

```text
F_d(m,c) = W4(m/d, c/d)  if (d odd or m/d even), (3 ∤ d or 3 | m/d) and d | c;
         = 0             otherwise.
O(m,c)   = (1/(4m)) sum_{d|m} phi(d) F_d(m,c).
```

Möbius inversion over divisors gives each least-period population exactly as
in PR6080. If gcd(c,m) = 1, every d > 1 fails d | c, so F_d = 0 for d > 1,
which proves the corollary. For c = 0, the gates alone decide: for example
m = 2 and m = 3 admit no periodic correct word, because d = 2 with n = 1 fails
the pair gate and d = 3 with n = 1 fails the triple gate.

## Evidence

`verify.py` uses the Python standard library only. It is a bounded checker of
the written proof, not a proof of every modulus.

- Literal chronological interval counts of v^d agree with the composition
  formula for all **1,508,928** (block, d) pairs: every block with n = 1, 2 and
  d = 1..12, and every one of the 369,600 blocks with n = 3 and d = 1..4.
- The gate law agrees with literal correctness of v^d for every block, d and
  target c in 0..m-1: **11,482,992** word-target checks, moduli up to m = 24.
  The resulting fixed-point counts equal the F_d formula in every case.
- Full literal census for m = 1, 2, 3: W4(2,0) = 816 in 102 classes,
  W4(3,0) = 24,984 in 2,082 classes, and W4(2,1) = W4(3,1) = W4(3,2) = 0.
  Every correct word at m = 2, 3 is primitive. Least periods, rotation closure
  and the Burnside sum agree with the class counts.
- The coefficient shift lemma (pair shift iff pair gate; d | C_3 n^3 iff triple
  gate; dn | C_3 n^3 and dn | C_4 n^4 under both gates) for all d <= 240,
  n <= 60.
- Five false claims are rejected by an explicit counterexample: dropping the
  pair gate, dropping the triple gate, keeping the depth-three cubic target
  shift, adding a quartic target shift, and not dividing the target by d.

The zero nonzero-target counts at m = 2, 3 agree with Nick Petalas's
[PR4279](https://github.com/CrocSwap/integer-mult-bounds/pull/4279), which shows
that no balanced word is correct for c != 0 at m = 2..5. The corollary is
therefore vacuous for m <= 5. It is nonvacuous for 6 <= m <= 64, where
[PR4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263) and
[PR4280](https://github.com/CrocSwap/integer-mult-bounds/pull/4280) exhibit
balanced correct words for every c != 0. This package does not recheck those
witnesses; it only cites them for nonvacuity.

## Reproduce

From the repository root with CPython 3.12 (about 25 seconds locally):

```sh
python3.12 -B research/chain-depth-four-repetition-law/verify.py
python3.12 -B scripts/research_package.py --package research/chain-depth-four-repetition-law
```

The verifier is read-only and prints a JSON receipt containing
`PASS_CHAIN_DEPTH_FOUR_REPETITION_LAW` and each package file's SHA-256.

## Sources and overlap

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Exact provenance pins
are in [SOURCES.json](SOURCES.json). Predecessors:

- SHIN09-git, [PR6080](https://github.com/CrocSwap/integer-mult-bounds/pull/6080):
  depth-three repetition law, Burnside/Möbius transform and the question
  answered here. The pair-gate argument and fixed-point reduction are theirs.
- Nick Petalas, [PR4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249)
  and the chain-tariff proof: interval identity and correctness criterion.
- Nick Petalas, [PR6037](https://github.com/CrocSwap/integer-mult-bounds/pull/6037):
  depth-three counts W(m,c).
- Nick Petalas, PR4263, PR4279 and PR4280: depth-four shortest lengths and
  count vectors. They do not quotient rotations or count balanced words.

Searches of merged README files and PR titles/bodies for depth-four rotation,
period and repetition laws found only PR6080's open question. No match is not
proof of novelty.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. What is the repetition law at general depth L? Depth three keeps a cubic
   target shift; depth four loses every shift. First apply the composition
   formula at depth five and reduce the four- and five-part shifts modulo dn
   under the depth-four gates. Mixed products of lower interval counts appear
   there and need their own argument.
2. What are the exact counts W4(m,c) and cyclic class numbers O(m,c) for
   m >= 4? The law above turns any such census into class counts, but only
   m <= 3 is counted here. First write a chronological residue DP over prefix
   letter counts and the six off-diagonal interval residues; m = 4 has about
   2.6 million states. PR4280's row model may give a smaller state space.

## Credit

This package was produced by Nick Petalas. Predecessor credit is listed above.
New work is Apache-2.0.
