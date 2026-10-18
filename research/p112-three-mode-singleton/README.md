# Three-mode P112 mixing with a one-column correction retains COPY64

**Scoped negative result: a written quantified proof with exact finite premises.**
Mix any three P112 coordinate terms and one arbitrary free one-column correction
by any `GL(4,C)` change of factors. The complete separate COPY sum has sharp floor
**64**, and the complete COPY power bill has sharp floor `8*8^q` for `0<q<=1`.
Transposition gives the same result for a one-row correction. All 56 coordinate
triples, all 112 singleton sites and arbitrary complex correction amplitudes are
covered, including a zero correction.

This supplies a parallel, independently checkable answer to the singleton-sided question in
[PR1512](https://github.com/CrocSwap/integer-mult-bounds/pull/1512).
That package treats three modes when both correction supports have at least two
entries. [PR1468](https://github.com/CrocSwap/integer-mult-bounds/pull/1468)
treats singleton-sided corrections with two modes. Neither theorem is assumed
here. This package recomputes its geometric premises and supplies the additional
compensation argument for three modes.

Andrey Mas's earlier [Discussion1550](https://github.com/CrocSwap/integer-mult-bounds/discussions/1550)
already claims the same core investigation for `(2,4,5)` and `|supp(u)|>=2`.
It was recognized at the final targeted overlap check; its snapshot contains a
claim, not a proof or artifact to compare. This submission credits that shared
scope and does not claim to have originated the follow-up. Its independently
reviewable contribution is the explicit proof, complete finite certificate,
second implementation, all-triple transport and zero/single-entry boundaries.

No new supplier or improved kappa is claimed. The selected record and frozen
inputs remain unchanged.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -I -B scripts/research_package.py --package research/p112-three-mode-singleton
```

The registered commands check source pins, recompute the primary receipt, run a
second implementation with assertions disabled, and run eight external tests.
Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-three-mode-singleton outcome=negative-result
```

[verify.py](verify.py) uses PR845's pinned simple-root labels and enumerates
normal intersections. [independent_check.py](independent_check.py) imports no
primary or predecessor code: it constructs Euclidean E8 roots, closes proper
rational row spaces by RREF, and eliminates full 112-bit pairing rows from the
opposite pivot direction. They compare every finite support and pairing, rather
than only their minimum or histogram. Both implementations have the same
AI-assisted author; their agreement is not independent human review.

[CERTIFICATE.json](CERTIFICATE.json) contains all support representatives,
character spectra, pairing tables, coordinate transports and fixture results.
Default replay only reads files. To regenerate a new receipt:

```sh
python3.12 -I -B research/p112-three-mode-singleton/verify.py --write /tmp/new-singleton-receipt.json
```

The output path must not already exist. [VALIDATION.json](VALIDATION.json)
records the actual checks and their limits.

## Model and exact statement

Use the PR845/PR717 P112 geometry: choose the lexicographically larger sign of
each doubled E8 root line, remove the eight lines
`f_(2k)=2e_(2k)+2e_(2k+1)` and `f_(2k+1)=2e_(2k)-2e_(2k+1)`, then sort the
112 remaining lines. Define

```text
G_ij = (r_i dot r_j)/4,
X_ik = (r_i dot f_k)/4,
B_ij = (1+G_ij) mod 2.
```

Then `XX^T=2G`. The entries of X are `0,+1,-1`. B is the nondegenerate
pairing on the nine-dimensional binary label space; the 112 labels are distinct
and nonzero. For supports A,C, let `rho(A,C)=rank_F2 B[A,C]`. A separately
charged scalar term `d t^T` costs `rho(supp(d),supp(t))`. Its complex values
determine its supports and are never reduced modulo two. All transposes below
are ordinary transposes.

Choose any three coordinate indices J and put `Y=X[:,J]`. Fix a live site j,
write `O_j={i:B_ij=0}`, and take arbitrary complex u supported on O_j. Set
`v=lambda e_j`, where lambda is any nonzero complex number. For any `M in GL(4,C)`,
put

```text
N=M^(-T),       D=[Y,u]M,       T=[Y,v]N.
```

The four terms have product `YY^T+uv^T`. Together with the other five coordinate
terms they agree with `2G` on every constrained entry `B_ij=1`. Let r_h be the
COPY ranks of these four terms.

**Theorem.** For every such choice and every real `0<q<=1`,

```text
sum_(h=0)^3 r_h^q >= 3*8^q.
```

Adding the five unchanged rank-eight terms gives the stated floor `8*8^q`,
and at q=1 gives 64. Identity mixing attains both for every allowed u and v:
its four ranks are `(8,8,8,0)`.

## Exhaustive finite geometry

It suffices to study `J=(2,4,5)`. The certificate provides 56 explicit
coordinate permutations carrying this triple to every triple. Both checkers
verify their signed bijections on all 112 root lines and all 12,544 entries of
B. Row signs and coordinate order can be absorbed into u, v and M without
changing supports. This transport uses no assumed group-classification result.

The 112 projected rows have 13 nonzero projective directions, precisely the
directions of `{0,+1,-1}^3`. For any nonzero `a in C^3`, the rational span of
the projected rows annihilating a is a proper rational flat of rank at most
two. Rational and complex ranks of rational matrices agree. The zero rows
are exactly those lying in this flat. Conversely, a generic normal to any
proper flat avoids all directions outside it; the primary checker supplies
an explicit representative for each resulting support. Therefore enumerating
these flats exhausts complex supports, not just a finite coefficient grid.

There are one rank-zero, 13 rank-one and 25 rank-two flats, giving **39 supports**.
This is the three-mode arrangement from PR1512, recomputed in both implementations.
For these supports S,T, the exact new one-anchor pairing table and retained
baseline facts are:

| Finite premise | Complete evidence |
|---|---|
| Original `rho(S,T)>=8` | 1,521 pairs: 225 of rank 8, 1,296 of rank 9 |
| Minimum positive character weight on S is at least 12 | 19,968 evaluations, including zero characters/weights |
| `rho(S intersect O_j-complement,T)>=7` | 170,352 cases: 19,464 of rank 7, 150,888 of rank 8 |
| Singleton deletion preserves each support's label span | 4,368 direct independent deletion checks |

The minimum positive character weights have distribution
`{12:6,24:10,30:12,32:6,38:4,40:1}` across the 39 supports. A separating
binary functional proves that deleting at most eleven rows from any support
preserves its full label span: otherwise a nonzero character restriction of
weight at most eleven would exist. This also proves singleton preservation.
The primary enumerates all 512 binary functionals; the independent checker
constructs the full dual code from the pairing matrix.

The one-anchor survivor dimensions are seven in 344 cases and eight in 4,024.
A dimension-only estimate would give pairing rank six in some cases. The exact
**pairing** minimum seven is what lets the three-mode compensation bill close.

## Proof of the complete four-term bill

Write each column of M as `(a_h,c_h)` and each column of N as `(b_h,d_h)`,
with `a_h,b_h in C^3`. From `MN^T=I_4`,

```text
sum_h a_h b_h^T = I_3.                              (1)
```

Call a product active when both a_h and b_h are nonzero. There are at least
three active products by rank subadditivity in (1). Each projection matrix
has rank three, hence has at most one zero column.

An active left factor contains every row of `supp(Ya_h)` outside U=supp(u).
In particular it contains `supp(Ya_h) intersect O_j-complement`. An active
right factor contains `supp(Yb_h)` outside `{j}`, whose label span is unchanged
by singleton deletion. The one-anchor pairing table and rank monotonicity
therefore give **r_h>=7 for every active product**. If `|U|<=11`, the full
left span also survives, so every active product instead has r_h>=8. This
already proves the theorem for small U, including u=0.

Assume now `|U|>=12`. The following cases exhaust the projection patterns.

1. **Some right projection b_h is zero.** Its column of N is a nonzero
   multiple of the fourth coordinate vector. `M^T N=I_4` forces `c_k=0`
   for every k different from h. The other three left factors are thus
   uncorrected, nonzero combinations of Y. Their right projections are nonzero
   and retain their full spans after singleton deletion. All three have
   pairing rank at least eight by the original pairing table. The fourth
   term has nonnegative cost.
2. **Every right and left projection is nonzero.** All four terms cost at
   least seven, so their rank sum is at least 28.
3. **Every right projection is nonzero and one left projection is zero.**
   This pure left factor is a nonzero scalar multiple of u. Its support U
   has at least twelve distinct nonzero labels, so its span has dimension
   at least four: dimension three has only seven nonzero vectors. Its right
   partner has span at least eight. In a nondegenerate nine-dimensional
   pairing space, subspaces A,C satisfy
   `rank B[A,C] >= dim(A)+dim(C)-9`. Consequently this pure factor costs
   at least three. The other three products are active and each costs at
   least seven. The complete rank sum is at least `3+3*7=24`.

Up to permutation, the four actual ranks therefore dominate one of

```text
(8,8,8,0),       (7,7,7,7),       (7,7,7,3).          (2)
```

Every entry t in these lower envelopes is at most eight. For `0<q<=1`,
`(t/8)^q >= t/8`, including t=0. Each envelope sums to at least 24, so its
q-power sum is at least `3*8^q`. Monotonicity transfers this to the actual
ranks, including those exceeding eight. This proves the theorem. Symmetry
of B and transposition give the one-row version.

For fixed width m, normalization and multiplicity, set `q=1-a`, `0<=a<1`.
The affected optimistic moment contribution cannot beat `3*(8/m)^q`, even
when additional preparation, frames, helpers, source access, restoration and
hosting are granted zero cost. This screens the stated COPY mechanism; it
does not bound other work or a changed billing contract.

## Why the compensation must remain in the bill

In the specified ordering, take j=0 and
`u_i=X_i,2` on O_0, zero elsewhere, with v=e_0. Its actual support has size
24. Set `M=I_4-E_(3,0)`. The four factors are

```text
D = [x_2-u, x_4, x_5, u],
T = [x_2,   x_4, x_5, x_2+e_0].
```

Their ranks are exactly `(7,8,8,7)`, so the whole COPY bill is 70. Only two
children retain rank eight; the stronger per-child assertion from the
two-sided case would be false here. Dropping the compensating fourth term
would give the apparent bill 63, but violates the constrained diagonal entry
`(9,9)`. Both implementations check the full 12,544-entry identity and all four
ranks. The cancellation mechanism is credited to PR1432/PR1468; the additional
coordinate term and three-mode quantified bound are the scope here.

Seven primary fixtures check 87,808 scalar entries: identity, compensation,
dense complex mixing, a single-entry correction, u=0, a pure right projection,
and transposition. Controls reject inverse/transpose confusion, Hermitian
substitution, singular mixing and omitted compensation. The external tests
also reject a missing stratum, wrong support representative, changed pairing
rank, forged floor 63, invalid transport, missing source pin and changed
geometry bytes. Their rejection checks remain active under `-O`.

## Provenance, overlap and limits

Initial main and mathematical base: `1f327c6f3e3a35271c5c141d381b540bab8ad005`.
The selector nonce was `097f8f53ac691a8f49688424ca8eba6b`, priority revision 2,
card `complex-masked-decoder`. The scope is refined to the open singleton case;
it changes the eight-term all-pairs premise to a nine-term masked decoder with
five original coordinate terms retained. [TASK.json](TASK.json) records the
bounded question and stop rule. The card's complex-field starting example was
replayed successfully.

The isolated branch was fast-forwarded to submission main `81e81af6` after
revision 3 of the priorities arrived. The selected record and both live pinned
inputs were unchanged. The original assignment remains historical provenance;
the present COPY power obstruction makes no new supplier or kappa claim.

[SOURCES.json](SOURCES.json) pins main inputs and the contextual predecessor
heads: PR1512 `403158808f075dfafcd80da09f630b9a3fde6baa`, PR1468
`5e2d8ec8ebff17c85e813ef1bd6f06312c1fe16a`. [OVERLAP.json](OVERLAP.json)
records live coverage and limitations. Discussion1360 varies all nine factors
for a **single-entry** completion; this result varies four factors for an
**arbitrary one-column** correction. Neither scope contains the other.
Discussion1581 concerns the rank-eight tangent problem. PR1512's both-sides
size-at-least-two result remains complementary and separately reviewable.

Four or more mixed coordinate modes, multiple correction terms, other punctures
and shared COPY billing are outside this proof. The universal argument is
written, not kernel checked. There is no independent human review, physical
word, native admission, selected-construction cold replay, all-size compiler,
common-label/mutable-source realization, owner/hosting proof, precision/tape
analysis or outer analytic transfer here. No multiplication theorem or frontier
change follows from this finite certificate.

Credit to Hanson Sun / PR1512 for the three-mode arrangement and open question;
Andrey Mas (@an664) / Discussion1550 for the earlier parallel investigation;
Gareth Davidson (@bitplane) / PR1468 for the singleton compensation argument
with two modes; commdata2338 / PR1375 and PR1432/PR1460/PR1473 for preceding
support-erasure and compensation work; Mihir Srivastava / PR845 for the pinned
geometry; DreamingOfClouds / PR717 and PR446/595 for the decoder/COPY model;
themilkman216 / PR968 for the pairing-cost floor; Joel Pulikkan / GamingPuzzled /
PR620 for the coordinate COPY64 construction; and woklerx / PR1077 for the
complex-field baseline. Existing source attribution is retained.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex** assistance
in mathematics, both implementations, checking and writing. No subagents were
used. New work is Apache-2.0.

## Open next questions

- **Four coordinate modes with one singleton-sided correction.** The
  one-anchor pairing table might retain a useful bound, but even if the same
  rank-seven premise held, `(7,7,7,7,3)` sums to 31, below the four-mode baseline 32.
  First enumerate proper flats of the four-coordinate projected rows and
  classify the low-pairing cases together with the pure-factor support.
  A stronger coupled bound or an exact improving factorization is needed;
  simply repeating the present dimension estimate cannot close it. Any
  favorable COPY result would still need the full physical supplier budget.
- **More than one free correction.** Multiple correction directions can
  erase larger support spans and invalidate the single pure-factor split.
  A feasible first test is a specified two-column support and exact `GL(5,C)`
  mixing with three retained modes. The blocker is a new complete support
  and compensation classification, followed by full charging of any candidate.
